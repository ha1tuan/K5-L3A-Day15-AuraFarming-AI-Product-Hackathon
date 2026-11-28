"""Router /api/trips: tạo chuyến, chọn gói và đọc lại chuyến đã lưu."""
from fastapi import APIRouter, HTTPException

from fastapi.responses import Response

from src.api.schemas import ApproveInput, ChatInput, QuoteInput, RecalcInput, TripInput, TripQuoteInput
from src.api.services import du_lieu_service
from src.api.services import trip_service

router = APIRouter(prefix="/api/trips", tags=["Trips"])


@router.post("")
def create_trip(body: TripInput) -> dict:
    return trip_service.create_trip(body)


@router.post("/{trip_id}/approve")
def approve_trip(trip_id: str, body: ApproveInput) -> dict:
    try:
        view = trip_service.approve_trip(trip_id, body)
    except trip_service.InvalidTripSelection as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if view is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy chuyến đi")
    return view


@router.get("/{trip_id}")
def get_trip(trip_id: str) -> dict:
    view = trip_service.get_trip(trip_id)
    if view is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy chuyến đi")
    return view


@router.post("/{trip_id}/recalc")
def recalc_trip(trip_id: str, body: RecalcInput) -> dict:
    """Sửa ngay trên trang kế hoạch: số người, số ngày, bỏ / thêm lại từng khoản → tính lại."""
    if body.headcount is not None and not 5 <= body.headcount <= 500:
        raise HTTPException(status_code=422, detail="Số người 5–500")
    if body.days is not None and not 1 <= body.days <= 7:
        raise HTTPException(status_code=422, detail="Số ngày 1–7")
    view = trip_service.recalc_trip(trip_id, body)
    if view is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy chuyến đi (hoặc chưa có địa điểm)")
    return view


@router.post("/{trip_id}/quote")
def quote_for_trip(trip_id: str, body: TripQuoteInput) -> dict:
    """Đối chiếu báo giá tour với gói đã lập."""
    import guardrails as gr
    safe, _ = gr.scrub_sensitive(body.text[:20000])
    r = trip_service.quote_for_trip(trip_id, body.tier, safe)
    if r is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy chuyến đi")
    return r


@router.get("/{trip_id}/export.xlsx")
def export_trip(trip_id: str) -> Response:
    view = trip_service.get_trip(trip_id)
    if view is None or not view.get("packages"):
        raise HTTPException(status_code=404, detail="Không tìm thấy chuyến đi")
    return Response(du_lieu_service.export_xlsx(view), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": 'attachment; filename="to-trinh-AuraFarming-%s.xlsx"' % trip_id[:8]})


estimate_router = APIRouter(prefix="/api/estimate", tags=["Estimate"])


@estimate_router.get("")
def estimate(origin: str, destination: str, headcount: int, days: int, purpose: str = "ca_hai") -> dict:
    """Ước tính nhanh khi đang điền form (không lưu)."""
    if not (5 <= headcount <= 500 and 1 <= days <= 7):
        return {"status": "skip"}
    r = du_lieu_service.estimate(origin, destination, headcount, days, purpose)
    return dict(r, status="ok") if r else {"status": "skip"}


quote_router = APIRouter(prefix="/api/quote-audit", tags=["Quote audit"])


@quote_router.post("")
def quote_audit(body: QuoteInput) -> dict:
    """Soát báo giá tour đoàn: tổng chi thật + chứng từ (codebase/soat_bao_gia.py, code thuần)."""
    import guardrails as gr
    import soat_bao_gia
    safe, _ = gr.scrub_sensitive(body.text[:20000])
    if not soat_bao_gia.la_bao_gia(safe):
        return {"status": "ask_back", "message": "Chưa thấy báo giá: cần có giá / khách và mục \"bao gồm\", \"không bao gồm\"."}
    return soat_bao_gia.soat(safe, ket_qua=True)


chat_router = APIRouter(prefix="/api/chat", tags=["Chat"])


@chat_router.post("")
def chat(body: ChatInput) -> dict:
    """Trợ lý Aura: báo giá → soát; yêu cầu chuyến đi → agent.answer(); còn lại → hỏi đáp (codebase/chat.py)."""
    import chat as aura
    return aura.tra_loi(body.messages)
