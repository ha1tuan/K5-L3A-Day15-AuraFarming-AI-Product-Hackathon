"""Nguồn dữ liệu cho agent: bộ dữ liệu dựng `data/*.json` (5 điểm đi × 24 điểm đến, xem data/DATA_CARD.md).

Khi nơi xuất phát và điểm đến có trong dữ liệu, agent KHÔNG nhờ model đoán đơn giá nữa: module này dựng hạng mục
+ đơn giá cho 3 gói từ dữ liệu (chặng đi thật theo tuyến, giá phòng / bữa / hoạt động theo mức, hoạt động theo mục
đích, điểm tham quan tên thật, video review đã kiểm), đúng định dạng `goi` mà `planner.tinh_goi` nhận — nên phép
tính, xếp phòng, giải thích vượt ngân sách vẫn do `planner.py` làm. Không có trong dữ liệu → trả None, agent quay
về cách cũ (model đề xuất đơn giá "ước tính").

    tim_diem_di(ten) / tim_diem_den(ten)  -> bản ghi hoặc None
    dung_diem_den(req, tu, den)           -> {"ten", "ly_do", "chang", "raw", "calc", ...}  (định dạng agent dùng)
    goi_y_diem_den(req, tu, so=3)         -> danh sách như trên, đã xếp hạng theo mục đích + ngân sách + thời gian đi
    thong_tin_them(dest, req)             -> đoạn markdown: cách đi từng gói, mùa đẹp, điểm tham quan, video

Chỉ thư viện chuẩn + planner. Khách sạn, nhà hàng, đơn vị team building / gala trong dữ liệu là TÊN DỰNG nên không
in tên, chỉ in hạng sao + tiện ích; điểm tham quan là tên thật (giá vé ước tính).
"""
import json
import math
import os
import re
import unicodedata
from datetime import date
from functools import lru_cache

import planner

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
MUC = {"tiet_kiem": "tiet_kiem", "can_bang": "can_bang", "cao_cap": "day_du"}   # gói agent → mức trong dữ liệu
TEN_DICH_VU = {"team_building": "Chương trình gắn kết ngoài trời (thuê đơn vị tổ chức)",
               "spa_thu_gian": "Spa / massage thư giãn", "bbq_tiec_ngoai_troi": "BBQ / tiệc ngoài trời cả đoàn"}
BI_DANH = {"HAN": ["ha noi", "hanoi", "hn"], "HPH": ["hai phong"], "DAD": ["da nang"],
           "SGN": ["tp.hcm", "tphcm", "tp hcm", "hcm", "ho chi minh", "sai gon", "saigon", "sg"],
           "VCA": ["can tho"],
           "phongnha": ["phong nha", "quang binh", "ke bang"], "phuyen": ["phu yen", "tuy hoa"],
           "muine": ["mui ne", "phan thiet"], "hotram": ["ho tram", "long hai"], "tayninh": ["tay ninh", "nui ba den"],
           "halong": ["ha long", "vinh ha long"], "sapa": ["sa pa", "sapa"], "bavi": ["ba vi"]}


def khong_dau(s):
    s = unicodedata.normalize("NFD", str(s or "").lower()).replace("đ", "d")
    return " ".join("".join(c for c in s if unicodedata.category(c) != "Mn").replace(",", " ").split())


@lru_cache(maxsize=None)
def D(ten):
    with open(os.path.join(DATA, ten + ".json"), encoding="utf-8") as f:
        return json.load(f)


def co_du_lieu():
    return all(os.path.exists(os.path.join(DATA, f + ".json"))
               for f in ("diem_den", "di_chuyen", "khach_san", "nha_hang", "hoat_dong", "muc_goi"))


def _tim(ten, ds):
    k = khong_dau(ten)
    if not k:
        return None
    for x in sorted(ds, key=lambda x: -len(x["ten"])):          # tên dài trước: "Hội An" không ăn nhầm "An"
        ten_x = khong_dau(x["ten"])
        names = [ten_x, ten_x.split(" (")[0], khong_dau(x["id"])] + BI_DANH.get(x["id"], [])
        if any(n and (k == n or f" {n} " in f" {k} ") for n in names):
            return x
    return None


def tim_diem_di(ten):
    """Nơi xuất phát: 5 điểm đi có tuyến sẵn trong di_chuyen.json, hoặc một trong 24 điểm đến (tuyến tính bằng cùng
    công thức của data/sinh_du_lieu.py — xem tuyen())."""
    if not co_du_lieu():
        return None
    return _tim(ten, D("diem_den")["diem_di"]) or _tim(ten, D("diem_den")["diem_den"])


def tim_diem_den(ten):
    return _tim(ten, D("diem_den")["diem_den"]) if co_du_lieu() else None


def _diem_md(ph, md):
    return ph["nghi_duong"] + ph["gan_ket"] if md == "ca_hai" else 2 * ph[md]


