import json
from dataclasses import replace
from datetime import date

from src.core.orchestration.nodes import trip_nodes as tn
from src.core.planning.estimates import load_estimates
from src.core.planning.pricing import price_packages
from src.core.planning.scheduler import hm, load_menus, load_programs, schedule, slot_minutes, to_min
from src.core.planning.travel import bus_hours, leg
from src.core.planning.types import Candidate, GeoPoint, TierPick, TripRequest
from src.core.planning.validator import validate

EST = load_estimates()
MENUS = load_menus()
PROGRAMS = load_programs()


def make_req(**kw):
    base = dict(headcount=30, days=3, nights=2, start_date=date(2026, 12, 4), origin="Hà Nội",
                purpose="gan_ket", budget=300_000_000, budget_per_person_input=False, destination="Đà Lạt",
                date_assumed=False, entry="C")
    base.update(kw)
    return TripRequest(**base)


def cand(group, name, **kw):
    return Candidate(id="%s:%s" % (group, name.lower().replace(" ", "-")), name=name, group=group,
                     source_url="https://a.vn/" + name.lower().replace(" ", "-"), **kw)


def build(req, tier="can_bang", pick=None, ranked=None):
    near = (GeoPoint(21.0, 105.8), GeoPoint(21.5, 106.2))  # ~70 km: đi xe, tới sớm
    pkgs = {p.tier: p for p in price_packages(req, near[0], near[1], {}, EST)}
    pkg = pkgs[tier]
    plan = schedule(req, pkg, pick or TierPick(None, [], [], {}), ranked or {}, EST, MENUS, PROGRAMS)
    return plan, pkg


def slots(plan, kind):
    return [s for d in plan.days for s in d.slots if s.kind == kind]


def test_schedule_no_overlap_three_days():
    req = make_req()
    plan, pkg = build(req)
    assert len(plan.days) == 3
    assert plan.days[0].label.startswith("Ngày 1 · ") and plan.days[0].date == "2026-12-04"
    for d in plan.days:
        starts = [s.start for s in d.slots]
        assert starts == sorted(starts)
    assert not [v for v in validate(req, plan, pkg) if v.code == "CHONG_GIO"]
    assert plan.days[0].slots[0].start == "06:30"


def test_day_trip_returns_same_day():
    req = make_req(days=1, nights=0)
    plan, pkg = build(req)
    assert len(plan.days) == 1
    last = plan.days[0].slots[-1]
    assert last.kind == "travel" and last.title.startswith("Về")
    assert not slots(plan, "hotel")


def test_meal_has_menu_estimated_when_no_source():
    req = make_req()
    rest = cand("an_uong", "Quan Hoa", menu_items=["Lau bo", "Ga nuong"], capacity=10)
    plan, _ = build(req, pick=TierPick(None, [rest.id], [], {}), ranked={"an_uong": [rest]})
    meals = slots(plan, "meal")
    assert meals[0].menu.estimated is False and meals[0].menu.dishes == ["Lau bo", "Ga nuong"]
    assert "confirm_capacity" in meals[0].flags
    assert all(m.menu.estimated and "estimate" in m.flags for m in meals[1:])
    assert meals[1].menu.dishes


def test_gala_has_program_and_menu():
    plan, _ = build(make_req())
    (gala,) = slots(plan, "gala")
    assert gala.start == "18:30" and gala.menu is not None
    assert len(gala.program["steps"]) >= 5 and gala.program["steps"][-1].end == "21:30"
    assert not slots(build(make_req(), tier="tiet_kiem")[0], "gala")


def test_team_building_has_program_steps_and_fallback():
    plan, _ = build(make_req(), tier="cao_cap")
    tb = [s for s in slots(plan, "activity")]
    assert len(tb) == 1 and tb[0].start == "14:00"
    p = tb[0].program
    assert p["steps"][0].start == "14:00" and p["steps"][-1].end == "17:00" and p["includes"] and p["fallback"]


def test_nghi_duong_has_rest_each_day():
    req = make_req(purpose="nghi_duong")
    plan, _ = build(req)
    assert all(any(s.kind == "rest" for s in d.slots) for d in plan.days)
    assert not slots(plan, "gala") and not slots(plan, "activity")


def test_validate_flags_short_rooms():
    req = make_req()
    plan, pkg = build(req)
    pkg.room_plan = replace(pkg.room_plan, short=3)
    assert "THIEU_PHONG" in [v.code for v in validate(req, plan, pkg)]


