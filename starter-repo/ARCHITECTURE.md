# ARCHITECTURE — Agent lập lịch trình du lịch (Track C)

> Bản đồ codebase. Chi tiết thiết kế và lý do: [`docs/superpowers/specs/2026-11-27-travel-planner-design.md`](docs/superpowers/specs/2026-11-27-travel-planner-design.md) · kế hoạch từng task: [`docs/superpowers/plans/2026-11-27-travel-planner.md`](docs/superpowers/plans/2026-11-27-travel-planner.md).

## 1. Hệ thống làm gì

Người dùng nhắn một yêu cầu tiếng Việt (sở thích, ngân sách, số ngày, số người). Hệ thống trả **lịch trình 2–3 ngày từng giờ ở thành phố người dùng chọn** — điểm chơi, quán ăn, khách sạn, di chuyển, tổng tiền, lý do — hoặc hỏi lại thông tin thiếu, hoặc nói rõ vì sao không xếp được và nên nới ràng buộc nào.

Nguyên tắc chi phối mọi quyết định: **model chọn *cái gì*, code quyết *lúc nào* và *bao nhiêu tiền*.** Model chỉ trả id + lý do; giờ, tiền, giờ mở cửa, còn phòng đều do code tính từ dữ liệu.

## 2. Hai lối vào, một lõi

```
  python run.py eval / simulate                    trình duyệt (React)
            │                                              │
            ▼                                              ▼
  codebase/agent.py :: answer(text)          FastAPI  src/main.py  (/api/trips)
  graph KHÔNG checkpointer,                  graph + SqliteSaver, dừng sau "select"
  không dừng, không nhớ                      để người dùng chọn khách sạn
            │                                              │
            └──────────────► build_travel_graph() ◄────────┘
                                   │
          ┌────────────────────────┼─────────────────────────┐
          ▼                        ▼                         ▼
   ai.call_model()          codebase/tools.py          src/core/planning/
   (model duy nhất,         (@tool, chỉ đọc)           (code thuần: xếp giờ,
    khung đếm token)               │                    tính tiền, kiểm lịch)
                                   ▼
        src/core/sources/ → Tavily (tìm web) · Nominatim (toạ độ) · cache data/cache/
```

- **Lối chấm** (`answer()`): bộ chấm của BTC gọi; phải chạy không cần server, database hay mạng ngoài lời gọi model.
- **Lối web**: web React (`codebase/web`, Vite) chạy riêng, gọi FastAPI **chỉ qua API** (`/api/trips`, CORS theo `WEB_ORIGINS`). Không commit `dist/`. Không đăng nhập, không Postgres, không Redis.

## 3. Luồng graph

> Nguồn dữ liệu đã đổi sang tìm web (spec §5.10). Bảng node dưới đây sẽ cập nhật đầy đủ ở Task 7; luồng đúng là dòng sơ đồ thứ hai.

```
parse_request ──thiếu tt / ngoài phạm vi / lỗi định dạng──► END (hỏi lại · từ chối · báo lỗi)
     │ đủ
     ▼
plan_queries ─► search ─► extract_candidates ─► ground_and_rank ─► [web: người dùng chọn | chấm: auto_select] ─► schedule_node ─► validate_node ─┬─ sạch ─────────────► render_node ─► END
  (code)    (model)      (code)          (code)       ├─ vi phạm, vòng < 2 ─► select (kèm vi phạm)
                                                      └─ vi phạm, hết vòng ─► infeasible_node ─► END
```

| Node | Ai làm | Vào → ra |
|---|---|---|
| `parse_request` | model + code | tin nhắn → `TripRequest` (code chuẩn hoá tiền, ngày, số người; thiếu → hỏi lại) |
| `research` | code + tools | `TripRequest` → ứng viên đã lọc (trẻ nhỏ, giờ mở theo thứ, còn phòng) |
| `select` | model | ứng viên (+ vi phạm vòng trước) → `Selection`: id + lý do, **không giờ, không tiền** |
| `schedule_node` | code | `Selection` → `Itinerary` (khung giờ, chi phí từng mục, tổng) |
| `validate_node` | code | `Itinerary` → danh sách `Violation` |
| `render_node` | code | lịch → chữ (cho `answer()`) + JSON (cho web); lý do lấy từ model |
| `infeasible_node` | code | nêu ràng buộc chặn + mức nới có số |

Web dừng sau `select` (`interrupt_after`), người dùng đổi hoặc giữ khách sạn, graph chạy tiếp từ `schedule_node`.

## 4. Bản đồ thư mục

Trạng thái: ✅ có · 🟡 khung (docstring, chưa code) · ⬜ chưa tạo.

