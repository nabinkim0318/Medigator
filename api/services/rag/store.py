# api/services/rag/store.py
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import faiss  # pip install faiss-cpu
import numpy as np


class RAGStore:
    """
    Lightweight FAISS + metadata store.

    Layout (out_dir):
      - index.faiss : FAISS index built over chunk embeddings (normalized)
      - meta.json   : list[DocChunk-like dict] aligned with embedding rows
    """

    def __init__(self, out_dir: str | None = None):
        if out_dir is None:
            out_dir = os.getenv("RAG_INDEX_DIR", "rag_index")
        self.dir = Path(out_dir)
        self.index_path = self.dir / "index.faiss"
        self.meta_path = self.dir / "meta.json"

        if not self.index_path.exists() or not self.meta_path.exists():
            raise FileNotFoundError(
                f"Missing index/meta under {self.dir}. "
                f"Expected {self.index_path.name} and {self.meta_path.name}. "
                f"Build with api.services.rag.index.build_index().",
            )

        # Load index
        self.index: faiss.Index = faiss.read_index(str(self.index_path))

        # Load meta
        self.meta: list[dict[str, Any]] = json.loads(self.meta_path.read_text(encoding="utf-8"))
        if not isinstance(self.meta, list) or not self.meta:
            raise RuntimeError("meta.json is empty or invalid")

        # Quick consistency checks
        self._dim = self.index.d
        self._rows = self.index.ntotal
        if self._rows != len(self.meta):
            # Downgrade to warning + slice based on the length of the meta
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(
                f"Index/Meta size mismatch: index rows={self._rows}, meta rows={len(self.meta)}. "
                f"Adjusting to smaller size for hackathon compatibility.",
            )
            min_rows = min(self._rows, len(self.meta))
            self.meta = self.meta[:min_rows]
            self._rows = min_rows

        # Simple per-process cache for get_meta()
        self._meta_cache: dict[int, dict[str, Any]] = {}

    @property
    def dim(self) -> int:
        return self._dim

    @property
    def size(self) -> int:
        return self._rows

    def search(self, q_emb: np.ndarray, top_k: int = 8) -> list[tuple[int, float]]:
        """
        q_emb: shape (1, d) or (d,) normalized (cosine via IndexFlatIP)
        returns: list of (meta_index, score) in descending score order
        """
        if q_emb is None:
            return []
        q = np.asarray(q_emb, dtype="float32")
        if q.ndim == 1:
            q = q[None, :]
        if q.shape[1] != self._dim:
            raise ValueError(f"Query dim {q.shape[1]} != index dim {self._dim}")

        # (1, top_k)
        scores, ids = self.index.search(q, min(top_k, self._rows))
        # ids is shape (1, k), scores (1, k)
        idxs = ids[0].tolist()
        scrs = scores[0].tolist()

        results: list[tuple[int, float]] = []
        for i, s in zip(idxs, scrs, strict=False):
            if i == -1:
                continue
            results.append((int(i), float(s)))
        return results

    def get_meta(self, i: int) -> dict[str, Any]:
        """
        Return metadata dict for row i.
        """
        if i < 0 or i >= self._rows:
            raise IndexError(f"meta index {i} out of range [0, {self._rows})")
        if i in self._meta_cache:
            return self._meta_cache[i]
        m = self.meta[i]
        # optionally ensure minimal keys exist
        # defaults for optional fields
        m.setdefault("url", None)
        self._meta_cache[i] = m
        return m

    def get_corpus_texts(self) -> list[str]:
        """
        Provide raw chunk texts for BM25 corpus.
        """
        texts: list[str] = []
        for m in self.meta:
            t = (m.get("text") or "").strip()
            if t:
                texts.append(t)
        return texts

    # Optional helper: retrieve by id string (e.g., "file__0001")
    def find_index_by_id(self, chunk_id: str) -> int | None:
        for i, m in enumerate(self.meta):
            if m.get("id") == chunk_id:
                return i
        return None
