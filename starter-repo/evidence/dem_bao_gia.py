"""Đếm giả thuyết 2 (evidence/hypothesis.md): báo giá tour đoàn công khai có cho biết tổng chi thật không.

    python evidence/dem_bao_gia.py            # tải (≤1 trang/giây, có cache evidence/raw_tour/, không commit) + đếm
    python evidence/dem_bao_gia.py --chi-dem  # chỉ đếm lại từ cache

Mẫu, cách đếm, ngưỡng: ghi TRƯỚC ở evidence/hypothesis.md "Giả thuyết 2". Danh sách URL: evidence/vietnambooking_tour_urls.txt
(sitemap công khai vietnambooking.com, lấy 27/11/2026). Ra: evidence/bao-gia-counts.json, evidence/bao-gia-labels.csv
(chỉ số đếm + trích ≤ 300 ký tự mục "không bao gồm", không lưu nguyên trang). Chỉ thư viện chuẩn.
"""
import csv
import hashlib
import html
import json
import random
import re
import sys
import time
import unicodedata
import urllib.request
from pathlib import Path

GOC = Path(__file__).resolve().parent
CACHE = GOC / "raw_tour"
UA = "Mozilla/5.0 (AI20K hackathon research; 1 req/s)"
NUOC_NGOAI = ("thai-lan", "bangkok", "singapore", "malaysia", "han-quoc", "seoul", "nhat-ban", "trung-quoc", "dai-loan",
              "hong-kong", "chau-au", "phap", "y", "duc", "thuy-si", "anh-quoc", "my", "uc", "dubai", "campuchia",
              "bali", "indonesia", "an-do", "nga", "maldives", "philippines", "myanmar", "macau", "tho-nhi-ky", "ai-cap",
              "nam-phi", "canada", "new-zealand", "phuket", "pattaya", "chiang-mai", "angkor", "kuala-lumpur",
              "thuong-hai", "bac-kinh", "truong-gia-gioi", "phuong-hoang", "le-giang", "tokyo", "osaka", "busan", "jeju",
              "ha-khau", "quang-chau", "nam-ninh", "xiem-riep", "phnom-penh", "chau-a", "chau-uc", "chau-my", "lao-vientiane",
              "vientiane", "luang-prabang", "nuoc-ngoai", "quoc-te")


def nuoc_ngoai(u):
    slug = "-" + u.rsplit("/", 1)[1][:-5] + "-"
    return any("-" + k + "-" in slug for k in NUOC_NGOAI) or ("-lao-" in slug and "-lao-cai-" not in slug)


NHOM_G = re.compile(r"team|gala|mice|khach-doan|cho-khach-doan|cong-ty")
DAU_MUC = re.compile(r"^(giá tour (chưa |không )?bao gồm|(giá )?(không|chưa) bao gồm|bao gồm|lưu ý|ghi chú|chính sách|điều kiện|"
                     r"giá (vé )?trẻ em|trẻ em|hủy|huỷ|quy định|thông tin|điều khoản|phụ thu|thời gian|đánh giá|tour liên quan|"
                     r"hình thức thanh toán|thanh toán|những (thông tin|điều) cần lưu ý|lưu ý|quy trình|\d+\. )", re.I)


def kd(s):
    s = unicodedata.normalize("NFD", s.lower()).replace("đ", "d")
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def tai(url, chi_dem):
    f = CACHE / (hashlib.sha1(url.encode()).hexdigest()[:16] + ".html")
    if f.exists():
        return f.read_text(encoding="utf-8", errors="ignore")
    if chi_dem:
        return None
    time.sleep(1.0)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=40) as r:
            s = r.read().decode("utf-8", "ignore")
    except Exception as e:  # noqa: BLE001
        print("  lỗi tải", url, e, file=sys.stderr)
        return None
    CACHE.mkdir(exist_ok=True)
    f.write_text(s, encoding="utf-8")
    return s


def chu(s):
    s = re.sub(r"<script.*?</script>|<style.*?</style>|<noscript.*?</noscript>", " ", s, flags=re.S | re.I)
    s = html.unescape(re.sub(r"<[^>]+>", "\n", s))
    return [x.strip(" \t -•+*–:") for x in s.splitlines() if x.strip(" \t -•+*–:")]


def muc(dong, dau):
    """Dòng thuộc mục bắt đầu bằng dòng khớp `dau`, tới đầu mục kế tiếp. Lấy lần xuất hiện đầu."""
    for i, x in enumerate(dong):
        if dau.match(x) and len(x) < 60:
            out = []
            for y in dong[i + 1:i + 60]:
                if DAU_MUC.match(y) and len(y) < 60:
                    break
                out.append(y)
            return out
    return None


