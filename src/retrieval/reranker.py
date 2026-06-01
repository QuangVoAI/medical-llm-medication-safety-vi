"""Lightweight reranker for medication safety retrieval."""

from __future__ import annotations

from src.safety_taxonomy import SafetyCategory

from .bm25 import tokenize
from .documents import RetrievalDocument


def rerank(
    query: str,
    category: SafetyCategory,
    candidates: list[tuple[RetrievalDocument, float, str]],
    top_k: int = 3,
) -> list[tuple[RetrievalDocument, float, str]]:
    query_tokens = set(tokenize(query))
    category_tokens = set(tokenize(" ".join(category.keywords + category.must_include)))
    ranked = []
    for doc, score, source in candidates:
        doc_tokens = set(tokenize(f"{doc.title} {doc.text} {' '.join(doc.tags)}"))
        exact_overlap = len(query_tokens & doc_tokens)
        category_overlap = len(category_tokens & doc_tokens)
        policy_bonus = 0.5 if doc.source == "curated_safety_policy" else 0.0
        final_score = score + 0.15 * exact_overlap + 0.08 * category_overlap + policy_bonus
        ranked.append((doc, final_score, source))
    ranked.sort(key=lambda item: item[1], reverse=True)
    return ranked[:top_k]

