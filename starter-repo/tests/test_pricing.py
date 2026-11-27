import json
from dataclasses import replace
from datetime import date
from pathlib import Path

from src.core.planning.estimates import load_estimates
from src.core.planning.pricing import price_packages, price_tier, round1k
from src.core.planning.rooms import allocate_rooms
from src.core.planning.travel import bus_hours, leg
from src.core.planning.types import Candidate, GeoPoint, RoomType, TripRequest

HERE = Path(__file__).parent
EST = load_estimates(HERE / "fixtures" / "estimates_small.json")
HN = GeoPoint(21.0285, 105.8542, "VN")
HALONG = GeoPoint(20.9517, 107.0800, "VN")
PQ = GeoPoint(10.2899, 103.9840, "VN")
NHA_TRANG = GeoPoint(12.2388, 109.1967, "VN")
NINH_BINH = GeoPoint(20.2506, 105.9745, "VN")
REQ_C_60 = TripRequest(headcount=60, days=3, nights=2, start_date=date(2026, 12, 4), origin="Hà Nội",
                       purpose="gan_ket", budget=150_000_000, budget_per_person_input=False,
                       destination="Hạ Long", date_assumed=False, entry="C")


def rt(kind, cap, price, available=None):
    return RoomType(kind=kind, capacity=cap, price=price, available=available)


def test_rooms_47():
    r = allocate_rooms(47, [rt("4", 4, 1_600_000), rt("3", 3, 1_350_000), rt("2", 2, 1_100_000)])
    assert r.seats >= 47 and r.cost_per_night == 18_950_000
    assert r.counts == {"4": 11, "3": 1}


def test_rooms_respects_available():
    r = allocate_rooms(60, [rt("4", 4, 1_600_000, available=5), rt("2", 2, 1_100_000)])
    assert r.counts == {"4": 5, "2": 20} and r.short == 0


def test_rooms_short_when_all_limited():
    assert allocate_rooms(60, [rt("4", 4, 1_600_000, available=5)]).short == 40


def test_leg_flight_only_destination():
    assert leg(HN, PQ, "tiet_kiem", 30, "Phú Quốc", EST).mode == "plane"


def test_leg_premium_flies_when_road_over_8h():
    # R13: xe 8–10 giờ -> chỉ cao cấp bay; xe quá 10 giờ (Hà Nội – Nha Trang) -> mọi gói bay
    mid = GeoPoint(HALONG.lat - 2.6, HALONG.lon)
    assert 8 < bus_hours(leg(mid, HALONG, "tiet_kiem", 40, "Hạ Long", EST).road_km) <= 10
    assert leg(mid, HALONG, "cao_cap", 40, "Hạ Long", EST).mode == "plane"
    assert leg(mid, HALONG, "tiet_kiem", 40, "Hạ Long", EST).mode == "bus"
    assert all(leg(HN, NHA_TRANG, t, 40, "Nha Trang", EST).mode == "plane" for t in ("tiet_kiem", "can_bang"))


def test_leg_missing_coords_assumes_300km():
    lg = leg(None, HALONG, "tiet_kiem", 60, "Hạ Long", EST)
    assert (lg.road_km, lg.estimated, lg.vehicles) == (300, True, 2)


def test_package_lines_add_up():
    for p in price_packages(REQ_C_60, HN, HALONG, {}, EST):
        assert all(li.amount == li.qty * li.unit_price for li in p.line_items)
        other = sum(li.amount for li in p.line_items if li.category != "Phát sinh")
        fee = next(li for li in p.line_items if li.category == "Phát sinh").amount
        assert fee == round1k(other * 0.05) and p.total == other + fee
        assert p.leg is not None and p.room_plan is not None and p.room_plan.short == 0


def test_price_day_trip_has_no_lodging():
    for p in price_packages(replace(REQ_C_60, days=1, nights=0), HN, NINH_BINH, {}, EST):
        cats = {li.category for li in p.line_items}
        assert "Lưu trú" not in cats and "Gala" not in cats


def test_exclude_gala_removes_lines():
    pk = price_packages(replace(REQ_C_60, exclude={"gala"}), HN, HALONG, {}, EST)
    assert all(li.category != "Gala" for p in pk for li in p.line_items)


def test_gala_only_for_upper_tiers():
    by_tier = {p.tier: p for p in price_packages(REQ_C_60, HN, HALONG, {}, EST)}
    has = {t: any(li.category == "Gala" for li in p.line_items) for t, p in by_tier.items()}
    assert has == {"tiet_kiem": False, "can_bang": True, "cao_cap": True}


def test_recommended_is_highest_within_budget():
    pk = price_packages(REQ_C_60, HN, HALONG, {}, EST)
    assert [p.tier for p in pk if p.recommended] == ["can_bang"]
    assert pk[0].total <= 150_000_000 and pk[1].total <= 150_000_000 < pk[2].total
    assert pk[2].over_budget == pk[2].total - 150_000_000


def test_recommended_falls_back_to_cheapest():
    pk = price_packages(replace(REQ_C_60, budget=1_000_000), HN, HALONG, {}, EST)
    assert [p.tier for p in pk if p.recommended] == ["tiet_kiem"]