def test_validate_flags_duplicate_and_capacity():
    req = make_req()
    r = cand("an_uong", "Quan Hoa", menu_items=["x"], capacity=10)
    plan, pkg = build(req, pick=TierPick(None, [r.id, r.id], [], {}), ranked={"an_uong": [r]})
    codes = [v.code for v in validate(req, plan, pkg)]
    assert "TRUNG_DIEM" in codes and "THIEU_SUC_CHUA" in codes


def fake_select(monkeypatch, payload, calls=None):
    def fake(system, user):
        if calls is not None:
            calls.append(user)
        return {"text": json.dumps(payload), "model": "t", "tokens_in": 0, "tokens_out": 0}
    monkeypatch.setattr(tn, "call_model", fake)


def test_select_drops_unknown_ids(monkeypatch):
    h = cand("luu_tru", "Hotel Mai", stars=4)
    h3 = cand("luu_tru", "Hotel Ba", stars=3)
    r = cand("an_uong", "Quan Hoa")
    ranked = {"luu_tru": [h, h3], "an_uong": [r]}
    pick = {"hotel": h.id, "restaurants": [r.id, "an_uong:bia"], "activities": ["hoat_dong:khong"], "reasons": {r.id: "ngon"}}
    fake_select(monkeypatch, {"tiet_kiem": pick, "can_bang": pick, "cao_cap": {"hotel": h3.id}})
    sink = []
    picks = tn.select_for_tiers(make_req(), ranked, est=EST, sink=sink)
    assert picks["can_bang"].hotel == h.id and picks["can_bang"].restaurants == [r.id]
    assert picks["can_bang"].activities == [] and picks["can_bang"].reasons == {r.id: "ngon"}
    assert picks["tiet_kiem"].hotel is None and picks["cao_cap"].hotel is None  # sai hạng sao
    assert {v.code for v in sink} == {"ID_KHONG_TON_TAI"}


def test_select_no_model_when_estimate_only(monkeypatch):
    calls = []
    fake_select(monkeypatch, {}, calls)
    out = tn.select({"request": make_req(), "ranked": {}, "estimate_only": True, "est": EST})
    assert not calls and all(p.hotel is None and not p.restaurants for p in out["picks"].values())


def test_repair_loop_stops_after_two_rounds(monkeypatch):
    h = cand("luu_tru", "Hotel Mai", stars=4)
    calls = []
    bad = {"hotel": h.id, "restaurants": ["an_uong:khong-co"], "activities": []}
    fake_select(monkeypatch, {t: bad for t in ("tiet_kiem", "can_bang", "cao_cap")}, calls)
    state = {"request": make_req(), "ranked": {"luu_tru": [h]}, "estimate_only": False, "est": EST,
             "origin_pt": None, "dest_pt": None}
    while True:
        for node in (tn.select, tn.price, tn.schedule_node, tn.validate_node):
            state.update(node(state))
        if tn.route_after_validate(state) == "explain":
            break
    assert len(calls) == 3 and state["warnings"] and state["violations"]
    assert "Violation" not in state["warnings"][0] and len(state["plans"]) == 3


def test_route_is_pure_and_validate_node_returns_warning(monkeypatch):
    h = cand("luu_tru", "Hotel Mai", stars=4)
    bad = {"hotel": h.id, "restaurants": ["an_uong:khong-co"]}
    fake_select(monkeypatch, {t: bad for t in ("tiet_kiem", "can_bang", "cao_cap")})
    state = {"request": make_req(), "ranked": {"luu_tru": [h]}, "est": EST, "origin_pt": None, "dest_pt": None,
             "warnings": ["cũ"], "repair_round": 1, "violations": []}
    for node in (tn.select, tn.price, tn.schedule_node):
        state.update(node(state))
    out = tn.validate_node(state)
    assert out["repair_round"] == 2 and out["warnings"][0] == "cũ" and len(out["warnings"]) == 2
    state.update(out)
    before = dict(state)
    assert tn.route_after_validate(state) == "explain" and state == before


def test_select_treats_null_hotel_strings_as_none(monkeypatch):
    h = cand("luu_tru", "Hotel Mai", stars=4)
    fake_select(monkeypatch, {t: {"hotel": v} for t, v in
                              (("tiet_kiem", "null"), ("can_bang", "None"), ("cao_cap", " "))})
    sink = []
    picks = tn.select_for_tiers(make_req(), {"luu_tru": [h]}, est=EST, sink=sink)
    assert all(p.hotel is None for p in picks.values()) and not sink


