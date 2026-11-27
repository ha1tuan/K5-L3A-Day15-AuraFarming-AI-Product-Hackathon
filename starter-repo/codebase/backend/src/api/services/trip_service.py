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


def _save(view: dict) -> dict:
    _store[view["trip_id"]] = view
    while len(_reqs) > MAX_TRIPS:
        _reqs.pop(next(iter(_reqs)))
    while len(_store) > MAX_TRIPS:
        _store.popitem(last=False)
    return view


FIELD_VI = {"headcount": "số người đi", "days": "số ngày", "origin": "nơi xuất phát", "purpose": "mục đích",
            "budget_or_destination": "kinh phí hoặc địa điểm"}


def create_trip(inp: TripInput) -> dict:
    """Ưu tiên đường dữ liệu (data/*.json, đủ 3 cách vào); nơi ngoài dữ liệu → graph cũ (chỉ cách C)."""
    req = du_lieu_service.build_req(inp)
    miss = du_lieu_service.missing(req)
    if miss:
        return _save({"trip_id": uuid.uuid4().hex, "status": "ask_back", "missing_fields": miss,
                      "message": "Cần thêm: " + ", ".join(FIELD_VI[m] for m in miss) + "."})
    if not 5 <= req["so_nguoi"] <= 500 or not 1 <= req["so_ngay"] <= 7:
        return _save({"trip_id": uuid.uuid4().hex, "status": "refused",
                      "message": "Hệ thống hỗ trợ đoàn 5–500 người, chuyến 1–7 ngày. Đoàn lớn hơn: chia đợt và lập kế hoạch từng đợt."})
    if du_lieu_service.handles(req):
        view = du_lieu_service.create(req)
        view["trip_id"] = uuid.uuid4().hex
        _reqs[view["trip_id"]] = req
        return _save(view)
    return _create_graph(inp)


def approve_trip(trip_id: str, body) -> Optional[dict]:
    req = _reqs.get(trip_id)
    if req is None:
        return None
    view = du_lieu_service.approve(req, body)
    view["trip_id"] = uuid.uuid4().hex
    _reqs[view["trip_id"]] = req
    return _save(view)


def _create_graph(inp: TripInput) -> dict:
    state = _form_graph().invoke({"raw": to_raw(inp), "today": os.environ.get("TRAVEL_TODAY") or ""})
    view = dict(state["view"])
    req = state.get("request")
    if req is not None and req.entry != "C":
        view = {"status": "error", "message": NOT_SUPPORTED}
    view["trip_id"] = uuid.uuid4().hex
    return _save(view)


def get_trip(trip_id: str) -> Optional[dict]:
    return _store.get(trip_id)
