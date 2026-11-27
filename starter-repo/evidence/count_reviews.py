"""Đào review công khai Google Play của các app đặt du lịch ở VN — script chạy lại được.

    pip install google-play-scraper
    python evidence/count_reviews.py            # tải review mới (ghi cache evidence/raw-reviews.jsonl, không commit)
    python evidence/count_reviews.py --cached   # chỉ đếm lại trên cache đã tải

Cách đếm (ghi trong evidence/data-mining.md §1 TRƯỚC khi chạy lần đầu):
  - Mẫu: tối đa PER_APP review MỚI NHẤT mỗi app, lang=vi, country=vn.
  - Cache KHÔNG giữ tên người viết (bỏ userName, userImage, reviewId) — chỉ giữ app, số sao, ngày, nội dung.
  - Mẫu số chính: review 1–2★ có nội dung ≥ 20 ký tự (người đang gặp vấn đề và kể ra).
  - Nhóm P (giá / phí lệch so với lúc xem): regex PRICE. Nhóm G (đặt cho đoàn / nhóm ≥3 người / ≥2 phòng /
    hoá đơn công ty): regex GROUP. Nhóm R (đến nơi không có phòng / đơn chưa được xác nhận): regex ROOM.
  - Regex chỉ là bước lọc ứng viên; độ chính xác đo bằng nhãn tay ở evidence/review-labels.csv (--label).
"""
import collections
import json
import os
import re
import sys
import unicodedata

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "raw-reviews.jsonl")  # khớp .gitignore evidence/**/raw-*
OUT = os.path.join(HERE, "review-counts.json")

APPS = {
    "com.traveloka.android": "Traveloka",
    "com.agoda.mobile.consumer": "Agoda",
    "com.booking": "Booking.com",
    "vn.mytour.apps.android": "Mytour",
    "com.klook": "Klook",
}
PER_APP = 2000
MIN_LEN = 20

# "đánh giá" chứa chữ "giá" → bỏ trước khi so (xem clean()).
def _rx(pattern):
    """Chuẩn hoá NFC cả mẫu regex (chữ có dấu gõ ở máy khác có thể là NFD) rồi mới compile."""
    return re.compile(unicodedata.normalize("NFC", pattern))


# v2 (sau khi gán nhãn 50 mẫu ở v1 chỉ đúng 18/50): "khác" khớp cả "khách", "phát sinh" khớp "sự cố phát sinh".
PRICE = _rx(
    r"\b(giá|tiền|phí)\b.{0,30}(\btăng\b|\bnhảy\b|đội lên|\bkhác\b|chênh|cao hơn|đắt hơn|không đúng|không giống|gấp đôi)"
    r"|phụ thu|phí ẩn|(phí|chi phí) phát sinh|phát sinh (thêm|phí|chi phí)|thu thêm|tính thêm|trả thêm|bù tiền")
_NUM = r"\b(\d+|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười|mấy|nhiều)"
GROUP = _rx(
    r"(?<!tập )\bđoàn\b|đi nhóm|nhóm bạn|cả nhóm|team ?building|(?<!phòng )tập thể"
    r"|\b(đặt|book|booking|thuê|lấy)\s+" + _NUM + r"\s+phòng|" + _NUM + r"\s+phòng\s+(cùng lúc|một lúc|1 lúc|cho)"
    r"|\b([3-9]|[1-9]\d+|ba|bốn|năm|sáu|bảy|tám|chín|mười)\s+(người|khách|vé)\b"
    r"|(hóa đơn|hoá đơn|vat).{0,40}công ty|công ty.{0,40}(hóa đơn|hoá đơn|vat)")
ROOM = _rx(
    r"(không|ko|k)\s+(có|còn)\s+phòng|hết phòng|không nhận (phòng|đặt|booking)|không có tên"
    r"|không (chấp nhận|ghi nhận) (đặt|booking)|chưa (xác nhận|confirm)|overbook")



def clean(t):
    return re.sub(unicodedata.normalize("NFC", "đánh giá"), " ", t)


def norm(t):
    return clean(unicodedata.normalize("NFC", (t or "")).lower())


