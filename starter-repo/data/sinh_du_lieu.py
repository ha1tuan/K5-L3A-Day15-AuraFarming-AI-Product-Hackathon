"""Sinh dữ liệu chạy thử cho agent lập kế hoạch du lịch công ty (Track C). Chỉ thư viện chuẩn.

    python data/sinh_du_lieu.py            # ghi data/*.json, seed cố định -> chạy lại ra đúng cùng nội dung
    python data/sinh_du_lieu.py --kiem     # chỉ in bảng kiểm, không ghi file

Nguồn giá: data/gia_chuan.json (mỗi số có link + ngày xem + độ tin cậy). Cách sinh: data/DATA_CARD.md.
- Điểm đi / điểm đến / điểm tham quan: tên thật, toạ độ xấp xỉ (thông tin công khai).
- Khách sạn, nhà hàng: TÊN DỰNG (không phải cơ sở thật), giá sinh quanh giá chuẩn theo hạng sao / mức gói.
- Cài sẵn chỗ khó cho bộ câu thử: khách sạn ít phòng, thiếu phòng 4 người, quán nhỏ hơn đoàn,
  điểm tham quan đóng cửa thứ Hai, Phú Quốc chỉ đi máy bay, khung giờ mở cửa hẹp.
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

# ------------------------------------------------------------------ điểm đi, điểm đến (thông tin công khai)
DIEM_DI = [
    {"id": "HAN", "ten": "Hà Nội", "lat": 21.0285, "lon": 105.8542, "san_bay": "HAN"},
    {"id": "DAD", "ten": "Đà Nẵng", "lat": 16.0544, "lon": 108.2022, "san_bay": "DAD"},
    {"id": "SGN", "ten": "TP.HCM", "lat": 10.7769, "lon": 106.7009, "san_bay": "SGN"},
]
DIEM_DEN = [
    {"id": "halong", "ten": "Hạ Long", "tinh": "Quảng Ninh", "lat": 20.9517, "lon": 107.0800, "san_bay": "VDO",
     "dao": False, "mua_dep": "4–10", "mo_ta": "vịnh di sản, du thuyền, khu vui chơi; gần Hà Nội"},
    {"id": "samson", "ten": "Sầm Sơn", "tinh": "Thanh Hoá", "lat": 19.7350, "lon": 105.9050, "san_bay": "THD",
     "dao": False, "mua_dep": "5–8", "mo_ta": "biển giá mềm, nhiều nhà hàng hải sản nhận đoàn đông; ít khách sạn 5 sao"},
    {"id": "danang", "ten": "Đà Nẵng - Hội An", "tinh": "Đà Nẵng, Quảng Nam", "lat": 16.0471, "lon": 108.2062,
     "san_bay": "DAD", "dao": False, "mua_dep": "2–8", "mo_ta": "biển, Bà Nà, phố cổ Hội An; nhiều resort nhận đoàn"},
    {"id": "nhatrang", "ten": "Nha Trang", "tinh": "Khánh Hoà", "lat": 12.2388, "lon": 109.1967, "san_bay": "CXR",
     "dao": False, "mua_dep": "1–8", "mo_ta": "biển, tour đảo, khu vui chơi"},
    {"id": "dalat", "ten": "Đà Lạt", "tinh": "Lâm Đồng", "lat": 11.9404, "lon": 108.4583, "san_bay": "DLI",
     "dao": False, "mua_dep": "11–4", "mo_ta": "cao nguyên mát, cảnh đồi thông; không có biển; đường đèo"},
    {"id": "phuquoc", "ten": "Phú Quốc", "tinh": "Kiên Giang", "lat": 10.2270, "lon": 103.9670, "san_bay": "PQC",
     "dao": True, "mua_dep": "11–4", "mo_ta": "đảo; chỉ tính đường bay (không tính phà cho đoàn)"},
]
SAN_BAY = {"HAN": (21.2212, 105.8072), "DAD": (16.0439, 108.1994), "SGN": (10.8188, 106.6520),
           "VDO": (21.1178, 107.4142), "THD": (19.9017, 105.4678), "CXR": (11.9982, 109.2194),
           "DLI": (11.7500, 108.3670), "PQC": (10.1698, 103.9931)}

# Điểm tham quan thật (tên công khai). Giá, giờ: ƯỚC TÍNH, nhãn uoc_tinh. ngay_dong: 0 = thứ Hai.
THAM_QUAN = {
    "halong": [("Du thuyền vịnh Hạ Long (tuyến hang Sửng Sốt, Ti Tốp)", 450000, 300, "08:00", "17:00", [], None),
               ("Sun World Hạ Long (cáp treo Nữ Hoàng)", 350000, 180, "09:00", "18:00", [], None),
               ("Bãi Cháy và công viên ven biển", 0, 90, "06:00", "22:00", [], None),
               ("Bảo tàng Quảng Ninh", 40000, 90, "08:00", "17:00", [0], None)],
    "samson": [("Bãi biển Sầm Sơn (tắm biển tự do)", 0, 150, "05:00", "21:00", [], None),
               ("Đền Độc Cước và Hòn Trống Mái", 0, 90, "06:00", "18:00", [], None),
               ("Khu du lịch sinh thái Sun World Sầm Sơn", 200000, 150, "15:00", "22:00", [0], None),
               ("Chợ hải sản Sầm Sơn", 0, 60, "05:00", "11:00", [], None)],
    "danang": [("Sun World Bà Nà Hills", 950000, 360, "08:00", "17:00", [], None),
               ("Phố cổ Hội An (vé tham quan)", 120000, 180, "08:00", "22:00", [], None),
               ("Ngũ Hành Sơn", 40000, 90, "07:00", "17:30", [], None),
               ("Bán đảo Sơn Trà và chùa Linh Ứng", 0, 120, "06:00", "18:00", [], None),
               ("Bảo tàng Điêu khắc Chăm", 60000, 75, "08:00", "17:00", [0], None)],
    "nhatrang": [("VinWonders Nha Trang", 880000, 360, "08:30", "20:00", [], None),
                 ("Tour 3 đảo bằng ca nô (Hòn Mun, Hòn Tằm)", 400000, 300, "08:00", "15:30", [], 120),
                 ("Tháp Bà Ponagar", 30000, 60, "06:00", "17:30", [], None),
                 ("Tắm bùn khoáng (khu du lịch)", 300000, 150, "07:00", "18:00", [], 150)],
    "dalat": [("Hồ Xuân Hương và chợ Đà Lạt", 0, 90, "05:00", "22:00", [], None),
              ("Khu du lịch Langbiang (xe jeep lên đỉnh)", 250000, 180, "07:00", "17:00", [], None),
              ("Thung lũng Tình Yêu", 250000, 120, "07:00", "17:00", [], None),
              ("Đồi chè Cầu Đất", 0, 120, "07:00", "17:00", [], None),
              ("Ga Đà Lạt (tàu cổ đi Trại Mát)", 150000, 90, "07:45", "16:00", [], 80)],
    "phuquoc": [("VinWonders Phú Quốc", 950000, 360, "09:00", "19:00", [], None),
                ("Cáp treo Hòn Thơm và công viên nước", 650000, 300, "09:00", "17:00", [], None),
                ("Tour 4 đảo Nam Phú Quốc (cano)", 650000, 360, "08:00", "16:00", [], 100),
                ("Chợ đêm Dinh Cậu", 0, 90, "17:00", "23:00", [], None),
                ("Grand World Phú Quốc", 0, 120, "09:00", "23:00", [], None)],
}

TEN_KS = ["Hải Âu", "Sao Biển", "Ngọc Lan", "Phương Nam", "Bình Minh", "Hoàng Gia", "Thiên Hà", "Hướng Dương",
          "Đông Á", "Mai Vàng", "Lan Anh", "Trường Sơn", "Vạn Xuân", "An Bình", "Tân Cảng", "Hồng Hạc"]
TEN_NH = ["Hải sản Biển Xanh", "Nhà hàng Đoàn Viên", "Bếp Quê", "Hải sản Ngư Phủ", "Nhà hàng Gió Biển",
          "Phố Ẩm Thực", "Nhà hàng Đồng Quê", "Nhà hàng Hoa Sen", "Buffet Đại Dương", "Nhà hàng Thuyền Rồng"]
HE_SO_DIEM = {"halong": 1.05, "samson": 0.9, "danang": 1.05, "nhatrang": 1.0, "dalat": 0.95, "phuquoc": 1.15}
SAO_THEO_MUC = {"tiet_kiem": [2, 3, 3], "can_bang": [4, 4, 4], "day_du": [5, 5, 5]}


def km_chim_bay(a, b):
    r = 6371.0
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def lam_tron(x, buoc=10000):
    return int(round(x / buoc) * buoc)


def gia_ve(di, den_sb, km_bay):
    """Vé một chiều phổ thông / người: dùng mốc có nguồn nếu có, không thì công thức ước tính."""
    ve = GIA["ve_may_bay_mot_chieu_pho_thong"]
    for m in ve["moc"]:
        a, b = m["chang"].split("-")
        if {a, b} == {di, den_sb} and "khoang" in m:
            return lam_tron(sum(m["khoang"]) / 2), False, m["nguon"]
    return lam_tron(ve["phi_co_dinh"] + ve["phi_moi_km"] * km_bay), True, None


def sinh_di_chuyen():
    tx = GIA["thue_xe_co_tai_xe"]
    xe = [{"loai": k, "so_cho": {"xe_16_cho": 15, "xe_29_cho": 28, "xe_45_cho": 44, "limousine_18_cho": 17}[k],
           "don_gia_km": v, "uoc_tinh": True} for k, v in tx["don_gia_km"].items()]
    tuyen = []
    for di in DIEM_DI:
        for den in DIEM_DEN:
            cung_noi = di["san_bay"] == den["san_bay"]
            km_bo = None if den["dao"] else round(km_chim_bay((di["lat"], di["lon"]), (den["lat"], den["lon"])) * 1.3)
            if cung_noi:
                km_bo = 0
            gio_bo = None if km_bo is None else round(km_bo / 50 + (km_bo / 50 // 3) * 0.5, 1)
            km_bay = round(km_chim_bay(SAN_BAY[di["san_bay"]], SAN_BAY[den["san_bay"]]))
            bay = None
            if not cung_noi and km_bay >= 250:
                gia, uoc, nguon = gia_ve(di["san_bay"], den["san_bay"], km_bay)
                bay = {"chang": f'{di["san_bay"]}-{den["san_bay"]}', "km": km_bay,
                       "gio_bay": round(km_bay / 700 + 0.3, 1), "gio_thu_tuc_dua_don": 2.5,
                       "gia_ve_mot_chieu": gia, "uoc_tinh": uoc, "nguon": nguon}
            tuyen.append({"tu": di["id"], "den": den["id"], "duong_bo_km": km_bo, "duong_bo_gio": gio_bo,
                          "duong_bay": bay,
                          "ghi_chu": "cùng nơi: chỉ di chuyển nội vùng" if cung_noi else
                                     ("đảo: chỉ đường bay" if den["dao"] else "")})
    return {"_mo_ta": "Di chuyển chặng đi/về. Đường bộ = chim bay × 1,3; xe 50 km/h + 30 phút nghỉ mỗi 3 giờ. "
                      "Đường bay: 700 km/h + 0,3 giờ cất hạ cánh; thủ tục + đưa đón 2,5 giờ.",
            "xe": xe, "phi_luu_dem_tai_xe": tx["phi_luu_dem_tai_xe"], "km_toi_thieu_moi_ngay": tx["km_toi_thieu_moi_ngay"],
            "km_noi_vung_moi_ngay": 60, "toc_do_xe_kmh": 50, "he_so_duong_bo": 1.3, "tuyen": tuyen}


def sinh_khach_san(rd):
    gp = GIA["phong_khach_san"]
    out, n = [], 0
    for den in DIEM_DEN:
        goc = gp["gia_goc_phong_doi"][den["ten"]]
        for muc in MUC:
            for k, sao in enumerate(SAO_THEO_MUC[muc]):
                if den["id"] == "samson" and sao == 5 and k > 0:
                    sao = 4                       # chỗ khó: Sầm Sơn ít 5 sao -> gói đầy đủ thiếu lựa chọn
                n += 1
                gia_doi = lam_tron(goc[str(sao)] * rd.uniform(0.85, 1.2))
                lp = []
                for suc in (2, 3, 4):
                    so_luong = rd.choice([10, 20, 30, 40, 60, 80])
                    lp.append({"suc_chua": suc, "gia_dem": lam_tron(gia_doi * gp["he_so_phong"][str(suc)]),
                               "so_luong": so_luong})
                if k == 1:
                    lp = [p for p in lp if p["suc_chua"] != 4]          # chỗ khó: không có phòng 4 người
                if k == 2:
                    for p in lp:
                        p["so_luong"] = max(3, p["so_luong"] // 6)      # chỗ khó: khách sạn nhỏ, đoàn lớn thiếu phòng
                loai = "resort" if sao == 5 and den["id"] in ("danang", "nhatrang", "phuquoc") else "khach_san"
                out.append({"id": f"KS{n:03d}", "ten": f'{"Resort" if loai == "resort" else "Khách sạn"} '
                                                      f'{TEN_KS[(n * 7) % len(TEN_KS)]} {den["ten"]} (tên dựng)',
                            "diem_den": den["id"], "muc": muc, "hang_sao": sao, "loai": loai,
                            "loai_phong": lp, "tong_phong": sum(p["so_luong"] for p in lp),
                            "gom_bua_sang": True, "uoc_tinh": True, "ten_dung": True})
    return out


def sinh_nha_hang(rd):
    gia = GIA["an_uong"]["theo_muc"]
    out, n = [], 0
    for den in DIEM_DEN:
        for muc in MUC:
            suc = [rd.choice([150, 200, 300, 400]), rd.choice([60, 80, 100]), 25]   # luôn có 1 quán nhỏ (chỗ khó)
            for k in range(3):
                n += 1
                mo = "10:00" if k != 2 else "11:00"
                dong = "22:00" if k != 2 else "14:00"                                 # quán nhỏ chỉ mở trưa
                out.append({"id": f"NH{n:03d}", "ten": f'{TEN_NH[(n * 3) % len(TEN_NH)]} {den["ten"]} (tên dựng)',
                            "diem_den": den["id"], "muc": muc, "suc_chua": suc[k],
                            "gia_nguoi_bua": lam_tron(gia[muc] * HE_SO_DIEM[den["id"]] * rd.uniform(0.85, 1.15), 5000),
                            "gio_mo": mo, "gio_dong": dong, "nhan_doan": suc[k] >= 60,
                            "uoc_tinh": True, "ten_dung": True})
    return out


def sinh_hoat_dong():
    hd = GIA["hoat_dong"]
    out, n = [], 0
    for den in DIEM_DEN:
        for ten, gia, phut, mo, dong, ngay_dong, suc in THAM_QUAN[den["id"]]:
            n += 1
            out.append({"id": f"HD{n:03d}", "ten": ten, "diem_den": den["id"], "loai": "tham_quan",
                        "gia_nguoi": gia, "thoi_luong_phut": phut, "gio_mo": mo, "gio_dong": dong,
                        "ngay_dong_cua": ngay_dong, "suc_chua": suc, "muc": list(MUC),
                        "uoc_tinh": True, "ten_dung": False})
        for loai, ten, phut, mo, dong in (("team_building", "Team building bãi biển / sân cỏ (đơn vị tổ chức)", 180, "07:00", "17:30"),
                                           ("gala_dinner", "Gala dinner có sân khấu, âm thanh, MC", 180, "18:00", "22:00")):
            for muc in ("can_bang", "day_du"):
                n += 1
                out.append({"id": f"HD{n:03d}", "ten": f"{ten} — {den['ten']} ({'gói cơ bản' if muc == 'can_bang' else 'gói trọn'})",
                            "diem_den": den["id"], "loai": loai,
                            "gia_nguoi": lam_tron(hd[loai][muc] * HE_SO_DIEM[den["id"]], 5000),
                            "thoi_luong_phut": phut, "gio_mo": mo, "gio_dong": dong, "ngay_dong_cua": [],
                            "suc_chua": None, "muc": [muc], "uoc_tinh": True, "ten_dung": True})
    return out


def muc_goi():
    return {"_mo_ta": "Quy tắc 3 gói. Cùng khung lịch (số ngày, giờ đi/về, bữa ăn); khác nhau ở MỨC của từng hạng mục.",
            "goi": {
                "tiet_kiem": {"ten": "Tiết kiệm", "hang_sao": [2, 3], "xe": "xe_45_cho", "muc_an": "tiet_kiem",
                              "team_building": False, "gala": False, "may_bay_khi_duong_bo_tren_gio": 12},
                "can_bang": {"ten": "Cân bằng", "hang_sao": [4], "xe": "xe_29_cho", "muc_an": "can_bang",
                             "team_building": True, "gala": True, "may_bay_khi_duong_bo_tren_gio": 10},
                "day_du": {"ten": "Đầy đủ", "hang_sao": [5], "xe": "limousine_18_cho", "muc_an": "day_du",
                           "team_building": True, "gala": True, "may_bay_khi_duong_bo_tren_gio": 8}},
            "phat_sinh_ty_le": GIA["phat_sinh_ty_le"],
            "khung_gio": {"bat_dau_ngay": "07:00", "an_trua": ["11:30", "13:30"], "an_toi": ["18:00", "20:00"],
                          "ket_thuc_muon_nhat": "22:00", "thoi_luong_bua_phut": 75},
            "gioi_han": {"so_nguoi": [5, 500], "so_ngay": [1, 7]}}


def bang_kiem(dc, ks, nh, hd):
    """Ước nhanh gói tiết kiệm 3N2Đ Hà Nội -> Sầm Sơn, 40 người, để so với giá tour ghép đoàn có nguồn."""
    t = next(x for x in dc["tuyen"] if x["tu"] == "HAN" and x["den"] == "samson")
    xe = next(x for x in dc["xe"] if x["loai"] == "xe_45_cho")
    km = max(2 * t["duong_bo_km"] + 2 * dc["km_noi_vung_moi_ngay"], 3 * dc["km_toi_thieu_moi_ngay"])
    tien_xe = km * xe["don_gia_km"] + 2 * dc["phi_luu_dem_tai_xe"]
    k = min((x for x in ks if x["diem_den"] == "samson" and x["muc"] == "tiet_kiem"
             and any(p["suc_chua"] == 4 for p in x["loai_phong"])), key=lambda x: x["loai_phong"][0]["gia_dem"])
    p4 = next(p for p in k["loai_phong"] if p["suc_chua"] == 4)
    phong = 10 * p4["gia_dem"] * 2
    an = min(x["gia_nguoi_bua"] for x in nh if x["diem_den"] == "samson" and x["muc"] == "tiet_kiem") * 40 * 5
    tong = (tien_xe + phong + an) * (1 + GIA["phat_sinh_ty_le"])
    return {"tuyen": "HAN -> Sầm Sơn, 3N2Đ, 40 người, gói tiết kiệm (xe 45 chỗ, 10 phòng 4 người, 5 bữa)",
            "km_xe": km, "tien_xe": tien_xe, "tien_phong": phong, "tien_an": an, "tong": round(tong),
            "moi_nguoi": round(tong / 40),
            "doi_chieu_tour_ghep_doan": GIA["doi_chieu_tour_tron_goi"]["moc"][0]["gia_nguoi"]}


def main():
    rd = random.Random(SEED)
    dc, ks, nh, hd = sinh_di_chuyen(), sinh_khach_san(rd), sinh_nha_hang(rd), sinh_hoat_dong()
    tep = {"diem_den.json": {"seed": SEED, "diem_di": DIEM_DI, "diem_den": DIEM_DEN},
           "di_chuyen.json": dc, "khach_san.json": ks, "nha_hang.json": nh, "hoat_dong.json": hd,
           "muc_goi.json": muc_goi()}
    if "--kiem" not in sys.argv:
        for ten, nd in tep.items():
            (THU_MUC / ten).write_text(json.dumps(nd, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("seed", SEED, "|", {k: (len(v) if isinstance(v, list) else "ok") for k, v in tep.items()})
    print("tuyến:", len(dc["tuyen"]), "| khách sạn:", len(ks), "| nhà hàng:", len(nh), "| hoạt động:", len(hd))
    print("bảng kiểm:", json.dumps(bang_kiem(dc, ks, nh, hd), ensure_ascii=False))


if __name__ == "__main__":
    main()
