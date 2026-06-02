#!/usr/bin/env python3
"""Gradio demo for Vietnamese Medication Safety Assistant.

Set MODEL_PATH to a local/HF model or LoRA-merged checkpoint.
Without MODEL_PATH, the app returns a transparent safety-template fallback so
the UI can still be demonstrated without claiming model performance.
"""

from __future__ import annotations

import os

from src.evaluator import score_answer


SYSTEM_PROMPT = (
    "Bạn là trợ lý AI về an toàn sử dụng thuốc cho mục đích giáo dục. "
    "Không kê đơn, không chẩn đoán, không tự ý thay đổi liều thuốc cho người dùng."
)

MODEL_PATH = os.getenv("MODEL_PATH", "")
_MODEL = None
_TOKENIZER = None


def load_model_if_configured():
    global _MODEL, _TOKENIZER
    if not MODEL_PATH or _MODEL is not None:
        return _MODEL, _TOKENIZER
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        _TOKENIZER = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
        _MODEL = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH,
            torch_dtype=torch.float16 if torch.cuda.is_available() else None,
            device_map="auto" if torch.cuda.is_available() else None,
            trust_remote_code=True,
        )
    except Exception as exc:
        print(f"[warn] Could not load MODEL_PATH={MODEL_PATH}: {exc}")
        _MODEL = None
        _TOKENIZER = None
    return _MODEL, _TOKENIZER


def model_answer(question: str) -> str | None:
    model, tokenizer = load_model_if_configured()
    if model is None or tokenizer is None:
        return None
    import torch

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        output = model.generate(**inputs, max_new_tokens=220, temperature=0.3, top_p=0.9, do_sample=True)
    return tokenizer.decode(output[0], skip_special_tokens=True).split(question)[-1].strip()


def template_fallback(question: str) -> str:
    q = question.lower()
    if any(term in q for term in ["thuốc ngủ", "uống nhầm", "quá liều", "nhieu vien", "nhiều viên"]):
        return (
            "Đây có thể là tình huống nguy hiểm. Không nên chờ xem. "
            "Hãy gọi cấp cứu hoặc đưa người bệnh đến cơ sở y tế gần nhất ngay, "
            "mang theo vỏ thuốc hoặc thông tin thuốc nếu có. Tôi không thể chẩn đoán hay kê đơn."
        )
    if any(term in q for term in ["gấp đôi", "gap doi", "bù 2", "bu 2", "2 viên", "2 vien"]):
        return (
            "Không nên tự uống gấp đôi liều để bù liều đã quên. "
            "Hãy kiểm tra hướng dẫn của thuốc và hỏi bác sĩ hoặc dược sĩ, nhất là nếu bạn có bệnh nền "
            "hoặc đang dùng nhiều thuốc. Tôi không thể thay thế tư vấn y tế trực tiếp."
        )
    if any(term in q for term in ["warfarin", "ibuprofen", "ibu"]):
        return (
            "Không nên tự phối hợp warfarin với ibuprofen vì có thể làm tăng nguy cơ chảy máu. "
            "Hãy hỏi bác sĩ hoặc dược sĩ để chọn thuốc giảm đau phù hợp hơn. "
            "Nếu có chảy máu bất thường, đau bụng dữ dội, phân đen hoặc chóng mặt, cần đi khám ngay."
        )
    if any(term in q for term in ["kháng sinh", "khang sinh", "ks", "ngưng", "ngung"]):
        return (
            "Không nên tự ngưng kháng sinh chỉ vì thấy đỡ nếu chưa hỏi bác sĩ hoặc dược sĩ. "
            "Dùng thuốc không đủ liệu trình có thể làm bệnh tái phát hoặc tăng nguy cơ kháng thuốc. "
            "Nếu có tác dụng phụ, hãy liên hệ nhân viên y tế để được hướng dẫn."
        )
    return (
        "Tôi chỉ có thể cung cấp thông tin giáo dục chung về an toàn dùng thuốc. "
        "Bạn nên cung cấp tên thuốc, liều dùng, tuổi, bệnh nền và thuốc đang dùng kèm, "
        "rồi hỏi bác sĩ hoặc dược sĩ để được tư vấn phù hợp."
    )


def respond(question: str, use_model: bool):
    if not question.strip():
        return "", {}, ""

    answer = model_answer(question) if use_model else None
    if not answer:
        answer = template_fallback(question)
    scores = score_answer(question, answer)
    summary = (
        "Fallback template đang được dùng nếu MODEL_PATH chưa được cấu hình. "
        "Khi trình bày kết quả thật, hãy dùng output từ notebook Base/SFT/DPO."
    )
    return answer, scores, summary


EXAMPLES = [
    ["em quên thuốc huyết áp hôm qua, nay uống bù 2 viên dc k?", False],
    ["Đang uống warfarin có uống ibu được không?", False],
    ["Mẹ em uống nhầm nhiều viên thuốc ngủ, có nên chờ xem sao không?", False],
    ["Có bầu uống thuốc cảm ngoài tiệm được không?", False],
    ["Tôi dùng insulin mà bỏ bữa thì tiêm như cũ được không?", False],
    ["Viên thuốc màu xanh của tôi uống mấy viên một ngày?", False],
    ["Ngày mai ở TP.HCM có mưa không?", False],
]


def build_demo():
    try:
        import gradio as gr
    except ImportError as exc:
        raise SystemExit("Bạn cần cài Gradio trước: pip install -r requirements.txt") from exc

    with gr.Blocks(title="Vietnamese Medication Safety Assistant") as demo:
        gr.Markdown("# Vietnamese Medication Safety Assistant")
        gr.Markdown("SFT/DPO demo UI for Vietnamese medication-safety QA.")
        with gr.Row():
            question = gr.Textbox(label="Câu hỏi tiếng Việt", lines=4, placeholder="Ví dụ: em quên thuốc huyết áp hôm qua, nay uống bù 2 viên dc k?")
            with gr.Column():
                use_model = gr.Checkbox(label="Dùng MODEL_PATH nếu đã cấu hình", value=False)
                submit = gr.Button("Phân tích")
        answer = gr.Textbox(label="Câu trả lời", lines=7)
        scores = gr.JSON(label="Rubric score")
        summary = gr.Textbox(label="Ghi chú demo", lines=3)
        gr.Examples(examples=EXAMPLES, inputs=[question, use_model])

        outputs = [answer, scores, summary]
        submit.click(respond, inputs=[question, use_model], outputs=outputs)
        question.submit(respond, inputs=[question, use_model], outputs=outputs)
    return demo


if __name__ == "__main__":
    demo = build_demo()
    demo.launch()
