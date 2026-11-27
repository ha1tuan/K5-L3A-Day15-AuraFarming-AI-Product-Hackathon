from collections import defaultdict
from dataclasses import replace
from datetime import date
from pathlib import Path

from src.core.planning.estimates import load_estimates
from src.core.planning.explain import explain_over
from src.core.planning.pricing import price_packages, price_tier
from src.core.planning.types import GeoPoint, TripRequest

EST = load_estimates(Path(__file__).parent / "fixtures" / "estimates_small.json")
HN = GeoPoint(21.0285, 105.8542, "VN")
HALONG = GeoPoint(20.9517, 107.0800, "VN")
REQ = TripRequest(headcount=60, days=3, nights=2, start_date=date(2026, 12, 4), origin="Hà Nội",
                  purpose="gan_ket", budget=150_000_000, budget_per_person_input=False,
                  destination="Hạ Long", date_assumed=False, entry="C")


def run(req):
    pk = price_packages(req, HN, HALONG, {}, EST)
    explain_over(pk, req.budget, req, EST, HN, HALONG, {})
    return {p.tier: p for p in pk}


def by_cat(p):
    d = defaultdict(int)
    for li in p.line_items:
        if li.category != "Phát sinh":
            d[li.category] += li.amount
    return d


def test_over_amount_and_pct():
    req = replace(REQ, budget=100_000_000)
    pk = run(req)
    over = [p for p in pk.values() if p.over_budget > 0]
    assert over
    for p in over:
        assert p.explanation.over_amount == p.total - 100_000_000
        assert p.explanation.over_pct == round(p.explanation.over_amount / 100_000_000 * 100)


def test_drivers_match_category_deltas():
    pk = run(replace(REQ, budget=1_000_000))
    p, lower = pk["cao_cap"], pk["can_bang"]
    ex = p.explanation
    assert ex.compared_to == "can_bang" and 2 <= len(ex.drivers) <= 3
    cur, prev = by_cat(p), by_cat(lower)
    deltas = sorted((cur[c] - prev.get(c, 0) for c in cur), reverse=True)
    assert [d["amount"] for d in ex.drivers] == deltas[:len(ex.drivers)]
    assert all(" thay " in d["label"] for d in ex.drivers)
    assert len(pk["tiet_kiem"].explanation.drivers) == 2 and pk["tiet_kiem"].explanation.compared_to is None


def test_cut_totals_are_recomputed():
    pk = run(replace(REQ, budget=1_000_000))
    p = pk["cao_cap"]
    cuts = {c["label"]: c for c in p.explanation.cuts}
    assert len(cuts) <= 3
    assert [c["saving"] for c in p.explanation.cuts] == sorted((c["saving"] for c in cuts.values()), reverse=True)
    for c in cuts.values():
        assert c["saving"] == p.total - c["total_after"] > 0
    full = p.explanation.cuts
    nights = price_tier(REQ, "cao_cap", HN, HALONG, None, EST, nights=1).total
    gala = price_tier(REQ, "cao_cap", HN, HALONG, None, EST, drop=frozenset({"Gala"})).total
    totals = {c["total_after"] for c in full}
    assert totals <= {nights, gala} | {
        price_tier(REQ, "cao_cap", HN, HALONG, None, EST, category_tiers={c: "can_bang"}).total
        for c in by_cat(p)}
    assert any(c["label"] == "Bớt 1 đêm" for c in full) or any(c["label"] == "Bỏ gala dinner" for c in full)


def test_all_over_sets_min_budget():
    req = replace(REQ, budget=3_000_000)
    pk = run(req)
    assert pk["tiet_kiem"].explanation.min_budget == pk["tiet_kiem"].total
    assert pk["cao_cap"].explanation.min_budget is None


def test_within_budget_has_no_explanation():
    req = replace(REQ, budget=pricing_total())
    pk = run(req)
    assert pk["tiet_kiem"].explanation is None
    assert pk["cao_cap"].explanation is not None and pk["cao_cap"].explanation.min_budget is None


def pricing_total():
    return price_tier(REQ, "tiet_kiem", HN, HALONG, None, EST).total
