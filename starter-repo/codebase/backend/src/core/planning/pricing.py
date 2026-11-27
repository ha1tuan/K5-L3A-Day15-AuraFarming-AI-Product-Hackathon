"""Dự trù chi phí 3 gói (tiết kiệm / cân bằng / cao cấp) cho cách C. Số do code tính từ bảng ước tính
(estimates) và khách sạn đã chọn; mọi dòng có amount = qty × unit_price."""
import math
from typing import Optional

from .estimates import Estimates
from .rooms import allocate_rooms
from .travel import leg
from .types import Candidate, GeoPoint, LineItem, Package, PackageSummary, TripRequest

TIERS = ("tiet_kiem", "can_bang", "cao_cap")
CONTINGENCY = 0.05


def round1k(x) -> int:
    """Làm tròn nửa lên tới 1.000."""
    return int(math.floor(x / 1000 + 0.5)) * 1000


def _item(category, description, qty, unit, unit_price, estimated=True, source_url=None, note=None) -> LineItem:
    return LineItem(category, description, qty, unit, unit_price, qty * unit_price, estimated, source_url, note)


def _room_label(kind: str) -> str:
    return f"Phòng {kind} người" if kind.isdigit() else f"Phòng {kind}"


def price_tier(req: TripRequest, tier: str, origin_pt: Optional[GeoPoint], dest_pt: Optional[GeoPoint],
               hotel: Optional[Candidate], est: Estimates, category_tiers: Optional[dict] = None,
               drop: set = frozenset(), nights: Optional[int] = None) -> Package:
    """Giá một gói. category_tiers: {hạng mục: gói} -> hạng mục đó dùng bảng giá của gói kia;
    drop: hạng mục bị bỏ (vd {"Gala"}); nights: ghi đè số đêm (days = nights + 1).
    Khách sạn `hotel` do người gọi chọn sẵn, được dùng nguyên cho hạng mục Lưu trú."""
    ct = category_tiers or {}
    use = lambda cat: ct.get(cat, tier)  # noqa: E731
    n = req.headcount
    nights = req.nights if nights is None else nights
    days = req.days if nights == req.nights else nights + 1
    dest_name = req.destination or ""
    items: list[LineItem] = []

    # Di chuyển
    lg = leg(origin_pt, dest_pt, use("Di chuyển"), n, dest_name, est, days=days)
    if lg.mode == "plane":
        items.append(_item("Di chuyển", f"Vé máy bay khứ hồi đi {dest_name}".strip(), lg.qty, "người",
                           lg.unit_price, note=lg.note))
    else:
        items.append(_item("Di chuyển", f"{lg.note} ({lg.road_km} km)", lg.qty, "xe", lg.unit_price,
                           note="Khoảng cách ước tính" if lg.estimated else None))

    # Lưu trú
    room_plan = None
    if nights >= 1 and "Lưu trú" not in drop:
        lt = use("Lưu trú")
        if hotel is not None and hotel.room_types:
            types, hname, url = hotel.room_types, hotel.name, hotel.source_url
        else:
            stars = hotel.stars if hotel is not None and hotel.stars else est.tier_stars[lt]
            types = est.rooms[str(stars)]
            hname, url = (hotel.name if hotel is not None else f"khách sạn {stars} sao"), None
        room_plan = allocate_rooms(n, types)
        by_kind = {t.kind: t for t in types}
        for kind, count in room_plan.counts.items():
            rt = by_kind[kind]
            items.append(_item("Lưu trú", f"{_room_label(kind)} – {hname}", count * nights, "phòng-đêm", rt.price,
                               estimated=rt.estimated, source_url=rt.source_url or url))
        if room_plan.short:
            items[-1].note = f"Thiếu chỗ cho {room_plan.short} người, cần xác nhận thêm phòng"

    # Gala thay bữa tối đêm cuối
    gala_tier = use("Gala")
    gala = (req.purpose != "nghi_duong" and tier != "tiet_kiem" and nights >= 1
            and "gala" not in req.exclude and "Gala" not in drop)

    # Ăn uống: ngày 1 và ngày giữa trưa + tối, ngày cuối chỉ trưa; days=1 chỉ trưa
    meal_price = est.meal_per_pax[use("Ăn uống")]
    meals = 0
    for d in range(1, days + 1):
        items.append(_item("Ăn uống", f"Ngày {d} – bữa trưa", n, "suất", meal_price))
        meals += 1
        if d < days and not (gala and d == days - 1):
            items.append(_item("Ăn uống", f"Ngày {d} – bữa tối", n, "suất", meal_price))
            meals += 1
    if nights >= 1:
        items.append(_item("Ăn uống", "Bữa sáng đã gồm trong giá phòng", 0, "suất", 0, estimated=False))

    if gala:
        items.append(_item("Gala", "Tiệc gala dinner đêm cuối", n, "người", est.gala_per_pax[gala_tier]))
        items.append(_item("Gala", "MC – âm thanh – ánh sáng", 1, "gói", est.gala_fixed[gala_tier]))

    # Hoạt động
    act_tier = use("Hoạt động")
    team = req.purpose != "nghi_duong" and "team_building" not in req.exclude
    activity = ""
    if "Hoạt động" not in drop and (team or req.purpose == "nghi_duong"):
        activity = "Team building" if team else "Hoạt động nghỉ dưỡng"
        items.append(_item("Hoạt động", activity, n, "người", est.activity_per_pax[req.purpose][act_tier]))

    if "Vé tham quan" not in drop:
        items.append(_item("Vé tham quan", "Vé tham quan điểm đến", n, "người", est.sight_per_pax[use("Vé tham quan")]))

    other = sum(li.amount for li in items)
    fee = round1k(other * CONTINGENCY)
    items.append(_item("Phát sinh", "Dự phòng phát sinh 5%", 1, "gói", fee))
    total = other + fee

    rooms_text = "Không lưu trú" if nights < 1 else ", ".join(
        f"{c} phòng {k} người" if k.isdigit() else f"{c} phòng {k}" for k, c in room_plan.counts.items())
    stars = est.tier_stars[use("Lưu trú")]
    summary = PackageSummary(
        transport=lg.note or "", lodging="" if nights < 1 else (hotel.name if hotel else f"Khách sạn {stars} sao"),
        rooms=f"{rooms_text} × {nights} đêm" if nights >= 1 else rooms_text,
        meals=f"{meals} bữa chính", gala="Có gala dinner" if gala else "Không có", activities=activity or "Không có")
    return Package(tier=tier, summary=summary, line_items=items, total=total, per_person=round1k(total / n),
                   over_budget=None if req.budget is None else total - req.budget, leg=lg, room_plan=room_plan)


def price_packages(req: TripRequest, origin_pt, dest_pt, hotels: dict, est: Estimates) -> list[Package]:
    pk = [price_tier(req, t, origin_pt, dest_pt, hotels.get(t), est) for t in TIERS]
    within = [p for p in pk if req.budget is not None and p.total <= req.budget]
    (within[-1] if within else pk[0]).recommended = True
    return pk