| Đường dẫn (từ `starter-repo/`) | Vai trò | Trạng thái |
|---|---|---|
| `run.py`, `codebase/tracing.py`, `eval/run_eval.py`, `cost/simulate.py` | khung chấm của BTC — không sửa | ✅ |
| `codebase/agent.py` | `answer(text) -> {"output"}` → graph | ✅ mẫu khung · Task 7 viết lại |
| `codebase/ai.py` | `call_model` — chỗ duy nhất gọi model (fake / gemini) | ✅ mẫu khung · Task 7 |
| `codebase/tools.py` | công cụ `@tool` chỉ đọc + `kiem_lich_trinh` | ✅ mẫu khung · Task 4, 6 |
| `codebase/app.py` | `python run.py` → khởi động uvicorn | ✅ CLI mẫu · Task 11 |
| `codebase/_paths.py` | thêm `codebase/` và `codebase/backend/` vào `sys.path` | ✅ |
| `codebase/backend/src/core/planning/` | lõi code thuần: `types`, `data`, `request`, `travel`, `scheduler`, `validator`, `feasibility`, `render` | 🟡 Task 1–7 |
| `codebase/backend/src/core/orchestration/` | LangGraph: `state/`, `prompts/`, `nodes/`, `graphs/`, `utils/utils.py` (bóc JSON) | 🟡 Task 7 |
| `codebase/backend/src/api/` | `routes/trips.py` → `services/trip_service.py` → graph; `schemas.py` | 🟡 Task 9′ |
| `codebase/backend/src/main.py` | app FastAPI, `/api/health`, CORS cho web | ✅ health + CORS · Task 9′ |
| `codebase/backend/var/trips.sqlite` | checkpoint graph của web (gitignore, env `TRIPS_DB`) | ⬜ tạo khi chạy |
| `codebase/web/` | Vite + React + TS + Tailwind + SCSS; gọi backend qua `VITE_API_URL` / proxy `/api`; `?demo=1` chạy không cần backend | ✅ giao diện + demo · nối API thật sau Task 9′ |
| `codebase/backend/src/core/sources/` | gọi Tavily / Nominatim qua cache ghi-lại-phát-lại (`SEARCH_MODE`) | ⬜ Task 1 |
| `data/estimates.json`, `data/cache/` | bảng số ước tính khi bài viết không có; cache tìm kiếm của bộ câu thử (commit) | ⬜ Task 1, 7 |
| `eval/benchmark.csv`, `eval/metric_spec.yaml` | bộ câu thử + chuẩn "đạt" (khoá sau CP2) | ⬜ Task 2 |
| `tests/` | pytest; `conftest.py` nạp `_paths` | ✅ smoke |

Thứ tự phụ thuộc (import một chiều): `planning` ← `tools.py` ← `orchestration` ← `agent.py` / `api`. `planning` không import LangGraph, FastAPI hay `ai`.

## 5. Dữ liệu và kiểu chính

- **Dữ liệu thành phố** — `data/cities/<slug>/{diem_choi,quan_an,khach_san,phuong_tien}.json`; lược đồ từng trường ở Task 1 của kế hoạch. `gio_mo` theo thứ (`"0"` = Thứ Hai, thiếu khoá = đóng cửa); `het_phong_ngay` là danh sách `YYYY-MM-DD`.
- **`TripRequest`** — city, days (1–5), start_date (+ `date_assumed`), budget_vnd (tổng cả nhóm, chi phí tại điểm đến), adults, children_ages, interests, incidents (trễ chuyến / mưa), preferred_hotel.
- **`Selection`** — hotel, transport, mỗi ngày: attractions (thứ tự), lunch, dinner; reasons theo id.
- **`Itinerary`** — các ngày → `Slot`(start, end, kind, ref, cost_vnd); cost_breakdown {ve, an, khach_san, di_chuyen}; total_vnd.
- **`TripView`** (API) — trip_id, status ∈ {hotel_pending, ok, ask_back, refused, infeasible, error}, message, hotel_options?, chosen_hotel?, itinerary?.

## 6. Bất biến

1. Mọi con số trong output (giờ, tiền, giờ mở) do code tính từ dữ liệu; model không trả số.
2. Mọi lời gọi model đi qua `ai.call_model` (để khung đếm token và ghi trace).
3. Công cụ chỉ đọc; hệ thống không đặt chỗ, không thanh toán.
4. `answer()` không nhớ giữa các lần gọi; mỗi câu thử tự đủ thông tin.
5. Lịch chỉ trả ra khi `validate` sạch; không sạch sau `MAX_REPAIR = 2` vòng thì trả lời "không xếp được" kèm mức nới.
6. Web và lối chấm dùng cùng `build_travel_graph`; khác nhau chỉ ở checkpointer và điểm dừng.

## 7. Chạy

```bash
cd starter-repo
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/pytest tests -q                 # test
.venv/bin/python run.py eval --try        # chấm thử 3 câu qua answer()
.venv/bin/python run.py                   # API: http://localhost:8000
cd codebase/web && npm install && npm run dev   # web: http://localhost:5173 (proxy /api → :8000) · ?demo=1 không cần backend
```

Model: `starter-repo/.env` — `MODEL_PROVIDER=gemini`, `MODEL_NAME`, `API_KEY` (không commit). Để trống = chế độ giả.

## 8. Mở rộng

- **Thêm thành phố:** thêm `data/cities/<slug>/` + một dòng `SUPPORTED_CITIES`.
- **Nhiều thành phố (hướng C):** `TripRequest.city` → `legs: [{city, days}]`, thêm công cụ `tra_chang_di` và một node xếp chặng trước `schedule_node`.
- **Đăng nhập / lịch sử người dùng:** code auth + Postgres cũ còn ở commit `6dcd7bb`.
