# Vietnamese Medication Safety Assistant

Đây là nhánh thực nghiệm Medical LLM cho bài lab NLP:

> Vietnamese Medication Safety Assistant: SFT, DPO, RAG, and Safety Evaluation for Safer Medical LLM Responses

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

- 15 prompt tiếng Việt trong `outputs/evaluation_prompts.jsonl`, gồm câu không dấu/viết tắt, ambiguous case và off-topic prompts.
- Bảng chấm thủ công trong `outputs/manual_eval_template.csv`.
- Baseline rule/RAG đã điền trong `outputs/manual_eval_with_rule_rag_baseline.csv`.

## Nâng cấp cho tiếng Việt đời thường

Project có thêm lớp xử lý để mô phỏng cách người Việt hỏi thật:

- không dấu: `em quen thuoc huyet ap...`;
- viết tắt: `ko`, `k`, `dc`, `đc`;
- viết tắt y tế đời thường: `bs`, `ds`, `ks`;
- tên thuốc viết ngắn: `para`, `ibu`;
- hỏi thay người thân: `ba em`, `mẹ em hỏi giúp`.

Các module chính:

- `src/vi_text.py`: normalization và informal augmentation.
- `src/safety_taxonomy.py`: taxonomy lỗi safety cho DPO.
- `src/rag_knowledge.py`: RAG nhỏ bằng rule-based snippets.
- `src/evaluator.py`: rubric safety/factuality/uncertainty/actionability/Vietnamese quality.
- `app.py`: demo Gradio.

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
    UPGRADE_PLAN.md
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
    score_outputs.py
  src/
    vi_text.py
    safety_taxonomy.py
    rag_knowledge.py
    evaluator.py
  app.py
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

## Chạy demo UI

```bash
pip install -r requirements.txt
python app.py
```

Nếu chưa có model train xong, app vẫn chạy bằng rule/RAG fallback để demo pipeline. Nếu đã có model, set:

```bash
MODEL_PATH=/path/to/model-or-merged-checkpoint python app.py
```

## Giới hạn cần nói rõ

- Dataset hiện là demo-scale: 500 SFT rows nhưng phần lớn đến từ seed augmentation/repetition, không phải production dataset.
- DPO pairs được tạo theo safety taxonomy để minh họa alignment, chưa phải preference data do chuyên gia annotate.
- RAG hiện là toy RAG, retrieval bằng keyword trên vài snippets.
- Rubric evaluation là heuristic proxy, không thay thế đánh giá y khoa hoặc NLG evaluation chuyên nghiệp.

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

> Điểm khó của tiếng Việt là người dùng không luôn hỏi bằng câu chuẩn: họ có thể không gõ dấu, dùng viết tắt như `ko`, `dc`, `ks`, `bs`, hoặc hỏi thay người thân. Vì vậy project thêm informal augmentation, safety taxonomy, RAG nhỏ và rubric evaluation.
