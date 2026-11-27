"""Nguồn dữ liệu ngoài (Tavily, Nominatim) qua cache ghi-lại-phát-lại. Gói này import planning (kiểu dữ liệu); planning không import ngược lại."""


class CacheMiss(Exception):
    """Chế độ replay mà cache không có khoá yêu cầu."""


class SearchUnavailable(Exception):
    """Không thể tìm kiếm (thiếu TAVILY_API_KEY, lỗi mạng / HTTP, phản hồi không phải JSON)."""
