"""Kiểm lịch: validate(req, plan, pkg) -> list[Violation].
Mã: CHONG_GIO (khối chồng nhau) · QUA_GIO_KET_THUC (kết thúc sau 22:00, trừ chặng về) · TRUNG_DIEM
(cùng một nơi xuất hiện hai lần) · THIEU_PHONG (RoomPlan.short > 0) · THIEU_SUC_CHUA (nguồn ghi sức chứa < số người).
(ID_KHONG_TON_TAI do bước chọn của trip_nodes phát ra.)"""
import re

from .scheduler import RETURN_PREFIX, slot_minutes, to_min
from .types import Violation

LATEST_END = 22 * 60
CAPACITY_RE = re.compile(r"Sức chứa theo nguồn: (\d+)")


def validate(req, plan, pkg) -> list[Violation]:
    out: list[Violation] = []
    seen: set = set()
    for day in plan.days:
        slots = sorted(day.slots, key=lambda s: to_min(s.start))
        for a, b in zip(slots, slots[1:]):
            if to_min(a.start) + slot_minutes(a, pkg) > to_min(b.start):
                out.append(Violation("CHONG_GIO", "%s: \"%s\" chồng lên \"%s\"" % (day.label, a.title, b.title),
                                     b.title))
        for s in slots:
            is_return = s.kind == "travel" and s.title.startswith(RETURN_PREFIX)
            if not is_return and to_min(s.start) + slot_minutes(s, pkg) > LATEST_END:
                out.append(Violation("QUA_GIO_KET_THUC", "%s: \"%s\" kết thúc sau 22:00" % (day.label, s.title),
                                     s.title))
            if s.source_url and s.kind in ("meal", "activity", "sight"):
                if s.source_url in seen:
                    out.append(Violation("TRUNG_DIEM", "\"%s\" xuất hiện nhiều hơn một lần" % s.title, s.title))
                seen.add(s.source_url)
            m = CAPACITY_RE.search(s.details or "")
            if m and int(m.group(1)) < req.headcount:
                out.append(Violation("THIEU_SUC_CHUA", "\"%s\" chỉ chứa %s người, đoàn %d người" % (
                    s.title, m.group(1), req.headcount), s.title))
    if pkg.room_plan is not None and pkg.room_plan.short > 0:
        out.append(Violation("THIEU_PHONG", "Gói %s còn thiếu chỗ cho %d người" % (pkg.tier, pkg.room_plan.short),
                             pkg.tier))
    return out
