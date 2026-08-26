# api/services/rag/index.py
from __future__ import annotations

import json
import logging
import re
from collections import Counter
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

try:
    import faiss
    import numpy as np
    from sentence_transformers import (
        SentenceTransformer,
    )
except ImportError:  # pragma: no cover - optional when RAG deps are absent
    faiss = None  # type: ignore
    np = None  # type: ignore
    SentenceTransformer = None  # type: ignore

# Get logger
logger = logging.getLogger(__name__)

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
# 4. Token length overflow prevention - MiniLM input length consideration
DEFAULT_CHUNK_SIZE = 800  # target characters per chunk (≈256 tokens)
DEFAULT_CHUNK_OVERLAP = 200  # overlap for context preservation
VALID_EXTS = {".txt", ".md"}  # keep it simple for hackathon

SENTENCE_SPLIT = re.compile(r"(?<=[\.\!\?\n])\s+")
# Frozen-index extra: discovered at original build, produced no chunks.
ORIGINAL_ZERO_CHUNK_FILES = ("prompts.md",)


@dataclass
class DocChunk:
    id: str
    title: str
    source: str
    text: str
    file: str
    start: int
    end: int
    url: str | None = None
    year: int | None = None
    section: str | None = None
    tags_json: dict[str, Any] | None = None


def _iter_files(docs_dir: Path) -> Iterable[Path]:
    for p in sorted(docs_dir.rglob("*")):
        if p.is_file() and p.suffix.lower() in VALID_EXTS:
            yield p


def _read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        # fallback to latin-1 if needed
        return path.read_text(encoding="latin-1", errors="ignore")


def _sentences(text: str) -> list[str]:
    # light-weight sentence split; keeps punctuation
    text = re.sub(r"\r\n?", "\n", text).strip()
    if not text:
        return []
    return [s.strip() for s in SENTENCE_SPLIT.split(text) if s.strip()]


