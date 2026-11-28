"""Công cụ của bài toán — mỗi hàm có @tool để khung ghi vào trace (spec.md §4 bảng "AI dựa vào đâu").

Bản chạy thử hiện CHƯA có công cụ tìm kiếm web (Tavily cần key, chưa có): đơn giá do model đề xuất và luôn mang
nhãn "ước tính"; không nêu tên cơ sở cụ thể vì không có nguồn để kiểm (spec.md §4 "Phần còn giả").
"""
import os
from dataclasses import asdict
from datetime import date
from types import SimpleNamespace

import _paths  # noqa: F401  (thêm codebase/backend vào sys.path để import src.* khi chạy run.py eval / app)
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
    VE_MUON, TRUNG_DIEM, THIEU_PHONG, THIEU_SUC_CHUA · không tác động ra ngoài."""
    pkg = SimpleNamespace(tier=plan.get("tier"), leg=SimpleNamespace(hours=leg_hours),
                          room_plan=SimpleNamespace(short=room_short))
    found = validate(SimpleNamespace(headcount=headcount), _plan_from_dict(plan), pkg)
    return [asdict(v) for v in found]
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


# --- Bộ dữ liệu data/*.json (codebase/du_lieu.py) ---------------------------------------------------
import du_lieu  # noqa: E402


@tool
def du_tru_tu_du_lieu(req: dict):
    """du_tru_tu_du_lieu · input: yêu cầu đã chuẩn hoá (so_nguoi, so_ngay, so_dem, muc_dich, noi_xuat_phat, dia_diem) ·
    output: 3 gói tính từ data/*.json (chặng đi theo tuyến, phòng / bữa / hoạt động theo mức và mục đích, video)
    hoặc None nếu nơi đi / điểm đến không có trong dữ liệu · không tác động ra ngoài."""
    tu, den = du_lieu.tim_diem_di(req.get("noi_xuat_phat")), du_lieu.tim_diem_den(req.get("dia_diem"))
    return du_lieu.dung_diem_den(req, tu, den) if tu and den else None


@tool
def goi_y_diem_den(req: dict, so: int = 3) -> list:
    """goi_y_diem_den · input: yêu cầu đã chuẩn hoá (có ngân sách, chưa có địa điểm), số gợi ý ·
    output: tối đa `so` điểm đến trong 24 nơi của data/*.json, xếp bằng code theo mục đích, gói cao nhất còn trong
    ngân sách, giờ đi một chiều, mùa đẹp; mỗi nơi đủ 3 gói · không tác động ra ngoài."""
    tu = du_lieu.tim_diem_di(req.get("noi_xuat_phat"))
    return du_lieu.goi_y_diem_den(req, tu, so) if tu else []


import soat_bao_gia  # noqa: E402


@tool
def soat_bao_gia_tour(text: str) -> str:
    """soat_bao_gia_tour · input: tin nhắn có báo giá tour đoàn (giá / khách, 'bao gồm', 'không bao gồm') + số người,
    ngân sách · output: bảng tổng chi thật (giá tour + VAT + vé / tip / vé máy bay tính được), so ngân sách, soát hoá đơn /
    chuyển khoản / trần phúc lợi (data/quy_tac_chung_tu.json), câu cần hỏi lại công ty tour · không tác động ra ngoài."""
    return soat_bao_gia.soat(text)
