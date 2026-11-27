"""Bộ tính THAM CHIẾU trên data/*.json: kiểm dữ liệu đủ cho bài toán + tính đáp án cho bộ câu thử. Chỉ thư viện chuẩn.
Mọi con số do code tính (không gọi model). Agent của nhóm có thể dùng lại các hàm này ở bước "code tính".

Chiều 1 · nhập địa điểm -> chi phí 3 gói:
    python data/tinh_thu.py --tu "Hà Nội" --den "Hạ Long" --nguoi 40 --ngay 3 --muc-dich gan_ket
    python data/tinh_thu.py --tu HAN --den halong --nguoi 40 --ngay 3 --muc-dich ca_hai --ngan-sach 150tr
Chiều 2 · nhập kinh phí -> gợi ý địa điểm (xếp theo mức hợp mục đích, gói cao nhất còn trong ngân sách):
    python data/tinh_thu.py --tu SGN --ngan-sach 3tr --moi-nguoi --nguoi 60 --ngay 3 --muc-dich nghi_duong
Thêm --json để in máy đọc được.

Quy tắc (ghi cả trong DATA_CARD.md):
- Gói khác nhau ở MỨC (hạng sao, loại xe, mức ăn, dịch vụ); cùng khung: số đêm = số ngày - 1, bữa chính = 2 × ngày - 1.
- Di chuyển: đảo -> bay; đường bộ quá ngưỡng giờ của gói và có chặng bay -> bay; còn lại thuê xe (cả đi, về, nội vùng).
- Xếp phòng: quy hoạch động, tổng tiền/đêm nhỏ nhất, đủ chỗ, không vượt số phòng; hoà thì ít phòng hơn.
  Một khách sạn không đủ -> chia 2 khách sạn cùng mức; vẫn không đủ -> cảnh báo THIEU_PHONG.
- Ăn: quán cùng mức đủ sức chứa, rẻ nhất; không quán nào đủ -> chia đoàn nhiều quán, cảnh báo.
- Hoạt động theo mục đích (muc_goi.json); điểm có sức chứa < đoàn bị bỏ, ghi lý do. Phát sinh 5%.
"""
import argparse
import json
import math
import re
import unicodedata
from pathlib import Path

THU_MUC = Path(__file__).resolve().parent
TEN_GOI = {"tiet_kiem": "Tiết kiệm", "can_bang": "Cân bằng", "day_du": "Đầy đủ"}
TEN_MD = {"nghi_duong": "Nghỉ dưỡng", "gan_ket": "Gắn kết đội nhóm", "ca_hai": "Nghỉ dưỡng + gắn kết"}


def doc(ten):
    return json.loads((THU_MUC / ten).read_text(encoding="utf-8"))


D = {k: doc(k + ".json") for k in ("diem_den", "di_chuyen", "khach_san", "nha_hang", "hoat_dong", "muc_goi")}
VIDEO = doc("video_review.json")["video"] if (THU_MUC / "video_review.json").exists() else {}


def khong_dau(s):
    s = unicodedata.normalize("NFD", str(s).lower()).replace("đ", "d")
    return "".join(c for c in s if unicodedata.category(c) != "Mn").strip()


def vnd(x):
    return f"{int(round(x)):,}".replace(",", ".") + "đ"


def doc_tien(s):
    """'150tr', '150 triệu', '3.5tr', '800k', '150000000' -> VND."""
    t = khong_dau(s).replace(" ", "").replace(",", ".")
    m = re.fullmatch(r"([\d.]+)(ty|trieu|tr|k|nghin|d)?", t)
    if not m:
        raise SystemExit(f"Không hiểu số tiền: {s}")
    so = float(m.group(1)) if m.group(2) else float(m.group(1).replace(".", ""))
    return int(so * {"ty": 1e9, "trieu": 1e6, "tr": 1e6, "k": 1e3, "nghin": 1e3, "d": 1, None: 1}[m.group(2)])


