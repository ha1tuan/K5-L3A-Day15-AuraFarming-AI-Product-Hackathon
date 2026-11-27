"""Router /api/trips: POST tạo chuyến (cách C), GET đọc lại chuyến đã lưu."""
from fastapi import APIRouter, HTTPException

from src.api.schemas import ApproveInput, ChatInput, QuoteInput, TripInput
from src.api.services import trip_service

router = APIRouter(prefix="/api/trips", tags=["Trips"])


@router.post("")
def create_trip(body: TripInput) -> dict:
    return trip_service.create_trip(body)


@router.get("/{trip_id}")
def get_trip(trip_id: str) -> dict:
    view = trip_service.get_trip(trip_id)
    if view is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy chuyến đi")
    return view


@router.post("/{trip_id}/approve")
def approve_trip(trip_id: str, body: ApproveInput) -> dict:
    view = trip_service.approve_trip(trip_id, body)
    if view is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy chuyến đi")
    return view


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
