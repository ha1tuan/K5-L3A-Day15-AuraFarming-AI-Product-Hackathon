# CLAUDE.md

Repo nộp bài hackathon AI20K, Track C: agent lập lịch trình du lịch Đà Lạt 2–3 ngày, có lối chấm (`answer()`) và web (FastAPI + React).

@AGENTS.md

## Đọc trước khi làm

- **Bản đồ code, luồng graph, bất biến** — [ARCHITECTURE.md](ARCHITECTURE.md). Đọc trước khi tạo file mới hoặc đổi chỗ code.
- **Lý do của từng quyết định** — [spec](docs/superpowers/specs/2026-11-27-travel-planner-design.md).
- **Việc đang làm** — [plan cách C](docs/superpowers/plans/2026-11-27-entry-c-plan.md) (plan cũ [travel-planner](docs/superpowers/plans/2026-11-27-travel-planner.md) viết cho bài toán người đi lẻ — chỉ tham khảo): làm đúng một task, đúng tên hàm và test trong khối *Interfaces* của task đó.

## Lệnh (chạy từ `starter-repo/`, luôn dùng venv)

```bash
.venv/bin/pytest tests -q -W ignore::DeprecationWarning
.venv/bin/python run.py eval --try        # chạy answer() trên 3 câu đầu
cd codebase/web && npm run dev && npm test   # web chạy riêng, gọi backend qua API; không commit dist/
```

## Cách làm

- **Test trước:** viết test của task → thấy đỏ → code → xanh → commit một task một commit trên nhánh `feat/travel-planner`.
- **Số do code tính:** giờ, tiền, giờ mở cửa, còn phòng lấy từ `src/core/planning/` và dữ liệu; prompt chỉ xin model id + lý do.
- **Model chỉ qua `ai.call_model`**; test thay model bằng monkeypatch `trip_nodes.call_model`, không gọi API thật.
- **`src/core/planning/` là code thuần**: chỉ import thư viện chuẩn và `planning`; LangGraph ở `orchestration/`, FastAPI ở `api/`.
- **Chữ cho người dùng bằng tiếng Việt**; tiền dạng `1.250.000đ`.

## Bẫy

- Import backend theo gói `src.*`; module trong `codebase/` cần `import _paths` trước (đã có ở `tests/conftest.py`).
- Ngày giả định phụ thuộc hôm nay: test và bộ chấm đặt env `TRAVEL_TODAY=YYYY-MM-DD` để kết quả cố định.
- `answer()` chạy không server: `graphs/graph.py` chỉ dựng `SqliteSaver` trong `get_web_graph()`, không ở đầu module.
- Python 3.14 in `DeprecationWarning` từ `langsmith` — vô hại.
