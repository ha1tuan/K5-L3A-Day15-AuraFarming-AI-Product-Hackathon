"""Bảng ước tính giá (data/estimates.json). Mỗi giá trị trong file đều kèm "_source"
("tự ước tính" khi chưa có nguồn thật). Loader bỏ các khoá "_source" và trả về Estimates."""
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .types import RoomType

DEFAULT_PATH = Path(__file__).resolve().parents[5] / "data" / "estimates.json"
BANDS = ("<500", "500–1000", ">1000")


def band_of(km: float) -> str:
    return BANDS[0] if km < 500 else BANDS[1] if km <= 1000 else BANDS[2]


def _plain(node):
    """Bỏ "_source": {"value": x, "_source": s} -> x; dict khác bỏ các khoá bắt đầu bằng "_"."""
    if isinstance(node, dict):
        if "value" in node and "_source" in node:
            return _plain(node["value"])
        return {k: _plain(v) for k, v in node.items() if not k.startswith("_")}
    if isinstance(node, list):
        return [_plain(v) for v in node]
    return node


@dataclass
class Estimates:
    transport: dict          # tier -> {vehicle, capacity, price_per_km, day_fee}
    flight_per_pax: dict     # tier -> {"<500", "500–1000", ">1000"} (khứ hồi / người)
    rooms: dict              # stars(str) -> list[RoomType] 2/3/4 người
    meal_per_pax: dict
    gala_per_pax: dict
    gala_fixed: dict
    activity_per_pax: dict   # purpose -> tier -> giá
    sight_per_pax: dict
    tier_stars: dict
    flight_only: list


def load_estimates(path: Optional[Path] = None) -> Estimates:
    raw = _plain(json.loads(Path(path or DEFAULT_PATH).read_text(encoding="utf-8")))
    rooms = {
        stars: [RoomType(kind=str(r["capacity"]), capacity=r["capacity"], price=r["price"], estimated=True)
                for r in sorted(types, key=lambda r: r["capacity"])]
        for stars, types in raw["rooms"].items()
    }
    return Estimates(
        transport=raw["transport"], flight_per_pax=raw["flight_per_pax"], rooms=rooms,
        meal_per_pax=raw["meal_per_pax"], gala_per_pax=raw["gala_per_pax"], gala_fixed=raw["gala_fixed"],
        activity_per_pax=raw["activity_per_pax"], sight_per_pax=raw["sight_per_pax"],
        tier_stars=raw["tier_stars"], flight_only=raw["flight_only"],
    )