def fetch():
    from google_play_scraper import Sort, reviews
    rows = []
    for app_id, name in APPS.items():
        got, token = [], None
        while len(got) < PER_APP:
            batch, token = reviews(app_id, lang="vi", country="vn", sort=Sort.NEWEST,
                                   count=min(200, PER_APP - len(got)), continuation_token=token)
            if not batch:
                break
            got += batch
            if token is None:
                break
        for r in got:
            rows.append({"app": name, "score": r["score"], "date": r["at"].strftime("%Y-%m-%d"),
                         "text": r["content"] or ""})
        print("%s: %d review" % (name, len(got)))
    with open(CACHE, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return rows


def load():
    with open(CACHE, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def count(rows):
    texted = [r for r in rows if len((r["text"] or "").strip()) >= MIN_LEN]
    neg = [r for r in texted if r["score"] <= 2]
    tag = lambda rx, rs: [r for r in rs if rx.search(norm(r["text"]))]
    res = {
        "tong_review_tai_ve": len(rows),
        "ngay_cu_nhat": min(r["date"] for r in rows), "ngay_moi_nhat": max(r["date"] for r in rows),
        "review_co_noi_dung": len(texted),
        "review_1_2_sao": len(neg),
        "P_gia_phi_lech_trong_1_2_sao": len(tag(PRICE, neg)),
        "G_doan_nhom_trong_1_2_sao": len(tag(GROUP, neg)),
        "R_khong_co_phong_trong_1_2_sao": len(tag(ROOM, neg)),
        "G_doan_nhom_moi_so_sao": len(tag(GROUP, texted)),
        "G_va_P_hoac_R_trong_1_2_sao": len([r for r in tag(GROUP, neg) if PRICE.search(norm(r["text"])) or ROOM.search(norm(r["text"]))]),
        "P_hoac_R_trong_1_2_sao": len([r for r in neg if PRICE.search(norm(r["text"])) or ROOM.search(norm(r["text"]))]),
        "theo_app": {},
    }
    for name in APPS.values():
        n = [r for r in neg if r["app"] == name]
        res["theo_app"][name] = {"review_1_2_sao": len(n), "P": len(tag(PRICE, n)),
                                 "G": len(tag(GROUP, n)), "R": len(tag(ROOM, n))}
    return res, tag(PRICE, neg), tag(GROUP, neg), tag(ROOM, neg)


def pct(x, n):
    return "%d/%d (%.1f%%)" % (x, n, 100.0 * x / n) if n else "%d/0" % x


LABELS = os.path.join(HERE, "review-labels.csv")


def key(r):
    import hashlib
    return hashlib.sha1(r["text"].encode("utf-8")).hexdigest()[:10]


def label_report(res, cands):
    """Độ chính xác của regex trên mẫu gán nhãn tay (evidence/review-labels.csv) → số ước tính đã hiệu chỉnh."""
    import csv
    if not os.path.exists(LABELS):
        return
    with open(LABELS, encoding="utf-8") as f:
        labels = list(csv.DictReader(f))
    n = res["review_1_2_sao"]
    print()
    print("Độ chính xác (nhãn tay, %s):" % os.path.relpath(LABELS, os.path.dirname(HERE)))
    for g, total in (("P", res["P_gia_phi_lech_trong_1_2_sao"]), ("G", res["G_doan_nhom_trong_1_2_sao"]),
                     ("R", res["R_khong_co_phong_trong_1_2_sao"])):
        live = {key(r) for r in cands[g]}
        lab = [l for l in labels if l["nhom"] == g and l["key"] in live]
        ok = sum(int(l["nhan"]) for l in lab)
        if not lab:
            continue
        prec = ok / len(lab)
        est = round(total * prec)
        res["do_chinh_xac_" + g] = "%d/%d" % (ok, len(lab))
        res["uoc_tinh_dung_" + g] = est
        print("  %s: đúng %d/%d mẫu (%.0f%%) → ước tính %d/%d review 1–2★ (%.1f%%)" % (
            g, ok, len(lab), 100 * prec, est, n, 100.0 * est / n))


if __name__ == "__main__":
    rows = load() if "--cached" in sys.argv else fetch()
    res, p, g, r = count(rows)
    label_report(res, {"P": p, "G": g, "R": r})
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    n = res["review_1_2_sao"]
    print("Khoảng ngày: %s → %s · tải %d · có nội dung %d · 1–2★ %d" % (
        res["ngay_cu_nhat"], res["ngay_moi_nhat"], res["tong_review_tai_ve"], res["review_co_noi_dung"], n))
    print("P giá/phí lệch:", pct(res["P_gia_phi_lech_trong_1_2_sao"], n))
    print("G đoàn/nhóm:   ", pct(res["G_doan_nhom_trong_1_2_sao"], n), "· mọi số sao:", res["G_doan_nhom_moi_so_sao"])
    print("R không phòng: ", pct(res["R_khong_co_phong_trong_1_2_sao"], n))
    print("P hoặc R:      ", pct(res["P_hoac_R_trong_1_2_sao"], n))
    print("G và (P hoặc R):", res["G_va_P_hoac_R_trong_1_2_sao"])
    for k, v in res["theo_app"].items():
        print("  %-12s 1–2★ %4d · P %s · G %d · R %d" % (k, v["review_1_2_sao"], pct(v["P"], v["review_1_2_sao"]), v["G"], v["R"]))
    if "--show" in sys.argv:
        for label, rs in (("G", g), ("P", p[:40]), ("R", r[:20])):
            print("\n==== %s" % label)
            for x in rs:
                print("- [%s %d★ %s] %s" % (x["app"], x["score"], x["date"], x["text"].replace("\n", " ")))
