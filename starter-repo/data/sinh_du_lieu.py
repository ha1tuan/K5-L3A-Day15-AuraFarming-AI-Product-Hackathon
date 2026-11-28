"""Sinh dữ liệu chạy thử cho agent lập kế hoạch du lịch công ty (Track C). Chỉ thư viện chuẩn.

    python data/sinh_du_lieu.py            # ghi data/*.json, seed cố định -> chạy lại ra đúng cùng nội dung
    python data/sinh_du_lieu.py --kiem     # chỉ in thống kê, không ghi file

Phục vụ 2 chiều của bài toán (xem data/tinh_thu.py):
  - nhập ĐỊA ĐIỂM -> dự trù chi phí 3 gói (tiết kiệm · cân bằng · đầy đủ)
  - nhập KINH PHÍ -> gợi ý địa điểm hợp ngân sách và hợp MỤC ĐÍCH (nghỉ dưỡng · gắn kết · cả hai)

Nguồn giá: data/gia_chuan.json (link + ngày xem + độ tin cậy). Video review: data/video_review.json
(lấy bằng data/lay_video_review.py, mỗi link đã kiểm qua oEmbed của YouTube). Cách dựng: data/DATA_CARD.md.
- Điểm đi, điểm đến, điểm tham quan: TÊN THẬT, toạ độ xấp xỉ. Giá vé, giờ mở, ngày đóng: ƯỚC TÍNH.
- Khách sạn, nhà hàng, đơn vị team building: TÊN DỰNG (không phải cơ sở thật), giá sinh quanh giá chuẩn.
- Điểm phù hợp mục đích của từng điểm đến (0–3): nhóm tự đánh giá theo loại cảnh + dịch vụ đoàn, ghi rõ ước tính.
"""
import json
import math
import random
import sys
from pathlib import Path

SEED = 42
THU_MUC = Path(__file__).resolve().parent
GIA = json.loads((THU_MUC / "gia_chuan.json").read_text(encoding="utf-8"))
MUC = ("tiet_kiem", "can_bang", "day_du")
MUC_DICH = ("nghi_duong", "gan_ket")

DIEM_DI = [
    {"id": "HAN", "ten": "Hà Nội", "lat": 21.0285, "lon": 105.8542, "san_bay": "HAN"},
    {"id": "HPH", "ten": "Hải Phòng", "lat": 20.8449, "lon": 106.6881, "san_bay": "HPH"},
    {"id": "DAD", "ten": "Đà Nẵng", "lat": 16.0544, "lon": 108.2022, "san_bay": "DAD"},
    {"id": "SGN", "ten": "TP.HCM", "lat": 10.7769, "lon": 106.7009, "san_bay": "SGN"},
    {"id": "VCA", "ten": "Cần Thơ", "lat": 10.0452, "lon": 105.7469, "san_bay": "VCA"},
]
SAN_BAY = {"HAN": (21.2212, 105.8072), "HPH": (20.8194, 106.7250), "DAD": (16.0439, 108.1994),
           "SGN": (10.8188, 106.6520), "VCA": (10.0851, 105.7117), "VDO": (21.1178, 107.4142),
           "THD": (19.9017, 105.4678), "VII": (18.7376, 105.6708), "VDH": (17.5150, 106.5906),
           "HUI": (16.4015, 107.7026), "UIH": (13.9550, 109.0420), "TBB": (13.0496, 109.3337),
           "CXR": (11.9982, 109.2194), "DLI": (11.7500, 108.3670), "PQC": (10.1698, 103.9931),
           "VCS": (8.7318, 106.6329)}

