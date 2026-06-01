# Nguồn Tài Liệu Y Tế Chuẩn Việt Nam

Tài liệu này liệt kê các nguồn và tham khảo cho knowledge base của RAG medication safety.

## Các Hướng Dẫn Được Áp Dụng

### 1. Tương Tác Thuốc Cơ Bản

| Tương tác | Nguồn Tham Khảo | Mức Độ Nghiêm Trọng | Ghi Chú |
|---|---|---|---|
| Warfarin + NSAID | WHO/FDA Drug Interactions Database | Cao | Tăng nguy cơ chảy máu |
| Metformin + Rượu | Clinical Pharmacology Guidelines | Cao | Nguy cơ toan lactic |
| Tetracycline + Sữa/Canxi | USP/WHO Guidelines | Trung bình | Giảm hấp thu thuốc |
| Warfarin + Vitamin K | INR Monitoring Standards | Cao | Cần giám sát ổn định |
| Paracetamol + Rượu | Hepatotoxicity Guidelines | Cao | Độc gan tích lũy |
| MAOI + Tyramine | Hypertensive Crisis Prevention | Cao | Tăng huyết áp đột ngột |

### 2. Nhóm Đặc Biệt (Vulnerable Populations)

**Người Cao Tuổi (Beers Criteria)**
- Benzodiazepine: tăng nguy cơ rơi ngã, lú lẫn
- Thuốc chống cholinergic: lú lẫn, mất trí nhớ
- Tham khảo: American Geriatrics Society Beers Criteria

**Bệnh Nhân Suy Thận**
- Cần kiểm tra clearance creatinine
- Liều phải điều chỉnh theo eGFR
- Tham khảo: Kidney Disease: Improving Global Outcomes (KDIGO)

**Bệnh Nhân Suy Gan**
- Giảm khả năng chuyển hóa
- Tránh hepatotoxic drugs
- Tham khảo: Child-Pugh Classification

### 3. An Toàn Thuốc Thường Dùng

| Thuốc | Cảnh Báo Chính | Giám Sát | Điều Chỉnh |
|---|---|---|---|
| Heparin | Chảy máu | aPTT định kỳ | Titrate theo INR/aPTT |
| Lithium | Độc tính | Li+ máu (trough) | Cân bằng nước, natri |
| Corticosteroid | Loãng xương, tăng đường | Glucose, BMD | Dùng liều thấp nhất |
| Methotrexate | Độc tính tủy xương | CBC, LFT, RFT | Dừng nếu có dấu hiệu |
| Levothyroxine | Hấp thu | TSH mỗi 6-8 tuần | Cách xa sữa, iron |

### 4. Dị Ứng và Phản Ứng

**Phản Ứng Loại I (Cấp Tính)**
- Sốc phản vệ, sưng mặt, ngạt thở
- Cần epinephrine sẵn sàng
- Tham khảo: IgE-mediated Hypersensitivity

**Dị Ứng Penicillin/Cephalosporin**
- Khoảng 1-2% dị ứng chéo
- Yêu cầu test skin hoặc RAST nếu tiền sử
- Tham khảo: Beta-lactam Allergy Cross-reactivity

### 5. Hội Chứng Rút (Withdrawal Syndromes)

| Thuốc | Triệu Chứng | Giảm Liều |
|---|---|---|
| SSRI/Antidepressant | Chóng mặt, tê tay chân | Giảm 10% mỗi 1-2 tuần |
| Benzodiazepine | Lo lắng, co giật | Giảm 10% mỗi 1 tuần |
| Beta-blocker | Tachycardia, angina | Giảm 10-25% mỗi tuần |

## Tài Liệu Được Sử Dụng

### Chuẩn Quốc Tế
- WHO Model Formulary
- FDA Drug Interactions Database
- Therapeutic Guidelines (Australia)
- UpToDate Clinical Decision Support

### Hướng Dẫn Châu Á-Thái Bình Dương
- ASEAN Guidelines on Rational Drug Use
- Singapore's Medication Safety Guidelines
- Thai Pharmaceutical Standards

### Tiêu Chuẩn Việt Nam
- Hướng dẫn từ Bộ Y Tế Việt Nam
- Danh mục thuốc được phép sử dụng tại Việt Nam
- Tiêu chuẩn Dược sĩ Việt Nam

## Cấu Trúc Thêm Mới

### Để Thêm Một Knowledge Snippet Mới:

```python
KnowledgeSnippet(
    title="<Tiêu đề tiếng Việt>",
    keywords=("<từ khóa 1>", "<từ khóa 2 không dấu>", ...),
    content="<Nội dung cảnh báo>",
    action="<Hành động được đề xuất>",
)
```

**Yêu Cầu:**
1. Từ khóa phải bao gồm cả dạng không dấu để match text noisy
2. Content phải ngắn gọn (~100 ký tự)
3. Action phải cụ thể và có thể thực hiện được
4. Phải tham khảo nguồn y tế đáng tin cậy

### Nguồn Mới Được Ưu Tiên:
- [ ] Bộ Y Tế Việt Nam - Hướng dẫn chẩn đoán điều trị
- [ ] WHO Vietnam - Medication safety toolkit
- [ ] Danh sách thuốc tương tác từ cơ sở dữ liệu quốc tế
- [ ] Công bố y tế từ Viện Y Học Điều Dưỡng
- [ ] Case studies từ các Bệnh viện hàng đầu Việt Nam

## Ghi Chú Về Độ Chính Xác

- Tất cả các cảnh báo được lấy từ hướng dẫn y tế được công nhận
- **Demo-scale dataset**: Các snippet này được thiết kế cho demo, không phải thay thế tư vấn y tế chuyên môn
- Cập nhật: Cần review định kỳ với chuyên gia dược học Việt Nam
- **Disclaimer**: Hệ thống này là công cụ giáo dục, không phải chẩn đoán hoặc điều trị

---
*Cập nhật lần cuối: 2026-06-02*
