"""Công cụ của bài toán — mỗi hàm có @tool để khung ghi vào trace (spec.md §4 bảng "AI dựa vào đâu").

Bản chạy thử hiện CHƯA có công cụ tìm kiếm web (Tavily cần key, chưa có): đơn giá do model đề xuất và luôn mang
nhãn "ước tính"; không nêu tên cơ sở cụ thể vì không có nguồn để kiểm (spec.md §4 "Phần còn giả").
"""
import planner
from tracing import tool, TOOLS  # noqa: F401


@tool
def xep_phong(loai_phong: list, so_nguoi: int) -> dict:
    """xep_phong · input: loại phòng [{ten, suc_chua, gia_dem, so_phong_con}], số người ·
    output: cơ cấu phòng rẻ nhất đủ chỗ (quy hoạch động), số chỗ, tiền / đêm, số chỗ còn thiếu ·
    tác động ra ngoài: không (tính bằng code)."""
    return planner.xep_phong(loai_phong, so_nguoi)


@tool
def du_tru_goi(req: dict, level: str, goi: dict) -> dict:
    """du_tru_goi · input: yêu cầu đã chuẩn hoá, mức gói, hạng mục + đơn giá tham khảo ·
    output: bảng khoản mục (số lượng × đơn giá = thành tiền), phát sinh 5%, tổng, mỗi người ·
    tác động ra ngoài: không (tính bằng code)."""
    return planner.tinh_goi(req, level, goi)


@tool
def giai_thich_vuot(req: dict, budget: int, g: dict, g_thap, goi_raw: dict, goi_thap_raw) -> str:
    """giai_thich_vuot · input: gói đã tính, gói thấp hơn liền kề, ngân sách ·
    output: số vượt + %, khoản gây vượt có số, cách cắt giảm có số (tính lại bằng code) ·
    tác động ra ngoài: không."""
    return planner.giai_thich_vuot(req, budget, g, g_thap, goi_raw, goi_thap_raw)