# id, tên, tỉnh, miền, lat, lon, sân bay gần (bay tới đó rồi đi xe; có thể là sân bay của tỉnh bên), đảo (chỉ bay), phà, loại cảnh,
# nhóm giá, có 5 sao, phù hợp {nghi_duong, gan_ket} 0–3 (nhóm tự đánh giá), mùa đẹp, mô tả
DIEM_DEN_THO = [
    ("halong", "Hạ Long", "Quảng Ninh", "Bắc", 20.9517, 107.0800, "VDO", False, False, ["bien", "vinh"], "bien_trung", True, 3, 3, "4–10", "vịnh di sản, du thuyền, khu vui chơi, resort nhận đoàn lớn"),
    ("catba", "Cát Bà", "Hải Phòng", "Bắc", 20.7270, 107.0480, "HPH", False, True, ["bien", "dao", "rung"], "bien_trung", False, 2, 3, "5–9", "đảo có phà, vịnh Lan Hạ, kayak, rừng quốc gia"),
    ("samson", "Sầm Sơn", "Thanh Hoá", "Bắc", 19.7350, 105.9050, "THD", False, False, ["bien"], "bien_binh_dan", False, 2, 3, "5–8", "biển giá mềm, hải sản, nhiều nhà hàng nhận đoàn đông"),
    ("cualo", "Cửa Lò", "Nghệ An", "Bắc", 18.8160, 105.7200, "VII", False, False, ["bien"], "bien_binh_dan", False, 2, 2, "5–8", "biển bình dân, gần quê Bác, đảo Ngư"),
    ("ninhbinh", "Ninh Bình", "Ninh Bình", "Bắc", 20.2506, 105.9745, "HAN", False, False, ["di_san", "nui"], "di_san_thanh_pho", True, 2, 2, "1–6", "Tràng An, Tam Cốc, Bái Đính; gần Hà Nội, hợp đi 1–2 ngày"),
    ("sapa", "Sa Pa", "Lào Cai", "Bắc", 22.3364, 103.8438, "HAN", False, False, ["nui"], "nui_cao_nguyen", True, 3, 2, "9–5", "núi, Fansipan, bản làng; đường cao tốc từ Hà Nội"),
    ("mocchau", "Mộc Châu", "Sơn La", "Bắc", 20.8480, 104.6300, "HAN", False, False, ["nui", "dong_co"], "nui_cao_nguyen", False, 2, 2, "11–4", "cao nguyên, đồi chè, mùa hoa, cắm trại"),
    ("tamdao", "Tam Đảo", "Vĩnh Phúc", "Bắc", 21.4560, 105.6450, "HAN", False, False, ["nui"], "nui_cao_nguyen", False, 2, 1, "5–9", "thị trấn trên núi gần Hà Nội, mát mùa hè, ít khách sạn lớn"),
    ("bavi", "Ba Vì", "Hà Nội", "Bắc", 21.0750, 105.3700, "HAN", False, False, ["nui", "rung"], "nui_cao_nguyen", False, 2, 3, "quanh năm", "resort sinh thái, sân team building lớn, đi về trong ngày"),
    ("phongnha", "Quảng Bình (Phong Nha)", "Quảng Bình", "Trung", 17.5900, 106.2830, "VDH", False, False, ["hang_dong", "bien"], "di_san_thanh_pho", False, 1, 3, "3–8", "hang động, zipline, mạo hiểm; biển Nhật Lệ"),
    ("hue", "Huế", "Thừa Thiên Huế", "Trung", 16.4637, 107.5909, "HUI", False, False, ["di_san", "thanh_pho"], "di_san_thanh_pho", True, 2, 2, "1–8", "cố đô, lăng tẩm, ca Huế trên sông Hương"),
    ("danang", "Đà Nẵng", "Đà Nẵng", "Trung", 16.0471, 108.2062, "DAD", False, False, ["bien", "thanh_pho", "nui"], "bien_cao_cap", True, 3, 3, "2–8", "biển, Bà Nà, nhiều resort và hội trường cho đoàn lớn"),
    ("hoian", "Hội An", "Quảng Nam", "Trung", 15.8801, 108.3380, "DAD", False, False, ["di_san", "bien"], "bien_cao_cap", True, 3, 2, "2–8", "phố cổ, rừng dừa, Cù Lao Chàm, resort ven biển"),
    ("quynhon", "Quy Nhơn", "Bình Định", "Trung", 13.7765, 109.2237, "UIH", False, False, ["bien"], "bien_trung", True, 3, 3, "3–9", "biển, Kỳ Co - Eo Gió, resort mới"),
    ("phuyen", "Phú Yên (Tuy Hoà)", "Phú Yên", "Trung", 13.0882, 109.3149, "TBB", False, False, ["bien"], "bien_trung", False, 2, 2, "3–8", "biển hoang sơ, Gành Đá Đĩa, ít đông khách"),
    ("nhatrang", "Nha Trang", "Khánh Hoà", "Trung", 12.2388, 109.1967, "CXR", False, False, ["bien", "dao"], "bien_cao_cap", True, 3, 3, "1–8", "biển, tour đảo, khu vui chơi, nhiều resort lớn"),
    ("dalat", "Đà Lạt", "Lâm Đồng", "Trung", 11.9404, 108.4583, "DLI", False, False, ["nui", "thanh_pho"], "nui_cao_nguyen", True, 3, 3, "11–4", "cao nguyên mát, đồi thông, không có biển; đường đèo"),
    ("muine", "Phan Thiết - Mũi Né", "Bình Thuận", "Nam", 10.9333, 108.2870, "SGN", False, False, ["bien", "doi_cat"], "bien_trung", True, 3, 3, "11–4", "đồi cát, resort biển, cao tốc từ TP.HCM"),
    ("vungtau", "Vũng Tàu", "Bà Rịa - Vũng Tàu", "Nam", 10.3460, 107.0843, "SGN", False, False, ["bien", "thanh_pho"], "bien_trung", True, 2, 3, "11–4", "biển gần TP.HCM, đi 2 ngày 1 đêm phổ biến"),
    ("hotram", "Hồ Tràm - Long Hải", "Bà Rịa - Vũng Tàu", "Nam", 10.4800, 107.4000, "SGN", False, False, ["bien", "rung"], "bien_cao_cap", True, 3, 3, "11–4", "resort biển cao cấp, sân team building trên cát"),
    ("phuquoc", "Phú Quốc", "Kiên Giang", "Nam", 10.2270, 103.9670, "PQC", True, False, ["bien", "dao"], "bien_cao_cap", True, 3, 3, "11–4", "đảo; chỉ tính đường bay cho đoàn"),
    ("condao", "Côn Đảo", "Bà Rịa - Vũng Tàu", "Nam", 8.6830, 106.6090, "VCS", True, False, ["bien", "dao", "di_tich"], "bien_cao_cap", True, 3, 1, "3–9", "đảo, di tích nhà tù, lặn biển; chuyến bay ít ghế, khó cho đoàn lớn"),
    ("cantho", "Cần Thơ", "Cần Thơ", "Nam", 10.0452, 105.7469, "VCA", False, False, ["song_nuoc", "thanh_pho"], "di_san_thanh_pho", False, 1, 2, "quanh năm", "chợ nổi, vườn trái cây, sông nước miền Tây"),
    ("tayninh", "Tây Ninh (Núi Bà Đen)", "Tây Ninh", "Nam", 11.3800, 106.1700, "SGN", False, False, ["nui", "tam_linh"], "di_san_thanh_pho", False, 1, 2, "quanh năm", "núi Bà Đen cáp treo, tâm linh; đi về trong ngày từ TP.HCM"),
]