def tim_noi(s, ds, loai):
    k = khong_dau(s)
    for x in ds:
        if k in (khong_dau(x["id"]), khong_dau(x["ten"])) or k in khong_dau(x["ten"]):
            return x
    raise SystemExit(f"{loai} '{s}' không có trong dữ liệu. Có: " + ", ".join(x["ten"] for x in ds))


# ------------------------------------------------------------------ xếp phòng (quy hoạch động)
def xep_phong(n, loai_phong):
    """Cơ cấu phòng rẻ nhất đủ chỗ cho n người, mỗi loại ≤ so_luong. Trả (tiền/đêm, {sức chứa: số phòng}) hoặc None."""
    INF = (float("inf"), 0)
    dp = [INF] * (n + 1)
    chon = [None] * (n + 1)
    dp[0], chon[0] = (0, 0), {}
    for p in loai_phong:
        for _ in range(p["so_luong"]):                     # đơn giản và đủ nhanh: n ≤ 500, ≤ 120 phòng / loại
            moi = dp[:]
            mchon = chon[:]
            for c in range(n, -1, -1):
                if dp[c] == INF:
                    continue
                c2 = min(n, c + p["suc_chua"])
                ung = (dp[c][0] + p["gia_dem"], dp[c][1] + 1)
                if ung < moi[c2] and chon[c].get(p["suc_chua"], 0) < p["so_luong"]:
                    moi[c2] = ung
                    mchon[c2] = chon[c] | {p["suc_chua"]: chon[c].get(p["suc_chua"], 0) + 1}
            if moi == dp:
                break
            dp, chon = moi, mchon
    return None if dp[n] == INF else (dp[n][0], dict(sorted(chon[n].items())))


def chon_khach_san(den, muc, n, md):
    ks = [k for k in D["khach_san"] if k["diem_den"] == den and k["muc"] == muc]
    def diem(k):
        return k["phu_hop"]["nghi_duong"] + k["phu_hop"]["gan_ket"] if md == "ca_hai" else k["phu_hop"][md]
    ung = []
    for k in ks:
        x = xep_phong(n, k["loai_phong"])
        if x:
            ung.append((-diem(k), x[0], k, x))
    if ung:
        _, gia, k, (tien, co_cau) = min(ung, key=lambda u: (u[0], u[1]))
        return [{"ks": k, "nguoi": n, "tien_dem": tien, "co_cau": co_cau}], []
    # chia 2 khách sạn: khách sạn lớn nhất lấp đầy, phần còn lại sang khách sạn khác cùng mức
    ks = sorted(ks, key=lambda k: -k["suc_chua_toi_da"])
    if len(ks) >= 2:
        a = ks[0]
        n1 = a["suc_chua_toi_da"]
        x1 = xep_phong(n1, a["loai_phong"])
        for b in ks[1:]:
            x2 = xep_phong(n - n1, b["loai_phong"]) if n - n1 > 0 else None
            if x1 and x2:
                return ([{"ks": a, "nguoi": n1, "tien_dem": x1[0], "co_cau": x1[1]},
                         {"ks": b, "nguoi": n - n1, "tien_dem": x2[0], "co_cau": x2[1]}],
                        ["CHIA_2_KHACH_SAN: không khách sạn nào mức này đủ chỗ cho cả đoàn"])
    return [], ["THIEU_PHONG: các khách sạn mức này không đủ chỗ cho cả đoàn"]


