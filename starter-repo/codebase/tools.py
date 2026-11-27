"""Công cụ của bài toán — NHÓM VIẾT. Điền ở guide bước 2.2 (thiết kế) và 3.2 (code).

Mỗi công cụ là một hàm Python có @tool. Docstring ghi đúng 4 ý như sơ đồ ở spec.md §4:
    tên · input · output · có tác động ra ngoài không (gửi tin, sửa dữ liệu, chấm điểm…)
Khung tự ghi mỗi lần gọi công cụ vào trace (tên, input, output rút gọn, thời gian, lỗi).

Số công cụ, kiểu công cụ do thiết kế của nhóm quyết định — có bài chỉ cần một công cụ tra cứu.
Công cụ có tác động ra ngoài: KHÔNG tự làm. Trả về bản nháp chờ người duyệt (guide bước 2.2, "chỗ người duyệt").
Dữ liệu công cụ đọc (bài mẫu, thông báo mẫu, lịch…): để trong data/ và mô tả ở data/DATA_CARD.md.
"""
from dataclasses import asdict

from tracing import tool, note, TOOLS  # noqa: F401  (TOOLS: danh sách công cụ đã đăng ký, dùng khi viết vòng lặp agent)

from src.core.sources import CacheMiss, SearchUnavailable
from src.core.sources.geo import geocode
from src.core.sources.tavily_client import search


@tool
def search_example(query: str) -> list:
    """(ví dụ — thay bằng công cụ của nhóm) Tra dữ liệu mẫu theo câu hỏi.
    Input: câu hỏi (str). Output: danh sách đoạn {"code", "text"}. Không tác động ra ngoài."""
    return [{"code": "VD-1", "text": "(ví dụ) đoạn dữ liệu giả — thay bằng dữ liệu thật của bài toán"}]


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
