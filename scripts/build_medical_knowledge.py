#!/usr/bin/env python3
"""Build extended medical knowledge base from medical_documents.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag_knowledge import KNOWLEDGE_BASE, KnowledgeSnippet


def load_medical_documents() -> list[KnowledgeSnippet]:
    """Load medical documents from JSON and convert to KnowledgeSnippets."""
    # Try both locations: scripts/data and project root data
    doc_file = Path(__file__).parent.parent / "data" / "medical_documents.json"

    if not doc_file.exists():
        print(f"⚠️  medical_documents.json tidak tìm thấy tại {doc_file}")
        return []

    with open(doc_file) as f:
        docs = json.load(f)

    snippets = []
    for doc in docs:
        snippet = KnowledgeSnippet(
            title=doc["title"],
            keywords=tuple(doc["keywords"]),
            content=doc["content"],
            action=doc["action"],
        )
        snippets.append(snippet)

    print(f"✓ Load {len(snippets)} documents từ {doc_file}")
    return snippets


def build_extended_knowledge_base() -> list[KnowledgeSnippet]:
    """Combine hardcoded KNOWLEDGE_BASE with medical_documents.json."""
    base_snippets = list(KNOWLEDGE_BASE)
    extended_snippets = load_medical_documents()

    combined = base_snippets + extended_snippets
    print(f"✓ Kết hợp: {len(base_snippets)} (hardcoded) + {len(extended_snippets)} (medical_documents.json) = {len(combined)} snippets")

    return combined


def build_medical_db_script() -> None:
    """Generate a preview script for inspecting the extended knowledge base."""
    extended = build_extended_knowledge_base()

    output_file = Path(__file__).parent.parent / "outputs" / "generated" / "rag_knowledge_preview.py"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w") as f:
        f.write("# Auto-generated from medical_documents.json + base knowledge base\n")
        f.write("from dataclasses import dataclass\n\n")
        f.write("@dataclass(frozen=True)\n")
        f.write("class KnowledgeSnippet:\n")
        f.write("    title: str\n")
        f.write("    keywords: tuple[str, ...]\n")
        f.write("    content: str\n")
        f.write("    action: str\n\n")
        f.write(f"EXTENDED_KNOWLEDGE_BASE = [\n")

        for snippet in extended:
            f.write(f"    KnowledgeSnippet(\n")
            f.write(f"        title={repr(snippet.title)},\n")
            f.write(f"        keywords={repr(snippet.keywords)},\n")
            f.write(f"        content={repr(snippet.content)},\n")
            f.write(f"        action={repr(snippet.action)},\n")
            f.write(f"    ),\n")

        f.write("]\n\n")
        f.write("def retrieve_snippets(query: str, top_k: int = 3) -> list[KnowledgeSnippet]:\n")
        f.write('    lowered = query.lower()\n')
        f.write("    scored = []\n")
        f.write("    for snippet in EXTENDED_KNOWLEDGE_BASE:\n")
        f.write("        score = sum(1 for keyword in snippet.keywords if keyword in lowered)\n")
        f.write("        if score:\n")
        f.write("            scored.append((score, snippet))\n")
        f.write("    scored.sort(key=lambda item: item[0], reverse=True)\n")
        f.write("    return [snippet for _, snippet in scored[:top_k]]\n")

    print(f"✓ Xuất preview extended knowledge base: {output_file}")
    print(f"  Chứa {len(extended)} snippets")

    # Statistics
    categories = {}
    for snippet in extended:
        for keyword in snippet.keywords:
            categories[keyword] = categories.get(keyword, 0) + 1

    print(f"\n📊 Thống kê:")
    print(f"  - Tổng snippets: {len(extended)}")
    print(f"  - Tổng từ khóa: {len(categories)}")
    print(f"  - Từ khóa phổ biến nhất: {sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "export":
        build_medical_db_script()
    else:
        extended = build_extended_knowledge_base()
        print("\n📋 Extended Knowledge Base Summary:")
        for i, snippet in enumerate(extended[-10:], start=len(extended) - 9):
            print(f"  {i}. {snippet.title}")
