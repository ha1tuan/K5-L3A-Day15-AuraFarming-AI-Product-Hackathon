import re
from datetime import date

from src.core.planning.estimates import load_estimates, round1k
from src.core.planning.explain import explain_over
from src.core.planning.pricing import price_packages
from src.core.planning.render import render_text, to_view
from src.core.planning.scheduler import load_menus, load_programs, schedule
from src.core.planning.types import GeoPoint, TierPick, TripRequest

EST = load_estimates()
HN = GeoPoint(21.0285, 105.8542, "VN")
HALONG = GeoPoint(20.9517, 107.0800, "VN")
LINE = re.compile(r"^- (.+): (\d+) (\S+) × ([\d.]+)đ = ([\d.]+)đ$")


def money(s: str) -> int:
    return int(s.replace(".", ""))


def make(budget=150_000_000, **kw):
    base = dict(headcount=60, days=3, nights=2, start_date=date(2026, 12, 4), origin="Hà Nội", purpose="gan_ket",
                budget=budget, budget_per_person_input=False, destination="Hạ Long", date_assumed=True, entry="C")
    base.update(kw)
    req = TripRequest(**base)
    pkgs = price_packages(req, HN, HALONG, {}, EST)
    explain_over(pkgs, req.budget, req, EST, HN, HALONG, {})
    plans = [schedule(req, p, TierPick(), {}, EST, load_menus(), load_programs()) for p in pkgs]
    for plan, p in zip(plans, pkgs):
        plan.explanation = p.explanation
    return req, pkgs, plans


def blocks(text: str) -> list[str]:
    return text.split("=== Kế hoạch")[1:]


def test_render_cost_lines_parse_and_add_up():
    req, pkgs, plans = make()
    text = render_text(req, pkgs, plans)
    assert text.startswith("Ngân sách đã hiểu: 150.000.000đ cho 60 người")
    parts = blocks(text)
    assert len(parts) == 3
    for part, pkg in zip(parts, pkgs):
        rows = [LINE.match(x) for x in part.splitlines()]
        rows = [m for m in rows if m]
        assert rows, part
        for m in rows:
            assert int(m.group(2)) * money(m.group(4)) == money(m.group(5))
        total = sum(money(m.group(5)) for m in rows)
        assert total == pkg.total
        assert "Tổng cộng: %s" % f"{total:,}".replace(",", ".") in part
        fee = next(m for m in rows if m.group(1).startswith("Dự phòng phát sinh 5%"))
        assert money(fee.group(5)) == round1k((total - money(fee.group(5))) * 0.05)
        per = re.search(r"Mỗi người: ([\d.]+)đ", part).group(1)
        assert money(per) == round1k(total / req.headcount)
    assert text.rstrip().endswith("Giá tham khảo; hệ thống không đặt chỗ.")


def test_render_over_budget_has_explanation_and_schedule():
    req, pkgs, plans = make(budget=100_000_000)
    text = render_text(req, pkgs, plans)
    for part in blocks(text):
        assert "Vượt ngân sách" in part and "Cách cắt giảm" in part
        assert "Cơ cấu phòng" in part and "Ngày 1 · " in part
    assert "Gala dinner" in text and "Thực đơn" in text and "Chương trình" in text
    assert " 0đ = 0đ" not in text


def test_render_estimate_only_says_no_source():
    req, pkgs, plans = make()
    text = render_text(req, pkgs, plans, estimate_only=True)
    assert "chưa tìm được nguồn" in text


def test_to_view_matches_web_contract():
    req, pkgs, plans = make(budget=100_000_000)
    v = to_view("t1", req, pkgs, plans)
    for k in ("trip_id", "status", "message", "request", "packages", "plans"):
        assert k in v
    assert v["status"] == "ok" and v["destination"] == "Hạ Long"
    assert v["request"] == {"headcount": 60, "days": 3, "nights": 2, "start_date": "2026-12-04",
                            "end_date": "2026-12-06", "origin": "Hà Nội", "purpose": "gan_ket",
                            "budget": 100_000_000, "entry": "C"}
    p = v["packages"][0]
    assert set(p) >= {"tier", "summary", "line_items", "total", "per_person", "over_budget", "recommended"}
    assert "leg" not in p and "room_plan" not in p
    assert p["explanation"]["drivers"]
    slot = v["plans"][0]["days"][0]["slots"][0]
    assert {"start", "kind", "title"} <= set(slot)
    assert all(val is not None for val in slot.values())
