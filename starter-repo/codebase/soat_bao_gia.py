"""Soát báo giá tour đoàn: tổng chi THẬT của công ty + chứng từ / hoá đơn (spec.md §1 bản 28/11).

Người dùng dán báo giá công ty tour gửi (giá / khách, mục "bao gồm", "không bao gồm") kèm số người, ngân sách.
Code (không model) bóc từng khoản "không bao gồm", quy ra tiền khi tính được (VAT theo % ghi trong báo giá, vé ghi
giá, tip, vé máy bay từ data/*.json), cộng ra **tổng chi thật** so với ngân sách, đối chiếu giá tham chiếu từ
bộ dữ liệu, rồi soát chứng từ theo data/quy_tac_chung_tu.json (hoá đơn VAT, chuyển khoản ≥ 5 triệu, trần phúc lợi,
khoản khó có hoá đơn) và liệt kê câu cần hỏi lại công ty tour.

    la_bao_gia(text) -> bool
    soat(text) -> str (markdown; bảng tiền đúng định dạng eval/check_outputs.py)

Số không có nguồn ghi "(ước tính)". Không đặt, không thanh toán, không phải tư vấn thuế.
"""
import json
import os
import re

import du_lieu
import planner

DATA = du_lieu.DATA
TIP_KHACH_NGAY = 50_000          # (tự ước tính) tip HDV + tài xế / khách / ngày khi báo giá không ghi số
VAT_MAC_DINH = 10                # % — báo giá không ghi mức thì tính mức thuế suất phổ thông, để không thiếu tiền
DAU_MUC = re.compile(r"^\W*(giá (tour )?)?(không|chưa) bao gồm|^\W*(giá (tour )?)?(đã )?bao gồm|^\W*(lưu ý|ghi chú|chính sách|"
                     r"điều kiện|giá trẻ em|trẻ em|hủy|huỷ|thanh toán|những thông tin)", re.I)


def kd(s):
    return du_lieu.khong_dau(s)


def la_bao_gia(text):
    t = kd(text)
    return bool(re.search(r"(khong|chua) bao gom", t) and re.search(r"bao gom", t)
                and re.search(r"[\d.]{5,}\s*(d|vnd|vnđ)\b", t.replace("đ", "d")))


def _so(s):
    return int(re.sub(r"[^\d]", "", s))


def _dong(text):
    out = []
    for x in re.split(r"\n|(?<=[.;])\s+(?=[-•+*·])|\s·\s", text):
        x = x.strip(" \t-•+*·:")
        if x:
            out.append(x)
    return out


def _muc(dong, dau):
    for i, x in enumerate(dong):
        m = dau.match(x)
        if m:
            out, du = [], x[m.end():].strip(" :")
            if du:
                out += [y.strip() for y in re.split(r";|\s-\s", du) if y.strip()]
            for y in dong[i + 1:]:
                if DAU_MUC.match(y):
                    break
                out.append(y)
            return out
    return []


def boc(text):
    """Bóc báo giá bằng code. Trả dict hoặc thiếu khoá khi không có trong chữ (không đoán)."""
    t = kd(text)
    dong = _dong(text)
    r = du_lieu.boc_tach(text)
    m = re.search(r"(\d+)\s*n\s*(\d+)\s*d\b", t)
    if m and not r["so_ngay"]:
        r["so_ngay"], r["so_dem"] = int(m.group(1)), int(m.group(2))
    gia = None
    for m in re.finditer(r"([\d.]{5,})\s*(?:đ|vnđ|vnd|dong)\s*/\s*(?:1\s*)?(khách|khach|người|nguoi|pax)", text, re.I):
        truoc = kd(text[max(0, m.start() - 40):m.start()])
        if "bao hiem" in truoc or "tieu chuan" in truoc or "suat" in truoc:
            continue
        gia = _so(m.group(1))
        break
    khong = _muc(dong, re.compile(r"^\W*(giá (tour )?)?(không|chưa) bao gồm", re.I))
    co = _muc(dong, re.compile(r"^\W*(giá (tour )?)?(đã )?bao gồm", re.I))
    return {"so_nguoi": r["so_nguoi"], "so_ngay": r["so_ngay"] or 1, "so_dem": r["so_dem"] if r["so_dem"] is not None else
            max(0, (r["so_ngay"] or 1) - 1), "ngan_sach": r["ngan_sach_tong"] or ((r["ngan_sach_moi_nguoi"] or 0) * (r["so_nguoi"] or 0))
            or None, "noi_xuat_phat": r["noi_xuat_phat"], "dia_diem": r["dia_diem"], "muc_dich": r["muc_dich"],
            "gia_moi_khach": gia, "bao_gom": co, "khong_bao_gom": khong,
            "luong_bq": _luong(t)}