# ------------------------------------------------------------------ di chuyển
def di_chuyen(tu, den, n, ngay, muc):
    dc, quy = D["di_chuyen"], D["muc_goi"]["goi"][muc]
    t = next(x for x in dc["tuyen"] if x["tu"] == tu and x["den"] == den["id"])
    xe = next(x for x in dc["xe"] if x["loai"] == quy["xe"])
    so_xe = math.ceil(n / xe["so_cho"])
    bay = t["duong_bay"] and (t["duong_bo_km"] is None or t["duong_bo_gio"] > quy["may_bay_khi_duong_bo_tren_gio"])
    dong, canh = [], []
    noi_vung = dc["km_noi_vung_moi_ngay"] * ngay
    if bay:
        b = t["duong_bay"]
        dong.append(("Di chuyển", f'Vé máy bay khứ hồi {b["chang"]} (phổ thông)', 2 * n, b["gia_ve_mot_chieu"], b["uoc_tinh"]))
        km = 2 * b["km_san_bay_toi_diem_den"] + noi_vung
        gio = b["gio_bay"] + b["gio_thu_tuc"] + b["km_san_bay_toi_diem_den"] / 50
        cach = f'máy bay {b["chang"]} + xe {xe["loai"]}'
    elif t["duong_bo_km"] is not None:
        km = 2 * t["duong_bo_km"] + noi_vung
        gio = t["duong_bo_gio"]
        cach = (f'xe {xe["loai"]} di chuyển nội vùng (điểm đi trùng điểm đến)' if t["duong_bo_km"] == 0
                else f'xe {xe["loai"]} đường bộ {t["duong_bo_km"]} km')
        if t["duong_bo_gio"] > quy["may_bay_khi_duong_bo_tren_gio"]:
            canh.append(f'DUONG_BO_DAI: {t["duong_bo_gio"]} giờ một chiều, không có chặng bay trong dữ liệu')
    else:
        return None
    km_tinh = max(km, dc["km_toi_thieu_moi_ngay"] * ngay)
    dong.append(("Di chuyển", f'Thuê {so_xe} xe {xe["loai"]} ({km_tinh} km, có tài xế)', so_xe * km_tinh, xe["don_gia_km"], True))
    if ngay > 1:
        dong.append(("Di chuyển", "Phí lưu đêm tài xế", so_xe * (ngay - 1), dc["phi_luu_dem_tai_xe"], True))
    if t["co_pha"] and not bay:
        dong.append(("Di chuyển", "Vé phà khứ hồi", 2 * n, dc["phi_pha_nguoi_luot"], True))
    return {"cach": cach, "gio_mot_chieu": round(gio, 1), "dong": dong, "canh_bao": canh}


