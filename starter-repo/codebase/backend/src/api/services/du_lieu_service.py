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
import sys
from datetime import date, timedelta
from typing import Optional

_CODEBASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
if _CODEBASE not in sys.path:
    sys.path.insert(0, _CODEBASE)

import du_lieu  # noqa: E402
import planner  # noqa: E402

TIERS = [lv for lv, _ in planner.PACKAGES]
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


def start_date(req) -> date:
    if req.get("start_date"):
        try:
            return date.fromisoformat(req["start_date"])
        except ValueError:
            pass
    try:
        today = date.fromisoformat(os.environ.get("TRAVEL_TODAY") or "")
    except ValueError:
        today = date.today()
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


def package(req, dest, lv, recommended) -> dict:
    g = dest["calc"][lv]
    items = [{"category": grp, "description": ten, "qty": sl, "unit": dv, "unit_price": dg, "amount": tt, "estimated": True}
             for grp, ten, sl, dv, dg, tt in g["lines"]]
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


def extra(req, dest, lv) -> dict:
    """Thông tin thêm cho người dùng (web) — câu chữ thường, không tên file / thuật ngữ kỹ thuật."""
    raw, den = dest["raw"][lv], dest["den"]
    c = raw["_chang"]
    di = (c["mo_ta"][0].upper() + c["mo_ta"][1:]).replace(" đường bộ ", " · đường bộ ").replace(" + ", " · ")
    if c["gio"]:
        di += " · khoảng %s giờ mỗi chiều%s" % (_gio(c["gio"]), " (đã gồm thủ tục bay, đưa đón sân bay)" if c["kieu"] == "ve" else "")
    thang = du_lieu.thang_hien_tai()
    trong_mua = du_lieu._trong_mua(den["mua_dep_thang"], thang)
    sights = [h["ten"] for h in raw["hoat_dong"] if h["ten"] not in du_lieu.TEN_DICH_VU.values() and not h["ten"].startswith("Vé phà")]
    sights += list(raw.get("_mien_phi") or [])
    return {"travel": di, "lodging": raw.get("_luu_tru_chi_tiet") or "Không lưu trú (đi về trong ngày)",
            "season": {"months": den["mua_dep_thang"], "in_season": trong_mua, "month_now": thang},
            "sights": sights,
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
    den = du_lieu.tim_diem_den(req["dia_diem"])
    dest = du_lieu.dung_diem_den(req, tu, den)
    if req["ngan_sach"]:
        return {"status": "ok", "message": "3 kế hoạch cho %s." % den["ten"], "request": echo(req, "C"), "destination": den["ten"],
                "packages": packages(req, dest), "plans": [plan(req, dest, lv) for lv in TIERS]}
    req["_entry"] = "B"
    return {"status": "choose_package", "message": "Dự trù 3 gói cho %s — chọn gói để lập kế hoạch chi tiết." % den["ten"],
            "request": echo(req, "B"), "destination": den["ten"], "packages": packages(req, dest)}


def approve(req, body) -> dict:
    """Bước duyệt (cách A, B): đổi địa điểm / gói / số người / bỏ gala, team building → tính lại → 1 kế hoạch."""
    req = copy.deepcopy(req)
    if body.headcount:
        req["so_nguoi"] = body.headcount
        if req.get("_ns_moi_nguoi"):                       # ngân sách / người → nhân lại theo số người mới
            req["ngan_sach"] = req["_ns_moi_nguoi"] * body.headcount
    if body.destination:
        req["dia_diem"] = body.destination
    for x in body.remove_items or []:
        req["khong_muon"].append("gala" if x == "gala" else "team building")
    tu, den = du_lieu.tim_diem_di(req["noi_xuat_phat"]), du_lieu.tim_diem_den(req["dia_diem"])
    if not (tu and den):
        return {"status": "error", "message": "Không tìm thấy địa điểm trong dữ liệu."}
    dest = du_lieu.dung_diem_den(req, tu, den)
    if "team building" in req["khong_muon"]:
        for lv in TIERS:
            dest["raw"][lv]["hoat_dong"] = [h for h in dest["raw"][lv]["hoat_dong"] if not h.get("team_building")]
            dest["calc"][lv] = planner.tinh_goi(req, lv, dest["raw"][lv])
            dest["lich"][lv], _ = du_lieu.lich_tu_du_lieu(req, dest, lv)
    lv = body.package
    return {"status": "ok", "message": "Kế hoạch gói %s cho %s." % (dict(planner.PACKAGES)[lv], den["ten"]),
            "request": echo(req, req.get("_entry", "A")), "destination": den["ten"],
            "packages": packages(req, dest), "plans": [plan(req, dest, lv)]}