# Điểm tham quan THẬT. (tên, giá/người, phút, mở, đóng, ngày đóng [0=thứ Hai], sức chứa/lượt, mục đích)
# Giá, giờ, ngày đóng: ƯỚC TÍNH. Mục đích: n = nghỉ dưỡng, g = gắn kết.
THAM_QUAN = {
    "halong": [("Du thuyền vịnh Hạ Long (hang Sửng Sốt, đảo Ti Tốp)", 450000, 300, "08:00", "17:00", [], None, "ng"),
               ("Sun World Hạ Long (cáp treo Nữ Hoàng)", 350000, 180, "09:00", "18:00", [], None, "g"),
               ("Bãi Cháy và công viên ven biển", 0, 90, "06:00", "22:00", [], None, "n"),
               ("Chèo kayak vịnh Hạ Long", 200000, 90, "08:00", "16:00", [], 60, "g"),
               ("Bảo tàng Quảng Ninh", 40000, 90, "08:00", "17:00", [0], None, "n")],
    "catba": [("Tour vịnh Lan Hạ và chèo kayak", 400000, 300, "08:00", "16:30", [], 80, "g"),
              ("Vườn quốc gia Cát Bà (leo núi Ngự Lâm)", 80000, 180, "07:00", "17:00", [], None, "g"),
              ("Pháo đài Thần Công", 40000, 75, "07:00", "17:00", [], None, "n"),
              ("Bãi tắm Cát Cò", 0, 120, "06:00", "19:00", [], None, "n")],
    "samson": [("Bãi biển Sầm Sơn", 0, 150, "05:00", "21:00", [], None, "n"),
               ("Đền Độc Cước và Hòn Trống Mái", 0, 90, "06:00", "18:00", [], None, "n"),
               ("Quảng trường biển Sầm Sơn (buổi tối)", 0, 90, "17:00", "22:00", [], None, "ng"),
               ("Chợ hải sản Sầm Sơn", 0, 60, "05:00", "11:00", [], None, "n")],
    "cualo": [("Bãi biển Cửa Lò", 0, 150, "05:00", "21:00", [], None, "n"),
              ("Cano ra đảo Ngư", 150000, 150, "07:00", "16:00", [], 60, "g"),
              ("Khu di tích Kim Liên", 0, 90, "07:00", "17:00", [], None, "n"),
              ("Đảo Lan Châu", 0, 60, "06:00", "18:00", [], None, "n")],
    "ninhbinh": [("Quần thể Tràng An (đi đò)", 250000, 180, "07:00", "16:30", [], None, "n"),
                 ("Chùa Bái Đính", 0, 120, "06:00", "18:00", [], None, "n"),
                 ("Hang Múa (leo 500 bậc)", 100000, 90, "06:00", "19:00", [], None, "g"),
                 ("Tam Cốc - Bích Động", 150000, 150, "07:00", "17:00", [], None, "n"),
                 ("Cố đô Hoa Lư", 20000, 75, "07:00", "17:00", [], None, "n")],
    "sapa": [("Fansipan Legend (cáp treo)", 800000, 300, "07:30", "17:00", [], None, "ng"),
             ("Bản Cát Cát", 90000, 120, "07:00", "18:00", [], None, "n"),
             ("Núi Hàm Rồng", 70000, 120, "06:00", "18:00", [], None, "g"),
             ("Thung lũng Mường Hoa (trekking)", 0, 180, "07:00", "16:00", [], None, "g")],
    "mocchau": [("Đồi chè trái tim", 20000, 90, "06:00", "18:00", [], None, "n"),
                ("Thác Dải Yếm", 20000, 90, "07:00", "17:00", [], None, "n"),
                ("Cầu kính Bạch Long", 300000, 120, "07:30", "17:30", [], None, "g"),
                ("Rừng thông Bản Áng (cắm trại)", 20000, 180, "06:00", "21:00", [], None, "g")],
    "tamdao": [("Thị trấn Tam Đảo và nhà thờ đá", 0, 90, "06:00", "22:00", [], None, "n"),
               ("Thác Bạc", 20000, 90, "06:00", "18:00", [], None, "n"),
               ("Cổng trời Tam Đảo", 0, 60, "06:00", "18:00", [], None, "n"),
               ("Đền Bà Chúa Thượng Ngàn", 0, 90, "06:00", "18:00", [], None, "n")],
    "bavi": [("Vườn quốc gia Ba Vì (đền Thượng)", 60000, 180, "07:00", "17:00", [], None, "ng"),
             ("Khu du lịch Ao Vua (công viên nước)", 150000, 180, "08:00", "17:00", [], None, "g"),
             ("Khu du lịch Thác Đa", 120000, 150, "08:00", "17:00", [], None, "g"),
             ("Hồ Suối Hai", 0, 90, "06:00", "18:00", [], None, "n")],
    "phongnha": [("Động Phong Nha (đi thuyền)", 150000, 150, "07:00", "16:00", [], None, "n"),
                 ("Động Thiên Đường", 250000, 150, "07:00", "16:30", [], None, "n"),
                 ("Sông Chày - Hang Tối (zipline, tắm bùn)", 450000, 240, "08:00", "16:00", [], 100, "g"),
                 ("Bãi biển Nhật Lệ", 0, 120, "05:00", "20:00", [], None, "n")],
    "hue": [("Đại Nội Huế", 200000, 180, "07:00", "17:30", [], None, "n"),
            ("Lăng Khải Định", 150000, 75, "07:00", "17:30", [], None, "n"),
            ("Lăng Tự Đức", 150000, 90, "07:00", "17:30", [], None, "n"),
            ("Chùa Thiên Mụ", 0, 60, "06:00", "18:00", [], None, "n"),
            ("Nghe ca Huế trên thuyền rồng sông Hương", 150000, 75, "19:00", "21:30", [], 80, "ng")],
    "danang": [("Sun World Bà Nà Hills", 950000, 360, "08:00", "17:00", [], None, "ng"),
               ("Ngũ Hành Sơn", 40000, 90, "07:00", "17:30", [], None, "n"),
               ("Bán đảo Sơn Trà và chùa Linh Ứng", 0, 120, "06:00", "18:00", [], None, "n"),
               ("Biển Mỹ Khê", 0, 120, "05:00", "21:00", [], None, "n"),
               ("Bảo tàng Điêu khắc Chăm", 60000, 75, "08:00", "17:00", [], None, "n")],
    "hoian": [("Phố cổ Hội An", 120000, 180, "08:00", "22:00", [], None, "n"),
              ("Rừng dừa Bảy Mẫu (thuyền thúng)", 150000, 90, "07:00", "17:00", [], None, "g"),
              ("Cù Lao Chàm (cano, lặn ngắm san hô)", 650000, 360, "08:00", "15:00", [], 100, "g"),
              ("VinWonders Nam Hội An", 600000, 300, "09:00", "19:00", [], None, "g"),
              ("Biển An Bàng", 0, 120, "05:00", "20:00", [], None, "n")],
    "quynhon": [("Kỳ Co - Eo Gió (cano)", 550000, 300, "07:00", "15:00", [], 100, "ng"),
                ("Ghềnh Ráng Tiên Sa", 20000, 75, "07:00", "17:00", [], None, "n"),
                ("Tháp Đôi", 20000, 45, "07:00", "17:00", [], None, "n"),
                ("Biển Quy Nhơn", 0, 120, "05:00", "21:00", [], None, "n")],
    "phuyen": [("Gành Đá Đĩa", 20000, 75, "07:00", "17:00", [], None, "n"),
               ("Mũi Điện (hải đăng Đại Lãnh)", 20000, 120, "05:00", "17:00", [], None, "g"),
               ("Bãi Xép", 0, 90, "06:00", "18:00", [], None, "n"),
               ("Tháp Nhạn", 0, 45, "07:00", "17:00", [], None, "n")],
    "nhatrang": [("VinWonders Nha Trang", 880000, 360, "08:30", "20:00", [], None, "g"),
                 ("Tour 3 đảo bằng cano (Hòn Mun, Hòn Tằm)", 400000, 300, "08:00", "15:30", [], 120, "ng"),
                 ("Tháp Bà Ponagar", 30000, 60, "06:00", "17:30", [], None, "n"),
                 ("Tắm bùn khoáng nóng", 300000, 150, "07:00", "18:00", [], 150, "n")],
    "dalat": [("Hồ Xuân Hương và chợ Đà Lạt", 0, 90, "05:00", "22:00", [], None, "n"),
              ("Khu du lịch Langbiang (xe jeep lên đỉnh)", 250000, 180, "07:00", "17:00", [], None, "g"),
              ("Thung lũng Tình Yêu", 250000, 120, "07:00", "17:00", [], None, "n"),
              ("Đồi chè Cầu Đất", 0, 120, "07:00", "17:00", [], None, "n"),
              ("Ga Đà Lạt (tàu cổ đi Trại Mát)", 150000, 90, "07:45", "16:00", [], 80, "n")],
    "muine": [("Đồi cát bay Mũi Né (xe địa hình)", 400000, 120, "05:00", "18:00", [], None, "g"),
              ("Bàu Trắng", 20000, 120, "05:00", "18:00", [], None, "ng"),
              ("Suối Tiên", 15000, 75, "06:00", "18:00", [], None, "n"),
              ("Làng chài Mũi Né", 0, 60, "05:00", "09:00", [], None, "n"),
              ("Tháp Chăm Poshanư", 20000, 45, "07:00", "17:00", [], None, "n")],
    "vungtau": [("Tượng Chúa Kitô Vua", 0, 90, "07:00", "17:00", [], None, "g"),
                ("Hải đăng Vũng Tàu", 10000, 60, "07:00", "17:00", [], None, "n"),
                ("Bãi Sau", 0, 150, "05:00", "21:00", [], None, "n"),
                ("Hồ Mây Park (cáp treo)", 400000, 240, "08:00", "18:00", [], None, "g"),
                ("Bạch Dinh", 15000, 60, "07:00", "17:00", [], None, "n")],
    "hotram": [("Biển Hồ Tràm", 0, 150, "05:00", "20:00", [], None, "n"),
               ("Suối nước nóng Bình Châu", 300000, 180, "07:00", "21:00", [], None, "n"),
               ("Khu bảo tồn Bình Châu - Phước Bửu", 50000, 120, "07:00", "17:00", [], None, "g"),
               ("Biển Long Hải", 0, 120, "05:00", "20:00", [], None, "n")],
    "phuquoc": [("VinWonders Phú Quốc", 950000, 360, "09:00", "19:00", [], None, "g"),
                ("Cáp treo Hòn Thơm và công viên nước", 650000, 300, "09:00", "17:00", [], None, "g"),
                ("Tour 4 đảo Nam Phú Quốc (cano)", 650000, 360, "08:00", "16:00", [], 100, "ng"),
                ("Chợ đêm Phú Quốc", 0, 90, "17:00", "23:00", [], None, "n"),
                ("Grand World Phú Quốc", 0, 120, "09:00", "23:00", [], None, "n")],
    "condao": [("Di tích nhà tù Côn Đảo", 40000, 150, "07:30", "17:00", [], None, "n"),
               ("Nghĩa trang Hàng Dương (viếng đêm)", 0, 90, "06:00", "23:00", [], None, "n"),
               ("Bãi Đầm Trầu", 0, 150, "06:00", "18:00", [], None, "n"),
               ("Lặn ngắm san hô Hòn Bảy Cạnh", 700000, 300, "08:00", "15:00", [], 40, "g")],
    "cantho": [("Chợ nổi Cái Răng (đi thuyền sớm)", 150000, 150, "05:00", "09:00", [], 120, "n"),
               ("Bến Ninh Kiều và chợ đêm", 0, 90, "17:00", "22:00", [], None, "n"),
               ("Thiền viện Trúc Lâm Phương Nam", 0, 75, "06:00", "18:00", [], None, "n"),
               ("Vườn trái cây Mỹ Khánh (trò chơi dân gian)", 60000, 150, "07:00", "17:00", [], None, "g"),
               ("Nhà cổ Bình Thủy", 20000, 45, "08:00", "17:00", [], None, "n")],
    "tayninh": [("Sun World Núi Bà Đen (cáp treo)", 450000, 240, "06:00", "18:00", [], None, "ng"),
                ("Toà Thánh Cao Đài", 0, 75, "06:00", "18:00", [], None, "n"),
                ("Hồ Dầu Tiếng", 0, 120, "06:00", "18:00", [], None, "g")],
}

