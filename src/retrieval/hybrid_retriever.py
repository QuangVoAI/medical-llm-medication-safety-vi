"""Hybrid BM25 + vector retrieval."""

from __future__ import annotations

from pathlib import Path

from src.safety_taxonomy import SafetyCategory

from .bm25 import BM25Retriever
from .documents import RetrievalDocument, load_default_documents
from .reranker import rerank
from .vector_store import VectorRetriever


class HybridRetriever:
    def __init__(
        self,
        documents: list[RetrievalDocument] | None = None,
        use_sentence_transformers: bool = True,
        embedding_cache_path: str | Path | None = None,
    ):
        self.documents = documents or load_default_documents()
        self.bm25 = BM25Retriever(self.documents)

        # Set default cache path if not provided
        if embedding_cache_path is None:
            embedding_cache_path = Path(__file__).parent.parent.parent / ".embeddings_cache.json"

        self.vector = VectorRetriever(
            self.documents,
            use_sentence_transformers=use_sentence_transformers,
            cache_path=embedding_cache_path,
        )

    def search(
        self,
        query: str,
        category: SafetyCategory,
        top_k: int = 3,
    ) -> list[tuple[RetrievalDocument, float, str]]:
        """Hybrid search combining BM25 and semantic search.

        Returns:
            List of (document, combined_score, retrieval_source) tuples.
        """
        candidates: dict[str, tuple[RetrievalDocument, float, str]] = {}

        # BM25 keyword search
        for doc, score in self.bm25.search(query, top_k=8):
            candidates[doc.doc_id] = (doc, score, "bm25")

        # Vector semantic search
        for doc, score in self.vector.search(query, top_k=8):
            if doc.doc_id in candidates:
                old_doc, old_score, old_source = candidates[doc.doc_id]
                # Combine scores: BM25 + semantic similarity
                combined_score = old_score + score * 0.5  # Weight semantic search slightly less
                candidates[doc.doc_id] = (old_doc, combined_score, f"{old_source}+semantic")
            else:
                candidates[doc.doc_id] = (doc, score, "semantic")

        return rerank(query, category, list(candidates.values()), top_k=top_k)

