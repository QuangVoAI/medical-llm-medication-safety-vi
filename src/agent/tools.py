"""Agent tools: normalization, entity extraction, query rewriting, retrieval."""

from __future__ import annotations

import re

from src.retrieval.hybrid_retriever import HybridRetriever
from src.safety_taxonomy import SafetyCategory
from src.vi_text import normalize_vi_text, remove_vietnamese_accents


DRUG_ALIASES = {
    "ibu": "ibuprofen",
    "ibuprofen": "ibuprofen",
    "warfarin": "warfarin",
    "para": "paracetamol",
    "paracetamol": "paracetamol",
    "aspirin": "aspirin",
    "insulin": "insulin",
    "ks": "kháng sinh",
    "khang sinh": "kháng sinh",
    "kháng sinh": "kháng sinh",
    "thuoc ngu": "thuốc ngủ",
    "thuốc ngủ": "thuốc ngủ",
}


def normalize_question(question: str) -> str:
    return normalize_vi_text(question)


def extract_drug_entities(question: str) -> list[str]:
    lowered = normalize_vi_text(question).lower()
    no_accent = remove_vietnamese_accents(lowered).lower()
    found = []
    for alias, canonical in DRUG_ALIASES.items():
        alias_norm = remove_vietnamese_accents(alias).lower()
        if re.search(rf"\b{re.escape(alias_norm)}\b", no_accent):
            found.append(canonical)
    return sorted(set(found))


def rewrite_query(question: str, category: SafetyCategory, entities: list[str]) -> str:
    entity_text = ", ".join(entities) if entities else "không rõ tên thuốc"
    return (
        f"Câu hỏi an toàn thuốc tiếng Việt. Risk category: {category.label}. "
        f"Thuốc/nhóm thuốc nhận diện: {entity_text}. Nội dung: {question}"
    )


def hybrid_retrieve(query: str, category: SafetyCategory, retriever: HybridRetriever):
    return retriever.search(query, category=category, top_k=3)

