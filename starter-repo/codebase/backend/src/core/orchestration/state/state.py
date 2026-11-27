"""TripState — trạng thái graph cách C (Task 7). Mọi khoá ghi đè (không reducer cộng dồn):
validate_node tự trả danh sách warnings đầy đủ (cũ + mới)."""
from datetime import date
from typing import Optional, TypedDict, Union

from src.core.planning.estimates import Estimates
from src.core.planning.types import Candidate, GeoPoint, Package, Plan, TierPick, TripRequest, Violation


class TripState(TypedDict, total=False):
    text: str                       # tin nhắn người dùng (đầu vào)
    raw: dict                       # trường đã bóc sẵn (đường form của web)
    today: Union[date, str]         # ngày tham chiếu (date hoặc YYYY-MM-DD)
    request: Optional[TripRequest]
    missing: list[str]
    refusal: Optional[str]
    status: str                     # ok | ask_back | refused
    notice: Optional[str]           # câu từ chối đặt chỗ / thanh toán (vẫn lập kế hoạch)
    origin_pt: Optional[GeoPoint]
    dest_pt: Optional[GeoPoint]
    est: Estimates
    ranked: dict[str, list[Candidate]]
    estimate_only: bool
    picks: dict[str, TierPick]
    pick_violations: list[Violation]
    packages: list[Package]
    plans: list[Plan]
    violations: list[Violation]
    repair_round: int
    warnings: list[str]
    output: str                     # chữ cho answer()
    view: dict                      # TripView cho web