TEN_KS = ["Hải Âu", "Sao Biển", "Ngọc Lan", "Phương Nam", "Bình Minh", "Hoàng Gia", "Thiên Hà", "Hướng Dương",
          "Đông Á", "Mai Vàng", "Lan Anh", "Trường Sơn", "Vạn Xuân", "An Bình", "Tân Cảng", "Hồng Hạc",
          "Bạch Đằng", "Thanh Bình", "Cẩm Tú", "Phú Gia", "Sông Hồng", "Ánh Dương", "Ngân Hà", "Đại Dương"]
TEN_NH = ["Hải sản Biển Xanh", "Nhà hàng Đoàn Viên", "Bếp Quê", "Hải sản Ngư Phủ", "Nhà hàng Gió Biển",
          "Phố Ẩm Thực", "Nhà hàng Đồng Quê", "Nhà hàng Hoa Sen", "Buffet Đại Dương", "Nhà hàng Thuyền Rồng",
          "Nhà hàng Mộc", "Bếp Nhà Làng", "Nhà hàng Phù Sa", "Nhà hàng Hội Ngộ"]
HE_SO_AN = {"bien_cao_cap": 1.15, "bien_trung": 1.0, "bien_binh_dan": 0.9, "nui_cao_nguyen": 0.95,
            "di_san_thanh_pho": 0.95}
