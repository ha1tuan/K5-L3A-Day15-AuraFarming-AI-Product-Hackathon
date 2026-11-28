"""Lõi tính toán — code thuần (spec.md §4: "model không trả số tổng — tiền, số phòng, số xe do code tính").

Model chỉ đề xuất HẠNG MỤC và ĐƠN GIÁ tham khảo (gắn nhãn "ước tính"); mọi phép nhân, cộng, phát sinh 5%,
cơ cấu phòng rẻ nhất, số xe, so ngân sách, giải thích vượt đều tính ở đây.

    xep_phong(loai_phong, so_nguoi)        -> cơ cấu phòng rẻ nhất đủ chỗ (quy hoạch động, tôn trọng số phòng còn)
    tinh_goi(req, goi)                     -> bảng khoản mục, tổng, mỗi người
    giai_thich_vuot(req, goi_tinh, thap_hon, goi_raw) -> đoạn giải thích có số
    fmt_vnd(x)                             -> "1.250.000đ"
"""
import copy
import math

PACKAGES = [("tiet_kiem", "Tiết kiệm"), ("can_bang", "Cân bằng"), ("cao_cap", "Cao cấp")]
PHAT_SINH = 0.05

# Đơn giá mặc định khi model đưa giá thiếu / ≤ 0 (chặn "giá 0đ" từ dữ liệu bị chèn lệnh) — (tự ước tính) của nhóm.
DEFAULTS = {
    "xe": {"tiet_kiem": 9_000_000, "can_bang": 11_000_000, "cao_cap": 14_000_000},       # xe 45 chỗ / chuyến khứ hồi
    "ve": {"tiet_kiem": 2_200_000, "can_bang": 3_000_000, "cao_cap": 4_500_000},         # vé máy bay khứ hồi / người
    "phong": {"tiet_kiem": 250_000, "can_bang": 450_000, "cao_cap": 900_000},            # mỗi chỗ / đêm
    "bua": {"tiet_kiem": 150_000, "can_bang": 250_000, "cao_cap": 450_000},
    "hoat_dong": {"tiet_kiem": 100_000, "can_bang": 200_000, "cao_cap": 400_000},
    "xe_tai_cho": {"tiet_kiem": 2_500_000, "can_bang": 3_000_000, "cao_cap": 4_000_000},  # xe / ngày
}


def fmt_vnd(x):
    return "{:,}".format(int(round(x))).replace(",", ".") + "đ"


def round_k(x):
    """Làm tròn đến 1.000đ."""
    return int(round(x / 1000.0)) * 1000


def _price(v, kind, level, flags, label):
    try:
        v = int(float(v))
    except (TypeError, ValueError):
        v = 0
    if v <= 0:
        flags.append("Đơn giá %s không hợp lệ (≤ 0đ hoặc thiếu) → thay bằng đơn giá ước tính mặc định %s."
                     % (label, fmt_vnd(DEFAULTS[kind][level])))
        return DEFAULTS[kind][level]
    return v


# --- Xếp phòng ------------------------------------------------------------------------------
def xep_phong(loai_phong, so_nguoi):
    """Cơ cấu phòng rẻ nhất (tổng tiền / đêm) có tổng chỗ ≥ so_nguoi.
    loai_phong: [{"ten", "suc_chua", "gia_dem", "so_phong_con" (None = không giới hạn)}]
    Trả {"co_cau": [(loai, so_phong)], "so_cho", "tien_dem", "thieu": số chỗ còn thiếu (0 nếu đủ)}."""
    types = [t for t in loai_phong if t["suc_chua"] > 0]
    max_c = max(t["suc_chua"] for t in types)
    cap = so_nguoi + max_c
    INF = float("inf")
    # best[s] = (chi phí, list số phòng từng loại) để có ĐÚNG s chỗ; bounded knapsack bằng cách duyệt từng loại.
    best = [INF] * (cap + 1)
    choice = [None] * (cap + 1)
    best[0] = 0
    choice[0] = [0] * len(types)
    for i, t in enumerate(types):
        limit = t.get("so_phong_con")
        limit = math.ceil(so_nguoi / t["suc_chua"]) + 1 if limit is None else int(limit)
        new_best, new_choice = best[:], [c[:] if c else None for c in choice]
        for s in range(cap + 1):
            if best[s] == INF:
                continue
            for k in range(1, limit + 1):
                s2 = min(cap, s + k * t["suc_chua"])
                cost = best[s] + k * t["gia_dem"]
                if cost < new_best[s2]:
                    new_best[s2] = cost
                    c = choice[s][:]
                    c[i] += k
                    new_choice[s2] = c
        best, choice = new_best, new_choice
    ok = [s for s in range(so_nguoi, cap + 1) if best[s] < INF]
    if ok:
        s = min(ok, key=lambda x: (best[x], x))
        thieu = 0
    else:  # không đủ chỗ với số phòng còn: lấy nhiều chỗ nhất có thể
        s = max(x for x in range(cap + 1) if best[x] < INF)
        thieu = so_nguoi - s
    co_cau = [(types[i], n) for i, n in enumerate(choice[s]) if n]
    return {"co_cau": co_cau, "so_cho": sum(t["suc_chua"] * n for t, n in co_cau),
            "tien_dem": sum(t["gia_dem"] * n for t, n in co_cau), "thieu": thieu}


