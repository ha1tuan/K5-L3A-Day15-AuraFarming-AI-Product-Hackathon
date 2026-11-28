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


def test_more_destinations_excludes_seen_and_can_reset(c):
    """Cách A: "Gợi ý nơi khác" trả nơi chưa xem; exclude rỗng = xem lại từ đầu; trip lạ → 404."""
    v = c.post("/api/trips", json=BASE).json()
    assert v["status"] == "choose_destination"
    first = [d["name"] for d in v["destinations"]]
    assert v["seen"] == first
    if v["has_more"]:
        v2 = c.post(f"/api/trips/{v['trip_id']}/more-destinations", json={"exclude": v["seen"]}).json()
        second = [d["name"] for d in v2["destinations"]]
        assert second and not set(second) & set(first)
        assert v2["seen"] == first + second
        assert not any(d["recommended"] for d in v2["destinations"])
        ok = c.post(f"/api/trips/{v2['trip_id']}/approve", json={"destination": second[0], "package": "tiet_kiem"})
        assert ok.status_code == 200 and ok.json()["status"] == "ok"
    v3 = c.post(f"/api/trips/{v['trip_id']}/more-destinations", json={"exclude": []}).json()
    assert [d["name"] for d in v3["destinations"]] == first
    assert c.post("/api/trips/khong-co/more-destinations", json={"exclude": []}).status_code == 404


def test_lich_co_chi_tiet_thuc_don_chuong_trinh_va_nguon(c):
    """Bữa ăn có thực đơn + giá/suất đúng giá đã tính; team building / gala có chương trình từng bước; có link nguồn / tra cứu."""
    v = c.post("/api/trips", json={**BASE, "origin": "Đà Nẵng", "destination": "Hội An", "days": 2}).json()
    p = next(x for x in v["plans"] if x["tier"] == "can_bang")
    slots = [s for d in p["days"] for s in d["slots"]]
    an = [s for s in slots if s["kind"] == "meal" and ("trưa" in s["title"] or "tối" in s["title"])]
    gia_bua = next(li["unit_price"] for pk in v["packages"] if pk["tier"] == "can_bang" for li in pk["line_items"] if li["unit"] == "suất")
    assert an and all(s["menu"]["dishes"] and s["menu"]["price_per_pax"] == gia_bua and s["sources"] for s in an)
    tb = [s for s in slots if "gắn kết" in s["title"] or s["kind"] == "gala"]
    assert tb and all(s["program"]["steps"] and s["program"]["steps"][0]["start"] == s["start"] for s in tb)
    assert all(x["url"].startswith("https://") for s in slots for x in s.get("sources", []))


def test_dia_diem_sai_bao_khong_ton_tai(c, monkeypatch):
    """Địa điểm gõ sai → hỏi lại kèm gợi ý; không có trên bản đồ VN → báo không tồn tại; nước ngoài → từ chối;
    nơi có thật ngoài dữ liệu vẫn cho qua."""
    from src.api.services import du_lieu_service as ds
    co_that = {"Quy Nhơn": True}
    monkeypatch.setattr(ds, "_co_o_viet_nam", lambda ten: co_that.get(ten, False))
    post = lambda **kw: c.post("/api/trips", json={**BASE, "origin": "Hà Nội", **kw}).json()
    v = post(destination="Đà Lạtt")
    assert v["status"] == "ask_back" and v["missing_fields"] == ["destination"] and "Đà Lạt" in v["suggestions"]
    v = post(destination="abcxyz")
    assert v["status"] == "ask_back" and v["suggestions"] == [] and "không tồn tại" in v["message"]
    assert post(destination="Paris")["status"] == "refused"
    v = post(origin="Xyzabc", destination="Hạ Long")
    assert v["status"] == "ask_back" and v["missing_fields"] == ["origin"]
    assert post(destination="Hạ Long")["status"] == "ok"
    assert ds.check_places({"noi_xuat_phat": "Hà Nội", "dia_diem": "Quy Nhơn"}) is None


def test_ban_do_chi_nhan_dia_danh(monkeypatch):
    """Bản đồ khớp gần đúng ("Mặt Trăng" → khách sạn Trăng Mật): chỉ nhận địa danh mang đúng tên, hoặc bến xe / bến phà đúng tên."""
    from src.api.services import du_lieu_service as ds
    from src.core.sources import cache
    tra = {"Mặt Trăng": [{"category": "tourism", "type": "hotel", "name": "Khách Sạn Trăng Mật"},
                         {"category": "landuse", "type": "cemetery", "name": "Nghĩa trang Lệ Mật"}],
           "Quy Nhơn": [{"category": "place", "type": "city", "name": "Quy Nhơn"}],
           "Cát Bà": [{"category": "amenity", "type": "bus_station", "name": "Cát Bà"}],
           "Sao Hỏa": [{"category": "highway", "type": "bus_stop", "name": "Nhà văn hóa thôn Sảo Thượng"}]}
    monkeypatch.setattr(cache, "cached_call", lambda ns, params, fetch: tra[params["q"]])
    assert ds._co_o_viet_nam("Mặt Trăng") is False and ds._co_o_viet_nam("Sao Hỏa") is False
    assert ds._co_o_viet_nam("Quy Nhơn") is True and ds._co_o_viet_nam("Cát Bà") is True

    def mat_mang(ns, params, fetch):
        raise cache.CacheMiss(ns, params) if hasattr(cache, "CacheMiss") else RuntimeError("offline")
    monkeypatch.setattr(cache, "cached_call", mat_mang)
    assert ds._co_o_viet_nam("Quy Nhơn") is None
