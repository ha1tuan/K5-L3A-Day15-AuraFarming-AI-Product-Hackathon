"""TripService: lập dự trù và lịch trình cho web, lưu chuyến trong bộ nhớ tiến trình."""
import json
import os
import uuid
from collections import OrderedDict
from dataclasses import replace
from pathlib import Path
from typing import Optional

from src.api.schemas import ApproveInput, TripInput
from src.core.orchestration.graphs.graph import build_trip_graph
from src.core.planning.estimates import load_estimates
from src.core.planning.pricing import price_packages
from src.core.planning.render import to_view
from src.core.planning.types import GeoPoint, TripRequest
from tools import dinh_vi

MAX_TRIPS = 200

_store: OrderedDict[str, tuple[dict, dict, dict]] = OrderedDict()
_graph = None


class InvalidTripSelection(ValueError):
    """Địa điểm hoặc gói nằm ngoài lựa chọn đã trả cho chuyến."""


def _form_graph():
    global _graph
    if _graph is None:
        _graph = build_trip_graph(entry="form")
    return _graph


def _load_destinations() -> list[dict]:
    path = Path(__file__).resolve().parents[5] / "data" / "diem_den.json"
    return json.loads(path.read_text(encoding="utf-8"))["diem_den"]


def _rank_destinations(req: TripRequest):
    origin = dinh_vi(req.origin, domestic=True)
    origin_pt = GeoPoint(**origin) if origin else None
    estimates = load_estimates()
    ranked = []

    for item in _load_destinations():
        name = item["ten"]
        dest_pt = GeoPoint(lat=item["lat"], lon=item["lon"])
        candidate = replace(req, destination=name)
        packages = price_packages(candidate, origin_pt, dest_pt, {}, estimates)
        ranked.append((name, packages))

    def sort_key(option):
        name, packages = option
        cheapest = min(pkg.total for pkg in packages)
        return cheapest > req.budget, cheapest, name

    return sorted(ranked, key=sort_key)[:3]


def to_raw(inp: TripInput) -> dict:
    """TripInput -> dict thô như model bóc ra (build_request đọc)."""
    budget_text = None
    if inp.budget:
        budget_text = f"{inp.budget} mỗi người" if inp.budget_per_person else str(inp.budget)
    return {"headcount": inp.headcount, "days": inp.days, "start_date": inp.start_date, "origin": inp.origin,
            "purpose": inp.purpose, "budget_text": budget_text, "destination": inp.destination, "country": "VN"}


def _save(view: dict, raw: dict, choices: dict) -> dict:
    _store[view["trip_id"]] = (view, raw, choices)
    while len(_store) > MAX_TRIPS:
        _store.popitem(last=False)
    return view


def create_trip(inp: TripInput) -> dict:
    raw = to_raw(inp)
    state = _form_graph().invoke({"raw": raw, "today": os.environ.get("TRAVEL_TODAY") or ""})
    view = dict(state["view"])
    req = state.get("request")
    if req is not None and req.entry == "A":
        view = {
            "status": "choose_destination",
            "message": "Gợi ý địa điểm theo kinh phí dự trù.",
            "request": to_view("", req, [], [])["request"],
            "destinations": [],
        }
        for index, (name, packages) in enumerate(_rank_destinations(req)):
            cheapest = min(packages, key=lambda pkg: pkg.total)
            view["destinations"].append({
                "name": name,
                "transport": cheapest.leg.mode,
                "travel_time": f"Khoảng {cheapest.leg.hours:g} giờ mỗi chiều",
                "why": "Có gói trong ngân sách." if cheapest.total <= req.budget
                       else "Gói thấp nhất vẫn vượt ngân sách.",
                "refs": {"articles": 0, "videos": 0},
                "packages": to_view("", req, packages, [])["packages"],
                "recommended": index == 0 and cheapest.total <= req.budget,
            })
    elif req is not None and req.entry == "B" and view["status"] == "ok":
        view["status"] = "choose_package"
        view["message"] = "Dự trù kinh phí cho ba gói."
        view.pop("plans", None)
    view["trip_id"] = uuid.uuid4().hex
    return _save(view, raw, view)


def get_trip(trip_id: str) -> Optional[dict]:
    stored = _store.get(trip_id)
    return stored[0] if stored is not None else None


def approve_trip(trip_id: str, inp: ApproveInput) -> Optional[dict]:
    stored = _store.get(trip_id)
    if stored is None:
        return None
    _, raw, choices = stored
    status = choices["status"]
    destination = inp.destination or choices.get("destination")
    if status == "choose_destination":
        packages = next((item["packages"] for item in choices["destinations"]
                         if item["name"] == destination), [])
    elif status == "choose_package" and destination == choices["destination"]:
        packages = choices["packages"]
    else:
        packages = []
    if not any(pkg["tier"] == inp.package for pkg in packages):
        raise InvalidTripSelection("Hãy chọn địa điểm và gói đã được đề xuất cho chuyến này.")

    selected = {**raw, "destination": destination, "start_date": choices["request"]["start_date"],
                "exclude": inp.remove_items}
    if inp.headcount is not None:
        selected["headcount"] = inp.headcount

    state = _form_graph().invoke({"raw": selected, "today": os.environ.get("TRAVEL_TODAY") or ""})
    view = dict(state["view"], trip_id=trip_id)
    if view["status"] != "ok":
        return view
    view["request"]["entry"] = choices["request"]["entry"]
    view["plans"] = [plan for plan in view["plans"] if plan["tier"] == inp.package]
    return _save(view, raw, choices)
