"""Luồng chính của bản chạy thử (lối chấm): answer(text) -> {"output": str}.

`python run.py`, `python run.py eval` và `python run.py simulate` đều gọi answer(text).
Hình dạng: workflow cố định (LangGraph, cách C — có cả kinh phí và địa điểm):
parse -> geocode -> research -> select -> price -> schedule -> validate -> (sửa ≤ 2 lần | explain) -> render.
Model chỉ bóc yêu cầu, lên từ khoá, trích ứng viên và chọn id; mọi con số do code tính.
Ngày tham chiếu: env TRAVEL_TODAY (YYYY-MM-DD), mặc định hôm nay.
"""
import os
from datetime import date

import _paths  # noqa: F401  (đặt đường dẫn cho gói src.*)

from src.core.orchestration.graphs.graph import build_trip_graph


def _today() -> date:
    v = (os.environ.get("TRAVEL_TODAY") or "").strip()
    return date.fromisoformat(v) if v else date.today()


def answer(text: str) -> dict:
    return {"output": build_trip_graph().invoke({"text": text, "today": _today()})["output"]}
