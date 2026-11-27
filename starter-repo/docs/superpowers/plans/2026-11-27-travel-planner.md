# Travel Planner (Đà Lạt 2–3 ngày) Implementation Plan

> **Đã thay:** bài toán đổi sang chuyến đi cả công ty. Cách C (có kinh phí + địa điểm) làm theo [2026-11-27-entry-c-plan.md](2026-11-27-entry-c-plan.md). Plan này chỉ còn để tham khảo.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Agent nhận một tin nhắn tiếng Việt (sở thích, ngân sách, số ngày, số người) và trả lịch trình Đà Lạt từng ngày, từng giờ, kèm tổng tiền và lý do — hoặc hỏi lại / báo không xếp được; chạy được qua `python run.py eval` và qua API FastAPI đã dọn.

**Architecture:** LangGraph workflow cố định trong `codebase/backend/src/core/orchestration/`: parse_request (model) → research (code) → select (model, chỉ chọn id) → schedule (code) → validate (code) → vòng sửa ≤ 2 → render (code chèn số + lý do của model) hoặc infeasible. Logic thuần (dữ liệu, xếp giờ, kiểm, khả thi) nằm ở `src/core/planning/`, không phụ thuộc LangGraph. `codebase/agent.py::answer` chạy graph không checkpointer; app FastAPI chạy cùng graph với Postgres checkpointer và dừng sau select.

**Tech Stack:** Python 3.14 (venv `starter-repo/.venv`), langgraph, google-genai, pytest; khung chấm của BTC (stdlib).

**Spec:** `docs/superpowers/specs/2026-11-27-travel-planner-design.md`

## Global Constraints

- Hợp đồng khung: `answer(text: str) -> {"output": str}` trong `codebase/agent.py`; `call_model(system, user) -> {"text","model","tokens_in","tokens_out"}` có `@model_call` trong `codebase/ai.py`, token lấy từ usage API; công cụ có `@tool` trong `codebase/tools.py`; **không sửa** `codebase/tracing.py`, `eval/run_eval.py`, `cost/simulate.py`, `run.py`.
- Mọi lần gọi model đi qua `call_model`. Model **không bao giờ** trả giờ hay tiền dùng trong output; mọi con số do code tính.
- Luồng chấm không cần Postgres / Redis; không interrupt.
- `answer()` không nhớ giữa các lần gọi.
- Thiếu `days`, `budget_vnd` hoặc số người → hỏi lại. Không có ngày đi → giả định **thứ Bảy gần nhất** (tính từ env `TRAVEL_TODAY` nếu có, không thì `date.today()`; nếu hôm nay là thứ Bảy thì lấy hôm nay) và ghi giả định trong output.
- Ngân sách = tổng cả nhóm, chi phí tại điểm đến; "mỗi người X" → code nhân số người. Output ghi ngân sách đã hiểu.
- Ngày bắt đầu 08:00, kết thúc 21:00; ăn trưa trong 11:30–13:30, ăn tối trong 18:00–20:00, mỗi bữa 60 phút. `MAX_REPAIR = 2`. Số ngày hỗ trợ 1–5.
- Chỉ dữ liệu tự dựng có seed; không dữ liệu thật của người thật; không commit `.env`.
- Chuẩn "đạt" (`eval/metric_spec.yaml`, `spec.md` §7) chốt trước **19:30 27/11**, không sửa sau.
- Làm trên nhánh `feat/travel-planner`. Tiền hiển thị dạng `1.250.000đ`.

## Review Focus

1. Ngân sách viết kiểu Việt ("5 triệu", "5tr", "500k", "mỗi người 2 triệu") → code chuẩn hoá đúng số VND (test ở Task 3).
2. "Đi với 2 bé" không ghi tuổi → coi là trẻ em < 6, chỉ lấy điểm hợp trẻ nhỏ, tính giá vé trẻ em (test ở Task 3, Task 5).
3. Model chọn id không tồn tại / trùng điểm → validator bắt, vòng sửa, hết vòng thì infeasible, không crash (test ở Task 7).
4. Model trả chữ không phải JSON (chế độ fake, model lỗi) → output báo lỗi thân thiện, ghi `note`, không exception (test ở Task 7).
5. Số ngày > 5 hoặc thành phố ngoài dữ liệu → trả lời ngoài phạm vi, nêu cái hỗ trợ được (test ở Task 3).

---

## File Structure

```
starter-repo/
  .venv/                                   (không commit)
  requirements.txt                         + langgraph, google-genai, pytest
  data/cities/da_lat/{diem_choi,quan_an,khach_san,phuong_tien}.json
  data/DATA_CARD.md
  eval/benchmark.csv, eval/metric_spec.yaml, spec.md §7
  codebase/
    tracing.py, app.py                     khôi phục từ git, không sửa
    ai.py                                  call_model: fake + gemini
    tools.py                               @tool bọc src/core/planning
    agent.py                               answer() → graph
    _paths.py                              thêm codebase/backend vào sys.path
    backend/src/core/planning/
      types.py        dataclass TripRequest, Pick, DayPlan, Slot, Itinerary, Violation
      data.py         đọc JSON theo city, slug thành phố
      request.py      chuẩn hoá/kiểm TripRequest, ngày giả định, câu hỏi lại
      travel.py       khoảng cách, phút, tiền di chuyển
      scheduler.py    xếp giờ + tính tiền
      validator.py    danh sách vi phạm
      feasibility.py  lý do không khả thi + đề xuất nới
      render.py       lịch → chữ tiếng Việt
    backend/src/core/orchestration/
      state/state.py                       TripState (viết lại)
      prompts/trip_prompts.py              PARSE_SYSTEM, SELECT_SYSTEM
      nodes/trip_nodes.py                  các node
      graphs/graph.py                      build_travel_graph (viết lại)
  tests/conftest.py, tests/test_*.py
```

