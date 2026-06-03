# Dataset Strategy

Tai lieu nay chot chien luoc du lieu cho de tai:

```text
Vietnamese Medication Safety QA
```

Muc tieu la mo rong SFT va DPO theo huong co co so nghien cuu hon, van giu duoc tinh thuc te cua cau hoi tieng Viet doi thuong.

## 1. Strategic Goal

Repo hien tai da co mot loii du lieu dung task, nhung con 3 diem yeu:

- dataset SFT con mong;
- DPO con lap nhieu prompt va chua du kho;
- evaluation con nghieng ve demo-scale.

Vi vay chien luoc moi la:

1. giu dataset hien tai lam loi patient-facing;
2. mo rong SFT bang nguon Vietnamese medical QA va grounded synthetic QA;
3. mo rong DPO bang hard negatives va unsafe-but-fluent responses;
4. gan tat ca vao mot safety taxonomy ro rang;
5. dat bai toan trong boi canh benchmark tieng Viet va benchmark safety hien dai.

## 2. SFT Data Strategy

SFT se dung 3 tang du lieu.

### Tang 1: Core dataset hien tai

File:

```text
data/processed/medication_safety_vi_sft.jsonl
```

Vai tro:

- giu lam loi vi da dung task medication safety;
- da co giong patient-facing;
- da co cac bien the tieng Viet doi thuong nhu khong dau, viet tat, hoi ho nguoi than.

Tang nay la nen de giu ban sac de tai, khong de ViMedAQA hoac synthetic data lam troi giong user Viet thuc te.

### Tang 2: Broaden bang ViMedAQA

Chi lay cac mau co lien quan den medication safety, khong lay toan bo.

Bo loc uu tien:

- thuoc;
- tac dung phu;
- tuong tac thuoc;
- lieu dung / quen lieu / uong bu;
- doi tuong dac biet nhu mang thai, tre em, nguoi gia.

Ly do:

- ViMedAQA la Vietnamese medical QA rong;
- no rat tot de mo rong do phu y khoa tieng Viet;
- nhung neu dua vao toan bo thi task se bi troi sang medical QA tong quat, khong con sac net medication safety.

Nguyen tac dung:

- lay nhung mau sat voi thuoc va an toan thuoc;
- bo cac mau qua xa bai toan nhu chan doan tong quat khong lien quan thuoc;
- chuan hoa ve cung phong cach tra loi ngan gon, than trong, khong ke don.

### Tang 3: Grounded synthetic QA

Sinh them mau tu:

- Meddies;
- MedLens;
- to huong dan thuoc;
- tai lieu thuoc / guideline / patient leaflet.

Day la tang du lieu giup dataset "xin" hon augmentation thong thuong.

Khac voi paraphrase don thuan, grounded synthetic QA se di theo luong:

```text
document / snippet / fact
-> user-style Vietnamese question
-> patient-facing safe answer
```

Vi du:

```text
Knowledge: warfarin + ibuprofen co the tang nguy co chay mau.
Question: Dang uong warfarin thi dau dau uong ibuprofen duoc khong?
Answer: Khong nen tu y dung chung...
```

Y nghia:

- tang do phu tinh huong;
- tang factual grounding;
- de noi voi thay rang du lieu sinh them van bam nguon kien thuc, khong chi lap lai seed.

## 3. Taxonomy Chot Cho De Tai

Taxonomy nghien cuu duoc chot theo 6 nhom chinh va 1 nhom dem.

### Nhom chinh

- `drug_interaction`
- `missed_dose`
- `overdose`
- `antibiotics_adherence`
- `pregnancy_child_elderly`
- `insulin_safety`

### Nhom dem

- `general_medication_safety`

## 4. Mapping Taxonomy Moi Vao Schema Hien Tai

Trong repo hien tai, mot so label dang dat ten khac. De tranh vo script/train notebooks, tam thoi map nhu sau:

| Taxonomy nghien cuu | Label hien tai trong repo |
|---|---|
| `drug_interaction` | `drug_interaction` |
| `missed_dose` | `missed_dose` |
| `overdose` | `overdose` |
| `antibiotics_adherence` | `stop_medication` hoac `antibiotic_adherence` trong `topic` |
| `pregnancy_child_elderly` | `pregnancy_child_elderly` |
| `insulin_safety` | `diabetes_insulin` |
| `general_medication_safety` | `general_medication_safety` |

Huong dung:

- trong phan thuyet trinh, ban dung ten taxonomy moi cho ro nghia;
- trong code hien tai, ban co the giu alias cu de tranh vo pipeline;
- khi refactor script build dataset, co the doi ten label thong nhat sau.

## 5. Vai Tro Tung Nguon Du Lieu

### Core SFT dataset hien tai

Vai tro:

- patient-facing Vietnamese style;
- medication safety scenarios da dung task;
- backbone de giu consistency cua assistant.

### ViMedAQA

Vai tro:

- mo rong Vietnamese medical QA coverage;
- them nhieu cach hoi va tra loi y khoa tu nhien hon;
- bo sung vocabulary va cau truc medical Vietnamese.

Han che:

- la medical QA rong;
- khong phai tat ca deu la medication safety;
- can loc rat ky truoc khi dua vao train.

