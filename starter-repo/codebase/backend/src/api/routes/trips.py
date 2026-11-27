"""Router /api/trips: POST tạo chuyến (cách C), GET đọc lại chuyến đã lưu."""
from fastapi import APIRouter, HTTPException

from src.api.schemas import TripInput
from src.api.services import trip_service

router = APIRouter(prefix="/api/trips", tags=["Trips"])


@router.post("")
def create_trip(body: TripInput) -> dict:
    return trip_service.create_trip(body)


@router.get("/{trip_id}")
def get_trip(trip_id: str) -> dict:
    view = trip_service.get_trip(trip_id)
    if view is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy chuyến đi")
    return view
