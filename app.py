#!/usr/bin/env python3
"""Gradio demo for Vietnamese Medication Safety Assistant.

The app works in two modes:
- Rule/RAG fallback: runs anywhere and shows the safety pipeline.
- Model mode: set MODEL_PATH to a local/HF model or LoRA-merged checkpoint.
"""

from __future__ import annotations

import os


from src.evaluator import score_answer
from src.rag_knowledge import retrieve_snippets
from src.safety_taxonomy import classify_question, risk_badge
from src.vi_text import normalize_vi_text


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


def rule_based_answer(question: str) -> tuple[str, str]:
    category = classify_question(question)
    snippets = retrieve_snippets(question)
    context_lines = [f"- {s.title}: {s.content} {s.action}" for s in snippets]
    context = "\n".join(context_lines) if context_lines else "- Không tìm thấy snippet cụ thể; áp dụng nguyên tắc an toàn thuốc chung."

    if category.risk_level == "urgent":
        answer = (
            "Đây có thể là tình huống nguy hiểm. Bạn không nên chờ theo dõi tại nhà. "
            "Hãy gọi cấp cứu hoặc đưa người bệnh đến cơ sở y tế ngay, và mang theo vỏ thuốc nếu có. "
            "Mình chỉ cung cấp thông tin giáo dục, không thay thế nhân viên y tế."
        )
    else:
        must = "; ".join(category.must_include)
        answer = (
            f"Với câu hỏi này, hướng an toàn là: {must}. "
            "Bạn không nên tự ý thêm, ngưng, đổi thuốc hoặc đổi liều khi chưa có hướng dẫn chuyên môn. "
            "Nếu có triệu chứng nặng, bất thường hoặc không chắc loại thuốc đang dùng, hãy hỏi bác sĩ/dược sĩ."
        )
    return answer, context


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
    question = normalize_vi_text(question)
    if not question:
        return "", "", {}, ""
    category = classify_question(question)
    fallback_answer, context = rule_based_answer(question)
    answer = model_answer(question, context) if use_model else None
    final_answer = answer or fallback_answer
    scores = score_answer(question, final_answer)
    badge = risk_badge(category)
    summary = f"Risk label: {badge}\nSafety category: {category.label}\nMode: {'model' if answer else 'rule/RAG fallback'}"
    return final_answer, context, scores, summary


EXAMPLES = [
    ["em quên thuốc huyết áp hôm qua, nay uống bù 2 viên dc k?", False],
    ["Đang uống warfarin có uống ibu được không?", False],
    ["Mẹ em uống nhầm nhiều viên thuốc ngủ, có nên chờ xem sao không?", False],
    ["Có bầu uống thuốc cảm ngoài tiệm được không?", False],
    ["Tôi dùng insulin mà bỏ bữa thì tiêm như cũ được không?", False],
]


def build_demo():
    try:
        import gradio as gr
    except ImportError as exc:
        raise SystemExit("Bạn cần cài Gradio trước: pip install -r requirements.txt") from exc

    with gr.Blocks(title="Vietnamese Medication Safety Assistant") as demo:
        gr.Markdown("# Vietnamese Medication Safety Assistant")
        gr.Markdown("Demo học thuật cho SFT/DPO, có lớp normalization, safety taxonomy, RAG nhỏ và rubric đánh giá.")
        with gr.Row():
            question = gr.Textbox(label="Câu hỏi tiếng Việt", lines=4, placeholder="Ví dụ: em quên thuốc huyết áp hôm qua, nay uống bù 2 viên dc k?")
            with gr.Column():
                use_model = gr.Checkbox(label="Dùng MODEL_PATH nếu đã cấu hình", value=False)
                submit = gr.Button("Phân tích")
        answer = gr.Textbox(label="Câu trả lời", lines=7)
        context = gr.Textbox(label="RAG context", lines=5)
        scores = gr.JSON(label="Rubric score")
        summary = gr.Textbox(label="Safety summary", lines=4)
        gr.Examples(examples=EXAMPLES, inputs=[question, use_model])

        submit.click(respond, inputs=[question, use_model], outputs=[answer, context, scores, summary])
        question.submit(respond, inputs=[question, use_model], outputs=[answer, context, scores, summary])
    return demo


if __name__ == "__main__":
    demo = build_demo()
    demo.launch()
