"""Chuẩn hoá yêu cầu do model bóc ra: parse_vnd, default_start, build_request, ask_back_text,
understood_text. Code thuần, chỉ thư viện chuẩn."""
import re
from datetime import date, timedelta
from typing import Optional

from .types import TripRequest

MIN_HEADCOUNT, MAX_HEADCOUNT = 5, 500
MAX_DAYS = 7
PURPOSES = ("gan_ket", "nghi_duong", "ca_hai")
EXCLUDABLE = ("gala", "team_building")
DOMESTIC = {"", "vn", "vietnam", "viet nam", "việt nam"}

_FIELD_TEXT = {
    "headcount": "số người đi",
    "days": "số ngày",
    "origin": "điểm xuất phát",
    "purpose": "mục đích chuyến đi (gắn kết, nghỉ dưỡng hay cả hai)",
    "budget_or_destination": "ngân sách hoặc địa điểm",
}
_UNITS = {"tỷ": 10**9, "tỉ": 10**9, "ty": 10**9, "triệu": 10**6, "trieu": 10**6, "tr": 10**6,
          "nghìn": 10**3, "ngàn": 10**3, "k": 10**3}
_NUM = re.compile(r"(\d+(?:[.,]\d+)*)\s*(tỷ|tỉ|ty|triệu|trieu|tr|nghìn|ngàn|k)?(?![a-zà-ỹ])")
_PER_PERSON = re.compile(r"(mỗi|một)\s*(người|nguoi|pax)\b|/\s*(người|nguoi|pax)\b|đầu người|dau nguoi|per person")


def _amount(num: str, unit: Optional[str]) -> int:
    if unit:
        return round(float(num.replace(",", ".")) * _UNITS[unit])
    return int(re.sub(r"[.,]", "", num))


def parse_vnd(s) -> Optional[int]:
    if s is None or isinstance(s, bool):
        return None
    if isinstance(s, (int, float)):
        return int(s)
    text = str(s).lower()
    matches = list(_NUM.finditer(text))
    if not matches:
        return None
    m = next((m for m in matches if m.group(2)), matches[0])
    return _amount(m.group(1), m.group(2))


def default_start(today: date) -> date:
    """Thứ Sáu kế tiếp; hôm nay là thứ Sáu thì lấy thứ Sáu tuần sau."""
    return today + timedelta(days=(4 - today.weekday()) % 7 or 7)


def _int(v) -> Optional[int]:
    try:
        return int(v) if v is not None and not isinstance(v, bool) else None
    except (TypeError, ValueError):
        return None


def _text(v) -> str:
    return str(v).strip() if v else ""


def build_request(raw: dict, today: date):
    """Trả (TripRequest | None, trường thiếu, lý do từ chối)."""
    country = _text(raw.get("country")).lower()
    if country not in DOMESTIC:
        return None, [], "Hiện chỉ hỗ trợ lập kế hoạch cho chuyến đi trong nước (Việt Nam)."
    headcount = _int(raw.get("headcount"))
    if headcount is not None and not MIN_HEADCOUNT <= headcount <= MAX_HEADCOUNT:
        return None, [], f"Hiện chỉ hỗ trợ đoàn từ {MIN_HEADCOUNT} đến {MAX_HEADCOUNT} người."

    days = _int(raw.get("days"))
    if days is not None and days > MAX_DAYS:
        return None, [], f"Hiện chỉ hỗ trợ chuyến đi tối đa {MAX_DAYS} ngày."
    if days is not None and days < 1:
        days = None
    origin = _text(raw.get("origin"))
    purpose = raw.get("purpose") if raw.get("purpose") in PURPOSES else None
    budget_text = raw.get("budget_text")
    destination = _text(raw.get("destination")) or None
    budget = parse_vnd(budget_text)

    missing = [name for name, ok in (("headcount", headcount is not None), ("days", days is not None),
                                     ("origin", bool(origin)), ("purpose", purpose is not None),
                                     ("budget_or_destination", budget is not None or destination is not None)) if not ok]
    if missing:
        return None, missing, None

    per_person = budget is not None and bool(_PER_PERSON.search(str(budget_text).lower()))
    if per_person:
        budget *= headcount
    start, assumed = None, True
    if raw.get("start_date"):
        try:
            start, assumed = date.fromisoformat(str(raw["start_date"])[:10]), False
        except ValueError:
            pass
    entry = "C" if budget is not None and destination else ("A" if budget is not None else "B")
    exclude = {x for x in (raw.get("exclude") or []) if x in EXCLUDABLE}
    return TripRequest(headcount=headcount, days=days, nights=days - 1, start_date=start or default_start(today),
                       origin=origin, purpose=purpose, budget=budget, budget_per_person_input=per_person,
                       destination=destination, date_assumed=assumed, entry=entry, exclude=exclude), [], None


def _vnd(n: int) -> str:
    return f"{n:,}".replace(",", ".") + "đ"


def ask_back_text(missing: list[str]) -> str:
    return "Để lập kế hoạch, mình cần thêm: " + ", ".join(_FIELD_TEXT.get(f, f) for f in missing) + "."


def understood_text(req: TripRequest) -> str:
    if req.budget is None:
        return f"Đã hiểu: {req.headcount} người"
    return f"Ngân sách đã hiểu: {_vnd(req.budget)} cho {req.headcount} người"
