# Auto-generated from medical_documents.json + base knowledge base
from dataclasses import dataclass

@dataclass(frozen=True)
class KnowledgeSnippet:
    title: str
    keywords: tuple[str, ...]
    content: str
    action: str

EXTENDED_KNOWLEDGE_BASE = [
    KnowledgeSnippet(
        title='Quên liều thuốc',
        keywords=('quên', 'quen', 'uống bù', 'uong bu', 'gấp đôi', 'gap doi'),
        content='Không tự ý uống gấp đôi liều để bù liều đã quên, vì một số thuốc có thể gây quá liều hoặc tác dụng phụ.',
        action='Kiểm tra tờ hướng dẫn thuốc và hỏi bác sĩ/dược sĩ nếu không chắc.',
    ),
    KnowledgeSnippet(
        title='Warfarin và thuốc giảm đau NSAID',
        keywords=('warfarin', 'ibuprofen', 'aspirin', 'chống đông', 'chong dong'),
        content='Warfarin dùng chung với một số thuốc giảm đau như ibuprofen/aspirin có thể làm tăng nguy cơ chảy máu.',
        action='Không tự ý phối hợp; hỏi bác sĩ/dược sĩ để chọn thuốc phù hợp.',
    ),
    KnowledgeSnippet(
        title='Paracetamol và rượu',
        keywords=('paracetamol', 'para', 'rượu', 'ruou', 'bia', 'độc gan', 'doc gan'),
        content='Paracetamol có nguy cơ gây độc gan khi dùng quá liều; rượu có thể làm nguy cơ này đáng lo hơn.',
        action='Tránh phối hợp với rượu và không vượt liều trên nhãn thuốc.',
    ),
    KnowledgeSnippet(
        title='Kháng sinh',
        keywords=('kháng sinh', 'khang sinh', 'ks', 'đỡ bệnh', 'do benh'),
        content='Tự ngưng kháng sinh sớm có thể làm nhiễm trùng chưa khỏi hẳn và góp phần gây kháng kháng sinh.',
        action='Dùng theo đơn; liên hệ bác sĩ nếu có tác dụng phụ hoặc muốn dừng.',
    ),
    KnowledgeSnippet(
        title='Quá liều hoặc uống nhầm nhiều thuốc',
        keywords=('quá liều', 'qua lieu', 'uống nhầm', 'uong nham', 'nhiều viên', 'thuốc ngủ', 'ngộ độc'),
        content='Uống nhầm nhiều viên thuốc hoặc quá liều có thể gây nguy hiểm, đặc biệt với thuốc ngủ, thuốc tim mạch, insulin hoặc thuốc của trẻ em.',
        action='Gọi cấp cứu hoặc đến cơ sở y tế ngay; mang theo vỏ thuốc nếu có.',
    ),
    KnowledgeSnippet(
        title='Phụ nữ mang thai và trẻ em',
        keywords=('mang thai', 'có bầu', 'co bau', 'trẻ em', 'tre em', 'em bé'),
        content='Phụ nữ mang thai và trẻ em là nhóm nhạy cảm; thuốc, liều và dạng bào chế cần được chọn cẩn thận.',
        action='Không tự dùng thuốc người lớn cho trẻ; hỏi bác sĩ/dược sĩ trước khi dùng.',
    ),
    KnowledgeSnippet(
        title='Insulin và bỏ bữa',
        keywords=('insulin', 'bỏ bữa', 'bo bua', 'hạ đường huyết', 'ha duong huyet'),
        content='Insulin khi không ăn đủ có thể gây hạ đường huyết, với biểu hiện run tay, vã mồ hôi, lú lẫn hoặc ngất.',
        action='Cần kế hoạch xử trí từ bác sĩ; tìm trợ giúp nếu có dấu hiệu nặng.',
    ),
    KnowledgeSnippet(
        title='Metformin và rượu',
        keywords=('metformin', 'rượu', 'ruou', 'bia', 'tiểu đường', 'tieu duong', 'đái tháo'),
        content='Metformin kết hợp rượu có thể làm tăng nguy cơ toan lactic (axit lactic), một tình trạng y tế cấp tính.',
        action='Tránh hoặc hạn chế rượu bia; thông báo cho bác sĩ nếu uống rượu thường xuyên.',
    ),
    KnowledgeSnippet(
        title='Các thuốc chống sinh gồm tứ nguyên tệ (tetracycline) và sữa/cá xương',
        keywords=('tetracycline', 'doxycycline', 'sữa', 'sua', 'cá xương', 'ca xuong', 'canxi'),
        content='Các thuốc này bị ảnh hưởng bởi canxi; sữa, phô mai, cá xương có thể giảm hấp thu thuốc.',
        action='Uống thuốc cách xa 2-3 giờ so với sữa và thực phẩm giàu canxi.',
    ),
    KnowledgeSnippet(
        title='Warfarin và rau muống, cải bó xôi',
        keywords=('warfarin', 'rau muống', 'rau cai', 'cai bo xoi', 'chống đông', 'chong dong', 'vitamin k'),
        content='Rau xanh giàu vitamin K có thể làm giảm hiệu quả của warfarin; lượng rau xanh nên ổn định.',
        action='Ăn rau xanh đều đặn; không tăng/giảm đột ngột; theo dõi INR.',
    ),
    KnowledgeSnippet(
        title='Benzodiazepine ở người cao tuổi',
        keywords=('benzodiazepine', 'diazepam', 'alprazolam', 'người già', 'nguoi gia', 'cao tuổi', 'cao tuoi'),
        content='Người cao tuổi dễ bị rơi ngã, nhầm lẫn khi dùng benzodiazepine; nguy cơ dùng quá liều cao.',
        action='Cần giám sát chặt chẽ; nên dùng liều thấp; tránh lái xe, hoạt động nguy hiểm.',
    ),
    KnowledgeSnippet(
        title='Các thuốc chống cholinergic ở người cao tuổi',
        keywords=('anticholinergic', 'sổi', 'người già', 'nguoi gia', 'lú lẫn', 'lu lan', 'nhầm lẫn'),
        content='Người cao tuổi dễ bị lú lẫn, mất trí nhớ, táo bón khi dùng thuốc chống cholinergic.',
        action='Cần lựa chọn thuốc khác nếu có thể; giám sát dấu hiệu tâm thần.',
    ),
    KnowledgeSnippet(
        title='Thuốc ở bệnh nhân suy thận',
        keywords=('suy thận', 'suy than', 'thận', 'creatinine', 'clearance', 'lọc thận'),
        content='Một số thuốc có thể tích tụ ở bệnh nhân suy thận và gây độc tính; liều phải được điều chỉnh.',
        action='Kiểm tra chức năng thận trước khi dùng; liên hệ bác sĩ để điều chỉnh liều.',
    ),
    KnowledgeSnippet(
        title='Thuốc ở bệnh nhân suy gan',
        keywords=('suy gan', 'suy can', 'gan', 'liver', 'cirrhosis', 'xơ gan', 'xo gan'),
        content='Bệnh nhân suy gan có khả năng chuyển hóa thuốc kém; dễ bị tích tụ và độc tính.',
        action='Thông báo cho bác sĩ về bệnh gan; có thể cần giảm liều hoặc chọn thuốc khác.',
    ),
    KnowledgeSnippet(
        title='MAOI và thực phẩm giàu tyramine',
        keywords=('maoi', 'moclobemide', 'tyramine', 'thực phẩm', 'thuc pham', 'pho', 'pho mai', 'pho cheese'),
        content='MAOI kết hợp tyramine (phô mai cũ, pho, sốt cà chua) có thể gây tăng huyết áp đột ngột nguy hiểm.',
        action='Tránh thực phẩm giàu tyramine; hỏi danh sách cụ thể từ dược sĩ.',
    ),
    KnowledgeSnippet(
        title='Aspirin ở bệnh nhân chảy máu dạ dày',
        keywords=('aspirin', 'chảy máu', 'chay mau', 'dạ dày', 'da day', 'loét', 'luet'),
        content='Aspirin có thể gây chảy máu dạ dày và loét, đặc biệt nếu dùng lâu dài hoặc với NSAID khác.',
        action='Không dùng nếu có tiền sử loét; dùng liều thấp nhất; kết hợp với bảo vệ dạ dày nếu cần.',
    ),
    KnowledgeSnippet(
        title='Methotrexate và ổn định liều',
        keywords=('methotrexate', 'ung thư', 'ung thu', 'viêm khớp', 'viem khop', 'rối loạn miễn dịch'),
        content='Methotrexate là thuốc mạnh dễ gây độc tính; cần giám sát huyết học và chức năng gan/thận thường xuyên.',
        action='Kiểm tra máu định kỳ; không tự ý thay đổi liều; báo ngay với bác sĩ về các tác dụng phụ.',
    ),
    KnowledgeSnippet(
        title='Thuốc lợi tiểu thiazide và kali',
        keywords=('thiazide', 'hydrochlorothiazide', 'kali', 'potassium', 'huyết áp', 'huyet ap'),
        content='Thiazide làm mất kali; nếu không bù kali, có thể gây loạn nhịp tim, yếu cơ, mệt mỏi.',
        action='Ăn thực phẩm giàu kali (chuối, khoai, cà chua); kiểm tra kali huyết định kỳ.',
    ),
    KnowledgeSnippet(
        title='Tự dùng kháng sinh không theo đơn',
        keywords=('kháng sinh', 'khang sinh', 'không đơn', 'tu dung', 'khong don'),
        content='Dùng kháng sinh tùy ý làm kháng kháng sinh, khiến thuốc kém hiệu quả trong tương lai.',
        action='Chỉ dùng kháng sinh theo đơn bác sĩ; hoàn thành đủ liệu trình.',
    ),
    KnowledgeSnippet(
        title='Dấu hiệu hạ đường huyết cần chú ý',
        keywords=('hạ đường', 'ha duong', 'chóng mặt', 'chong mat', 'run tay', 'run tay', 'ra mồ hôi', 'ra mo hoi'),
        content='Triệu chứng hạ đường huyết: run tay, ra mồ hôi, chóng mặt, lú lẫn, thèm ăn, tim đập nhanh.',
        action='Ăn kẹo, mật ong, nước ngọt; nếu nặng hoặc không tỉnh lại là cấp cứu.',
    ),
    KnowledgeSnippet(
        title='Heparin và giám sát aPTT',
        keywords=('heparin', 'chống đông', 'chong dong', 'aptt', 'máu', 'mau', 'chảy máu'),
        content='Heparin cần giám sát chặt chẽ bằng aPTT; liều quá cao gây chảy máu, quá thấp không tác dụng.',
        action='Kiểm tra aPTT thường xuyên; báo ngay với bác sĩ nếu có dấu hiệu chảy máu.',
    ),
    KnowledgeSnippet(
        title='Corticosteroid dài hạn',
        keywords=('corticosteroid', 'prednisone', 'prednisolone', 'dài hạn', 'dai han', 'tăng đường', 'tang duong'),
        content='Dùng corticosteroid lâu dài có thể gây loãng xương, tăng đường huyết, kém miễn dịch, tăng cân.',
        action='Uống với thực phẩm; bổ sung canxi và vitamin D; không tự ngưng đột ngột.',
    ),
    KnowledgeSnippet(
        title='Lithium và lượng nước, natri',
        keywords=('lithium', 'tâm thần', 'tam than', 'bipolar', 'natri', 'nước', 'nước'),
        content='Lithium bị ảnh hưởng bởi lượng natri và nước; mất nước có thể làm tăng độc tính lithium.',
        action='Uống đủ nước; ăn đủ muối; kiểm tra lithium máu định kỳ; báo với bác sĩ nếu tiêu chảy hoặc nôn.',
    ),
    KnowledgeSnippet(
        title='Kháng acid và hấp thu thuốc khác',
        keywords=('kháng acid', 'khang acid', 'antacid', 'omeprazole', 'ranitidine', 'hấp thu', 'hap thu'),
        content='Kháng acid giảm hấp thu của một số thuốc như iron, azole antifungals, digoxin.',
        action='Uống kháng acid cách xa các thuốc khác ít nhất 2 giờ.',
    ),
    KnowledgeSnippet(
        title='Dị ứng kháng sinh Penicillin và Cephalosporin',
        keywords=('dị ứng', 'di ung', 'penicillin', 'cephalosporin', 'phát ban', 'phat ban', 'sốc phản vệ'),
        content='Người dị ứng penicillin có thể dị ứng cephalosporin; có thể gây phát ban, sốc phản vệ.',
        action='Báo luôn dị ứng khi thăm khám; mang thẻ cảnh báo nếu dị ứng nặng.',
    ),
    KnowledgeSnippet(
        title='Metronidazole và rượu',
        keywords=('metronidazole', 'flagyl', 'rượu', 'ruou', 'bia', 'buồn nôn', 'buon non'),
        content='Metronidazole kết hợp rượu gây buồn nôn, chóng mặt, đỏ mặt, khó chịu.',
        action='Tránh rượu bia trong quá trình dùng metronidazole và 48 giờ sau khi ngưng.',
    ),
    KnowledgeSnippet(
        title='Liều Ibuprofen an toàn',
        keywords=('ibuprofen', 'ibu', 'giảm đau', 'giam dau', 'viêm', 'viem', 'liều', 'lieu'),
        content='Liều ibuprofen tối đa 2400-3200 mg/ngày; dùng liều thấp nhất trong thời gian ngắn nhất.',
        action='Dùng với thực phẩm; báo với bác sĩ nếu dùng thường xuyên.',
    ),
    KnowledgeSnippet(
        title='Levothyroxine và hấp thu',
        keywords=('levothyroxine', 'thyroid', 'tuyến giáp', 'tuyen giap', 'sữa', 'sua', 'iron'),
        content='Levothyroxine bị ảnh hưởng bởi sữa, iron, canxi; uống cách xa 4-6 giờ.',
        action='Uống sáng sớm trên bụng không; cách xa thực phẩm, vitamin và kháng acid.',
    ),
    KnowledgeSnippet(
        title='Phản ứng Gell-Coombs loại 1 (dị ứng cấp tính)',
        keywords=('dị ứng', 'di ung', 'sốc phản vệ', 'soc phan ve', 'ngạt thở', 'ngat tho', 'sưng mặt'),
        content='Dị ứng loại 1 xảy ra nhanh (phút): sưng mặt, ngạt thở, huyết áp giảm, sốc. Cần cấp cứu ngay.',
        action='Gọi cấp cứu ngay 115; có epinephrine sẵn nếu biết dị ứng nặng.',
    ),
    KnowledgeSnippet(
        title='Đừng tự dừng thuốc chống trầm cảm đột ngột',
        keywords=('trầm cảm', 'tram cam', 'serotonin', 'antidepressant', 'dừng', 'dung', 'đột ngột', 'dot ngot'),
        content='Ngưng đột ngột thuốc chống trầm cảm gây hội chứng rút: chóng mặt, chứng rối loạn, tê tay chân.',
        action='Giảm liều dần; lên kế hoạch với bác sĩ; không tự ngưng.',
    ),
    KnowledgeSnippet(
        title='ACE inhibitor và Potassium',
        keywords=('ace inhibitor', 'lisinopril', 'enalapril', 'kali', 'potassium', 'cao'),
        content='ACE inhibitor có thể làm tăng kali huyết; khi dùng cần giám sát kali định kỳ, tránh bổ sung kali quá mức.',
        action='Kiểm tra kali máu mỗi 1-3 tháng; báo ngay với bác sĩ nếu kali cao.',
    ),
    KnowledgeSnippet(
        title='NSAIDs và bệnh tim mạch',
        keywords=('nsaid', 'ibuprofen', 'aspirin', 'tim mạch', 'tim mach', 'nhồi máu'),
        content='NSAIDs dùng lâu dài tăng nguy cơ nhồi máu, đột quỵ, suy tim ở người có bệnh tim.',
        action='Dùng liều thấp nhất trong thời gian ngắn; báo ngay bệnh tim cho bác sĩ.',
    ),
    KnowledgeSnippet(
        title='Cephalosporin và bệnh thận',
        keywords=('cephalosporin', 'cephalexin', 'thận', 'than', 'clearance', 'creatinine'),
        content='Cephalosporin bị thải qua thận; bệnh nhân suy thận có thể tích tụ thuốc.',
        action='Kiểm tra creatinine trước khi dùng; điều chỉnh liều theo eGFR.',
    ),
    KnowledgeSnippet(
        title='Fluconazole và Warfarin',
        keywords=('fluconazole', 'warfarin', 'chống đông', 'chong dong', 'inr'),
        content='Fluconazole ức chế CYP2C9, làm tăng INR; nguy cơ chảy máu.',
        action='Giám sát INR thường xuyên; có thể cần giảm warfarin.',
    ),
    KnowledgeSnippet(
        title='Simvastatin và Grapefruit juice',
        keywords=('simvastatin', 'statin', 'grapefruit', 'nước bưởi', 'nuoc buoi'),
        content='Grapefruit ức chế CYP3A4, làm tăng mức simvastatin, nguy cơ viêm cơ.',
        action='Tránh grapefruit; chọn statin khác nếu cần uống grapefruit.',
    ),
    KnowledgeSnippet(
        title='Erythromycin và QT prolongation',
        keywords=('erythromycin', 'clarithromycin', 'qt', 'tim', 'tim', 'rhythm'),
        content='Macrolide antibiotics có thể kéo dài QT, gây rối loạn nhịp tim.',
        action='Báo với bác sĩ nếu có tiền sử rối loạn nhịp; tránh nếu QT dài sẵn.',
    ),
    KnowledgeSnippet(
        title='Ritonavir và nhiều tương tác',
        keywords=('ritonavir', 'hiv', 'boost', 'boosted', 'tương tác', 'tuong tac'),
        content='Ritonavir là ức chế CYP3A4 mạnh; tương tác với rất nhiều thuốc, làm tăng mức độc tính.',
        action='Kiểm tra toàn bộ danh sách thuốc hiện tại với bác sĩ/dược sĩ.',
    ),
    KnowledgeSnippet(
        title='Phenytoin và tương tác phức tạp',
        keywords=('phenytoin', 'kytril', 'dilantin', 'co giật', 'co giat', 'tương tác'),
        content='Phenytoin là inducer mạnh của CYP450; làm giảm hiệu quả nhiều thuốc khác.',
        action='Kiểm tra danh sách thuốc đang uống; có thể cần tăng liều hoặc chuyển thuốc.',
    ),
    KnowledgeSnippet(
        title='Hướng dẫn xử trí tăng huyết áp từ Bộ Y Tế',
        keywords=('tăng huyết áp', 'tang huyet ap', 'huyết áp cao', 'hypertension', 'chẩn đoán', 'chan doan'),
        content='Tăng huyết áp được định nghĩa là ≥140/90 mmHg; cần đo lại 3 lần trong 1-4 tuần để chẩn đoán. Thay đổi lối sống là bước đầu tiên.',
        action='Đo huyết áp đúng kỹ thuật; theo dõi tại nhà; báo cáo với bác sĩ.',
    ),
    KnowledgeSnippet(
        title='Xử trí bệnh tiểu đường type 2 tại Việt Nam',
        keywords=('tiểu đường', 'tieu duong', 'type 2', 'glucose', 'đường huyết', 'duong huyet'),
        content='Mục tiêu kiểm soát glucose: lúc đói 6.1-7.0 mmol/L; sau ăn <10 mmol/L; HbA1c <7%. Cần giáo dục bệnh nhân về ăn uống, tập luyện.',
        action='Kiểm tra glucose định kỳ; học về dinh dưỡng; tập thể dục 150 phút/tuần.',
    ),
    KnowledgeSnippet(
        title='Phòng chống nhiễm trùng bằng kháng sinh hợp lý',
        keywords=('kháng sinh', 'khang sinh', 'nhiễm trùng', 'nhiem trung', 'hợp lý', 'hop ly'),
        content='Sử dụng kháng sinh chỉ khi có chỉ định, đúng liều, đúng thời gian. Tránh lạm dụng kháng sinh để phòng ngừa kháng kháng sinh.',
        action='Dùng theo đơn bác sĩ; hoàn thành đủ liệu trình; không chia sẻ kháng sinh với người khác.',
    ),
    KnowledgeSnippet(
        title='Tiêm chủng an toàn tại Việt Nam',
        keywords=('tiêm chủng', 'tiem chung', 'vaccine', 'vacxin', 'miễn dịch', 'mien dich'),
        content='Tuân thủ lịch tiêm chủng quốc gia; báo cáo phản ứng không mong muốn; không tiêm nếu bệnh nặng.',
        action='Tuân theo lịch Bộ Y Tế; báo cáo tác dụng phụ ngay; giữ thẻ tiêm chủng.',
    ),
    KnowledgeSnippet(
        title='Quản lý ung thư tại các bệnh viện Việt Nam',
        keywords=('ung thư', 'ung thu', 'hóa trị', 'hoa tri', 'xạ trị', 'xa tri'),
        content='Điều trị ung thư cần bác sĩ chuyên khoa; kết hợp phẫu thuật, hóa trị, xạ trị nếu cần. Cần tư vấn về chế độ dinh dưỡng.',
        action='Thăm khám tại bệnh viện ung thư; tuân theo kế hoạch điều trị; báo tác dụng phụ.',
    ),
    KnowledgeSnippet(
        title='Sức khỏe tâm thần - Phòng ngừa và điều trị',
        keywords=('tâm thần', 'tam than', 'trầm cảm', 'tram cam', 'lo âu', 'lo au', 'stress'),
        content='Các rối loạn tâm thần cần chẩn đoán từ bác sĩ chuyên khoa; kết hợp tư vấn tâm lý, thuốc, hoạt động thể chất.',
        action='Liên hệ bác sĩ tâm thần; tham gia hoạt động xã hội; tập thiền hoặc yoga.',
    ),
    KnowledgeSnippet(
        title='Clopidogrel và Proton Pump Inhibitor',
        keywords=('clopidogrel', 'plavix', 'omeprazole', 'pantoprazole', 'nhồi máu'),
        content='PPI ức chế CYP2C19; làm giảm hiệu quả clopidogrel, tăng nguy cơ nhồi máu nút mạch.',
        action='Chọn H2-blocker thay vì PPI nếu cần; hoặc giãn cách 12-24 giờ.',
    ),
    KnowledgeSnippet(
        title='Digoxin và thuốc làm tăng kali',
        keywords=('digoxin', 'lanoxin', 'tim', 'kali', 'potassium', 'ACE inhibitor'),
        content='Kali cao làm tăng độc tính của digoxin; gây rối loạn nhịp tim nguy hiểm.',
        action='Kiểm tra kali huyết thường xuyên; giám sát nhịp tim; báo tác dụng phụ.',
    ),
    KnowledgeSnippet(
        title='Dabigatran và H2-blocker/PPI',
        keywords=('dabigatran', 'pradaxa', 'chống đông', 'chong dong', 'omeprazole', 'pantoprazole'),
        content='PPI giảm hấp thu dabigatran; H2-blocker cũng có tác động. Có thể cần chuyển sang anticoagulant khác.',
        action='Báo với bác sĩ nếu dùng PPI; có thể cần thay thuốc chống đông.',
    ),
    KnowledgeSnippet(
        title='Quinolone và tất cả các tương tác',
        keywords=('quinolone', 'levofloxacin', 'ciprofloxacin', 'nsaid', 'co giật', 'co giat'),
        content='Quinolone + NSAID tăng nguy cơ co giật; kết hợp với theophylline tăng độc tính.',
        action='Tránh NSAID; báo các thuốc đang dùng; cảnh báo dấu hiệu co giật.',
    ),
    KnowledgeSnippet(
        title='Statin và fibrate',
        keywords=('statin', 'fibrate', 'lipid', 'lipidemia', 'cơ', 'co', 'viêm cơ'),
        content='Kết hợp statin + fibrate tăng nguy cơ rhabdomyolysis (viêm cơ nặng). Cần theo dõi CK huyết.',
        action='Chỉ dùng cùng nếu cần; kiểm tra CK máu; báo yếu cơ, nước tiểu sẫm.',
    ),
    KnowledgeSnippet(
        title='Methotrexate và NSAIDs',
        keywords=('methotrexate', 'nsaid', 'thận', 'than', 'độc tính', 'doc tính'),
        content='NSAIDs giảm thải methotrexate qua thận; tăng độc tính, đặc biệt ở bệnh nhân suy thận.',
        action='Tránh NSAIDs; dùng acetaminophen thay thế; kiểm tra thận.',
    ),
    KnowledgeSnippet(
        title='Phenytoin và tương tác phức tạp (mở rộng)',
        keywords=('phenytoin', 'inducer', 'cyp450', 'warfarin', 'oral contraceptive', 'contraceptive'),
        content='Phenytoin induces CYP3A4, CYP2C9, CYP2C19; làm giảm hiệu quả warfarin, oral contraceptive, thành phần khác.',
        action='Tăng liều warfarin; chuyển sang contraceptive khác; giám sát chặt chẽ.',
    ),
    KnowledgeSnippet(
        title='Amiodarone - ức chế CYP3A4 mạnh',
        keywords=('amiodarone', 'cordarone', 'tim', 'nhịp tim', 'arrhythmia', 'warfarin'),
        content='Amiodarone ức chế CYP3A4 rất mạnh; tương tác với warfarin, digoxin, statins. Cần theo dõi chặt chẽ.',
        action='Kiểm tra INR thường xuyên; cân nhắc giảm liều warfarin; giám sát digoxin.',
    ),
    KnowledgeSnippet(
        title='Antithyroid + Anticoagulant',
        keywords=('antithyroid', 'methimazole', 'warfarin', 'chống đông', 'chong dong', 'thrombus'),
        content='Bệnh Graves/hyperthyroid tăng yêu cầu vitamin K; khi điều trị bằng antithyroid, cần giám sát INR.',
        action='Kiểm tra INR sau 2-3 tuần điều trị antithyroid; điều chỉnh warfarin nếu cần.',
    ),
    KnowledgeSnippet(
        title='Chloroquine/Hydroxychloroquine và tương tác',
        keywords=('chloroquine', 'hydroxychloroquine', 'mắt', 'mat', 'retinopathy', 'tích tụ'),
        content='Chloroquine tích tụ trong mô; có thể gây độc tính mắt; tương tác với digoxin.',
        action='Kiểm tra mắt định kỳ; giám sát digoxin; báo nếu thị lực xấu.',
    ),
    KnowledgeSnippet(
        title='Thiopurine (azathioprine, 6-MP) và Allopurinol',
        keywords=('azathioprine', '6-mercaptopurine', 'allopurinol', 'xanthine oxidase', 'độc tính'),
        content='Allopurinol ức chế xanthine oxidase; nếu dùng với thiopurine, cần giảm liều 50-75% để tránh độc tính.',
        action='Giảm liều thiopurine; kiểm tra toàn bộ máu định kỳ.',
    ),
    KnowledgeSnippet(
        title='ACE inhibitor + Angiotensin Receptor Blocker',
        keywords=('ace inhibitor', 'arb', 'angiotensin receptor', 'kali', 'potassium', 'thận'),
        content='Kết hợp ACE-I + ARB không được khuyến khích; tăng nguy cơ hyperkalemia, suy thận, hạ huyết áp.',
        action='Chọn một trong hai; nếu phải dùng cùng thì giám sát kali, creatinine rất chặt chẽ.',
    ),
    KnowledgeSnippet(
        title='Sulfonylurea + Clarithromycin',
        keywords=('sulfonylurea', 'glibenclamide', 'clarithromycin', 'hạ đường', 'ha duong', 'hypoglycemia'),
        content='Clarithromycin tăng mức sulfonylurea; tăng nguy cơ hạ đường huyết nặng.',
        action='Giám sát glucose chặt chẽ; cân nhắc giảm sulfonylurea; ăn thường xuyên.',
    ),
    KnowledgeSnippet(
        title='Bisphosphonate + Calcium/Iron',
        keywords=('bisphosphonate', 'alendronate', 'risedronate', 'calcium', 'iron', 'hấp thu'),
        content='Calcium, iron, magnesium giảm hấp thu bisphosphonate; cần cách xa 30 phút - 2 giờ.',
        action='Uống bisphosphonate một mình trên bụng không; calcium/iron sau 30 phút.',
    ),
    KnowledgeSnippet(
        title='TNF-alpha inhibitor - lây nhiễm nguy hiểm',
        keywords=('tnf inhibitor', 'infliximab', 'etanercept', 'tuberculosis', 'viêm nhiễm', 'viem nhiem'),
        content='TNF inhibitor làm suy yếu miễn dịch; tăng nguy cơ lao, nhiễm trùng. Cần check tuberculin trước khi dùng.',
        action='Kiểm tra lao (tuberculin test/IGRA) trước dùng; báo ngay nếu ho lâu, sốt.',
    ),
]

def retrieve_snippets(query: str, top_k: int = 3) -> list[KnowledgeSnippet]:
    lowered = query.lower()
    scored = []
    for snippet in EXTENDED_KNOWLEDGE_BASE:
        score = sum(1 for keyword in snippet.keywords if keyword in lowered)
        if score:
            scored.append((score, snippet))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [snippet for _, snippet in scored[:top_k]]
