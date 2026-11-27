"""Xếp lịch bằng code: schedule(req, pkg, pick, ranked, est, menus, programs) -> Plan.
Model chỉ chọn id; giờ, thực đơn, chương trình do code ghép. Mỗi khối nối tiếp theo con trỏ thời gian
nên không chồng nhau; giờ cố định (trưa 11:30, tối 18:00, gala 18:30, team building 14:00) chỉ đẩy muộn
khi chặng đi kéo dài. Chỉ thư viện chuẩn + planning."""
import json
from datetime import timedelta
from pathlib import Path
from typing import Optional

from .estimates import Estimates
from .types import Candidate, Day, Menu, Package, Plan, ProgramStep, Slot, TierPick, TripRequest

DATA_DIR = Path(__file__).resolve().parents[5] / "data"
WEEKDAYS = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
RETURN_PREFIX = "Về"
DURATION = {"hotel": 30, "meal": 90, "activity": 180, "sight": 150, "rest": 90, "gala": 180}
DEFAULT_TRAVEL_MIN = 240


def load_menus(path: Optional[Path] = None) -> dict:
    """data/menus.json: tier -> list thực đơn mẫu (role: bua_trua | bua_toi | gala)."""
    raw = json.loads(Path(path or DATA_DIR / "menus.json").read_text(encoding="utf-8"))
    return {k: v for k, v in raw.items() if not k.startswith("_")}


def load_programs(path: Optional[Path] = None) -> dict:
    """data/programs.json: gala, team_building[tier], nghi_duong.rest; bước theo offset/minutes."""
    raw = json.loads(Path(path or DATA_DIR / "programs.json").read_text(encoding="utf-8"))
    return {k: v for k, v in raw.items() if not k.startswith("_")}


