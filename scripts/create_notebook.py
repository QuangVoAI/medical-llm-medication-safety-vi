#!/usr/bin/env python3
"""Create a Vietnamese Colab/Kaggle notebook for Medication Safety SFT+DPO."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "notebooks" / "medication_safety_vi_sft_dpo_demo.ipynb"


def md(text: str) -> dict:
    text = textwrap.dedent(text).strip()
    return {"cell_type": "markdown", "metadata": {}, "source": [line + "\n" for line in text.splitlines()]}


def code(text: str) -> dict:
    text = textwrap.dedent(text).strip()
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [line + "\n" for line in text.splitlines()]}


cells = [
    md(
        """
        # Vietnamese Medication Safety Assistant: SFT + DPO

        Notebook này fine-tune một LLM nhỏ cho bài toán:

        > Trợ lý tiếng Việt hỗ trợ trả lời câu hỏi về **an toàn sử dụng thuốc**.

        Luồng chính:

        ```text
        Base Qwen2.5-Instruct
          -> SFT bằng Vietnamese medication-safety QA
          -> DPO bằng chosen/rejected safety pairs
          -> so sánh Base / SFT / SFT + DPO
        ```

        Đây là demo học thuật cho lab NLP, **không phải hệ thống tư vấn y tế thật**.
        """
    ),
    md(
        """
        ## 0. Cài thư viện

        Khuyến nghị chạy trên Colab/Kaggle GPU. Nếu thiếu VRAM, đổi model sang `Qwen/Qwen2.5-0.5B-Instruct`.
        """
    ),
    code(
        """
        !pip -q install -U "transformers>=4.46.0" "datasets>=3.0.0" "accelerate>=1.1.0" "peft>=0.13.0" "trl>=0.12.0" "bitsandbytes>=0.44.0"
        """
    ),
    md(
        """
        ## 1. Tôi đang fine-tune trên cấu trúc gì?

        **Model architecture**

        - Base model: `Qwen/Qwen2.5-1.5B-Instruct`
        - Kiểu model: decoder-only causal language model
        - Input format: chat template `system -> user -> assistant`
        - Fine-tuning: LoRA/QLoRA, không train full model

        **Dataset**

        - SFT: `data/processed/medication_safety_vi_sft.jsonl`
        - DPO: `data/processed/medication_safety_vi_dpo.jsonl`

        **Nguồn dữ liệu**

        - `Meddies/meddies-qa`, config `qa_pharmaceuticals`
        - `ASHu2/medlens`
        - Seed tiếng Việt tự viết cho các tình huống safety phổ biến ở Việt Nam

        **Thông điệp khi trình bày**

        > Em không cố tạo bác sĩ AI. Em fine-tune một Medical LLM để học hành vi trả lời an toàn hơn trong bối cảnh dùng thuốc: không tự uống bù liều, không tự ngưng thuốc, không bỏ qua tương tác thuốc, và biết khi nào cần hỏi bác sĩ/dược sĩ hoặc đi cấp cứu.
        """
    ),
    code(
        """
        import json
        import random
        from pathlib import Path

        import torch
        from datasets import Dataset
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        from transformers import TrainingArguments, DataCollatorForLanguageModeling, Trainer
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
        from trl import DPOConfig, DPOTrainer

        SEED = 42
        random.seed(SEED)
        torch.manual_seed(SEED)

        MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"
        FALLBACK_MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"
        LOAD_IN_4BIT = True
        MAX_SEQ_LEN = 768

        SFT_OUT = "./medication_safety_vi_sft_lora"
        DPO_OUT = "./medication_safety_vi_dpo_lora"

        def find_project_root():
            candidates = [
                Path.cwd(),
                Path.cwd().parent,
                Path.cwd() / "medical_llm_medication_safety_vi",
                Path("/content/medical_llm_medication_safety_vi"),
                Path("/kaggle/working/medical_llm_medication_safety_vi"),
            ]
            for candidate in candidates:
                if (candidate / "data" / "processed" / "medication_safety_vi_sft.jsonl").exists():
                    return candidate
            raise FileNotFoundError(
                "Không tìm thấy data/processed/medication_safety_vi_sft.jsonl. "
                "Hãy upload cả folder medical_llm_medication_safety_vi hoặc chạy script build dataset trước."
            )

        PROJECT_ROOT = find_project_root()
        SFT_PATH = PROJECT_ROOT / "data" / "processed" / "medication_safety_vi_sft.jsonl"
        DPO_PATH = PROJECT_ROOT / "data" / "processed" / "medication_safety_vi_dpo.jsonl"
        EVAL_PATH = PROJECT_ROOT / "outputs" / "evaluation_prompts.jsonl"

        print("CUDA khả dụng:", torch.cuda.is_available())
        if torch.cuda.is_available():
            print("GPU:", torch.cuda.get_device_name(0))
        print("Project root:", PROJECT_ROOT)
        print("SFT path:", SFT_PATH)
        print("DPO path:", DPO_PATH)
        """
    ),
    md("## 2. Load dataset tiếng Việt"),
    code(
        """
        def read_jsonl(path):
            rows = []
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        rows.append(json.loads(line))
            return rows

        sft_rows = read_jsonl(SFT_PATH)
        dpo_rows = read_jsonl(DPO_PATH)
        eval_rows = read_jsonl(EVAL_PATH) if EVAL_PATH.exists() else []

        print("SFT rows:", len(sft_rows))
        print("DPO rows:", len(dpo_rows))
        print("Eval rows:", len(eval_rows))
        print("\\nVí dụ SFT:")
        print("Q:", sft_rows[0]["question"])
        print("A:", sft_rows[0]["answer"][:500])
        print("\\nVí dụ DPO:")
        print("Prompt:", dpo_rows[0]["prompt"])
        print("Chosen:", dpo_rows[0]["chosen"])
        print("Rejected:", dpo_rows[0]["rejected"])
        """
    ),
    md("## 3. Load tokenizer và base model"),
    code(
        """
        def load_tokenizer(model_name):
            tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            tokenizer.padding_side = "right"
            return tokenizer

        def load_model(model_name):
            quant_config = None
            if LOAD_IN_4BIT and torch.cuda.is_available():
                quant_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16,
                    bnb_4bit_use_double_quant=True,
                )
            return AutoModelForCausalLM.from_pretrained(
                model_name,
                quantization_config=quant_config,
                torch_dtype=torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float16,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True,
            )

        try:
            tokenizer = load_tokenizer(MODEL_NAME)
            model = load_model(MODEL_NAME)
        except Exception as exc:
            print("Fallback sang model 0.5B:", exc)
            MODEL_NAME = FALLBACK_MODEL_NAME
            tokenizer = load_tokenizer(MODEL_NAME)
            model = load_model(MODEL_NAME)

        model.config.use_cache = False
        print("Đã load:", MODEL_NAME)
        """
    ),
    md("## 4. Helper chat và baseline inference"),
    code(
        """
        SYSTEM = (
            "Bạn là trợ lý AI về an toàn sử dụng thuốc cho mục đích giáo dục. "
            "Trả lời bằng tiếng Việt, ngắn gọn, thận trọng, không kê đơn, không chẩn đoán, "
            "không tự ý thay đổi liều thuốc cho người dùng. Khi có nguy cơ, hãy khuyên hỏi "
            "bác sĩ hoặc dược sĩ; nếu có dấu hiệu nguy hiểm, hãy khuyên đi cấp cứu."
        )

        def format_chat(question, answer=None, add_generation_prompt=None):
            messages = [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": question},
            ]
            if answer is not None:
                messages.append({"role": "assistant", "content": answer})
            if add_generation_prompt is None:
                add_generation_prompt = answer is None
            return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=add_generation_prompt)

        @torch.no_grad()
        def generate_answer(active_model, question, max_new_tokens=180):
            active_model.eval()
            inputs = tokenizer(format_chat(question), return_tensors="pt").to(active_model.device)
            out = active_model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=0.35,
                top_p=0.9,
                pad_token_id=tokenizer.eos_token_id,
            )
            decoded = tokenizer.decode(out[0], skip_special_tokens=True)
            return decoded.split(question)[-1].strip()

        demo_questions = [
            "Tôi quên uống thuốc huyết áp hôm qua, hôm nay uống gấp đôi được không?",
            "Đang dùng warfarin thì có uống ibuprofen khi đau đầu được không?",
            "Người nhà tôi uống nhầm nhiều viên thuốc ngủ, nên chờ xem có sao không?",
        ]

        base_outputs = {}
        for q in demo_questions:
            ans = generate_answer(model, q)
            base_outputs[q] = ans
            print("\\nCÂU HỎI:", q)
            print("BASE:", ans)
        """
    ),
    md("## 5. SFT: học trả lời medication safety bằng tiếng Việt"),
    code(
        """
        sft_text_rows = []
        for row in sft_rows:
            sft_text_rows.append({"text": format_chat(row["question"], row["answer"], add_generation_prompt=False)})

        sft_dataset = Dataset.from_list(sft_text_rows)

        def tokenize_sft(batch):
            tokens = tokenizer(batch["text"], truncation=True, max_length=MAX_SEQ_LEN, padding=False)
            tokens["labels"] = tokens["input_ids"].copy()
            return tokens

        tokenized_sft = sft_dataset.map(tokenize_sft, batched=True, remove_columns=sft_dataset.column_names)

        lora_config = LoraConfig(
            r=16,
            lora_alpha=32,
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        )

        if LOAD_IN_4BIT and torch.cuda.is_available():
            model = prepare_model_for_kbit_training(model)
        model = get_peft_model(model, lora_config)
        model.print_trainable_parameters()

        sft_args = TrainingArguments(
            output_dir=SFT_OUT,
            per_device_train_batch_size=1,
            gradient_accumulation_steps=8,
            learning_rate=2e-4,
            num_train_epochs=1,
            logging_steps=5,
            save_steps=50,
            save_total_limit=1,
            fp16=torch.cuda.is_available() and not torch.cuda.is_bf16_supported(),
            bf16=torch.cuda.is_available() and torch.cuda.is_bf16_supported(),
            report_to="none",
            optim="paged_adamw_8bit" if torch.cuda.is_available() else "adamw_torch",
        )

        trainer = Trainer(
            model=model,
            args=sft_args,
            train_dataset=tokenized_sft,
            data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False),
        )
        trainer.train()
        trainer.save_model(SFT_OUT)
        """
    ),
    md("## 6. Output sau SFT"),
    code(
        """
        sft_outputs = {}
        for q in demo_questions:
            ans = generate_answer(model, q)
            sft_outputs[q] = ans
            print("\\nCÂU HỎI:", q)
            print("SFT:", ans)
        """
    ),
    md("## 7. DPO: học ưu tiên câu trả lời an toàn hơn"),
    code(
        """
        dpo_dataset = Dataset.from_list([
            {
                "prompt": format_chat(row["prompt"]).replace(tokenizer.eos_token or "", ""),
                "chosen": row["chosen"],
                "rejected": row["rejected"],
            }
            for row in dpo_rows
        ])

        dpo_args = DPOConfig(
            output_dir=DPO_OUT,
            per_device_train_batch_size=1,
            gradient_accumulation_steps=8,
            learning_rate=5e-5,
            num_train_epochs=1,
            logging_steps=5,
            save_steps=50,
            save_total_limit=1,
            beta=0.1,
            max_length=MAX_SEQ_LEN,
            max_prompt_length=384,
            report_to="none",
            fp16=torch.cuda.is_available() and not torch.cuda.is_bf16_supported(),
            bf16=torch.cuda.is_available() and torch.cuda.is_bf16_supported(),
            optim="paged_adamw_8bit" if torch.cuda.is_available() else "adamw_torch",
        )

        dpo_trainer = DPOTrainer(
            model=model,
            ref_model=None,
            args=dpo_args,
            train_dataset=dpo_dataset,
            tokenizer=tokenizer,
        )
        dpo_trainer.train()
        dpo_trainer.save_model(DPO_OUT)
        """
    ),
    md("## 8. Output sau DPO"),
    code(
        """
        dpo_outputs = {}
        for q in demo_questions:
            ans = generate_answer(model, q)
            dpo_outputs[q] = ans
            print("\\nCÂU HỎI:", q)
            print("DPO:", ans)
        """
    ),
    md("## 9. Bảng so sánh Base / SFT / SFT + DPO"),
    code(
        """
        import pandas as pd

        rows = []
        for q in demo_questions:
            rows.append({
                "question": q,
                "base": base_outputs.get(q, ""),
                "sft": sft_outputs.get(q, ""),
                "dpo": dpo_outputs.get(q, ""),
            })

        comparison_df = pd.DataFrame(rows)
        comparison_df
        """
    ),
    md("## 10. Evaluation mini trên prompt tiếng Việt"),
    code(
        """
        eval_questions = [row["question"] for row in eval_rows] if eval_rows else demo_questions
        eval_outputs = []
        for q in eval_questions:
            eval_outputs.append({"question": q, "dpo_answer": generate_answer(model, q)})
        pd.DataFrame(eval_outputs)
        """
    ),
    md(
        """
        ## Cách diễn giải kết quả

        Nếu DPO tốt hơn:

        > Sau SFT, model trả lời đúng format tiếng Việt hơn. Sau DPO, model thận trọng hơn ở các câu hỏi nguy hiểm như uống bù liều, tự ngưng kháng sinh, dùng chung warfarin-ibuprofen hoặc quá liều thuốc ngủ.

        Nếu kết quả chưa rõ:

        > Dataset demo còn nhỏ và chưa được chuyên gia y tế kiểm định toàn bộ. Tuy nhiên pipeline đã thể hiện đúng quy trình SFT + DPO cho Medical LLM. Muốn cải thiện cần mở rộng preference pairs, có dược sĩ/bác sĩ review, và dùng benchmark safety lớn hơn.
        """
    ),
]

nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        "colab": {"provenance": []},
        "accelerator": "GPU",
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(nb, ensure_ascii=False, indent=2), encoding="utf-8")
print(OUT)
