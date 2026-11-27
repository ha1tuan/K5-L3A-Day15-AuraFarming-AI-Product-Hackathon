from datetime import date

import pytest

from src.core.planning.request import build_request, parse_vnd, understood_text, ask_back_text, default_start

TODAY = date(2026, 11, 27)
FULL = {"headcount": 60, "days": 3, "origin": "Hà Nội", "purpose": "gan_ket",
        "budget_text": "150 triệu", "destination": "Hạ Long", "country": "VN"}


def test_full_c_request():
    req, missing, refusal = build_request(FULL, TODAY)
    assert missing == [] and refusal is None
    assert (req.entry, req.budget, req.nights, req.start_date) == ("C", 150_000_000, 2, date(2026, 12, 4))
    assert req.date_assumed is True


def test_missing_fields():
    _, missing, _ = build_request({"days": 3, "budget_text": "150 triệu"}, TODAY)
    assert missing == ["headcount", "origin", "purpose"]


def test_neither_budget_nor_destination():
    _, missing, _ = build_request({k: v for k, v in FULL.items() if k not in ("budget_text", "destination")}, TODAY)
    assert missing == ["budget_or_destination"]


def test_budget_per_person():
    req, _, _ = build_request({**FULL, "headcount": 80, "budget_text": "mỗi người 3 triệu"}, TODAY)
    assert req.budget == 240_000_000 and req.budget_per_person_input
    assert understood_text(req) == "Ngân sách đã hiểu: 240.000.000đ cho 80 người"


@pytest.mark.parametrize("n", [4, 501, 800])
def test_headcount_out_of_range_refused(n):
    _, _, refusal = build_request({**FULL, "headcount": n}, TODAY)
    assert "500" in refusal


def test_foreign_refused():
    _, _, refusal = build_request({**FULL, "destination": "Bangkok", "country": "Thái Lan"}, TODAY)
    assert "trong nước" in refusal


def test_exclude_gala():
    req, _, _ = build_request({**FULL, "exclude": ["gala"]}, TODAY)
    assert req.exclude == {"gala"}


def test_missing_country_is_domestic_and_explicit_date_kept():
    raw = {k: v for k, v in FULL.items() if k != "country"}
    req, _, refusal = build_request({**raw, "start_date": "2026-12-20"}, TODAY)
    assert refusal is None and req.start_date == date(2026, 12, 20) and req.date_assumed is False


def test_entries_a_and_b():
    a, _, _ = build_request({**FULL, "destination": None}, TODAY)
    b, _, _ = build_request({**FULL, "budget_text": None}, TODAY)
    assert (a.entry, b.entry) == ("A", "B")


@pytest.mark.parametrize("s,v", [("150tr", 150_000_000), ("1,2 tỷ", 1_200_000_000), ("150.000.000", 150_000_000),
                                 ("3 triệu", 3_000_000), ("3 triệu/người", 3_000_000), (150_000_000, 150_000_000),
                                 (None, None), ("", None), ("không rõ", None)])
def test_parse_vnd(s, v):
    assert parse_vnd(s) == v


def test_default_start_is_next_friday():
    assert default_start(date(2026, 11, 27)) == date(2026, 12, 4)  # hôm nay là thứ Sáu
    assert default_start(date(2026, 11, 28)) == date(2026, 12, 4)
    assert default_start(date(2026, 11, 23)) == date(2026, 11, 27)


def test_ask_back_text_lists_fields():
    t = ask_back_text(["headcount", "budget_or_destination"])
    assert "số người" in t and "ngân sách" in t
