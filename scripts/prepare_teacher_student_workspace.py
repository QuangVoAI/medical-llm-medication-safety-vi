#!/usr/bin/env python3
"""Scaffold teacher-student data folders for Kaggle training.

This script creates the optional directories and template files used to extend
the core SFT/DPO datasets with filtered ViMedAQA rows and teacher-generated
examples.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATED_DIR = ROOT / "data" / "generated"
EXTERNAL_DIR = ROOT / "data" / "external"
TEMPLATES_DIR = ROOT / "data" / "templates"


def write_if_missing(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def write_jsonl_if_missing(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    write_if_missing(
        EXTERNAL_DIR / "README.md",
        """# External Data

Dat cac file raw hoac intermediate tai day khi ban muon mo rong dataset.

Goi y:

- `vimedaqa/` cho data da tai ve hoac da loc so bo
- `leaflets/` cho to huong dan thuoc
- `guidelines/` cho trich doan guideline ngan

Khong can commit raw dump lon vao git.
""",
    )

    write_if_missing(
        GENERATED_DIR / "README.md",
        """# Generated Data

Thu muc nay chua cac file JSONL mo rong de build dataset train cuoi.

Script `scripts/build_medication_safety_datasets.py` se tu dong nap:

- `vimedaqa_filtered_sft.jsonl`
- `teacher_grounded_sft.jsonl`
- `teacher_generated_dpo.jsonl`

Chi can giu dung schema trong `data/templates/`.
""",
    )

    write_jsonl_if_missing(
        TEMPLATES_DIR / "vimedaqa_filtered_sft_example.jsonl",
        [
            {
                "question": "Đang uống thuốc chống đông thì có dùng thêm thuốc giảm đau được không?",
                "answer": "Không nên tự phối hợp khi chưa rõ loại thuốc cụ thể vì có thể làm tăng nguy cơ chảy máu. Bạn nên hỏi bác sĩ hoặc dược sĩ trước khi dùng thêm thuốc giảm đau.",
                "topic": "drug_interaction",
                "source": "ViMedAQA::filtered_example",
                "notes": "Patient-facing rewrite from Vietnamese medical QA",
            }
        ],
    )

    write_jsonl_if_missing(
        TEMPLATES_DIR / "teacher_grounded_sft_example.jsonl",
        [
            {
                "question": "Tôi đang dùng insulin, nếu bỏ bữa sáng thì có tiêm như bình thường không?",
                "answer": "Không nên tự quyết định giữ nguyên liều insulin khi bỏ bữa nếu chưa có hướng dẫn cá nhân hóa. Bạn có nguy cơ hạ đường huyết nên cần hỏi bác sĩ về cách xử trí an toàn.",
                "topic": "insulin_safety",
                "source": "teacher_grounded::leaflet_example",
                "grounding": "Insulin when meal skipped may increase hypoglycemia risk",
            }
        ],
    )

    write_jsonl_if_missing(
        TEMPLATES_DIR / "teacher_generated_dpo_example.jsonl",
        [
            {
                "prompt": "uống ks thấy đỡ rồi ngưng luôn được không?",
                "chosen": "Không nên tự ý ngưng kháng sinh khi thấy đỡ vì nhiễm trùng có thể chưa khỏi hẳn và có nguy cơ góp phần gây kháng kháng sinh. Bạn nên dùng theo hướng dẫn và hỏi bác sĩ nếu muốn dừng thuốc.",
                "rejected": "Nếu triệu chứng đã giảm thì có thể ngưng để tránh dùng thuốc quá lâu.",
                "topic": "antibiotics_adherence",
                "source": "teacher_generated::unsafe_but_fluent_example",
                "error_type": "premature_stop",
            }
        ],
    )

    write_jsonl_if_missing(GENERATED_DIR / "vimedaqa_filtered_sft.jsonl", [])
    write_jsonl_if_missing(GENERATED_DIR / "teacher_grounded_sft.jsonl", [])
    write_jsonl_if_missing(GENERATED_DIR / "teacher_generated_dpo.jsonl", [])
    print("Teacher-student workspace is ready.")


if __name__ == "__main__":
    main()