# ------------------------------------------------------------------ một gói
def mot_goi(tu, den, n, ngay, md, muc):
    dong, canh = [], []
    dc = di_chuyen(tu, den, n, ngay, muc)
    if dc is None:
        return None
    dong += dc["dong"]
    canh += dc["canh_bao"]
    ks_chon = []
    if ngay > 1:
        ks_chon, c = chon_khach_san(den["id"], muc, n, md)
        canh += c
        for x in ks_chon:
            mo_ta = " + ".join(f"{v} phòng {k} người" for k, v in x["co_cau"].items())
            dong.append(("Lưu trú", f'{x["ks"]["ten"]} {x["ks"]["hang_sao"]}★: {mo_ta} ({x["nguoi"]} người)',
                         ngay - 1, x["tien_dem"], True))
    so_bua = max(1, 2 * ngay - 1)
    nh = sorted((x for x in D["nha_hang"] if x["diem_den"] == den["id"] and x["muc"] == muc), key=lambda x: x["gia_nguoi_bua"])
    du = [x for x in nh if x["suc_chua"] >= n]
    if du:
        quan = [(du[0], n)]
    else:
        quan, con = [], n
        for x in sorted(nh, key=lambda x: -x["suc_chua"]):
            if con <= 0:
                break
            quan.append((x, min(con, x["suc_chua"])))
            con -= x["suc_chua"]
        canh.append(f"CHIA_QUAN: không quán nào đủ {n} chỗ, chia đoàn {len(quan)} quán")
        if con > 0:
            canh.append("THIEU_SUC_CHUA_AN: tổng sức chứa các quán không đủ")
    for x, so in quan:
        dong.append(("Ăn uống", f'{x["ten"]}: {so} người × {so_bua} bữa chính (sức chứa {x["suc_chua"]})', so * so_bua, x["gia_nguoi_bua"], True))
    loai_can = D["muc_goi"]["hoat_dong_theo_muc_dich"][md][muc]
    hd = [x for x in D["hoat_dong"] if x["diem_den"] == den["id"] and muc in x["muc"]]
    bo = []
    if "tham_quan" in loai_can:
        tq = [x for x in hd if x["loai"] == "tham_quan" and (md == "ca_hai" or md in x["muc_dich"])]
        bo = [x for x in tq if x["suc_chua"] and x["suc_chua"] < n]
        tq = [x for x in tq if not (x["suc_chua"] and x["suc_chua"] < n)]
        tq.sort(key=lambda x: (x["gia_nguoi"], x["id"]), reverse=(muc == "day_du"))
        if muc == "can_bang":
            tq = tq[len(tq) // 3:] + tq[:len(tq) // 3]
        for x in tq[:max(1, ngay)]:
            dong.append(("Hoạt động", x["ten"] + " (tham quan)", n, x["gia_nguoi"], x["uoc_tinh"]))
    for loai in loai_can:
        if loai in ("tham_quan", "tu_do") or (loai == "gala_dinner" and ngay == 1):
            continue
        x = next((h for h in hd if h["loai"] == loai), None)
        if x:
            dong.append(("Hoạt động", x["ten"], n, x["gia_nguoi"], x["uoc_tinh"]))
    if "tu_do" in loai_can:
        dong.append(("Hoạt động", "Thời gian tự do nghỉ ngơi tại nơi ở", n, 0, False))
    if bo:
        canh.append("BO_DIEM_SUC_CHUA: " + "; ".join(f'{x["ten"]} (tối đa {x["suc_chua"]} khách/lượt)' for x in bo))
    tam = sum(sl * dg for _, _, sl, dg, _ in dong)
    ps = D["muc_goi"]["phat_sinh_ty_le"]
    dong.append(("Phát sinh", f"Dự phòng phát sinh {int(ps * 100)}%", 1, round(tam * ps), True))
    tong = tam * (1 + ps)
    return {"goi": muc, "ten_goi": TEN_GOI[muc], "di_chuyen": dc["cach"], "gio_di_mot_chieu": dc["gio_mot_chieu"],
            "dong": [{"hang_muc": h, "mo_ta": m, "so_luong": sl, "don_gia": dg, "thanh_tien": round(sl * dg), "uoc_tinh": u}
                     for h, m, sl, dg, u in dong],
            "tong": round(tong), "moi_nguoi": round(tong / n), "canh_bao": canh}


def ba_goi(tu, den, n, ngay, md, ngan_sach=None):
    out = []
    for muc in TEN_GOI:
        g = mot_goi(tu, den, n, ngay, md, muc)
        if g is None:
            continue
        if ngan_sach:
            g["chenh_ngan_sach"] = g["tong"] - ngan_sach
            g["trong_ngan_sach"] = g["tong"] <= ngan_sach
        out.append(g)
    if ngan_sach:
        for i, g in enumerate(out):
            if not g["trong_ngan_sach"]:
                g["giai_thich_vuot"] = giai_thich(g, out[i - 1] if i else None, ngan_sach, tu, den, n, ngay, md)
    return out


def giai_thich(g, thap_hon, ns, tu, den, n, ngay, md):
    vuot = g["tong"] - ns
    top = sorted((d for d in g["dong"] if d["hang_muc"] != "Phát sinh"), key=lambda d: -d["thanh_tien"])[:3]
    cat = []
    if thap_hon:
        cat.append({"cach": f'Hạ xuống gói {thap_hon["ten_goi"]}', "tiet_kiem": g["tong"] - thap_hon["tong"], "tong_sau": thap_hon["tong"]})
    gala = next((d for d in g["dong"] if "Gala" in d["mo_ta"]), None)
    if gala:
        tk = round(gala["thanh_tien"] * 1.05)
        cat.append({"cach": "Bỏ gala dinner", "tiet_kiem": tk, "tong_sau": g["tong"] - tk})
    if ngay > 1:
        g2 = mot_goi(tu, den, n, ngay - 1, md, g["goi"])
        if g2:
            cat.append({"cach": f"Bớt 1 ngày ({ngay - 1} ngày)", "tiet_kiem": g["tong"] - g2["tong"], "tong_sau": g2["tong"]})
    return {"vuot": vuot, "vuot_phan_tram": round(100 * vuot / ns, 1),
            "khoan_lon_nhat": [{"mo_ta": d["mo_ta"], "thanh_tien": d["thanh_tien"]} for d in top],
            "cach_cat": sorted(cat, key=lambda c: c["tiet_kiem"]),
            "ve_lai_ngan_sach": [c["cach"] for c in cat if c["tong_sau"] <= ns]}


def goi_y_dia_diem(tu, n, ngay, md, ns, so_goi_y=3):
    ung = []
    for den in D["diem_den"]["diem_den"]:
        gs = ba_goi(tu, den, n, ngay, md, ns)
        trong = [g for g in gs if g["trong_ngan_sach"] and not any(c.startswith(("THIEU_PHONG", "THIEU_SUC_CHUA")) for c in g["canh_bao"])]
        if not trong:
            continue
        tot = trong[-1]
        ph = den["phu_hop"]
        diem_md = ph["nghi_duong"] + ph["gan_ket"] if md == "ca_hai" else 2 * ph[md]
        diem = diem_md * 10 + list(TEN_GOI).index(tot["goi"]) * 4 - tot["gio_di_mot_chieu"]
        ung.append({"diem_den": den, "diem": round(diem, 1), "goi_tot_nhat": tot, "ba_goi": gs})
    ung.sort(key=lambda u: -u["diem"])
    if ung:
        return {"goi_y": ung[:so_goi_y], "so_noi_vua_ngan_sach": len(ung)}
    re_nhat = min(((den, g) for den in D["diem_den"]["diem_den"] for g in ba_goi(tu, den, n, ngay, md)
                   if not any(c.startswith(("THIEU_PHONG", "THIEU_SUC_CHUA")) for c in g["canh_bao"])),
                  key=lambda x: x[1]["tong"])
    return {"goi_y": [], "ngan_sach_toi_thieu": re_nhat[1]["tong"], "noi_re_nhat": re_nhat[0]["ten"]}


# ------------------------------------------------------------------ in ra
def in_goi(g, ns):
    s = [f'\n■ Gói {g["ten_goi"]}: {vnd(g["tong"])} cả đoàn · {vnd(g["moi_nguoi"])}/người · {g["di_chuyen"]} (~{g["gio_di_mot_chieu"]} giờ/chiều)']
    if ns:
        s.append(f'  {"TRONG" if g["trong_ngan_sach"] else "VƯỢT"} ngân sách: chênh {vnd(abs(g["chenh_ngan_sach"]))}')
    for d in g["dong"]:
        s.append(f'  - [{d["hang_muc"]}] {d["mo_ta"]}: {d["so_luong"]} × {vnd(d["don_gia"])} = {vnd(d["thanh_tien"])}{" (ước tính)" if d["uoc_tinh"] else ""}')
    for c in g["canh_bao"]:
        s.append(f"  ! {c}")
    gt = g.get("giai_thich_vuot")
    if gt:
        s.append(f'  Vì sao vượt: vượt {vnd(gt["vuot"])} ({gt["vuot_phan_tram"]}%). Khoản lớn nhất: ' +
                 "; ".join(f'{k["mo_ta"][:50]} {vnd(k["thanh_tien"])}' for k in gt["khoan_lon_nhat"]))
        for c in gt["cach_cat"]:
            s.append(f'    · {c["cach"]}: tiết kiệm {vnd(c["tiet_kiem"])} → còn {vnd(c["tong_sau"])}')
    return "\n".join(s)


def in_video(den_id):
    v = VIDEO.get(den_id) or []
    return "\n".join(f'  ▶ [{x["loai"]}] {x["tieu_de"][:70]} · {x["kenh"]} · {x["url"]}' for x in v) or "  (chưa có video)"


def main():
    ap = argparse.ArgumentParser(description="Bộ tính tham chiếu: địa điểm -> chi phí 3 gói, hoặc kinh phí -> địa điểm")
    ap.add_argument("--tu", required=True, help="điểm đi: Hà Nội, Hải Phòng, Đà Nẵng, TP.HCM, Cần Thơ (hoặc mã)")
    ap.add_argument("--den", help="điểm đến (bỏ trống = gợi ý theo kinh phí)")
    ap.add_argument("--nguoi", type=int, required=True)
    ap.add_argument("--ngay", type=int, default=3)
    ap.add_argument("--muc-dich", choices=list(TEN_MD), default="ca_hai")
    ap.add_argument("--ngan-sach", help="vd 150tr, 3.5tr, 800k")
    ap.add_argument("--moi-nguoi", action="store_true", help="ngân sách tính cho mỗi người")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    gh = D["muc_goi"]["gioi_han"]
    if not gh["so_nguoi"][0] <= a.nguoi <= gh["so_nguoi"][1] or not gh["so_ngay"][0] <= a.ngay <= gh["so_ngay"][1]:
        raise SystemExit(f'Ngoài phạm vi: số người {gh["so_nguoi"]}, số ngày {gh["so_ngay"]}')
    tu = tim_noi(a.tu, D["diem_den"]["diem_di"], "Điểm đi")["id"]
    ns = doc_tien(a.ngan_sach) * (a.nguoi if a.moi_nguoi else 1) if a.ngan_sach else None
    dau = f'{a.nguoi} người · {a.ngay} ngày · {TEN_MD[a.muc_dich]}' + (f' · ngân sách đã hiểu: {vnd(ns)} cho {a.nguoi} người' if ns else "")
    if a.den:
        den = tim_noi(a.den, D["diem_den"]["diem_den"], "Điểm đến")
        kq = ba_goi(tu, den, a.nguoi, a.ngay, a.muc_dich, ns)
        if a.json:
            print(json.dumps({"diem_den": den["id"], "ba_goi": kq, "video": VIDEO.get(den["id"], [])}, ensure_ascii=False, indent=1))
            return
        print(f'{a.tu} → {den["ten"]} · {dau}')
        for g in kq:
            print(in_goi(g, ns))
        print("\nVideo review:\n" + in_video(den["id"]))
        return
    if not ns:
        raise SystemExit("Cần --den hoặc --ngan-sach")
    kq = goi_y_dia_diem(tu, a.nguoi, a.ngay, a.muc_dich, ns)
    if a.json:
        print(json.dumps(kq, ensure_ascii=False, indent=1, default=str))
        return
    print(f'Gợi ý từ {a.tu} · {dau}')
    if not kq["goi_y"]:
        print(f'Không nơi nào vừa ngân sách. Cần tối thiểu {vnd(kq["ngan_sach_toi_thieu"])} (gói rẻ nhất: {kq["noi_re_nhat"]}).')
        return
    print(f'{kq["so_noi_vua_ngan_sach"]} nơi vừa ngân sách. Top {len(kq["goi_y"])}:')
    for i, u in enumerate(kq["goi_y"], 1):
        d, g = u["diem_den"], u["goi_tot_nhat"]
        print(f'\n{i}. {d["ten"]} ({d["mien"]}) · điểm {u["diem"]} · {d["mo_ta"]}')
        for x in u["ba_goi"]:
            print(f'   {x["ten_goi"]:9s} {vnd(x["tong"]):>16s} ({vnd(x["moi_nguoi"])}/người) {"✓" if x["trong_ngan_sach"] else "vượt"}')
        print(f'   → đề xuất gói {g["ten_goi"]}, {g["di_chuyen"]}')
        print(in_video(d["id"]))


if __name__ == "__main__":
    main()
