"""Đường dữ liệu cho web: TripInput → TripView (codebase/web/src/api/types.ts) dựng từ data/*.json qua codebase/du_lieu.py.

Cùng lõi với lối chấm answer() (codebase/agent.py): đơn giá, xếp phòng, chặng đi, lịch từng giờ, giải thích vượt ngân sách
đều do code tính (du_lieu.py + planner.py). Hỗ trợ đủ 3 cách vào:
  A — chỉ kinh phí  → status "choose_destination" (≤3 điểm đến, mỗi nơi 3 gói) → approve → "ok" (1 kế hoạch)
  B — chỉ địa điểm  → status "choose_package" (3 gói)                         → approve → "ok"
  C — cả hai        → status "ok" (3 kế hoạch, không bước duyệt)
Nơi đi / điểm đến ngoài dữ liệu → trả None để trip_service dùng graph cũ.
"""
import copy
import os
import re
import sys
from datetime import date, datetime, timedelta, timezone
from typing import Optional

_CODEBASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
if _CODEBASE not in sys.path:
    sys.path.insert(0, _CODEBASE)

import du_lieu  # noqa: E402
import planner  # noqa: E402

TIERS = [lv for lv, _ in planner.PACKAGES]
D_SAO = {"tiet_kiem": [2, 3], "can_bang": [4], "cao_cap": [5]}       # hạng sao theo gói (data/muc_goi.json)
KIND = {"di_chuyen": "travel", "an": "meal", "team_building": "activity", "tu_do": "rest", "nghi": "hotel", "tham_quan": "sight"}
NOT_SUPPORTED = None


# --- chuẩn hoá ---------------------------------------------------------------------------------
def build_req(inp) -> dict:
    n = inp.headcount
    budget = inp.budget
    if budget and inp.budget_per_person and n:
        budget = budget * n
    days = inp.days or 0
    return {"so_nguoi": n, "so_ngay": days, "so_dem": max(0, days - 1), "muc_dich": inp.purpose,
            "ngan_sach": budget or None, "noi_xuat_phat": (inp.origin or "").strip(), "dia_diem": (inp.destination or "").strip(),
            "khong_muon": [], "start_date": inp.start_date,
            "_ns_moi_nguoi": inp.budget if inp.budget and inp.budget_per_person else None}


def missing(req) -> list:
    m = [f for f, k in (("headcount", "so_nguoi"), ("days", "so_ngay"), ("origin", "noi_xuat_phat"), ("purpose", "muc_dich"))
         if not req.get(k)]
    if not req.get("ngan_sach") and not req.get("dia_diem"):
        m.append("budget_or_destination")
    return m


def now_vn() -> datetime:
    """Giờ thực Việt Nam (UTC+7). TRAVEL_TODAY=YYYY-MM-DD (test / bộ chấm) cố định ngày, giờ = 00:00."""
    t = os.environ.get("TRAVEL_TODAY")
    if t:
        try:
            return datetime.combine(date.fromisoformat(t), datetime.min.time())
        except ValueError:
            pass
    return datetime.now(timezone(timedelta(hours=7))).replace(tzinfo=None)


def start_range() -> tuple:
    """Ngày đi hợp lệ: từ hôm nay (nếu chưa quá 6:00 — kịp xuất phát 7:00) hoặc ngày mai, tới 1 năm sau."""
    n = now_vn()
    lo = n.date() + timedelta(days=0 if n.hour < 6 else 1)
    return lo, n.date() + timedelta(days=366)


def check_start(req) -> Optional[str]:
    """Thông báo lỗi nếu ngày đi người dùng chọn đã qua / quá xa / sai định dạng; None nếu hợp lệ hoặc để trống."""
    if not req.get("start_date"):
        return None
    try:
        d = date.fromisoformat(req["start_date"])
    except ValueError:
        return "Ngày đi không đúng định dạng — chọn lại trên lịch."
    lo, hi = start_range()
    if d < lo:
        return ("Ngày đi %s đã qua hoặc quá sát giờ xuất phát (hôm nay %s) — chọn ngày từ %s trở đi."
                % (d.strftime("%d/%m/%Y"), now_vn().strftime("%d/%m/%Y"), lo.strftime("%d/%m/%Y")))
    if d > hi:
        return "Ngày đi %s xa hơn 1 năm — giá tham khảo không còn sát; chọn ngày trước %s." % (d.strftime("%d/%m/%Y"), hi.strftime("%d/%m/%Y"))
    return None


def start_date(req) -> date:
    if req.get("start_date") and not check_start(req):
        return date.fromisoformat(req["start_date"])
    today = now_vn().date()
    return today + timedelta(days=(4 - today.weekday()) % 7 or 7)       # thứ Sáu gần nhất sau hôm nay