def test_du_tru_goi_defaults_start_to_travel_today(monkeypatch):
    import tools
    seen = {}
    monkeypatch.setenv("TRAVEL_TODAY", "2026-11-27")
    monkeypatch.setattr(tools, "dinh_vi", lambda *a, **k: None)
    monkeypatch.setattr(tools, "price_packages", lambda req, *a: seen.setdefault("req", req) and [])
    tools.du_tru_goi(30, 2, 1, "Hà Nội", "Đà Lạt")
    assert seen["req"].start_date == date(2026, 12, 4) and seen["req"].date_assumed


HN, DL = GeoPoint(21.03, 105.85), GeoPoint(11.94, 108.44)


def assert_chronological(plan):
    for d in plan.days:
        mins = [to_min(s.start) for s in d.slots]
        assert mins == sorted(mins), (d.label, [s.start for s in d.slots])
        assert all(0 <= m < 24 * 60 for m in mins), (d.label, [s.start for s in d.slots])


def test_hm_never_wraps_past_midnight():
    assert hm(25 * 60 + 10) != "01:10"


def test_every_tier_flies_when_bus_leg_over_10h():
    near_10 = GeoPoint(11.94 + 4.0, 108.44)  # ~ 580 km đường bộ, xe ~ 13 giờ
    km = 0
    for tier in ("tiet_kiem", "can_bang", "cao_cap"):
        lg = leg(near_10, DL, tier, 50, "Đà Lạt", EST, days=3)
        assert bus_hours(lg.road_km) > 10 and lg.mode == "plane", tier
        km = lg.road_km
    assert km


def test_bus_up_to_10h_stays_bus_for_non_premium():
    p = GeoPoint(11.94 + 2.6, 108.44)  # xe ~ 8–10 giờ
    lg = leg(p, DL, "tiet_kiem", 50, "Đà Lạt", EST, days=3)
    assert 8 < bus_hours(lg.road_km) <= 10 and lg.mode == "bus"


def test_hanoi_dalat_50_people_all_tiers_fly_and_clock_valid():
    req = make_req(headcount=50, days=3, nights=2)
    pkgs = price_packages(req, HN, DL, {}, EST)
    assert [p.leg.mode for p in pkgs] == ["plane"] * 3
    for pkg in pkgs:
        plan = schedule(req, pkg, TierPick(), {}, EST, MENUS, PROGRAMS)
        assert_chronological(plan)
        day1 = plan.days[0].slots
        arrive = to_min(day1[0].start) + slot_minutes(day1[0], pkg)
        lunch = next(s for s in day1 if s.kind == "meal")
        assert to_min(lunch.start) >= arrive
        codes = {v.code for v in validate(req, plan, pkg)}
        assert "CHONG_GIO" not in codes and "QUA_GIO_KET_THUC" not in codes, (pkg.tier, codes)


def test_leg_past_midnight_moves_arrival_to_next_day():
    req = make_req(headcount=50, days=3, nights=2)
    plan, pkg = build(req)
    pkg.leg = replace(pkg.leg, mode="bus", hours=31.7)
    plan = schedule(req, pkg, TierPick(), {}, EST, MENUS, PROGRAMS)
    assert_chronological(plan)
    assert [s.kind for s in plan.days[0].slots] == ["travel"]
    arrive = 6 * 60 + 30 + int(round(31.7 * 60)) - 24 * 60  # 14:12 ngày 2
    assert "14:12" in plan.days[0].slots[0].details and "ngày 2" in plan.days[0].slots[0].details
    day2 = plan.days[1].slots
    assert day2[0].kind == "meal" and to_min(day2[0].start) >= arrive
    assert any(s.kind == "hotel" and s.title.startswith("Nhận phòng") for s in day2)


def test_return_past_midnight_is_not_shown_as_early_morning():
    req = make_req(days=2, nights=1)
    plan, pkg = build(req)
    pkg.leg = replace(pkg.leg, hours=12.0)
    plan = schedule(req, pkg, TierPick(), {}, EST, MENUS, PROGRAMS)
    ret = plan.days[-1].slots[-1]
    assert ret.title.startswith("Về") and "hôm sau" in ret.details


def test_day_trip_late_return_flagged():
    req = make_req(days=1, nights=0)
    plan, pkg = build(req)
    pkg.leg = replace(pkg.leg, hours=9.0)
    plan = schedule(req, pkg, TierPick(), {}, EST, MENUS, PROGRAMS)
    assert "VE_MUON" in {v.code for v in validate(req, plan, pkg)}


def test_day_trip_near_not_flagged_late():
    req = make_req(days=1, nights=0)
    plan, pkg = build(req)
    codes = {v.code for v in validate(req, plan, pkg)}
    assert "VE_MUON" not in codes and "QUA_GIO_KET_THUC" not in codes and "CHONG_GIO" not in codes
