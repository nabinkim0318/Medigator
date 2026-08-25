from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import faiss
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.services.rag import eval as eval_mod
from api.services.rag import eval_runtime
from api.services.rag.eval import (
    DEFAULT_FAISS,
    DEFAULT_MANIFEST,
    DEFAULT_META,
    DEFAULT_QUERIES,
)
from api.services.rag.retrieve import (
    HYBRID_W_BM25,
    HYBRID_W_EMB,
    MODEL_NAME,
    _merge_scores,
    merge_retrieval_channels,
    rank_channels,
)
from api.services.rag.store import RAGStore


class _FakeMiniLM:
    def __init__(self, dim: int = 384, vector: np.ndarray | None = None):
        self.dim = dim
        self.vector = vector

    def encode(self, texts, normalize_embeddings=True):  # noqa: ARG002
        if self.vector is not None:
            return self.vector.astype("float32")
        vec = np.zeros((1, self.dim), dtype="float32")
        vec[0, 0] = 1.0
        return vec


def _tiny_corpus() -> list[dict]:
    return [
        {
            "id": "doc-a__0000",
            "file": "a.md",
            "title": "Alpha",
            "text": "alpha token one",
            "start": 0,
            "end": 15,
        },
        {
            "id": "doc-b__0000",
            "file": "b.md",
            "title": "Beta",
            "text": "beta token two",
            "start": 0,
            "end": 14,
        },
        {
            "id": "doc-c__0000",
            "file": "c.md",
            "title": "Gamma",
            "text": "gamma token three",
            "start": 0,
            "end": 17,
        },
    ]


