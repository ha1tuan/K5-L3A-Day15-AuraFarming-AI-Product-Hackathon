"""Chặng đi từ điểm xuất phát tới điểm đến: leg(...) -> Leg. Đường bộ = haversine × 1.3;
giờ xe = km/50 + 0.5 giờ nghỉ cho mỗi 3 giờ chạy. Chỉ thư viện chuẩn + planning."""
import math
from typing import Optional

from .estimates import Estimates, band_of
from .types import GeoPoint, Leg

ROAD_FACTOR = 1.3
BUS_KMH = 50
DEFAULT_KM = 300
PLANE_KMH = 700
PLANE_OVERHEAD_H = 3.0   # làm thủ tục + di chuyển ra/vào sân bay
PREMIUM_FLY_OVER_H = 8


def haversine_km(a: GeoPoint, b: GeoPoint) -> float:
    p1, p2 = math.radians(a.lat), math.radians(b.lat)
    dp, dl = p2 - p1, math.radians(b.lon - a.lon)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h))


def bus_hours(road_km: float) -> float:
    drive = road_km / BUS_KMH
    return round(drive + 0.5 * int(drive // 3), 2)


def leg(origin: Optional[GeoPoint], dest: Optional[GeoPoint], tier: str, headcount: int,
        dest_name: str, est: Estimates, days: int = 1) -> Leg:
    """Xe: unit_price = giá một xe cho cả chuyến khứ hồi (km × 2 × đơn giá + phí ngày × days), qty = số xe.
    Máy bay: unit_price = vé khứ hồi một người, qty = headcount."""
    guessed = origin is None or dest is None
    road_km = DEFAULT_KM if guessed else round(haversine_km(origin, dest) * ROAD_FACTOR)
    hours = bus_hours(road_km)
    if dest_name in est.flight_only or (tier == "cao_cap" and hours > PREMIUM_FLY_OVER_H):
        return Leg(mode="plane", road_km=road_km, hours=round(road_km / PLANE_KMH + PLANE_OVERHEAD_H, 2),
                   vehicles=0, unit_price=est.flight_per_pax[tier][band_of(road_km)], qty=headcount,
                   estimated=guessed, note="Vé máy bay khứ hồi")
    t = est.transport[tier]
    vehicles = -(-headcount // t["capacity"])
    price = round(road_km * 2 * t["price_per_km"] + t["day_fee"] * days)
    return Leg(mode="bus", road_km=road_km, hours=hours, vehicles=vehicles, unit_price=price, qty=vehicles,
               estimated=guessed, note=f"{t['vehicle']} khứ hồi")
