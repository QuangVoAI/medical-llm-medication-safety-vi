# Upgrade Plan

## Mục tiêu nâng cấp

Bản nâng cấp chuyển project từ demo SFT/DPO cơ bản thành một pipeline rõ ràng hơn cho người Việt:

```text
Vietnamese input
  -> normalization + informal variants
  -> safety taxonomy
  -> small RAG knowledge layer
  -> SFT/DPO training
  -> rubric evaluation
  -> Gradio demo
```

## 1. Vietnamese Robustness

Tiếng Việt thực tế có nhiều biến thể:

- có dấu / không dấu;
- viết tắt: `ko`, `k`, `khong`, `dc`, `đc`;
- viết tắt y tế đời thường: `bs`, `ds`, `ks`;
- tên thuốc viết ngắn: `para`, `ibu`;
- câu hỏi qua người thân: `ba em`, `mẹ em`, `hỏi giúp`.

Project hiện có module:

```text
src/vi_text.py
```

Module này tạo query variants cho seed data, giúp SFT/DPO thấy nhiều cách hỏi gần với người Việt hơn.

## 2. Safety Taxonomy

Thay vì chỉ có chosen/rejected chung chung, DPO pairs được gắn taxonomy lỗi:

- `missed_dose`: uống bù/gấp đôi liều;
- `drug_interaction`: dùng chung thuốc có nguy cơ;
- `overdose`: quá liều/uống nhầm nhiều thuốc;
- `stop_medication`: tự ngưng thuốc;
- `pregnancy_child_elderly`: nhóm nhạy cảm;
- `diabetes_insulin`: insulin và bỏ bữa;
- `general_medication_safety`: câu hỏi thuốc chung.

Module:

```text
src/safety_taxonomy.py
```

Khi trình bày:

> Em thiết kế preference data theo taxonomy lỗi safety. Mỗi rejected answer đại diện cho một hành vi nguy hiểm mà Medical LLM cần tránh.

## 3. RAG nhẹ

Module:

```text
src/rag_knowledge.py
```

RAG ở đây là bản nhỏ, rule-based, dùng vài snippet an toàn thuốc để minh họa:

- quên liều;
- warfarin + NSAID;
- paracetamol + rượu;
- kháng sinh;
- quá liều;
- phụ nữ mang thai/trẻ em;
- insulin và bỏ bữa.

Khi trình bày:

> Fine-tuning giúp model học hành vi; RAG giúp đưa thêm ngữ cảnh an toàn để giảm hallucination.

## 4. Evaluation Rubric

Module:

```text
src/evaluator.py
scripts/score_outputs.py
```

Rubric gồm:

- safety;
- factuality;
- uncertainty;
- actionability;
- Vietnamese quality.

Mỗi tiêu chí chấm 0-3. Đây là heuristic cho demo, không thay thế đánh giá chuyên gia.

## 5. Gradio Demo

File:

```text
app.py
```

Chạy:

```bash
pip install -r requirements.txt
python app.py
```

App có:

- ô nhập câu hỏi tiếng Việt;
- checkbox dùng model nếu có `MODEL_PATH`;
- RAG context;
- safety summary;
- rubric score.

Nếu chưa có model train xong, app vẫn chạy bằng rule/RAG fallback để demo pipeline.

## 6. Thứ tự làm thí nghiệm

```text
1. Build dataset
2. Chạy notebook SFT
3. Chạy DPO
4. Sinh output Base/SFT/DPO cho eval prompts
5. Điền manual_eval_template.csv
6. Chạy scripts/score_outputs.py
7. Trình bày bảng score và 3 ví dụ qualitative
```

## Câu chốt trước Lab

> Điểm khó của Medication Safety Assistant tiếng Việt không chỉ là kiến thức thuốc, mà còn là robustness với cách người Việt hỏi rất đa dạng: không dấu, viết tắt, tiếng lóng, hỏi thay người thân. Vì vậy em thêm normalization, informal augmentation, safety taxonomy, DPO preference pairs và rubric evaluation để đánh giá hành vi an toàn.
