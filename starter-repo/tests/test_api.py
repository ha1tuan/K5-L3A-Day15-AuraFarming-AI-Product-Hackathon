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


def test_post_entry_a_suggests_destinations_and_approves_a_package(world, monkeypatch):
    # Nhánh vinh: Hà Nội → Hạ Long chạy đường dữ liệu; test này giữ cho đường graph (nơi ngoài dữ liệu, PR #13).
    monkeypatch.setattr(trip_service.du_lieu_service, "handles", lambda req: False)
    monkeypatch.setattr(trip_service, "dinh_vi", lambda *args, **kwargs: None)
    r = client.post("/api/trips", json={**BODY, "destination": ""})
    assert r.status_code == 200
    view = r.json()
    assert view["status"] == "choose_destination" and view["request"]["entry"] == "A"
    options = view["destinations"]
    assert len(options) == 3 and all(len(item["packages"]) == 3 for item in options)
    totals = [min(pkg["total"] for pkg in item["packages"]) for item in options]
    assert totals == sorted(totals)
    url = f"/api/trips/{view['trip_id']}/approve"
    assert client.post(url, json={"destination": "Ngoài danh sách", "package": "tiet_kiem"}).status_code == 422

    approved = client.post(url, json={"destination": options[0]["name"], "package": "tiet_kiem"})
    assert approved.status_code == 200
    plan = approved.json()
    assert plan["status"] == "ok" and plan["request"]["entry"] == "A"
    assert plan["destination"] == options[0]["name"]
    assert [item["tier"] for item in plan["plans"]] == ["tiet_kiem"]
    assert client.get(f"/api/trips/{view['trip_id']}").json() == plan


def test_post_entry_b_estimates_without_budget_and_approves_a_package(world, monkeypatch):
    # Nhánh vinh: Hà Nội → Hạ Long chạy đường dữ liệu; test này giữ cho đường graph (nơi ngoài dữ liệu, PR #13).
    monkeypatch.setattr(trip_service.du_lieu_service, "handles", lambda req: False)
    view = client.post("/api/trips", json={**BODY, "budget": None}).json()
    assert view["status"] == "choose_package" and view["request"]["entry"] == "B"
    assert view["request"]["budget"] is None and len(view["packages"]) == 3
    assert all(pkg["over_budget"] is None for pkg in view["packages"])

    approved = client.post(f"/api/trips/{view['trip_id']}/approve", json={
        "package": "can_bang", "headcount": 45, "remove_items": ["gala"],
    })
    assert approved.status_code == 200
    plan = approved.json()
    assert plan["status"] == "ok" and plan["request"]["headcount"] == 45
    assert plan["request"]["budget"] is None
    assert [item["tier"] for item in plan["plans"]] == ["can_bang"]
    assert all(line["category"] != "Gala" for line in plan["packages"][1]["line_items"])


def test_post_out_of_range_is_refused_not_500(world):
    r = client.post("/api/trips", json={**BODY, "headcount": 800})
    assert r.status_code == 200 and r.json()["status"] == "refused" and "500" in r.json()["message"]


def test_get_trip_roundtrip(world):
    v = client.post("/api/trips", json=BODY).json()
    got = client.get("/api/trips/" + v["trip_id"])
    assert got.status_code == 200 and got.json() == v
    assert client.get("/api/trips/khong-co").status_code == 404


def test_store_evicts_oldest(world, monkeypatch):
    # 28/11: bộ nhớ vẫn giới hạn MAX_TRIPS, nhưng chuyến bị đẩy ra vẫn đọc lại được từ SQLite (link chia sẻ bền)
    monkeypatch.setattr(trip_service, "MAX_TRIPS", 2)
    ids = [client.post("/api/trips", json={**BODY, "origin": ""}).json()["trip_id"] for _ in range(3)]
    assert ids[0] not in trip_service._store and len(trip_service._store) <= 2
    assert client.get("/api/trips/" + ids[0]).status_code == 200
    assert client.get("/api/trips/" + ids[2]).status_code == 200


def test_cors_allows_vite_origin():
    r = client.options("/api/trips", headers={"Origin": "http://localhost:5173",
                                              "Access-Control-Request-Method": "POST",
                                              "Access-Control-Request-Headers": "content-type"})
    assert r.headers["access-control-allow-origin"] == "http://localhost:5173"