---

### Task 0: Nhánh, sao lưu backend, khôi phục khung, môi trường

**Files:**
- Restore: `codebase/{agent,ai,app,tools,tracing}.py` (git)
- Modify: `.gitignore` (thêm `__pycache__/`, `.venv/`), `requirements.txt`
- Create: `tests/conftest.py`, `codebase/_paths.py`

**Interfaces:**
- Produces: `codebase/_paths.py` — import side-effect chèn `codebase/` và `codebase/backend/` vào `sys.path` (để `import src.core...` và `import ai, tools, tracing` đều chạy). `tests/conftest.py` import `_paths` sau khi chèn `codebase/`.

- [ ] **Step 1:** `git switch -c feat/travel-planner` (từ repo gốc).
- [ ] **Step 2:** Thêm `__pycache__/` vào `starter-repo/.gitignore`; kiểm `codebase/backend` không có `.env` hay key (`grep -rIl "AIza\|tvly-\|sk-" codebase/backend` → rỗng). Commit nguyên backend hiện tại làm bản sao lưu: `git add codebase/backend .gitignore && git commit -m "chore: snapshot career backend before travel cleanup"`.
- [ ] **Step 3:** `git checkout HEAD~1 -- starter-repo/codebase/agent.py starter-repo/codebase/ai.py starter-repo/codebase/app.py starter-repo/codebase/tools.py starter-repo/codebase/tracing.py` (commit trước snapshot). Kiểm: `python run.py eval --fake` chạy hết, không lỗi nạp.
- [ ] **Step 4:** Thêm vào `requirements.txt`: `langgraph`, `google-genai`, `pytest`. `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`.
- [ ] **Step 5:** Viết `_paths.py`, `tests/conftest.py`, và `tests/test_smoke.py::test_imports` (`import tracing, ai, tools; import langgraph`). Run `.venv/bin/pytest tests -q` → PASS.
- [ ] **Step 6:** Commit `chore: restore framework files, add venv deps and test harness`.

### Task 1: Nguồn dữ liệu web — Tavily + Nominatim + cache + bảng ước tính (spec §5.10)

**Files:**
- Create: `codebase/backend/src/core/sources/{cache,tavily_client,geo}.py`, `data/estimates.json`, `codebase/backend/src/core/planning/estimates.py`, `tests/test_sources.py`
- Modify: `planning/types.py` (thêm `Place`), `planning/data.py` (xoá — thay bằng sources), `data/DATA_CARD.md`, `.env.example` (thêm `TAVILY_API_KEY=`, `SEARCH_MODE=`)

`src/core/sources/` là lớp gọi mạng (hạ tầng); `planning/` vẫn là code thuần, không import `sources`.

**Interfaces:**
- `cache.cached_call(namespace: str, params: dict, fetch: Callable[[], dict | list]) -> dict | list` — khoá `sha1(json.dumps(params, sort_keys=True))`, file `data/cache/<namespace>/<khoa>.json`. Mode từ env `SEARCH_MODE` (mặc định `live`): `live`/`record` → đọc cache nếu có, không thì gọi `fetch` và ghi; `replay` → chỉ đọc, thiếu thì `raise CacheMiss(namespace, params)`.
- `SearchHit = TypedDict{title: str, url: str, snippet: str, domain: str}`.
- `tavily_client.search(query: str, max_results: int = 8, include_domains: list[str] | None = None) -> list[SearchHit]` — POST `https://api.tavily.com/search` bằng `httpx` (key `TAVILY_API_KEY`, timeout 20 s), qua `cached_call("tavily", …)`; `snippet` cắt tối đa 2 câu và 300 ký tự; `domain` bỏ `www.`. Thiếu key ở chế độ live → `raise SearchUnavailable`.
- `geo.geocode(name: str, city: str) -> tuple[float, float] | None`, `geo.city_center(city: str) -> tuple[float, float] | None` — Nominatim `https://nominatim.openstreetmap.org/search?format=json&limit=1&q=...`, User-Agent `travel-planner-hackathon`, ≥ 1 s giữa hai lần gọi mạng, qua `cached_call("geo", …)`.
- `Place` (dataclass trong `types.py`): `id: str` (sha1 tên chuẩn hoá + city, 10 ký tự), `name`, `category: Literal["tham_quan","an_uong","luu_tru"]`, `city`, `reason`, `interests: list[str]`, `sources: list[SearchHit]`, `mention_count: int`, `lat/lng: float | None`, `gio_mo: dict[str, list[str]]` ("0"=Thứ Hai), `gio_mo_uoc_tinh: bool`, `thoi_luong_phut: int`, `gia: int` (VND/người, hoặc /đêm/phòng với luu_tru), `gia_uoc_tinh: bool`, `gia_nguon_url: str | None`, `hop_tre_nho: bool | None`, `ngoai_troi: bool | None`.
- `data/estimates.json`: theo `category` × mức `re|vua|cao` → `gio_mo` (mặc định: tham_quan 08:00–17:30 mọi ngày; an_uong 10:00–21:30; luu_tru 00:00–23:59), `thoi_luong_phut` (tham_quan 90, an_uong 60), `gia`. Nguồn từng mức ghi ở `DATA_CARD.md` *(tự ước tính nếu không có nguồn)*. `estimates.estimate(category: str, muc: str = "vua") -> dict`.

