"""Vector retriever with optional sentence-transformers and pure-Python fallback."""

from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from .bm25 import tokenize
from .documents import RetrievalDocument

if TYPE_CHECKING:
    pass


def cosine(counter_a: Counter[str], counter_b: Counter[str]) -> float:
    shared = set(counter_a) & set(counter_b)
    dot = sum(counter_a[key] * counter_b[key] for key in shared)
    norm_a = math.sqrt(sum(value * value for value in counter_a.values()))
    norm_b = math.sqrt(sum(value * value for value in counter_b.values()))
    if not norm_a or not norm_b:
        return 0.0
    return dot / (norm_a * norm_b)


class VectorRetriever:
    """Semantic retriever.

    If sentence-transformers is available and `use_sentence_transformers=True`,
    it uses multilingual embeddings. Otherwise it falls back to token-vector
    cosine similarity so the repo still runs anywhere.
    """

    def __init__(
        self,
        documents: list[RetrievalDocument],
        model_name: str = "sentence-transformers/paraphrase-multilingual-minilm-l12-v2",
        use_sentence_transformers: bool = True,
        cache_path: str | Path | None = None,
    ):
        self.documents = documents
        self.model = None
        self.embeddings = None
        self.doc_vectors = [
            Counter(tokenize(f"{doc.title} {doc.text} {' '.join(doc.tags)}")) for doc in documents
        ]
        self.cache_path = Path(cache_path) if cache_path else None

        if use_sentence_transformers:
            try:
                from sentence_transformers import SentenceTransformer

                self.model = SentenceTransformer(model_name)

                # Try load cached embeddings first
                if self.cache_path and self.cache_path.exists():
                    self.embeddings = self._load_embeddings_cache()
                else:
                    # Generate embeddings
                    self.embeddings = self.model.encode(
                        [f"{doc.title}. {doc.text}" for doc in documents],
                        normalize_embeddings=True,
                        show_progress_bar=False,
                    )
                    # Save cache
                    if self.cache_path:
                        self._save_embeddings_cache()
            except Exception as exc:
                print(f"[warn] sentence-transformers unavailable, using fallback vector search: {exc}")
                self.model = None
                self.embeddings = None

    def _load_embeddings_cache(self) -> list[np.ndarray] | None:
        """Load cached embeddings from disk."""
        try:
            with open(self.cache_path) as f:
                data = json.load(f)
            return [np.array(emb) for emb in data["embeddings"]]
        except Exception:
            return None

    def _save_embeddings_cache(self) -> None:
        """Save embeddings to cache for faster subsequent loads."""
        if not self.embeddings or not self.cache_path:
            return
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_path, "w") as f:
            json.dump(
                {"embeddings": [emb.tolist() for emb in self.embeddings]},
                f,
            )

    def search(self, query: str, top_k: int = 5) -> list[tuple[RetrievalDocument, float]]:
        if self.model is not None and self.embeddings is not None:
            query_embedding = self.model.encode([query], normalize_embeddings=True, show_progress_bar=False)[0]
            scored = []
            for doc, doc_embedding in zip(self.documents, self.embeddings, strict=True):
                score = float(np.dot(query_embedding, doc_embedding))
                if score > 0:
                    scored.append((doc, score))
            scored.sort(key=lambda item: item[1], reverse=True)
            return scored[:top_k]

        query_vec = Counter(tokenize(query))
        scored = []
        for doc, doc_vec in zip(self.documents, self.doc_vectors, strict=True):
            score = cosine(query_vec, doc_vec)
            if score > 0:
                scored.append((doc, score))
        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[:top_k]

