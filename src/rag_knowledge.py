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
    # === Tương tác thuốc cơ bản ===
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

    # === Tương tác với thực phẩm ===
    KnowledgeSnippet(
        title="Metformin và rượu",
        keywords=("metformin", "rượu", "ruou", "bia", "tiểu đường", "tieu duong", "đái tháo"),
        content="Metformin kết hợp rượu có thể làm tăng nguy cơ toan lactic (axit lactic), một tình trạng y tế cấp tính.",
        action="Tránh hoặc hạn chế rượu bia; thông báo cho bác sĩ nếu uống rượu thường xuyên.",
    ),
    KnowledgeSnippet(
        title="Các thuốc chống sinh gồm tứ nguyên tệ (tetracycline) và sữa/cá xương",
        keywords=("tetracycline", "doxycycline", "sữa", "sua", "cá xương", "ca xuong", "canxi"),
        content="Các thuốc này bị ảnh hưởng bởi canxi; sữa, phô mai, cá xương có thể giảm hấp thu thuốc.",
        action="Uống thuốc cách xa 2-3 giờ so với sữa và thực phẩm giàu canxi.",
    ),
    KnowledgeSnippet(
        title="Warfarin và rau muống, cải bó xôi",
        keywords=("warfarin", "rau muống", "rau cai", "cai bo xoi", "chống đông", "chong dong", "vitamin k"),
        content="Rau xanh giàu vitamin K có thể làm giảm hiệu quả của warfarin; lượng rau xanh nên ổn định.",
        action="Ăn rau xanh đều đặn; không tăng/giảm đột ngột; theo dõi INR.",
    ),

    # === Độc tính ở người cao tuổi ===
    KnowledgeSnippet(
        title="Benzodiazepine ở người cao tuổi",
        keywords=("benzodiazepine", "diazepam", "alprazolam", "người già", "nguoi gia", "cao tuổi", "cao tuoi"),
        content="Người cao tuổi dễ bị rơi ngã, nhầm lẫn khi dùng benzodiazepine; nguy cơ dùng quá liều cao.",
        action="Cần giám sát chặt chẽ; nên dùng liều thấp; tránh lái xe, hoạt động nguy hiểm.",
    ),
    KnowledgeSnippet(
        title="Các thuốc chống cholinergic ở người cao tuổi",
        keywords=("anticholinergic", "sổi", "người già", "nguoi gia", "lú lẫn", "lu lan", "nhầm lẫn"),
        content="Người cao tuổi dễ bị lú lẫn, mất trí nhớ, táo bón khi dùng thuốc chống cholinergic.",
        action="Cần lựa chọn thuốc khác nếu có thể; giám sát dấu hiệu tâm thần.",
    ),

    # === Bệnh gan/thận ===
    KnowledgeSnippet(
        title="Thuốc ở bệnh nhân suy thận",
        keywords=("suy thận", "suy than", "thận", "creatinine", "clearance", "lọc thận"),
        content="Một số thuốc có thể tích tụ ở bệnh nhân suy thận và gây độc tính; liều phải được điều chỉnh.",
        action="Kiểm tra chức năng thận trước khi dùng; liên hệ bác sĩ để điều chỉnh liều.",
    ),
    KnowledgeSnippet(
        title="Thuốc ở bệnh nhân suy gan",
        keywords=("suy gan", "suy can", "gan", "liver", "cirrhosis", "xơ gan", "xo gan"),
        content="Bệnh nhân suy gan có khả năng chuyển hóa thuốc kém; dễ bị tích tụ và độc tính.",
        action="Thông báo cho bác sĩ về bệnh gan; có thể cần giảm liều hoặc chọn thuốc khác.",
    ),

    # === Tương tác MAOI ===
    KnowledgeSnippet(
        title="MAOI và thực phẩm giàu tyramine",
        keywords=("maoi", "moclobemide", "tyramine", "thực phẩm", "thuc pham", "pho", "pho mai", "pho cheese"),
        content="MAOI kết hợp tyramine (phô mai cũ, pho, sốt cà chua) có thể gây tăng huyết áp đột ngột nguy hiểm.",
        action="Tránh thực phẩm giàu tyramine; hỏi danh sách cụ thể từ dược sĩ.",
    ),

    # === An toàn Aspirin ===
    KnowledgeSnippet(
        title="Aspirin ở bệnh nhân chảy máu dạ dày",
        keywords=("aspirin", "chảy máu", "chay mau", "dạ dày", "da day", "loét", "luet"),
        content="Aspirin có thể gây chảy máu dạ dày và loét, đặc biệt nếu dùng lâu dài hoặc với NSAID khác.",
        action="Không dùng nếu có tiền sử loét; dùng liều thấp nhất; kết hợp với bảo vệ dạ dày nếu cần.",
    ),

    # === An toàn Methotrexate ===
    KnowledgeSnippet(
        title="Methotrexate và ổn định liều",
        keywords=("methotrexate", "ung thư", "ung thu", "viêm khớp", "viem khop", "rối loạn miễn dịch"),
        content="Methotrexate là thuốc mạnh dễ gây độc tính; cần giám sát huyết học và chức năng gan/thận thường xuyên.",
        action="Kiểm tra máu định kỳ; không tự ý thay đổi liều; báo ngay với bác sĩ về các tác dụng phụ.",
    ),

    # === Thiazide và kali ===
    KnowledgeSnippet(
        title="Thuốc lợi tiểu thiazide và kali",
        keywords=("thiazide", "hydrochlorothiazide", "kali", "potassium", "huyết áp", "huyet ap"),
        content="Thiazide làm mất kali; nếu không bù kali, có thể gây loạn nhịp tim, yếu cơ, mệt mỏi.",
        action="Ăn thực phẩm giàu kali (chuối, khoai, cà chua); kiểm tra kali huyết định kỳ.",
    ),

    # === Dùng thuốc mà không cần ===
    KnowledgeSnippet(
        title="Tự dùng kháng sinh không theo đơn",
        keywords=("kháng sinh", "khang sinh", "không đơn", "tu dung", "khong don"),
        content="Dùng kháng sinh tùy ý làm kháng kháng sinh, khiến thuốc kém hiệu quả trong tương lai.",
        action="Chỉ dùng kháng sinh theo đơn bác sĩ; hoàn thành đủ liệu trình.",
    ),

    # === Hạ đường huyết ===
    KnowledgeSnippet(
        title="Dấu hiệu hạ đường huyết cần chú ý",
        keywords=("hạ đường", "ha duong", "chóng mặt", "chong mat", "run tay", "run tay", "ra mồ hôi", "ra mo hoi"),
        content="Triệu chứng hạ đường huyết: run tay, ra mồ hôi, chóng mặt, lú lẫn, thèm ăn, tim đập nhanh.",
        action="Ăn kẹo, mật ong, nước ngọt; nếu nặng hoặc không tỉnh lại là cấp cứu.",
    ),

    # === Hamartia liều ===
    KnowledgeSnippet(
        title="Heparin và giám sát aPTT",
        keywords=("heparin", "chống đông", "chong dong", "aptt", "máu", "mau", "chảy máu"),
        content="Heparin cần giám sát chặt chẽ bằng aPTT; liều quá cao gây chảy máu, quá thấp không tác dụng.",
        action="Kiểm tra aPTT thường xuyên; báo ngay với bác sĩ nếu có dấu hiệu chảy máu.",
    ),

    # === Corticosteroid ===
    KnowledgeSnippet(
        title="Corticosteroid dài hạn",
        keywords=("corticosteroid", "prednisone", "prednisolone", "dài hạn", "dai han", "tăng đường", "tang duong"),
        content="Dùng corticosteroid lâu dài có thể gây loãng xương, tăng đường huyết, kém miễn dịch, tăng cân.",
        action="Uống với thực phẩm; bổ sung canxi và vitamin D; không tự ngưng đột ngột.",
    ),

    # === Lithium ===
    KnowledgeSnippet(
        title="Lithium và lượng nước, natri",
        keywords=("lithium", "tâm thần", "tam than", "bipolar", "natri", "nước", "nước"),
        content="Lithium bị ảnh hưởng bởi lượng natri và nước; mất nước có thể làm tăng độc tính lithium.",
        action="Uống đủ nước; ăn đủ muối; kiểm tra lithium máu định kỳ; báo với bác sĩ nếu tiêu chảy hoặc nôn.",
    ),

    # === Kháng acid và tương tác ===
    KnowledgeSnippet(
        title="Kháng acid và hấp thu thuốc khác",
        keywords=("kháng acid", "khang acid", "antacid", "omeprazole", "ranitidine", "hấp thu", "hap thu"),
        content="Kháng acid giảm hấp thu của một số thuốc như iron, azole antifungals, digoxin.",
        action="Uống kháng acid cách xa các thuốc khác ít nhất 2 giờ.",
    ),

    # === Allergia ===
    KnowledgeSnippet(
        title="Dị ứng kháng sinh Penicillin và Cephalosporin",
        keywords=("dị ứng", "di ung", "penicillin", "cephalosporin", "phát ban", "phat ban", "sốc phản vệ"),
        content="Người dị ứng penicillin có thể dị ứng cephalosporin; có thể gây phát ban, sốc phản vệ.",
        action="Báo luôn dị ứng khi thăm khám; mang thẻ cảnh báo nếu dị ứng nặng.",
    ),

    # === Metronidazole ===
    KnowledgeSnippet(
        title="Metronidazole và rượu",
        keywords=("metronidazole", "flagyl", "rượu", "ruou", "bia", "buồn nôn", "buon non"),
        content="Metronidazole kết hợp rượu gây buồn nôn, chóng mặt, đỏ mặt, khó chịu.",
        action="Tránh rượu bia trong quá trình dùng metronidazole và 48 giờ sau khi ngưng.",
    ),

    # === Chống viêm ===
    KnowledgeSnippet(
        title="Liều Ibuprofen an toàn",
        keywords=("ibuprofen", "ibu", "giảm đau", "giam dau", "viêm", "viem", "liều", "lieu"),
        content="Liều ibuprofen tối đa 2400-3200 mg/ngày; dùng liều thấp nhất trong thời gian ngắn nhất.",
        action="Dùng với thực phẩm; báo với bác sĩ nếu dùng thường xuyên.",
    ),

    # === Thyroid ===
    KnowledgeSnippet(
        title="Levothyroxine và hấp thu",
        keywords=("levothyroxine", "thyroid", "tuyến giáp", "tuyen giap", "sữa", "sua", "iron"),
        content="Levothyroxine bị ảnh hưởng bởi sữa, iron, canxi; uống cách xa 4-6 giờ.",
        action="Uống sáng sớm trên bụng không; cách xa thực phẩm, vitamin và kháng acid.",
    ),

    # === Dị ứng thuốc ===
    KnowledgeSnippet(
        title="Phản ứng Gell-Coombs loại 1 (dị ứng cấp tính)",
        keywords=("dị ứng", "di ung", "sốc phản vệ", "soc phan ve", "ngạt thở", "ngat tho", "sưng mặt"),
        content="Dị ứng loại 1 xảy ra nhanh (phút): sưng mặt, ngạt thở, huyết áp giảm, sốc. Cần cấp cứu ngay.",
        action="Gọi cấp cứu ngay 115; có epinephrine sẵn nếu biết dị ứng nặng.",
    ),

    # === Tự dừng thuốc tâm thần ===
    KnowledgeSnippet(
        title="Đừng tự dừng thuốc chống trầm cảm đột ngột",
        keywords=("trầm cảm", "tram cam", "serotonin", "antidepressant", "dừng", "dung", "đột ngột", "dot ngot"),
        content="Ngưng đột ngột thuốc chống trầm cảm gây hội chứng rút: chóng mặt, chứng rối loạn, tê tay chân.",
        action="Giảm liều dần; lên kế hoạch với bác sĩ; không tự ngưng.",
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