# --- Chặng đi ------------------------------------------------------------------------------------
# Toạ độ sân bay — chép từ data/sinh_du_lieu.py (để tính tuyến cho nơi xuất phát ngoài 5 điểm đi có sẵn).
SAN_BAY = {"HAN": (21.2212, 105.8072), "HPH": (20.8194, 106.7250), "DAD": (16.0439, 108.1994),
           "SGN": (10.8188, 106.6520), "VCA": (10.0851, 105.7117), "VDO": (21.1178, 107.4142),
           "THD": (19.9017, 105.4678), "VII": (18.7376, 105.6708), "VDH": (17.5150, 106.5906),
           "HUI": (16.4015, 107.7026), "UIH": (13.9550, 109.0420), "TBB": (13.0496, 109.3337),
           "CXR": (11.9982, 109.2194), "DLI": (11.7500, 108.3670), "PQC": (10.1698, 103.9931),
           "VCS": (8.7318, 106.6329)}


def _km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(h))


def tuyen(tu, den):
    """Tuyến tu → den: lấy trong di_chuyen.json nếu có; không thì tính như data/sinh_du_lieu.py (đường bộ = chim bay
    × 1,3, xe 50 km/h + 30 phút nghỉ mỗi 3 giờ, phà +1 giờ; bay 700 km/h + 0,3 giờ, thủ tục 2 giờ; vé theo mốc có
    nguồn hoặc phí cố định + phí / km). Đảo chỉ đường bay."""
    t = next((x for x in D("di_chuyen")["tuyen"] if x["tu"] == tu["id"] and x["den"] == den["id"]), None)
    if t:
        return t
    dao = tu.get("dao_chi_duong_bay") or den.get("dao_chi_duong_bay")
    km_bo = None if dao else round(_km((tu["lat"], tu["lon"]), (den["lat"], den["lon"])) * 1.3)
    cung_noi = tu["id"] == den["id"] or (km_bo is not None and km_bo < 25)
    if cung_noi:
        km_bo = 0
    gio_bo = None if km_bo is None else round(km_bo / 50 + (km_bo / 50 // 3) * 0.5 + (1.0 if den.get("co_pha") else 0), 1)
    bay = None
    a, b = tu.get("san_bay"), den.get("san_bay")
    if a in SAN_BAY and b in SAN_BAY and a != b and not cung_noi:
        km_bay = round(_km(SAN_BAY[a], SAN_BAY[b]))
        if km_bay >= (50 if dao else 250):
            ve = D("gia_chuan")["ve_may_bay_mot_chieu_pho_thong"]
            moc = next((m for m in ve["moc"] if set(m["chang"].split("-")) == {a, b} and "khoang" in m), None)
            gia = (int(round(sum(moc["khoang"]) / 2 / 10000) * 10000) if moc else
                   int(round((ve["phi_co_dinh"] + ve["phi_moi_km"] * km_bay) / 10000) * 10000))
            bay = {"chang": "%s-%s" % (a, b), "km": km_bay, "gio_bay": round(km_bay / 700 + 0.3, 1), "gio_thu_tuc": 2.0,
                   "km_san_bay_toi_diem_den": round(_km(SAN_BAY[b], (den["lat"], den["lon"])) * 1.3),
                   "gia_ve_mot_chieu": gia, "uoc_tinh": moc is None, "nguon": moc and moc.get("nguon")}
    return {"tu": tu["id"], "den": den["id"], "duong_bo_km": km_bo, "duong_bo_gio": gio_bo,
            "co_pha": bool(den.get("co_pha")), "duong_bay": bay, "ghi_chu": "tính theo công thức của bộ dữ liệu"}


def chang_di(tu, den, n, so_ngay, muc):
    """Phương tiện theo quy tắc gói (muc_goi): đường bộ dài hơn ngưỡng của gói và có chặng bay → máy bay."""
    dc, quy = D("di_chuyen"), D("muc_goi")["goi"][muc]
    t = tuyen(tu, den)
    # Xe: gói cao cấp giữ loại xe của quy tắc gói (limousine); gói khác chọn loại rẻ nhất cho đúng số người
    # (đoàn 12 người không thuê xe 45 chỗ) — tiết kiệm: 16/29/45 chỗ, cân bằng: 16/29 chỗ.
    cho_phep = {"tiet_kiem": ("xe_16_cho", "xe_29_cho", "xe_45_cho"), "can_bang": ("xe_16_cho", "xe_29_cho")}.get(muc)
    xe = (min((x for x in dc["xe"] if x["loai"] in cho_phep), key=lambda x: (-(-n // x["so_cho"]) * x["don_gia_km"], -x["so_cho"]))
          if cho_phep else next(x for x in dc["xe"] if x["loai"] == quy["xe"]))
    ten_xe = xe["loai"].replace("_", " ").replace("cho", "chỗ")
    bay = t["duong_bay"] and (t["duong_bo_km"] is None or t["duong_bo_gio"] > quy["may_bay_khi_duong_bo_tren_gio"])
    noi_vung = dc["km_noi_vung_moi_ngay"] * so_ngay
    if bay:
        b = t["duong_bay"]
        km = max(2 * b["km_san_bay_toi_diem_den"] + noi_vung, dc["km_toi_thieu_moi_ngay"] * so_ngay)
        gio = round(b["gio_bay"] + b["gio_thu_tuc"] + b["km_san_bay_toi_diem_den"] / 50, 1)
        tien_xe = km * xe["don_gia_km"] + (so_ngay - 1) * dc["phi_luu_dem_tai_xe"]
        return {"kieu": "ve", "gio": gio, "mo_ta": "máy bay %s + %s tại chỗ" % (b["chang"], ten_xe),
                "di_chuyen": {"kieu": "ve", "loai": "Vé máy bay khứ hồi %s (phổ thông)" % b["chang"],
                              "don_gia": 2 * b["gia_ve_mot_chieu"]},
                "xe_tai_cho": {"loai": "Thuê %s có tài xế (đưa đón sân bay + đi lại)" % ten_xe, "suc_chua": xe["so_cho"],
                               "don_gia_xe_ngay": planner.round_k(tien_xe / so_ngay)},
                "pha": False, "tuyen": t}
    if t["duong_bo_km"] is None:
        return None
    km = max(2 * t["duong_bo_km"] + noi_vung, dc["km_toi_thieu_moi_ngay"] * so_ngay)
    tien_xe = km * xe["don_gia_km"] + (so_ngay - 1) * dc["phi_luu_dem_tai_xe"]
    return {"kieu": "xe", "gio": t["duong_bo_gio"],
            "mo_ta": ("%s đi lại nội vùng" % ten_xe) if t["duong_bo_km"] == 0 else
                     "%s đường bộ %d km" % (ten_xe, t["duong_bo_km"]),
            "di_chuyen": {"kieu": "xe", "loai": "Thuê %s có tài xế, %d km cả chuyến" % (ten_xe, km),
                          "suc_chua_xe": xe["so_cho"], "don_gia": tien_xe},
            "pha": bool(t["co_pha"]), "tuyen": t}


# --- Lưu trú, ăn, hoạt động --------------------------------------------------------------------
def chon_khach_san(den, muc, n, md):
    ks = [k for k in D("khach_san") if k["diem_den"] == den["id"] and k["muc"] == muc]
    if not ks:
        return None
    du = [k for k in ks if sum(p["suc_chua"] * p["so_luong"] for p in k["loai_phong"]) >= n]
    if du:
        ph = (lambda k: k["phu_hop"]["nghi_duong"] + k["phu_hop"]["gan_ket"]) if md == "ca_hai" else (lambda k: k["phu_hop"][md])
        return max(du, key=lambda k: (ph(k), -min(p["gia_dem"] / p["suc_chua"] for p in k["loai_phong"])))
    return max(ks, key=lambda k: k["suc_chua_toi_da"])          # không cơ sở nào đủ → planner báo thiếu phòng


def mo_ta_khach_san(k):
    ti = k["tien_ich"]
    co = [x for x, ok in (("hồ bơi", ti["ho_boi"]), ("bãi biển riêng", ti["bai_bien_rieng"]), ("spa", ti["spa"]),
                          ("khuôn viên team building ~%d người" % ti["khuon_vien_team_building_nguoi"],
                           ti["khuon_vien_team_building_nguoi"]),
                          ("hội trường %d chỗ" % ti["hoi_truong_cho"], ti["hoi_truong_cho"]),
                          ("gồm bữa sáng", k.get("gom_bua_sang"))) if ok]
    return "%s %d★%s" % ("Resort" if k["loai"] == "resort" else "Khách sạn", k["hang_sao"], (" (" + ", ".join(co) + ")") if co else "")


def tham_quan(den, muc, md, n, so):
    hd = [x for x in D("hoat_dong") if x["diem_den"] == den["id"] and muc in x["muc"] and x["loai"] == "tham_quan"
          and (md == "ca_hai" or md in x["muc_dich"])]
    bo = [x for x in hd if x["suc_chua"] and x["suc_chua"] < n]
    hd = [x for x in hd if x not in bo]
    hd.sort(key=lambda x: (x["gia_nguoi"], x["id"]), reverse=(muc == "day_du"))
    if muc == "can_bang":
        hd = hd[len(hd) // 3:] + hd[:len(hd) // 3]
    return hd[:so], bo


def goi_tu_du_lieu(req, tu, den, lv):
    """Hạng mục + đơn giá của MỘT gói, đúng định dạng planner.tinh_goi. None nếu không có tuyến."""
    muc, n, md = MUC[lv], req["so_nguoi"], req["muc_dich"]
    so_ngay = max(1, req["so_ngay"])
    c = chang_di(tu, den, n, so_ngay, muc)
    if c is None:
        return None
    goi = {"di_chuyen": c["di_chuyen"], "_chang": c}
    if c.get("xe_tai_cho"):
        goi["xe_tai_cho"] = c["xe_tai_cho"]
    if req["so_dem"] > 0:
        k = chon_khach_san(den, muc, n, md)
        if k:
            goi["_luu_tru_chi_tiet"] = mo_ta_khach_san(k)
            goi["luu_tru"] = {"mo_ta": "%s %d★ tại %s" % ("Resort" if k["loai"] == "resort" else "Khách sạn", k["hang_sao"], den["ten"]),
                              "loai_phong": [{"ten": "Phòng %d người" % p["suc_chua"], "suc_chua": p["suc_chua"],
                                              "gia_dem": p["gia_dem"], "so_phong_con": p["so_luong"]}
                                             for p in k["loai_phong"]]}
    nh = sorted((x for x in D("nha_hang") if x["diem_den"] == den["id"] and x["muc"] == muc), key=lambda x: x["gia_nguoi_bua"])
    du = [x for x in nh if x["suc_chua"] >= n]
    if du:
        goi["an_uong"] = {"mo_ta": "Nhà hàng nhận đoàn ≥ %d chỗ (giá mức %s)" % (n, dict(planner.PACKAGES)[lv].lower()),
                          "don_gia_bua": du[0]["gia_nguoi_bua"]}
    elif nh:
        goi["an_uong"] = {"mo_ta": "Chia đoàn nhiều nhà hàng (không quán nào đủ %d chỗ)" % n,
                          "don_gia_bua": planner.round_k(sum(x["gia_nguoi_bua"] for x in nh) / len(nh))}
    loai_can = D("muc_goi")["hoat_dong_theo_muc_dich"][md][muc]
    tq, bo = tham_quan(den, muc, md, n, max(1, so_ngay)) if "tham_quan" in loai_can else ([], [])
    hd = [{"ten": x["ten"], "don_gia_nguoi": x["gia_nguoi"], "team_building": False} for x in tq if x["gia_nguoi"] > 0]
    goi["_mien_phi"] = [x["ten"] for x in tq if x["gia_nguoi"] <= 0]
    dv = [x for x in D("hoat_dong") if x["diem_den"] == den["id"] and muc in x["muc"]]
    for loai in loai_can:
        x = next((h for h in dv if h["loai"] == loai), None)
        if x and loai in TEN_DICH_VU:
            hd.append({"ten": TEN_DICH_VU[loai], "don_gia_nguoi": x["gia_nguoi"], "team_building": loai == "team_building"})
    if c["pha"]:
        hd.append({"ten": "Vé phà khứ hồi (2 lượt)", "don_gia_nguoi": 2 * D("di_chuyen")["phi_pha_nguoi_luot"], "team_building": False})
    goi["hoat_dong"] = hd
    gala = next((h for h in dv if h["loai"] == "gala_dinner"), None)
    goi["gala"] = {"co": bool(gala and "gala_dinner" in loai_can and req["so_dem"] > 0),
                   "don_gia_nguoi": gala["gia_nguoi"] if gala else 0}
    goi["_tu_do"] = "tu_do" in loai_can
    goi["_bo_suc_chua"] = [x["ten"] for x in bo]
    return goi


# --- Ghép thành "dest" agent dùng ---------------------------------------------------------------
def ly_do(den, md):
    ph = den["phu_hop"]
    muc = {"nghi_duong": "nghỉ dưỡng %d/3" % ph["nghi_duong"], "gan_ket": "gắn kết %d/3" % ph["gan_ket"],
           "ca_hai": "nghỉ dưỡng %d/3, gắn kết %d/3" % (ph["nghi_duong"], ph["gan_ket"])}[md]
    return "%s; độ hợp %s *(nhóm tự ước tính)*; mùa đẹp tháng %s." % (den["mo_ta"][:1].upper() + den["mo_ta"][1:], muc, den["mua_dep_thang"])


def dung_diem_den(req, tu, den):
    raw = {}
    for lv, _ in planner.PACKAGES:
        g = goi_tu_du_lieu(req, tu, den, lv)
        if g is None:
            return None
        raw[lv] = g
    dest = {"den": den, "tu": tu, "raw": raw}
    lich = {}
    for lv in raw:                       # tiền chỉ tính việc có trong lịch: xếp lịch trước, bỏ việc không đủ giờ
        lich[lv], bo = lich_tu_du_lieu(req, dest, lv)
        if bo:
            raw[lv]["hoat_dong"] = [h for h in raw[lv]["hoat_dong"] if h["ten"] not in bo]
            raw[lv]["_mien_phi"] = [x for x in raw[lv].get("_mien_phi") or [] if x not in bo]
            dest.setdefault("canh_bao", set()).add("Gói %s: bỏ %s vì không đủ thời gian trong %d ngày (đã trừ khỏi bảng tiền)."
                                                   % (dict(planner.PACKAGES)[lv].lower(), "; ".join(bo), req["so_ngay"]))
    calc = {lv: planner.tinh_goi(req, lv, raw[lv]) for lv in raw}
    tk = raw["tiet_kiem"]["_chang"]
    t = tk["tuyen"]
    b = t.get("duong_bay") or {}
    chang = {"km": t["duong_bo_km"] if t["duong_bo_km"] is not None else b.get("km"),
             "gio_xe": t["duong_bo_gio"] if t["duong_bo_km"] else None,
             "gio_bay": round(b["gio_bay"] + b["gio_thu_tuc"], 1) if b else None,
             "ghi_chu": "; ".join("gói %s: %s" % (name.lower(), raw[lv]["_chang"]["mo_ta"]) for lv, name in planner.PACKAGES)}
    dest.update({"ten": den["ten"], "id": den["id"], "ly_do": ly_do(den, req["muc_dich"]), "chang": chang,
                 "calc": calc, "nguon": "du_lieu", "lich": lich})
    return dest


def _trong_mua(mua, thang):
    if "quanh" in mua:
        return True
    a, b = (int(x) for x in mua.replace("–", "-").split("-"))
    return a <= thang <= b if a <= b else (thang >= a or thang <= b)


def thang_hien_tai():
    try:
        return date.fromisoformat(os.environ.get("TRAVEL_TODAY") or "").month
    except ValueError:
        return date.today().month


def goi_y_diem_den(req, tu, so=3, bo_qua=()):
    """Cách A: xếp 24 điểm đến bằng code. Ưu tiên nơi hợp mục đích (≥2/3), gói cao nhất còn trong ngân sách,
    thời gian đi một chiều hợp số ngày, đúng mùa. Không nơi nào vừa ngân sách → trả các nơi rẻ nhất.
    bo_qua: tên điểm đến người dùng đã xem (bấm "Gợi ý nơi khác") — bỏ ra để lấy các nơi tiếp theo."""
    bo = {khong_dau(x) for x in bo_qua or ()}
    b, md, so_ngay = req["ngan_sach"], req["muc_dich"], max(1, req["so_ngay"])
    gio_toi_da = 3 if so_ngay == 1 else 2.5 * so_ngay + 1
    thang = thang_hien_tai()
    ung = []
    for den in D("diem_den")["diem_den"]:
        ph = den["phu_hop"]
        if (md == "ca_hai" and min(ph.values()) < 2) or (md != "ca_hai" and ph[md] < 2):
            continue
        if khong_dau(den["ten"]) in bo:
            continue
        if den["id"] == tu["id"] or tuyen(tu, den)["duong_bo_km"] == 0:                            # đi chơi ngay tại thành phố xuất phát: không gợi ý
            continue
        d = dung_diem_den(req, tu, den)
        if d is None:
            continue
        ok = [i for i, (lv, _) in enumerate(planner.PACKAGES) if not b or d["calc"][lv]["tong"] <= b]
        lv_tot = ok[-1] if ok else None
        gio = d["raw"][planner.PACKAGES[lv_tot or 0][0]]["_chang"]["gio"]
        if gio > gio_toi_da:
            continue
        diem = (_diem_md(ph, md) * 5 + (lv_tot if lv_tot is not None else -10) * 6 - gio * max(1, 6 / so_ngay)
                + (3 if _trong_mua(den["mua_dep_thang"], thang) else 0))
        ung.append((lv_tot is not None, diem, -d["calc"]["tiet_kiem"]["tong"], d))
    vua = [u for u in ung if u[0]]
    if vua:
        vua.sort(key=lambda u: -u[1])
        return [u[3] for u in vua[:so]]
    ung.sort(key=lambda u: u[2], reverse=True)                     # không nơi nào vừa: rẻ nhất trước
    return [u[3] for u in ung[:so]]


# --- Thông tin thêm (cho người dùng) ------------------------------------------------------------
def video(den_id, so_review=2, so_tb=1):
    try:
        v = D("video_review")["video"].get(den_id) or []
    except FileNotFoundError:
        return []
    return [x for x in v if x["loai"] == "review"][:so_review] + [x for x in v if x["loai"] != "review"][:so_tb]


def thong_tin_them(dest, req, levels=None):
    den = dest["den"]
    out = ["### Thông tin thêm về %s" % den["ten"]]
    cach = [(name.lower(), dest["raw"][lv]["_chang"]) for lv, name in planner.PACKAGES if not levels or lv in levels]
    out.append("- **Cách đi từ %s** (giờ một chiều, gồm thủ tục bay nếu có): " % dest["tu"]["ten"] + " · ".join(
        "gói %s: %s%s" % (ten, c["mo_ta"], "" if c["gio"] == 0 else ", ~%s giờ" % c["gio"]) for ten, c in cach))
    t = dest["raw"]["tiet_kiem"]["_chang"]["tuyen"]
    if t.get("duong_bay") and t["duong_bo_km"]:
        out.append("- Đường bộ %d km (~%s giờ); có chặng bay %s. Gói nào đi xe thì đã tính giờ xe thật." % (
            t["duong_bo_km"], t["duong_bo_gio"], t["duong_bay"]["chang"]))
    lt = [(name.lower(), dest["raw"][lv].get("_luu_tru_chi_tiet")) for lv, name in planner.PACKAGES
          if (not levels or lv in levels) and dest["raw"][lv].get("_luu_tru_chi_tiet")]
    if lt:
        out.append("- **Nơi ở theo gói:** " + " · ".join("gói %s: %s" % x for x in lt))
    mua = den["mua_dep_thang"]
    out.append("- **Mùa đẹp:** tháng %s%s." % (mua, "" if _trong_mua(mua, thang_hien_tai()) else
                                             " — tháng %d (hiện tại) **ngoài mùa đẹp**, nên cân nhắc thời tiết hoặc dời ngày" % thang_hien_tai()))
    tq = sorted({h["ten"] for lv in dest["raw"] for h in dest["raw"][lv]["hoat_dong"] if h["ten"] not in TEN_DICH_VU.values()
                 and not h["ten"].startswith("Vé phà")})
    if tq:
        out.append("- **Điểm tham quan trong kế hoạch** (tên thật, giá vé ước tính): " + "; ".join(tq) + ".")
    bo = sorted({x for lv in dest["raw"] for x in dest["raw"][lv]["_bo_suc_chua"]})
    if bo:
        out.append("- Đã bỏ vì sức chứa / lượt nhỏ hơn đoàn %d người: %s." % (req["so_nguoi"], "; ".join(bo)))
    vs = video(den["id"])
    if vs:
        out.append("- **Video tham khảo** (YouTube, đã kiểm link 27/11/2026):")
        out += ["  - [%s](%s) — %s" % (x["tieu_de"], x["url"], x["kenh"]) for x in vs]
    for w in sorted(dest.get("canh_bao") or []):
        out.append("- ⚠ " + w)
    out.append("- **Về giá:** giá tham khảo theo hạng khách sạn, nhà hàng và giá thị trường có nguồn — **chưa phải báo giá "
               "của một cơ sở cụ thể**. Trước khi đặt, công ty chọn cơ sở thật cùng hạng và xác nhận đủ số phòng.")
    return "\n".join(out)


# --- Bóc tách bằng code (dự phòng khi model không trả JSON, vd chế độ giả / hết lượt) ------------------
def _so(s):
    return float(s.replace(",", "."))


def boc_tach(text):
    """Chỉ lấy thông tin NÓI RÕ trong câu (không đoán): số người, ngày / đêm, ngân sách (tổng hoặc mỗi người),
    nơi xuất phát, điểm đến có trong dữ liệu, mục đích. Trả dict cùng khoá với PARSE_SYSTEM (thiếu → None)."""
    t = khong_dau(text)
    r = {k: None for k in ("so_nguoi", "noi_xuat_phat", "muc_dich", "so_ngay", "so_dem", "ngan_sach_tong",
                           "ngan_sach_moi_nguoi", "dia_diem")}
    m = re.search(r"(\d+)\s*(nguoi|nhan vien|thanh vien|khach|ban)\b", t)
    r["so_nguoi"] = int(m.group(1)) if m else None
    m = re.search(r"(\d+)\s*ngay", t)
    r["so_ngay"] = int(m.group(1)) if m else None
    m = re.search(r"(\d+)\s*dem", t)
    r["so_dem"] = int(m.group(1)) if m else (0 if re.search(r"trong ngay|di ve trong ngay", t) else None)
    if r["so_dem"] == 0 and not r["so_ngay"]:
        r["so_ngay"] = 1
    tp = unicodedata.normalize("NFD", str(text).lower()).replace("đ", "d")          # giữ dấu phẩy thập phân: "1,5 tỷ"
    tp = " ".join("".join(c for c in tp if unicodedata.category(c) != "Mn").split())
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*(ty|trieu|tr)\b(\s*(?:/|mot|moi|1)\s*(?:nguoi|dau nguoi|khach))?", tp)
    if m:
        v = int(_so(m.group(1)) * (1e9 if m.group(2) == "ty" else 1e6))
        r["ngan_sach_moi_nguoi" if m.group(3) or re.search(r"(moi|dau) nguoi", tp[max(0, m.start() - 15):m.start()]) else
          "ngan_sach_tong"] = v
    tu = re.search(r"(?:tu|xuat phat(?: tu)?|khoi hanh(?: tu)?)\s+([a-z. ]{2,25})", t)
    if tu:
        x = tim_diem_di(" ".join(tu.group(1).split()[:4])) or next(
            (x for x in D("diem_den")["diem_di"] for n in [khong_dau(x["ten"])] + BI_DANH.get(x["id"], [])
             if tu.group(1).startswith(n)), None)
        r["noi_xuat_phat"] = x["ten"] if x else None
    con = t.replace(khong_dau(r["noi_xuat_phat"] or "@@"), " ")
    for den in sorted(D("diem_den")["diem_den"], key=lambda x: -len(x["ten"])):
        names = [khong_dau(den["ten"]).split(" (")[0], khong_dau(den["ten"])] + BI_DANH.get(den["id"], [])
        if any(f" {n} " in f" {con} " for n in names if n):
            r["dia_diem"] = den["ten"]
            break
    nd = bool(re.search(r"nghi duong|thu gian|nghi ngoi", t))
    gk = bool(re.search(r"gan ket|team ?building|teambuilding|doan ket", t))
    r["muc_dich"] = "ca_hai" if (nd and gk) or "ca hai" in t else "nghi_duong" if nd else "gan_ket" if gk else None
    r["dia_diem_xac_dinh"], r["trong_nuoc"], r["khong_muon"] = True, True, []
    if re.search(r"khong (can|muon|co) gala", t):
        r["khong_muon"].append("gala")
    return r


# --- Xếp lịch bằng code (đường dữ liệu): model không cần đoán giờ --------------------------------
def _hm(phut):
    phut = int(round(phut / 5.0)) * 5
    return "%02d:%02d" % (phut // 60 % 24, phut % 60) + (" (+1 ngày)" if phut >= 1440 else "")


def _p(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def _hang_viec(raw, den, md, n_ngay):
    """Việc cần xếp: (tên, phút, loại, giờ mở, giờ đóng) — đúng các hoạt động đã tính tiền + tham quan miễn phí."""
    info = {x["ten"]: x for x in D("hoat_dong") if x["diem_den"] == den["id"]}
    hang = []
    for h in raw["hoat_dong"]:
        if h["ten"].startswith("Vé phà"):
            continue
        if h["ten"] == TEN_DICH_VU["bbq_tiec_ngoai_troi"] and n_ngay > 1:
            continue                                        # BBQ: buổi tối đêm đầu
        x = info.get(h["ten"])
        loai = ("team_building" if h.get("team_building") or (h["ten"] == TEN_DICH_VU["bbq_tiec_ngoai_troi"] and md != "nghi_duong")
                else "nghi" if h["ten"] == TEN_DICH_VU["spa_thu_gian"] else "an" if h["ten"] == TEN_DICH_VU["bbq_tiec_ngoai_troi"]
                else "tham_quan")
        phut = x["thoi_luong_phut"] if x else {"team_building": 180, "nghi": 120}.get(loai, 90)
        hang.append((h["ten"], phut, loai, _p(x["gio_mo"]) if x else 7 * 60, _p(x["gio_dong"]) if x else 17 * 60 + 30))
    for ten in raw.get("_mien_phi") or []:
        x = info.get(ten)
        hang.append((ten, x["thoi_luong_phut"] if x else 90, "tham_quan", _p(x["gio_mo"]) if x else 0,
                     _p(x["gio_dong"]) if x else 1440))
    return sorted(hang, key=lambda h: (h[2] != "team_building", -h[1]))


def lich_tu_du_lieu(req, dest, lv):
    """Lịch từng ngày cho một gói, cùng định dạng LICH_SYSTEM: [{"ngay", "khoi": [{"gio", "viec", "loai"}]}].
    Trả (lich, viec_bo): viec_bo = hoạt động đã tính tiền nhưng không đủ thời gian xếp (dung_diem_den bỏ khỏi bảng
    tiền rồi tính lại). Ngày 1 mở bằng chặng đi (giờ thật của tuyến), ngày cuối đóng bằng chặng về; tham quan theo
    thời lượng + giờ mở cửa; nghỉ dưỡng → mỗi ngày có tự do; gắn kết → team building / BBQ; gala đêm cuối."""
    raw, den, tu = dest["raw"][lv], dest["den"], dest["tu"]
    c, n_ngay, md = raw["_chang"], max(1, req["so_ngay"]), req["muc_dich"]
    g = int(round(c["gio"] * 60))
    co_bbq = n_ngay > 1 and any(h["ten"] == TEN_DICH_VU["bbq_tiec_ngoai_troi"] for h in raw["hoat_dong"])
    gala = bool(raw["gala"].get("co")) and not any("gala" in x for x in req.get("khong_muon") or [])
    can_tu_do = md in ("nghi_duong", "ca_hai")
    ngay = []                                          # mỗi ngày: {"khoi": [...], "trong": [(a, b)], "trua": (a, b) | None}
    for d in range(1, n_ngay + 1):
        khoi, t = [], (7 if d == 1 else 8) * 60
        if d == 1:
            if g:
                khoi.append((t, t + g, "Khởi hành từ %s đi %s (%s)" % (tu["ten"], den["ten"], c["mo_ta"]), "di_chuyen"))
                t += g
            else:
                khoi.append((7 * 60 + 30, 8 * 60, "Xe đón đoàn tại điểm hẹn ở %s" % tu["ten"], "di_chuyen"))
                t = 8 * 60
            if req["so_dem"] > 0 and t <= 15 * 60:
                khoi.append((t, t + 30, "Nhận phòng / gửi đồ, nghỉ ngắn" if t >= 13 * 60 else "Gửi đồ tại nơi ở", "nghi"))
                t += 30
        cuoi = d == n_ngay
        if cuoi:
            het = (min(14 * 60, 21 * 60 + 30 - g) if n_ngay > 1 else
                   max(t + 75 + 195, min(16 * 60, 21 * 60 + 30 - g)))
            het = max(het, t)
        else:
            het = max(17 * 60 + 30, t)
        trua = None
        if t <= 11 * 60 + 30 and het >= 12 * 60 + 45:
            trua = (11 * 60 + 30, 12 * 60 + 45)
        elif 11 * 60 + 30 < t <= 14 * 60 and het >= t + 75:
            trua = (t, t + 75)
        trong = [(t, het)] if not trua else [(t, trua[0]), (trua[1], het)]
        toi = None                                        # buổi tối (sau bữa tối thường) cho việc mở buổi tối
        if not cuoi and not (gala and d == n_ngay - 1) and not (co_bbq and d == 1):
            toi = (max(het, 18 * 60 + 30) + 75 + 15, 22 * 60)
        ngay.append({"khoi": khoi, "trong": [w for w in trong if w[1] - w[0] >= 30], "trua": trua, "het": het,
                     "cuoi": cuoi, "da_xep": 0, "toi": toi})
    bo = []
    for h in _hang_viec(raw, den, md, n_ngay):
        ung = []
        for i, nd in enumerate(ngay):
            if h[3] >= 16 * 60 and nd["toi"] and max(nd["toi"][0], h[3]) + h[1] <= min(nd["toi"][1], h[4]):
                ung.append((nd["da_xep"] - 0.5, i, max(nd["toi"][0], h[3]), None, "toi"))   # việc buổi tối
            for j, (a, b) in enumerate(nd["trong"]):
                st = max(a, h[3])
                if st + h[1] <= min(b, h[4]):
                    ung.append((nd["da_xep"], i, st, j, None))
            if h[1] >= 240 and nd["trua"] and len(nd["trong"]) == 2 and nd["da_xep"] == 0:   # việc dài: gồm ăn trưa
                (a, _), (_, b) = sorted(nd["trong"])
                st = max(a, h[3])
                if st + h[1] <= min(b, h[4]):
                    ung.append((nd["da_xep"] + 0.5, i, st, None, "ca_ngay"))
        if not ung:
            bo.append(h[0])
            continue
        _, i, st, j, kieu = min(ung)
        nd = ngay[i]
        if kieu == "toi":
            nd["khoi"].append((st, st + h[1], h[0], h[2]))
            nd["toi"] = None
        elif kieu == "ca_ngay":
            (a, _), (_, b) = sorted(nd["trong"])
            nd["trua"] = None
            nd["khoi"].append((st, st + h[1], h[0] + " — gồm ăn trưa trong chương trình", h[2]))
            nd["trong"] = [w for w in ((a, st), (st + h[1] + 15, b)) if w[1] - w[0] >= 30]
        else:
            a, b = nd["trong"].pop(j)
            nd["khoi"].append((st, st + h[1], h[0], h[2]))
            nd["trong"] += [w for w in ((a, st), (st + h[1] + 15, b)) if w[1] - w[0] >= 30]
        nd["da_xep"] += h[1]
    out = []
    for d, nd in enumerate(ngay, 1):
        khoi = nd["khoi"]
        if nd["trua"]:
            khoi.append((nd["trua"][0], nd["trua"][1], "Ăn trưa cả đoàn", "an"))
        co_tu_do = False
        for a, b in sorted(nd["trong"], key=lambda w: w[0] - w[1]):    # ô trống dài trước
            if b - a >= 60 or (can_tu_do and not co_tu_do):
                viec = ("Tự do nghỉ ngơi tại nơi ở / tắm biển / dạo phố" if can_tu_do and not co_tu_do else
                        "Tự do khám phá %s theo nhóm nhỏ (ăn vặt, chợ, mua quà)" % den["ten"] if not co_tu_do else
                        "Nghỉ ngơi tự do")
                khoi.append((a, b, viec, "tu_do"))
                co_tu_do = True
        het = nd["het"]
        if can_tu_do and not co_tu_do:                    # ngày kín: thêm 30 phút tự do (cuối ngày dời chặng về)
            khoi.append((het, het + 30, "Tự do nghỉ ngơi", "tu_do"))
            het += 30
        if not nd["cuoi"]:
            toi = max(het, 18 * 60) if co_bbq and d == 1 else max(het, 18 * 60 + 30)
            if gala and d == n_ngay - 1:
                khoi.append((toi, toi + 180, "Gala dinner cả đoàn (sân khấu, MC, trao giải)", "an"))
            elif co_bbq and d == 1:
                khoi.append((toi, toi + 150, TEN_DICH_VU["bbq_tiec_ngoai_troi"] + ", giao lưu",
                             "team_building" if md != "nghi_duong" else "an"))
            else:
                khoi.append((toi, toi + 75, "Ăn tối cả đoàn", "an"))
        else:
            khoi.append((het, het + max(g, 30), ("Về %s (%s)" % (tu["ten"], c["mo_ta"])) if g else
                         "Xe đưa đoàn về điểm hẹn, kết thúc chương trình", "di_chuyen"))
            if het + g > 23 * 60:
                dest.setdefault("canh_bao", set()).add(
                    "Gói %s: chặng về (%s) kết thúc lúc ~%s — quá muộn; nên thêm 1 đêm hoặc chọn gói đi máy bay."
                    % (dict(planner.PACKAGES)[lv].lower(), c["mo_ta"], _hm(het + g)))
        khoi.sort(key=lambda x: x[0])
        out.append({"ngay": d, "khoi": [{"gio": "%s–%s" % (_hm(a), _hm(b)), "viec": v, "loai": lo} for a, b, v, lo in khoi]})
    return out, bo


def co_y_muc_dich(text):
    """Câu có nói tới mục đích (kể cả cách nói khác) không — để không nhận mục đích model tự điền."""
    return bool(re.search(r"nghi duong|thu gian|nghi ngoi|xa hoi|nghi mat|gan ket|team ?building|doan ket|giao luu|"
                          r"hoa dong|ky niem|thuong nhan vien|tri an|nghi le|tham quan|kham pha", khong_dau(text)))
