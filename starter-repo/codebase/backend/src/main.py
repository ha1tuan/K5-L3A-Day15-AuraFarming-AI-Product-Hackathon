"""App FastAPI: chỉ phục vụ API dưới /api. Web React (codebase/web) chạy riêng và gọi API này.

Chạy: python run.py  (codebase/app.py gọi uvicorn)  ·  hoặc trong codebase/backend: uvicorn src.main:app --reload
Router /api/trips: src/api/routes/trips.py.
"""
import os
import sys

# Node gọi model import `ai` (ở codebase/) → thêm codebase/ vào sys.path khi chạy uvicorn từ codebase/backend.
_CODEBASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _CODEBASE not in sys.path:
    sys.path.insert(0, _CODEBASE)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import trips

app = FastAPI(title="Travel Planner API", version="0.1.0", description="AI lập lịch trình du lịch")

# Web React chạy riêng (Vite :5173 khi dev) và gọi API qua HTTP → cho phép origin của web.
# Production: đặt WEB_ORIGINS="https://web.example.com" (nhiều origin cách nhau bằng dấu phẩy).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in os.getenv("WEB_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if o.strip()],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


app.include_router(trips.router)


@app.get("/api/health", tags=["System"])
def health() -> dict:
    return {"status": "ok"}
