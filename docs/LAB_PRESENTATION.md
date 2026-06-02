# Lab Presentation Guide

## Thông điệp chính

Đề tài nên được trình bày theo trục:

> Medical LLM for Vietnamese Medication Safety QA: Continued pretraining -> SFT -> DPO để trả lời câu hỏi dùng thuốc an toàn hơn.

RAG không phải trọng tâm bài này. Nếu nhắc đến, chỉ đặt ở backup slide hoặc future work.

## Slide Flow Đề Xuất

1. **Motivation**
   - Medical LLM không chỉ cần nói trôi chảy, mà cần đúng, thận trọng và an toàn.
   - Medication safety phù hợp với người Việt vì câu hỏi thường không dấu, viết tắt, thiếu ngữ cảnh.

2. **Task Definition**
   - Input: câu hỏi tiếng Việt về dùng thuốc.
   - Output: câu trả lời an toàn, không kê đơn, không tự đổi liều, biết khuyên hỏi bác sĩ/dược sĩ/cấp cứu.

3. **Medical LLM Overview**
   - Medical LLM là LLM được huấn luyện hoặc fine-tune trên dữ liệu y khoa.
   - Use cases: medical QA, clinical note summarization, guideline QA, patient communication.
   - Chi tiết để đưa vào slide: `docs/MEDICAL_LLM_OVERVIEW_BENCHMARKS.md`.

4. **Benchmarks**
   - MedQA, MedMCQA, PubMedQA, MMLU Medical.
   - MultiMedQA cho Med-PaLM.
   - HealthBench/MedHELM nhấn mạnh safety, usefulness, hội thoại thực tế.

5. **Dataset**
   - CPT/pretraining: raw text format `{"text": "..."}`.
   - SFT: 500 rows.
   - DPO: 400 preference pairs.
   - Nguồn: Meddies QA, MedLens, seed safety tiếng Việt, informal augmentation.
   - Nói rõ: demo-scale, nhiều row là augmentation/repetition, chưa phải production dataset.

6. **Pretraining Foundation**
   - Dùng `Qwen/Qwen2.5-0.5B`.
   - Làm continued pretraining/domain-adaptive pretraining, không phải pretrain từ random init.
   - Objective: causal language modeling, next-token prediction.
   - Theo dõi: training loss, eval loss, perplexity, generation before/after.
   - Chi tiết: `docs/PRETRAINING_FOUNDATION.md` và `notebooks/qwen_0_5b_medical_cpt_demo.ipynb`.

7. **Model And Training**
   - Base: `Qwen/Qwen2.5-1.5B-Instruct`.
   - Fallback: `Qwen/Qwen2.5-0.5B-Instruct`.
   - Method: QLoRA/LoRA.
   - SFT: học format trả lời an toàn bằng tiếng Việt.
   - DPO: học ưu tiên câu trả lời an toàn hơn câu trả lời nguy hiểm.

8. **SFT Result**
   - Show loss debug hoặc full training loss.
   - Show 2-3 outputs sau SFT.
   - Nói thẳng lỗi: SFT có thể nói đúng format nhưng vẫn hallucinate medical facts.

9. **DPO Result**
   - Show chosen/rejected pair.
   - So sánh SFT vs DPO ở các case nguy hiểm:
     - quên liều huyết áp;
     - warfarin + ibuprofen;
     - tự ngưng kháng sinh;
     - uống nhầm thuốc ngủ.

10. **Evaluation**
   - Qualitative comparison: Base / SFT / SFT + DPO.
   - Manual safety rubric 0-3.
   - Heuristic evaluator chỉ là proxy, không thay thế chuyên gia y tế.

11. **Conclusion**
    - CPT giúp model quen ngôn ngữ/domain.
    - SFT giúp model học cách trả lời theo format.
    - DPO quan trọng để alignment theo safety.
    - Medical LLM khó vì factuality, uncertainty, safety và domain knowledge.

## Câu Trả Lời Khi Bị Hỏi

**Tại sao không tập trung RAG?**

> Vì yêu cầu bài tập là SFT, DPO và overview Medical LLM/benchmark. Em có để RAG như hướng mở rộng để giảm hallucination bằng tài liệu thuốc có kiểm chứng, nhưng phần trình bày chính của em là fine-tuning và alignment.

**Tại sao dùng Qwen mà không dùng model y tế mạnh?**

> Vì mục tiêu là thực nghiệm SFT/DPO trên GPU vừa sức như Kaggle/Colab. Các model y tế mạnh thường lớn, không tối ưu tiếng Việt, hoặc khó fine-tune trong tài nguyên lab. Em dùng Qwen nhỏ để chứng minh pipeline, còn hướng nâng cấp là dùng medical teacher model hoặc model lớn hơn để distill/generate preference data.

**SFT và DPO khác nhau thế nào?**

> SFT dạy model bắt chước câu trả lời mẫu. DPO dạy model thích câu trả lời tốt hơn theo preference. Trong medical domain, DPO quan trọng vì câu trả lời không chỉ cần đúng format mà còn phải an toàn, thận trọng và biết giới hạn.

**CPT/pretraining khác SFT thế nào?**

> CPT học từ raw text bằng next-token prediction để model quen ngôn ngữ và thuật ngữ domain. SFT học từ cặp user-assistant để model biết trả lời câu hỏi theo format mong muốn.

**Benchmark medical LLM có vấn đề gì?**

> MedQA, MedMCQA, PubMedQA đo kiến thức tốt nhưng phần lớn là trắc nghiệm. Hội thoại y tế thật còn cần safety, uncertainty, multi-turn behavior và usefulness, nên các benchmark mới như HealthBench/MedHELM quan trọng hơn cho medical assistant.

## Không Nên Nói Quá

- Không nói model dùng được trong lâm sàng.
- Không nói dataset đã đủ lớn.
- Không nói evaluator là đánh giá y khoa thật.
- Không nói RAG là đóng góp chính của bài này.
- Không nói SFT/DPO đã giải quyết hoàn toàn hallucination.

## Một Câu Pitch Ngắn

> Em chọn Medical LLM vì đây là domain mà NLP phải đi xa hơn fluency: model cần factuality, reasoning, uncertainty và safety. Em thực nghiệm trên bài toán Vietnamese Medication Safety QA, dùng SFT để dạy format trả lời an toàn và DPO để alignment model tránh các hành vi nguy hiểm.