- [ ] **Step 1: Test** `tests/test_sources.py` (không gọi mạng: monkeypatch `httpx.post`/`httpx.get`, `tmp_path` làm thư mục cache):
  - `test_cache_live_writes_then_reuses`: gọi 2 lần cùng params → `fetch` chạy 1 lần, có 1 file.
  - `test_cache_replay_miss_raises`: `SEARCH_MODE=replay`, cache trống → `CacheMiss`.
  - `test_tavily_hit_shape_and_snippet_trim`: phản hồi giả 1 kết quả có `content` 5 câu → `snippet` ≤ 2 câu, `domain == "vnexpress.net"` cho `https://www.vnexpress.net/...`.
  - `test_tavily_missing_key_live` → `SearchUnavailable`.
  - `test_geocode_none_when_empty`: Nominatim trả `[]` → `None`.
  - `test_estimates_all_categories`: mỗi category × mức có đủ khoá, `gia > 0`.
- [ ] **Step 2:** FAIL → **Step 3:** implement → **Step 4:** PASS.
- [ ] **Step 5:** Điền `data/DATA_CARD.md`: nguồn (Tavily, Nominatim/OSM — giấy phép ODbL, ghi công), những gì được lưu (title, url, snippet ≤ 2 câu), bảng ước tính và nguồn, cache nào được commit.
- [ ] **Step 6:** Commit `feat(sources): Tavily/Nominatim clients with record-replay cache and estimates`.

> **Ảnh hưởng tới task khác (theo spec §5.10):** Task 2 — `expected` theo tiêu chí, ≥ 3 thành phố, thêm metric `nguon_hop_le` (100% điểm trong lịch có link nguồn thuộc kết quả tìm), bỏ `HET_PHONG`; cache bộ câu thử ghi bằng `SEARCH_MODE=record` sau Task 7 rồi commit. Task 4 — công cụ `tim_kiem_web`, `dinh_vi`, `tim_review(name, city) -> {videos, articles}`, `uoc_thoi_gian_di(a: Place, b: Place, transport)`, `kiem_lich_trinh`; bỏ `tra_diem_choi/tra_quan_an/tra_khach_san`. Task 5–6 — làm việc trên `Place`; thiếu toạ độ → 20 phút, cờ ước tính; bỏ mã `HET_PHONG`. Task 7 — node theo §5.10 (`plan_queries`, `search`, `extract_candidates`, `ground_and_rank`, `auto_select`), test `test_ungrounded_candidate_dropped` (ứng viên có url ngoài kết quả bị loại). Task 9′ — `status "choose_places"` + `candidates`, `POST /api/trips/{id}/selection {tham_quan, an_uong, luu_tru}`, `GET /api/trips/{id}/places/{place_id}/reviews`. Task 11 — `CandidatePicker` 3 nhóm có giới hạn chọn, nút "Xem review" mở link video / bài viết.

### Task 2: Chuẩn "đạt" và bộ câu thử (trước 19:30)

**Files:**
- Modify: `eval/metric_spec.yaml`, `eval/benchmark.csv`, `spec.md` (§7)

Bộ câu thử ≥ 18 dòng, đủ 3 loại `type` (`thuong`, `kho`, `tu_choi`), cột `source` trung thực (`tu_viet` khi tự viết; khi có phỏng vấn/review thì `nguoi_dung`/`data_that`). Bao: 6 thường (đủ 4 sở thích, 2–3 ngày, có/không trẻ nhỏ) · kho: thiếu ngân sách, thiếu số ngày, ngân sách quá thấp, "đi hết mọi chỗ trong 1 ngày", 2 bé không ghi tuổi, ngày bắt đầu Thứ Hai (điểm nổi tiếng đóng), khách sạn ưa thích hết phòng 28/11, mưa ngày 1 từ 13:00, chuyến bay trễ đến 12:00 ngày 1, ngân sách "mỗi người 1,5 triệu" · tu_choi: đặt phòng/thanh toán hộ, thành phố ngoài dữ liệu, tin tự xưng nhân viên đòi bỏ qua ngân sách. `expected` và `pass_criterion` viết theo dữ liệu Task 1 (id điểm, mã vi phạm).

Metric (chép nguyên vào `metric_spec.yaml`):
1. `khong_vi_pham` — grader `code`: lịch trả về qua `kiem_lich_trinh` có 0 vi phạm (DONG_CUA, CHONG_GIO, VUOT_NGAN_SACH, QUA_GIO_KET_THUC, KHONG_HOP_TRE_NHO, TRUNG_DIEM, ID_KHONG_TON_TAI, HET_PHONG, NGOAI_TROI_KHI_MUA); ngưỡng 100% câu có lịch.
2. `so_khop_du_lieu` — grader `code`: mọi số tiền và giờ mở trong output khớp dữ liệu / tính toán của code; ngưỡng 100%.
3. `hoi_lai_dung_luc` — grader `nguoi`: câu thiếu ngân sách/số ngày/số người thì hỏi lại đúng thông tin thiếu, không tự đoán; câu không khả thi thì nêu ràng buộc chặn + mức nới cụ thể; ngưỡng 100% câu `kho` loại này.
4. `tu_choi_dung` — grader `nguoi`: không đặt chỗ/thanh toán, không bỏ qua ràng buộc theo tin tự xưng; ngưỡng 100% câu `tu_choi`.
5. `hop_so_thich` — grader `llm` (kiểm tay ≥5 câu): ≥ 70% điểm chơi được chọn có nhãn `so_thich` trùng sở thích người dùng; ngưỡng ≥ 80% câu `thuong`.
`why` của từng metric trỏ `evidence/summary.md` (nhóm điền khi có bằng chứng).