def echo(req, entry) -> dict:
    d0 = start_date(req)
    return {"headcount": req["so_nguoi"], "days": req["so_ngay"], "nights": req["so_dem"], "start_date": d0.isoformat(),
            "end_date": (d0 + timedelta(days=req["so_ngay"] - 1)).isoformat(), "origin": req["noi_xuat_phat"],
            "purpose": req["muc_dich"], "budget": req["ngan_sach"], "entry": entry}


# --- gói --------------------------------------------------------------------------------------
def _over(req, g):
    b = req.get("ngan_sach")
    return (g["tong"] - b) if b and g["tong"] > b else None


def explanation(req, dest, lv) -> Optional[dict]:
    b = req.get("ngan_sach")
    g = dest["calc"][lv]
    if not b or g["tong"] <= b:
        return None
    i = TIERS.index(lv)
    lower = TIERS[i - 1] if i else None
    cur = planner.by_group(g)
    if lower:
        low = planner.by_group(dest["calc"][lower])
        drivers = sorted(((k, cur.get(k, 0) - low.get(k, 0)) for k in set(cur) | set(low)), key=lambda x: -x[1])
        drivers = [x for x in drivers if x[1] > 0][:3]
    else:
        drivers = sorted(cur.items(), key=lambda x: -x[1])[:2]
    raw = {k: v for k, v in dest["raw"][lv].items()}
    raw_low = dest["raw"][lower] if lower else None
    cuts = sorted([(lab, t) for lab, t in planner.cat_giam(req, lv, raw, raw_low) if t < g["tong"]], key=lambda x: x[1])[:3]
    tk = dest["calc"]["tiet_kiem"]["tong"]
    return {"over_amount": g["tong"] - b, "over_pct": round(100.0 * (g["tong"] - b) / b, 1), "compared_to": lower,
            "drivers": [{"label": k, "amount": v} for k, v in drivers],
            "cuts": [{"label": lab, "saving": g["tong"] - t, "total_after": t} for lab, t in cuts],
            "min_budget": tk if tk > b else None}


def summary(dest, lv) -> dict:
    raw, g = dest["raw"][lv], dest["calc"][lv]
    c = raw["_chang"]
    au = raw.get("an_uong") or {}
    p = g.get("phong")
    tq = [h["ten"] for h in raw["hoat_dong"]] + list(raw.get("_mien_phi") or [])
    return {"transport": "%s%s" % (c["mo_ta"], "" if not c["gio"] else " · ~%s giờ / chiều" % c["gio"]),
            "lodging": raw.get("_luu_tru_chi_tiet") or "Không lưu trú (đi về trong ngày)",
            "rooms": (" + ".join("%d × %s" % (k, t["ten"].lower()) for t, k in p["co_cau"]) + " = %d chỗ" % p["so_cho"]) if p else "—",
            "meals": "%s · %s/suất" % (au.get("mo_ta", "Bữa chính theo đoàn"), planner.fmt_vnd(au.get("don_gia_bua", 0))),
            "gala": ("Có · %s/người" % planner.fmt_vnd(raw["gala"]["don_gia_nguoi"])) if raw["gala"].get("co") else "Không",
            "activities": "; ".join(tq) or "—"}