# --- Tính một gói ----------------------------------------------------------------------------
def tinh_goi(req, level, goi):
    """req: {"so_nguoi", "so_ngay", "so_dem", "khong_muon": [..]} · goi: hạng mục model đề xuất.
    Trả {"lines": [(nhóm, hạng mục, số lượng, đơn vị, đơn giá, thành tiền)], "tong", "moi_nguoi", "flags", ...}."""
    n, days, nights = req["so_nguoi"], req["so_ngay"], req["so_dem"]
    flags, lines = [], []
    goi = goi or {}

    # Di chuyển chặng chính
    dc = goi.get("di_chuyen") or {}
    kieu = "ve" if str(dc.get("kieu", "")).lower() in ("ve", "vé", "may_bay", "máy bay") else "xe"
    if kieu == "ve":
        gia = _price(dc.get("don_gia"), "ve", level, flags, "vé")
        lines.append(("Di chuyển", dc.get("loai") or "Vé máy bay khứ hồi", n, "vé", gia, n * gia))
    else:
        suc = int(dc.get("suc_chua_xe") or 45)
        suc = suc if suc > 0 else 45
        so_xe = math.ceil(n / suc)
        gia = _price(dc.get("don_gia"), "xe", level, flags, "xe")
        lines.append(("Di chuyển", "%s (%d chỗ, khứ hồi)" % (dc.get("loai") or "Xe du lịch", suc), so_xe, "xe", gia, so_xe * gia))
    tai_cho = goi.get("xe_tai_cho") or {}
    if kieu == "ve" and tai_cho:
        suc = int(tai_cho.get("suc_chua") or 45) or 45
        so_xe = math.ceil(n / suc)
        gia = _price(tai_cho.get("don_gia_xe_ngay"), "xe_tai_cho", level, flags, "xe tại chỗ")
        lines.append(("Di chuyển", "%s tại điểm đến (chở %d khách / xe)" % (tai_cho.get("loai") or "Xe đưa đón", suc),
                      so_xe * days, "xe·ngày", gia, so_xe * days * gia))

    # Lưu trú
    phong = None
    if nights > 0:
        lt = goi.get("luu_tru") or {}
        types = []
        for t in lt.get("loai_phong") or []:
            try:
                c = int(t.get("suc_chua") or 0)
            except (TypeError, ValueError):
                c = 0
            if c <= 0:
                continue
            try:
                p = int(float(t.get("gia_dem") or 0))
            except (TypeError, ValueError):
                p = 0
            if p <= 0:
                p = DEFAULTS["phong"][level] * c
                flags.append("Đơn giá phòng \"%s\" không hợp lệ (≤ 0đ hoặc thiếu) → thay bằng ước tính mặc định %s/đêm."
                             % (t.get("ten") or c, fmt_vnd(p)))
            con = t.get("so_phong_con")
            types.append({"ten": t.get("ten") or "Phòng %d người" % c, "suc_chua": c, "gia_dem": p,
                          "so_phong_con": int(con) if isinstance(con, (int, float)) and con >= 0 else None})
        if not types:
            types = [{"ten": "Phòng 2 người", "suc_chua": 2, "gia_dem": DEFAULTS["phong"][level] * 2, "so_phong_con": None}]
            flags.append("Thiếu loại phòng → dùng phòng 2 người giá ước tính mặc định.")
        phong = xep_phong(types, n)
        noi = lt.get("mo_ta") or "Cơ sở lưu trú"
        for t, k in phong["co_cau"]:
            lines.append(("Lưu trú", "%s — %s (%d người/phòng)" % (noi, t["ten"], t["suc_chua"]),
                          k * nights, "phòng·đêm", t["gia_dem"], k * nights * t["gia_dem"]))
        if phong["thieu"] > 0:
            add = min(types, key=lambda t: t["gia_dem"] / t["suc_chua"])
            k = math.ceil(phong["thieu"] / add["suc_chua"])
            flags.append("⚠ Thiếu phòng: %s chỉ còn đủ %d chỗ cho %d người (thiếu %d chỗ). Cần thêm một cơ sở lưu trú "
                         "cùng mức hoặc đổi cơ sở; tạm tính %d %s ở cơ sở thứ hai theo cùng đơn giá — cần xác nhận."
                         % (noi, phong["so_cho"], n, phong["thieu"], k, add["ten"].lower()))
            lines.append(("Lưu trú", "Cơ sở thứ hai cùng mức (cần tìm thêm) — %s" % add["ten"],
                          k * nights, "phòng·đêm", add["gia_dem"], k * nights * add["gia_dem"]))

    # Ăn uống
    au = goi.get("an_uong") or {}
    so_bua = max(1, 2 * days if days > 1 or nights > 0 else 2)
    gia = _price(au.get("don_gia_bua"), "bua", level, flags, "bữa ăn")
    lines.append(("Ăn uống", au.get("mo_ta") or "Bữa chính theo đoàn", n * so_bua, "suất", gia, n * so_bua * gia))

    # Hoạt động
    banned = [b.lower() for b in req.get("khong_muon") or []]
    for hd in goi.get("hoat_dong") or []:
        ten = hd.get("ten") or "Hoạt động"
        if any(b and b in ten.lower() for b in banned):
            flags.append("Bỏ \"%s\" theo yêu cầu không muốn." % ten)
            continue
        gia = _price(hd.get("don_gia_nguoi"), "hoat_dong", level, flags, "hoạt động \"%s\"" % ten)
        lines.append(("Hoạt động", ten + (" (team building)" if hd.get("team_building") else ""), n, "người", gia, n * gia))
    gala = goi.get("gala") or {}
    no_gala = any("gala" in b or "tiệc tối" in b for b in banned)
    if gala.get("co") and not no_gala:
        gia = _price(gala.get("don_gia_nguoi"), "hoat_dong", level, flags, "gala")
        lines.append(("Hoạt động", "Gala dinner / tiệc tối cả đoàn", n, "người", gia, n * gia))

    sub = sum(l[5] for l in lines)
    ps = round_k(sub * PHAT_SINH)
    lines.append(("Phát sinh", "Dự phòng phát sinh 5%", 1, "khoản", ps, ps))
    tong = sub + ps
    return {"level": level, "lines": lines, "tong": tong, "moi_nguoi": round_k(tong / n), "flags": flags,
            "phong": phong, "kieu_di": kieu, "co_luu_tru": nights > 0}


