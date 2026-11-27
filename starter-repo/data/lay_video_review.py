"""Lấy link video review YouTube cho từng điểm đến -> data/video_review.json. Chỉ thư viện chuẩn.

    python data/lay_video_review.py              # bỏ qua điểm đến đã có video trong file
    python data/lay_video_review.py --lam-moi    # lấy lại tất cả

Cách làm (ghi trong DATA_CARD.md):
1. Tìm trên trang kết quả YouTube với 2 câu: "review du lịch <điểm đến>" và "team building <điểm đến>".
2. Lấy mã video theo thứ tự YouTube xếp, bỏ trùng.
3. KIỂM từng video qua oEmbed chính thức của YouTube (https://www.youtube.com/oembed): video còn tồn tại,
   công khai, lấy đúng tiêu đề + tên kênh từ YouTube. Không kiểm được -> bỏ.
4. Chỉ giữ video có TIÊU ĐỀ chứa tên điểm đến (so không dấu). Tối đa 3 video review + 2 video team building.
Không tải video, không lưu ảnh, không lưu bình luận. Nghỉ 1,5 giây giữa các lần gọi.
"""
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

THU_MUC = Path(__file__).resolve().parent
RA = THU_MUC / "video_review.json"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36",
      "Accept-Language": "vi-VN,vi;q=0.9"}
TU_KHOA_PHU = {"phongnha": ["phong nha", "quang binh"], "hue": ["hue"], "muine": ["mui ne", "phan thiet"],
               "hotram": ["ho tram", "long hai"], "tayninh": ["ba den", "tay ninh"], "phuyen": ["phu yen", "tuy hoa"],
               "danang": ["da nang"], "condao": ["con dao"]}


def khong_dau(s):
    s = unicodedata.normalize("NFD", s.lower()).replace("đ", "d")
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def tu_khoa(d):
    if d["id"] in TU_KHOA_PHU:
        return TU_KHOA_PHU[d["id"]]
    return [khong_dau(re.sub(r"\s*\(.*\)", "", d["ten"]).split(" - ")[0])]


def get(url, timeout=30):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read().decode("utf-8", "replace")


def tim(cau):
    html = get("https://www.youtube.com/results?search_query=" + urllib.parse.quote(cau))
    ids = []
    for i in re.findall(r'"videoId":"([\w-]{11})"', html):
        if i not in ids:
            ids.append(i)
    return ids


def kiem(vid):
    try:
        d = json.loads(get("https://www.youtube.com/oembed?format=json&url=" +
                           urllib.parse.quote("https://www.youtube.com/watch?v=" + vid), timeout=20))
        return {"url": "https://www.youtube.com/watch?v=" + vid, "tieu_de": d["title"], "kenh": d["author_name"]}
    except Exception:
        return None


def bi_loai(d, v, loai):
    """Loại thủ công (đã đọc tiêu đề ngày 27/11/2026): sai nơi, không phải team building công ty, nội dung chê bai."""
    t = khong_dau(v["tieu_de"])
    if "phan cam" in t:
        return "nội dung chê bai, câu view"
    if loai == "team_building" and d["id"] != "dalat" and "da lat" in t:
        return "quay ở Đà Lạt, không phải nơi này"
    if loai == "team_building" and any(x in t for x in ("schannel", "huongda", "team boy")):
        return "không phải team building công ty"
    return None


def lay(d, cau, loai, toi_da, da_co=()):
    kw, out = tu_khoa(d), []
    thay = {khong_dau(x["tieu_de"])[:60] for x in da_co}
    for vid in tim(cau)[:12]:
        time.sleep(1.5)
        v = kiem(vid)
        if v and (bi_loai(d, v, loai) or khong_dau(v["tieu_de"])[:60] in thay):
            continue
        if v and any(k in khong_dau(v["tieu_de"]) for k in kw):
            thay.add(khong_dau(v["tieu_de"])[:60])
            out.append(v | {"loai": loai, "cau_tim": cau})
            if len(out) == toi_da:
                break
    return out


def main():
    dd = json.loads((THU_MUC / "diem_den.json").read_text(encoding="utf-8"))["diem_den"]
    cu = {} if "--lam-moi" in sys.argv or not RA.exists() else json.loads(RA.read_text(encoding="utf-8"))["video"]
    for d in dd:
        if cu.get(d["id"]):
            continue
        ten = re.sub(r"\s*\(.*\)", "", d["ten"])
        try:
            r = lay(d, f"review du lịch {ten}", "review", 3)
            v = r + lay(d, f"team building {ten}", "team_building", 2, r)
        except Exception as e:
            print(d["id"], "LỖI", e)
            continue
        cu[d["id"]] = v
        print(f'{d["id"]:9s} review {sum(x["loai"] == "review" for x in v)} · team building {sum(x["loai"] == "team_building" for x in v)}', flush=True)
        RA.write_text(json.dumps({"ngay_kiem": date.today().isoformat(),
                                  "cach_lay": "tìm YouTube 'review du lịch <nơi>' và 'team building <nơi>', kiểm từng link qua oEmbed, giữ video có tên nơi trong tiêu đề",
                                  "video": cu}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("tổng video:", sum(len(v) for v in cu.values()), "· điểm đến thiếu video:", [k for k, v in cu.items() if not v])


if __name__ == "__main__":
    main()
