# Dataset Strategy

## Vì sao chọn các dataset này?

Medication Safety Assistant cần hai loại dữ liệu:

1. Dữ liệu tiếng Việt để model học cách hỏi đáp y khoa bằng ngôn ngữ của người Việt.
2. Dữ liệu liên quan thuốc/tương tác thuốc để bài toán không bị quá chung chung.

Vì vậy dataset được chốt là:

- **Meddies QA**: nguồn chính cho SFT tiếng Việt.
- **MedLens**: nguồn bổ sung cho tương tác thuốc.
- **Seed safety data**: tự viết để bảo đảm có tình huống đúng trọng tâm người Việt.

## Vai trò từng nguồn

### Meddies QA

Sử dụng config `qa_pharmaceuticals`.

Vai trò:

- cung cấp QA tiếng Việt về dược học;
- giúp model quen với thuật ngữ thuốc tiếng Việt;
- dùng cho SFT.

Hạn chế:

- nhiều câu hỏi khá kỹ thuật;
- một số câu trả lời có phần suy luận dài;
- cần lọc/clean `<think>...</think>`.

### MedLens

Vai trò:

- cung cấp dữ liệu interaction/adverse-event signal;
- dùng để tạo câu hỏi tiếng Việt dạng "Tôi đang dùng A, B, C. Có nguy cơ tương tác không?"

Hạn chế:

- dữ liệu gốc tiếng Anh;
- dựa trên tín hiệu báo cáo bất lợi, không khẳng định nhân quả;
- vì vậy câu trả lời phải luôn có caveat.

### Seed Vietnamese Safety Data

Vai trò:

- bao phủ các tình huống thực tế ở Việt Nam:
  - quên liều thuốc huyết áp;
  - tự ngưng kháng sinh;
  - paracetamol và rượu;
  - warfarin và ibuprofen;
  - insulin khi bỏ bữa;
  - phụ nữ mang thai tự mua thuốc;
  - trẻ em dùng thuốc người lớn;
  - quá liều thuốc ngủ.

Đây là phần quan trọng nhất để DPO có tín hiệu safety rõ.

## Format SFT

Mỗi dòng JSONL:

```json
{
  "question": "...",
  "answer": "...",
  "topic": "...",
  "source": "...",
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

## Format DPO

Mỗi dòng JSONL:

```json
{
  "prompt": "...",
  "chosen": "...",
  "rejected": "...",
  "topic": "..."
}
```

## Điều cần nói rõ trong slide

Dataset này là demo học thuật:

- không dùng để deploy lâm sàng;
- chưa có bác sĩ/dược sĩ kiểm định toàn bộ;
- dùng để minh họa SFT/DPO và evaluation safety;
- mọi output cần được xem là thông tin giáo dục, không thay thế tư vấn y tế.