def by_group(g):
    out = {}
    for grp, _, _, _, _, tt in g["lines"]:
        if grp != "Phát sinh":
            out[grp] = out.get(grp, 0) + tt
    return out


def variant(req, level, goi_raw, change):
    """Tính lại gói sau khi cắt giảm (để số tiết kiệm khớp đúng bảng)."""
    g = copy.deepcopy(goi_raw)
    change(g)
    return tinh_goi(req, level, g)


def cat_giam(req, level, goi_raw, goi_thap_raw):
    """Các phương án cắt giảm, mỗi phương án tính lại bằng code: (mô tả, tổng sau cắt)."""
    opts = []
    if goi_thap_raw and req["so_dem"] > 0:
        def lt(g):
            g["luu_tru"] = copy.deepcopy(goi_thap_raw.get("luu_tru"))
        opts.append(("Hạ lưu trú về mức của gói thấp hơn liền kề", variant(req, level, goi_raw, lt)["tong"]))
    if (goi_raw.get("gala") or {}).get("co"):
        def ng(g):
            g["gala"] = {"co": False}
        opts.append(("Bỏ gala dinner", variant(req, level, goi_raw, ng)["tong"]))
    hds = goi_raw.get("hoat_dong") or []
    if hds:
        top = max(range(len(hds)), key=lambda i: float(hds[i].get("don_gia_nguoi") or 0))
        def bh(g):
            g["hoat_dong"] = [h for i, h in enumerate(g.get("hoat_dong") or []) if i != top]
        opts.append(("Bỏ hoạt động trả phí đắt nhất (\"%s\")" % hds[top].get("ten"), variant(req, level, goi_raw, bh)["tong"]))
    if goi_thap_raw and goi_thap_raw.get("di_chuyen"):
        def dc(g):
            g["di_chuyen"] = copy.deepcopy(goi_thap_raw.get("di_chuyen"))
            if "xe_tai_cho" in goi_thap_raw:
                g["xe_tai_cho"] = copy.deepcopy(goi_thap_raw.get("xe_tai_cho"))
        t = variant(req, level, goi_raw, dc)["tong"]
        opts.append(("Dùng phương tiện của gói thấp hơn liền kề", t))
    if req["so_dem"] >= 1 and req["so_ngay"] >= 2:
        r2 = dict(req, so_ngay=req["so_ngay"] - 1, so_dem=req["so_dem"] - 1)
        opts.append(("Bớt 1 ngày 1 đêm (%d ngày %d đêm)" % (r2["so_ngay"], r2["so_dem"]), tinh_goi(r2, level, goi_raw)["tong"]))
    return opts


