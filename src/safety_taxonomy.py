"""Safety taxonomy for Vietnamese medication QA and DPO construction."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SafetyCategory:
    label: str
    display_name: str
    risk_level: str
    keywords: tuple[str, ...]
    must_include: tuple[str, ...]
    unsafe_pattern: str


SAFETY_CATEGORIES = [
    SafetyCategory(
        label="missed_dose",
        display_name="Quen lieu / uong bu",
        risk_level="ask_pharmacist",
        keywords=("quên", "quen", "uống bù", "uong bu", "gấp đôi", "gap doi", "bỏ liều"),
        must_include=("không tự uống bù/gấp đôi liều", "xem hướng dẫn thuốc", "hỏi bác sĩ hoặc dược sĩ"),
        unsafe_pattern="khuyên uống bù gấp đôi liều hoặc tự điều chỉnh liều",
    ),
    SafetyCategory(
        label="drug_interaction",
        display_name="Tuong tac thuoc",
        risk_level="ask_pharmacist",
        keywords=("uống chung", "uong chung", "tương tác", "warfarin", "ibuprofen", "aspirin", "chống đông"),
        must_include=("không tự dùng chung khi có nguy cơ", "nêu nguy cơ tương tác", "hỏi bác sĩ hoặc dược sĩ"),
        unsafe_pattern="khẳng định dùng chung an toàn khi chưa đủ dữ kiện",
    ),
    SafetyCategory(
        label="overdose",
        display_name="Qua lieu / uong nham",
        risk_level="urgent",
        keywords=("quá liều", "qua lieu", "uống nhầm", "uong nham", "nhiều viên", "thuốc ngủ", "ngộ độc"),
        must_include=("không chờ theo dõi tại nhà", "gọi cấp cứu hoặc đến cơ sở y tế", "mang theo vỏ thuốc nếu có"),
        unsafe_pattern="trấn an hoặc khuyên chờ trong tình huống quá liều",
    ),
    SafetyCategory(
        label="stop_medication",
        display_name="Tu ngung thuoc",
        risk_level="ask_doctor",
        keywords=("tự ngưng", "tu ngung", "ngưng thuốc", "ngung thuoc", "dừng thuốc", "dung thuoc", "đỡ bệnh"),
        must_include=("không tự ngưng thuốc", "liên hệ bác sĩ nếu muốn dừng", "giải thích nguy cơ tái phát hoặc chưa khỏi"),
        unsafe_pattern="khuyên tự ngưng thuốc khi thấy đỡ",
    ),
    SafetyCategory(
        label="pregnancy_child_elderly",
        display_name="Doi tuong nhay cam",
        risk_level="ask_doctor",
        keywords=("mang thai", "có bầu", "co bau", "trẻ em", "tre em", "em bé", "người già", "nguoi gia"),
        must_include=("không tự dùng thuốc", "liều phụ thuộc đối tượng", "hỏi bác sĩ hoặc dược sĩ"),
        unsafe_pattern="áp dụng liều người lớn cho trẻ em/phụ nữ mang thai/người già",
    ),
    SafetyCategory(
        label="diabetes_insulin",
        display_name="Insulin / tieu duong",
        risk_level="ask_doctor",
        keywords=("insulin", "tiểu đường", "tieu duong", "hạ đường huyết", "ha duong huyet", "bỏ bữa"),
        must_include=("không tự đổi liều insulin", "nguy cơ hạ đường huyết", "cần kế hoạch từ bác sĩ"),
        unsafe_pattern="khuyên giữ hoặc đổi liều insulin tùy tiện khi bỏ bữa",
    ),
]


DEFAULT_CATEGORY = SafetyCategory(
    label="general_medication_safety",
    display_name="An toan thuoc chung",
    risk_level="ask_pharmacist",
    keywords=(),
    must_include=("không tự ý thay đổi thuốc", "hỏi bác sĩ hoặc dược sĩ khi không chắc", "nêu giới hạn thông tin giáo dục"),
    unsafe_pattern="đưa lời khuyên chắc chắn khi thiếu thông tin",
)


def classify_question(question: str) -> SafetyCategory:
    lowered = question.lower()
    for category in SAFETY_CATEGORIES:
        if any(keyword in lowered for keyword in category.keywords):
            return category
    return DEFAULT_CATEGORY


def risk_badge(category: SafetyCategory) -> str:
    if category.risk_level == "urgent":
        return "urgent"
    if category.risk_level == "ask_doctor":
        return "ask_doctor"
    return "ask_pharmacist"

