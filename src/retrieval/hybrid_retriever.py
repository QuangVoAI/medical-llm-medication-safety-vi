"""Hybrid BM25 + vector retrieval."""

from __future__ import annotations

from src.safety_taxonomy import SafetyCategory

from .bm25 import BM25Retriever
from .documents import RetrievalDocument, load_default_documents
from .reranker import rerank
from .vector_store import VectorRetriever


class HybridRetriever:
    def __init__(self, documents: list[RetrievalDocument] | None = None, use_sentence_transformers: bool = False):
        self.documents = documents or load_default_documents()
        self.bm25 = BM25Retriever(self.documents)
        self.vector = VectorRetriever(self.documents, use_sentence_transformers=use_sentence_transformers)

    def search(self, query: str, category: SafetyCategory, top_k: int = 3) -> list[tuple[RetrievalDocument, float, str]]:
        candidates: dict[str, tuple[RetrievalDocument, float, str]] = {}

        for doc, score in self.bm25.search(query, top_k=8):
            candidates[doc.doc_id] = (doc, score, "bm25")

        for doc, score in self.vector.search(query, top_k=8):
            if doc.doc_id in candidates:
                old_doc, old_score, old_source = candidates[doc.doc_id]
                candidates[doc.doc_id] = (old_doc, old_score + score, f"{old_source}+vector")
            else:
                candidates[doc.doc_id] = (doc, score, "vector")

        return rerank(query, category, list(candidates.values()), top_k=top_k)