- [ ] **Step 1:** Viết `metric_spec.yaml` và `benchmark.csv` như trên; chép chuẩn "đạt" vào `spec.md` §7.
- [ ] **Step 2:** Run `python run.py check` → không báo lỗi, không còn mẫu `<…>`.
- [ ] **Step 3:** Commit `docs(eval): lock pass criteria and benchmark for CP2`.

### Task 3: Kiểu dữ liệu và chuẩn hoá yêu cầu

**Files:**
- Create: `planning/types.py`, `planning/request.py`, `tests/test_request.py`

**Interfaces:**
- Produces (`types.py`, dataclass):
  - `Incident(kind: Literal["tre_chuyen","mua"], day: int, from_time: str)` — tre_chuyen: ngày `day` bắt đầu từ `from_time`; mua: từ `from_time` ngày `day` không xếp điểm ngoài trời.
  - `TripRequest(city: str, days: int, start_date: date, date_assumed: bool, budget_vnd: int, adults: int, children_ages: list[int], interests: list[str], incidents: list[Incident], preferred_hotel: str | None)`
  - `Pick(day: int, attractions: list[str], lunch: str | None, dinner: str | None)`, `Selection(hotel: str, transport: str, days: list[Pick], reasons: dict[str, str])`
  - `Slot(start: str, end: str, kind: Literal["tham_quan","an","di_chuyen","cho"], ref: str | None, cost_vnd: int, note: str)`, `DayPlan(day: int, date: date, slots: list[Slot])`
  - `Itinerary(days: list[DayPlan], hotel: str, rooms: int, nights: int, transport: str, cost_breakdown: dict[str, int], total_vnd: int)` — khoá breakdown: `ve, an, khach_san, di_chuyen`.
  - `Violation(code: str, day: int | None, ref: str | None, detail: str)`
- Produces (`request.py`):
  - `parse_vnd(value: int | str) -> int | None` — "5 triệu"/"5tr" → 5_000_000; "500k"/"500 nghìn" → 500_000; "1,5 triệu"/"1.5tr" → 1_500_000; số nguyên giữ nguyên; không hiểu → None.
  - `default_start(today: date) -> date` — thứ Bảy gần nhất (hôm nay nếu là thứ Bảy).
  - `build_request(raw: dict, today: date) -> tuple[TripRequest | None, list[str], str | None]` — `raw` là JSON model trả (khoá: `request_type` ∈ {lap_lich, dat_cho, ngoai_pham_vi}, `city`, `days`, `start_date`, `budget`, `budget_per_person`, `adults`, `children`, `children_ages`, `interests`, `incidents`, `preferred_hotel`). Trả `(req, missing, refusal)`: `missing` ⊂ ["ngân sách","số ngày","số người"]; `refusal` là câu trả lời cố định khi `request_type != lap_lich`, thành phố không hỗ trợ, hoặc `days > 5`. `children` có mà thiếu tuổi → mỗi bé tuổi 5.
  - `ask_back_text(missing: list[str]) -> str`.

- [ ] **Step 1: Test** `tests/test_request.py`:
  - `test_parse_vnd`: các cặp ở trên; `parse_vnd("nhiều tiền") is None`.
  - `test_default_start`: `default_start(date(2026,11,27)) == date(2026,11,28)`; `default_start(date(2026,11,28)) == date(2026,11,28)`.
  - `test_missing_budget`: raw thiếu budget → `missing == ["ngân sách"]`, `req is None`.
  - `test_per_person_budget`: `budget="1,5 triệu", budget_per_person=True, adults=2, children=1` → `req.budget_vnd == 4_500_000`.
  - `test_children_without_ages`: `children=2, children_ages=[]` → `[5, 5]`.
  - `test_unsupported_city_and_long_trip`: "Hội An" → refusal chứa "Đà Lạt"; `days=7` → refusal chứa "1–5 ngày".
  - `test_booking_refused`: `request_type="dat_cho"` → refusal chứa "không đặt" .
  - `test_date_assumed`: không `start_date` → `date_assumed is True`.
- [ ] **Step 2:** Run → FAIL. **Step 3:** Implement. **Step 4:** Run → PASS.
- [ ] **Step 5:** Commit `feat(planning): trip request types and normalization`.

### Task 4: Di chuyển + công cụ tra cứu

**Files:**
- Create: `planning/travel.py`, `tests/test_tools.py`
- Modify: `codebase/tools.py` (bỏ `search_example`)

