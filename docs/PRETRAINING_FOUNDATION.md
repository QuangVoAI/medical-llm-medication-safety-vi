# Pretraining Foundation: From CPT To SFT/DPO

Tài liệu này dùng cho bài tập trước: tự thực hiện pretraining LLM với Qwen 0.5B hoặc mô hình nhỏ, sau đó phát triển lên bài Medical LLM hiện tại.

## Ý Tưởng Chính

Với tài nguyên sinh viên/Colab, không nên nói là pretrain một LLM lớn từ đầu. Cách hợp lý hơn:

> Continued Pretraining hoặc Domain-Adaptive Pretraining: lấy một base model nhỏ như `Qwen/Qwen2.5-0.5B`, rồi tiếp tục train next-token prediction trên corpus y khoa/thuốc tiếng Việt.

Sau đó nối lên bài hiện tại:

```text
Qwen 0.5B base
  -> Continued pretraining trên raw medical text tiếng Việt
  -> SFT trên medication-safety QA
  -> DPO trên chosen/rejected safety pairs
  -> Evaluation Base / CPT / SFT / DPO
```

## 1. Data Như Thế Nào?

Pretraining dùng **raw text**, không cần format hỏi-đáp.

Format khuyên dùng: JSONL, mỗi dòng có một field `text`.

```json
{"text": "Paracetamol là thuốc giảm đau hạ sốt. Không nên dùng quá liều vì có nguy cơ gây độc gan."}
{"text": "Khi quên một liều thuốc, người bệnh không nên tự ý uống gấp đôi liều nếu chưa có hướng dẫn."}
{"text": "Warfarin dùng chung với một số thuốc giảm đau NSAID có thể làm tăng nguy cơ chảy máu."}
```

Khác nhau giữa các giai đoạn:

| Giai đoạn | Data format | Model học gì |
|---|---|---|
| Continued pretraining | raw text: `{"text": "..."}` | học phân bố ngôn ngữ và domain y khoa/thuốc |
| SFT | chat/instruction: user -> assistant | học cách trả lời câu hỏi |
| DPO | prompt + chosen + rejected | học ưu tiên câu trả lời an toàn hơn |

## 2. Loss, Learning Rate, Batch Size

Task pretraining là **causal language modeling**:

```text
Input tokens:  x1, x2, x3, ..., xn
Target tokens: x2, x3, x4, ..., x(n+1)
Loss: cross entropy next-token prediction
```

Thông số khuyên dùng để debug:

| Tham số | Debug | Train nhỏ ổn định |
|---|---:|---:|
| Model | `Qwen/Qwen2.5-0.5B` | `Qwen/Qwen2.5-0.5B` |
| block size | 256 | 512 |
| batch size | 1 | 1-2 |
| gradient accumulation | 4 | 8 |
| learning rate | `5e-5` | `2e-5` đến `5e-5` |
| max steps | 20 | 200-1000 |
| epoch | dùng `max_steps` | 1-3 |

Vì đây là continued pretraining trên model đã biết ngôn ngữ, learning rate nên nhỏ hơn SFT. Nếu LR quá lớn, model dễ quên kiến thức cũ hoặc loss dao động mạnh.

## 3. Khi Training Thì Xem Sự Thay Đổi Như Thế Nào?

Nên quan sát 4 thứ:

1. **Training loss**
   - loss giảm nghĩa là model dự đoán token tiếp theo trên corpus tốt hơn;
   - loss dao động là bình thường nếu batch nhỏ;
   - loss giảm quá nhanh trên corpus rất nhỏ có thể là overfit.

2. **Perplexity**
   - `perplexity = exp(eval_loss)`;
   - perplexity thấp hơn nghĩa là model bớt “ngạc nhiên” với văn bản domain.

3. **Generation before/after**
   - prompt cùng một câu trước và sau CPT;
   - xem model có dùng thuật ngữ y khoa/thuốc tự nhiên hơn không.

4. **Downstream readiness**
   - CPT không dạy model trả lời QA tốt ngay;
   - CPT chỉ làm model quen domain hơn;
   - SFT/DPO mới dạy format trả lời và hành vi safety.

## 4. Cách Nói Khi Trình Bày

Nếu thầy hỏi “em pretrain gì?”:

> Em thực hiện continued pretraining cho Qwen 0.5B trên corpus raw text về medication safety tiếng Việt. Objective là next-token prediction, loss là cross entropy. Mục tiêu không phải tạo LLM từ đầu, mà làm model quen hơn với ngôn ngữ và thuật ngữ domain trước khi SFT/DPO.

Nếu hỏi “vì sao không pretrain từ đầu?”:

> Pretrain từ random initialization cần dữ liệu và compute rất lớn. Với bài lab, em chọn cách realistic hơn là continued pretraining trên model nhỏ, để vẫn quan sát được data format, loss, learning rate và sự thay đổi của model.

Nếu hỏi “CPT khác SFT thế nào?”:

> CPT học từ raw text để cải thiện phân bố ngôn ngữ/domain. SFT học từ instruction-response để model biết trả lời câu hỏi. DPO học từ preference để model chọn câu trả lời an toàn hơn.

## 5. Kết Luận Nối Sang Bài Hiện Tại

Pretraining là tầng nền:

```text
Pretraining/CPT: học domain language
SFT: học trả lời theo format
DPO: học preference safety
Evaluation: kiểm tra hành vi trên câu hỏi nguy hiểm
```

Vì vậy bài pretraining trước có thể trở thành slide mở rộng cho bài Medical LLM hiện tại.
