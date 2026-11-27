"""Kết quả cách C -> chữ cho answer() (render_text) và dict TripView cho web (to_view).
Mọi số lấy nguyên từ Package / Plan do code tính; ở đây chỉ định dạng. Chỉ thư viện chuẩn + planning."""
from dataclasses import asdict
from datetime import date, timedelta
from typing import Optional

from .request import understood_text
from .scheduler import WEEKDAYS
from .types import Package, Plan, TripRequest

TIER_TITLES = {"tiet_kiem": "Tiết kiệm", "can_bang": "Cân bằng", "cao_cap": "Cao cấp"}
PURPOSE_TEXT = {"gan_ket": "gắn kết đội", "nghi_duong": "nghỉ dưỡng", "ca_hai": "gắn kết + nghỉ dưỡng"}
FOOTER = "Giá tham khảo; hệ thống không đặt chỗ."
NO_SOURCE = ("Lưu ý: chưa tìm được nguồn cho cơ sở lưu trú, ăn uống, hoạt động cụ thể; "
             "mọi đơn giá dưới đây là ước tính, cần báo giá thực tế.")
MAX_DISHES = 5
MAX_STEPS = 6
KEEP_NULL = {"over_budget", "budget"}  # types.ts: number | null (các trường khác có dấu ? -> bỏ khi None)


def money(x: int) -> str:
    return f"{x:,}".replace(",", ".") + "đ"


def _dmy(d: date) -> str:
    return d.strftime("%d/%m/%Y")


def _header(req: TripRequest) -> list[str]:
    start = req.start_date
    end = start + timedelta(days=req.days - 1)
    trip = "%d ngày %d đêm" % (req.days, req.nights) if req.nights else "%d ngày" % req.days
    when = "%s %s – %s" % (WEEKDAYS[start.weekday()], _dmy(start), _dmy(end))
    if req.date_assumed:
        when += " (chưa có ngày đi, tạm lấy thứ Sáu gần nhất)"
    return [understood_text(req),
            "Chuyến đi: %s · %s · từ %s · %s · %s" % (req.destination, trip, req.origin,
                                                      PURPOSE_TEXT.get(req.purpose, req.purpose), when)]


def _status(pkg: Package) -> str:
    if pkg.over_budget is None:
        return ""
    if pkg.over_budget > 0:
        return " · Vượt ngân sách %s" % money(pkg.over_budget)
    return " · Trong ngân sách (còn dư %s)" % money(-pkg.over_budget)


def _explanation(pkg: Package) -> list[str]:
    e = pkg.explanation
    if e is None:
        return []
    out = ["Giải thích vượt ngân sách:",
           "- Vượt %s (%s%% ngân sách)" % (money(e.over_amount), e.over_pct)]
    if e.drivers:
        base = " (so với gói %s)" % TIER_TITLES[e.compared_to].lower() if e.compared_to else ""
        out.append("- Khoản gây vượt%s:" % base)
        out += ["  + %s: %s" % (d["label"], money(d["amount"])) for d in e.drivers]
    if e.cuts:
        out.append("- Cách cắt giảm:")
        out += ["  + %s: tiết kiệm %s, tổng sau cắt %s" % (c["label"], money(c["saving"]), money(c["total_after"]))
                for c in e.cuts]
    if e.min_budget:
        out.append("- Ngân sách tối thiểu (tổng gói tiết kiệm): %s" % money(e.min_budget))
    return out


def _cost_table(pkg: Package, headcount: int) -> list[str]:
    out = ["Bảng chi phí:"]
    for li in pkg.line_items:
        desc = li.description + (" (ước tính)" if li.estimated else "")
        if li.amount == 0:  # dòng "đã gồm" / chưa có phòng: không phải khoản tiền
            out.append("- %s%s" % (li.description, " — %s" % li.note if li.note else ""))
            continue
        out.append("- %s: %d %s × %s = %s" % (desc, li.qty, li.unit, money(li.unit_price), money(li.amount)))
        extra = [x for x in (li.note, "nguồn: %s" % li.source_url if li.source_url else None) if x]
        if extra:
            out.append("  (%s)" % "; ".join(extra))
    out.append("Tổng cộng: %s" % money(pkg.total))
    out.append("Mỗi người: %s (tổng / %d người)" % (money(pkg.per_person), headcount))
    return out


