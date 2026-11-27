"""Công cụ của bài toán — NHÓM VIẾT. Điền ở guide bước 2.2 (thiết kế) và 3.2 (code).

Mỗi công cụ là một hàm Python có @tool. Docstring ghi đúng 4 ý như sơ đồ ở spec.md §4:
    tên · input · output · có tác động ra ngoài không (gửi tin, sửa dữ liệu, chấm điểm…)
Khung tự ghi mỗi lần gọi công cụ vào trace (tên, input, output rút gọn, thời gian, lỗi).

Số công cụ, kiểu công cụ do thiết kế của nhóm quyết định — có bài chỉ cần một công cụ tra cứu.
Công cụ có tác động ra ngoài: KHÔNG tự làm. Trả về bản nháp chờ người duyệt (guide bước 2.2, "chỗ người duyệt").
Dữ liệu công cụ đọc (bài mẫu, thông báo mẫu, lịch…): để trong data/ và mô tả ở data/DATA_CARD.md.
"""
import os
from dataclasses import asdict
from datetime import date
from types import SimpleNamespace

from tracing import tool, note, TOOLS  # noqa: F401  (TOOLS: danh sách công cụ đã đăng ký, dùng khi viết vòng lặp agent)

from src.core.planning.estimates import load_estimates
from src.core.planning.pricing import price_packages
from src.core.planning.request import default_start
from src.core.planning.rooms import allocate_rooms
from src.core.planning.types import Day, GeoPoint, Menu, Plan, Slot, TripRequest
from src.core.planning.validator import validate
from src.core.sources import CacheMiss, SearchUnavailable
from src.core.sources.geo import geocode
from src.core.sources.tavily_client import search


@tool
def tim_kiem_web(query: str) -> list:
    """tim_kiem_web · input: từ khoá (str) · output: danh sách {title, url, snippet, domain}; rỗng khi
    không tìm được (thiếu khoá / không có trong cache) · không tác động ra ngoài."""
    try:
        return [asdict(h) for h in search(query)]
    except (SearchUnavailable, CacheMiss):
        note("search: unavailable")
        return []


@tool
def dinh_vi(name: str, near: str = None, domestic: bool = True):
    """dinh_vi · input: tên nơi (str), near: vùng lân cận (str, tuỳ chọn), domestic: địa điểm trong nước (mặc định True)
    · output: {lat, lon, country_code} hoặc None · không tác động ra ngoài."""
    try:
        p = geocode(name, near, domestic=domestic)
    except (SearchUnavailable, CacheMiss):
        note("geocode: unavailable")
        return None
    return asdict(p) if p else None


@tool
def xep_phong(headcount: int, stars: int = 3) -> dict:
    """xep_phong · input: số người (int), hạng sao 2-5 (int, mặc định 3) · output: {counts, seats, cost_per_night, short}
    theo bảng giá phòng ước tính · không tác động ra ngoài."""
    types = load_estimates().rooms.get(str(stars))
    if not types:
        return {"error": "không có bảng phòng cho hạng %s sao" % stars}
    return asdict(allocate_rooms(headcount, types))


def _point(d):
    return GeoPoint(**d) if d else None


@tool
def du_tru_goi(headcount: int, days: int, nights: int, origin: str, destination: str,
               purpose: str = "gan_ket", budget: int = None, start_date: str = None) -> list:
    """du_tru_goi · input: số người, số ngày, số đêm, nơi đi, nơi đến, mục đích (gan_ket|nghi_duong|ca_hai),
    ngân sách tổng (tuỳ chọn), ngày đi ISO (tuỳ chọn) · output: 3 gói tiết kiệm / cân bằng / cao cấp
    (dòng chi phí, tổng, bình quân người) tính bằng bảng ước tính, chưa chọn khách sạn cụ thể · không tác động ra ngoài."""
    req = TripRequest(headcount=headcount, days=days, nights=nights,
                      start_date=date.fromisoformat(start_date) if start_date else default_start(
                          date.fromisoformat(os.environ.get("TRAVEL_TODAY") or date.today().isoformat())), origin=origin,
                      purpose=purpose, budget=budget, budget_per_person_input=False, destination=destination,
                      date_assumed=start_date is None, entry="C")
    pkgs = price_packages(req, _point(dinh_vi(origin)), _point(dinh_vi(destination)), {}, load_estimates())
    return [asdict(p) for p in pkgs]


def _plan_from_dict(d: dict) -> Plan:
    def slot(s: dict) -> Slot:
        s = dict(s)
        if s.get("menu"):
            s["menu"] = Menu(**s["menu"])
        return Slot(**s)

    return Plan(**{**d, "explanation": None, "days": [Day(x["label"], x["date"], [slot(s) for s in x["slots"]])
                                                     for x in d["days"]]})


@tool
def kiem_lich_trinh(headcount: int, plan: dict, room_short: int = 0, leg_hours: float = 4.0) -> list:
    """kiem_lich_trinh · input: số người, plan (dict dạng Plan của web), room_short: số người còn thiếu phòng,
    leg_hours: giờ của chặng di chuyển · output: danh sách {code, message, ref} với mã CHONG_GIO, QUA_GIO_KET_THUC,
    TRUNG_DIEM, THIEU_PHONG, THIEU_SUC_CHUA · không tác động ra ngoài."""
    pkg = SimpleNamespace(tier=plan.get("tier"), leg=SimpleNamespace(hours=leg_hours),
                          room_plan=SimpleNamespace(short=room_short))
    found = validate(SimpleNamespace(headcount=headcount), _plan_from_dict(plan), pkg)
    return [asdict(v) for v in found]
