"""Router /api/trips: tạo chuyến, chọn gói và đọc lại chuyến đã lưu."""
from fastapi import APIRouter, HTTPException

from src.api.schemas import ApproveInput, TripInput
from src.api.services import trip_service

router = APIRouter(prefix="/api/trips", tags=["Trips"])


@router.post("")
def create_trip(body: TripInput) -> dict:
    return trip_service.create_trip(body)


@router.post("/{trip_id}/approve")
def approve_trip(trip_id: str, body: ApproveInput) -> dict:
    try:
        view = trip_service.approve_trip(trip_id, body)
    except trip_service.InvalidTripSelection as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if view is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy chuyến đi")
    return view


@router.get("/{trip_id}")
def get_trip(trip_id: str) -> dict:
    view = trip_service.get_trip(trip_id)
    if view is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy chuyến đi")
    return view