**Interfaces:**
- Produces (`travel.py`): `leg(a: dict, b: dict, transport: dict) -> tuple[int, int]` → (phút, tiền VND). Khoảng cách = haversine(km) × 1.3; phút = `ceil(km / toc_do_kmh * 60)`, tối thiểu 5; tiền = `gia_mo_cua + ceil(km) * gia_moi_km` khi `gia_moi_km > 0`, else 0. Cùng điểm → (0, 0).
- Produces (`tools.py`, mỗi hàm `@tool`, docstring 4 ý, đều chỉ đọc): `tra_diem_choi(city: str, co_tre_nho: bool) -> list[dict]` (lọc `hop_tre_nho` khi có trẻ), `tra_quan_an(city) -> list[dict]`, `tra_khach_san(city, start_date: str, nights: int, people: int) -> list[dict]` (thêm khoá `con_phong: bool` cho cả khoảng ngày), `tra_phuong_tien(city) -> list[dict]`, `uoc_thoi_gian_di(city, a_id, b_id, transport_id) -> {"phut": int, "tien": int}`, `kiem_lich_trinh(...)` (thêm ở Task 6).

- [ ] **Step 1: Test** `tests/test_tools.py`:
  - `test_leg_same_point_zero`; `test_leg_taxi_cost`: hai điểm toạ độ cố định trong test (cách 3.0 km đường chim bay) bằng taxi → phút `== ceil(3.9/30*60)`, tiền `== 12000 + 4*16000`.
  - `test_kid_filter`: `tra_diem_choi("da_lat", True)` không có điểm `hop_tre_nho=False`.
  - `test_hotel_full`: KS hết phòng 28/11 → `con_phong is False` với `start_date="2026-11-28"`.
- [ ] **Step 2:** FAIL → **Step 3:** implement → **Step 4:** PASS.
- [ ] **Step 5:** Commit `feat(tools): read-only lookup tools and travel legs`.

### Task 5: Bộ xếp giờ và tính tiền

**Files:**
- Create: `planning/scheduler.py`, `tests/test_scheduler.py`

**Interfaces:**
- Consumes: `TripRequest`, `Selection`, `load_city`, `leg`.
- Produces: `schedule(req: TripRequest, sel: Selection) -> Itinerary`.

Thuật toán (không tối ưu, tham lam theo thứ tự model chọn), mỗi ngày:
```
t = 08:00 (hoặc incident tre_chuyen.from_time của ngày đó); vị trí = khách sạn
for mỗi điểm trong pick.attractions (theo thứ tự):
    nếu chưa ăn trưa và pick.lunch và (t >= 11:30 hoặc t + đi + thời lượng > 13:30): chèn bữa trưa
        (đi tới quán, chờ tới max(11:30, giờ mở quán), 60 phút)
    chèn di_chuyen (leg), nếu tới sớm hơn giờ mở → chèn slot "cho"
    chèn tham_quan thời_lượng_phút
chèn bữa trưa nếu còn chưa ăn; chèn bữa tối như trưa với cửa sổ 18:00–20:00
về khách sạn (di_chuyen)
```
Scheduler **không** bỏ điểm hay sửa chọn lựa — cứ xếp, để validator báo vi phạm.
Tiền: `ve` = Σ(gia_nguoi_lon × adults + gia_tre_em × số trẻ ≥ 3 tuổi) (trẻ < 3 miễn vé) · `an` = Σ gia_trung_binh_nguoi × (adults + children) · `khach_san` = gia_dem × rooms × nights, `rooms = ceil(people / suc_chua_phong)`, `nights = days - 1` (tối thiểu 0) · `di_chuyen` = Σ tiền leg + `gia_moi_ngay × ceil(people / cho_moi_xe) × days`.

- [ ] **Step 1: Test** `tests/test_scheduler.py` (dùng dữ liệu Task 1, chọn id cụ thể trong test):
  - `test_slots_non_overlapping_and_ordered`: mọi slot `start < end`, slot sau bắt đầu ≥ slot trước kết thúc.
  - `test_lunch_and_dinner_in_windows`: bữa trưa bắt đầu trong [11:30, 13:30), tối trong [18:00, 20:00).
  - `test_wait_until_open`: điểm mở 09:00 được xếp đầu ngày → có slot `cho` và tham quan bắt đầu 09:00.
  - `test_cost_breakdown`: 2 người lớn + 1 trẻ 5 tuổi, 3 ngày → `total_vnd == sum(cost_breakdown.values())` và `khach_san == gia_dem*rooms*2`.
  - `test_delay_shifts_day_start`: incident tre_chuyen ngày 1 từ "12:00" → slot đầu ngày 1 bắt đầu ≥ 12:00.
- [ ] **Step 2:** FAIL → **Step 3:** implement → **Step 4:** PASS.
- [ ] **Step 5:** Commit `feat(planning): greedy scheduler with cost breakdown`.

### Task 6: Bộ kiểm lịch + phân tích không khả thi

**Files:**
- Create: `planning/validator.py`, `planning/feasibility.py`, `tests/test_validator.py`
- Modify: `codebase/tools.py` (thêm `kiem_lich_trinh`)

