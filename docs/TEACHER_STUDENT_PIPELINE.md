# Teacher-Student Pipeline

Tai lieu nay chot huong nang cap "xin" cho project:

```text
medical teacher models
-> sinh va ra soat du lieu
-> Qwen student model duoc fine-tune de tra loi tieng Viet
```

## 1. Student Model

Student model la model ban train that va demo cuoi cung.

Khuyen nghi:

- uu tien: `Qwen/Qwen2.5-7B-Instruct`

Ly do:

- multilingual, co ho tro Vietnamese tot;
- thuc te de fine-tune bang QLoRA;
- phu hop bai toan patient-facing Vietnamese medication safety.

## 2. Teacher Model

Teacher model khong phai model deploy cuoi.

Teacher dung de:

- tao grounded synthetic QA;
- tao chosen answers tot hon cho DPO;
- tao rejected answers kieu unsafe-but-fluent;
- goi y rubric va error taxonomy.

Ung vien teacher:

- MedGemma
- Meditron
- hoac bat ky medical LLM manh nao ban truy cap duoc

## 3. Teacher Lam Gi Cho SFT

Teacher nhan:

- snippet tu Meddies / MedLens / leaflets / guideline
- taxonomy category
- yeu cau patient-facing Vietnamese style

Teacher sinh:

- 1-3 cau hoi nguoi dung
- 1 cau tra loi an toan
- bien the informal / khong dau neu can

Schema dua vao:

```text
data/generated/teacher_grounded_sft.jsonl
```

## 4. Teacher Lam Gi Cho DPO

Teacher sinh preference pairs:

- `chosen`: an toan, co caveat, co escalation
- `rejected`: tron tria, nghe hop ly, nhung nguy hiem

Schema dua vao:

```text
data/generated/teacher_generated_dpo.jsonl
```

## 5. ViMedAQA Nam O Dau

ViMedAQA khong dua thang vao train toan bo.

No di theo luong:

```text
ViMedAQA raw
-> loc theo medication safety scope
-> rewrite ve patient-facing style neu can
-> data/generated/vimedaqa_filtered_sft.jsonl
```

## 6. Build Train Set Cuoi

Script:

```text
scripts/build_medication_safety_datasets.py
```

Se tu dong gop:

- core SFT dataset
- Meddies
- MedLens
- `data/generated/vimedaqa_filtered_sft.jsonl`
- `data/generated/teacher_grounded_sft.jsonl`
- seed DPO
- `data/generated/teacher_generated_dpo.jsonl`

## 7. Thu Tu Lam Viec De Nhat

1. Chay:

```bash
python scripts/prepare_teacher_student_workspace.py
```

2. Dat du lieu da loc/generate vao:

- `data/generated/vimedaqa_filtered_sft.jsonl`
- `data/generated/teacher_grounded_sft.jsonl`
- `data/generated/teacher_generated_dpo.jsonl`

3. Rebuild dataset train:

```bash
python scripts/build_medication_safety_datasets.py
```

4. Mo notebook chinh tren Kaggle:

```text
notebooks/medical-llm-medication-safety-vi-v2_1.ipynb
```

5. Train theo config trong `configs/`

## 8. Triet Ly Cua Pipeline

Y tuong trung tam:

> medical teacher giup nang chat du lieu va preference pairs, con Qwen student giu duoc su thuc te khi fine-tune cho tieng Viet.

Nhu vay project cua ban:

- co chat nghien cuu hon;
- van train duoc tren tai nguyen sinh vien;
- va co mot cau chuyen rat dep de bao cao voi thay.