def dem(url, s):
    dong = chu(s)
    tieu_de = next((x for x in dong if len(x) > 15 and "tour" in x.lower()), "")[:120]
    khong = muc(dong, re.compile(r"^(giá (tour )?)?(không|chưa) bao gồm", re.I))
    co = muc(dong, re.compile(r"^giá tour bao gồm|^bao gồm", re.I))
    khoan = [x for x in (khong or []) if len(x) >= 4][:30]
    toan = kd(" \n".join(dong))
    vat_re = re.compile(r"\bvat\b|hoa don|thue gtgt|thue gia tri gia tang")
    vat_khong = bool(khong and vat_re.search(kd(" ".join(khong))))
    vat_co = bool(co and vat_re.search(kd(" ".join(co))))
    vat = "khong_bao_gom" if vat_khong else "bao_gom" if vat_co else "nhac_noi_khac" if vat_re.search(toan) else "khong_nhac"
    phu_thu = bool(re.search(r"(?<!pham )phu thu", toan))   # bỏ tên đường "Phạm Phú Thứ" ở chân trang
    gia_so = bool(re.search(r"\d{1,3}(\.\d{3}){1,3}\s*(vnd|d\b|vnđ)", toan))
    lien_he = bool(re.search(r"lien he (de |)(nhan |)bao gia|gia: ?lien he|lien he bao gia", toan))
    thay_doi = bool(re.search(r"(gia|chi phi) (tour )?(co the |se )?thay doi|tuy theo (thoi diem|so luong)", toan))
    return {"url": url, "tieu_de": tieu_de, "co_muc_khong_bao_gom": khong is not None, "so_khoan_khong_bao_gom": len(khoan),
            "vat": vat, "phu_thu": phu_thu, "gia_bang_so": gia_so, "chi_lien_he": lien_he and not gia_so,
            "gia_thay_doi": thay_doi, "trich_khong_bao_gom": " · ".join(khoan)[:300]}


def main():
    chi_dem = "--chi-dem" in sys.argv
    urls = [u.strip() for u in (GOC / "vietnambooking_tour_urls.txt").read_text().split() if u.strip()]
    urls = [u for u in urls if u.count("/") == 4 and not nuoc_ngoai(u)]   # bỏ trang danh mục, nước ngoài
    g = [u for u in urls if NHOM_G.search(u.rsplit("/", 1)[1])]
    s = random.Random(42).sample([u for u in urls if u not in g], 60)
    print(f"{len(urls)} tour trong nước · nhóm G {len(g)} · nhóm S {len(s)}", flush=True)
    rows = []
    for nhom, ds in (("G", g), ("S", s)):
        for u in ds:
            x = tai(u, chi_dem)
            if x:
                rows.append(dict(dem(u, x), nhom=nhom))
    out = {}
    for nhom in ("G", "S"):
        r = [x for x in rows if x["nhom"] == nhom]
        n = len(r)
        if not n:
            continue
        c = lambda f: sum(1 for x in r if f(x))  # noqa: E731
        out[nhom] = {
            "N": n,
            "K1_co_muc_khong_bao_gom": c(lambda x: x["co_muc_khong_bao_gom"]),
            "K1_khong_bao_gom_ge3_khoan": c(lambda x: x["so_khoan_khong_bao_gom"] >= 3),
            "K1_so_khoan_trung_vi": sorted(x["so_khoan_khong_bao_gom"] for x in r)[n // 2],
            "K2_vat_khong_bao_gom": c(lambda x: x["vat"] == "khong_bao_gom"),
            "K2_vat_bao_gom": c(lambda x: x["vat"] == "bao_gom"),
            "K2_vat_nhac_noi_khac": c(lambda x: x["vat"] == "nhac_noi_khac"),
            "K2_vat_khong_nhac": c(lambda x: x["vat"] == "khong_nhac"),
            "K3_phu_thu": c(lambda x: x["phu_thu"]),
            "K4_chi_lien_he": c(lambda x: x["chi_lien_he"]),
            "K5_gia_thay_doi": c(lambda x: x["gia_thay_doi"]),
            "NGUONG_ge3_khoan_va_vat_khong_ro": c(lambda x: x["so_khoan_khong_bao_gom"] >= 3
                                                  and x["vat"] in ("khong_bao_gom", "khong_nhac")),
        }
    (GOC / "bao-gia-counts.json").write_text(json.dumps({"ngay": "2026-11-27", "nguon": "vietnambooking.com sitemap",
                                                         "ket_qua": out}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    with open(GOC / "bao-gia-labels.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["nhom"] + [k for k in rows[0] if k != "nhom"] + ["kiem_tay"])
        w.writeheader()
        w.writerows(dict(x, kiem_tay="") for x in rows)
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
