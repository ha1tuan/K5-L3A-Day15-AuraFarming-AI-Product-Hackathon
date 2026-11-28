"""TripService: TripInput của web -> graph cách C (đường "form") -> TripView; lưu trong bộ nhớ tiến trình."""
import os
import uuid
from collections import OrderedDict
from typing import Optional

from src.api.schemas import TripInput
from src.core.orchestration.graphs.graph import build_trip_graph
from src.api.services import du_lieu_service

MAX_TRIPS = 200
NOT_SUPPORTED = "Bản hiện tại cần cả kinh phí và địa điểm."

_store: "OrderedDict[str, dict]" = OrderedDict()
_reqs: dict = {}
_graph = None


def _form_graph():
    global _graph
    if _graph is None:
        _graph = build_trip_graph(entry="form")
    return _graph


def to_raw(inp: TripInput) -> dict:
    """TripInput -> dict thô như model bóc ra (build_request đọc)."""
    budget_text = None
    if inp.budget:
        budget_text = f"{inp.budget} mỗi người" if inp.budget_per_person else str(inp.budget)
    return {"headcount": inp.headcount, "days": inp.days, "start_date": inp.start_date, "origin": inp.origin,
            "purpose": inp.purpose, "budget_text": budget_text, "destination": inp.destination, "country": "VN"}


# Lưu bền (SQLite) để link ?trip=<id> gửi sếp vẫn mở được sau khi máy chủ khởi động lại. TRIPS_DB đổi chỗ lưu.
_DB = os.environ.get("TRIPS_DB") or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))), "var", "trips.sqlite")


def _db():
    import sqlite3
    os.makedirs(os.path.dirname(_DB), exist_ok=True)
    c = sqlite3.connect(_DB, timeout=10)
    c.execute("create table if not exists trips (id text primary key, view text, req text, ts real)")
    return c


def _persist(view: dict, req: Optional[dict]) -> None:
    import json
    import time
    try:
        with _db() as c:
            c.execute("insert or replace into trips values (?, ?, ?, ?)",
                      (view["trip_id"], json.dumps(view, ensure_ascii=False), json.dumps(req, ensure_ascii=False) if req else None, time.time()))
    except Exception:  # noqa: BLE001 — không lưu được thì vẫn trả kết quả (chỉ mất link chia sẻ)
        pass


def _load(trip_id: str):
    import json
    try:
        with _db() as c:
            row = c.execute("select view, req from trips where id = ?", (trip_id,)).fetchone()
    except Exception:  # noqa: BLE001
        return None, None
    if not row:
        return None, None
    return json.loads(row[0]), (json.loads(row[1]) if row[1] else None)


def get_req(trip_id: str) -> Optional[dict]:
    if trip_id in _reqs:
        return _reqs[trip_id]
    return _load(trip_id)[1]


def _save(view: dict, req: Optional[dict] = None) -> dict:
    _store[view["trip_id"]] = view
    if req is not None:
        _reqs[view["trip_id"]] = req
    _persist(view, req)
    while len(_reqs) > MAX_TRIPS:
        _reqs.pop(next(iter(_reqs)))
    while len(_store) > MAX_TRIPS:
        _store.popitem(last=False)
    return view


FIELD_VI = {"headcount": "số người đi", "days": "số ngày", "start_date": "ngày đi", "origin": "nơi xuất phát", "purpose": "mục đích",
            "budget_or_destination": "kinh phí hoặc địa điểm"}


def create_trip(inp: TripInput) -> dict:
    """Ưu tiên đường dữ liệu (data/*.json, đủ 3 cách vào); nơi ngoài dữ liệu → graph cũ (chỉ cách C)."""
    req = du_lieu_service.build_req(inp)
    miss = du_lieu_service.missing(req)
    if miss:
        return _save({"trip_id": uuid.uuid4().hex, "status": "ask_back", "missing_fields": miss,
                      "message": "Cần thêm: " + ", ".join(FIELD_VI[m] for m in miss) + "."})
    bad_date = du_lieu_service.check_start(req)
    if bad_date:
        return _save({"trip_id": uuid.uuid4().hex, "status": "ask_back", "missing_fields": ["start_date"], "message": bad_date})
    if not 5 <= req["so_nguoi"] <= 500 or not 1 <= req["so_ngay"] <= 7:
        return _save({"trip_id": uuid.uuid4().hex, "status": "refused",
                      "message": "Hệ thống hỗ trợ đoàn 5–500 người, chuyến 1–7 ngày. Đoàn lớn hơn: chia đợt và lập kế hoạch từng đợt."})
    if du_lieu_service.handles(req):
        view = du_lieu_service.create(req)
        view["trip_id"] = uuid.uuid4().hex
        return _save(view, req)
    return _create_graph(inp)


def approve_trip(trip_id: str, body) -> Optional[dict]:
    req = get_req(trip_id)
    if req is None:
        return None
    view, req2 = du_lieu_service.approve(req, body)
    view["trip_id"] = uuid.uuid4().hex
    return _save(view, req2)


def recalc_trip(trip_id: str, body) -> Optional[dict]:
    req = get_req(trip_id)
    if req is None or not req.get("dia_diem"):
        return None
    view, req2 = du_lieu_service.recalc(req, body)
    view["trip_id"] = uuid.uuid4().hex
    return _save(view, req2)


def quote_for_trip(trip_id: str, tier: str, text: str) -> Optional[dict]:
    req = get_req(trip_id)
    if req is None or not req.get("dia_diem"):
        return None
    return du_lieu_service.quote_compare(req, tier, text)


def _create_graph(inp: TripInput) -> dict:
    state = _form_graph().invoke({"raw": to_raw(inp), "today": os.environ.get("TRAVEL_TODAY") or ""})
    view = dict(state["view"])
    req = state.get("request")
    if req is not None and req.entry != "C":
        view = {"status": "error", "message": NOT_SUPPORTED}
    view["trip_id"] = uuid.uuid4().hex
    return _save(view)


def get_trip(trip_id: str) -> Optional[dict]:
    return _store.get(trip_id) or _load(trip_id)[0]
