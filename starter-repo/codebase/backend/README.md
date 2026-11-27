# Backend — Travel Planner

Một tiến trình FastAPI chỉ phục vụ API dưới `/api`; web React (`codebase/web`) chạy riêng và gọi API này.
Chuyến đi lưu trong bộ nhớ tiến trình (tối đa 200 chuyến, mất khi khởi động lại).

Kiến trúc, luồng dữ liệu và trạng thái từng phần: [../../ARCHITECTURE.md](../../ARCHITECTURE.md).

```bash
# từ starter-repo/ (model + Tavily đọc từ starter-repo/.env)
python -m venv .venv && .venv/bin/pip install -r requirements.txt
cd codebase/backend && ../../.venv/bin/python -m uvicorn src.main:app --reload --port 8000

# terminal khác: web
cd codebase/web && npm install && npm run dev    # http://localhost:5173, /api proxy → :8000
```

| Endpoint | Mô tả |
|---|---|
| `GET /api/health` | `{"status": "ok"}` |
| `POST /api/trips` | body `TripInput` → `TripView` (cách C: `status: "ok"` + 3 gói + 3 kế hoạch; thiếu trường → `ask_back`; ngoài phạm vi → `refused`; lỗi model/tìm kiếm → `error`) |
| `GET /api/trips/{id}` | đọc lại `TripView` đã lưu (404 nếu không có) |
| `POST /api/trips/{id}/approve` | cách A/B — chưa hỗ trợ, trả `status: "error"` |

Hợp đồng dữ liệu: `src/api/schemas.py` ↔ `codebase/web/src/api/types.ts`.
Deploy web ở origin khác: đặt `WEB_ORIGINS=https://web.example.com` cho CORS và build web với `VITE_API_URL`.
