"""API web trên đường dữ liệu: 3 cách vào, duyệt, soát báo giá (không gọi model, không mạng)."""
import json

import pytest
from fastapi.testclient import TestClient

from src.main import app

BASE = {"headcount": 50, "days": 2, "start_date": None, "origin": "Đà Nẵng", "purpose": "gan_ket",
        "budget": 200000000, "budget_per_person": False, "destination": ""}


@pytest.fixture
def c(monkeypatch):
    monkeypatch.setenv("TRAVEL_TODAY", "2026-11-27")
    return TestClient(app)


def test_cach_a_goi_y_roi_duyet(c):
    v = c.post("/api/trips", json=BASE).json()
    assert v["status"] == "choose_destination" and 2 <= len(v["destinations"]) <= 3
    assert v["request"]["entry"] == "A" and all(len(d["packages"]) == 3 for d in v["destinations"])
    d = v["destinations"][0]
    ok = c.post("/api/trips/%s/approve" % v["trip_id"], json={"destination": d["name"], "package": "can_bang",
                                                              "remove_items": ["gala"]}).json()
    assert ok["status"] == "ok" and len(ok["plans"]) == 1 and ok["plans"][0]["days"]
    assert not any("Gala" in li["description"] for li in [x for p in ok["packages"] for x in p["line_items"]])


def test_cach_b_va_c(c):
    b = c.post("/api/trips", json=dict(BASE, budget=None, destination="Hội An")).json()
    assert b["status"] == "choose_package" and len(b["packages"]) == 3 and b["request"]["entry"] == "B"
    cc = c.post("/api/trips", json=dict(BASE, origin="Hà Nội", destination="Hạ Long", budget=150000000)).json()
    assert cc["status"] == "ok" and len(cc["plans"]) == 3 and cc["request"]["entry"] == "C"
    for p in cc["packages"]:
        assert sum(li["amount"] for li in p["line_items"]) == p["total"]
        if p["over_budget"]:
            assert p["explanation"]["over_amount"] == p["over_budget"] and p["explanation"]["cuts"]
    assert cc["plans"][0]["videos"] and cc["plans"][0]["info"]
    assert c.get("/api/trips/%s" % cc["trip_id"]).status_code == 200


def test_ngan_sach_moi_nguoi_va_hoi_lai(c):
    v = c.post("/api/trips", json=dict(BASE, budget=3000000, budget_per_person=True)).json()
    assert v["request"]["budget"] == 150000000
    ask = c.post("/api/trips", json=dict(BASE, headcount=None, purpose=None)).json()
    assert ask["status"] == "ask_back" and set(ask["missing_fields"]) == {"headcount", "purpose"}
    assert c.post("/api/trips", json=dict(BASE, headcount=800)).json()["status"] == "refused"


def test_soat_bao_gia_api(c):
    q = [x for x in json.load(open("data/bao_gia_mau.json", encoding="utf-8"))["bao_gia"] if x["url"].endswith("bcr.html")][0]
    t = ("Công ty 45 người, ngân sách 45 triệu.\nGiá: 950.000 đ/khách\nGiá tour bao gồm:\n" + "\n".join("- " + i for i in q["bao_gom"])
         + "\nGiá tour không bao gồm:\n" + "\n".join("- " + i for i in q["khong_bao_gom"]))
    r = c.post("/api/quote-audit", json={"text": t}).json()
    assert r["status"] == "ok" and r["tong"] == sum(d["thanh_tien"] for d in r["dong"]) and r["vuot"] == r["tong"] - 45000000
    assert r["chung_tu"] and r["cau_hoi"] and r["to_trinh"]
    assert c.post("/api/quote-audit", json={"text": "xin chào"}).json()["status"] == "ask_back"


def test_ngay_di_phai_tu_hom_nay(c):
    past = c.post("/api/trips", json=dict(BASE, start_date="2026-11-04")).json()          # TRAVEL_TODAY=2026-11-27
    assert past["status"] == "ask_back" and past["missing_fields"] == ["start_date"] and "đã qua" in past["message"]
    far = c.post("/api/trips", json=dict(BASE, start_date="2028-01-01")).json()
    assert far["status"] == "ask_back" and "1 năm" in far["message"]
    ok = c.post("/api/trips", json=dict(BASE, destination="Hội An", start_date="2026-12-04")).json()
    assert ok["request"]["start_date"] == "2026-12-04"
    d = c.post("/api/trips", json=dict(BASE, destination="Hội An")).json()
    assert d["request"]["start_date"] > "2026-11-27"                                         # mặc định: thứ Sáu sau hôm nay


def test_mua_dep_theo_thang_di(c):
    v = c.post("/api/trips", json=dict(BASE, origin="Hà Nội", destination="Hạ Long", budget=200000000, start_date="2027-06-04")).json()
    assert v["plans"][0]["extra"]["season"] == {"months": "4–10", "in_season": True, "month_now": 6}


def test_tuy_chinh_tinh_lai(c):
    v = c.post("/api/trips", json=dict(BASE, origin="Hà Nội", destination="Hạ Long", budget=150000000, days=3)).json()
    opts = v["customize"]["options"]
    assert "Gala dinner" in opts and v["map"]["dest"]["name"] == "Hạ Long"
    tong = {p["tier"]: p["total"] for p in v["packages"]}
    r = c.post("/api/trips/%s/recalc" % v["trip_id"], json={"removed": ["Gala dinner"], "headcount": 40, "days": 2}).json()
    assert r["request"]["headcount"] == 40 and r["request"]["days"] == 2 and r["customize"]["removed"] == ["Gala dinner"]
    assert all(r2["total"] < tong[r2["tier"]] for r2 in r["packages"])
    assert not any("Gala" in li["description"] for p in r["packages"] for li in p["line_items"])
    back = c.post("/api/trips/%s/recalc" % r["trip_id"], json={"removed": []}).json()
    assert any("Gala" in li["description"] for p in back["packages"] for li in p["line_items"])


def test_uoc_tinh_doi_chieu_xuat_excel(c):
    e = c.get("/api/estimate", params={"origin": "Hà Nội", "destination": "Hạ Long", "headcount": 40, "days": 3}).json()
    assert e["status"] == "ok" and [t["tier"] for t in e["tiers"]] == ["tiet_kiem", "can_bang", "cao_cap"]
    v = c.post("/api/trips", json=dict(BASE, destination="Hội An", budget=100000000)).json()
    q = [x for x in json.load(open("data/bao_gia_mau.json", encoding="utf-8"))["bao_gia"] if x["url"].endswith("bcr.html")][0]
    t = ("Giá: 950.000 đ/khách\nGiá tour bao gồm:\n" + "\n".join("- " + i for i in q["bao_gom"])
         + "\nGiá tour không bao gồm:\n" + "\n".join("- " + i for i in q["khong_bao_gom"]))
    r = c.post("/api/trips/%s/quote" % v["trip_id"], json={"text": t, "tier": "can_bang"}).json()
    assert r["status"] == "ok" and r["so_nguoi"] == 50 and r["doi_chieu"]["ke_hoach"] > 0
    x = c.get("/api/trips/%s/export.xlsx" % v["trip_id"])
    assert x.status_code == 200 and x.content[:2] == b"PK"
