# api/services/rag/index.py
from __future__ import annotations

import json
import logging
import re
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import faiss
import numpy as np
from sentence_transformers import (
    SentenceTransformer,
)  # pip install sentence-transformers

# Get logger
logger = logging.getLogger(__name__)

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
# 4. Token length overflow prevention - MiniLM input length consideration
DEFAULT_CHUNK_SIZE = 800  # target characters per chunk (≈256 tokens)
DEFAULT_CHUNK_OVERLAP = 200  # overlap for context preservation
VALID_EXTS = {".txt", ".md"}  # keep it simple for hackathon

SENTENCE_SPLIT = re.compile(r"(?<=[\.\!\?\n])\s+")


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
    logger.info(f"Starting RAG index build: docs_dir={docs_dir}, out_dir={out_dir}")
    logger.info(
        f"Parameters: chunk_size={chunk_size}, overlap={overlap}, max_docs={max_docs}"
    )

    docs_path = Path(docs_dir)
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    files = list(_iter_files(docs_path))
    if max_docs is not None:
        files = files[:max_docs]

    if not files:
        logger.error(f"No documents found under {docs_path} (expected .txt/.md)")
        raise RuntimeError(f"No documents found under {docs_path} (expected .txt/.md)")

    logger.info(f"Found {len(files)} documents to process")
    model = SentenceTransformer(model_name)
    logger.info(f"Loaded model: {model_name}")

    all_chunks: list[DocChunk] = []
    all_texts: list[str] = []

    for fi, f in enumerate(files):
        logger.info(f"Processing file {fi + 1}/{len(files)}: {f.name}")
        raw = _read_file(f)
        sents = _sentences(raw)
        chs = _chunk_sentences(sents, chunk_size=chunk_size, overlap=overlap)
        title = _title_from_path(f)
        source = title  # simple source label
        logger.debug(f"File {f.name}: {len(chs)} chunks created")

        # 5. Fill metadata fields (year/section/tags)
        year = None
        m = re.search(r"(19|20)\d{2}", f.name)
        if m:
            year = int(m.group(0))

        # Tag inference based on filename
        tags_json = {
            "type": "guideline" if "guideline" in f.name.lower() else "document"
        }

        for ci, (txt, start, end) in enumerate(chs):
            cid = f"{f.stem}__{ci:04d}"
            all_chunks.append(
                DocChunk(
                    id=cid,
                    title=title,
                    source=source,
                    text=txt,
                    file=str(f.relative_to(docs_path)),
                    start=start,
                    end=end,
                    url=None,
                    year=year,
                    section=None,
                    tags_json=tags_json,
                ),
            )
            all_texts.append(txt)

    if not all_texts:
        logger.error("No chunks produced. Check your documents or chunking parameters.")
        raise RuntimeError(
            "No chunks produced. Check your documents or chunking parameters."
        )

    logger.info(f"Total chunks created: {len(all_chunks)}")
    logger.info("Generating embeddings...")

    # Embeddings
    embeddings = model.encode(all_texts, batch_size=64, show_progress_bar=True)
    embeddings = np.asarray(embeddings).astype("float32")
    embeddings = _normalize(embeddings)

    d = embeddings.shape[1]
    logger.info(f"Embedding dimension: {d}")

    index = faiss.IndexFlatIP(d)  # cosine via normalized vectors
    index.add(embeddings)
    logger.info("FAISS index created and populated")

    # Persist
    logger.info("Saving index and metadata...")
    faiss.write_index(index, str(out_path / "index.faiss"))

    meta = [asdict(ch) for ch in all_chunks]
    (out_path / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    summary = {
        "docs_dir": str(docs_path),
        "out_dir": str(out_path),
        "model": model_name,
        "chunks": len(all_chunks),
        "dim": d,
        "files_indexed": len(files),
        "index_path": str(out_path / "index.faiss"),
        "meta_path": str(out_path / "meta.json"),
    }
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


if __name__ == "__main__":
    # Quick CLI build: python -m api.services.rag.index
    info = build_index()
    print(json.dumps(info, indent=2, ensure_ascii=False))
