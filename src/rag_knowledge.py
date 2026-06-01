"""Tiny rule-based retrieval layer for medication safety demo."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class KnowledgeSnippet:
    title: str
    keywords: tuple[str, ...]
    content: str
    action: str


KNOWLEDGE_BASE = [
    KnowledgeSnippet(
        title="Quên liều thuốc",
        keywords=("quên", "quen", "uống bù", "uong bu", "gấp đôi", "gap doi"),
        content="Không tự ý uống gấp đôi liều để bù liều đã quên, vì một số thuốc có thể gây quá liều hoặc tác dụng phụ.",
        action="Kiểm tra tờ hướng dẫn thuốc và hỏi bác sĩ/dược sĩ nếu không chắc.",
    ),
    KnowledgeSnippet(
        title="Warfarin và thuốc giảm đau NSAID",
        keywords=("warfarin", "ibuprofen", "aspirin", "chống đông", "chong dong"),
        content="Warfarin dùng chung với một số thuốc giảm đau như ibuprofen/aspirin có thể làm tăng nguy cơ chảy máu.",
        action="Không tự ý phối hợp; hỏi bác sĩ/dược sĩ để chọn thuốc phù hợp.",
    ),
    KnowledgeSnippet(
        title="Paracetamol và rượu",
        keywords=("paracetamol", "para", "rượu", "ruou", "bia", "độc gan", "doc gan"),
        content="Paracetamol có nguy cơ gây độc gan khi dùng quá liều; rượu có thể làm nguy cơ này đáng lo hơn.",
        action="Tránh phối hợp với rượu và không vượt liều trên nhãn thuốc.",
    ),
    KnowledgeSnippet(
        title="Kháng sinh",
        keywords=("kháng sinh", "khang sinh", "ks", "đỡ bệnh", "do benh"),
        content="Tự ngưng kháng sinh sớm có thể làm nhiễm trùng chưa khỏi hẳn và góp phần gây kháng kháng sinh.",
        action="Dùng theo đơn; liên hệ bác sĩ nếu có tác dụng phụ hoặc muốn dừng.",
    ),
    KnowledgeSnippet(
        title="Quá liều hoặc uống nhầm nhiều thuốc",
        keywords=("quá liều", "qua lieu", "uống nhầm", "uong nham", "nhiều viên", "thuốc ngủ", "ngộ độc"),
        content="Uống nhầm nhiều viên thuốc hoặc quá liều có thể gây nguy hiểm, đặc biệt với thuốc ngủ, thuốc tim mạch, insulin hoặc thuốc của trẻ em.",
        action="Gọi cấp cứu hoặc đến cơ sở y tế ngay; mang theo vỏ thuốc nếu có.",
    ),
    KnowledgeSnippet(
        title="Phụ nữ mang thai và trẻ em",
        keywords=("mang thai", "có bầu", "co bau", "trẻ em", "tre em", "em bé"),
        content="Phụ nữ mang thai và trẻ em là nhóm nhạy cảm; thuốc, liều và dạng bào chế cần được chọn cẩn thận.",
        action="Không tự dùng thuốc người lớn cho trẻ; hỏi bác sĩ/dược sĩ trước khi dùng.",
    ),
    KnowledgeSnippet(
        title="Insulin và bỏ bữa",
        keywords=("insulin", "bỏ bữa", "bo bua", "hạ đường huyết", "ha duong huyet"),
        content="Insulin khi không ăn đủ có thể gây hạ đường huyết, với biểu hiện run tay, vã mồ hôi, lú lẫn hoặc ngất.",
        action="Cần kế hoạch xử trí từ bác sĩ; tìm trợ giúp nếu có dấu hiệu nặng.",
    ),
]


def retrieve_snippets(query: str, top_k: int = 3) -> list[KnowledgeSnippet]:
    lowered = query.lower()
    scored = []
    for snippet in KNOWLEDGE_BASE:
        score = sum(1 for keyword in snippet.keywords if keyword in lowered)
        if score:
            scored.append((score, snippet))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [snippet for _, snippet in scored[:top_k]]