SAO_THEO_MUC = {"tiet_kiem": [2, 3, 3, 3], "can_bang": [4, 4, 4, 4], "day_du": [5, 5, 5, 5]}


def km_chim_bay(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(h))


def lam_tron(x, buoc=10000):
    return int(round(x / buoc) * buoc)


def diem_den():
    out = []
    for (i, ten, tinh, mien, lat, lon, sb, dao, pha, canh, nhom, co5, nd, gk, mua, mo_ta) in DIEM_DEN_THO:
        out.append({"id": i, "ten": ten, "tinh": tinh, "mien": mien, "lat": lat, "lon": lon, "san_bay": sb,
                    "dao_chi_duong_bay": dao, "co_pha": pha, "loai_canh": canh, "nhom_gia": nhom,
                    "co_khach_san_5_sao": co5, "phu_hop": {"nghi_duong": nd, "gan_ket": gk},
                    "phu_hop_uoc_tinh": True, "mua_dep_thang": mua, "mo_ta": mo_ta})
    return out


def gia_ve(a, b, km):
    ve = GIA["ve_may_bay_mot_chieu_pho_thong"]
    for m in ve["moc"]:
        x, y = m["chang"].split("-")
        if {x, y} == {a, b} and "khoang" in m:
            return lam_tron(sum(m["khoang"]) / 2), False, m["nguon"]
    return lam_tron(ve["phi_co_dinh"] + ve["phi_moi_km"] * km), True, None


