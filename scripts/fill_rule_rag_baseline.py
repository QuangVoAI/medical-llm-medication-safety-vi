#!/usr/bin/env python3
"""Fill manual_eval_template.csv with rule/RAG fallback answers.

This gives the experiment at least one completed baseline column before GPU
training. It is not a learned model baseline; it is a transparent pipeline
baseline used for sanity checking and presentation.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import respond
from src.evaluator import score_answer


def fill_baseline(input_path: Path, output_path: Path, answer_column: str = "base_answer") -> None:
    with input_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    for row in rows:
        question = row["question"]
        answer, _context, scores, _summary = respond(question, use_model=False)
        row[answer_column] = answer
        prefix = answer_column.replace("_answer", "")
        row[f"{prefix}_safety_0_3"] = scores["safety"]
        row[f"{prefix}_factuality_0_3"] = scores["factuality"]
        row[f"{prefix}_uncertainty_0_3"] = scores["uncertainty"]
        row[f"{prefix}_actionability_0_3"] = scores["actionability"]
        row[f"{prefix}_vietnamese_quality_0_3"] = scores["vietnamese_quality"]
        row["notes"] = (row.get("notes", "") + " | base_answer is rule/RAG fallback, not trained LLM").strip()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote rule/RAG baseline to {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=ROOT / "outputs" / "manual_eval_template.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs" / "manual_eval_with_rule_rag_baseline.csv")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    fill_baseline(args.input, args.output)
