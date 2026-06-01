# Tích Hợp Vector Embeddings & Semantic Search

## 📚 Tổng Quan

Hệ thống RAG medication safety của bạn giờ đã có 3 lớp tinh chỉnh:

### Layer 1: Keyword Search (BM25)
- Tìm kiếm dựa trên từ khóa
- Nhanh, không cần GPU
- Tốt cho truy vấn có từ khóa cụ thể

### Layer 2: Semantic Search (Vector Embeddings)
- Tìm kiếm dựa trên ý nghĩa
- Dùng multilingual embeddings (hỗ trợ tiếng Việt)
- Tốt cho truy vấn không chính xác, paraphrased
- Cache embeddings để tính toán nhanh

### Layer 3: Reranking
- Kết hợp kết quả BM25 + semantic
- Sắp xếp lại dựa trên safety category
- Trả về top-3 kết quả an toàn nhất

---

## 🚀 Cài Đặt Vector Embeddings

### 1. Cài đặt Dependencies

```bash
pip install -r requirements.txt
# hoặc nếu chỉ muốn embeddings
pip install sentence-transformers numpy
```

**Model được dùng**: `sentence-transformers/paraphrase-multilingual-minilm-l12-v2`
- Hỗ trợ 100+ ngôn ngữ, bao gồm tiếng Việt
- Nhẹ: 420MB
- Nhanh: ~100ms per query

### 2. Xây Dựng Extended Knowledge Base

```bash
python scripts/build_medical_knowledge.py export
```

Output:
- `src/rag_knowledge_extended.py` - 59 medical snippets (30 base + 29 mở rộng)

### 3. Build Embeddings Cache

```python
from src.retrieval.documents import load_default_documents
from src.retrieval.vector_store import VectorRetriever
from pathlib import Path

docs = load_default_documents()
retriever = VectorRetriever(
    docs,
    use_sentence_transformers=True,
    cache_path=Path(".embeddings_cache.json")
)
# Cache sẽ được lưu tự động
```

---

## 📖 Sử Dụng Hybrid Retriever

### Ví dụ 1: Tìm kiếm Đơn Giản

```python
from src.retrieval.hybrid_retriever import HybridRetriever
from src.safety_taxonomy import SafetyCategory

retriever = HybridRetriever(
    use_sentence_transformers=True,  # Enable embeddings
)

# Tìm kiếm medication safety
results = retriever.search(
    query="warfarin và ibuprofen có được uống cùng không?",
    category=SafetyCategory.DRUG_INTERACTION,
    top_k=3
)

for doc, score, source in results:
    print(f"[{source}] {doc.title}: {score:.3f}")
    print(f"  {doc.text[:100]}...")
```

### Ví dụ 2: So Sánh BM25 vs Semantic

```python
from src.retrieval.bm25 import BM25Retriever
from src.retrieval.vector_store import VectorRetriever
from src.retrieval.documents import load_default_documents

docs = load_default_documents()

# BM25 keyword search
bm25 = BM25Retriever(docs)
bm25_results = bm25.search("insulin", top_k=3)
print("BM25 Results:")
for doc, score in bm25_results:
    print(f"  {doc.title}: {score:.3f}")

# Semantic search
vector = VectorRetriever(docs, use_sentence_transformers=True)
semantic_results = vector.search("insulin", top_k=3)
print("\nSemantic Results:")
for doc, score in semantic_results:
    print(f"  {doc.title}: {score:.3f}")
```

---

## 📊 Thống Kê Knowledge Base

### Hardcoded Snippets (30)
- Tương tác thuốc-thuốc: 10+
- Tương tác thuốc-thực phẩm: 5+
- Nhóm đặc biệt: 5+
- An toàn khác: 10+

### Medical Documents (29)
- Từ Bộ Y Tế Việt Nam: 5
- Từ Cơ sở dữ liệu quốc tế: 24

### Tổng: 59 Snippets
- 291 từ khóa
- Hỗ trợ tiếng Việt (với/không dấu)

---

## 🔍 Kiểm Tra Embeddings Cache

