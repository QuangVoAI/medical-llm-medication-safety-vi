# Medical LLM Overview And Benchmarks

Tài liệu này dùng để làm slide phần overview Medical LLM và benchmark. Trọng tâm bài thực nghiệm vẫn là SFT/DPO cho Vietnamese Medication Safety QA.

## Medical LLM Là Gì?

Medical LLM là mô hình ngôn ngữ lớn được huấn luyện, tiếp tục pretrain, instruction-tune hoặc alignment trên dữ liệu y sinh/y khoa.

Nguồn dữ liệu thường gặp:

- biomedical literature: PubMed, PubMed Central, paper y sinh;
- medical textbooks và guideline;
- medical QA datasets;
- clinical notes hoặc EHR đã xử lý quyền riêng tư;
- hội thoại bác sĩ-bệnh nhân hoặc câu hỏi sức khỏe từ người dùng.

Điểm khác với LLM tổng quát:

- cần factuality cao hơn;
- câu trả lời sai có thể gây hại;
- phải biết uncertainty, không chẩn đoán chắc chắn khi thiếu dữ kiện;
- phải biết escalation: hỏi bác sĩ, dược sĩ, cấp cứu;
- phải tôn trọng privacy và giới hạn lâm sàng.

## Vì Sao Medical LLM Khó?

| Vấn đề | Ý nghĩa khi trình bày |
|---|---|
| Hallucination | Một câu trả lời nghe hợp lý nhưng sai y khoa có thể nguy hiểm. |
| Domain knowledge | Thuật ngữ, thuốc, tương tác thuốc, guideline thay đổi theo thời gian. |
| Clinical reasoning | Nhiều câu hỏi cần suy luận nhiều bước và hỏi thêm thông tin. |
| Safety | Không được khuyên tự đổi liều, tự ngưng thuốc, trì hoãn cấp cứu. |
| Evaluation | Accuracy trắc nghiệm chưa đủ để đo usefulness và safety trong hội thoại thật. |

## Các Model Tiêu Biểu

| Model | Ý chính | Nên nói gì trong slide |
|---|---|---|
| Med-PaLM | Google/DeepMind dùng PaLM/Flan-PaLM và benchmark MultiMedQA. | Một mốc quan trọng cho medical QA và clinical knowledge. |
| Med-PaLM 2 | Cải thiện mạnh trên MultiMedQA và đánh giá lâm sàng. | Cho thấy prompt, instruction tuning và alignment rất quan trọng. |
| BioGPT | Generative Transformer được pretrain trên biomedical literature. | Mạnh về biomedical text generation/mining, không nhất thiết tối ưu hội thoại tiếng Việt. |
| PubMedGPT | 2.7B model trained on biomedical literature. | Ví dụ domain pretraining nhỏ hơn nhưng tập trung vào PubMed. |
| PMC-LLaMA | Open-source LLaMA adapted to medicine using PMC papers/textbooks and instruction tuning. | Ví dụ open medical LLM có data-centric knowledge injection. |
| Meditron | Open medical LLM family, 7B/70B, medical pretraining. | Ví dụ hướng scale medical pretraining cho open-source LLM. |

Điểm cần nhấn mạnh:

> Model y tế mạnh không tự động phù hợp với bài của em, vì bài của em cần fine-tune tiếng Việt, chạy được trên GPU vừa sức, và chứng minh pipeline SFT/DPO. Các model y tế lớn có thể dùng làm teacher hoặc hướng nâng cấp.

## Benchmark Truyền Thống

| Benchmark | Dạng task | Đo được gì | Hạn chế |
|---|---|---|---|
| MedQA | Câu hỏi kiểu USMLE/medical exam | Medical knowledge và exam reasoning | Chủ yếu trắc nghiệm, không giống hội thoại bệnh nhân. |
| MedMCQA | Multiple-choice medical QA quy mô lớn | Kiến thức nhiều chuyên ngành y | Trắc nghiệm, có thể chưa đo safety. |
| PubMedQA | QA dựa trên abstract PubMed, yes/no/maybe | Đọc hiểu biomedical literature | Không đại diện đầy đủ cho patient-facing advice. |
| MMLU Medical subsets | Các môn y trong MMLU | Kiến thức tổng quát theo môn | Không chuyên sâu vào clinical safety. |
| MultiMedQA | Tập hợp MedQA, MedMCQA, PubMedQA, LiveQA, MedicationQA, MMLU clinical topics, HealthSearchQA | Đánh giá rộng hơn cho medical QA | Vẫn cần human evaluation cho harm, factuality, equity, usefulness. |

Thông điệp:

