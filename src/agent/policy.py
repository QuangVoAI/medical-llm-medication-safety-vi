"""Controlled policy for medication safety agent."""

from __future__ import annotations

from dataclasses import dataclass

from src.safety_taxonomy import SafetyCategory


OFF_TOPIC_KEYWORDS = ("thời tiết", "tp.hcm", "python", "sắp xếp", "danh sách", "code", "hàm")
AMBIGUOUS_KEYWORDS = ("viên thuốc màu", "màu xanh", "màu trắng", "uống mấy viên", "thuốc này")


@dataclass(frozen=True)
class AgentDecision:
    action: str
    risk_level: str
    reason: str


def decide_action(question: str, category: SafetyCategory, entities: list[str]) -> AgentDecision:
    lowered = question.lower()
    if any(keyword in lowered for keyword in OFF_TOPIC_KEYWORDS):
        return AgentDecision("out_of_scope", "out_of_scope", "Question is not about medication safety.")
    if any(keyword in lowered for keyword in AMBIGUOUS_KEYWORDS) and not entities:
        return AgentDecision("ask_clarification", "ask_pharmacist", "Medication identity is ambiguous.")
    if category.risk_level == "urgent":
        return AgentDecision("urgent", "urgent", "Potential overdose or emergency signal.")
    return AgentDecision("answer", category.risk_level, "Enough information for educational safety answer.")


def self_check(answer: str, decision: AgentDecision) -> tuple[bool, list[str]]:
    lowered = answer.lower()
    issues = []
    if decision.action == "urgent" and "cấp cứu" not in lowered and "cơ sở y tế" not in lowered:
        issues.append("urgent_answer_missing_emergency_instruction")
    if "uống gấp đôi" in lowered and "không" not in lowered[:80]:
        issues.append("possible_self_dose_advice")
    if "tự ngưng" in lowered and "không" not in lowered[:80]:
        issues.append("possible_self_stop_advice")
    if decision.action == "ask_clarification" and not any(term in lowered for term in ("không đủ", "cần", "dược sĩ")):
        issues.append("ambiguous_case_missing_clarification")
    return not issues, issues

