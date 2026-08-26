from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.services.rag.eval import (
    DEFAULT_FAISS,
    DEFAULT_MANIFEST,
    DEFAULT_META,
    DEFAULT_QUERIES,
)
from api.services.rag.index import (
    ORIGINAL_ZERO_CHUNK_FILES,
    frozen_index_provenance,
    inventory_corpus,
    main as index_main,
)

ROOT = Path(__file__).resolve().parents[2]
FROZEN_META = "2063bdbc89d08adf662d0f93528b56986a524a87ec6af1813cb25d4b532c13b5"
FROZEN_FAISS = "8e8280e2a45640d1fdaa3bae671d8b666251658ed94f0e0e876d537891c86eeb"
FROZEN_QUERIES = "dc26206b31b78ef7da9b8fae1e9b84a6617de578c8704910ebbe2cc5aff06409"


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_inventory_records_discovered_indexed_skipped_and_zero_chunk(tmp_path: Path):
    (tmp_path / "keep.md").write_text(
        "Chest pain is a symptom. Risk scores help.", encoding="utf-8"
    )
    (tmp_path / "empty.md").write_text("", encoding="utf-8")
    (tmp_path / "later.md").write_text(
        "Third file should be skipped.", encoding="utf-8"
    )
    (tmp_path / "notes.json").write_text("{}", encoding="utf-8")

    inventory = inventory_corpus(str(tmp_path), max_docs=2)
    by_file = {item["file"]: item for item in inventory["files"]}

    assert inventory["files_discovered"] == 3
    assert inventory["files_indexed"] == 2
    assert inventory["files_with_chunks"] == 1
    assert inventory["files_zero_chunk"] == 1
    assert inventory["files_skipped"] == 1
    assert by_file["keep.md"]["status"] == "indexed"
    assert by_file["keep.md"]["chunks"] >= 1
    assert by_file["empty.md"]["status"] == "zero_chunk"
    assert by_file["empty.md"]["reason"] == "empty_text"
    assert by_file["empty.md"]["chunks"] == 0
    assert by_file["keep.md"]["sha256"] == _digest(tmp_path / "keep.md")
    assert by_file["empty.md"]["sha256"] == _digest(tmp_path / "empty.md")
    assert by_file["later.md"]["status"] == "skipped"
    assert by_file["later.md"]["reason"] == "max_docs"
    assert "notes.json" not in by_file


def test_frozen_index_fifteen_vs_fourteen_is_empty_prompts_md():
    summary = json.loads((ROOT / "rag_index" / "build_summary.json").read_text())
    meta = json.loads(DEFAULT_META.read_text(encoding="utf-8"))
    meta_files = sorted({item["file"] for item in meta})
    records = {item["file"]: item for item in summary["files"]}

    assert summary["files_indexed"] == 15
    assert summary["files_discovered"] == 15
    assert summary["files_with_chunks"] == 14
    assert summary["files_zero_chunk"] == 1
    assert summary["files_skipped"] == 0
    assert summary["chunks"] == 49
    assert len(meta_files) == 14
    assert set(meta_files) == {
        name for name, item in records.items() if item["status"] == "indexed"
    }
    assert ORIGINAL_ZERO_CHUNK_FILES == ("prompts.md",)
    assert records["prompts.md"]["status"] == "zero_chunk"
    assert records["prompts.md"]["reason"] == "empty_text"
    assert records["prompts.md"]["chunks"] == 0
    assert "prompts.md" not in meta_files
    for rel in meta_files:
        assert records[rel]["chunks"] == sum(1 for item in meta if item["file"] == rel)
        assert records[rel]["sha256"] == _digest(ROOT / "docs" / rel)
    assert records["prompts.md"]["sha256"] == _digest(ROOT / "docs" / "prompts.md")


def test_original_fifteen_file_set_explains_zero_chunk_without_minilm(tmp_path: Path):
    meta = json.loads(DEFAULT_META.read_text(encoding="utf-8"))
    docs = ROOT / "docs"
    names = sorted({item["file"] for item in meta} | set(ORIGINAL_ZERO_CHUNK_FILES))
    for rel in names:
        dest = tmp_path / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes((docs / rel).read_bytes())

    inventory = inventory_corpus(str(tmp_path))
    zero = [
        item["file"] for item in inventory["files"] if item["status"] == "zero_chunk"
    ]
    indexed = {
        item["file"] for item in inventory["files"] if item["status"] == "indexed"
    }

    assert inventory["files_discovered"] == 15
    assert inventory["files_with_chunks"] == 14
    assert inventory["files_zero_chunk"] == 1
    assert inventory["files_skipped"] == 0
    assert inventory["chunks"] == 49
    assert zero == ["prompts.md"]
    assert "prompts.md" not in indexed


def test_inventory_only_cli_does_not_require_minilm(tmp_path: Path, monkeypatch):
    (tmp_path / "doc.md").write_text(
        "Troponin testing is used in chest pain.", encoding="utf-8"
    )
    monkeypatch.setattr("api.services.rag.index.SentenceTransformer", None)
    assert (
        index_main(
            [
                "--docs-dir",
                str(tmp_path),
                "--out-dir",
                str(tmp_path / "out"),
                "--inventory-only",
            ]
        )
        == 0
    )


def test_frozen_retrieval_artifacts_were_not_rebuilt():
    committed = json.loads(DEFAULT_MANIFEST.read_text(encoding="utf-8"))
    assert _digest(DEFAULT_META) == FROZEN_META == committed["meta.json"]
    assert _digest(DEFAULT_FAISS) == FROZEN_FAISS == committed["index.faiss"]
    assert _digest(DEFAULT_QUERIES) == FROZEN_QUERIES == committed["eval_queries.json"]
    live = frozen_index_provenance()
    assert live["files_indexed"] == 15
    assert live["files_with_chunks"] == 14
    assert live["files_zero_chunk"] == 1
    assert (
        _digest(ROOT / "rag_index" / "build_summary.json")
        == committed["build_summary.json"]
    )
    indexed = [item for item in live["files"] if item["status"] == "indexed"]
    for item in indexed:
        assert item["sha256"] == committed["source_files"][item["file"]]


def test_default_inventory_uses_fourteen_source_manifest_not_project_docs():
    inventory = inventory_corpus(str(ROOT / "docs"))
    names = {item["file"] for item in inventory["files"]}
    assert inventory["files_discovered"] == 14
    assert inventory["files_with_chunks"] == 14
    assert inventory["files_zero_chunk"] == 0
    assert inventory["chunks"] == 49
    assert "API.md" not in names
    assert "RAG.md" not in names
    assert "SECURITY.md" not in names
    assert "prompts.md" not in names
    assert "diabetes_management.txt" in names
    assert "rag/reviews/2013_HEART-Score.md" in names


def test_source_manifest_ignores_unrelated_docs(tmp_path: Path):
    (tmp_path / "keep.md").write_text("Chest pain protocol.", encoding="utf-8")
    (tmp_path / "API.md").write_text(
        "# Project API docs should not be indexed.", encoding="utf-8"
    )
    manifest = tmp_path / "corpus_sources.json"
    manifest.write_text(
        json.dumps({"schema_version": 1, "sources": ["keep.md"]}),
        encoding="utf-8",
    )
    inventory = inventory_corpus(str(tmp_path), source_manifest=manifest)
    names = {item["file"] for item in inventory["files"]}
    assert names == {"keep.md"}
    assert inventory["files_discovered"] == 1
    assert inventory["files_with_chunks"] == 1
    assert "API.md" not in names