def to_min(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def hm(minutes: int) -> str:
    minutes %= 24 * 60
    return "%02d:%02d" % (minutes // 60, minutes % 60)


def _step_end(step) -> str:
    return step["end"] if isinstance(step, dict) else step.end


def slot_minutes(slot: Slot, pkg) -> int:
    """Thời lượng một khối (phút): chặng đi/về = leg.hours; có chương trình = đến bước cuối; còn lại theo loại."""
    steps = (slot.program or {}).get("steps")
    if steps:
        return to_min(_step_end(steps[-1])) - to_min(slot.start)
    if slot.kind == "travel":
        leg = getattr(pkg, "leg", None)
        return int(round(leg.hours * 60)) if leg else DEFAULT_TRAVEL_MIN
    return DURATION[slot.kind]


def _steps(prog: dict, start: int) -> list[ProgramStep]:
    return [ProgramStep(hm(start + s["offset"]), hm(start + s["offset"] + s["minutes"]), s["text"])
            for s in prog["steps"]]


def _cap_note(c: Candidate) -> Optional[str]:
    return "Sức chứa theo nguồn: %d người" % c.capacity if c.capacity else None


def schedule(req: TripRequest, pkg: Package, pick: TierPick, ranked: dict, est: Estimates,
             menus: dict, programs: dict) -> Plan:
    tier, n, days = pkg.tier, req.headcount, req.days
    by_id = {c.id: c for items in ranked.values() for c in items}
    hotel = by_id.get(pick.hotel) if pick.hotel else None
    leg = pkg.leg
    dest = req.destination or "điểm đến"
    rest_mode = req.purpose == "nghi_duong"
    has_gala = any(li.category == "Gala" for li in pkg.line_items)
    team = any(li.category == "Hoạt động" and li.description == "Team building" for li in pkg.line_items)
    restaurants = iter(pick.restaurants)
    acts = [by_id[a] for a in pick.activities if a in by_id]
    tb_cand = acts.pop(0) if team and acts else None
    tmpl = {m["role"]: m for m in menus.get(tier, [])}

    def template(role: str) -> dict:
        return tmpl.get(role) or next(iter(tmpl.values()), {"name": "Thực đơn mẫu", "dishes": []})

    def meal(role: str, label: str, cur: int, fixed: int) -> Slot:
        c = by_id.get(next(restaurants, None))
        t = template(role)
        price = est.meal_per_pax[tier]
        if c is not None and c.menu_items:
            menu = Menu(c.name, c.price_per_pax or price, list(c.menu_items), False, t.get("table_size"),
                        None, c.price_source_url or c.source_url)
        else:
            menu = Menu(t["name"], price, list(t["dishes"]), True, t.get("table_size"), t.get("drinks_note"))
        flags = ["estimate"] if menu.estimated else []
        if c is not None and (c.capacity is None or c.capacity < n):
            flags.append("confirm_capacity")
        title = "%s – %s" % (label, c.name) if c else "%s (nhà hàng địa phương)" % label
        return Slot(hm(max(cur, fixed)), "meal", title, note=pick.reasons.get(c.id) if c else None, flags=flags,
                    source_url=c.source_url if c else None, menu=menu, details=_cap_note(c) if c else None)

    def sight(cur: int, fixed: int, d: int, part: str) -> Slot:
        c = acts.pop(0) if acts else None
        if c is None:
            return Slot(hm(max(cur, fixed)), "sight", "Tham quan %s – %s ngày %d" % (dest, part, d),
                        flags=["estimate"])
        return Slot(hm(max(cur, fixed)), "sight", c.name, note=pick.reasons.get(c.id), source_url=c.source_url,
                    details=_cap_note(c))

    def hotel_in(cur: int, fixed: int) -> Slot:
        if hotel is None:
            title, flags, url = "Nhận phòng khách sạn %d sao" % est.tier_stars[tier], ["estimate", "confirm_rooms"], None
        else:
            kinds = list(pkg.room_plan.counts) if pkg.room_plan else []
            used = [r for r in hotel.room_types if r.kind in kinds]
            flags = [] if hotel.room_types and used and all(r.available is not None for r in used) else ["confirm_rooms"]
            if not hotel.room_types:
                flags.append("estimate")
            title, url = "Nhận phòng – %s" % hotel.name, hotel.source_url
        return Slot(hm(max(cur, fixed)), "hotel", title, note=pick.reasons.get(pick.hotel) if hotel else None,
                    flags=flags, source_url=url, details=pkg.summary.rooms or None)

    out_days = []
    for d in range(1, days + 1):
        first, last = d == 1, d == days
        slots: list[Slot] = []
        cur = 0

        def add(slot: Slot) -> Slot:
            nonlocal cur
            slots.append(slot)
            cur = to_min(slot.start) + slot_minutes(slot, pkg)
            return slot

        if first:
            plane = leg.mode == "plane"
            start = 330 if plane else 390
            title = ("Tập hợp ra sân bay %s, bay đi %s" % (req.origin, dest)) if plane else \
                "Xuất phát từ %s đi %s" % (req.origin, dest)
            add(Slot(hm(start), "travel", title, note=leg.note, flags=["estimate"] if leg.estimated else [],
                     details="Khoảng %s km, dự kiến %s giờ" % (leg.road_km, leg.hours)))
        else:
            if last and req.nights >= 1:
                add(Slot("08:00", "hotel", "Trả phòng khách sạn"))
            add(sight(cur, 510, d, "buổi sáng"))
        add(meal("bua_trua", "Bữa trưa", cur, 690))
        if first and req.nights >= 1:
            add(hotel_in(cur, 780))
        if rest_mode:
            r = programs["nghi_duong"]["rest"][(d - 1) % len(programs["nghi_duong"]["rest"])]
            add(Slot(hm(max(cur, 780 if last else 840)), "rest", r["title"], details=r["details"]))
        if first and team:
            s = max(cur, 840)
            prog = programs["team_building"][tier]
            add(Slot(hm(s), "activity", ("Team building – %s" % tb_cand.name) if tb_cand else "Team building",
                     note=pick.reasons.get(tb_cand.id) if tb_cand else None,
                     flags=[] if tb_cand else ["estimate"], source_url=tb_cand.source_url if tb_cand else None,
                     program={"title": prog["title"], "steps": _steps(prog, s), "includes": prog["includes"],
                              "fallback": prog["fallback"]}))
        if not (first and team) and (not last or first) and (not rest_mode or last):
            add(sight(cur, 840, d, "buổi chiều"))
        if not last:
            if has_gala and d == days - 1:
                s = max(cur, 1110)
                prog = programs["gala"]
                t = template("gala")
                menu = Menu(t["name"], est.gala_per_pax[tier], list(t["dishes"]), True, t.get("table_size"),
                            t.get("drinks_note"))
                add(Slot(hm(s), "gala", "Gala dinner", flags=["estimate"], menu=menu,
                         program={"title": prog["title"], "steps": _steps(prog, s)}))
            else:
                add(meal("bua_toi", "Bữa tối", cur, 1080))
        else:
            dep = max(cur, 960 if first else 840)
            arrive = dep + int(round(leg.hours * 60))
            add(Slot(hm(dep), "travel", "%s %s" % (RETURN_PREFIX, req.origin), note=leg.note,
                     flags=["estimate"] if leg.estimated else [],
                     details="Dự kiến đến nơi lúc %s" % hm(arrive)))
        day_date = req.start_date + timedelta(days=d - 1)
        out_days.append(Day("Ngày %d · %s" % (d, WEEKDAYS[day_date.weekday()]), day_date.isoformat(), slots))

    est_total = sum(li.amount for li in pkg.line_items if li.estimated)
    return Plan(tier=tier, destination=dest, total=pkg.total, per_person=pkg.per_person,
                estimate_total=est_total,
                estimate_note="Các khoản ước tính dùng bảng giá tự ước tính, cần báo giá thực tế." if est_total else None,
                over_budget=pkg.over_budget, explanation=pkg.explanation, days=out_days)
