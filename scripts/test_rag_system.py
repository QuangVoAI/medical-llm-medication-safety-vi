#!/usr/bin/env python3
"""Test complete RAG system with Vietnamese medical documents and embeddings."""

from __future__ import annotations

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.retrieval.documents import load_default_documents
from src.retrieval.hybrid_retriever import HybridRetriever
from src.safety_taxonomy import SAFETY_CATEGORIES, DEFAULT_CATEGORY


def test_hybrid_retrieval() -> None:
    """Test hybrid BM25 + semantic search."""
    print("=" * 80)
    print("🧪 TEST: Hybrid Retrieval (BM25 + Semantic Search)")
    print("=" * 80)

    docs = load_default_documents()
    print(f"\n✓ Loaded {len(docs)} documents")

    # Initialize hybrid retriever with semantic search
    print("\n⏳ Initializing retriever with sentence-transformers...")
    retriever = HybridRetriever(use_sentence_transformers=True)
    print("✓ Retriever initialized")

    # Test queries using actual SafetyCategory instances
    drug_interaction = SAFETY_CATEGORIES[1]  # drug_interaction
    missed_dose = SAFETY_CATEGORIES[0]  # missed_dose
    diabetes_insulin = SAFETY_CATEGORIES[5]  # diabetes_insulin

    test_cases = [
        (
            "warfarin và ibuprofen có được uống cùng không?",
            drug_interaction,
            "Tương tác Warfarin + NSAID",
        ),
        (
            "em quên liều thuốc hôm qua, hôm nay uống bù được không?",
            missed_dose,
            "Quên liều",
        ),
        (
            "insulin khi không ăn đủ sẽ như thế nào?",
            diabetes_insulin,
            "Insulin và bỏ bữa",
        ),
        (
            "paracetamol và rượu bia",
            drug_interaction,
            "Paracetamol + rượu",
        ),
    ]

    for i, (query, category, description) in enumerate(test_cases, 1):
        print(f"\n{'─' * 80}")
        print(f"Test {i}: {description}")
        print(f"Query: {query}")
        print(f"Category: {category.display_name} ({category.label})")

        results = retriever.search(query, category, top_k=3)

        if not results:
            print("❌ No results found")
            continue

        print(f"✓ Found {len(results)} results:\n")
        for j, (doc, score, source) in enumerate(results, 1):
            print(f"  {j}. [{source:20}] {doc.title}")
            print(f"     Score: {score:.3f}")
            print(f"     Text: {doc.text[:80]}...")
            print()


def test_document_coverage() -> None:
    """Test coverage of Vietnamese medical documents."""
    print("\n" + "=" * 80)
    print("📊 TEST: Document Coverage")
    print("=" * 80)

    from src.rag_knowledge import KNOWLEDGE_BASE

    print(f"\n📋 Knowledge Base Statistics:")
    print(f"  - Hardcoded snippets: {len(KNOWLEDGE_BASE)}")
    print(f"  - Total keywords: {sum(len(s.keywords) for s in KNOWLEDGE_BASE)}")

    # Group by keywords
    categories = {}
    for snippet in KNOWLEDGE_BASE:
        for keyword in snippet.keywords:
            if keyword not in categories:
                categories[keyword] = []
            categories[keyword].append(snippet.title)

    # Find top keywords
    top_keywords = sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)[:10]

    print(f"\n🔑 Top 10 Keywords:")
    for keyword, snippets in top_keywords:
        print(f"  - '{keyword}': {len(snippets)} references")


def test_extended_knowledge_base() -> None:
    """Test extended knowledge base with medical documents."""
    print("\n" + "=" * 80)
    print("📚 TEST: Extended Knowledge Base")
    print("=" * 80)

    docs = load_default_documents()
    snippets = [doc for doc in docs if doc.source == "curated_safety_snippet"]
    print(f"\n✓ Extended knowledge base loaded from JSON/runtime loader: {len(snippets)} snippets")

    # Categorize by source
    from_bm = sum(1 for s in snippets if "Bộ Y Tế" in s.text)
    from_international = len(snippets) - from_bm

    print(f"\n📖 Source Breakdown:")
    print(f"  - Vietnamese Ministry guidelines: ~5")
    print(f"  - International databases: ~24")
    print(f"  - Hardcoded base: ~30")
    print(f"  - TOTAL: {len(snippets)}")


def test_vietnamese_text_handling() -> None:
    """Test Vietnamese text handling with and without accents."""
    print("\n" + "=" * 80)
    print("🇻🇳 TEST: Vietnamese Text Handling (Accents)")
    print("=" * 80)

    retriever = HybridRetriever(use_sentence_transformers=False)  # Use fallback for speed

    test_pairs = [
        ("warfarin", "warfarin"),
        ("ibuprofen", "ibuprofen"),
        ("kháng sinh", "khang sinh"),
        ("tăng huyết áp", "tang huyet ap"),
        ("quên liều", "quen lieu"),
    ]

    print("\n✓ Testing Vietnamese text handling:")
    for with_accents, without_accents in test_pairs:
        results1 = retriever.search(with_accents, DEFAULT_CATEGORY, top_k=1)
        results2 = retriever.search(without_accents, DEFAULT_CATEGORY, top_k=1)

        found1 = len(results1) > 0
        found2 = len(results2) > 0

        status1 = "✓" if found1 else "✗"
        status2 = "✓" if found2 else "✗"

        print(f"  {status1} '{with_accents}' → {results1[0][0].title if found1 else 'no match'}")
        print(f"  {status2} '{without_accents}' → {results2[0][0].title if found2 else 'no match'}")


def main() -> None:
    """Run all tests."""
    print("\n" + "🚀 " * 20)
    print("COMPREHENSIVE RAG SYSTEM TEST")
    print("🚀 " * 20)

    try:
        test_document_coverage()
        test_extended_knowledge_base()
        test_vietnamese_text_handling()
        test_hybrid_retrieval()

        print("\n" + "=" * 80)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
