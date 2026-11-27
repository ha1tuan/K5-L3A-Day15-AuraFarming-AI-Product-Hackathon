"""TripService: TripInput của web -> graph cách C (đường "form") -> TripView; lưu trong bộ nhớ tiến trình."""
import os
import uuid
from collections import OrderedDict
from typing import Optional

from src.api.schemas import TripInput
from src.core.orchestration.graphs.graph import build_trip_graph

MAX_TRIPS = 200
NOT_SUPPORTED = "Bản hiện tại cần cả kinh phí và địa điểm."

_store: "OrderedDict[str, dict]" = OrderedDict()
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
    while len(_store) > MAX_TRIPS:
        _store.popitem(last=False)
    return view


def create_trip(inp: TripInput) -> dict:
    state = _form_graph().invoke({"raw": to_raw(inp), "today": os.environ.get("TRAVEL_TODAY") or ""})
    view = dict(state["view"])
    req = state.get("request")
    if req is not None and req.entry != "C":
        view = {"status": "error", "message": NOT_SUPPORTED}
    view["trip_id"] = uuid.uuid4().hex
    return _save(view)


def get_trip(trip_id: str) -> Optional[dict]:
    return _store.get(trip_id)
