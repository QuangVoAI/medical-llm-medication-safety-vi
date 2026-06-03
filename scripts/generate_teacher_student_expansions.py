#!/usr/bin/env python3
"""Generate larger Vietnamese SFT/DPO expansions for medication safety.

This is a practical teacher-lite expansion layer for the repo:
- grounded SFT rows in patient-facing Vietnamese
- DPO pairs with hard negatives / unsafe-but-fluent answers

It does not pretend to be clinician-verified data. It is intended to enlarge
the lab dataset so the student model can be trained on broader scenarios before
adding external sources like ViMedAQA.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATED_DIR = ROOT / "data" / "generated"

import sys

sys.path.insert(0, str(ROOT))

from src.vi_text import make_informal_variants, normalize_vi_text


PERSONAS = [
    "Tôi",
    "Em",
    "Ba em",
    "Mẹ em",
    "Người nhà tôi",
]

QUESTION_PREFIXES = [
    "",
    "Cho tôi hỏi, ",
    "Mình hỏi chút, ",
    "Cho em hỏi, ",
]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def uniq_by_key(rows: list[dict], key_fn) -> list[dict]:
    seen = set()
    out = []
    for row in rows:
        key = key_fn(row)
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def sft_row(question: str, answer: str, topic: str, source: str, grounding: str) -> dict:
    return {
        "question": normalize_vi_text(question),
        "answer": normalize_vi_text(answer),
        "topic": topic,
        "source": source,
        "grounding": grounding,
    }


def dpo_row(prompt: str, chosen: str, rejected: str, topic: str, source: str, error_type: str) -> dict:
    return {
        "prompt": normalize_vi_text(prompt),
        "chosen": normalize_vi_text(chosen),
        "rejected": normalize_vi_text(rejected),
        "topic": topic,
        "source": source,
        "error_type": error_type,
    }


def build_missed_dose_sft() -> list[dict]:
    meds = [
        ("thuốc huyết áp", "uống bù gấp đôi có thể gây tụt huyết áp, chóng mặt hoặc ngất"),
        ("thuốc tuyến giáp", "cách xử trí phụ thuộc loại thuốc và thời điểm quên liều"),
        ("thuốc mỡ máu", "tự uống bù nhiều hơn chỉ định không phải lúc nào cũng có lợi"),
        ("thuốc chống đông", "tự bù liều có thể làm tăng nguy cơ chảy máu"),
        ("thuốc tiểu đường", "tự đổi liều có thể làm tăng nguy cơ hạ hoặc tăng đường huyết"),
    ]
    time_contexts = [
        "hôm qua quên một liều",
        "sáng nay quên uống thuốc",
        "tối qua bỏ sót thuốc",
        "quên uống hai liều liên tiếp",
    ]
    rows = []
    for persona, prefix, (med, risk), ctx in itertools.product(PERSONAS, QUESTION_PREFIXES, meds, time_contexts):
        q = f"{prefix}{persona} {ctx} {med}, hôm nay có nên uống bù gấp đôi không?"
        a = (
            f"Không nên tự ý uống bù gấp đôi {med}. {risk}. "
            "Bạn nên xem hướng dẫn sử dụng của thuốc và hỏi bác sĩ hoặc dược sĩ để biết cách xử trí phù hợp với loại thuốc đang dùng."
        )
        rows.append(sft_row(q, a, "missed_dose", "teacher_grounded::missed_dose", risk))
    return rows


def build_drug_interaction_sft() -> list[dict]:
    pairs = [
        ("warfarin", "ibuprofen", "có thể làm tăng nguy cơ chảy máu"),
        ("warfarin", "aspirin", "có thể làm tăng nguy cơ chảy máu"),
        ("clopidogrel", "ibuprofen", "có thể làm tăng nguy cơ chảy máu hoặc bầm tím"),
        ("thuốc huyết áp", "thuốc cảm", "một số thuốc cảm có thể ảnh hưởng huyết áp hoặc nhịp tim"),
        ("metformin", "rượu", "có thể làm tăng nguy cơ tác dụng không mong muốn và cần được hỏi lại bác sĩ"),
        ("insulin", "rượu", "có thể làm tăng nguy cơ hạ đường huyết ở một số trường hợp"),
    ]
    intents = [
        "dùng chung được không",
        "có tương tác gì đáng lo không",
        "có nên tự uống thêm không",
        "uống cùng lúc có sao không",
    ]
    rows = []
    for persona, prefix, (a, b, risk), intent in itertools.product(PERSONAS, QUESTION_PREFIXES, pairs, intents):
        q = f"{prefix}{persona} đang dùng {a}, bây giờ muốn uống thêm {b} thì {intent}?"
        ans = (
            f"Không nên tự ý phối hợp {a} với {b} khi chưa được tư vấn. Hai thuốc này {risk}. "
            "Bạn nên hỏi bác sĩ hoặc dược sĩ trước khi dùng thêm, nhất là nếu đang có bệnh nền hoặc đã từng có tác dụng phụ."
        )
        rows.append(sft_row(q, ans, "drug_interaction", "teacher_grounded::drug_interaction", risk))
    return rows


def build_overdose_sft() -> list[dict]:
    items = [
        ("paracetamol", "độc gan"),
        ("thuốc ngủ", "buồn ngủ sâu, suy hô hấp hoặc hôn mê"),
        ("thuốc cảm", "quá liều hoặc phối hợp trùng hoạt chất"),
        ("thuốc hạ sốt", "quá liều và cần được đánh giá sớm"),
        ("vitamin sắt của trẻ", "ngộ độc nếu uống nhầm nhiều viên"),
    ]
    quantities = [
        "uống nhầm nhiều viên",
        "lỡ uống gấp đôi mấy lần trong ngày",
        "không nhớ đã uống mấy viên",
        "uống quá liều ghi trên vỏ hộp",
    ]
    rows = []
    for persona, prefix, (med, danger), qty in itertools.product(PERSONAS, QUESTION_PREFIXES, items, quantities):
        q = f"{prefix}{persona} {qty} {med}, có nên chờ ở nhà xem sao không?"
        a = (
            f"Không nên chờ theo dõi tại nhà trong tình huống này. {med.capitalize()} có thể gây {danger}. "
            "Bạn nên liên hệ cấp cứu hoặc đưa người bệnh đến cơ sở y tế càng sớm càng tốt, mang theo vỏ thuốc hoặc toa thuốc nếu có."
        )
        rows.append(sft_row(q, a, "overdose", "teacher_grounded::overdose", danger))
    return rows


def build_antibiotics_sft() -> list[dict]:
    antibiotics = ["amoxicillin", "cefixime", "azithromycin", "kháng sinh bác sĩ kê", "thuốc kháng sinh đang uống"]
    states = [
        "thấy đỡ rồi",
        "hết sốt được một ngày",
        "bớt ho và bớt đau họng",
        "đỡ triệu chứng hơn nhiều",
    ]
    rows = []
    for persona, prefix, abx, state in itertools.product(PERSONAS, QUESTION_PREFIXES, antibiotics, states):
        q = f"{prefix}{persona} đang uống {abx}, giờ {state} thì có thể tự ngưng luôn được không?"
        a = (
            "Không nên tự ý ngưng kháng sinh chỉ vì thấy đỡ triệu chứng. "
            "Ngưng sớm có thể làm nhiễm trùng chưa khỏi hẳn và góp phần tăng nguy cơ kháng kháng sinh. "
            "Bạn nên dùng theo hướng dẫn và hỏi bác sĩ nếu muốn dừng thuốc hoặc đang gặp tác dụng phụ."
        )
        rows.append(sft_row(q, a, "antibiotics_adherence", "teacher_grounded::antibiotics_adherence", "không tự ngưng kháng sinh sớm"))
    return rows


def build_pregnancy_child_elderly_sft() -> list[dict]:
    cases = [
        ("đang mang thai", "thuốc cảm", "một số thuốc không phù hợp theo tuổi thai"),
        ("đang cho con bú", "thuốc giảm đau", "một số thuốc có thể không phù hợp khi đang cho con bú"),
        ("trẻ em", "thuốc của người lớn", "liều trẻ em không thể suy ra bằng cách chia liều người lớn"),
        ("người lớn tuổi", "thuốc ngủ", "người lớn tuổi có thể nhạy cảm hơn với tác dụng phụ"),
        ("người già có nhiều bệnh nền", "thuốc cảm", "cần thận trọng vì có thể ảnh hưởng huyết áp hoặc tim mạch"),
    ]
    rows = []
    for persona, prefix, (group, med, risk) in itertools.product(PERSONAS, QUESTION_PREFIXES, cases):
        q = f"{prefix}{persona} thuộc nhóm {group}, có thể tự dùng {med} được không?"
        a = (
            f"Không nên tự ý dùng {med} cho nhóm {group}. {risk}. "
            "Bạn nên hỏi bác sĩ hoặc dược sĩ để được hướng dẫn phù hợp với tuổi, bệnh nền, thai kỳ hoặc thuốc đang dùng."
        )
        rows.append(sft_row(q, a, "pregnancy_child_elderly", "teacher_grounded::special_population", risk))
    return rows


def build_insulin_sft() -> list[dict]:
    contexts = [
        ("bỏ bữa sáng", "hạ đường huyết"),
        ("ăn ít hơn bình thường", "hạ đường huyết"),
        ("đang nôn ói nên ăn kém", "hạ đường huyết hoặc mất cân bằng đường huyết"),
        ("chuẩn bị vận động mạnh hơn thường lệ", "đường huyết thay đổi ngoài dự kiến"),
        ("đường huyết đang thấp mà tới giờ tiêm", "hạ đường huyết nặng hơn"),
    ]
    rows = []
    for persona, prefix, (ctx, risk) in itertools.product(PERSONAS, QUESTION_PREFIXES, contexts):
        q = f"{prefix}{persona} đang dùng insulin, nếu {ctx} thì có tiêm liều như bình thường không?"
        a = (
            f"Không nên tự quyết định giữ nguyên hoặc đổi liều insulin khi {ctx} nếu chưa có kế hoạch bác sĩ đã dặn trước. "
            f"Làm vậy có thể làm tăng nguy cơ {risk}. Bạn nên theo dõi đường huyết và hỏi bác sĩ để được hướng dẫn cá thể hóa."
        )
        rows.append(sft_row(q, a, "insulin_safety", "teacher_grounded::insulin", risk))
    return rows


def build_general_sft() -> list[dict]:
    cases = [
        ("đã hết hạn", "không nên tự dùng thuốc đã hết hạn nếu không được xác nhận còn an toàn"),
        ("không nhớ tên thuốc nhưng muốn uống lại", "không nên uống lại khi chưa xác định đúng thuốc"),
        ("đang uống hai loại thuốc cùng hoạt chất", "có thể dẫn tới trùng liều"),
        ("muốn tăng liều thuốc giảm đau vì chưa đỡ", "tự tăng liều có thể làm tăng nguy cơ tác dụng phụ"),
        ("đang uống thuốc mà có phát ban và khó chịu", "cần được bác sĩ hoặc dược sĩ tư vấn sớm"),
    ]
    rows = []
    for persona, prefix, (ctx, safety) in itertools.product(PERSONAS, QUESTION_PREFIXES, cases):
        q = f"{prefix}{persona} có thuốc {ctx}, giờ nên tự xử lý thế nào?"
        a = (
            f"Bạn không nên tự ý thay đổi cách dùng thuốc trong tình huống này. {safety}. "
            "Nếu không chắc thông tin thuốc là gì hoặc đang có dấu hiệu bất thường, hãy hỏi bác sĩ hoặc dược sĩ để được hướng dẫn."
        )
        rows.append(sft_row(q, a, "general_medication_safety", "teacher_grounded::general", safety))
    return rows


def expand_sft_rows(base_rows: list[dict], max_variants: int = 2) -> list[dict]:
    rows = []
    for row in base_rows:
        rows.append(row)
        for variant in make_informal_variants(row["question"], max_variants=max_variants, seed=42):
            rows.append(
                {
                    **row,
                    "question": normalize_vi_text(variant),
                    "source": f'{row["source"]}::informal_variant',
                }
            )
    return uniq_by_key(rows, lambda r: (r["question"], r["answer"]))


def build_category_dpo(prompt_rows: list[tuple[str, str, list[str], str, str]]) -> list[dict]:
    rows = []
    for prompt, chosen, rejected_options, topic, error_type in prompt_rows:
        prompt_variants = {normalize_vi_text(prompt)}
        for persona, prefix in itertools.product(PERSONAS, QUESTION_PREFIXES):
            if prompt.lower().startswith(("tôi ", "em ", "ba em", "mẹ em", "người nhà tôi")):
                prompt_variants.add(normalize_vi_text(f"{prefix}{prompt}"))
            else:
                prompt_variants.add(normalize_vi_text(f"{prefix}{persona} hỏi: {prompt[0].lower() + prompt[1:]}"))
        expanded_prompts = set(prompt_variants)
        for p in list(prompt_variants):
            expanded_prompts.update(make_informal_variants(p, max_variants=2, seed=123))

        for p in expanded_prompts:
            for idx, rejected in enumerate(rejected_options):
                source = "teacher_generated::base" if idx == 0 else "teacher_generated::alternate_rejected"
                rows.append(dpo_row(p, chosen, rejected, topic, source, error_type))
    return rows


def build_dpo_rows() -> list[dict]:
    base = []

    for med in ["thuốc huyết áp", "thuốc tiểu đường", "thuốc chống đông", "thuốc tuyến giáp"]:
        base.append(
            (
                f"Tôi quên uống {med} hôm qua, hôm nay uống gấp đôi được không?",
                f"Không nên tự ý uống gấp đôi {med} để bù liều đã quên. Bạn nên xem hướng dẫn thuốc và hỏi bác sĩ hoặc dược sĩ để được hướng dẫn phù hợp.",
                [
                    f"Nếu đã quên một liều {med} thì hôm sau uống gấp đôi để bù lại là hợp lý.",
                    f"Bạn có thể tự tăng gấp đôi {med} trong một lần để tránh mất tác dụng thuốc.",
                ],
                "missed_dose",
                "double_dose",
            )
        )

    for a, b in [("warfarin", "ibuprofen"), ("warfarin", "aspirin"), ("clopidogrel", "ibuprofen"), ("thuốc huyết áp", "thuốc cảm")]:
        base.append(
            (
                f"Đang dùng {a} thì có uống thêm {b} được không?",
                f"Không nên tự ý phối hợp {a} với {b} khi chưa được bác sĩ hoặc dược sĩ tư vấn vì có thể có tương tác hoặc làm tăng nguy cơ tác dụng phụ.",
                [
                    f"Bạn có thể uống thêm {b} cùng {a} vì thuốc thông dụng thì thường dùng chung được.",
                    f"Nếu chỉ uống một hai lần thì {a} với {b} hầu như không có gì đáng lo.",
                ],
                "drug_interaction",
                "ignores_interaction",
            )
        )

    for med in ["thuốc ngủ", "paracetamol", "thuốc cảm", "thuốc hạ sốt"]:
        base.append(
            (
                f"Người nhà tôi uống nhầm nhiều viên {med}, nên chờ xem có sao không?",
                "Không nên chờ theo dõi tại nhà. Đây có thể là tình huống nguy hiểm nên cần liên hệ cấp cứu hoặc đưa người bệnh đến cơ sở y tế ngay.",
                [
                    "Cứ chờ xem vài tiếng, nếu còn tỉnh táo thì thường không sao đâu.",
                    "Để người bệnh nghỉ ngơi ở nhà trước, chỉ cần đi viện nếu nặng lên hẳn.",
                ],
                "overdose",
                "delays_emergency_care",
            )
        )

    for abx in ["amoxicillin", "cefixime", "azithromycin", "kháng sinh bác sĩ kê"]:
        base.append(
            (
                f"Uống {abx} thấy đỡ rồi thì ngưng luôn được không?",
                "Không nên tự ý ngưng kháng sinh khi thấy đỡ. Bạn nên dùng theo hướng dẫn và hỏi bác sĩ nếu muốn dừng thuốc hoặc có tác dụng phụ.",
                [
                    "Nếu đã thấy đỡ thì có thể ngưng sớm để đỡ phải uống thuốc thêm.",
                    "Dùng kháng sinh tới lúc dễ chịu hơn là được, không cần uống đủ liệu trình.",
                ],
                "antibiotics_adherence",
                "premature_stop",
            )
        )

    for group, med in [("mang thai", "thuốc cảm"), ("đang cho con bú", "thuốc giảm đau"), ("trẻ em", "thuốc người lớn"), ("người già", "thuốc ngủ")]:
        base.append(
            (
                f"{group} có thể tự dùng {med} được không?",
                f"Không nên tự dùng {med} cho người {group} khi chưa có tư vấn y tế vì liều và độ an toàn phụ thuộc từng đối tượng cụ thể.",
                [
                    f"{group.capitalize()} vẫn có thể tự dùng {med} nếu chỉ uống ít một chút cho an tâm.",
                    f"Nếu là thuốc không kê đơn thì người {group} thường vẫn tự dùng được mà không cần hỏi thêm.",
                ],
                "pregnancy_child_elderly",
                "special_population_no_warning",
            )
        )

    for ctx in ["bỏ bữa sáng", "ăn ít hơn bình thường", "đang nôn ói nên ăn kém", "chuẩn bị vận động mạnh"]:
        base.append(
            (
                f"Đang dùng insulin mà {ctx} thì có tiêm như bình thường không?",
                "Không nên tự giữ nguyên hoặc đổi liều insulin nếu chưa có kế hoạch bác sĩ đã hướng dẫn. Bạn có nguy cơ hạ đường huyết và nên được tư vấn cá thể hóa.",
                [
                    "Cứ tiêm insulin như bình thường vì bữa ăn không ảnh hưởng nhiều đến liều.",
                    "Chỉ cần tiêm như mọi hôm cho đều, chuyện bỏ bữa thường không quan trọng lắm với insulin.",
                ],
                "insulin_safety",
                "unsafe_insulin_adjustment",
            )
        )

    for ctx in ["thuốc đã hết hạn", "không nhớ tên thuốc nhưng muốn uống lại", "đang uống hai thuốc có vẻ giống nhau", "muốn tăng liều thuốc giảm đau vì chưa đỡ"]:
        base.append(
            (
                f"Tôi có {ctx}, giờ tự xử lý được không?",
                "Bạn không nên tự ý thay đổi cách dùng thuốc trong tình huống này. Hãy hỏi bác sĩ hoặc dược sĩ khi chưa chắc mình đang dùng đúng thuốc hoặc đúng liều.",
                [
                    "Bạn cứ tự điều chỉnh thử trước, nếu không ổn thì mới hỏi sau cũng được.",
                    "Các vấn đề thuốc thông thường có thể tự xử lý trước ở nhà, không cần hỏi ngay.",
                ],
                "general_medication_safety",
                "overconfident_self_management",
            )
        )

    return uniq_by_key(build_category_dpo(base), lambda r: (r["prompt"], r["chosen"], r["rejected"]))


def main() -> None:
    sft_base = []
    sft_base.extend(build_missed_dose_sft())
    sft_base.extend(build_drug_interaction_sft())
    sft_base.extend(build_overdose_sft())
    sft_base.extend(build_antibiotics_sft())
    sft_base.extend(build_pregnancy_child_elderly_sft())
    sft_base.extend(build_insulin_sft())
    sft_base.extend(build_general_sft())
    sft_rows = expand_sft_rows(uniq_by_key(sft_base, lambda r: (r["question"], r["answer"])), max_variants=2)

    dpo_rows = build_dpo_rows()

    write_jsonl(GENERATED_DIR / "teacher_grounded_sft.jsonl", sft_rows)
    write_jsonl(GENERATED_DIR / "teacher_generated_dpo.jsonl", dpo_rows)

    summary = {
        "teacher_grounded_sft_rows": len(sft_rows),
        "teacher_generated_dpo_rows": len(dpo_rows),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
