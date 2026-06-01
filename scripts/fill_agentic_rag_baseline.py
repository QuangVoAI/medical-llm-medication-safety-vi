#!/usr/bin/env python3
"""Fill evaluation CSV with controlled Agentic RAG baseline answers.

This gives the experiment one completed baseline column before GPU training.
It is not a learned-model baseline; it is a transparent controlled Agentic RAG
baseline used for sanity checking and presentation.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import respond


DEFAULT_FIELDS = [
    "id",
    "question",
    "risk_type",
    "base_answer",
    "sft_answer",
    "dpo_answer",
    "base_safety_0_3",
    "base_factuality_0_3",
    "base_uncertainty_0_3",
    "base_actionability_0_3",
    "base_vietnamese_quality_0_3",
    "sft_safety_0_3",
    "sft_factuality_0_3",
    "sft_uncertainty_0_3",
    "sft_actionability_0_3",
    "sft_vietnamese_quality_0_3",
    "dpo_safety_0_3",
    "dpo_factuality_0_3",
    "dpo_uncertainty_0_3",
    "dpo_actionability_0_3",
    "dpo_vietnamese_quality_0_3",
    "notes",
]


def load_rows(input_path: Path) -> tuple[list[dict], list[str]]:
    if input_path.exists():
        with input_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            return list(reader), list(reader.fieldnames or DEFAULT_FIELDS)

    eval_path = ROOT / "outputs" / "evaluation_prompts.jsonl"
    rows = []
    for line in eval_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        rows.append(
            {
                "id": item["id"],
                "question": item["question"],
                "risk_type": item["risk_type"],
                "notes": "Expected: " + "; ".join(item["expected_points"]),
            }
        )
    return rows, DEFAULT_FIELDS


def fill_baseline(input_path: Path, output_path: Path, answer_column: str = "base_answer") -> None:
    rows, fieldnames = load_rows(input_path)

    for row in rows:
        question = row["question"]
        answer, _context, scores, _summary, trace, decision = respond(question, use_model=False)
        row[answer_column] = answer
        prefix = answer_column.replace("_answer", "")
        row[f"{prefix}_safety_0_3"] = scores["safety"]
        row[f"{prefix}_factuality_0_3"] = scores["factuality"]
        row[f"{prefix}_uncertainty_0_3"] = scores["uncertainty"]
        row[f"{prefix}_actionability_0_3"] = scores["actionability"]
        row[f"{prefix}_vietnamese_quality_0_3"] = scores["vietnamese_quality"]
        row["notes"] = (
            row.get("notes", "")
            + f" | base_answer is controlled agentic RAG fallback, not trained LLM; decision={decision}; category={trace.get('category')}"
        ).strip()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote controlled Agentic RAG baseline to {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=ROOT / "outputs" / "manual_eval_template.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs" / "manual_eval_with_agentic_rag_baseline.csv")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    fill_baseline(args.input, args.output)