def giai_thich_vuot(req, budget, g, g_thap, goi_raw, goi_thap_raw):
    tong = g["tong"]
    vuot = tong - budget
    lines = ["- **Vượt ngân sách %s (%.1f%%)**: tổng %s − ngân sách %s."
             % (fmt_vnd(vuot), 100.0 * vuot / budget, fmt_vnd(tong), fmt_vnd(budget))]
    cur = by_group(g)
    if g_thap:
        low = by_group(g_thap)
        diffs = sorted(((k, cur.get(k, 0) - low.get(k, 0)) for k in set(cur) | set(low)), key=lambda x: -x[1])
        diffs = [d for d in diffs if d[1] > 0][:3]
        if len(diffs) < 2:
            diffs = sorted(cur.items(), key=lambda x: -x[1])[:2]
            lines.append("- Khoản lớn nhất: " + "; ".join("%s %s" % (k.lower(), fmt_vnd(v)) for k, v in diffs) + ".")
        else:
            lines.append("- Khoản tăng nhiều nhất so với gói thấp hơn liền kề: "
                         + "; ".join("%s +%s" % (k.lower(), fmt_vnd(v)) for k, v in diffs) + ".")
    else:
        top = sorted(cur.items(), key=lambda x: -x[1])[:2]
        lines.append("- Hai khoản lớn nhất: " + "; ".join("%s %s" % (k.lower(), fmt_vnd(v)) for k, v in top) + ".")
    opts = [(d, t) for d, t in cat_giam(req, g["level"], goi_raw, goi_thap_raw) if t < tong]
    opts.sort(key=lambda x: x[1])
    if opts:
        lines.append("- Cách cắt giảm (tính lại bằng code):")
        for d, t in opts[:3]:
            lines.append("  - %s: tiết kiệm %s → tổng còn %s%s" % (d, fmt_vnd(tong - t), fmt_vnd(t),
                                                                 " (trong ngân sách)" if t <= budget else ""))
    return "\n".join(lines)


# --- Render ---------------------------------------------------------------------------------
def bang_chi_phi(g, n):
    out = ["| Hạng mục | Số lượng | Đơn giá (ước tính) | Thành tiền |", "|---|---|---|---|"]
    for grp, ten, sl, dv, dg, tt in g["lines"]:
        out.append("| %s: %s | %s %s | %s | %s |" % (grp, ten, "{:,}".format(sl).replace(",", "."), dv, fmt_vnd(dg), fmt_vnd(tt)))
    out.append("| **Tổng cả đoàn** | | | **%s** |" % fmt_vnd(g["tong"]))
    out.append("| **Mỗi người** (%d người) | | | **%s** |" % (n, fmt_vnd(g["moi_nguoi"])))
    if g.get("phong"):
        p = g["phong"]
        out.append("")
        out.append("Cơ cấu phòng: " + " + ".join("%d × %s" % (k, t["ten"]) for t, k in p["co_cau"])
                   + " = %d chỗ cho %d người · %s/đêm" % (p["so_cho"], n, fmt_vnd(p["tien_dem"])))
    for f in g["flags"]:
        out.append("")
        out.append("> " + f)
    return "\n".join(out)
