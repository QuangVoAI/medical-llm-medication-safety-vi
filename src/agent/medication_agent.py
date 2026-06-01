"""Controlled Agentic RAG pipeline for Vietnamese medication safety."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from src.agent.policy import AgentDecision, decide_action, self_check
from src.agent.tools import extract_drug_entities, hybrid_retrieve, normalize_question, rewrite_query
from src.evaluator import score_answer
from src.retrieval.hybrid_retriever import HybridRetriever
from src.safety_taxonomy import classify_question


@dataclass
class AgentResult:
    answer: str
    context: str
    scores: dict
    summary: str
    trace: dict
    decision: str


class MedicationSafetyAgent:
    def __init__(self, retriever: HybridRetriever | None = None):
        self.retriever = retriever or HybridRetriever(use_sentence_transformers=False)

    def run(self, question: str, model_answer_fn=None) -> AgentResult:
        normalized = normalize_question(question)
        entities = extract_drug_entities(normalized)
        category = classify_question(normalized)
        decision = decide_action(normalized, category, entities)
        rewritten = rewrite_query(normalized, category, entities)
        retrieved = hybrid_retrieve(rewritten, category, self.retriever)
        retrieved = self._filter_retrieved_for_decision(retrieved, decision)
        context = "\n".join(
            f"- [{source}] {doc.title}: {doc.text}" for doc, _score, source in retrieved
        ) or "- Không tìm thấy tài liệu phù hợp."

        fallback_answer = self._fallback_answer(normalized, category, decision, context)
        generated = model_answer_fn(normalized, context) if model_answer_fn and decision.action == "answer" else None
        answer = generated or fallback_answer
        passed, issues = self_check(answer, decision)
        if not passed:
            answer = self._repair_answer(normalized, decision, issues)

        scores = score_answer(normalized, answer)
        trace = {
            "normalized_question": normalized,
            "entities": entities,
            "category": category.label,
            "risk_level": decision.risk_level,
            "decision": asdict(decision),
            "rewritten_query": rewritten,
            "retrieved_docs": [
                {"doc_id": doc.doc_id, "title": doc.title, "score": round(score, 3), "retriever": source}
                for doc, score, source in retrieved
            ],
            "self_check": {"passed": passed, "issues": issues},
            "generation_mode": "model" if generated else "agentic_rag_fallback",
        }
        summary = (
            f"Decision: {decision.action}\n"
            f"Risk level: {decision.risk_level}\n"
            f"Category: {category.label}\n"
            f"Entities: {', '.join(entities) if entities else 'none'}\n"
            f"Self-check: {'passed' if passed else 'repaired'}"
        )
        return AgentResult(answer, context, scores, summary, trace, decision.action)

    def _fallback_answer(self, question: str, category, decision: AgentDecision, context: str) -> str:
        if decision.action == "out_of_scope":
            return (
                "Câu hỏi này nằm ngoài phạm vi demo an toàn sử dụng thuốc. "
                "Mình không nên bịa thông tin y tế cho câu hỏi không liên quan. "
                "Nếu bạn muốn hỏi về thuốc, hãy gửi tên thuốc, liều và tình huống sử dụng."
            )
        if decision.action == "ask_clarification":
            return (
                "Không đủ thông tin để xác định thuốc hoặc liều dùng. Không nên đoán thuốc dựa trên màu sắc/hình dạng. "
                "Bạn cần kiểm tra tên thuốc, hoạt chất, hàm lượng trên vỏ thuốc hoặc hỏi dược sĩ/bác sĩ."
            )
        if decision.action == "urgent":
            return (
                "Đây có thể là tình huống nguy hiểm. Không nên chờ theo dõi tại nhà. "
                "Hãy gọi cấp cứu hoặc đưa người bệnh đến cơ sở y tế ngay, và mang theo vỏ thuốc nếu có. "
                "Mình chỉ cung cấp thông tin giáo dục, không thay thế nhân viên y tế."
            )

        must = "; ".join(category.must_include)
        return (
            f"Với câu hỏi này, hướng an toàn là: {must}. "
            "Bạn không nên tự ý thêm, ngưng, đổi thuốc hoặc đổi liều khi chưa có hướng dẫn chuyên môn. "
            "Nếu có triệu chứng nặng, bất thường hoặc không chắc loại thuốc đang dùng, hãy hỏi bác sĩ/dược sĩ."
        )

    def _filter_retrieved_for_decision(self, retrieved, decision: AgentDecision):
        filtered = []
        for doc, score, source in retrieved:
            if doc.doc_id == "scope-offtopic" and decision.action != "out_of_scope":
                continue
            if doc.doc_id == "scope-ambiguous-pill" and decision.action != "ask_clarification":
                continue
            filtered.append((doc, score, source))
        return filtered or retrieved[:1]

    def _repair_answer(self, question: str, decision: AgentDecision, issues: list[str]) -> str:
        if decision.action == "urgent":
            return "Có dấu hiệu nguy hiểm. Hãy gọi cấp cứu hoặc đến cơ sở y tế ngay, mang theo vỏ thuốc nếu có."
        if decision.action == "ask_clarification":
            return "Không đủ thông tin để trả lời an toàn. Cần tên thuốc, hàm lượng, đơn thuốc hoặc hỏi dược sĩ/bác sĩ."
        return (
            "Để an toàn, không tự ý thay đổi thuốc hoặc liều dùng. "
            "Hãy hỏi bác sĩ/dược sĩ, đặc biệt nếu có triệu chứng bất thường hoặc đang dùng nhiều thuốc."
        )
