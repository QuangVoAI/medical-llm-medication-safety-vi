# Hướng Dẫn Thu Thập & Nạp Tài Liệu Y Tế

## 📊 Tình Hình Hiện Tại

### Knowledge Base Status
- **Trước**: 7 snippets (cơ bản)
- **Sau khi cập nhật**: 30+ snippets (tái thiết kế)
- **Thêm được**: ~8 tài liệu từ `medical_documents.json`
- **Tổng tiềm năng**: 40+ snippets

### Phạm Vi Bảo Phủ
- ✅ Tương tác thuốc-thuốc (drug-drug interactions)
- ✅ Tương tác thuốc-thực phẩm (drug-food interactions)
- ✅ Nhóm dân cư đặc biệt (people with kidney/liver disease, elderly)
- ✅ An toàn liều lượng (dosing safety)
- ✅ Hội chứng rút (withdrawal syndromes)
- ✅ Dị ứng (allergies/hypersensitivity)
- ✅ Kiểm soát bệnh mạn tính (chronic disease management)

---

## 🔧 Thêm Tài Liệu Mới

### Cách 1: Thông Qua `medical_documents.json` (Dễ Nhất)

```bash
# 1. Mở file
data/medical_documents.json

# 2. Thêm một object mới:
{
  "title": "Tên tài liệu tiếng Việt",
  "keywords": ["từ khóa 1", "tu khoa 1 khong dau", "từ khóa 2"],
  "content": "Nội dung cảnh báo (100-200 ký tự)",
  "action": "Hành động đề xuất rõ ràng",
  "source": "Nguồn tham khảo (VD: WHO Guidelines)",
  "category": "drug_interaction|special_population|safety|dosing|warning",
  "severity": "high|medium|low",
  "notes": "Ghi chú thêm (optional)"
}

# 3. Chạy công cụ quản lý
python scripts/manage_medical_docs.py validate
python scripts/manage_medical_docs.py list

# 4. Xuất sang format KnowledgeSnippet
python scripts/manage_medical_docs.py export
```

### Cách 2: Trực Tiếp Chỉnh Sửa `src/rag_knowledge.py`

```python
KNOWLEDGE_BASE = [
    # ... existing snippets ...
    KnowledgeSnippet(
        title="Tên tài liệu",
        keywords=("từ khóa 1", "từ khóa 2 không dấu", "tù khóa 3"),
        content="Cảnh báo chi tiết (100-200 ký tự)",
        action="Hành động: kiểm tra, báo với bác sĩ, etc.",
    ),
]
```

---

## 📚 Nguồn Tài Liệu Được Khuyến Khích

### Chuẩn Quốc Tế (Tiếng Anh/Dịch Tiếng Việt)

| Nguồn | Loại | Độ Tin Cậy | Link |
|---|---|---|---|
| WHO Drug Interactions Database | API/Database | 🟢 Cao | https://www.who.int/medicines |
| FDA Drug Interactions Database | Web | 🟢 Cao | https://www.fda.gov/drugs/information-consumers |
| UpToDate Clinical Pharmacology | Subscription | 🟢 Cao | https://www.uptodate.com |
| Therapeutic Guidelines | Web | 🟢 Cao | https://www.tg.org.au |
| PubMed/MEDLINE | Research Articles | 🟢 Cao | https://pubmed.ncbi.nlm.nih.gov |
| Drugs.com Interaction Checker | Web/API | 🟡 Trung | https://www.drugs.com/interaction |

### Nguồn Việt Nam (Ưu Tiên Cao)

| Tổ Chức | Tài Liệu | Trạng Thái |
|---|---|---|
| **Bộ Y Tế** | Hướng Dẫn Chẩn Đoán Điều Trị | [ ] Chưa thu thập |
| **Cục Dược** | Danh Mục Thuốc Được Phép | [ ] Chưa thu thập |
| **Bệnh Viện Lớn** (Việt Đức, Chợ Rẫy) | Case Studies, Guidelines | [ ] Chưa thu thập |
| **WHO Vietnam Office** | Localized Materials | [ ] Chưa thu thập |
| **Viện Y Học** | Nghiên Cứu | [ ] Chưa thu thập |

---

## 📋 Checklist Khi Thêm Tài Liệu

- [ ] Tiêu đề **ngắn, rõ ràng**, tiếng Việt
- [ ] Keywords **có cả dạng không dấu** (vì user input thường không dấu)
- [ ] Content **chính xác y tế**, không quá dài (< 200 ký tự)
- [ ] Action **cụ thể, có thể thực hiện** (VD: "kiểm tra X", "báo bác sĩ", v.v.)
- [ ] Source **tham khảo rõ** (VD: "WHO Guidelines", "FDA Database")
- [ ] Severity **chính xác** (high = nguy hiểm, medium = nên chú ý, low = lưu ý)
- [ ] **Test** bằng chạy app: `python app.py`

---

## 🧪 Test Knowledge Base Mới

```bash
# 1. Chạy validation
python scripts/manage_medical_docs.py validate

# 2. List tất cả tài liệu
python scripts/manage_medical_docs.py list

# 3. List theo danh mục
python scripts/manage_medical_docs.py list drug_interaction

# 4. Chạy app demo
python app.py

# 5. Test retrieval với hybrid_retriever
python -c "
from src.retrieval.hybrid_retriever import HybridRetriever
from src.retrieval.documents import load_default_documents
docs = load_default_documents()
print(f'Loaded {len(docs)} documents')
"
```

---

## 📈 Mục Tiêu Mở Rộng

**Phase 1 (HOÀN THÀNH)**: 30 snippets cơ bản
- Tương tác thuốc-thuốc: ✅ 10+
- Tương tác thuốc-thực phẩm: ✅ 5+
- Nhóm đặc biệt: ✅ 5+
- An toàn khác: ✅ 10+

**Phase 2 (TIẾP THEO)**: 40+ snippets từ medical_documents.json
- [ ] Thêm từ Bộ Y Tế Việt Nam
- [ ] Thêm từ WHO Guidelines
- [ ] Thêm từ cơ sở dữ liệu tương tác quốc tế

**Phase 3 (TƯƠNG LAI)**: 100+ snippets + vector embedding
- [ ] Full retrieval-augmented generation
- [ ] Semantic search với embedding
- [ ] Real-time updates từ pharmadb

---

## 🔗 Kết Nối với RAG

```python
# Lấy documents từ KNOWLEDGE_BASE
from src.retrieval.documents import load_default_documents
docs = load_default_documents()
# -> Mỗi KnowledgeSnippet -> RetrievalDocument

# Hybrid retrieval + ranking
from src.retrieval.hybrid_retriever import HybridRetriever
retriever = HybridRetriever(docs)
results = retriever.retrieve("warfarin và ibuprofen")
# -> Top 3 safety context snippets
```

---

## ✅ Hoàn Tất

- ✅ Mở rộng `src/rag_knowledge.py`: 7 → 30 snippets
- ✅ Tạo `docs/MEDICAL_SOURCES.md`: tham khảo nguồn
- ✅ Tạo `data/medical_documents.json`: quản lý tài liệu
- ✅ Tạo `scripts/manage_medical_docs.py`: CLI tool
- ✅ Hướng dẫn này

**Bước tiếp theo**: Thu thập tài liệu từ Bộ Y Tế Việt Nam hoặc WHO Vietnam