def _write_index(tmp_path: Path, vectors: np.ndarray, meta: list[dict]) -> Path:
    index = faiss.IndexFlatIP(int(vectors.shape[1]))
    index.add(vectors.astype("float32"))
    faiss.write_index(index, str(tmp_path / "index.faiss"))
    (tmp_path / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    return tmp_path


def test_runtime_reuses_deterministic_metric_helpers():
    assert eval_runtime.metrics_for_row is eval_mod.metrics_for_row
    assert eval_runtime.rank_channels is rank_channels
    assert eval_runtime.HYBRID_W_EMB == HYBRID_W_EMB == 0.6
    assert eval_runtime.HYBRID_W_BM25 == HYBRID_W_BM25 == 0.4


def test_hybrid_merge_uses_production_weights():
    emb = [(0, 1.0), (1, 0.0)]
    bm25 = [(0, 0.0), (1, 1.0)]
    merged = merge_retrieval_channels(emb, bm25)
    expected = _merge_scores(emb, bm25, w_emb=HYBRID_W_EMB, w_bm25=HYBRID_W_BM25)
    assert merged == expected
    assert merged[0][0] == 0
    assert merged[0][1] == pytest.approx(0.6)


def test_faiss_indices_map_to_chunk_ids(tmp_path: Path):
    meta = _tiny_corpus()
    vectors = np.array(
        [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
        ],
        dtype="float32",
    )
    _write_index(tmp_path, vectors, meta)
    store = RAGStore(str(tmp_path))
    model = _FakeMiniLM(dim=4, vector=np.array([[0.0, 1.0, 0.0, 0.0]], dtype="float32"))
    ranked = eval_runtime.rank_runtime(
        "beta",
        store=store,
        model=model,
        bm25=None,
        mode="vector",
        k=3,
    )
    assert ranked[0]["id"] == "doc-b__0000"
    assert ranked[0]["file"] == "b.md"
    assert {hit["id"] for hit in ranked} == {
        "doc-a__0000",
        "doc-b__0000",
        "doc-c__0000",
    }


def test_vector_count_mismatch_fails_clearly(tmp_path: Path):
    meta = _tiny_corpus()
    vectors = np.array([[1.0, 0.0], [0.0, 1.0]], dtype="float32")
    _write_index(tmp_path, vectors, meta)
    with pytest.raises(eval_runtime.IndexIntegrityError, match="vector count"):
        eval_runtime.verify_runtime_index(
            meta_path=tmp_path / "meta.json",
            faiss_path=tmp_path / "index.faiss",
            summary_path=tmp_path / "missing-summary.json",
            manifest_path=tmp_path / "missing-manifest.json",
        )


def test_manifest_hash_mismatch_fails(tmp_path: Path):
    meta = _tiny_corpus()[:1]
    vectors = np.array([[1.0, 0.0, 0.0, 0.0]], dtype="float32")
    _write_index(tmp_path, vectors, meta)
    (tmp_path / "eval_manifest.json").write_text(
        json.dumps({"index.faiss": "not-the-real-hash", "meta.json": "also-wrong"}),
        encoding="utf-8",
    )
    with pytest.raises(eval_runtime.IndexIntegrityError, match="hash"):
        eval_runtime.verify_runtime_index(
            meta_path=tmp_path / "meta.json",
            faiss_path=tmp_path / "index.faiss",
            summary_path=tmp_path / "missing-summary.json",
            manifest_path=tmp_path / "eval_manifest.json",
        )


def test_model_unavailable_does_not_use_tfidf(monkeypatch):
    import sklearn.feature_extraction.text as text_mod

    called = {"tfidf": False}

    class Probe(text_mod.TfidfVectorizer):
        def __init__(self, *args, **kwargs):
            called["tfidf"] = True
            super().__init__(*args, **kwargs)

    def _boom(*args, **kwargs):
        raise eval_runtime.RuntimeBenchmarkNotRun(
            "RUNTIME_BENCHMARK_NOT_RUN: missing MiniLM"
        )

    monkeypatch.setattr(text_mod, "TfidfVectorizer", Probe)
    monkeypatch.setattr(eval_runtime, "load_embedding_model", _boom)
    with pytest.raises(
        eval_runtime.RuntimeBenchmarkNotRun, match="RUNTIME_BENCHMARK_NOT_RUN"
    ):
        eval_runtime.evaluate_runtime(include_ci_baseline=False)
    assert called["tfidf"] is False


def test_load_embedding_model_fails_explicitly(monkeypatch):
    monkeypatch.setattr(eval_runtime, "SentenceTransformer", None)
    with pytest.raises(
        eval_runtime.RuntimeBenchmarkNotRun, match="RUNTIME_BENCHMARK_NOT_RUN"
    ):
        eval_runtime.load_embedding_model()

    class Boom:
        def __init__(self, *args, **kwargs):
            raise OSError("cache miss")

    monkeypatch.setattr(eval_runtime, "SentenceTransformer", Boom)
    with pytest.raises(
        eval_runtime.RuntimeBenchmarkNotRun, match="RUNTIME_BENCHMARK_NOT_RUN"
    ):
        eval_runtime.load_embedding_model(local_files_only=True)


def test_cli_reports_not_run_without_substituting(monkeypatch, capsys):
    def _boom(*args, **kwargs):
        raise eval_runtime.RuntimeBenchmarkNotRun(
            "RUNTIME_BENCHMARK_NOT_RUN: missing MiniLM"
        )

    monkeypatch.setattr(eval_runtime, "evaluate_runtime", _boom)
    assert eval_runtime.main(["--no-ci-baseline"]) == 2
    err = capsys.readouterr().err
    assert "RUNTIME_BENCHMARK_NOT_RUN" in err


def test_runtime_benchmark_does_not_mutate_fixture():
    def _digest(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    watched = [DEFAULT_QUERIES, DEFAULT_MANIFEST, DEFAULT_META, DEFAULT_FAISS]
    before = {str(path): _digest(path) for path in watched}
    result = eval_runtime.evaluate_runtime(
        include_ci_baseline=False,
        model=_FakeMiniLM(),
    )
    after = {str(path): _digest(path) for path in watched}
    assert before == after
    corpus_ids = {item["id"] for item in eval_mod.load_json(DEFAULT_META)}
    for row in result["runtime"]["vector"]["rows"]:
        assert row["channel"] == "vector"
        assert set(row["ranked_ids"]) <= corpus_ids
    assert result["bm25_query_expansion"] is False
    assert result["hybrid_weights"] == {"vector": 0.6, "bm25": 0.4}
    assert result["embedding_model"] == MODEL_NAME


def test_runtime_uses_make_query_for_eval_strings(monkeypatch, tmp_path: Path):
    meta = _tiny_corpus()
    vectors = np.eye(3, 4, dtype="float32")
    _write_index(tmp_path, vectors, meta)
    store = RAGStore(str(tmp_path))
    seen: list[dict] = []
    real = eval_runtime.make_query

    def _wrap(summary):
        seen.append(summary)
        return real(summary)

    monkeypatch.setattr(eval_runtime, "make_query", _wrap)
    eval_runtime.rank_runtime(
        "HEART score",
        store=store,
        model=_FakeMiniLM(
            dim=4, vector=np.array([[1.0, 0.0, 0.0, 0.0]], dtype="float32")
        ),
        bm25=None,
        mode="vector",
        k=1,
    )
    assert seen == [{"cc": "HEART score"}]


def test_committed_index_integrity_passes():
    info = eval_runtime.verify_runtime_index()
    assert info["ntotal"] == 49
    assert info["dim"] == 384
    assert info["type"] == "IndexFlatIP"
    assert info["model"] == MODEL_NAME
