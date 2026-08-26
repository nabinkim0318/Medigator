from __future__ import annotations

import importlib
import sys
from pathlib import Path

import numpy as np
import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.core.config import Settings, settings as app_settings
from api.services.rag import eval_runtime
from api.services.rag.retrieve import (
    HYBRID_W_BM25,
    HYBRID_W_EMB,
    _merge_scores,
    make_query,
    retrieval_mode_flags,
    retrieve,
    settings as rag_settings,
)

retrieve_mod = importlib.import_module("api.services.rag.retrieve")


class _FakeStore:
    def __init__(self) -> None:
        self.search_calls = 0

    def search(self, q_emb, top_k):  # noqa: ARG002
        self.search_calls += 1
        return [(0, 1.0), (1, 0.0)][:top_k]

    def get_meta(self, idx: int) -> dict[str, object]:
        return {
            "id": f"chunk-{idx}",
            "title": "t",
            "text": "x",
            "file": "a.md",
            "start": 0,
            "end": 1,
        }


class _FakeBM25:
    def __init__(self) -> None:
        self.score_calls = 0

    def get_scores(self, tokens):  # noqa: ARG002
        self.score_calls += 1
        return [0.0, 1.0]


class _FakeModel:
    def __init__(self) -> None:
        self.encode_calls = 0

    def encode(self, texts, normalize_embeddings=True):  # noqa: ARG002
        self.encode_calls += 1
        return [[1.0, 0.0, 0.0, 0.0]]


class _BenchModel:
    def encode(self, texts, normalize_embeddings=True):  # noqa: ARG002
        vec = np.zeros((1, 384), dtype="float32")
        vec[0, 0] = 1.0
        return vec


def _enable_retriever(monkeypatch, store, bm25, model: _FakeModel | None = None):
    monkeypatch.setattr(retrieve_mod, "USE_RAG", True)
    monkeypatch.setattr(retrieve_mod, "_store", store)
    monkeypatch.setattr(retrieve_mod, "_bm25", bm25)
    if model is None:
        monkeypatch.setattr(
            retrieve_mod,
            "_get_model",
            lambda: (_ for _ in ()).throw(AssertionError("MiniLM should not load")),
        )
    else:
        monkeypatch.setattr(retrieve_mod, "_get_model", lambda: model)


def test_default_retrieval_mode_is_bm25(monkeypatch):
    monkeypatch.delenv("RAG_RETRIEVAL_MODE", raising=False)
    fresh = Settings(_env_file=None)
    assert fresh.rag_retrieval_mode == "bm25"
    assert retrieval_mode_flags(fresh.rag_retrieval_mode) == (False, True)


def test_retrieve_default_path_uses_bm25_not_hybrid(monkeypatch):
    monkeypatch.delenv("RAG_RETRIEVAL_MODE", raising=False)
    monkeypatch.setattr(rag_settings, "rag_retrieval_mode", "bm25")
    captured: dict[str, object] = {}
    real_rank = retrieve_mod.rank_channels

    def _wrap(query_dict, **kwargs):
        captured.update(kwargs)
        return real_rank(query_dict, **kwargs)

    store = _FakeStore()
    bm25 = _FakeBM25()
    _enable_retriever(monkeypatch, store, bm25)
    monkeypatch.setattr(retrieve_mod, "rank_channels", _wrap)

    results = retrieve({"cc": "chest pain"}, k=1)

    assert captured["use_vector"] is False
    assert captured["use_bm25"] is True
    assert captured["model"] is None
    assert store.search_calls == 0
    assert bm25.score_calls == 1
    assert results
    assert results[0]["chunk"]["id"] == "chunk-1"


def test_bm25_mode_does_not_encode_with_minilm(monkeypatch):
    model = _FakeModel()
    store = _FakeStore()
    bm25 = _FakeBM25()
    monkeypatch.setattr(rag_settings, "rag_retrieval_mode", "bm25")
    _enable_retriever(monkeypatch, store, bm25, model=None)

    results = retrieve({"cc": "alpha token"}, k=2)

    assert model.encode_calls == 0
    assert store.search_calls == 0
    assert bm25.score_calls == 1
    assert [item["chunk"]["id"] for item in results] == ["chunk-1", "chunk-0"]


