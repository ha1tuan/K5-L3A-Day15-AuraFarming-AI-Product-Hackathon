"""Định vị qua Nominatim (OpenStreetMap), có cache, tối đa 1 yêu cầu/giây."""
import time
from typing import Optional

import httpx

from ..planning.types import GeoPoint
from .cache import cached_call

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "travel-planner-hackathon"
MIN_INTERVAL = 1.0

_last_call: Optional[float] = None


def _throttle() -> None:
    global _last_call
    if _last_call is not None:
        wait = MIN_INTERVAL - (time.monotonic() - _last_call)
        if wait > 0:
            time.sleep(wait)
    _last_call = time.monotonic()


def _fetch(params: dict) -> list[dict]:
    _throttle()
    resp = httpx.get(NOMINATIM_URL, params=params, headers={"User-Agent": USER_AGENT}, timeout=20)
    resp.raise_for_status()
    return [
        {"lat": r["lat"], "lon": r["lon"], "country_code": (r.get("address") or {}).get("country_code")}
        for r in resp.json()[:1]
    ]


def geocode(name: str, near: Optional[str] = None, domestic: bool = False) -> Optional[GeoPoint]:
    """domestic=True khi đã biết địa điểm trong nước: thêm countrycodes=vn."""
    params = {
        "q": f"{name}, {near}" if near else name,
        "format": "jsonv2",
        "limit": 1,
        "addressdetails": 1,
    }
    if domestic:
        params["countrycodes"] = "vn"
    try:
        rows = cached_call("geo", params, lambda: _fetch(params))
    except httpx.HTTPError:
        return None
    if not rows:
        return None
    r = rows[0]
    return GeoPoint(float(r["lat"]), float(r["lon"]), r.get("country_code"))