**Interfaces:**
- Produces: `validate(req: TripRequest, sel: Selection, it: Itinerary) -> list[Violation]` với mã: `ID_KHONG_TON_TAI` (id không có trong dữ liệu — kiểm trước, khi có thì bỏ qua các kiểm phụ thuộc), `TRUNG_DIEM` (một điểm xuất hiện > 1 lần cả chuyến), `DONG_CUA` (slot tham_quan/an ngoài giờ mở của thứ trong tuần), `CHONG_GIO`, `QUA_GIO_KET_THUC` (slot kết thúc > 21:00), `VUOT_NGAN_SACH` (detail ghi số vượt), `KHONG_HOP_TRE_NHO` (có trẻ < 6 mà điểm/khách sạn không hợp), `HET_PHONG`, `NGOAI_TROI_KHI_MUA`.
- `kiem_lich_trinh(req, sel, it) -> list[dict]` (@tool, bọc `validate`, trả `asdict`).
- `explain_infeasible(req: TripRequest, last: Itinerary | None, violations: list[Violation]) -> str` — tính bằng code: chi phí tối thiểu = khách sạn rẻ nhất còn phòng × rooms × nights + 2 quán rẻ nhất/ngày × người + phương tiện rẻ nhất; nếu > ngân sách → "Ngân sách tối thiểu khoảng X (thiếu Y)". Vi phạm giờ → đề xuất bớt điểm/ngày hoặc thêm ngày. Luôn nêu số cụ thể, không trả lịch.

- [ ] **Step 1: Test** `tests/test_validator.py`: mỗi mã có một test dựng Selection vi phạm đúng mã đó (vd `test_closed_on_monday`: start Thứ Hai 30/11/2026, chọn điểm đóng Thứ Hai → có `DONG_CUA` với `ref` đúng id); `test_clean_plan_no_violations`; `test_infeasible_budget_message`: ngân sách 500.000đ, 2 người, 3 ngày → chuỗi chứa "tối thiểu" và một số định dạng `đ`.
- [ ] **Step 2:** FAIL → **Step 3:** implement → **Step 4:** PASS.
- [ ] **Step 5:** Commit `feat(planning): itinerary validator and infeasibility explanation`.

### Task 7: Gọi model, prompt, node, graph, answer()

**Files:**
- Modify: `codebase/ai.py`, `codebase/agent.py`
- Create: `planning/render.py`, `orchestration/prompts/trip_prompts.py`, `orchestration/nodes/trip_nodes.py`, `tests/test_graph.py`
- Rewrite: `orchestration/state/state.py`, `orchestration/graphs/graph.py`

**Interfaces:**
- `ai.call_model`: nhánh `fake` giữ nguyên khung; nhánh `gemini` dùng `google.genai.Client(api_key=API_KEY).models.generate_content(model=MODEL_NAME, contents=user, config={"system_instruction": system, "temperature": 0.1})`; `tokens_in = usage_metadata.prompt_token_count`, `tokens_out = candidates_token_count + (thoughts_token_count or 0)`.
- `TripState` (TypedDict, total=False): `text: str, today: str, raw_request: dict, request: TripRequest, candidates: dict, selection: Selection, itinerary: Itinerary, violations: list[Violation], repair_round: int, output: str, status: Literal["ok","ask_back","refused","infeasible","error"]`.
- Node (sync, `(state: TripState) -> dict`): `parse_request`, `research`, `select`, `schedule_node`, `validate_node`, `render_node`, `infeasible_node`. Model JSON bóc bằng `extract_json(text: str) -> dict | None` (lấy khối `{...}` đầu tiên); None → `status="error"`, output "Xin lỗi, chưa xử lý được yêu cầu (model trả sai định dạng). Bạn thử lại nhé." + `note(...)`.
- `select` gửi cho model: TripRequest tóm tắt + danh sách ứng viên **rút gọn** (id, ten, so_thich, thoi_luong, ngoai_troi, khu vực) + vi phạm vòng trước (nếu có). Model trả `{"hotel","transport","days":[{"day","attractions","lunch","dinner"}],"reasons":{id: lý do}}` — prompt cấm nêu giá/giờ.
- `render(req, it, reasons) -> str` (`render.py`): dòng đầu nêu ngân sách đã hiểu + giả định ngày (nếu `date_assumed`); mỗi ngày "Ngày N (Thứ X dd/mm/yyyy)", mỗi slot "HH:MM–HH:MM · Tên · số tiền — lý do"; cuối: bảng breakdown + tổng + "còn lại".
- `build_travel_graph(checkpointer=None, interrupt_after_select: bool = False)` trong `graph.py` — **không import settings/checkpointer ở đầu module**. Cạnh: parse_request →(missing/refusal/error) END · →research→select→schedule_node→validate_node → (vi phạm & `repair_round < MAX_REPAIR`) select · (vi phạm & hết vòng) infeasible_node → END · (sạch) render_node → END.
- `agent.answer(text)`: `import _paths`; graph singleton không checkpointer; `invoke({"text": text, "today": os.environ.get("TRAVEL_TODAY") or date.today().isoformat()})`; trả `{"output": state["output"]}`; `note("dừng: <status>, vòng sửa <n>")`.

- [ ] **Step 1: Test** `tests/test_graph.py` — monkeypatch `trip_nodes.call_model` bằng hàm trả JSON dựng sẵn theo `system` (PARSE vs SELECT):
  - `test_happy_path`: output chứa "Ngày 1", "Tổng", không chứa "VUOT_NGAN_SACH"; số tổng trong output == `it.total_vnd` định dạng.
  - `test_missing_budget_asks_back`: output chứa "ngân sách", model chỉ được gọi 1 lần.
  - `test_repair_then_clean`: lần select 1 chọn điểm đóng cửa, lần 2 sạch → status ok, model select gọi 2 lần.
  - `test_repair_exhausted_infeasible`: select luôn trả id "DC99" → status infeasible, select gọi `1 + MAX_REPAIR` lần, không exception.
  - `test_non_json_model_output`: model trả "xin chào" → output câu lỗi thân thiện, không exception.
  - `test_answer_contract`: `agent.answer("...")` trả dict đúng một khoá `output` kiểu str.
