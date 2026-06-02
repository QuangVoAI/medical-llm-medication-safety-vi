#!/usr/bin/env python3
"""Create a Vietnamese notebook for Qwen 0.5B continued pretraining."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "notebooks" / "qwen_0_5b_medical_cpt_demo.ipynb"


def md(text: str) -> dict:
    text = textwrap.dedent(text).strip()
    return {"cell_type": "markdown", "metadata": {}, "source": [line + "\n" for line in text.splitlines()]}


def code(text: str) -> dict:
    text = textwrap.dedent(text).strip()
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [line + "\n" for line in text.splitlines()]}


cells = [
    md(
        """
        # Continued Pretraining Qwen 0.5B trên medical text tiếng Việt

        Notebook này phục vụ bài tập trước:

        > Tự thực hiện pretraining LLM, dùng Qwen 0.5B hoặc model nhỏ.

        Với tài nguyên Colab/Kaggle, ta làm **continued pretraining / domain-adaptive pretraining** thay vì pretrain từ random initialization.

        Luồng:

        ```text
        Raw medical text tiếng Việt
          -> tokenize
          -> group thành token blocks
          -> causal language modeling
          -> theo dõi train loss, eval loss, perplexity
          -> nối tiếp sang SFT/DPO medication safety
        ```
        """
    ),
    md("## 0. Cài thư viện"),
    code(
        """
        %pip install -q "transformers>=4.46.0" "datasets>=3.0.0" "accelerate>=1.1.0" "peft>=0.13.0" "bitsandbytes>=0.44.0" --upgrade-strategy only-if-needed
        """
    ),
    md(
        """
        ## 0.1. Clone repo nếu chạy trên Colab/Kaggle

        Nếu repo private, set `GITHUB_TOKEN` trong Kaggle Secret hoặc biến môi trường.
        """
    ),
    code(
        """
        import os
        import subprocess
        from pathlib import Path

        REPO_URL = "https://github.com/QuangVoAI/medical-llm-medication-safety-vi.git"

        if Path("/kaggle/working").exists():
            PROJECT_DIR = Path("/kaggle/working/medical_llm_medication_safety_vi")
        elif Path("/content").exists():
            PROJECT_DIR = Path("/content/medical_llm_medication_safety_vi")
        else:
            PROJECT_DIR = Path.cwd()

        DATA_FILE = PROJECT_DIR / "data" / "pretraining" / "medical_cpt_corpus_sample.jsonl"

        def get_github_token():
            token = os.environ.get("GITHUB_TOKEN", "").strip()
            if token:
                return token
            try:
                from kaggle_secrets import UserSecretsClient
                return UserSecretsClient().get_secret("GITHUB_TOKEN").strip()
            except Exception:
                return ""

        if not DATA_FILE.exists() and not (PROJECT_DIR / "scripts").exists():
            token = get_github_token()
            clone_url = REPO_URL.replace("https://", f"https://{token}@") if token else REPO_URL
            subprocess.run(["git", "clone", clone_url, str(PROJECT_DIR)], check=True)

        print("Project dir:", PROJECT_DIR)
        print("Data file exists:", DATA_FILE.exists())
        """
    ),
    md(
        """
        ## 1. Data format cho pretraining

        Pretraining/CPT dùng raw text:

        ```json
        {"text": "Paracetamol là thuốc giảm đau hạ sốt..."}
        ```

        Khác với SFT:

        - CPT: raw text, học next-token prediction.
        - SFT: user -> assistant, học format trả lời.
        - DPO: prompt + chosen/rejected, học preference an toàn.
        """
    ),
    code(
        """
        import json
        import math
        import random
        from pathlib import Path

        import torch
        from datasets import Dataset
        from transformers import (
            AutoModelForCausalLM,
            AutoTokenizer,
            BitsAndBytesConfig,
            DataCollatorForLanguageModeling,
            Trainer,
            TrainingArguments,
        )
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

        SEED = 42
        random.seed(SEED)
        torch.manual_seed(SEED)

        def find_project_root():
            candidates = [
                Path.cwd(),
                Path.cwd() / "medical_llm_medication_safety_vi",
                Path("/content/medical_llm_medication_safety_vi"),
                Path("/kaggle/working/medical_llm_medication_safety_vi"),
            ]
            for candidate in candidates:
                if (candidate / "data" / "pretraining" / "medical_cpt_corpus_sample.jsonl").exists():
                    return candidate
            raise FileNotFoundError("Không tìm thấy data/pretraining/medical_cpt_corpus_sample.jsonl")

        PROJECT_ROOT = find_project_root()
        CPT_PATH = PROJECT_ROOT / "data" / "pretraining" / "medical_cpt_corpus_sample.jsonl"
        SFT_PATH = PROJECT_ROOT / "data" / "processed" / "medication_safety_vi_sft.jsonl"

        MODEL_NAME = "Qwen/Qwen2.5-0.5B"
        OUT_DIR = "./qwen_0_5b_medical_cpt_lora"
        BLOCK_SIZE = 256
        MAX_STEPS = 20

        print("CUDA:", torch.cuda.is_available())
        if torch.cuda.is_available():
            print("GPU:", torch.cuda.get_device_name(0))
        print("Project root:", PROJECT_ROOT)
        """
    ),
    md("## 2. Load corpus raw text"),
    code(
        """
        def read_jsonl(path):
            rows = []
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        rows.append(json.loads(line))
            return rows

        rows = read_jsonl(CPT_PATH)

        # Nếu có SFT dataset trong repo, lấy thêm question/answer làm raw text domain.
        # Đây không phải SFT; ta chỉ nối text để model học phân bố ngôn ngữ y khoa/thuốc.
        if SFT_PATH.exists():
            for row in read_jsonl(SFT_PATH)[:300]:
                text = f"Câu hỏi: {row.get('question', '')}\\nTrả lời an toàn: {row.get('answer', '')}"
                rows.append({"text": text})

        rows = [row for row in rows if len(row.get("text", "").split()) >= 8]
        random.shuffle(rows)
        dataset = Dataset.from_list(rows)
        split = dataset.train_test_split(test_size=min(0.15, 20 / max(len(dataset), 1)), seed=SEED)

        print("Total text rows:", len(dataset))
        print("Train rows:", len(split["train"]))
        print("Eval rows:", len(split["test"]))
        print("\\nSample:")
        print(split["train"][0]["text"][:600])
        """
    ),
    md(
        """
        ## 3. Tokenize và group thành blocks

        Causal LM không học từng dòng riêng lẻ. Ta tokenize text rồi group token thành block cố định.

        Ví dụ `BLOCK_SIZE = 256` nghĩa là mỗi training example có 256 tokens.
        """
    ),
    code(
        """
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        def tokenize(batch):
            return tokenizer(batch["text"], truncation=False)

        tokenized = split.map(tokenize, batched=True, remove_columns=["text"])

        def group_texts(examples):
            concatenated = {k: sum(examples[k], []) for k in examples.keys()}
            total_length = len(concatenated["input_ids"])
            total_length = (total_length // BLOCK_SIZE) * BLOCK_SIZE
            result = {
                k: [t[i : i + BLOCK_SIZE] for i in range(0, total_length, BLOCK_SIZE)]
                for k, t in concatenated.items()
            }
            result["labels"] = result["input_ids"].copy()
            return result

        lm_data = tokenized.map(group_texts, batched=True)
        print(lm_data)
        print("Train token blocks:", len(lm_data["train"]))
        print("Eval token blocks:", len(lm_data["test"]))
        """
    ),
    md("## 4. Load Qwen 0.5B + LoRA cho continued pretraining"),
    code(
        """
        quant_config = None
        if torch.cuda.is_available():
            quant_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16,
                bnb_4bit_use_double_quant=True,
            )

        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            quantization_config=quant_config,
            torch_dtype=torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float16,
            device_map="auto" if torch.cuda.is_available() else None,
            trust_remote_code=True,
        )

        model.config.use_cache = False
        if torch.cuda.is_available():
            model = prepare_model_for_kbit_training(model)

        lora_config = LoraConfig(
            r=16,
            lora_alpha=32,
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        )
        model = get_peft_model(model, lora_config)
        model.print_trainable_parameters()
        """
    ),
    md("## 5. Generate trước khi CPT"),
    code(
        """
        def generate_continuation(prompt, max_new_tokens=80):
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            with torch.no_grad():
                out = model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    pad_token_id=tokenizer.eos_token_id,
                )
            return tokenizer.decode(out[0], skip_special_tokens=True)

        prompts = [
            "Warfarin và ibuprofen",
            "Khi quên một liều thuốc huyết áp",
            "Tự ý ngưng kháng sinh",
        ]

        print("=== BEFORE CPT ===")
        for p in prompts:
            print("\\nPROMPT:", p)
            print(generate_continuation(p))
        """
    ),
    md(
        """
        ## 6. Train CPT và theo dõi loss

        Loss ở đây là **cross entropy next-token prediction**.

        - Debug: `MAX_STEPS = 20`.
        - Train thật hơn: tăng `max_steps` lên 200-1000 hoặc dùng 1-3 epochs.
        - Learning rate nên nhỏ: `5e-5` hoặc thấp hơn.
        """
    ),
    code(
        """
        args = TrainingArguments(
            output_dir=OUT_DIR,
            per_device_train_batch_size=1,
            per_device_eval_batch_size=1,
            gradient_accumulation_steps=4,
            learning_rate=5e-5,
            max_steps=MAX_STEPS,
            warmup_steps=5,
            logging_steps=1,
            eval_strategy="steps",
            eval_steps=10,
            save_steps=20,
            save_total_limit=1,
            fp16=torch.cuda.is_available() and not torch.cuda.is_bf16_supported(),
            bf16=torch.cuda.is_available() and torch.cuda.is_bf16_supported(),
            report_to="none",
            optim="paged_adamw_8bit" if torch.cuda.is_available() else "adamw_torch",
        )

        trainer = Trainer(
            model=model,
            args=args,
            train_dataset=lm_data["train"],
            eval_dataset=lm_data["test"],
            data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False),
        )

        train_result = trainer.train()
        eval_metrics = trainer.evaluate()
        trainer.save_model(OUT_DIR)

        print("Train metrics:", train_result.metrics)
        print("Eval metrics:", eval_metrics)
        if "eval_loss" in eval_metrics:
            print("Perplexity:", math.exp(eval_metrics["eval_loss"]))
        """
    ),
    md("## 7. Generate sau CPT và so sánh"),
    code(
        """
        print("=== AFTER CPT ===")
        for p in prompts:
            print("\\nPROMPT:", p)
            print(generate_continuation(p))
        """
    ),
    md(
        """
        ## 8. Cách diễn giải kết quả

        Khi trình bày:

        - Nếu loss giảm: model dự đoán token domain tốt hơn.
        - Nếu eval loss/perplexity giảm: model bớt ngạc nhiên với text y khoa/thuốc.
        - Nếu generation sau CPT dùng thuật ngữ thuốc tự nhiên hơn: CPT có tác dụng domain adaptation.
        - Nếu generation vẫn chưa trả lời QA tốt: bình thường, vì CPT không phải SFT.

        Câu nối sang bài hiện tại:

        > CPT giúp model quen domain language. Sau đó SFT dạy model trả lời câu hỏi; DPO dạy model ưu tiên câu trả lời an toàn hơn.
        """
    ),
]


nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(nb, ensure_ascii=False, indent=2), encoding="utf-8")
print(OUT)
