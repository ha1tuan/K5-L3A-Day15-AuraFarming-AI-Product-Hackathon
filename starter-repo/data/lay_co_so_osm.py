"""Lấy khách sạn / resort / nhà hàng TÊN THẬT quanh 24 điểm đến từ OpenStreetMap (Overpass API) → data/co_so_osm.json.

    python data/lay_co_so_osm.py            # ~3 phút, 1 truy vấn / điểm đến, nghỉ 5 giây giữa các truy vấn

Dữ liệu © OpenStreetMap contributors, giấy phép ODbL (ghi công ở web và data/DATA_CARD.md). Chỉ lấy: tên, loại, toạ độ,
website / điện thoại nếu có, mã OSM. OSM ở Việt Nam hầu như KHÔNG ghi hạng sao → web ghi "chưa rõ hạng" và đưa link tìm
đúng hạng (Booking lọc theo sao) thay vì tự gán hạng. Không lấy giá (không có nguồn mở; trang đặt phòng cấm tự động lấy giá).
"""
import json
import math
import time
import urllib.parse
import urllib.request
from pathlib import Path

GOC = Path(__file__).resolve().parent
UA = {"User-Agent": "AuraFarming-hackathon/0.1 (educational)"}
BAN_KINH = 8000          # m quanh toạ độ điểm đến
MAY_CHU = ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter",
           "https://overpass.private.coffee/api/interpreter"]
UU_TIEN_AN = ("hải sản", "hai san", "nhà hàng", "nha hang", "seafood", "vietnamese", "regional")


def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (*a, *b))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h))


def overpass(lat, lon):
    q = f"""[out:json][timeout:50];
(nwr["tourism"~"^(hotel|resort)$"]["name"](around:{BAN_KINH},{lat},{lon});
 nwr["amenity"="restaurant"]["name"](around:{BAN_KINH},{lat},{lon}););
out center tags;"""
    for t, url in enumerate(MAY_CHU * 2):                  # máy chủ chính quá tải → thử máy chủ dự phòng
        try:
            req = urllib.request.Request(url, data=urllib.parse.urlencode({"data": q}).encode(), headers=UA)
            return json.load(urllib.request.urlopen(req, timeout=90))["elements"]
        except Exception as e:  # noqa: BLE001
            print("  thử lại", t + 1, url.split("/")[2], e, flush=True)
            time.sleep(10)
    return []


def gon(e, c):
    t = e["tags"]
    la = e.get("lat") or e.get("center", {}).get("lat")
    lo = e.get("lon") or e.get("center", {}).get("lon")
    return {"ten": t["name"], "loai": t.get("tourism") or t.get("amenity"), "lat": la, "lon": lo,
            "cach_trung_tam_km": round(km(c, (la, lo)), 1),
            "website": t.get("website") or t.get("contact:website"), "dien_thoai": t.get("phone") or t.get("contact:phone"),
            "sao": t.get("stars"), "am_thuc": t.get("cuisine"), "osm": "https://www.openstreetmap.org/%s/%s" % (e["type"], e["id"])}


def ghi(out):
    (GOC / "co_so_osm.json").write_text(json.dumps({
        "_mo_ta": "Khách sạn / resort / nhà hàng tên thật quanh 24 điểm đến (bán kính 8 km) từ OpenStreetMap. Chưa kiểm hạng sao, giá, "
                  "số phòng, sức chứa đoàn — chỉ để người dùng tự tra & liên hệ.",
        "nguon": "© OpenStreetMap contributors (ODbL) — Overpass API", "ngay_lay": time.strftime("%Y-%m-%d"), "diem_den": out},
        ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def main():
    dd = json.loads((GOC / "diem_den.json").read_text(encoding="utf-8"))["diem_den"]
    f = GOC / "co_so_osm.json"
    out = json.loads(f.read_text(encoding="utf-8"))["diem_den"] if f.exists() else {}      # chạy lại: bỏ qua điểm đã có
    for d in dd:
        if out.get(d["id"], {}).get("tong_tim_thay", {}).get("khach_san"):
            continue
        c = (d["lat"], d["lon"])
        els = [e for e in overpass(*c) if (e.get("lat") or e.get("center"))]
        ks = sorted((gon(e, c) for e in els if e["tags"].get("tourism") in ("hotel", "resort")), key=lambda x: x["cach_trung_tam_km"])
        nh = sorted((gon(e, c) for e in els if e["tags"].get("amenity") == "restaurant"),
                    key=lambda x: (not any(k in (x["ten"] + " " + (x["am_thuc"] or "")).lower() for k in UU_TIEN_AN), x["cach_trung_tam_km"]))
        resort = [x for x in ks if x["loai"] == "resort"]
        out[d["id"]] = {"khach_san": (resort[:3] + [x for x in ks if x not in resort[:3]])[:8], "nha_hang": nh[:6],
                        "tong_tim_thay": {"khach_san": len(ks), "nha_hang": len(nh)}}
        print(d["ten"], "· khách sạn", len(ks), "· nhà hàng", len(nh), flush=True)
        ghi(out)                                          # ghi sau mỗi điểm: dừng giữa chừng không mất dữ liệu
        time.sleep(5)


if __name__ == "__main__":
    main()
