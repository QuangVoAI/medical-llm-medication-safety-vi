# Vietnamese Medication Safety Assistant

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](#)
[![Task](https://img.shields.io/badge/Task-Medication%20Safety-green)](#)
[![Training](https://img.shields.io/badge/Training-SFT%20%2B%20DPO-orange)](#)
[![Scope](https://img.shields.io/badge/Scope-Research%20Demo-lightgrey)](#)

Vietnamese Medication Safety Assistant is a Medical LLM lab project for safer Vietnamese medication question answering.

The project demonstrates how to combine:

- Vietnamese instruction data
- informal Vietnamese augmentation
- SFT with LoRA/QLoRA
- DPO safety preference alignment
- a small rule-based RAG layer
- safety-oriented evaluation
- a Gradio demo UI

This is a research and education demo, not a clinical product.

## Problem

Vietnamese users often ask medication questions in messy, real-world language:

```text
em quen thuoc huyet ap hom qua, nay uong bu 2 vien dc k?
ba em dang uong warfarin, dau dau uong ibu dc ko?
uống ks thấy đỡ rồi ngưng luôn được không?
```

The assistant should avoid unsafe behavior:

- no self-adjusting dosage
- no self-stopping medication
- no confident diagnosis or prescribing
- no ignoring drug interactions
- no delaying urgent care for overdose
- clear advice to contact a doctor/pharmacist when needed

## System Flow

```mermaid
flowchart TD
    A["Vietnamese user question"] --> B["Vietnamese normalization"]
    B --> C["Safety taxonomy classifier"]
    C --> D["Toy RAG retrieval"]
    D --> E["LLM response generation"]
    E --> F["Safety rubric evaluation"]
    F --> G["Demo output table"]

    H["Meddies QA"] --> I["SFT dataset"]
    J["MedLens"] --> I
    K["Vietnamese seed safety data"] --> I
    L["Informal variants: ko, dc, ks, ibu"] --> I

    I --> M["SFT with LoRA/QLoRA"]
    N["Chosen / rejected safety pairs"] --> O["DPO alignment"]
    M --> O
    O --> E
```

## Training Flow

```mermaid
flowchart LR
    A["Qwen2.5 Instruct Base"] --> B["SFT on Vietnamese medication QA"]
    B --> C["SFT LoRA adapter"]
    C --> D["DPO on safety preference pairs"]
    D --> E["SFT + DPO adapter"]
    E --> F["Evaluate Base / SFT / DPO"]
```

## Repository Map

| Path | Purpose |
|---|---|
| [notebooks/medication_safety_vi_sft_dpo_demo.ipynb](notebooks/medication_safety_vi_sft_dpo_demo.ipynb) | Main Colab/Kaggle training notebook |
| [data/processed/medication_safety_vi_sft.jsonl](data/processed/medication_safety_vi_sft.jsonl) | Vietnamese SFT data |
| [data/processed/medication_safety_vi_dpo.jsonl](data/processed/medication_safety_vi_dpo.jsonl) | DPO chosen/rejected pairs |
| [src/vi_text.py](src/vi_text.py) | Vietnamese normalization and informal augmentation |
| [src/safety_taxonomy.py](src/safety_taxonomy.py) | Safety category taxonomy |
| [src/rag_knowledge.py](src/rag_knowledge.py) | Small keyword-based RAG knowledge layer |
| [src/evaluator.py](src/evaluator.py) | Heuristic safety rubric |
| [app.py](app.py) | Gradio demo app |
| [outputs/evaluation_prompts.jsonl](outputs/evaluation_prompts.jsonl) | Evaluation prompts |
| [outputs/manual_eval_with_rule_rag_baseline.csv](outputs/manual_eval_with_rule_rag_baseline.csv) | Filled rule/RAG baseline answers |
| [docs/PIPELINE.md](docs/PIPELINE.md) | Detailed system pipeline |
| [docs/DATASET_STRATEGY.md](docs/DATASET_STRATEGY.md) | Dataset sources and limitations |
| [docs/UPGRADE_PLAN.md](docs/UPGRADE_PLAN.md) | Upgrade notes and presentation talking points |

## Dataset Snapshot

Current generated dataset:

| Split | Rows | Notes |
|---|---:|---|
| SFT | 500 | Meddies + MedLens + Vietnamese seed augmentation |
| DPO | 400 | Safety preference pairs with informal variants |
| Evaluation | 15 | Medication safety, informal Vietnamese, ambiguous and off-topic prompts |

Sources:

- [Meddies/meddies-qa](https://huggingface.co/datasets/Meddies/meddies-qa)
- [ASHu2/medlens](https://huggingface.co/datasets/ASHu2/medlens)
- Vietnamese seed safety data written for this lab demo

## Vietnamese Robustness

The project explicitly includes common Vietnamese input variants:

| Phenomenon | Example |
|---|---|
| No accents | `em quen thuoc huyet ap...` |
| Short forms | `ko`, `k`, `dc`, `đc` |
| Medical shorthand | `bs`, `ds`, `ks` |
| Drug shorthand | `para`, `ibu` |
| Family proxy questions | `ba em`, `mẹ em hỏi giúp` |

## Quickstart

Install dependencies:

```bash
pip install -r requirements.txt
```

Rebuild local artifacts:

```bash
python scripts/build_medication_safety_datasets.py
python scripts/create_eval_artifacts.py
python scripts/fill_rule_rag_baseline.py
python scripts/score_outputs.py \
  --input outputs/manual_eval_with_rule_rag_baseline.csv \
  --output outputs/scored_rule_rag_baseline.csv
```

Run the demo UI:

```bash
python app.py
```

If a trained or merged model checkpoint is available:

```bash
MODEL_PATH=/path/to/model-or-checkpoint python app.py
```

## Training

Open and run:

```text
notebooks/medication_safety_vi_sft_dpo_demo.ipynb
```

Recommended setup:

| Component | Choice |
|---|---|
| GPU | Colab/Kaggle T4 or better |
| Base model | `Qwen/Qwen2.5-1.5B-Instruct` |
| Fallback model | `Qwen/Qwen2.5-0.5B-Instruct` |
| Method | QLoRA + LoRA |
| Stages | Base inference -> SFT -> DPO -> evaluation |

## Evaluation Flow

```mermaid
flowchart TD
    A["15 evaluation prompts"] --> B["Base model output"]
    A --> C["SFT model output"]
    A --> D["SFT + DPO model output"]
    B --> E["Manual CSV table"]
    C --> E
    D --> E
    E --> F["Heuristic score_outputs.py"]
    F --> G["Safety / factuality / uncertainty / actionability / Vietnamese quality"]
```

The current repo includes a filled rule/RAG baseline so the evaluation table is not empty before GPU training:

- [outputs/manual_eval_with_rule_rag_baseline.csv](outputs/manual_eval_with_rule_rag_baseline.csv)
- [outputs/scored_rule_rag_baseline.csv](outputs/scored_rule_rag_baseline.csv)

## Demo Questions

```text
Tôi quên uống thuốc huyết áp hôm qua, hôm nay uống gấp đôi được không?
Đang dùng warfarin thì có uống ibuprofen khi đau đầu được không?
Người nhà tôi uống nhầm nhiều viên thuốc ngủ, nên chờ xem có sao không?
em quen thuoc huyet ap hom qua, nay uong bu 2 vien dc k?
uống ks thấy đỡ rồi ngưng luôn được không?
Viên thuốc màu xanh của tôi uống mấy viên một ngày?
```

## Limitations

This project intentionally acknowledges its current limits:

- The dataset is demo-scale. Many rows come from seed augmentation and repetition.
- DPO preferences are taxonomy-designed examples, not expert-annotated clinical preference data.
- The RAG layer is toy retrieval using keyword matching over a few snippets.
- The evaluator is a heuristic proxy. It does not replace medical review, human evaluation, or proper NLG quality evaluation.
- The assistant must not be presented as a diagnosis, prescribing, or clinical decision system.

## Presentation Pitch

> Em chọn Medication Safety vì đây là một bài toán Medical LLM rất phù hợp với SFT và DPO. SFT giúp model học cách trả lời tiếng Việt theo format an toàn. DPO giúp model ưu tiên câu trả lời thận trọng hơn, tránh các lời khuyên nguy hiểm như tự uống bù liều, tự ngưng kháng sinh, hoặc dùng chung thuốc có nguy cơ tương tác.

> Điểm khó của tiếng Việt là người dùng không luôn hỏi bằng câu chuẩn: họ có thể không gõ dấu, dùng viết tắt như `ko`, `dc`, `ks`, `bs`, hoặc hỏi thay người thân. Vì vậy project thêm informal augmentation, safety taxonomy, RAG nhỏ và rubric evaluation.