def _slot_lines(slot) -> list[str]:
    head = "- %s · %s" % (slot.start, slot.title)
    if "estimate" in slot.flags:
        head += " (ước tính)"
    out = [head]
    if slot.note:
        out.append("  Ghi chú: %s" % slot.note)
    if slot.details:
        out.append("  %s" % slot.details)
    if slot.menu:
        m = slot.menu
        dishes = ", ".join(m.dishes[:MAX_DISHES]) + (", …" if len(m.dishes) > MAX_DISHES else "")
        out.append("  Thực đơn: %s (%s/khách): %s" % (m.name, money(m.price_per_pax), dishes or "theo nhà hàng"))
    if slot.program:
        steps = slot.program.get("steps") or []
        text = "; ".join("%s %s" % (s.start, s.text) for s in steps[:MAX_STEPS])
        if len(steps) > MAX_STEPS:
            text += "; …"
        out.append("  Chương trình%s: %s" % (" " + slot.program["title"] if slot.program.get("title") else "", text))
    flags = [f for f in slot.flags if f != "estimate"]
    if "confirm_rooms" in flags:
        out.append("  Cần xác nhận còn đủ phòng với khách sạn.")
    if "confirm_capacity" in flags:
        out.append("  Cần xác nhận sức chứa cho cả đoàn.")
    if slot.source_url:
        out.append("  Nguồn: %s" % slot.source_url)
    return out


def render_text(req: TripRequest, packages: list[Package], plans: list[Plan], estimate_only: bool = False,
                notes: Optional[list[str]] = None) -> str:
    """Chữ cho answer(): đầu là câu 'đã hiểu', mỗi gói một khối (tổng, giải thích vượt, bảng chi phí dạng
    '<mô tả>: <qty> <unit> × <đơn giá> = <thành tiền>', cơ cấu phòng, lịch từng ngày), cuối là lưu ý giá."""
    lines = _header(req)
    if estimate_only:
        lines.append(NO_SOURCE)
    plan_by_tier = {p.tier: p for p in plans}
    for i, pkg in enumerate(packages, 1):
        plan = plan_by_tier.get(pkg.tier)
        title = TIER_TITLES[pkg.tier] + (" — phù hợp ngân sách nhất" if pkg.recommended else "")
        lines += ["", "=== Kế hoạch %d: %s ===" % (i, title),
                  "Tổng: %s · Mỗi người: %s%s" % (money(pkg.total), money(pkg.per_person), _status(pkg))]
        s = pkg.summary
        lines.append("Tóm tắt: di chuyển %s; lưu trú %s; %s; gala: %s; hoạt động: %s" % (
            s.transport or "—", s.lodging or "không", s.meals, s.gala, s.activities))
        lines += _explanation(pkg)
        lines += _cost_table(pkg, req.headcount)
        lines.append("Cơ cấu phòng: %s" % (s.rooms or "Không lưu trú"))
        if plan is not None:
            if plan.estimate_note:
                lines.append("Ước tính: %s trong tổng là ước tính. %s" % (money(plan.estimate_total), plan.estimate_note))
            lines.append("Lịch trình:")
            for day in plan.days:
                lines.append("%s (%s)" % (day.label, _dmy(date.fromisoformat(day.date))))
                for slot in day.slots:
                    lines += _slot_lines(slot)
    for n in notes or []:
        lines += ["", n]
    lines += ["", FOOTER]
    return "\n".join(lines)


def _clean(node):
    """Bỏ khoá giá trị None (trường tuỳ chọn của types.ts), trừ KEEP_NULL."""
    if isinstance(node, dict):
        return {k: _clean(v) for k, v in node.items() if v is not None or k in KEEP_NULL}
    if isinstance(node, list):
        return [_clean(v) for v in node]
    return node


def _package_view(pkg: Package) -> dict:
    d = asdict(pkg)
    d.pop("leg", None)
    d.pop("room_plan", None)
    return _clean(d)


def to_view(trip_id: str, req: TripRequest, packages: list[Package], plans: list[Plan],
            message: Optional[str] = None) -> dict:
    """Dict đúng TripView (codebase/web/src/api/types.ts) cho cách C, status "ok"."""
    end = req.start_date + timedelta(days=req.days - 1)
    echo = {"headcount": req.headcount, "days": req.days, "nights": req.nights,
            "start_date": req.start_date.isoformat(), "end_date": end.isoformat(), "origin": req.origin,
            "purpose": req.purpose, "budget": req.budget, "entry": req.entry}
    return {"trip_id": trip_id, "status": "ok", "message": message or understood_text(req), "request": echo,
            "destination": req.destination, "packages": [_package_view(p) for p in packages],
            "plans": [_clean(asdict(p)) for p in plans]}