def _chunk_sentences(
    sents: list[str],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[tuple[str, int, int]]:
    """
    Return list of (chunk_text, start_char_idx, end_char_idx) on the original joined string.
    Uses char-length packing with sentence boundaries and char-based overlap.
    """
    if not sents:
        return []

    joined = ""
    offsets = []  # sentence start offsets in joined
    for s in sents:
        start = len(joined)
        joined += s + " "
        offsets.append(start)
    joined = joined.strip()

    chunks = []
    i = 0
    N = len(sents)

    while i < N:
        # greedily add sentences up to chunk_size (chars)
        start_sent = i
        start_char = offsets[start_sent]
        cur_end_char = start_char
        while i < N:
            cand_end_char = offsets[i] + len(sents[i])
            if cand_end_char - start_char > chunk_size and i > start_sent:
                break
            cur_end_char = cand_end_char
            i += 1

        chunk_text = joined[start_char:cur_end_char].strip()
        chunks.append((chunk_text, start_char, cur_end_char))

        if i >= N:
            break

        # compute next window start by char overlap
        next_start_char = max(start_char, cur_end_char - overlap)
        # map back to nearest sentence index whose start >= next_start_char
        # find smallest j >= start_sent such that offsets[j] >= next_start_char
        j = start_sent
        while j < N and offsets[j] < next_start_char:
            j += 1
        i = j if j > start_sent else start_sent + 1

    return chunks


def _normalize(vecs: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-12
    return vecs / norms


def _title_from_path(p: Path) -> str:
    return p.stem.replace("_", " ").replace("-", " ").strip().title()


def _zero_chunk_reason(raw: str, sents: list[str]) -> str:
    if not raw.strip():
        return "empty_text"
    if not sents:
        return "no_sentences"
    return "no_chunks"


def _file_chunks(
    path: Path,
    docs_path: Path,
    *,
    chunk_size: int,
    overlap: int,
) -> tuple[list[DocChunk], dict[str, Any]]:
    raw = _read_file(path)
    sents = _sentences(raw)
    packed = _chunk_sentences(sents, chunk_size=chunk_size, overlap=overlap)
    rel = str(path.relative_to(docs_path))
    if not packed:
        return [], {
            "file": rel,
            "status": "zero_chunk",
            "chunks": 0,
            "sentences": len(sents),
            "reason": _zero_chunk_reason(raw, sents),
        }

    title = _title_from_path(path)
    year = None
    matched = re.search(r"(19|20)\d{2}", path.name)
    if matched:
        year = int(matched.group(0))
    tags_json = {
        "type": "guideline" if "guideline" in path.name.lower() else "document"
    }
    chunks: list[DocChunk] = []
    for index, (txt, start, end) in enumerate(packed):
        chunks.append(
            DocChunk(
                id=f"{path.stem}__{index:04d}",
                title=title,
                source=title,
                text=txt,
                file=rel,
                start=start,
                end=end,
                url=None,
                year=year,
                section=None,
                tags_json=tags_json,
            )
        )
    return chunks, {
        "file": rel,
        "status": "indexed",
        "chunks": len(chunks),
        "sentences": len(sents),
    }


def inventory_corpus(
    docs_dir: str = "docs",
    *,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
    max_docs: int | None = None,
) -> dict[str, Any]:
    """Inventory discovered files and chunks without loading MiniLM."""
    docs_path = Path(docs_dir)
    discovered = list(_iter_files(docs_path))
    if max_docs is None:
        to_process, skipped = discovered, []
    else:
        to_process, skipped = discovered[:max_docs], discovered[max_docs:]

    records: list[dict[str, Any]] = []
    all_chunks: list[DocChunk] = []
    for path in to_process:
        chunks, record = _file_chunks(
            path, docs_path, chunk_size=chunk_size, overlap=overlap
        )
        records.append(record)
        all_chunks.extend(chunks)
    for path in skipped:
        records.append(
            {
                "file": str(path.relative_to(docs_path)),
                "status": "skipped",
                "chunks": 0,
                "reason": "max_docs",
            }
        )
    records.sort(key=lambda item: str(item["file"]))
    with_chunks = sum(1 for item in records if item["status"] == "indexed")
    zero_chunk = sum(1 for item in records if item["status"] == "zero_chunk")
    skipped_count = sum(1 for item in records if item["status"] == "skipped")
    logger.info(
        "corpus inventory discovered=%s with_chunks=%s zero_chunk=%s skipped=%s",
        len(discovered),
        with_chunks,
        zero_chunk,
        skipped_count,
    )
    return {
        "docs_dir": str(docs_path),
        "files_discovered": len(discovered),
        "files_indexed": len(to_process),
        "files_with_chunks": with_chunks,
        "files_zero_chunk": zero_chunk,
        "files_skipped": skipped_count,
        "chunks": len(all_chunks),
        "files": records,
        "all_chunks": all_chunks,
    }


def summary_from_inventory(
    inventory: dict[str, Any],
    *,
    model_name: str = MODEL_NAME,
    dim: int | None = None,
    out_dir: str = "rag_index",
) -> dict[str, Any]:
    """Public build-summary payload (no chunk texts)."""
    out_path = Path(out_dir)
    payload = {
        "docs_dir": inventory["docs_dir"],
        "out_dir": str(out_path),
        "model": model_name,
        "chunks": inventory["chunks"],
        "dim": dim,
        "files_indexed": inventory["files_indexed"],
        "files_discovered": inventory["files_discovered"],
        "files_with_chunks": inventory["files_with_chunks"],
        "files_zero_chunk": inventory["files_zero_chunk"],
        "files_skipped": inventory["files_skipped"],
        "index_path": str(out_path / "index.faiss"),
        "meta_path": str(out_path / "meta.json"),
        "files": inventory["files"],
    }
    return payload


def frozen_index_provenance(
    *,
    meta_path: str | Path = "rag_index/meta.json",
    docs_dir: str | Path = "docs",
    out_dir: str = "rag_index",
    model_name: str = MODEL_NAME,
    dim: int = 384,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> dict[str, Any]:
    """Explain the committed index build: 15 discovered files, 14 with chunks."""
    docs_path = Path(docs_dir)
    meta = json.loads(Path(meta_path).read_text(encoding="utf-8"))
    counts = Counter(str(item.get("file") or "") for item in meta)
    records: list[dict[str, Any]] = []
    for rel, n_chunks in sorted(counts.items()):
        if not rel:
            continue
        records.append({"file": rel, "status": "indexed", "chunks": n_chunks})
    for rel in ORIGINAL_ZERO_CHUNK_FILES:
        _chunks, record = _file_chunks(
            docs_path / rel,
            docs_path,
            chunk_size=chunk_size,
            overlap=overlap,
        )
        records.append(record)
    records.sort(key=lambda item: str(item["file"]))
    with_chunks = sum(1 for item in records if item["status"] == "indexed")
    zero_chunk = sum(1 for item in records if item["status"] == "zero_chunk")
    processed = with_chunks + zero_chunk
    return {
        "docs_dir": str(docs_path),
        "out_dir": out_dir,
        "model": model_name,
        "chunks": len(meta),
        "dim": dim,
        "files_indexed": processed,
        "files_discovered": processed,
        "files_with_chunks": with_chunks,
        "files_zero_chunk": zero_chunk,
        "files_skipped": 0,
        "index_path": str(Path(out_dir) / "index.faiss"),
        "meta_path": str(Path(out_dir) / "meta.json"),
        "files": records,
        "note": (
            "files_indexed counts .txt/.md files processed at the original "
            "frozen-index build. One discovered file produced zero chunks, so "
            "meta.json contains 14 files. This describes that build, not a live "
            "rescan of docs/."
        ),
    }


def build_index(
    docs_dir: str = "docs",
    out_dir: str = "rag_index",
    model_name: str = MODEL_NAME,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
    max_docs: int | None = None,
) -> dict[str, Any]:
    """
    Build FAISS index and metadata from local docs.
    Returns a small summary dict.
    """
    if SentenceTransformer is None or faiss is None or np is None:
        raise RuntimeError("RAG index dependencies are not installed")
    logger.info(
        "index build chunk_size=%s overlap=%s max_docs=%s",
        chunk_size,
        overlap,
        max_docs,
    )

    inventory = inventory_corpus(
        docs_dir,
        chunk_size=chunk_size,
        overlap=overlap,
        max_docs=max_docs,
    )
    if inventory["files_discovered"] == 0:
        logger.error("No documents found under %s (expected .txt/.md)", docs_dir)
        raise RuntimeError(f"No documents found under {docs_dir} (expected .txt/.md)")
    all_chunks: list[DocChunk] = inventory["all_chunks"]
    if not all_chunks:
        logger.error("No chunks produced. Check your documents or chunking parameters.")
        raise RuntimeError(
            "No chunks produced. Check your documents or chunking parameters."
        )

    model = SentenceTransformer(model_name)
    logger.info("Loaded model: %s", model_name)
    embeddings = model.encode(
        [chunk.text for chunk in all_chunks],
        batch_size=64,
        show_progress_bar=True,
    )
    embeddings = np.asarray(embeddings).astype("float32")
    embeddings = _normalize(embeddings)
    dim = int(embeddings.shape[1])

    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(out_path / "index.faiss"))
    (out_path / "meta.json").write_text(
        json.dumps(
            [asdict(chunk) for chunk in all_chunks], ensure_ascii=False, indent=2
        ),
        encoding="utf-8",
    )
    summary = summary_from_inventory(
        inventory, model_name=model_name, dim=dim, out_dir=out_dir
    )
    (out_path / "build_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return summary


def load_index(out_dir: str = "rag_index") -> tuple[faiss.Index, list[dict[str, Any]]]:
    """
    Load FAISS index and metadata list.
    """
    out_path = Path(out_dir)
    index_path = out_path / "index.faiss"
    meta_path = out_path / "meta.json"

    if not index_path.exists() or not meta_path.exists():
        raise FileNotFoundError(
            f"Missing index/meta in {out_path}. Run build_index() first."
        )

    index = faiss.read_index(str(index_path))
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    return index, meta


def main(argv: list[str] | None = None) -> int:
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Build or inventory the local RAG corpus. Inventory does not load MiniLM."
    )
    parser.add_argument("--docs-dir", default="docs")
    parser.add_argument("--out-dir", default="rag_index")
    parser.add_argument("--max-docs", type=int, default=None)
    parser.add_argument(
        "--inventory-only",
        action="store_true",
        help="Record discovered/indexed/zero_chunk/skipped files without embedding",
    )
    args = parser.parse_args(argv)
    if args.inventory_only:
        inventory = inventory_corpus(args.docs_dir, max_docs=args.max_docs)
        print(
            json.dumps(
                summary_from_inventory(inventory, out_dir=args.out_dir), indent=2
            )
        )
        return 0
    try:
        print(
            json.dumps(
                build_index(
                    docs_dir=args.docs_dir, out_dir=args.out_dir, max_docs=args.max_docs
                ),
                indent=2,
            )
        )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