def _luong(t):
    m = re.search(r"luong (binh quan|trung binh)[^\d]{0,20}([\d.,]+)\s*(trieu|tr)", t)
    return int(float(m.group(2).replace(",", ".")) * 1e6) if m else None


def _tien_trong(item):
    """Số tiền / khách ghi trong một khoản, vd '80k/ khách', '880.000 VND/ vé người lớn'."""
    t = kd(item)
    m = re.search(r"(\d+)\s*k\b", t) or re.search(r"([\d.]{5,})\s*(vnd|d\b|dong|ve\b|/)", t.replace("đ", "d"))
    if not m:
        return None
    v = int(m.group(1)) * 1000 if m.re.pattern.startswith(r"(\d+)\s*k") else _so(m.group(1))
    return v if 1000 <= v <= 20_000_000 else None


def phan_loai(item):
    t = kd(item)
    if re.search(r"\bvat\b|hoa don|thue gtgt|gia tri gia tang", t):
        m = re.search(r"(\d{1,2})\s*%", t)
        return "vat", int(m.group(1)) if m else None
    if re.search(r"\btip\b|\btip\b|\btip|tien tip|típ", t + " " + item.lower()):
        return "tip", None
    if re.search(r"ve may bay", t):
        return "may_bay", None
    if re.search(r"ca nhan|giat|dien thoai|minibar|ngoai chuong trinh", t) and not _tien_trong(item):
        return "ca_nhan", None
    if re.search(r"\bve\b|cap treo|tham quan|tro choi|ho boi|chuong trinh", t):
        v = _tien_trong(item)
        return ("ve_co_gia", v) if v else ("can_hoi", None)
    return "can_hoi", None


