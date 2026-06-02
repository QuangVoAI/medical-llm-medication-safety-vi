#!/usr/bin/env python3
"""Build expanded Vietnamese pretraining (CPT) corpus from SFT + Meddies data.

This creates a realistic 800-1000 row pretraining dataset from:
- SFT answers (500 rows of medication safety text)
- Meddies pharmaceutical QA (200+ rows)
- Segmented and augmented with Vietnamese robustness variants

Purpose: Task 1 (CPT) becomes substantial and meaningful, not just 10 demo rows.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.vi_text import normalize_vi_text, remove_vietnamese_accents, make_informal_variants


OUT_DIR = ROOT / "data" / "pretraining"
PROCESSED_DIR = ROOT / "data" / "processed"


def read_jsonl(path: Path) -> list[dict]:
    """Read JSONL file."""
    rows = []
    if not path.exists():
        return rows
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def fetch_hf_rows(dataset: str, config: str, split: str, limit: int, max_pages: int = 20) -> list[dict]:
    """Fetch rows from Hugging Face Dataset Viewer API."""
    rows = []
    base = "https://datasets-server.huggingface.co/rows"
    for page_idx in range(max_pages):
        params = {
            "dataset": dataset,
            "config": config,
            "split": split,
            "offset": page_idx * 100,
            "length": min(100, max(limit - len(rows), 1)),
        }
        url = base + "?" + urllib.parse.urlencode(params)
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            print(f"[warn] Fetch failed: {exc}")
            break
        for item in payload.get("rows", []):
            row = item.get("row")
            if isinstance(row, dict):
                rows.append(row)
        if len(rows) >= limit or not payload.get("rows"):
            break
    return rows


def extract_qa_from_messages(row: dict) -> tuple[str, str] | None:
    """Extract question and answer from messages format."""
    msg_list = row.get("messages")
    if not isinstance(msg_list, list):
        return None
    user = next((m.get("content", "") for m in msg_list if m.get("role") == "user"), "")
    assistant = next((m.get("content", "") for m in msg_list if m.get("role") == "assistant"), "")
    if not user or not assistant:
        return None
    return str(user).strip(), str(assistant).strip()


def load_sft_corpus(limit: int) -> list[str]:
    """Load SFT answers as pretraining text."""
    sft_path = PROCESSED_DIR / "medication_safety_vi_sft.jsonl"
    rows = read_jsonl(sft_path)

    texts = []
    for row in rows[:limit]:
        answer = row.get("answer", "").strip()
        if answer:
            texts.append(answer)

    print(f"[CPT] Loaded {len(texts)} rows from SFT")
    return texts


def load_meddies_corpus(limit: int, seed: int) -> list[str]:
    """Load Meddies pharmaceutical QA as pretraining text."""
    try:
        from datasets import load_dataset
        raw = load_dataset("Meddies/meddies-qa", "qa_pharmaceuticals", split="train", streaming=True)
        rows = list(raw.shuffle(seed=seed, buffer_size=2000).take(max(limit * 2, 400)))
    except Exception as exc:
        print(f"[warn] Fallback to API: {exc}")
        rows = fetch_hf_rows("Meddies/meddies-qa", "qa_pharmaceuticals", "train", limit=max(limit * 2, 400))

    texts = []
    for row in rows:
        qa = extract_qa_from_messages(row)
        if qa:
            question, answer = qa
            combined_text = f"{question} {answer}".strip()
            if combined_text and len(combined_text) > 20:
                texts.append(combined_text)
                if len(texts) >= limit:
                    break

    print(f"[CPT] Loaded {len(texts)} rows from Meddies")
    return texts


def segment_long_text(text: str, max_length: int = 200, overlap: int = 30) -> list[str]:
    """Segment long text into chunks with overlap."""
    text = normalize_vi_text(text)
    if len(text) <= max_length:
        return [text]

    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = ""

    for sent in sentences:
        if len(current_chunk) + len(sent) + 1 <= max_length:
            current_chunk += (" " if current_chunk else "") + sent
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = sent

    if current_chunk:
        chunks.append(current_chunk)

    return chunks if chunks else [text[:max_length]]


def create_cpt_corpus_rows(texts: list[str], seed: int, add_variants: bool = True) -> list[dict]:
    """Create pretraining corpus rows with variants."""
    rng = random.Random(seed)
    rows = []
    row_id = 0

    for text in texts:
        text = normalize_vi_text(text)
        if not text or len(text) < 20:
            continue

        # Add main text
        rows.append({
            "id": row_id,
            "text": text,
            "source": "medical_qa",
            "variant": "original",
            "length": len(text),
        })
        row_id += 1

        # Add no-accent variant
        if add_variants:
            no_accent = remove_vietnamese_accents(text)
            if no_accent != text:
                rows.append({
                    "id": row_id,
                    "text": no_accent,
                    "source": "medical_qa",
                    "variant": "no_accent",
                    "length": len(no_accent),
                })
                row_id += 1

            # Add informal variants (with abbreviations)
            informal_variants = make_informal_variants(text, max_variants=2, seed=seed)
            for informal_text in informal_variants:
                rows.append({
                    "id": row_id,
                    "text": informal_text,
                    "source": "medical_qa",
                    "variant": "informal",
                    "length": len(informal_text),
                })
                row_id += 1

    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    """Write rows to JSONL."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def build(args: argparse.Namespace) -> None:
    """Build expanded CPT corpus."""
    random.seed(args.seed)

    print("\n=== Building Expanded CPT Corpus ===\n")

    # Load raw texts
    sft_texts = load_sft_corpus(args.sft_limit)
    meddies_texts = load_meddies_corpus(args.meddies_limit, args.seed)

    all_texts = sft_texts + meddies_texts
    random.shuffle(all_texts)

    print(f"[CPT] Total raw texts: {len(all_texts)}")
    print(f"[CPT] Creating corpus rows with variants...")

    # Create corpus rows with variants
    corpus_rows = create_cpt_corpus_rows(all_texts, seed=args.seed, add_variants=args.add_variants)

    print(f"[CPT] Generated {len(corpus_rows)} total rows (including variants)")

    # Save expanded corpus
    expanded_path = OUT_DIR / "medical_corpus_expanded.jsonl"
    write_jsonl(expanded_path, corpus_rows)
    print(f"[CPT] ✓ Saved to {expanded_path}")

    # Summary stats
    stats = {
        "total_rows": len(corpus_rows),
        "unique_sources": len(all_texts),
        "sft_rows": len(sft_texts),
        "meddies_rows": len(meddies_texts),
        "variant_types": {
            "original": sum(1 for r in corpus_rows if r["variant"] == "original"),
            "no_accent": sum(1 for r in corpus_rows if r["variant"] == "no_accent"),
            "informal": sum(1 for r in corpus_rows if r["variant"] == "informal"),
        },
        "avg_text_length": sum(r["length"] for r in corpus_rows) / len(corpus_rows) if corpus_rows else 0,
    }

    print(f"\n[CPT] Corpus Statistics:")
    print(json.dumps(stats, ensure_ascii=False, indent=2))

    # Save metadata
    metadata_path = OUT_DIR / "cpt_corpus_metadata.json"
    metadata_path.write_text(json.dumps({
        **stats,
        "description": "Expanded Vietnamese medication safety pretraining corpus",
        "task": "Continued Pretraining (Task 1)",
        "sources": {
            "sft_answers": "medication_safety_vi_sft.jsonl",
            "meddies_qa": "Meddies/meddies-qa (qa_pharmaceuticals)",
        },
        "augmentation": {
            "add_no_accent_variant": args.add_variants,
            "add_informal_abbreviations": args.add_variants,
        },
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[CPT] ✓ Metadata saved to {metadata_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build expanded Vietnamese CPT corpus")
    parser.add_argument("--sft-limit", type=int, default=500, help="Limit SFT rows to load")
    parser.add_argument("--meddies-limit", type=int, default=300, help="Limit Meddies rows to load")
    parser.add_argument("--add-variants", action="store_true", default=True, help="Add no-accent and informal variants")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    return parser.parse_args()


if __name__ == "__main__":
    build(parse_args())
