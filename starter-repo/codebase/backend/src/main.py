"""App FastAPI: chỉ phục vụ API dưới /api. Web React (codebase/web) chạy riêng và gọi API này.

Chạy: python run.py  (codebase/app.py gọi uvicorn)  ·  hoặc trong codebase/backend: uvicorn src.main:app --reload
Router /api/trips: src/api/routes/trips.py.
"""
import os
import sys

# codebase/ (ai, tools, du_lieu, planner…) phải có trong sys.path khi chạy uvicorn từ codebase/backend
_CODEBASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _CODEBASE not in sys.path:
    sys.path.insert(0, _CODEBASE)

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from src.api.routes import trips  # noqa: E402

app = FastAPI(title="Travel Planner API", version="0.1.0", description="AI lập lịch trình du lịch")

# Web React chạy riêng (Vite :5173 khi dev) và gọi API qua HTTP → cho phép origin của web.
# Production: đặt WEB_ORIGINS="https://web.example.com" (nhiều origin cách nhau bằng dấu phẩy).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in os.getenv("WEB_ORIGINS", "http://localhost:5173").split(",") if o.strip()],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


app.include_router(trips.router)
app.include_router(trips.quote_router)
app.include_router(trips.chat_router)
app.include_router(trips.estimate_router)


@app.get("/api/health", tags=["System"])
def health() -> dict:
    return {"status": "ok"}


# Tuỳ chọn: SERVE_WEB=1 → phục vụ luôn bản build của web (codebase/web/dist) ở "/" cùng cổng với API — tiện demo / quay video
# bằng một lệnh. Mặc định tắt: web vẫn chạy riêng (npm run dev) và gọi API như thiết kế.
_DIST = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "web", "dist")
if os.getenv("SERVE_WEB") == "1" and os.path.isdir(_DIST):
    from fastapi.staticfiles import StaticFiles

    app.mount("/", StaticFiles(directory=_DIST, html=True), name="web")