def soat(text, ket_qua=False):
    """ket_qua=True: trả dict có cấu trúc cho web (/api/quote-audit) thay vì markdown."""
    b = boc(text)
    n, gia = b["so_nguoi"], b["gia_moi_khach"]
    if not n or not gia:
        thieu = [x for x, ok in (("số người đi", n), ("giá / khách trong báo giá (vd 1.590.000đ/khách)", gia)) if not ok]
        msg = ("Để soát báo giá và tính tổng chi thật, mình cần thêm: " + "; ".join(thieu) + ". "
               "Mình không tự đoán vì sai số người / giá thì cả tổng chi sai.")
        return {"status": "ask_back", "message": msg} if ket_qua else msg
    quy = {q["id"]: q for q in json.load(open(os.path.join(DATA, "quy_tac_chung_tu.json"), encoding="utf-8"))["quy_tac"]}
    lines, hoi, ca_nhan, kho_hd = [("Giá tour theo báo giá", n, "khách", gia)], [], [], []
    vat_pct = None
    ngay = b["so_ngay"]
    for item in b["khong_bao_gom"]:
        loai, v = phan_loai(item)
        if loai == "vat":
            vat_pct = v or VAT_MAC_DINH
        elif loai == "tip":
            lines.append(("Tip hướng dẫn viên + tài xế — ước tính %s/khách/ngày" % planner.fmt_vnd(TIP_KHACH_NGAY),
                          n * ngay, "khách·ngày", TIP_KHACH_NGAY))
            kho_hd.append("tip hướng dẫn viên / tài xế")
        elif loai == "ve_co_gia":
            lines.append(("%s — giá ghi trong báo giá" % item.split("(")[0].strip().rstrip(".:")[:60], n, "khách", v))
            kho_hd.append(item.split("(")[0].strip().rstrip(".")[:40] + " (nếu mua tại cổng)")
        elif loai == "may_bay":
            tu, den = du_lieu.tim_diem_di(b["noi_xuat_phat"]), du_lieu.tim_diem_den(b["dia_diem"])
            t = du_lieu.tuyen(tu, den) if tu and den else None
            if t and t.get("duong_bay"):
                lines.append(("Vé máy bay khứ hồi %s (ước tính từ data/*.json)" % t["duong_bay"]["chang"], n, "vé",
                              2 * t["duong_bay"]["gia_ve_mot_chieu"]))
            else:
                hoi.append("Báo giá **chưa gồm vé máy bay** — xin giá vé đoàn khứ hồi cho %d người (chưa tính được vì thiếu nơi đi / đến)." % n)
        elif loai == "ca_nhan":
            ca_nhan.append(item[:80])
        else:
            hoi.append("Khoản \"%s\" chưa có số tiền — hỏi giá cụ thể cho %d người." % (item.strip().rstrip(".")[:90], n))
    vat_ghi_ro = vat_pct is not None
    if not vat_ghi_ro and not re.search(r"\bvat\b|hoa don", kd(" ".join(b["bao_gom"]))):
        hoi.insert(0, "Báo giá **không nói** giá đã gồm VAT và xuất hoá đơn cho công ty hay chưa — hỏi rõ trước khi duyệt "
                      "(tạm tính thêm %d%% để không thiếu tiền)." % VAT_MAC_DINH)
        vat_pct = VAT_MAC_DINH
    rows = [(ten, sl, dv, dg, sl * dg) for ten, sl, dv, dg in lines]
    if vat_pct:
        co_so = sum(r[4] for r in rows[:1])
        vat = planner.round_k(co_so * vat_pct / 100.0)
        rows.insert(1, ("Thuế VAT %d%% để công ty có hoá đơn (báo giá %s)" % (
            vat_pct, "ghi 'không bao gồm'" if vat_ghi_ro else "không nói rõ — tạm tính"), 1, "khoản", vat, vat))
    tong = sum(r[4] for r in rows)
    bao = n * gia
    ns = b["ngan_sach"]
    nhan = "" if not ns else (" — ✅ trong ngân sách" if tong <= ns else " — ❌ vượt ngân sách %s" % planner.fmt_vnd(tong - ns))
    out = ["## Soát báo giá tour đoàn — %d khách%s" % (n, (" · " + b["dia_diem"]) if b["dia_diem"] else ""),
           "Giá báo: **%s/khách × %d = %s**. Sau khi cộng các khoản *không bao gồm* tính được, **tổng chi thật của công ty "
           "≈ %s (+%s, +%.0f%%)**." % (planner.fmt_vnd(gia), n, planner.fmt_vnd(bao), planner.fmt_vnd(tong),
                                         planner.fmt_vnd(tong - bao), 100.0 * (tong - bao) / bao)]
    if ns:
        out.append("Ngân sách đã hiểu: **%s cho %d người**." % (planner.fmt_vnd(ns), n))
    bang = ["### Tổng chi thật ước tính%s" % nhan, "",
            "| Hạng mục | Số lượng | Đơn giá | Thành tiền |", "|---|---|---|---|"]
    for ten, sl, dv, dg, tt in rows:
        bang.append("| %s | %s %s | %s | %s |" % (ten, "{:,}".format(sl).replace(",", "."), dv, planner.fmt_vnd(dg), planner.fmt_vnd(tt)))
    bang += ["| **Tổng cả đoàn** | | | **%s** |" % planner.fmt_vnd(tong),
             "| **Mỗi người** (%d người) | | | **%s** |" % (n, planner.fmt_vnd(planner.round_k(tong / n)))]
    out.append("\n".join(bang))
    if ns and tong > ns:
        thua = [(r[0].split(" — ")[0].split(" (")[0], r[4]) for r in rows[1:] if not r[0].startswith("Thuế VAT")]
        goi_y = ["- **Vượt ngân sách %s (%.1f%%)**: tổng chi thật %s − ngân sách %s." % (
            planner.fmt_vnd(tong - ns), 100.0 * (tong - ns) / ns, planner.fmt_vnd(tong), planner.fmt_vnd(ns))]
        if bao <= ns:
            goi_y.append("- Giá báo (%s) **nằm trong** ngân sách nhưng tổng chi thật thì **vượt** — chính các khoản "
                         "\"không bao gồm\" làm vượt." % planner.fmt_vnd(bao))
        for ten, tt in sorted(thua, key=lambda x: -x[1])[:2]:
            goi_y.append("- Thương lượng đưa vào giá tour / bỏ \"%s\": tiết kiệm %s → tổng còn %s." % (
                ten, planner.fmt_vnd(tt), planner.fmt_vnd(tong - tt)))
        goi_y.append("- Ngân sách tối thiểu cho báo giá này: **%s**." % planner.fmt_vnd(tong))
        out.append("**Vì sao vượt:**\n" + "\n".join(goi_y))
    ref = _tham_chieu(b)
    if ref:
        out.append(ref)
    ct = ["### Soát chứng từ / hoá đơn (để kế toán duyệt được)",
          "- **Hoá đơn VAT:** %s Khoản chi chỉ tính vào chi phí được trừ khi có hoá đơn, chứng từ hợp pháp. ([nguồn](%s))" % (
              ("báo giá ghi VAT %d%% *không bao gồm* → công ty cần hoá đơn thì phải trả thêm %s." % (
                  vat_pct, planner.fmt_vnd(rows[1][4]))) if vat_ghi_ro else
              "báo giá không nói về VAT / hoá đơn → yêu cầu ghi rõ \"giá đã gồm VAT, xuất hoá đơn cho công ty\".",
              quy["HOA_DON_VAT"]["nguon"][0]),
          "- **Chuyển khoản:** tổng %s ≥ 5.000.000đ → thanh toán từ tài khoản công ty, không trả tiền mặt (từ 01/07/2025 "
          "hoá đơn ≥ 5 triệu phải thanh toán không dùng tiền mặt mới được khấu trừ GTGT). ([nguồn](%s))" % (
              planner.fmt_vnd(tong), quy["CHUYEN_KHOAN_5TR"]["nguon"][0]),
          "- **Hợp đồng / hoá đơn ghi \"đoàn %d khách\"**, không kèm danh sách tên: chi chung cho tập thể không tính vào "
          "thu nhập chịu thuế TNCN của nhân viên. ([nguồn](%s))" % (n, quy["CHI_CHUNG_TAP_THE"]["nguon"][0])]
    if kho_hd:
        ct.append("- **Khoản khó có hoá đơn cho công ty:** %s — đưa vào hợp đồng tour, hoặc ghi rõ nhân viên tự chi." % "; ".join(kho_hd))
    if b["luong_bq"]:
        mn = planner.round_k(tong / n)
        ct.append("- **Trần phúc lợi:** chi phí / người %s so với 1 tháng lương bình quân %s → %s (theo Thông tư 96/2015, "
                  "chưa tính phúc lợi khác trong năm; Luật Thuế TNDN 2025 có thể đã đổi). ([nguồn](%s))" % (
                      planner.fmt_vnd(mn), planner.fmt_vnd(b["luong_bq"]),
                      "**vượt trần** — phần vượt có thể không được trừ khi tính thuế TNDN" if mn > b["luong_bq"] else "trong trần",
                      quy["TRAN_PHUC_LOI"]["nguon"][0]))
    else:
        ct.append("- **Trần phúc lợi:** cho mình lương bình quân / tháng để so chi phí / người với trần 1 tháng lương "
                  "(Thông tư 96/2015 — cần đối chiếu luật mới).")
    ct.append("- *Không phải tư vấn thuế — kế toán đối chiếu văn bản hiện hành (`data/quy_tac_chung_tu.json`).*")
    out.append("\n".join(ct))
    if ca_nhan:
        out.append("Khoản cá nhân, công ty không phải chịu (không cộng vào tổng): " + "; ".join(ca_nhan) + ".")
    hoi += ["Giá trên áp dụng cho đúng %d khách và ngày đi dự kiến chưa (phụ thu cuối tuần / lễ / phòng đơn)?" % n,
            "Chính sách huỷ / đổi ngày và mức cọc?"]
    out.append("### Câu cần hỏi lại công ty tour trước khi duyệt\n" + "\n".join("%d. %s" % (i, h) for i, h in enumerate(hoi, 1)))
    out.append("**Tờ trình (nháp):** Đề xuất duyệt chuyến đi %d khách%s theo báo giá %s/khách; tổng chi dự kiến "
               "**%s** (đã gồm VAT và các khoản ngoài giá tour tính được)%s. Thanh toán chuyển khoản, nhận hoá đơn VAT "
               "ghi tên công ty." % (n, (" " + b["dia_diem"]) if b["dia_diem"] else "", planner.fmt_vnd(gia),
                                      planner.fmt_vnd(tong), (", %s ngân sách %s" % ("trong" if tong <= ns else "vượt",
                                                                                     planner.fmt_vnd(ns))) if ns else ""))
    out.append("Hệ thống chỉ soát và dự trù, không đặt tour, không thanh toán; số \"ước tính\" cần công ty tour xác nhận.")
    if ket_qua:
        return {"status": "ok", "so_nguoi": n, "dia_diem": b["dia_diem"], "gia_moi_khach": gia, "gia_bao": bao, "tong": tong,
                "moi_nguoi": planner.round_k(tong / n), "ngan_sach": ns, "vuot": (tong - ns) if ns and tong > ns else None,
                "chenh_pct": round(100.0 * (tong - bao) / bao, 1),
                "dong": [{"ten": t, "so_luong": sl, "don_vi": dv, "don_gia": dg, "thanh_tien": tt} for t, sl, dv, dg, tt in rows],
                "vi_sao_vuot": [g[2:] for g in goi_y] if ns and tong > ns else [], "tham_chieu": ref,
                "chung_tu": [c[2:] for c in ct[1:]], "ca_nhan": ca_nhan, "cau_hoi": hoi, "to_trinh": out[-2][len("**Tờ trình (nháp):** "):],
                "markdown": "\n\n".join(out)}
    return "\n\n".join(out)


def _tham_chieu(b):
    """So giá báo với gói tính từ data/*.json (cùng điểm đến, số người, số ngày) — chỉ để tham khảo."""
    tu, den = du_lieu.tim_diem_di(b["noi_xuat_phat"]), du_lieu.tim_diem_den(b["dia_diem"])
    if not (tu and den and b["so_nguoi"]):
        return ""
    req = {"so_nguoi": b["so_nguoi"], "so_ngay": b["so_ngay"], "so_dem": b["so_dem"], "khong_muon": [],
           "muc_dich": b["muc_dich"] or "gan_ket", "ngan_sach": None}
    d = du_lieu.dung_diem_den(req, tu, den)
    if not d:
        return ""
    gia = [(name, d["calc"][lv]["moi_nguoi"]) for lv, name in planner.PACKAGES]
    return ("Giá tham chiếu tự tính từ `data/*.json` (%s → %s, %d ngày, %d người, chưa VAT): " % (
        tu["ten"], den["ten"], b["so_ngay"], b["so_nguoi"]) + " · ".join("%s %s/người" % (x, planner.fmt_vnd(y)) for x, y in gia)
        + ". Chỉ để biết báo giá đang ở mức nào — hai bên có thể khác hạng mục.")