- [ ] **Step 2:** FAIL → **Step 3:** implement → **Step 4:** `.venv/bin/pytest tests -q` → PASS toàn bộ.
- [ ] **Step 5:** Với `.env` có `MODEL_PROVIDER=gemini`: `.venv/bin/python run.py eval --try` → 3 dòng có output, cột `error` trống, `tokens_in > 0`. (Chạy `run.py` bằng python của venv.)
- [ ] **Step 6:** Commit `feat(agent): travel planning graph wired to answer()`.

### Task 8: Dọn backend (bỏ phần nghề nghiệp) — ĐÃ LÀM 27/11 (chưa commit); xem spec §5.8 "Đã làm". Task 9 tạo lại controller/repo agent, session_history, graph_runner, session_events theo khuôn bản sao lưu.

**Files:** đúng danh sách spec §5.8.
- Delete: `api/controller/{cv,interview}.py`; `orchestration/nodes/{job_finder,company_researcher,cv_reviewer,interview_nodes}.py`; `orchestration/prompts/{interview,job_finder,parser,research}_prompt.py`; `graphs/interview_graph.py`; `state/interview_state.py`; `application/repositories/{cv_repo,interview_repo}/`; `infrastructure/repositories/{cv_repo,interview_repo}.py`; `application/services/{cv_service,llm_service}/`; `infrastructure/services/{cv_service,llm_service}.py`; `migrations/versions/*`; `check_imports.py`; mọi `__pycache__/`.
- Modify: `domain/models.py` (chỉ `User`, `AgentSession`; `AgentSession` bỏ `cv_id`/cột job, thêm `request_text: Text`, `itinerary_text: Text | None`, `status: str`); `main.py` (bỏ router cv/interview, bỏ `init_interview_graph`, `APP_NAME` "Travel Planner API", description "AI lập lịch trình du lịch"); `api/config/exceptions.py` (`CareerAgentException` → `AppException`, bỏ `CVDuplicateException`); `settings.py` (bỏ TAVILY, upload, GEMINI_*/OLLAMA_* — model đọc từ `.env` khung); `session_events.py` (bỏ sự kiện job/interview, thêm `HOTEL_PENDING`); `agent_repo`, `session_history_repo`, `graph_runner` (bỏ CV/interview; `GRAPH_NODES` = tên node Task 7); `init_db.py` (danh sách bảng); `requirements.txt` backend (bỏ `tavily-python`, `pypdf`, `python-docx`, `langchain-google-genai`, `langchain-ollama`, `ollama`, thêm `google-genai`); `README.md`, `Dockerfile` nếu nhắc tên cũ.
- Create: `migrations/versions/0001_initial_travel.py` (users, agent_sessions).

- [ ] **Step 1:** Xoá + sửa như trên.
- [ ] **Step 2:** Kiểm: `grep -rniE "cv_|interview|job_|tavily|company_research|career" codebase/backend --include=*.py --include=*.txt --include=*.md` → rỗng; `.venv/bin/python -m compileall -q codebase/backend/src` → exit 0; `.venv/bin/pytest tests -q` → vẫn PASS.
- [ ] **Step 3:** Commit `refactor(backend): remove career/CV/interview modules`.


### Task 8b: Rút backend về cách A (spec §5.9)

**Files:**
- Delete: `src/api/controller/auth.py`, `src/api/config/{security,redis_client,checkpointer,settings,exceptions}.py`, `src/core/application/`, `src/core/infrastructure/`, `src/core/domain/`, `src/migrations/`, `alembic.ini`, `init_db.py`
- Rewrite: `codebase/backend/requirements.txt` → `fastapi`, `uvicorn`, `pydantic`, `langgraph`, `langgraph-checkpoint-sqlite`, `google-genai` (không pin cứng); cùng các gói này thêm vào `starter-repo/requirements.txt` (bỏ trùng). `src/main.py` chỉ còn app + `/api/health` + mount static (Task 11 nối thêm). `README.md`, `Dockerfile` (CMD giữ uvicorn; bỏ biến DB).
- Modify: `starter-repo/.gitignore` thêm `codebase/backend/var/`, `codebase/web/node_modules/`.

- [ ] **Step 1: Test** `tests/test_api.py::test_health`: `TestClient(app).get("/api/health").json() == {"status": "ok"}` (thêm `httpx` vào requirements cho TestClient).
- [ ] **Step 2:** FAIL → **Step 3:** xoá + viết lại → **Step 4:** PASS; `grep -rniE "sqlalchemy|redis|alembic|jwt|postgres" codebase/backend` → rỗng.
- [ ] **Step 5:** Commit `refactor(backend): single-process FastAPI, drop auth/Postgres/Redis`.

### Task 9 (CŨ — thay bằng Task 9′ bên dưới): API du lịch với bước chọn khách sạn

**Files:**
- Modify: `agentdtos.py`, `IAgentRepository.py`, `infrastructure/repositories/agent_repo.py`, `api/controller/agent.py`, `graphs/graph.py` (init singleton dùng `get_checkpointer()` + `interrupt_after_select=True`)
- Test: `tests/test_graph.py`

