#!/usr/bin/env python3
"""Build Vietnamese SFT/DPO datasets for a medication-safety LLM demo.

Sources:
- Meddies/meddies-qa, config qa_pharmaceuticals: Vietnamese pharmaceutical QA.
- ASHu2/medlens: medication interaction QA from FAERS-style signals.

The script keeps the final task Vietnamese-first and adds a seed set for
reproducibility. It is designed for a lab demo, not clinical deployment.
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
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "processed"
sys.path.insert(0, str(ROOT))

from src.safety_taxonomy import classify_question
from src.vi_text import make_informal_variants, normalize_vi_text

SYSTEM_PROMPT = (
    "Bạn là trợ lý AI về an toàn sử dụng thuốc cho mục đích giáo dục. "
    "Trả lời bằng tiếng Việt, ngắn gọn, thận trọng, không kê đơn, không chẩn đoán, "
    "không tự ý thay đổi liều thuốc cho người dùng. Khi có nguy cơ, hãy khuyên hỏi "
    "bác sĩ hoặc dược sĩ; nếu có dấu hiệu nguy hiểm, hãy khuyên đi cấp cứu."
)

MEDICATION_KEYWORDS_VI = [
    "thuốc",
    "liều",
    "quá liều",
    "tác dụng phụ",
    "tương tác",
    "uống chung",
    "kháng sinh",
    "paracetamol",
    "ibuprofen",
    "warfarin",
    "insulin",
    "huyết áp",
    "tiểu đường",
    "mang thai",
    "trẻ em",
]

SEED_SFT = [
    {
        "question": "Tôi quên uống thuốc huyết áp hôm qua, hôm nay uống gấp đôi được không?",
        "answer": (
            "Không nên tự ý uống gấp đôi liều thuốc huyết áp. Việc uống bù quá liều có thể "
            "gây tụt huyết áp, chóng mặt hoặc ngất. Bạn nên đọc hướng dẫn thuốc và hỏi bác sĩ "
            "hoặc dược sĩ để biết cách xử trí phù hợp với loại thuốc đang dùng."
        ),
        "topic": "missed_dose",
        "source": "seed_vi_medication_safety",
    },
    {
        "question": "Đang dùng warfarin thì có uống ibuprofen khi đau đầu được không?",
        "answer": (
            "Không nên tự ý dùng ibuprofen khi đang dùng warfarin vì có thể làm tăng nguy cơ "
            "chảy máu. Bạn nên hỏi bác sĩ hoặc dược sĩ trước khi dùng thuốc giảm đau. Nếu có "
            "chảy máu bất thường, phân đen, nôn ra máu hoặc đau đầu dữ dội, cần đi khám khẩn cấp."
        ),
        "topic": "drug_interaction",
        "source": "seed_vi_medication_safety",
    },
    {
        "question": "Uống paracetamol với rượu có sao không?",
        "answer": (
            "Nên tránh uống paracetamol cùng rượu vì có thể tăng nguy cơ độc gan, đặc biệt khi "
            "dùng liều cao, uống rượu nhiều hoặc có bệnh gan. Không tự ý vượt quá liều trên nhãn "
            "thuốc và hãy hỏi dược sĩ/bác sĩ nếu bạn không chắc."
        ),
        "topic": "overdose_liver_safety",
        "source": "seed_vi_medication_safety",
    },
    {
        "question": "Tôi thấy đỡ bệnh rồi, có thể tự ngưng kháng sinh không?",
        "answer": (
            "Không nên tự ý ngưng kháng sinh khi chưa hỏi bác sĩ. Ngưng sớm có thể làm nhiễm trùng "
            "chưa khỏi hẳn và góp phần gây kháng kháng sinh. Hãy dùng đúng đơn hoặc liên hệ bác sĩ "
            "nếu có tác dụng phụ hoặc muốn dừng thuốc."
        ),
        "topic": "antibiotic_adherence",
        "source": "seed_vi_medication_safety",
    },
    {
        "question": "Người nhà tôi uống nhầm nhiều viên thuốc ngủ, nên chờ xem có sao không?",
        "answer": (
            "Không nên chờ. Uống nhầm nhiều viên thuốc ngủ có thể gây buồn ngủ sâu, suy hô hấp, "
            "tụt huyết áp hoặc hôn mê. Hãy gọi cấp cứu hoặc đưa người bệnh đến cơ sở y tế ngay, "
            "mang theo vỏ thuốc nếu có."
        ),
        "topic": "emergency_overdose",
        "source": "seed_vi_medication_safety",
    },
    {
        "question": "Phụ nữ mang thai có tự mua thuốc cảm uống được không?",
        "answer": (
            "Phụ nữ mang thai không nên tự dùng thuốc cảm vì một số thuốc có thể không phù hợp "
            "theo tuổi thai hoặc bệnh nền. Nên hỏi bác sĩ hoặc dược sĩ trước khi dùng, kể cả thuốc "
            "không kê đơn và thực phẩm bổ sung."
        ),
        "topic": "pregnancy_safety",
        "source": "seed_vi_medication_safety",
    },
    {
        "question": "Tôi đang dùng insulin, nếu bỏ bữa thì có tiêm liều như bình thường không?",
        "answer": (
            "Không nên tự quyết định liều insulin khi bỏ bữa nếu chưa có hướng dẫn từ bác sĩ. "
            "Insulin khi không ăn đủ có thể gây hạ đường huyết. Nếu có run tay, vã mồ hôi, lú lẫn "
            "hoặc ngất, cần xử trí hạ đường huyết theo hướng dẫn y tế và tìm trợ giúp ngay."
        ),
        "topic": "diabetes_medication_safety",
        "source": "seed_vi_medication_safety",
    },
    {
        "question": "Thuốc của người lớn có thể bẻ nhỏ cho trẻ em uống được không?",
        "answer": (
            "Không nên tự ý bẻ nhỏ thuốc người lớn cho trẻ em. Liều trẻ em phụ thuộc cân nặng, tuổi, "
            "dạng bào chế và bệnh cụ thể; một số viên không được bẻ hoặc nghiền. Hãy hỏi bác sĩ hoặc "
            "dược sĩ trước khi cho trẻ dùng bất kỳ thuốc nào."
        ),
        "topic": "pediatric_safety",
        "source": "seed_vi_medication_safety",
    },
]

SEED_DPO = [
    {
        "prompt": "Tôi quên uống thuốc huyết áp hôm qua, hôm nay uống gấp đôi được không?",
        "chosen": "Không nên tự ý uống gấp đôi liều. Uống bù quá liều có thể gây tụt huyết áp, chóng mặt hoặc ngất. Hãy xem hướng dẫn thuốc và hỏi bác sĩ/dược sĩ về cách xử trí phù hợp.",
        "rejected": "Được, hôm qua quên thì hôm nay uống gấp đôi để bù lại là hợp lý.",
        "topic": "missed_dose",
    },
    {
        "prompt": "Đang dùng warfarin thì có uống ibuprofen khi đau đầu được không?",
        "chosen": "Không nên tự ý dùng ibuprofen khi đang dùng warfarin vì có thể tăng nguy cơ chảy máu. Hãy hỏi bác sĩ/dược sĩ trước khi dùng thuốc giảm đau khác.",
        "rejected": "Có thể uống bình thường, hai thuốc này không có vấn đề gì đáng lo.",
        "topic": "drug_interaction",
    },
    {
        "prompt": "Uống paracetamol với rượu có sao không?",
        "chosen": "Nên tránh phối hợp paracetamol với rượu vì có thể tăng nguy cơ độc gan, nhất là khi dùng liều cao, uống rượu nhiều hoặc có bệnh gan.",
        "rejected": "Không sao, paracetamol là thuốc thông dụng nên uống với rượu vẫn an toàn.",
        "topic": "overdose_liver_safety",
    },
    {
        "prompt": "Tôi thấy đỡ bệnh rồi, có thể tự ngưng kháng sinh không?",
        "chosen": "Không nên tự ý ngưng kháng sinh khi chưa hỏi bác sĩ. Ngưng sớm có thể làm bệnh chưa khỏi hẳn và góp phần gây kháng kháng sinh.",
        "rejected": "Nếu thấy đỡ rồi thì nên ngưng ngay để tránh uống thuốc không cần thiết.",
        "topic": "antibiotic_adherence",
    },
    {
        "prompt": "Người nhà tôi uống nhầm nhiều viên thuốc ngủ, nên chờ xem có sao không?",
        "chosen": "Không nên chờ. Đây có thể là tình huống nguy hiểm như suy hô hấp hoặc hôn mê. Hãy gọi cấp cứu hoặc đưa người bệnh đến cơ sở y tế ngay.",
        "rejected": "Cứ để người đó ngủ, thuốc ngủ chủ yếu làm buồn ngủ nên thường không nguy hiểm.",
        "topic": "emergency_overdose",
    },
    {
        "prompt": "Phụ nữ mang thai có tự mua thuốc cảm uống được không?",
        "chosen": "Không nên tự dùng thuốc cảm khi mang thai. Một số thuốc không phù hợp theo tuổi thai hoặc bệnh nền, nên hỏi bác sĩ/dược sĩ trước khi dùng.",
        "rejected": "Có thể tự mua thuốc cảm thông thường vì thuốc không kê đơn là an toàn cho thai kỳ.",
        "topic": "pregnancy_safety",
    },
    {
        "prompt": "Tôi đang dùng insulin, nếu bỏ bữa thì có tiêm liều như bình thường không?",
        "chosen": "Không nên tự quyết định liều insulin khi bỏ bữa nếu chưa có hướng dẫn. Insulin khi không ăn đủ có thể gây hạ đường huyết, cần hỏi bác sĩ về kế hoạch xử trí.",
        "rejected": "Cứ tiêm liều như bình thường, bữa ăn không ảnh hưởng nhiều đến insulin.",
        "topic": "diabetes_medication_safety",
    },
    {
        "prompt": "Thuốc của người lớn có thể bẻ nhỏ cho trẻ em uống được không?",
        "chosen": "Không nên tự ý bẻ nhỏ thuốc người lớn cho trẻ em. Liều trẻ em phụ thuộc tuổi, cân nặng và dạng thuốc; hãy hỏi bác sĩ/dược sĩ trước.",
        "rejected": "Được, chỉ cần bẻ nhỏ viên thuốc người lớn là trẻ em dùng được.",
        "topic": "pediatric_safety",
    },
]


def strip_think(text: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
    return re.sub(r"\s+", " ", text).strip()


def messages(question: str, answer: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
        {"role": "assistant", "content": answer},
    ]


def normalize_dataset_row(row: dict[str, Any]) -> dict[str, Any]:
    row = dict(row)
    row["question"] = normalize_vi_text(row["question"])
    row["answer"] = normalize_vi_text(row["answer"])
    row["safety_category"] = classify_question(row["question"]).label
    row["messages"] = messages(row["question"], row["answer"])
    return row


def augment_seed_rows(seed_rows: list[dict[str, Any]], repeat_seed: int, seed: int) -> list[dict[str, Any]]:
    """Repeat seed rows and add Vietnamese informal variants."""

    augmented: list[dict[str, Any]] = []
    for row in seed_rows:
        category = classify_question(row["question"])
        normalized = normalize_dataset_row(row)
        normalized["augmentation"] = "original_seed"
        augmented.append(normalized)
        for variant in make_informal_variants(row["question"], max_variants=4, seed=seed):
            augmented.append(
                normalize_dataset_row(
                    {
                        **row,
                        "question": variant,
                        "source": "seed_vi_medication_safety::informal_variant",
                        "topic": category.label,
                        "augmentation": "informal_variant",
                    }
                )
            )

    repeated = (augmented * max(repeat_seed, 1))[: len(augmented) * max(repeat_seed, 1)]
    return repeated


def extract_qa_from_messages(row: dict[str, Any]) -> tuple[str, str] | None:
    msg_list = row.get("messages")
    if not isinstance(msg_list, list):
        return None
    user = next((m.get("content", "") for m in msg_list if m.get("role") == "user"), "")
    assistant = next((m.get("content", "") for m in msg_list if m.get("role") == "assistant"), "")
    if not user or not assistant:
        return None
    return str(user).strip(), strip_think(str(assistant))


def has_medication_keyword(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in MEDICATION_KEYWORDS_VI)


def fetch_hf_rows(dataset: str, config: str, split: str, limit: int, max_pages: int = 10) -> list[dict[str, Any]]:
    """Fetch rows through the Hugging Face Dataset Viewer API.

    This avoids importing `datasets`, which can fail on local machines with a
    broken torch install. It is read-only and only pulls small pages.
    """

    rows: list[dict[str, Any]] = []
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
            print(f"[warn] Dataset Viewer API failed for {dataset}: {exc}")
            break
        for item in payload.get("rows", []):
            row = item.get("row")
            if isinstance(row, dict):
                rows.append(row)
        if len(rows) >= limit or not payload.get("rows"):
            break
    return rows


def load_meddies(limit: int, seed: int) -> list[dict[str, Any]]:
    api_fallback_rows: list[dict[str, Any]] | None = None
    try:
        from datasets import load_dataset
    except Exception as exc:
        print(f"[warn] datasets library unavailable: {exc}")
        api_fallback_rows = fetch_hf_rows("Meddies/meddies-qa", "qa_pharmaceuticals", "train", limit=max(limit * 2, 200))

    if api_fallback_rows is None:
        try:
            raw = load_dataset("Meddies/meddies-qa", "qa_pharmaceuticals", split="train", streaming=True)
        except Exception as exc:
            print(f"[warn] could not load Meddies QA: {exc}")
            api_fallback_rows = fetch_hf_rows("Meddies/meddies-qa", "qa_pharmaceuticals", "train", limit=max(limit * 2, 200))
        else:
            api_fallback_rows = list(raw.shuffle(seed=seed, buffer_size=2000).take(max(limit * 2, 200)))

    rows: list[dict[str, Any]] = []
    random.Random(seed).shuffle(api_fallback_rows)
    for row in api_fallback_rows:
        qa = extract_qa_from_messages(row)
        if not qa:
            continue
        question, answer = qa
        if not has_medication_keyword(question + " " + answer):
            continue
        rows.append(
            normalize_dataset_row(
                {
                    "question": question,
                    "answer": answer,
                    "topic": row.get("question_category", "pharmaceuticals"),
                    "source": "Meddies/meddies-qa::qa_pharmaceuticals",
                }
            )
        )
        if len(rows) >= limit:
            break
    return rows


def translate_medlens_answer(answer: str) -> str:
    severity = "cao" if "MAJOR" in answer.upper() or "Overall risk: Major" in answer else "thấp/vừa"
    urgency = "Cần được bác sĩ hoặc dược sĩ rà soát sớm." if severity == "cao" else "Nên trao đổi với bác sĩ hoặc dược sĩ nếu triệu chứng tiếp diễn."
    return (
        f"Nguy cơ tương tác thuốc có thể ở mức {severity}. Đây là tín hiệu từ dữ liệu báo cáo "
        "bất lợi, không khẳng định chắc chắn một cặp thuốc là nguyên nhân. Không nên tự ý ngưng, "
        f"thêm hoặc đổi liều thuốc. {urgency}"
    )


def load_medlens(limit: int, seed: int) -> list[dict[str, Any]]:
    api_fallback_rows: list[dict[str, Any]] | None = None
    try:
        from datasets import load_dataset
    except Exception as exc:
        print(f"[warn] datasets library unavailable: {exc}")
        api_fallback_rows = fetch_hf_rows("ASHu2/medlens", "default", "train", limit=max(limit * 2, 200))

    if api_fallback_rows is None:
        try:
            raw = load_dataset("ASHu2/medlens", split="train", streaming=True)
        except Exception as exc:
            print(f"[warn] could not load MedLens: {exc}")
            api_fallback_rows = fetch_hf_rows("ASHu2/medlens", "default", "train", limit=max(limit * 2, 200))
        else:
            api_fallback_rows = list(raw.shuffle(seed=seed, buffer_size=2000).take(max(limit * 2, 200)))

    rows: list[dict[str, Any]] = []
    random.Random(seed).shuffle(api_fallback_rows)
    for row in api_fallback_rows:
        qa = extract_qa_from_messages(row)
        if not qa:
            continue
        question_en, answer_en = qa
        meds_match = re.search(r"(?:Medications|Current drugs|currently take|medications are)[: ]+([^.\n]+)", question_en, re.IGNORECASE)
        meds = meds_match.group(1).replace("\\", ", ") if meds_match else "các thuốc hiện tại"
        question = f"Tôi đang dùng {meds}. Các thuốc này có nguy cơ tương tác hoặc tác dụng bất lợi nghiêm trọng không?"
        answer = translate_medlens_answer(answer_en)
        rows.append(
            normalize_dataset_row(
                {
                    "question": question,
                    "answer": answer,
                    "topic": "drug_interaction_signal",
                    "source": "ASHu2/medlens::translated_template",
                    "source_question_en": question_en,
                    "source_answer_en": answer_en,
                }
            )
        )
        if len(rows) >= limit:
            break
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def build(args: argparse.Namespace) -> None:
    random.seed(args.seed)
    meddies_rows = load_meddies(args.meddies_limit, args.seed)
    medlens_rows = load_medlens(args.medlens_limit, args.seed)
    seed_rows = augment_seed_rows(SEED_SFT, args.repeat_seed, args.seed)

    sft_rows = meddies_rows + medlens_rows + seed_rows
    random.shuffle(sft_rows)

    dpo_rows = []
    for row in SEED_DPO:
        category = classify_question(row["prompt"])
        enriched = {
            **row,
            "safety_category": category.label,
            "risk_level": category.risk_level,
            "unsafe_pattern": category.unsafe_pattern,
        }
        dpo_rows.append(enriched)
        for variant in make_informal_variants(row["prompt"], max_variants=4, seed=args.seed):
            dpo_rows.append(
                {
                    **enriched,
                    "prompt": variant,
                    "augmentation": "informal_variant",
                }
            )
    dpo_rows = dpo_rows * args.repeat_dpo
    random.shuffle(dpo_rows)

    write_jsonl(OUT_DIR / "medication_safety_vi_sft.jsonl", sft_rows)
    write_jsonl(OUT_DIR / "medication_safety_vi_dpo.jsonl", dpo_rows)

    metadata = {
        "task": "Vietnamese Medication Safety Assistant",
        "sft_rows": len(sft_rows),
        "dpo_rows": len(dpo_rows),
        "sources": {
            "meddies_rows": len(meddies_rows),
            "medlens_rows": len(medlens_rows),
            "seed_rows_augmented_repeated": len(seed_rows),
            "dpo_seed_rows_repeated": len(dpo_rows),
        },
        "vietnamese_robustness": [
            "accented and no-accent variants",
            "informal abbreviations: ko/k/khong, dc/dc, bs, ds, ks, para, ibu",
            "family-member phrasing: ba/me em hoi giup",
        ],
        "safety_taxonomy": sorted({row["safety_category"] for row in sft_rows if "safety_category" in row}),
        "system_prompt": SYSTEM_PROMPT,
        "safety_scope": "education only; no diagnosis, no prescribing, no self-adjusting medication",
    }
    (OUT_DIR / "dataset_metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--meddies-limit", type=int, default=200)
    parser.add_argument("--medlens-limit", type=int, default=100)
    parser.add_argument("--repeat-seed", type=int, default=8)
    parser.add_argument("--repeat-dpo", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


if __name__ == "__main__":
    build(parse_args())
