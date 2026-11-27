"""App FastAPI: chỉ phục vụ API dưới /api. Web React (codebase/web) chạy riêng và gọi API này.

Chạy: python run.py  (codebase/app.py gọi uvicorn)  ·  hoặc trong codebase/backend: uvicorn src.main:app --reload
Router /api/trips: thêm ở Task 9′.
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Travel Planner API", version="0.1.0", description="AI lập lịch trình du lịch")

# Web React chạy riêng (Vite :5173 khi dev) và gọi API qua HTTP → cho phép origin của web.
# Production: đặt WEB_ORIGINS="https://web.example.com" (nhiều origin cách nhau bằng dấu phẩy).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in os.getenv("WEB_ORIGINS", "http://localhost:5173").split(",") if o.strip()],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/api/health", tags=["System"])
def health() -> dict:
    return {"status": "ok"}