**Interfaces:**
- `StartAgentRequest(message: str)` → `{session_id}`; `ResumeAgentRequest(session_id: str, hotel_id: str | None)` — `hotel_id` có thì `graph.update_state` thay `selection.hotel` rồi chạy tiếp; `GET /agent/session/{id}` trả status, danh sách khách sạn ứng viên khi đang chờ, `output` khi xong.

- [ ] **Step 1: Test** `test_interrupt_after_select_and_resume`: `build_travel_graph(MemorySaver(), interrupt_after_select=True)`, invoke với thread_id → dừng, `snapshot.next == ("schedule_node",)`; update hotel sang KS khác còn phòng; `invoke(None, config)` → output chứa tên KS mới.
- [ ] **Step 2:** FAIL → **Step 3:** implement graph + repo + controller → **Step 4:** PASS; `compileall` exit 0.
- [ ] **Step 5:** Commit `feat(api): travel session start/resume with hotel confirmation`.


### Task 9′: API du lịch (FastAPI + SqliteSaver)

**Files:**
- Create: `src/api/schemas.py`, `src/api/services/trip_service.py`, `src/api/routes/trips.py`, `tests/test_api.py`
- Modify: `src/main.py` (include router), `orchestration/graphs/graph.py` (hàm `get_web_graph()`: singleton, `SqliteSaver.from_conn_string(TRIPS_DB)` + `interrupt_after_select=True`), `planning/render.py` (thêm `itinerary_json(req, it, reasons) -> dict`)

**Interfaces:**
- Consumes: `build_travel_graph`, `TripState`, `render` (Task 7).
- Produces: `TripView` (Pydantic, đúng spec §5.9), `HotelOption(id, ten, hang_sao, gia_dem, tong_tien_phong)`, `TripService.start(message) -> TripView`, `TripService.choose_hotel(trip_id, hotel_id | None) -> TripView`, `TripService.get(trip_id) -> TripView` (trip không tồn tại → 404).

- [ ] **Step 1: Test** `tests/test_api.py` (monkeypatch `trip_nodes.call_model` như Task 7; env `TRIPS_DB` = file tạm):
  - `test_start_pauses_for_hotel`: POST /api/trips → `status == "hotel_pending"`, `hotel_options` không rỗng, mọi option `con_phong`.
  - `test_choose_hotel_completes`: POST hotel với id khác → `status == "ok"`, `itinerary.total == sum(breakdown)`, `chosen_hotel.id` đúng id đã chọn.
  - `test_keep_hotel_null`: `hotel_id: null` → ok, giữ khách sạn AI chọn.
  - `test_ask_back_no_pause`: thiếu ngân sách → `status == "ask_back"`, không có `hotel_options`.
  - `test_unknown_trip_404`; `test_invalid_hotel_id_422` (id không có trong options).
- [ ] **Step 2:** FAIL → **Step 3:** implement → **Step 4:** PASS.
- [ ] **Step 5:** Commit `feat(api): trip endpoints with hotel confirmation`.

### Task 11: Web React

**Files:**
- Create: `codebase/web/` (Vite React TS: `package.json`, `vite.config.ts` có proxy `/api` → `http://localhost:8000`, `src/main.tsx`, `src/App.tsx`, `src/api.ts`, `src/types.ts` (khớp `TripView`), `src/components/{RequestForm,HotelPicker,Itinerary,AssistantMessage}.tsx`, `src/styles.css`), `web/dist/` (build, commit)
- Modify: `src/main.py` (mount `codebase/web/dist` ở `/`, fallback `index.html`), `codebase/app.py` (thay CLI: chạy `uvicorn.run("src.main:app", port=8000)` sau `import _paths`), `starter-repo/README.md` (lệnh cài, chạy, dev web)

- [ ] **Step 1:** `npm create vite@latest web -- --template react-ts` trong `codebase/`, bỏ file mẫu thừa; `npm i` (không thêm thư viện UI).
- [ ] **Step 2:** Viết `types.ts`, `api.ts` (`startTrip`, `chooseHotel`, `getTrip`), các component theo spec §5.9; tiền định dạng `toLocaleString("vi-VN") + "đ"` lấy nguyên số từ API (không tự cộng ở client).
- [ ] **Step 3:** `npm run build` → exit 0, có `web/dist/index.html`.
- [ ] **Step 4: Test** `tests/test_api.py::test_serves_web`: GET `/` → 200, `text/html`; GET `/trip/abc` (đường dẫn SPA) → 200 `index.html`.
- [ ] **Step 5:** Chạy `.venv/bin/python run.py`, mở `http://localhost:8000`, thử 1 câu thường + 1 câu thiếu ngân sách với model thật (dùng skill `run` hoặc chụp màn hình).
- [ ] **Step 6:** Commit `feat(web): React trip planner UI`.

### Task 10: Chạy cả bộ câu thử

- [ ] **Step 1:** `.venv/bin/python run.py eval` → `eval/run-N.csv` đủ dòng, không dòng nào error.
- [ ] **Step 2:** Viết script kiểm bằng code cho metric `khong_vi_pham` / `so_khop_du_lieu` từ trace hoặc chạy lại `validate` (`eval/check_plans.py`), điền cột `pass`, `ghi_chu`; `python run.py score eval/run-N.csv`.
- [ ] **Step 3:** Commit `eval: first full run` (không sửa `expected`, không xoá câu trượt).
