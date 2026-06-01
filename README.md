# Vietnamese Medication Safety Assistant

Đây là nhánh thực nghiệm Medical LLM cho bài lab NLP:

> Vietnamese Medication Safety Assistant: SFT and DPO Alignment for Safer Medical LLM Responses

Mục tiêu không phải xây công cụ tư vấn y tế thật, mà là demo pipeline SFT/DPO cho một bài toán medical NLP có rủi ro rõ ràng: an toàn sử dụng thuốc cho người Việt.

## Bài toán

Input là câu hỏi tiếng Việt của người dùng về thuốc:

- quên liều;
- tự uống bù liều;
- tự ngưng thuốc;
- tương tác thuốc;
- quá liều;
- kháng sinh;
- thuốc huyết áp;
- insulin/tiểu đường;
- phụ nữ mang thai, trẻ em, người già.

Output mong muốn:

- trả lời bằng tiếng Việt dễ hiểu;
- không kê đơn, không chẩn đoán;
- không khuyên tự đổi liều/tự ngưng thuốc;
- nêu nguy cơ chính;
- khuyên hỏi bác sĩ/dược sĩ khi cần;
- nhận diện tình huống cần cấp cứu.

## Dataset chốt

SFT dataset:

- `Meddies/meddies-qa`, config `qa_pharmaceuticals`: nguồn QA tiếng Việt về dược/pharmaceuticals.
- `ASHu2/medlens`: nguồn tín hiệu tương tác thuốc, được chuyển thành câu hỏi/câu trả lời tiếng Việt bằng template.
- Seed set tiếng Việt tự viết để bao phủ các tình huống safety phổ biến ở Việt Nam.

DPO dataset:

- Preference pairs tiếng Việt tự tạo:
  - `chosen`: câu trả lời an toàn, thận trọng.
  - `rejected`: câu trả lời nguy hiểm hoặc quá chắc chắn.

Evaluation:

- 8 prompt tiếng Việt trong `outputs/evaluation_prompts.jsonl`.
- Bảng chấm thủ công trong `outputs/manual_eval_template.csv`.

## Cấu trúc

```text
medical_llm_medication_safety_vi/
  data/processed/
    medication_safety_vi_sft.jsonl
    medication_safety_vi_dpo.jsonl
    dataset_metadata.json
  docs/
    EXPERIMENT_PLAN.md
    DATASET_STRATEGY.md
  notebooks/
    medication_safety_vi_sft_dpo_demo.ipynb
  outputs/
    evaluation_prompts.jsonl
    manual_eval_template.csv
    RESULT_TEMPLATE.md
  scripts/
    build_medication_safety_datasets.py
    create_eval_artifacts.py
    create_notebook.py
```

## Chạy local để tạo dữ liệu

```bash
cd "/Users/springwang/Library/Mobile Documents/com~apple~CloudDocs/juniorYear/Research/medical_llm_medication_safety_vi"
python scripts/build_medication_safety_datasets.py
python scripts/create_eval_artifacts.py
python scripts/create_notebook.py
```

Nếu máy local không có thư viện `datasets`, script vẫn tạo được phần seed khi chạy trong môi trường có dependency hoặc sau khi cài:

```bash
pip install datasets
```

## Train demo

Chạy notebook:

```text
notebooks/medication_safety_vi_sft_dpo_demo.ipynb
```

Khuyến nghị Colab/Kaggle GPU:

- base model: `Qwen/Qwen2.5-1.5B-Instruct`;
- fallback: `Qwen/Qwen2.5-0.5B-Instruct`;
- method: QLoRA + LoRA;
- SFT trước, DPO sau;
- so sánh Base vs SFT vs SFT + DPO.

## Câu nói khi trình bày

> Em chọn Medication Safety vì đây là một bài toán Medical LLM rất phù hợp với SFT và DPO. SFT giúp model học cách trả lời tiếng Việt theo format an toàn. DPO giúp model ưu tiên câu trả lời thận trọng hơn, tránh các lời khuyên nguy hiểm như tự uống bù liều, tự ngưng kháng sinh, hoặc dùng chung thuốc có nguy cơ tương tác.