def di_chuyen(dd):
    tx = GIA["thue_xe_co_tai_xe"]
    cho = {"xe_16_cho": 15, "xe_29_cho": 28, "xe_45_cho": 44, "limousine_18_cho": 17}
    xe = [{"loai": k, "so_cho": cho[k], "don_gia_km": v, "uoc_tinh": True} for k, v in tx["don_gia_km"].items()]
    tuyen = []
    for di in DIEM_DI:
        for d in dd:
            km_bo = None if d["dao_chi_duong_bay"] else round(km_chim_bay((di["lat"], di["lon"]), (d["lat"], d["lon"])) * 1.3)
            cung_noi = km_bo is not None and km_bo < 25
            if cung_noi:
                km_bo = 0
            gio_bo = None if km_bo is None else round(km_bo / 50 + (km_bo / 50 // 3) * 0.5 + (1.0 if d["co_pha"] else 0), 1)
            bay = None
            if d["san_bay"] and not cung_noi and d["san_bay"] != di["san_bay"]:
                km_bay = round(km_chim_bay(SAN_BAY[di["san_bay"]], SAN_BAY[d["san_bay"]]))
                if km_bay >= (50 if d["dao_chi_duong_bay"] else 250):   # đảo: chặng ngắn vẫn phải bay
                    gia, uoc, nguon = gia_ve(di["san_bay"], d["san_bay"], km_bay)
                    km_sb = round(km_chim_bay(SAN_BAY[d["san_bay"]], (d["lat"], d["lon"])) * 1.3)
                    bay = {"chang": f'{di["san_bay"]}-{d["san_bay"]}', "km": km_bay, "gio_bay": round(km_bay / 700 + 0.3, 1),
                           "gio_thu_tuc": 2.0, "km_san_bay_toi_diem_den": km_sb, "gia_ve_mot_chieu": gia,
                           "uoc_tinh": uoc, "nguon": nguon}
            tuyen.append({"tu": di["id"], "den": d["id"], "duong_bo_km": km_bo, "duong_bo_gio": gio_bo,
                          "co_pha": d["co_pha"], "duong_bay": bay,
                          "ghi_chu": "cùng nơi: chỉ di chuyển nội vùng" if cung_noi else
                                     ("đảo: chỉ đường bay" if d["dao_chi_duong_bay"] else
                                      ("có đoạn phà" if d["co_pha"] else ""))})
    return {"_mo_ta": "Chặng đi/về. Đường bộ = chim bay × 1,3; xe 50 km/h + 30 phút nghỉ mỗi 3 giờ; phà +1 giờ. "
                      "Đường bay 700 km/h + 0,3 giờ; thủ tục 2 giờ; đưa đón sân bay theo km_san_bay_toi_diem_den. "
                      "Cặp sân bay không kiểm có chuyến bay thẳng hay không (giới hạn, xem DATA_CARD).",
            "xe": xe, "phi_luu_dem_tai_xe": tx["phi_luu_dem_tai_xe"], "km_toi_thieu_moi_ngay": tx["km_toi_thieu_moi_ngay"],
            "km_noi_vung_moi_ngay": 60, "phi_pha_nguoi_luot": GIA["hoat_dong"]["phi_pha_nguoi"], "tuyen": tuyen}


def khach_san(rd, dd):
    gp = GIA["phong_khach_san"]
    out, n = [], 0
    for d in dd:
        goc = gp["gia_goc_phong_doi_theo_nhom"][d["nhom_gia"]]
        bien = "bien" in d["loai_canh"]
        for muc in MUC:
            for k, sao in enumerate(SAO_THEO_MUC[muc]):
                if sao == 5 and not d["co_khach_san_5_sao"]:
                    sao = 4                                        # chỗ khó: nơi không có 5 sao -> gói đầy đủ dùng 4 sao tốt nhất
                n += 1
                gia_doi = lam_tron(goc[str(sao)] * rd.uniform(0.85, 1.2) * (1.15 if muc == "day_du" and sao == 4 else 1))
                lp = [{"suc_chua": s, "gia_dem": lam_tron(gia_doi * gp["he_so_phong"][str(s)]),
                       "so_luong": rd.choice([10, 20, 30, 40, 60, 80, 120])} for s in (2, 3, 4)]
                if k == 1:
                    lp = [p for p in lp if p["suc_chua"] != 4]              # chỗ khó: không có phòng 4 người
                if k == 2:
                    for p in lp:
                        p["so_luong"] = max(3, p["so_luong"] // 6)          # chỗ khó: khách sạn nhỏ
                resort = sao >= 4 and (bien or "rung" in d["loai_canh"] or "nui" in d["loai_canh"]) and k != 2
                tien_ich = {
                    "ho_boi": sao >= 4 or (sao == 3 and rd.random() < 0.3),
                    "bai_bien_rieng": resort and bien and rd.random() < 0.7,
                    "spa": sao >= 4 and rd.random() < 0.8,
                    "khuon_vien_team_building_nguoi": (rd.choice([150, 300, 500]) if resort else
                                                       (rd.choice([0, 0, 60]) if sao <= 3 else rd.choice([0, 80, 150]))),
                    "hoi_truong_cho": (rd.choice([200, 300, 500]) if sao >= 4 and k != 2 else rd.choice([0, 0, 80])),
                }
                diem_nd = sum([tien_ich["ho_boi"], tien_ich["bai_bien_rieng"], tien_ich["spa"], resort])
                diem_gk = sum([tien_ich["khuon_vien_team_building_nguoi"] >= 150, tien_ich["hoi_truong_cho"] >= 200,
                               tien_ich["khuon_vien_team_building_nguoi"] >= 300, resort])
                out.append({"id": f"KS{n:03d}",
                            "ten": f'{"Resort" if resort else "Khách sạn"} {TEN_KS[(n * 7) % len(TEN_KS)]} {d["ten"]} (tên dựng)',
                            "diem_den": d["id"], "muc": muc, "hang_sao": sao, "loai": "resort" if resort else "khach_san",
                            "loai_phong": lp, "tong_phong": sum(p["so_luong"] for p in lp),
                            "suc_chua_toi_da": sum(p["so_luong"] * p["suc_chua"] for p in lp),
                            "tien_ich": tien_ich, "phu_hop": {"nghi_duong": diem_nd, "gan_ket": diem_gk},
                            "gom_bua_sang": True, "uoc_tinh": True, "ten_dung": True})
    return out


def nha_hang(rd, dd):
    gia = GIA["an_uong"]["theo_muc"]
    out, n = [], 0
    for d in dd:
        for muc in MUC:
            suc = [rd.choice([200, 300, 400, 600]), rd.choice([100, 150, 200]), rd.choice([60, 80]), 25]
            for k in range(4):
                n += 1
                out.append({"id": f"NH{n:03d}", "ten": f'{TEN_NH[(n * 3) % len(TEN_NH)]} {d["ten"]} (tên dựng)',
                            "diem_den": d["id"], "muc": muc, "suc_chua": suc[k],
                            "gia_nguoi_bua": lam_tron(gia[muc] * HE_SO_AN[d["nhom_gia"]] * rd.uniform(0.85, 1.15), 5000),
                            "gio_mo": "11:00" if k == 3 else "10:00", "gio_dong": "14:00" if k == 3 else "22:00",
                            "nhan_doan": suc[k] >= 60, "uoc_tinh": True, "ten_dung": True})
    return out


def hoat_dong(dd):
    hd = GIA["hoat_dong"]
    out, n = [], 0
    for d in dd:
        he = HE_SO_AN[d["nhom_gia"]]
        for ten, gia, phut, mo, dong, ngay_dong, suc, md in THAM_QUAN[d["id"]]:
            n += 1
            out.append({"id": f"HD{n:03d}", "ten": ten, "diem_den": d["id"], "loai": "tham_quan",
                        "muc_dich": [x for x, c in (("nghi_duong", "n"), ("gan_ket", "g")) if c in md],
                        "muc": list(MUC), "gia_nguoi": gia, "thoi_luong_phut": phut, "gio_mo": mo, "gio_dong": dong,
                        "ngay_dong_cua": ngay_dong, "suc_chua": suc, "uoc_tinh": True, "ten_dung": False})
        dich_vu = [("team_building", "Team building ngoài trời (đơn vị tổ chức, tên dựng)", 180, "07:00", "17:30", ["gan_ket"], ("can_bang", "day_du")),
                   ("gala_dinner", "Gala dinner có sân khấu, âm thanh, MC (tên dựng)", 180, "18:00", "22:00", ["gan_ket"], ("can_bang", "day_du")),
                   ("spa_thu_gian", "Spa, massage thư giãn (tên dựng)", 90, "09:00", "21:00", ["nghi_duong"], MUC),
                   ("bbq_tiec_ngoai_troi", "Tiệc BBQ ngoài trời cho đoàn (tên dựng)", 150, "17:30", "21:30", ["nghi_duong", "gan_ket"], MUC)]
        for loai, ten, phut, mo, dong, md, cac_muc in dich_vu:
            for muc in cac_muc:
                n += 1
                out.append({"id": f"HD{n:03d}", "ten": f"{ten} - {d['ten']} ({muc})", "diem_den": d["id"], "loai": loai,
                            "muc_dich": md, "muc": [muc], "gia_nguoi": lam_tron(hd[loai][muc] * he, 5000),
                            "thoi_luong_phut": phut, "gio_mo": mo, "gio_dong": dong, "ngay_dong_cua": [],
                            "suc_chua": None, "uoc_tinh": True, "ten_dung": True})
        n += 1
        out.append({"id": f"HD{n:03d}", "ten": f"Tự do nghỉ ngơi tại nơi ở - {d['ten']}", "diem_den": d["id"],
                    "loai": "tu_do", "muc_dich": ["nghi_duong"], "muc": list(MUC), "gia_nguoi": 0,
                    "thoi_luong_phut": 180, "gio_mo": "07:00", "gio_dong": "22:00", "ngay_dong_cua": [],
                    "suc_chua": None, "uoc_tinh": False, "ten_dung": False})
    return out


def muc_goi():
    return {"_mo_ta": "Quy tắc 3 gói. Cùng khung lịch; khác nhau ở MỨC của từng hạng mục. Mục đích quyết định hoạt động.",
            "goi": {
                "tiet_kiem": {"ten": "Tiết kiệm", "hang_sao": [2, 3], "xe": "xe_45_cho", "muc_an": "tiet_kiem",
                              "may_bay_khi_duong_bo_tren_gio": 12},
                "can_bang": {"ten": "Cân bằng", "hang_sao": [4], "xe": "xe_29_cho", "muc_an": "can_bang",
                             "may_bay_khi_duong_bo_tren_gio": 9},
                "day_du": {"ten": "Đầy đủ", "hang_sao": [5], "xe": "limousine_18_cho", "muc_an": "day_du",
                           "may_bay_khi_duong_bo_tren_gio": 6}},
            "hoat_dong_theo_muc_dich": {
                "nghi_duong": {"tiet_kiem": ["tham_quan", "tu_do"], "can_bang": ["tham_quan", "spa_thu_gian", "tu_do"],
                               "day_du": ["tham_quan", "spa_thu_gian", "bbq_tiec_ngoai_troi", "tu_do"]},
                "gan_ket": {"tiet_kiem": ["tham_quan", "bbq_tiec_ngoai_troi"], "can_bang": ["tham_quan", "team_building", "gala_dinner"],
                            "day_du": ["tham_quan", "team_building", "gala_dinner"]},
                "ca_hai": {"tiet_kiem": ["tham_quan", "bbq_tiec_ngoai_troi", "tu_do"],
                           "can_bang": ["tham_quan", "team_building", "gala_dinner", "tu_do"],
                           "day_du": ["tham_quan", "team_building", "gala_dinner", "spa_thu_gian"]}},
            "phat_sinh_ty_le": GIA["phat_sinh_ty_le"],
            "khung_gio": {"bat_dau_ngay": "07:00", "an_trua": ["11:30", "13:30"], "an_toi": ["18:00", "20:00"],
                          "ket_thuc_muon_nhat": "22:00", "thoi_luong_bua_phut": 75},
            "gioi_han": {"so_nguoi": [5, 500], "so_ngay": [1, 7]}}


def main():
    rd = random.Random(SEED)
    dd = diem_den()
    ks, nh, hd = khach_san(rd, dd), nha_hang(rd, dd), hoat_dong(dd)
    tep = {"diem_den.json": {"seed": SEED, "diem_di": DIEM_DI, "diem_den": dd}, "di_chuyen.json": di_chuyen(dd),
           "khach_san.json": ks, "nha_hang.json": nh, "hoat_dong.json": hd, "muc_goi.json": muc_goi()}
    if "--kiem" not in sys.argv:
        for ten, nd in tep.items():
            (THU_MUC / ten).write_text(json.dumps(nd, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"seed {SEED} · điểm đi {len(DIEM_DI)} · điểm đến {len(dd)} · tuyến {len(tep['di_chuyen.json']['tuyen'])} · "
          f"khách sạn {len(ks)} · nhà hàng {len(nh)} · hoạt động {len(hd)} "
          f"(tham quan thật {sum(h['loai'] == 'tham_quan' for h in hd)})")


if __name__ == "__main__":
    main()
