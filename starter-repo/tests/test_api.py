import pytest
from fastapi.testclient import TestClient

from src.api.services import trip_service
from src.main import app
from test_graph_c import world  # noqa: F401  (model / tìm kiếm / định vị giả)

BODY = {"headcount": 60, "days": 3, "start_date": None, "origin": "Hà Nội", "purpose": "gan_ket",
        "budget": 150_000_000, "budget_per_person": False, "destination": "Hạ Long"}
client = TestClient(app)


def test_post_c_returns_ok_with_three_plans(world):
    r = client.post("/api/trips", json=BODY)
    assert r.status_code == 200
    v = r.json()
    assert v["status"] == "ok" and v["trip_id"] and v["destination"] == "Hạ Long"
    assert [p["tier"] for p in v["plans"]] == ["tiet_kiem", "can_bang", "cao_cap"]
    assert len(v["packages"]) == 3 and v["request"]["budget"] == 150_000_000
    assert world["parse"] == []  # đường form không gọi model bóc yêu cầu


def test_post_per_person_budget_multiplies(world):
    v = client.post("/api/trips", json={**BODY, "budget": 2_500_000, "budget_per_person": True}).json()
    assert v["request"]["budget"] == 150_000_000


def test_post_missing_returns_ask_back(world):
    v = client.post("/api/trips", json={**BODY, "origin": "", "purpose": None}).json()
    assert v["status"] == "ask_back" and v["missing_fields"] == ["origin", "purpose"] and v["trip_id"]


def test_post_entry_a_suggests_destinations(world):
    # 27/11 tối: cách A chạy trên đường dữ liệu (du_lieu_service) — trước đó trả "Bản hiện tại cần cả kinh phí và địa điểm."
    r = client.post("/api/trips", json={**BODY, "destination": ""})
    assert r.status_code == 200
    assert r.json()["status"] == "choose_destination" and r.json()["destinations"]


def test_post_out_of_range_is_refused_not_500(world):
    r = client.post("/api/trips", json={**BODY, "headcount": 800})
    assert r.status_code == 200 and r.json()["status"] == "refused" and "500" in r.json()["message"]


def test_get_trip_roundtrip(world):
    v = client.post("/api/trips", json=BODY).json()
    got = client.get("/api/trips/" + v["trip_id"])
    assert got.status_code == 200 and got.json() == v
    assert client.get("/api/trips/khong-co").status_code == 404


def test_store_evicts_oldest(world, monkeypatch):
    monkeypatch.setattr(trip_service, "MAX_TRIPS", 2)
    ids = [client.post("/api/trips", json={**BODY, "origin": ""}).json()["trip_id"] for _ in range(3)]
    assert client.get("/api/trips/" + ids[0]).status_code == 404
    assert client.get("/api/trips/" + ids[2]).status_code == 200


def test_cors_allows_vite_origin():
    r = client.options("/api/trips", headers={"Origin": "http://localhost:5173",
                                              "Access-Control-Request-Method": "POST",
                                              "Access-Control-Request-Headers": "content-type"})
    assert r.headers["access-control-allow-origin"] == "http://localhost:5173"