def test_vector_mode_disables_bm25_contribution(monkeypatch):
    model = _FakeModel()
    store = _FakeStore()
    bm25 = _FakeBM25()
    monkeypatch.setattr(rag_settings, "rag_retrieval_mode", "vector")
    _enable_retriever(monkeypatch, store, bm25, model=model)

    results = retrieve({"cc": "alpha token"}, k=2)

    assert model.encode_calls == 1
    assert store.search_calls == 1
    assert bm25.score_calls == 0
    assert [item["chunk"]["id"] for item in results] == ["chunk-0", "chunk-1"]


def test_hybrid_mode_uses_existing_weights(monkeypatch):
    model = _FakeModel()
    store = _FakeStore()
    bm25 = _FakeBM25()
    monkeypatch.setattr(rag_settings, "rag_retrieval_mode", "hybrid")
    _enable_retriever(monkeypatch, store, bm25, model=model)

    results = retrieve({"cc": "alpha token"}, k=2)

    assert model.encode_calls == 1
    assert store.search_calls == 1
    assert bm25.score_calls == 1
    expected = _merge_scores(
        [(0, 1.0), (1, 0.0)],
        [(0, 0.0), (1, 1.0)],
        w_emb=HYBRID_W_EMB,
        w_bm25=HYBRID_W_BM25,
    )
    assert HYBRID_W_EMB == 0.6
    assert HYBRID_W_BM25 == 0.4
    assert results[0]["chunk"]["id"] == "chunk-0"
    assert results[0]["score"] == pytest.approx(expected[0][1])
    assert expected[0][1] == pytest.approx(0.6)


def test_invalid_retrieval_mode_fails_clearly(monkeypatch):
    monkeypatch.setenv("RAG_RETRIEVAL_MODE", "foobar")
    with pytest.raises(ValidationError, match="bm25"):
        Settings(_env_file=None)
    with pytest.raises(ValueError, match="unsupported RAG_RETRIEVAL_MODE"):
        retrieval_mode_flags("foobar")
    monkeypatch.setattr(rag_settings, "rag_retrieval_mode", "foobar")
    monkeypatch.setattr(retrieve_mod, "USE_RAG", True)
    with pytest.raises(ValueError, match="unsupported RAG_RETRIEVAL_MODE"):
        retrieve({"cc": "x"})


def test_retrieval_mode_does_not_change_bm25_expansion_default(monkeypatch):
    monkeypatch.delenv("RAG_RETRIEVAL_MODE", raising=False)
    monkeypatch.delenv("BM25_QUERY_EXPANSION", raising=False)
    fresh = Settings(_env_file=None)
    assert fresh.rag_retrieval_mode == "bm25"
    assert fresh.bm25_query_expansion is False
    assert app_settings.bm25_query_expansion is False

    monkeypatch.setattr(rag_settings, "bm25_query_expansion", False)
    monkeypatch.setattr(rag_settings, "rag_retrieval_mode", "bm25")
    expansion_off = make_query({"cc": "a1c"})
    monkeypatch.setattr(rag_settings, "rag_retrieval_mode", "hybrid")
    still_off = make_query({"cc": "a1c"})
    assert expansion_off["bm25"] == ["a1c"]
    assert still_off["bm25"] == ["a1c"]
    assert expansion_off["embed"] == still_off["embed"]


def test_eval_runtime_still_scores_all_modes_when_default_is_bm25(monkeypatch):
    monkeypatch.setattr(rag_settings, "rag_retrieval_mode", "bm25")
    monkeypatch.setattr(eval_runtime.settings, "rag_retrieval_mode", "bm25")
    result = eval_runtime.evaluate_runtime(
        include_ci_baseline=False,
        model=_BenchModel(),
    )
    assert set(result["runtime"]) == {"bm25", "vector", "hybrid"}
    assert result["hybrid_weights"] == {"vector": 0.6, "bm25": 0.4}
    assert result["bm25_query_expansion"] is False


def test_retrieve_logs_are_mode_aware_and_query_free(monkeypatch):
    store = _FakeStore()
    bm25 = _FakeBM25()
    monkeypatch.setattr(rag_settings, "rag_retrieval_mode", "bm25")
    _enable_retriever(monkeypatch, store, bm25)
    messages: list[str] = []

    def _capture(msg, *args, **_kwargs):
        messages.append(msg % args if args else str(msg))

    monkeypatch.setattr(retrieve_mod.logger, "info", _capture)

    retrieve({"cc": "left-arm crushing pain with diaphoresis"}, k=1)

    text = " ".join(messages)
    assert "retrieval mode=bm25" in text
    assert "retrieval returned" in text
    assert "left-arm crushing pain" not in text
    assert "Hybrid ranking" not in text