def qty_note(req, sl, dv) -> Optional[str]:
    """Số lượng gộp viết thành phép nhân dễ hiểu: 8 xe·ngày → "2 xe × 4 ngày" (chỉ khi chia hết)."""
    n, d, dem = req.get("so_nguoi") or 0, req.get("so_ngay") or 0, req.get("so_dem") or 0
    if dv == "xe·ngày" and d and sl % d == 0:
        return "%d xe × %d ngày" % (sl // d, d)
    if dv == "phòng·đêm" and dem and sl % dem == 0:
        return "%d phòng × %d đêm" % (sl // dem, dem)
    if dv == "suất" and n and sl % n == 0 and sl > n:
        return "%d người × %d bữa" % (n, sl // n)
    return None


def package(req, dest, lv, recommended) -> dict:
    g = dest["calc"][lv]
    items = [{"category": grp, "description": ten, "qty": sl, "unit": dv, "unit_price": dg, "amount": tt, "estimated": True}
             for grp, ten, sl, dv, dg, tt in g["lines"]]
    for it in items:
        note = qty_note(req, it["qty"], it["unit"])
        if note:
            it["qty_note"] = note
    for f in g["flags"]:
        items[-1].setdefault("note", f)
    out = {"tier": lv, "summary": summary(dest, lv), "line_items": items, "total": g["tong"], "per_person": g["moi_nguoi"],
           "over_budget": _over(req, g), "recommended": recommended}
    ex = explanation(req, dest, lv)
    if ex:
        out["explanation"] = ex
    return out


def best_tier(req, dest) -> str:
    b = req.get("ngan_sach")
    if not b:
        return "can_bang"
    ok = [lv for lv in TIERS if dest["calc"][lv]["tong"] <= b]
    return ok[-1] if ok else "tiet_kiem"


def packages(req, dest) -> list:
    rec = best_tier(req, dest)
    return [package(req, dest, lv, lv == rec) for lv in TIERS]


def plan(req, dest, lv) -> dict:
    d0 = start_date(req)
    g = dest["calc"][lv]
    days = []
    for day in dest["lich"][lv]:
        slots = []
        for k in day["khoi"]:
            kind = KIND.get(k["loai"], "activity")
            if "Gala" in k["viec"]:
                kind = "gala"
            slots.append({"start": k["gio"].split("–")[0][:5], "kind": kind, "title": k["viec"],
                          "note": "đến %s" % k["gio"].split("–")[1]})
        days.append({"label": "Ngày %d" % day["ngay"], "date": (d0 + timedelta(days=day["ngay"] - 1)).isoformat(), "slots": slots})
    vids = du_lieu.video(dest["id"], 2, 1)
    out = {"tier": lv, "destination": dest["ten"], "total": g["tong"], "per_person": g["moi_nguoi"], "estimate_total": g["tong"],
           "over_budget": _over(req, g), "days": days,
           "notes": sorted(dest.get("canh_bao") or []) + list(g["flags"]),
           "videos": [{"title": v["tieu_de"], "url": v["url"], "channel": v["kenh"],
                       "kind": "Review du lịch" if v["loai"] == "review" else "Team building"} for v in vids],
           "extra": extra(req, dest, lv),
           "info": [x for x in du_lieu.thong_tin_them(dest, req, [lv]).splitlines()[1:]
                    if not x.startswith(("- **Video", "  - [", "- ⚠"))]}
    ex = explanation(req, dest, lv)
    if ex:
        out["explanation"] = ex
    return out


def _gio(h):
    return ("%.1f" % h).rstrip("0").rstrip(".").replace(".", ",")


_OSM = None


def _co_so_osm(den_id):
    """Khách sạn / nhà hàng tên thật quanh điểm đến (data/co_so_osm.json, © OpenStreetMap ODbL)."""
    global _OSM
    f = os.path.join(du_lieu.DATA, "co_so_osm.json")
    if os.path.exists(f) and (_OSM is None or _OSM[0] != os.path.getmtime(f)):    # nạp lại khi file đổi / mới có
        import json
        _OSM = (os.path.getmtime(f), json.load(open(f, encoding="utf-8"))["diem_den"])
    return (_OSM[1] if _OSM else {}).get(den_id) or {"khach_san": [], "nha_hang": []}


def _maps(q):
    from urllib.parse import quote_plus
    return "https://www.google.com/maps/search/" + quote_plus(q)


def where_to_book(req, dest, lv) -> dict:
    """Gợi ý nơi ở / ăn THẬT: link tìm đúng hạng sao kèm ngày đi + số phòng (giá thật do người dùng tự xem), và cơ sở thật
    gần trung tâm từ OpenStreetMap (chưa rõ hạng, chưa kiểm giá / phòng / sức chứa — ghi rõ)."""
    from urllib.parse import urlencode
    den = dest["den"]
    g = dest["calc"][lv]
    sao = D_SAO[lv]
    m = re.search(r"(\d)★", dest["raw"][lv].get("_luu_tru_chi_tiet") or "")
    if m and lv != "tiet_kiem":
        sao = [int(m.group(1))]                          # nơi không có 5★: gói cao cấp dùng 4★ tốt nhất (data/DATA_CARD.md)
    d0 = start_date(req)
    d1 = d0 + timedelta(days=max(1, req["so_dem"]))
    phong = sum(k for _, k in (g.get("phong") or {}).get("co_cau", [])) or max(1, -(-req["so_nguoi"] // 2))
    ten = den["ten"].split(" (")[0]
    booking = "https://www.booking.com/searchresults.vi.html?" + urlencode({
        "ss": ten + ", Việt Nam", "checkin": d0.isoformat(), "checkout": d1.isoformat(), "group_adults": req["so_nguoi"],
        "no_rooms": phong, "group_children": 0, "nflt": ";".join("class=%d" % x for x in sao)})
    sao_txt = "–".join(str(x) for x in (sao[0], sao[-1])) if len(sao) > 1 else str(sao[0])
    osm = _co_so_osm(den["id"])
    ks = [{"name": x["ten"], "kind": "Resort" if x["loai"] == "resort" else "Khách sạn", "km": x["cach_trung_tam_km"],
           "maps": _maps("%s %s" % (x["ten"], ten)), "website": x.get("website"), "phone": x.get("dien_thoai"), "osm": x["osm"]}
          for x in osm["khach_san"][:6]]
    nh = [{"name": x["ten"], "kind": "Nhà hàng", "km": x["cach_trung_tam_km"], "maps": _maps("%s %s" % (x["ten"], ten)),
           "website": x.get("website"), "phone": x.get("dien_thoai"), "osm": x["osm"]} for x in osm["nha_hang"][:5]]
    au = dest["raw"][lv].get("an_uong") or {}
    if req["so_dem"] == 0:
        stay = None
    else:
        stay = {"title": "Khách sạn %s★ cho %d người · %d phòng · %s → %s" % (sao_txt, req["so_nguoi"], phong, d0.strftime("%d/%m"), d1.strftime("%d/%m")),
                "links": [{"label": "Xem giá thật trên Booking (lọc %s★, đúng ngày, %d phòng)" % (sao_txt, phong), "url": booking},
                          {"label": "Tìm khách sạn %s sao trên Google Maps" % sao_txt, "url": _maps("khách sạn %s sao %s" % (sao_txt, ten))}],
                "places": ks}
    eat = {"title": "Nhà hàng nhận đoàn %d người · dự trù ~%s/suất" % (req["so_nguoi"], planner.fmt_vnd(au.get("don_gia_bua", 0))),
           "links": [{"label": "Tìm nhà hàng nhận đoàn trên Google Maps", "url": _maps("nhà hàng nhận đoàn %s" % ten)}],
           "places": nh}
    return {"stay": stay, "eat": eat,
            "note": "Danh sách cơ sở lấy từ OpenStreetMap (bản đồ mở) — chưa rõ hạng sao, chưa kiểm giá, số phòng, sức chứa đoàn. "
                    "Bấm từng nơi để xem ảnh, đánh giá, điện thoại; giá thật xem qua nút Booking theo đúng ngày đi.",
            "credit": "© OpenStreetMap contributors (ODbL)"}


def extra(req, dest, lv) -> dict:
    """Thông tin thêm cho người dùng (web) — câu chữ thường, không tên file / thuật ngữ kỹ thuật."""
    raw, den = dest["raw"][lv], dest["den"]
    c = raw["_chang"]
    di = (c["mo_ta"][0].upper() + c["mo_ta"][1:]).replace(" đường bộ ", " · đường bộ ").replace(" + ", " · ")
    if c["gio"]:
        di += " · khoảng %s giờ mỗi chiều%s" % (_gio(c["gio"]), " (đã gồm thủ tục bay, đưa đón sân bay)" if c["kieu"] == "ve" else "")
    thang = start_date(req).month                         # mùa đẹp so theo THÁNG ĐI, không phải tháng hiện tại
    trong_mua = du_lieu._trong_mua(den["mua_dep_thang"], thang)
    sights = [h["ten"] for h in raw["hoat_dong"] if h["ten"] not in du_lieu.TEN_DICH_VU.values() and not h["ten"].startswith("Vé phà")]
    sights += list(raw.get("_mien_phi") or [])
    return {"travel": di, "lodging": raw.get("_luu_tru_chi_tiet") or "Không lưu trú (đi về trong ngày)",
            "season": {"months": den["mua_dep_thang"], "in_season": trong_mua, "month_now": thang},
            "sights": sights,
            "book": where_to_book(req, dest, lv),
            "price_note": "Giá trong kế hoạch là giá tham khảo theo hạng khách sạn, nhà hàng và giá thị trường có nguồn — "
                          "chưa phải báo giá của một cơ sở cụ thể. Trước khi đặt, công ty chọn khách sạn / nhà hàng thật "
                          "cùng hạng, xin báo giá và xác nhận đủ số phòng cho cả đoàn."}


def destination_option(req, dest, recommended) -> dict:
    c = dest["raw"][best_tier(req, dest)]["_chang"]
    vids = du_lieu.video(dest["id"], 3, 2)
    return {"name": dest["ten"], "transport": "plane" if c["kieu"] == "ve" else "bus",
            "travel_time": ("~%s giờ %s từ %s" % (c["gio"], "bay (gồm thủ tục)" if c["kieu"] == "ve" else "xe", req["noi_xuat_phat"]))
            if c["gio"] else "Đi lại nội vùng",
            "why": dest["ly_do"], "refs": {"articles": 0, "videos": len(vids), "url": vids[0]["url"] if vids else None},
            "packages": packages(req, dest), "recommended": recommended}


# --- vào ---------------------------------------------------------------------------------------
def handles(req) -> bool:
    if not du_lieu.co_du_lieu() or not du_lieu.tim_diem_di(req["noi_xuat_phat"]):
        return False
    return not req["dia_diem"] or du_lieu.tim_diem_den(req["dia_diem"]) is not None


def build_dest(req):
    """Dựng 3 gói cho req (đã có nơi đi + điểm đến), áp các khoản người dùng bỏ (req["_bo"]: tên hoạt động, "Gala dinner")."""
    tu, den = du_lieu.tim_diem_di(req["noi_xuat_phat"]), du_lieu.tim_diem_den(req["dia_diem"])
    if not (tu and den):
        return None
    bo = set(req.get("_bo") or [])
    req["khong_muon"] = ["gala"] if "Gala dinner" in bo else []
    dest = du_lieu.dung_diem_den(req, tu, den)
    if bo - {"Gala dinner"}:
        for lv in TIERS:
            dest["raw"][lv]["hoat_dong"] = [h for h in dest["raw"][lv]["hoat_dong"] if h["ten"] not in bo]
            dest["raw"][lv]["_mien_phi"] = [x for x in dest["raw"][lv].get("_mien_phi") or [] if x not in bo]
            dest["calc"][lv] = planner.tinh_goi(req, lv, dest["raw"][lv])
            dest["lich"][lv], _ = du_lieu.lich_tu_du_lieu(req, dest, lv)
    return dest


def customize(req) -> dict:
    """Những gì người dùng sửa được ngay trên trang kế hoạch (bỏ / thêm lại từng khoản, số người, số ngày)."""
    r2 = dict(req, _bo=[])
    full = build_dest(r2)
    opts = []
    if full:
        for lv in TIERS:
            for h in full["raw"][lv]["hoat_dong"]:
                if h["ten"] not in opts and not h["ten"].startswith("Vé phà"):
                    opts.append(h["ten"])
            if full["raw"][lv]["gala"].get("co") and req["so_dem"] > 0 and "Gala dinner" not in opts:
                opts.append("Gala dinner")
    return {"options": opts, "removed": list(req.get("_bo") or []), "headcount": req["so_nguoi"], "days": req["so_ngay"]}


SAN_BAY_TEN = {"HAN": "Sân bay Nội Bài", "HPH": "Sân bay Cát Bi", "DAD": "Sân bay Đà Nẵng", "SGN": "Sân bay Tân Sơn Nhất",
               "VCA": "Sân bay Cần Thơ", "VDO": "Sân bay Vân Đồn", "THD": "Sân bay Thọ Xuân", "VII": "Sân bay Vinh",
               "VDH": "Sân bay Đồng Hới", "HUI": "Sân bay Phú Bài", "UIH": "Sân bay Phù Cát", "TBB": "Sân bay Tuy Hòa",
               "CXR": "Sân bay Cam Ranh", "DLI": "Sân bay Liên Khương", "PQC": "Sân bay Phú Quốc", "VCS": "Sân bay Côn Đảo"}
_OSRM_CACHE: dict = {}
_OSRM_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "var", "osrm_cache.json")


def _duong_bo(a, b):
    """Đường bộ thật giữa 2 điểm (OSRM công khai, dữ liệu OpenStreetMap) — [[lat, lon], ...], km. Lỗi mạng → đường thẳng, approx."""
    import json
    import urllib.request
    if os.environ.get("NO_OSRM"):                         # test / chạy không mạng
        return {"path": [list(a), list(b)], "km": None, "approx": True}
    key = "%.4f,%.4f;%.4f,%.4f" % (a[0], a[1], b[0], b[1])
    if not _OSRM_CACHE and os.path.exists(_OSRM_FILE):
        try:
            _OSRM_CACHE.update(json.load(open(_OSRM_FILE, encoding="utf-8")))
        except Exception:  # noqa: BLE001
            pass
    if key in _OSRM_CACHE:
        return _OSRM_CACHE[key]
    url = ("https://router.project-osrm.org/route/v1/driving/%.5f,%.5f;%.5f,%.5f?overview=simplified&geometries=geojson"
           % (a[1], a[0], b[1], b[0]))
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "AuraFarming-hackathon"}), timeout=8) as r:
            x = json.loads(r.read())["routes"][0]
        out = {"path": [[round(lat, 5), round(lon, 5)] for lon, lat in x["geometry"]["coordinates"]],
               "km": round(x["distance"] / 1000), "approx": False}
    except Exception:  # noqa: BLE001
        return {"path": [list(a), list(b)], "km": None, "approx": True}
    _OSRM_CACHE[key] = out
    try:
        os.makedirs(os.path.dirname(_OSRM_FILE), exist_ok=True)
        json.dump(_OSRM_CACHE, open(_OSRM_FILE, "w", encoding="utf-8"))
    except Exception:  # noqa: BLE001
        pass
    return out


def _cung_bay(a, b, n=24):
    """Cung cong cho chặng bay (chỉ để vẽ)."""
    (la1, lo1), (la2, lo2) = a, b
    mla, mlo = (la1 + la2) / 2, (lo1 + lo2) / 2
    dla, dlo = la2 - la1, lo2 - lo1
    cla, clo = mla - dlo * 0.18, mlo + dla * 0.18            # điểm điều khiển lệch vuông góc
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append([round((1 - t) ** 2 * la1 + 2 * (1 - t) * t * cla + t * t * la2, 5),
                    round((1 - t) ** 2 * lo1 + 2 * (1 - t) * t * clo + t * t * lo2, 5)])
    return pts


def routes(req, dest) -> dict:
    """Các chặng đi theo từng gói: từ đâu → đến đâu, phương tiện, km, giờ, đường vẽ (đường bộ thật / cung bay)."""
    tu, den = dest["tu"], dest["den"]
    A, B = (tu["lat"], tu["lon"]), (den["lat"], den["lon"])
    out = {}
    for lv in TIERS:
        c = dest["raw"][lv]["_chang"]
        t = c["tuyen"]
        xe = c["mo_ta"].split(" đường bộ")[0].split(" đi lại")[0]
        if c["kieu"] == "ve":
            b = t["duong_bay"]
            sa, sb = b["chang"].split("-")
            PA, PB = du_lieu.SAN_BAY[sa], du_lieu.SAN_BAY[sb]
            r1, r3 = _duong_bo(A, PA), _duong_bo(PB, B)
            xe_dich = c["mo_ta"].split("+ ")[-1].replace(" tại chỗ", "")
            legs = [
                {"from": tu["ten"], "to": SAN_BAY_TEN.get(sa, sa), "mode": "road", "vehicle": "Tự đến sân bay (chưa tính trong gói)",
                 "km": r1["km"], "hours": None, "path": r1["path"], "approx": r1["approx"]},
                {"from": SAN_BAY_TEN.get(sa, sa), "to": SAN_BAY_TEN.get(sb, sb), "mode": "flight", "vehicle": "Máy bay %s (vé khứ hồi trong gói)" % b["chang"],
                 "km": b["km"], "hours": round(b["gio_bay"], 1), "path": _cung_bay(PA, PB), "approx": False},
                {"from": SAN_BAY_TEN.get(sb, sb), "to": den["ten"], "mode": "road", "vehicle": xe_dich[0].upper() + xe_dich[1:] + " (trong gói)",
                 "km": r3["km"] or b["km_san_bay_toi_diem_den"], "hours": round(b["km_san_bay_toi_diem_den"] / 50, 1), "path": r3["path"], "approx": r3["approx"]},
            ]
        elif t["duong_bo_km"]:
            r = _duong_bo(A, B)
            legs = [{"from": tu["ten"], "to": den["ten"], "mode": "road", "vehicle": xe[0].upper() + xe[1:] + " (trong gói)",
                     "km": r["km"] or t["duong_bo_km"], "hours": t["duong_bo_gio"], "path": r["path"], "approx": r["approx"],
                     "ferry": bool(t.get("co_pha"))}]
        else:
            legs = []
        out[lv] = legs
    return out


def map_info(req, dest) -> dict:
    tu, den = dest["tu"], dest["den"]
    c = dest["raw"]["tiet_kiem"]["_chang"]
    return {"origin": {"name": tu["ten"], "lat": tu["lat"], "lon": tu["lon"]},
            "dest": {"name": den["ten"], "lat": den["lat"], "lon": den["lon"]},
            "mode": "plane" if c["kieu"] == "ve" else "bus", "routes": routes(req, dest)}


def view_for(req) -> dict:
    """View đầy đủ theo trạng thái req: đã chọn gói (_tier) → 1 kế hoạch; có ngân sách (cách C) → 3 kế hoạch; cách B → chọn gói."""
    dest = build_dest(req)
    if not dest:
        return {"status": "error", "message": "Không tìm thấy địa điểm trong dữ liệu."}
    den = dest["den"]
    base = {"request": echo(req, req.get("_entry", "C")), "destination": den["ten"], "packages": packages(req, dest),
            "customize": customize(req), "map": map_info(req, dest)}
    if req.get("_tier"):
        lv = req["_tier"]
        return dict(base, status="ok", message="Kế hoạch gói %s cho %s." % (dict(planner.PACKAGES)[lv], den["ten"]),
                    plans=[plan(req, dest, lv)])
    if req.get("_entry") == "B":
        return dict(base, status="choose_package", message="Dự trù 3 gói cho %s — chọn gói để lập kế hoạch chi tiết." % den["ten"])
    return dict(base, status="ok", message="3 kế hoạch cho %s." % den["ten"], plans=[plan(req, dest, lv) for lv in TIERS])


def recalc(req, body) -> dict:
    """Sửa ngay trên trang kế hoạch: số người, số ngày, danh sách khoản bỏ → tính lại toàn bộ."""
    req = copy.deepcopy(req)
    if body.headcount:
        req["so_nguoi"] = int(body.headcount)
        if req.get("_ns_moi_nguoi"):
            req["ngan_sach"] = req["_ns_moi_nguoi"] * req["so_nguoi"]
    if body.days:
        req["so_ngay"], req["so_dem"] = int(body.days), max(0, int(body.days) - 1)
    if body.removed is not None:
        req["_bo"] = list(body.removed)
    return view_for(req), req


def estimate(origin, destination, n, days, purpose) -> Optional[dict]:
    """Ước tính nhanh khi đang điền form: tổng / mỗi người của 3 gói."""
    tu, den = du_lieu.tim_diem_di(origin), du_lieu.tim_diem_den(destination)
    if not (tu and den and n and days):
        return None
    req = {"so_nguoi": n, "so_ngay": days, "so_dem": max(0, days - 1), "muc_dich": purpose or "ca_hai", "ngan_sach": None, "khong_muon": []}
    d = du_lieu.dung_diem_den(req, tu, den)
    return {"destination": den["ten"], "origin": tu["ten"],
            "tiers": [{"tier": lv, "total": d["calc"][lv]["tong"], "per_person": d["calc"][lv]["moi_nguoi"]} for lv in TIERS]}


def quote_compare(req, tier, text) -> dict:
    """Soát báo giá tour rồi đặt cạnh gói đã lập (cùng số người, ngân sách)."""
    import soat_bao_gia
    if not re.search(r"\d+\s*(người|khách|nhân viên)", text, re.I):
        text = "Công ty %d người%s.\n%s" % (req["so_nguoi"], (", ngân sách %d triệu" % round(req["ngan_sach"] / 1e6)) if req.get("ngan_sach") else "", text)
    r = soat_bao_gia.soat(text, ket_qua=True)
    if r.get("status") != "ok":
        return r
    dest = build_dest(req)
    g = dest["calc"][tier] if dest else None
    if g:
        chenh = r["tong"] - g["tong"]
        r["doi_chieu"] = {"tier": tier, "ke_hoach": g["tong"], "ke_hoach_moi_nguoi": g["moi_nguoi"], "bao_gia_that": r["tong"],
                          "chenh": chenh, "chenh_pct": round(100.0 * chenh / g["tong"], 1),
                          "nhan_xet": ("Báo giá tour (sau khi cộng khoản ngoài giá) **cao hơn** dự trù gói %s %s — có cơ sở để thương lượng."
                                       if chenh > 0 else "Báo giá tour (sau khi cộng khoản ngoài giá) **thấp hơn** dự trù gói %s %s — kiểm kỹ tour đã gồm đủ hạng mục chưa.")
                                      % (dict(planner.PACKAGES)[tier], planner.fmt_vnd(abs(chenh)))}
    return r


def export_xlsx(view) -> bytes:
    """Tờ trình Excel: tóm tắt 3 gói + bảng chi phí từng gói + lịch trình — cho sếp và kế toán."""
    import io
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    wb = Workbook()
    ws = wb.active
    ws.title = "Tờ trình"
    rq = view.get("request") or {}
    bold, head = Font(bold=True), PatternFill("solid", fgColor="0E7490")
    ws.append(["TỜ TRÌNH DỰ TRÙ CHUYẾN ĐI CÔNG TY — AuraFarming"])
    ws["A1"].font = Font(bold=True, size=14)
    ws.append(["Địa điểm", view.get("destination")])
    ws.append(["Số người", rq.get("headcount")])
    ws.append(["Thời gian", "%s → %s (%s ngày %s đêm)" % (rq.get("start_date"), rq.get("end_date"), rq.get("days"), rq.get("nights"))])
    ws.append(["Xuất phát", rq.get("origin")])
    ws.append(["Ngân sách", rq.get("budget") or "chưa có"])
    ws.append([])
    ws.append(["Gói", "Tổng cả đoàn (đ)", "Mỗi người (đ)", "So với ngân sách", "Đề xuất"])
    for c in ws[ws.max_row]:
        c.font, c.fill = Font(bold=True, color="FFFFFF"), head
    names = dict(planner.PACKAGES)
    for p in view.get("packages") or []:
        ws.append([names[p["tier"]], p["total"], p["per_person"],
                   ("vượt " + planner.fmt_vnd(p["over_budget"])) if p["over_budget"] else ("trong ngân sách" if rq.get("budget") else "—"),
                   "✔" if p["recommended"] else ""])
    ws.append([])
    for t in ["Ghi chú cho kế toán:",
              "- Giá là tham khảo theo hạng khách sạn / nhà hàng và giá thị trường có nguồn, chưa phải báo giá của cơ sở cụ thể.",
              "- Yêu cầu hoá đơn VAT ghi tên công ty; thanh toán chuyển khoản cho hoá đơn từ 5 triệu đồng trở lên.",
              "- Hợp đồng / hoá đơn ghi theo đoàn, không kèm danh sách tên nhân viên.",
              "- Đã gồm 5% dự phòng phát sinh."]:
        ws.append([t])
    ws.column_dimensions["A"].width, ws.column_dimensions["B"].width = 34, 22
    for col in "CDE":
        ws.column_dimensions[col].width = 20
    for p in view.get("packages") or []:
        w = wb.create_sheet("Chi phí " + names[p["tier"]])
        w.append(["Nhóm", "Hạng mục", "Số lượng", "Đơn vị", "Đơn giá (đ)", "Thành tiền (đ)"])
        for c in w[1]:
            c.font, c.fill = Font(bold=True, color="FFFFFF"), head
        for li in p["line_items"]:
            w.append([li["category"], li["description"], li["qty"], li["unit"], li["unit_price"], li["amount"]])
        w.append(["", "TỔNG CẢ ĐOÀN", "", "", "", p["total"]])
        w.append(["", "MỖI NGƯỜI", "", "", "", p["per_person"]])
        for r in (w.max_row - 1, w.max_row):
            for c in w[r]:
                c.font = bold
        w.column_dimensions["B"].width = 70
        for col in "ACDEF":
            w.column_dimensions[col].width = 16
    for pl in view.get("plans") or []:
        w = wb.create_sheet("Lịch " + names[pl["tier"]])
        w.append(["Ngày", "Giờ", "Việc"])
        for c in w[1]:
            c.font, c.fill = Font(bold=True, color="FFFFFF"), head
        for d in pl["days"]:
            for sl in d["slots"]:
                w.append(["%s (%s)" % (d["label"], d["date"]), "%s %s" % (sl["start"], sl.get("note") or ""), sl["title"]])
        w.column_dimensions["A"].width, w.column_dimensions["B"].width, w.column_dimensions["C"].width = 22, 16, 80
    for w in wb.worksheets:
        for row in w.iter_rows():
            for c in row:
                if isinstance(c.value, int) and c.value >= 1000:
                    c.number_format = "#,##0"
                c.alignment = Alignment(vertical="top", wrap_text=isinstance(c.value, str) and len(c.value) > 40)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def create(req) -> dict:
    """req đã đủ trường (missing() rỗng) và handles(req) đúng."""
    tu = du_lieu.tim_diem_di(req["noi_xuat_phat"])
    if not req["dia_diem"]:
        dests = du_lieu.goi_y_diem_den(req, tu)
        if not dests:
            return {"status": "error", "message": "Không tìm được điểm đến nào trong dữ liệu hợp mục đích và thời gian đi."}
        within = [d for d in dests if d["calc"]["tiet_kiem"]["tong"] <= (req["ngan_sach"] or 0)]
        msg = ("Gợi ý %d điểm đến cho %d người từ %s." % (len(dests), req["so_nguoi"], tu["ten"]) if within else
               "Không nơi nào vừa ngân sách; đây là các nơi rẻ nhất — xem ngân sách tối thiểu ở từng gói.")
        req["_entry"] = "A"
        return {"status": "choose_destination", "message": msg, "request": echo(req, "A"),
                "destinations": [destination_option(req, d, i == 0) for i, d in enumerate(dests)]}
    req["_entry"] = "C" if req["ngan_sach"] else "B"
    return view_for(req)


def approve(req, body):
    """Bước duyệt (cách A, B): chọn địa điểm / gói, sửa số người, bỏ gala / team building → 1 kế hoạch. Trả (view, req mới)."""
    req = copy.deepcopy(req)
    if body.headcount:
        req["so_nguoi"] = body.headcount
        if req.get("_ns_moi_nguoi"):                       # ngân sách / người → nhân lại theo số người mới
            req["ngan_sach"] = req["_ns_moi_nguoi"] * body.headcount
    if body.destination:
        req["dia_diem"] = body.destination
    req["_tier"] = body.package
    bo = list(req.get("_bo") or [])
    if "gala" in (body.remove_items or []):
        bo.append("Gala dinner")
    if "team_building" in (body.remove_items or []):
        bo.append(du_lieu.TEN_DICH_VU["team_building"])
    req["_bo"] = bo
    return view_for(req), req
