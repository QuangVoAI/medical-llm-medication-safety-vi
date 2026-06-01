#!/usr/bin/env python3
"""Gradio demo for Vietnamese Medication Safety Assistant.

The app works in two modes:
- Agentic RAG fallback: runs anywhere and shows the safety pipeline.
- Model mode: set MODEL_PATH to a local/HF model or LoRA-merged checkpoint.
"""

from __future__ import annotations

import os


from src.agent.medication_agent import MedicationSafetyAgent


SYSTEM_PROMPT = (
    "Bạn là trợ lý AI về an toàn sử dụng thuốc cho mục đích giáo dục. "
    "Không kê đơn, không chẩn đoán, không tự ý thay đổi liều thuốc cho người dùng."
)

MODEL_PATH = os.getenv("MODEL_PATH", "")
_MODEL = None
_TOKENIZER = None
_AGENT = MedicationSafetyAgent()


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


def model_answer(question: str, context: str) -> str | None:
    model, tokenizer = load_model_if_configured()
    if model is None or tokenizer is None:
        return None
    import torch

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + "\nNgữ cảnh tham khảo:\n" + context},
        {"role": "user", "content": question},
    ]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        output = model.generate(**inputs, max_new_tokens=220, temperature=0.3, top_p=0.9, do_sample=True)
    return tokenizer.decode(output[0], skip_special_tokens=True).split(question)[-1].strip()


def respond(question: str, use_model: bool):
    if not question.strip():
        return "", "", {}, "", {}, ""

    result = _AGENT.run(question, model_answer_fn=model_answer if use_model else None)
    return result.answer, result.context, result.scores, result.summary, result.trace, result.decision


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
        gr.Markdown("Controlled Agentic RAG demo: normalize -> classify risk -> hybrid retrieve -> self-check -> answer.")
        with gr.Row():
            question = gr.Textbox(label="Câu hỏi tiếng Việt", lines=4, placeholder="Ví dụ: em quên thuốc huyết áp hôm qua, nay uống bù 2 viên dc k?")
            with gr.Column():
                use_model = gr.Checkbox(label="Dùng MODEL_PATH nếu đã cấu hình", value=False)
                submit = gr.Button("Phân tích")
        answer = gr.Textbox(label="Câu trả lời", lines=7)
        decision = gr.Textbox(label="Agent decision", lines=1)
        context = gr.Textbox(label="Hybrid RAG context", lines=5)
        trace = gr.JSON(label="Agent trace")
        scores = gr.JSON(label="Rubric score")
        summary = gr.Textbox(label="Safety summary", lines=4)
        gr.Examples(examples=EXAMPLES, inputs=[question, use_model])

        outputs = [answer, context, scores, summary, trace, decision]
        submit.click(respond, inputs=[question, use_model], outputs=outputs)
        question.submit(respond, inputs=[question, use_model], outputs=outputs)
    return demo


if __name__ == "__main__":
    demo = build_demo()
    demo.launch()
