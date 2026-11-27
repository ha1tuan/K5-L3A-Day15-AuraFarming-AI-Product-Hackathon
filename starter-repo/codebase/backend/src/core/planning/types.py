"""Kiểu dữ liệu của lõi lập kế hoạch (cách C). Dataclass thuần; tên trường của LineItem, Package,
Explanation, Menu, ProgramStep, Slot, Day, Plan khớp codebase/web/src/api/types.ts."""
from dataclasses import dataclass, field
from datetime import date
from typing import Literal, Optional

Tier = Literal["tiet_kiem", "can_bang", "cao_cap"]
Purpose = Literal["gan_ket", "nghi_duong", "ca_hai"]


@dataclass
class TripRequest:
    headcount: int
    days: int
    nights: int
    start_date: date
    origin: str
    purpose: Purpose
    budget: Optional[int]
    budget_per_person_input: bool
    destination: Optional[str]
    date_assumed: bool
    entry: Literal["A", "B", "C"]
    exclude: set[str] = field(default_factory=set)


@dataclass
class GeoPoint:
    lat: float
    lon: float
    country_code: Optional[str] = None


@dataclass
class RoomType:
    kind: str
    capacity: int
    price: int
    available: Optional[int] = None
    estimated: bool = False
    source_url: Optional[str] = None


@dataclass
class Candidate:
    id: str
    name: str
    group: Literal["luu_tru", "an_uong", "hoat_dong"]
    reason: str = ""
    source_url: Optional[str] = None
    domain: str = ""
    mentions: int = 1
    stars: Optional[int] = None
    room_types: list[RoomType] = field(default_factory=list)
    price_per_pax: Optional[int] = None
    price_source_url: Optional[str] = None
    capacity: Optional[int] = None
    menu_items: list[str] = field(default_factory=list)


@dataclass
class Leg:
    """Chặng di chuyển (logic tính ở Task 3)."""
    mode: str
    road_km: float
    hours: float
    vehicles: int
    unit_price: int
    qty: int
    estimated: bool = False
    note: Optional[str] = None


@dataclass
class RoomPlan:
    """Phương án phòng (logic tính ở Task 3)."""
    counts: dict[str, int]
    seats: int
    cost_per_night: int
    short: int = 0


@dataclass
class LineItem:
    category: str
    description: str
    qty: int
    unit: str
    unit_price: int
    amount: int
    estimated: bool = False
    source_url: Optional[str] = None
    note: Optional[str] = None


@dataclass
class Explanation:
    over_amount: int
    over_pct: float
    compared_to: Optional[Tier] = None
    drivers: list[dict] = field(default_factory=list)  # {label, amount}
    cuts: list[dict] = field(default_factory=list)  # {label, saving, total_after}
    min_budget: Optional[int] = None


@dataclass
class PackageSummary:
    transport: str = ""
    lodging: str = ""
    rooms: str = ""
    meals: str = ""
    gala: str = ""
    activities: str = ""


@dataclass
class Package:
    tier: Tier
    summary: PackageSummary
    line_items: list[LineItem]
    total: int
    per_person: int
    over_budget: Optional[int] = None
    recommended: bool = False
    explanation: Optional[Explanation] = None
    # Nội bộ, không thuộc hợp đồng web:
    leg: Optional[Leg] = None
    room_plan: Optional[RoomPlan] = None


@dataclass
class Menu:
    name: str
    price_per_pax: int
    dishes: list[str] = field(default_factory=list)
    estimated: bool = False
    table_size: Optional[int] = None
    drinks_note: Optional[str] = None
    source_url: Optional[str] = None


@dataclass
class ProgramStep:
    start: str
    end: str
    text: str


SlotKind = Literal["travel", "hotel", "meal", "activity", "gala", "sight", "rest"]


@dataclass
class Slot:
    start: str
    kind: SlotKind
    title: str
    note: Optional[str] = None
    flags: list[str] = field(default_factory=list)  # estimate | confirm_rooms | confirm_capacity
    source_url: Optional[str] = None
    menu: Optional[Menu] = None
    program: Optional[dict] = None  # {title?, steps: list[ProgramStep], includes?, fallback?}
    details: Optional[str] = None
    ref: Optional[str] = None  # nội bộ: id ứng viên (không thuộc hợp đồng web, to_view bỏ đi)


@dataclass
class Day:
    label: str
    date: str
    slots: list[Slot] = field(default_factory=list)


@dataclass
class Plan:
    tier: Tier
    destination: str
    total: int
    per_person: int
    estimate_total: int = 0
    estimate_note: Optional[str] = None
    over_budget: Optional[int] = None
    explanation: Optional[Explanation] = None
    days: list[Day] = field(default_factory=list)


@dataclass
class TierPick:
    """Lựa chọn của model cho một gói: id khách sạn, id quán theo thứ tự bữa, id hoạt động, lý do theo id."""
    hotel: Optional[str] = None
    restaurants: list[str] = field(default_factory=list)
    activities: list[str] = field(default_factory=list)
    reasons: dict[str, str] = field(default_factory=dict)


@dataclass
class Violation:
    code: str
    message: str
    ref: Optional[str] = None