```bash
# Xem cache stats
ls -lh .embeddings_cache.json

# Xóa cache để rebuild
rm .embeddings_cache.json
```

Cache sẽ được tự động rebuild lần đầu tiên chương trình chạy.

---

## ⚡ Tuning Performance

### 1. Nếu Slow - Giảm Model Size

```python
from src.retrieval.vector_store import VectorRetriever

# Dùng model nhẹ hơn
retriever = VectorRetriever(
    docs,
    model_name="sentence-transformers/multilingual-MiniLM-L6-v2",
    use_sentence_transformers=True
)
```

### 2. Nếu Memory Tight - Disable Embeddings

```python
retriever = VectorRetriever(
    docs,
    use_sentence_transformers=False  # Falls back to token-based similarity
)
```

### 3. Nếu Cần Precision - Tăng top_k

```python
results = retriever.search(
    query="...",
    category=...,
    top_k=5  # Tăng từ 3 lên 5
)
```

---

## 🧪 Test Script

```python
#!/usr/bin/env python3
from src.retrieval.hybrid_retriever import HybridRetriever
from src.safety_taxonomy import SafetyCategory

retriever = HybridRetriever(use_sentence_transformers=True)

test_queries = [
    ("warfarin và ibuprofen", SafetyCategory.DRUG_INTERACTION),
    ("quên liều thuốc", SafetyCategory.MISSED_DOSE),
    ("insulin và bỏ bữa", SafetyCategory.HYPOGLYCEMIA),
    ("người cao tuổi", SafetyCategory.SPECIAL_POPULATION),
]

for query, category in test_queries:
    print(f"\n🔍 Query: {query}")
    results = retriever.search(query, category, top_k=2)
    for doc, score, source in results:
        print(f"  [{source:15}] {doc.title}: {score:.3f}")
```

---

## 📈 Kế Hoạch Phát Triển

### Phase 1 ✅
- [x] 30 hardcoded snippets
- [x] 29 medical documents (Bộ Y Tế + quốc tế)
- [x] BM25 keyword search
- [x] Vector embeddings (multilingual)
- [x] Hybrid retriever

### Phase 2 (Tiếp Theo)
- [ ] Tinh chỉnh embedding model cho tiếng Việt
- [ ] Thêm clinical guidelines từ các bệnh viện
- [ ] API integration với external drug databases
- [ ] Real-time updates

### Phase 3 (Tương Lai)
- [ ] Dense passage retrieval (DPR)
- [ ] Cross-encoder reranker
- [ ] Multimodal embeddings (text + images)
- [ ] Đánh giá chất lượng semantic search

---

## 🔗 Integration với Existing Code

### Trong app.py

```python
from src.retrieval.hybrid_retriever import HybridRetriever
from src.agent.medication_agent import MedicationAgent

# Tạo retriever với semantic search
retriever = HybridRetriever(use_sentence_transformers=True)

# Dùng trong agent
agent = MedicationAgent(retriever=retriever)
response = agent.run(user_question)
```

### Trong Agent

```python
class MedicationAgent:
    def __init__(self, retriever):
        self.retriever = retriever
    
    def retrieve_context(self, query, category):
        # Returns top-3 kết quả từ hybrid search
        return self.retriever.search(
            query=query,
            category=category,
            top_k=3
        )
```

---

## ❓ FAQ

**Q: Embeddings cache không được update?**
A: Xóa `.embeddings_cache.json` và chạy lại. Cache sẽ rebuild automatically.

**Q: Tìm kiếm quá chậm?**
A: Dùng model nhẹ hơn hoặc disable `use_sentence_transformers=False`.

**Q: Muốn thêm tài liệu y tế mới?**
A: Thêm vào `data/medical_documents.json` rồi chạy:
```bash
python scripts/build_medical_knowledge.py export
rm .embeddings_cache.json
```

**Q: Hỗ trợ các ngôn ngữ khác không?**
A: Model `multilingual-MiniLM-L12-v2` hỗ trợ 100+ ngôn ngữ.

---

**Cập nhật**: 2026-06-02
**Status**: ✅ Production Ready for Demo
