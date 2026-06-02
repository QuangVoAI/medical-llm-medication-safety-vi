#!/usr/bin/env python3
"""Công cụ quản lý knowledge base medication safety."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class MedicalDocument:
    """Tài liệu y tế được thêm vào knowledge base."""

    title: str
    keywords: tuple[str, ...]
    content: str
    action: str
    source: str  # Nguồn tham khảo
    category: str  # Danh mục: "drug_interaction", "special_population", "safety", v.v.
    severity: str  # "high", "medium", "low"
    notes: str = ""


def load_medical_documents() -> list[MedicalDocument]:
    """Load tài liệu y tế từ JSON."""
    doc_file = Path(__file__).parent.parent / "data" / "medical_documents.json"
    if not doc_file.exists():
        print(f"Tệp {doc_file} chưa tồn tại. Khởi tạo...")
        return []

    with open(doc_file) as f:
        data = json.load(f)
        return [MedicalDocument(**doc) for doc in data]


def save_medical_documents(docs: list[MedicalDocument]) -> None:
    """Lưu tài liệu y tế vào JSON."""
    doc_file = Path(__file__).parent.parent / "data" / "medical_documents.json"
    doc_file.parent.mkdir(parents=True, exist_ok=True)

    with open(doc_file, "w") as f:
        json.dump([asdict(doc) for doc in docs], f, indent=2, ensure_ascii=False)
    print(f"✓ Lưu {len(docs)} tài liệu vào {doc_file}")


def add_document(
    title: str,
    keywords: list[str],
    content: str,
    action: str,
    source: str,
    category: str,
    severity: str,
    notes: str = "",
) -> None:
    """Thêm tài liệu y tế mới."""
    docs = load_medical_documents()
    new_doc = MedicalDocument(
        title=title,
        keywords=tuple(keywords),
        content=content,
        action=action,
        source=source,
        category=category,
        severity=severity,
        notes=notes,
    )
    docs.append(new_doc)
    save_medical_documents(docs)
    print(f"✓ Thêm tài liệu: {title}")


def list_documents(category: str | None = None) -> None:
    """Liệt kê tài liệu theo danh mục."""
    docs = load_medical_documents()
    if category:
        docs = [d for d in docs if d.category == category]

    print(f"\n📋 Tổng: {len(docs)} tài liệu\n")
    for i, doc in enumerate(docs, 1):
        print(f"{i}. {doc.title}")
        print(f"   Danh mục: {doc.category} | Mức độ: {doc.severity}")
        print(f"   Nguồn: {doc.source}")
        if doc.notes:
            print(f"   Ghi chú: {doc.notes}")
        print()


def export_to_knowledge_snippets() -> None:
    """Xuất preview KnowledgeSnippet format, không dùng làm runtime source."""
    docs = load_medical_documents()

    output = Path(__file__).parent.parent / "outputs" / "generated" / "rag_knowledge_preview.py"
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w") as f:
        f.write("# Auto-generated from medical_documents.json\n")
        f.write("from dataclasses import dataclass\n\n")
        f.write("@dataclass(frozen=True)\n")
        f.write("class KnowledgeSnippet:\n")
        f.write('    title: str\n')
        f.write('    keywords: tuple[str, ...]\n')
        f.write('    content: str\n')
        f.write('    action: str\n\n')
        f.write("EXTENDED_SNIPPETS = [\n")
        for doc in docs:
            f.write(f"    KnowledgeSnippet(\n")
            f.write(f'        title={repr(doc.title)},\n')
            f.write(f"        keywords={repr(doc.keywords)},\n")
            f.write(f'        content={repr(doc.content)},\n')
            f.write(f'        action={repr(doc.action)},\n')
            f.write(f"    ),\n")
        f.write("]\n")
    print(f"✓ Xuất {len(docs)} snippets sang {output}")


def validate_documents() -> bool:
    """Kiểm tra tính hợp lệ của tài liệu."""
    docs = load_medical_documents()
    errors = []

    for i, doc in enumerate(docs):
        if not doc.title or not doc.title.strip():
            errors.append(f"Doc {i}: Tiêu đề trống")
        if not doc.keywords or len(doc.keywords) < 2:
            errors.append(f"Doc {i} ({doc.title}): Cần ít nhất 2 từ khóa")
        if not doc.content or len(doc.content) < 20:
            errors.append(f"Doc {i} ({doc.title}): Nội dung quá ngắn")
        if not doc.action or len(doc.action) < 10:
            errors.append(f"Doc {i} ({doc.title}): Hành động quá ngắn")
        if doc.severity not in ("high", "medium", "low"):
            errors.append(
                f"Doc {i} ({doc.title}): Mức độ phải là high/medium/low"
            )

    if errors:
        print("❌ Lỗi xác thực:")
        for e in errors:
            print(f"  - {e}")
        return False

    print(f"✓ Kiểm tra {len(docs)} tài liệu: OK")
    return True


def main():
    """CLI cho công cụ quản lý."""
    if len(sys.argv) < 2:
        print("Công cụ quản lý Knowledge Base Y Tế")
        print("\nCách dùng:")
        print("  python scripts/manage_medical_docs.py list [category]")
        print("  python scripts/manage_medical_docs.py add <title> <keywords...>")
        print("  python scripts/manage_medical_docs.py validate")
        print("  python scripts/manage_medical_docs.py export")
        print("\nDanh mục: drug_interaction, special_population, safety, dosing")
        return

    cmd = sys.argv[1]

    if cmd == "list":
        category = sys.argv[2] if len(sys.argv) > 2 else None
        list_documents(category)
    elif cmd == "validate":
        validate_documents()
    elif cmd == "export":
        export_to_knowledge_snippets()
    else:
        print(f"Lệnh không biết: {cmd}")


if __name__ == "__main__":
    main()