def test_price_tier_category_tiers_changes_only_lodging():
    base = price_tier(REQ_C_60, "cao_cap", HN, HALONG, None, EST)
    cut = price_tier(REQ_C_60, "cao_cap", HN, HALONG, None, EST, category_tiers={"Lưu trú": "tiet_kiem"})
    lodging = lambda p: sum(li.amount for li in p.line_items if li.category == "Lưu trú")  # noqa: E731
    rest = lambda p: [(li.category, li.amount) for li in p.line_items if li.category not in ("Lưu trú", "Phát sinh")]  # noqa: E731
    assert lodging(cut) < lodging(base) and rest(cut) == rest(base)


def test_price_tier_drop_gala_restores_dinner():
    base = price_tier(REQ_C_60, "cao_cap", HN, HALONG, None, EST)
    cut = price_tier(REQ_C_60, "cao_cap", HN, HALONG, None, EST, drop={"Gala"})
    assert all(li.category != "Gala" for li in cut.line_items) and cut.total < base.total
    dinners = lambda p: sum(1 for li in p.line_items if li.description.endswith("bữa tối"))  # noqa: E731
    assert dinners(cut) == dinners(base) + 1


def test_price_tier_nights_override():
    p = price_tier(REQ_C_60, "can_bang", HN, HALONG, None, EST, nights=1)
    assert "1 đêm" in p.summary.rooms and sum(1 for li in p.line_items if li.description.endswith("bữa trưa")) == 2


def test_round1k_half_up():
    assert (round1k(1_499), round1k(1_500), round1k(2_500)) == (1_000, 2_000, 3_000)


def test_real_estimates_file_loads_and_every_value_has_source():
    path = Path(__file__).resolve().parents[1] / "data" / "estimates.json"
    def walk(node):
        if isinstance(node, dict):
            assert "_source" in node or all(isinstance(v, (dict, list)) for v in node.values()), node
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
    walk(json.loads(path.read_text(encoding="utf-8")))
    est = load_estimates()
    assert est.tier_stars == {"tiet_kiem": 3, "can_bang": 4, "cao_cap": 5} and "Phú Quốc" in est.flight_only


def _lodging(p):
    return [(li.description, li.qty, li.unit_price) for li in p.line_items if li.category == "Lưu trú"]


def _hotel(**kw):
    return Candidate(id="h1", name="KS Thật", group="luu_tru", **kw)


def test_category_tiers_lodging_ignores_passed_hotel():
    real = _hotel(stars=5, room_types=[rt("2", 2, 9_000_000), rt("4", 4, 9_500_000)])
    cut = price_tier(REQ_C_60, "cao_cap", HN, HALONG, real, EST, category_tiers={"Lưu trú": "tiet_kiem"})
    generic = price_tier(REQ_C_60, "tiet_kiem", HN, HALONG, None, EST)
    assert _lodging(cut) == _lodging(generic)
    assert "KS Thật" not in cut.summary.lodging and cut.summary.lodging == generic.summary.lodging


def test_hotel_with_unlisted_stars_falls_back_to_tier_rooms():
    for stars in (1, 2, None):
        p = price_tier(REQ_C_60, "can_bang", HN, HALONG, _hotel(stars=stars), EST)
        generic = price_tier(REQ_C_60, "can_bang", HN, HALONG, None, EST)
        assert [x[1:] for x in _lodging(p)] == [x[1:] for x in _lodging(generic)]


def test_no_rooms_available_note_not_on_transport_line():
    sold_out = _hotel(room_types=[rt("4", 4, 1_000_000, available=0)])
    p = price_tier(REQ_C_60, "can_bang", HN, HALONG, sold_out, EST)
    assert p.room_plan.short == 60
    assert p.line_items[0].category == "Di chuyển" and p.line_items[0].note is None
    assert any(li.category == "Lưu trú" and li.note and "Thiếu chỗ" in li.note for li in p.line_items)


def test_short_hotel_prices_missing_people_with_generic_rooms():
    req = replace(REQ_C_60, headcount=50, budget=None)
    short = _hotel(stars=4, room_types=[rt("2", 2, 1_000_000, available=3)])  # "còn 3 phòng" cho 50 người
    p = price_tier(req, "can_bang", HN, HALONG, short, EST)
    assert p.room_plan.short == 44
    hotel_part = 3 * 1_000_000 * req.nights
    extra = allocate_rooms(44, EST.rooms[str(EST.tier_stars["can_bang"])])
    lodging = sum(li.amount for li in p.line_items if li.category == "Lưu trú")
    assert lodging == hotel_part + extra.cost_per_night * req.nights
    generic_lines = [li for li in p.line_items if li.category == "Lưu trú" and li.estimated]
    assert generic_lines and all("44 người" in li.description for li in generic_lines)
    assert any(li.note and "Thiếu chỗ cho 44 người" in li.note for li in p.line_items)
    assert sum(li.amount for li in p.line_items) == p.total


def test_short_hotel_recommendation_uses_full_total():
    req = replace(REQ_C_60, headcount=50)
    short = _hotel(stars=4, room_types=[rt("2", 2, 1_000_000, available=3)])
    full = price_tier(replace(req, budget=None), "can_bang", HN, HALONG, short, EST).total
    pk = price_packages(replace(req, budget=full - 1), HN, HALONG, {"can_bang": short}, EST)
    assert pk[1].total == full and pk[1].over_budget == 1 and not pk[1].recommended
    assert pk[1].room_plan.short == 44
