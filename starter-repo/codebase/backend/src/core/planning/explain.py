"""Giải thích vì sao gói vượt ngân sách và gợi ý cách cắt giảm. Mọi `total_after` đều do
`price_tier` tính lại với thay đổi tương ứng, không cộng trừ tay trên dòng chi phí."""
from collections import defaultdict
from typing import Optional

from .estimates import Estimates
from .pricing import TIERS, price_tier
from .types import Explanation, Package, TripRequest

TIER_NAMES = {"tiet_kiem": "tiết kiệm", "can_bang": "cân bằng", "cao_cap": "cao cấp"}
SKIP = "Phát sinh"  # dự phòng 5% tính theo phần còn lại, không phải một lựa chọn


def _money(x: int) -> str:
    return f"{x:,}".replace(",", ".") + "đ"


def _by_category(pkg: Package) -> dict[str, int]:
    out: dict[str, int] = defaultdict(int)
    for li in pkg.line_items:
        if li.category != SKIP:
            out[li.category] += li.amount
    return dict(out)


def _describe(pkg: Package, cat: str) -> str:
    """Mô tả ngắn hạng mục ở mức của gói (dùng trong nhãn 'A thay B')."""
    if cat == "Di chuyển" and pkg.summary.transport:
        return pkg.summary.transport
    if cat == "Lưu trú" and pkg.summary.lodging:
        return pkg.summary.lodging
    li = next((x for x in pkg.line_items if x.category == cat and x.amount > 0), None)
    return f"{_money(li.unit_price)}/{li.unit}" if li else "không có"


def _drivers(pkg: Package, lower: Optional[Package]) -> list[dict]:
    cur = _by_category(pkg)
    if lower is None:
        top = sorted(cur.items(), key=lambda kv: kv[1], reverse=True)[:2]
        return [{"label": f"{c}: {_describe(pkg, c)}", "amount": a, "category": c} for c, a in top if a > 0]
    prev = _by_category(lower)
    deltas = {c: a - prev.get(c, 0) for c, a in cur.items()}
    top = sorted((kv for kv in deltas.items() if kv[1] > 0), key=lambda kv: kv[1], reverse=True)[:3]
    return [{"label": f"{c}: {_describe(pkg, c)} thay {_describe(lower, c)}", "amount": a, "category": c}
            for c, a in top]


def explain_over(packages: list[Package], budget: int, req: TripRequest, est: Estimates,
                 origin_pt=None, dest_pt=None, hotels: Optional[dict] = None) -> None:
    """Gán `Package.explanation` cho mỗi gói vượt ngân sách. origin_pt/dest_pt/hotels phải giống
    lúc gọi `price_packages` để giá tính lại khớp."""
    hotels = hotels or {}
    ordered = sorted(packages, key=lambda p: TIERS.index(p.tier))
    for i, pkg in enumerate(ordered):
        if pkg.over_budget is None or pkg.over_budget <= 0:
            continue
        lower = ordered[i - 1] if i > 0 else None
        hotel = hotels.get(pkg.tier)

        def reprice(**kw) -> int:
            return price_tier(req, pkg.tier, origin_pt, dest_pt, hotel, est, **kw).total

        drivers = _drivers(pkg, lower)
        cuts = []
        if lower is not None:
            for d in drivers:
                after = reprice(category_tiers={d["category"]: lower.tier})
                cuts.append((f"Hạ {d['category'].lower()} xuống mức {TIER_NAMES[lower.tier]}", after))
        if any(li.category == "Gala" for li in pkg.line_items):
            cuts.append(("Bỏ gala dinner", reprice(drop=frozenset({"Gala"}))))
        if req.nights >= 1:
            cuts.append(("Bớt 1 đêm", reprice(nights=req.nights - 1)))
        cut_rows = sorted(({"label": lb, "saving": pkg.total - after, "total_after": after}
                           for lb, after in cuts if pkg.total - after > 0),
                          key=lambda c: c["saving"], reverse=True)[:3]
        pkg.explanation = Explanation(
            over_amount=pkg.over_budget, over_pct=round(pkg.over_budget / budget * 100) if budget else 0,
            compared_to=lower.tier if lower else None,
            drivers=[{"label": d["label"], "amount": d["amount"]} for d in drivers], cuts=cut_rows)
    if ordered and all(p.over_budget is not None and p.over_budget > 0 for p in ordered):
        if ordered[0].explanation:
            ordered[0].explanation.min_budget = ordered[0].total
