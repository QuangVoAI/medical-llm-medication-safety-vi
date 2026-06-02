"""Retrieval document definitions."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from src.rag_knowledge import KNOWLEDGE_BASE, KnowledgeSnippet


@dataclass(frozen=True)
class RetrievalDocument:
    doc_id: str
    title: str
    text: str
    source: str
    tags: tuple[str, ...] = ()


def load_json_knowledge_documents() -> list[KnowledgeSnippet]:
    """Load curated JSON knowledge docs without committing generated Python code."""

    doc_file = Path(__file__).resolve().parents[2] / "data" / "medical_documents.json"
    if not doc_file.exists():
        return []

    with doc_file.open("r", encoding="utf-8") as handle:
        rows = json.load(handle)

    snippets: list[KnowledgeSnippet] = []
    for row in rows:
        snippets.append(
            KnowledgeSnippet(
                title=row["title"],
                keywords=tuple(row["keywords"]),
                content=row["content"],
                action=row["action"],
            )
        )
    return snippets


def load_knowledge_base() -> list[KnowledgeSnippet]:
    """Return base snippets plus JSON-maintained medication-safety documents."""

    return list(KNOWLEDGE_BASE) + load_json_knowledge_documents()


def load_default_documents() -> list[RetrievalDocument]:
    docs: list[RetrievalDocument] = []
    for idx, snippet in enumerate(load_knowledge_base(), start=1):
        docs.append(
            RetrievalDocument(
                doc_id=f"safety-{idx}",
                title=snippet.title,
                text=f"{snippet.content} {snippet.action}",
                source="curated_safety_snippet",
                tags=snippet.keywords,
            )
        )
    docs.extend(
        [
            RetrievalDocument(
                doc_id="scope-ambiguous-pill",
                title="Không xác định thuốc bằng màu sắc",
                text=(
                    "Không thể xác định thuốc chỉ dựa vào màu sắc, hình dạng hoặc mô tả mơ hồ. "
                    "Cần tên thuốc, hoạt chất, hàm lượng, vỏ thuốc, đơn thuốc hoặc tư vấn dược sĩ."
                ),
                source="curated_safety_policy",
                tags=("viên thuốc", "màu xanh", "không biết thuốc", "liều"),
            ),
            RetrievalDocument(
                doc_id="scope-offtopic",
                title="Ngoài phạm vi medication safety",
                text=(
                    "Nếu câu hỏi không liên quan đến thuốc hoặc an toàn dùng thuốc, hệ thống nên nói rõ "
                    "ngoài phạm vi demo thay vì ép câu trả lời sang y tế."
                ),
                source="curated_safety_policy",
                tags=("thời tiết", "python", "code", "ngoài phạm vi"),
            ),
        ]
    )
    return docs