> Benchmark trắc nghiệm đo kiến thức, nhưng Medical LLM thật cần đo thêm factuality, uncertainty, harm, usefulness và hành vi hội thoại.

## Benchmark Mới Và Thực Tế Hơn

| Benchmark | Điểm mạnh | Vì sao đáng nhắc |
|---|---|---|
| MedHELM | Holistic healthcare evaluation, hướng tới real-world applicability. | Cho thấy medical evaluation không chỉ là accuracy, mà còn nhiều kịch bản healthcare thực tế. |
| HealthBench | 5,000 multi-turn health conversations, physician-written rubrics. | Gần với cách người dùng/bác sĩ thật trò chuyện với LLM, có chấm safety và usefulness theo rubric. |
| HealthBench Professional | Tập trung task clinician-facing như care consult, writing/documentation, medical research. | Gợi ý hướng benchmark tương lai cho workflow của bác sĩ thật. |

## Benchmark Va Related Work Gan Hon Voi De Tai

| Ten | Vai tro doi voi de tai |
|---|---|
| ViMedAQA | Nguon Vietnamese medical QA de mo rong SFT, nhung can loc chi cac case lien quan den medication safety. |
| VM14K | Benchmark y khoa tieng Viet de dat bai toan vao boi canh Vietnamese medical NLP. |
| MedSafetyBench | Y tuong cho safety taxonomy, unsafe cases va evaluation beyond factuality. |
| RxSafeBench | Gan nhat voi medication safety; huu ich cho hard negatives, contraindication, drug-drug interaction va patient risk framing. |

Thong diep:

> Related work gan nhat voi bai cua em khong chi la Medical LLM chung chung, ma la giao diem giua Vietnamese medical QA, medication safety, va safety benchmark.

## Liên Hệ Với Đề Tài Của Em

Đề tài của em không cố cạnh tranh benchmark lớn. Em dùng một bài toán nhỏ nhưng có ý nghĩa safety:

> Vietnamese Medication Safety QA.

Mapping với Medical LLM evaluation:

| Yêu cầu medical LLM | Em kiểm tra bằng gì |
|---|---|
| Trả lời tiếng Việt | SFT Vietnamese QA. |
| Robust với không dấu/viết tắt | Informal augmentation: `ko`, `dc`, `ks`, `ibu`, `para`. |
| Không khuyên hành vi nguy hiểm | DPO chosen/rejected safety pairs. |
| Biết escalation | Prompt cases: quá liều, thuốc ngủ, tương tác thuốc, quên liều. |
| Evaluation | Manual safety rubric 0-3 + qualitative Base/SFT/DPO comparison. |

Mapping related work vao pipeline:

| Thanh phan | Em dung nguon nao |
|---|---|
| SFT core | dataset medication safety tieng Viet hien tai |
| SFT broaden | ViMedAQA + Meddies/MedLens + grounded synthetic QA |
| DPO design | MedSafetyBench + RxSafeBench la nguon y tuong cho hard negatives va unsafe-but-fluent responses |
| Benchmark narrative | VM14K cho boi canh tieng Viet; HealthBench/MedSafetyBench/RxSafeBench cho safety evaluation hien dai |

## Câu Nói Khi Chuyển Sang Demo

> Sau khi tìm hiểu benchmark, em thấy nhiều benchmark truyền thống đo kiến thức y khoa bằng trắc nghiệm. Vì bài lab yêu cầu SFT/DPO, em chọn một lát cắt nhỏ hơn: Medication Safety QA tiếng Việt. Em không claim model đạt chuẩn lâm sàng, mà dùng task này để minh họa fine-tuning và alignment theo safety.

## References

- [Large language models encode clinical knowledge, Nature](https://www.nature.com/articles/s41586-023-06291-2)
- [Toward expert-level medical question answering with large language models, Nature Medicine](https://www.nature.com/articles/s41591-024-03423-7)
- [MedHELM, Stanford CRFM](https://crfm.stanford.edu/helm/medhelm/v2.0.0/)
- [HealthBench, OpenAI](https://openai.com/index/healthbench/)
- [HealthBench paper, arXiv](https://arxiv.org/abs/2505.08775)
- [BioGPT paper](https://academic.oup.com/bib/article/23/6/bbac409/6713511)
- [PubMedGPT 2.7B, Stanford HAI](https://hai.stanford.edu/news/stanford-crfm-introduces-pubmedgpt-27b/)
- [PMC-LLaMA, PubMed Central](https://pmc.ncbi.nlm.nih.gov/articles/PMC11639126/)
- [MEDITRON-70B paper](https://arxiv.org/abs/2311.16079)