### Meddies QA

Vai tro:

- nguon mo tieng Viet lien quan duoc hoc;
- phu hop cho SFT vi co dang QA;
- huu ich de tao them grounded synthetic QA.

Han che:

- mot so answer technical hoac dai;
- can clean `<think>...</think>` va rut gon theo patient-facing style.

### MedLens

Vai tro:

- phu hop de xay case tuong tac thuoc va adverse signal;
- rat huu ich cho `drug_interaction`.

Han che:

- du lieu goc khong phai patient-facing Vietnamese;
- phai viet lai thanh cautionary Vietnamese QA;
- phai luon kem caveat vi signal khong dong nghia nhan qua.

### To huong dan thuoc / guideline

Vai tro:

- tao grounded synthetic QA co do tin cay narrative tot hon;
- giup answer khong qua chung chung.

Han che:

- can chon loc nguon de hoc;
- khong bien project thanh he thong guideline-chatbot rong.

## 6. DPO Strategy

DPO la noi project cua ban bat dau co "chat rieng".

Khong nen chi tao:

- `chosen` dung;
- `rejected` sai lo lieu.

Thay vao do, DPO phai tap trung vao 3 loai pair.

### Hard negatives

Rejected answer nghe hop ly, nhung thieu canh bao hoac thieu escalation.

Vi du:

- nghe lich su;
- nghe tron tria;
- nhung bo qua nguy co qua lieu, tuong tac, hay doi lieu.

### Unsafe-but-fluent responses

Day la cac cau:

- rat troi chay;
- co ve huu ich;
- nhung dua ra advice nguy hiem.

Vi du:

- goi y tu uong bu lieu;
- cho phep ngung khang sinh som;
- tri hoan cap cuu trong overdose;
- khang dinh dung chung thuoc la an toan khi chua du du kien.

### Taxonomy-based errors

Day la cach tao rejected co he thong theo tung nhom nguy co:

- tu doi lieu;
- tri hoan cap cuu;
- dung thuoc khi mang thai/tre em ma khong canh bao;
- ngung khang sinh som;
- bo qua tuong tac thuoc;
- xu tri insulin khi bo bua mot cach tuy tien.

Tat ca DPO pairs deu phai chuyen hoa thanh:

- tieng Viet;
- hoi dap doi thuong;
- patient-facing style;
- phu hop van phong cua nguoi Viet hoi that.

## 7. Evaluation Strategy

Evaluation duoc chia thanh 2 tang de vua dung bai, vua co chieu sau hoc thuat.

### Tang benchmark tieng Viet

Dung `VM14K` de noi ve boi canh benchmark y khoa tieng Viet.

Vai tro:

- dat project vao he sinh thai Vietnamese medical NLP;
- cho thay bai toan cua ban khong phai dung mot minh;
- ho tro phan Task 2 overview benchmark.

### Tang benchmark safety thuc te

Dung:

- `HealthBench`
- `MedSafetyBench`
- `RxSafeBench`

de noi ve evaluation hien dai cho medical LLM.

Thong diep can nhan manh:

- factuality chua du;
- can safety;
- can uncertainty;
- can escalation;
- can clinical usefulness.

Cau noi de dua vao slide:

> VM14K giup nhin tu goc do benchmark y khoa tieng Viet, con HealthBench, MedSafetyBench va RxSafeBench cho thay danh gia Medical LLM hien dai phai di xa hon accuracy, bao gom ca safety, uncertainty va clinical usefulness.

## 8. Vi Sao Plan Nay Manh

Plan nay giai quyet truc tiep 3 diem yeu cua repo hien tai:

- dataset con mong;
- DPO con lap nhieu;
- evaluation con nghieng ve demo-scale.

Tac dung mong doi:

- SFT rong hon ve coverage;
- DPO sau hon ve alignment;
- benchmark narrative chac hon khi trinh bay voi thay;
- project co cau truc nghien cuu ro hon, khong chi la notebook demo.

## 9. Cau Chot De Tai

Ban co the dung nguyen cau nay:

> Em xay dung mot Vietnamese Medical LLM cho bai toan Medication Safety QA, trong do SFT duoc mo rong bang du lieu loi hien tai, ViMedAQA va grounded synthetic QA; DPO duoc thiet ke tu hard negative va unsafe-but-fluent responses dua tren y tuong tu MedSafetyBench va RxSafeBench; phan danh gia dat trong boi canh benchmark tieng Viet va benchmark safety hien dai nhu VM14K va HealthBench.

## 10. Dieu Can Noi Ro Trong Slide

Dataset nay van la du lieu hoc thuat:

- khong dung de deploy lam sang;
- khong thay the bac si hoac duoc si;
- chua phai expert-annotated clinical dataset;
- duoc thiet ke de nghien cuu fine-tuning, alignment va safety evaluation.

Khi trinh bay, nen noi that:

> Muc tieu cua em khong phai claim da xay dung duoc mot medical assistant dung lam sang, ma la xay dung mot pipeline nghien cuu co cau truc cho Vietnamese Medication Safety QA, trong do data, alignment va evaluation duoc thiet ke nham giam advice nguy hiem.
