#!/usr/bin/env python3
"""Score model outputs with the medication-safety heuristic rubric."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.evaluator import score_answer


MODEL_COLUMNS = ["base_answer", "sft_answer", "dpo_answer"]


def score_csv(input_path: Path, output_path: Path) -> None:
    with input_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    extra_fields = []
    for column in MODEL_COLUMNS:
        if column in fieldnames:
            prefix = column.replace("_answer", "")
            extra_fields.extend(
                [
                    f"{prefix}_rubric_json",
                    f"{prefix}_average",
                    f"{prefix}_safety",
                    f"{prefix}_factuality",
                    f"{prefix}_uncertainty",
                    f"{prefix}_actionability",
                ]
            )

    output_fields = fieldnames + [field for field in extra_fields if field not in fieldnames]
    for row in rows:
        question = row.get("question", "")
        for column in MODEL_COLUMNS:
            answer = row.get(column, "")
            if not answer:
                continue
            prefix = column.replace("_answer", "")
            scores = score_answer(question, answer)
            row[f"{prefix}_rubric_json"] = json.dumps(scores, ensure_ascii=False)
            row[f"{prefix}_average"] = scores["average"]
            row[f"{prefix}_safety"] = scores["safety"]
            row[f"{prefix}_factuality"] = scores["factuality"]
            row[f"{prefix}_uncertainty"] = scores["uncertainty"]
            row[f"{prefix}_actionability"] = scores["actionability"]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote scored CSV to {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=ROOT / "outputs" / "manual_eval_template.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs" / "scored_eval.csv")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    score_csv(args.input, args.output)
