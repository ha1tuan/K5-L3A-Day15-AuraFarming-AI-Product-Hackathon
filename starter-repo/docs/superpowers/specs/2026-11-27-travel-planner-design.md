# Thiết kế — Agent lập kế hoạch du lịch cho cả công ty (Track C)

Ngày: 2026-11-27 · Trạng thái: bản nháp chờ duyệt (thay toàn bộ thiết kế "người đi lẻ" trước đó; lịch sử ở §8) · Bản đồ code: [`ARCHITECTURE.md`](../../../ARCHITECTURE.md) · Bản nộp: [`spec.md`](../../../spec.md)

## 1. Mục đích

**Người dùng:** giám đốc, hoặc người được giao tổ chức chuyến du lịch cho cả công ty.

**Pain (lời người dùng):** khó và mất thời gian (1) tìm địa điểm phù hợp cho cả công ty, (2) ra kế hoạch tối ưu nằm trong ngân sách được cấp. *(Bằng chứng định lượng cho spec.md §1 nhóm thu song song.)*

**Việc hệ thống làm:** nhận số người, mục đích (nghỉ dưỡng hay gắn kết), số ngày, nơi xuất phát, cùng **kinh phí dự trù và/hoặc địa điểm** → gợi ý địa điểm hoặc dự trù kinh phí theo **3 gói (tiết kiệm · cân bằng · cao cấp)** → giám đốc duyệt → **kế hoạch chi tiết**: di chuyển, ăn uống, nghỉ ngơi, hoạt động theo từng ngày, từng giờ, kèm bảng chi phí cả đoàn và mỗi người. Vượt ngân sách thì giải thích rõ: vượt bao nhiêu, khoản nào gây vượt, vì sao, bớt gì để về trong ngân sách.

**Lát cắt một câu:** *Một giám đốc cần tổ chức chuyến đi cho công ty · nhập số người, mục đích, số ngày, nơi xuất phát cùng kinh phí và/hoặc địa điểm · AI tìm địa điểm, chỗ ở, ăn uống, hoạt động có nguồn và code dự trù 3 gói theo ngân sách · giám đốc nhận kế hoạch từng giờ kèm bảng chi phí và lời giải thích khi vượt ngân sách.*

**Bối cảnh:** hackathon AI20K, Track C (hướng nhóm tự mở rộng). CP2 19:30 27/11 chốt chuẩn "đạt" · CP3 10:00 28/11 · CP4 14:30 28/11.

## 2. Ba cách vào

| Cách | Người dùng nhập (ngoài số người, mục đích, số ngày, nơi xuất phát) | Hệ thống trả | Người duyệt |
|---|---|---|---|
| **A** | kinh phí dự trù | 2–3 địa điểm phù hợp, mỗi nơi có tổng chi phí 3 gói (ước tính), cách đi, thời gian đi, lý do, link tham khảo | Có — chọn địa điểm + gói, sửa được → kế hoạch chi tiết **gói đã chọn** |
| **B** | địa điểm | dự trù kinh phí 3 gói cho địa điểm đó, tách từng khoản | Có — chọn gói, sửa được → kế hoạch chi tiết **gói đã chọn** |
| **C** | cả kinh phí và địa điểm | **bỏ qua bước duyệt**, sinh luôn **kế hoạch chi tiết cả 3 gói**, đánh dấu gói nào trong / vượt ngân sách, giải thích gói vượt | Không |

Hệ thống tự nhận cách vào từ những gì người dùng nhập. Thiếu số người, mục đích, số ngày, nơi xuất phát, hoặc thiếu cả kinh phí lẫn địa điểm → hỏi lại đúng thông tin thiếu.

## 3. Mục tiêu · không làm · thất bại dù chạy được

**Mục tiêu**
- Ba cách vào như §2; ba gói luôn tính bằng code trên cùng một khung lịch.
- Mọi con số (giờ, tiền, số phòng, số xe, thời gian đi) do code tính; số không có nguồn mang nhãn "ước tính".
- Vượt ngân sách luôn kèm giải thích có số: chênh bao nhiêu, 2–3 khoản đóng góp lớn nhất, lựa chọn cắt giảm và số tiền tiết kiệm của từng lựa chọn.
- Mỗi địa điểm, chỗ ở, quán, hoạt động có link nguồn (bài viết, video) nếu tìm thấy.

**Không làm**
- Không đặt phòng, đặt xe, đặt vé, thanh toán; không khẳng định còn phòng / còn chỗ; giá là "tham khảo / ước tính".
- Chỉ trong nước (Việt Nam) — không visa, ngoại tệ *(người thiết kế tự quyết, xem §7)*.
- Không khảo sát nguyện vọng từng nhân viên; không chia lịch riêng theo phòng ban.
- Không đăng nhập, không lưu lịch sử dài hạn.

**Thất bại dù chạy được**
- Model tự nhẩm tiền cho cả đoàn; bảng chi phí không khớp phép tính.
- Gói "trong ngân sách" mà tổng thực tế vượt; vượt mà không giải thích hoặc giải thích không có số.
- Gợi ý địa điểm / chỗ ở không có trong kết quả tìm kiếm (bịa).
- Lịch chồng giờ, đến lúc đóng cửa, đoàn 60 người xếp vào quán 20 chỗ khi nguồn ghi rõ sức chứa.
- Cơ cấu phòng không đủ chỗ cho cả đoàn, hoặc đắt hơn cơ cấu rẻ nhất có thể với cùng loại phòng.
- Tự đoán số người / ngân sách thay vì hỏi lại.

## 4. Ràng buộc

- **Hợp đồng khung chấm (không đổi):** `codebase/agent.py::answer(text) -> {"output": str}` · `codebase/ai.py::call_model(system, user)` có `@model_call`, token từ `usage` · công cụ `@tool` trong `codebase/tools.py` · không sửa `tracing.py`, `eval/run_eval.py`, `cost/simulate.py`, `run.py` (giao diện thay qua `codebase/app.py`).
- Mọi lời gọi model qua `call_model`; model không trả số dùng trong output.
- `answer()` chạy không cần server / database, không nhớ giữa các lần gọi, không dừng chờ người duyệt.
- Luật dữ liệu: cache chỉ giữ tiêu đề, link, trích ≤ 2 câu; không tên người viết; không dữ liệu thật của người thật.
- `TAVILY_API_KEY`, khoá model trong `starter-repo/.env` (không commit). Nominatim ≤ 1 yêu cầu / giây, User-Agent `travel-planner-hackathon`.
- Chuẩn "đạt" chốt trước CP2, không sửa sau.

## 5. Các cách đã cân nhắc

| Quyết định | Các cách | Chọn | Vì sao |
|---|---|---|---|
| Dựng hệ thống | (1) một graph có bước nhận cách vào · (2) hai agent "dự trù" + "lập kế hoạch" nối qua API · (3) model tự dự trù và viết kế hoạch | **(1)** | dùng lại lõi, web, lối chấm chung một graph; (2) tách trạng thái, trông như hai sản phẩm; (3) model nhẩm tiền cho cả đoàn — bẫy track |
| "Tối ưu theo ngân sách" | (a) dùng sát ngân sách · (b) rẻ nhất · (c) 3 gói | **(c)** | giám đốc so sánh rồi chọn |
| Lõi | model chọn, code xếp giờ + tính tiền | giữ | số luôn đúng |
| Nguồn dữ liệu | Tavily + Nominatim + bảng ước tính + cache ghi-lại-phát-lại | giữ | địa điểm bất kỳ, có bài viết / review |
| Web | một tiến trình FastAPI + SQLite + React | giữ | người ngoài chạy một lệnh (rubric R3) |

Hình dạng: **workflow cố định có rẽ nhánh theo cách vào và một vòng sửa giới hạn** (`MAX_REPAIR = 2`).

## 6. Thiết kế

### 6.1 Luồng graph

```
parse_request ──thiếu thông tin / ngoài phạm vi──► END (hỏi lại · từ chối)
     │
   route ─┬─ A (chỉ kinh phí) ─► goi_y_dia_diem: plan_queries → tim_kiem_web → extract → ground_and_rank (địa điểm)
          │                       → du_tru_3_goi cho từng địa điểm (2–3)
          ├─ B (chỉ địa điểm) ──► du_tru_3_goi
          └─ C (cả hai) ───────► du_tru_3_goi
                                     │
          A, B (web): DỪNG — giám đốc duyệt: chọn địa điểm (A) + gói, sửa số người / bỏ hoạt động → tính lại
          A, B (chấm): tự duyệt — A lấy địa điểm xếp hạng 1; gói = gói cao nhất còn trong ngân sách
                       (B không có ngân sách → cân bằng; không gói nào trong ngân sách → tiết kiệm)
          C: không dừng, đi tiếp với cả 3 gói
                                     │
     lap_ke_hoach (mỗi gói được giao): tim_kiem_web (chỗ ở, quán cho đoàn, hoạt động theo mục đích)
          → extract → ground_and_rank → chon (model, một lần gọi cho mọi gói) → xep_gio (code) → kiem (code)
          → (vi phạm, ≤ 2 vòng) chon lại → render: lịch + bảng chi phí + giải thích vượt ngân sách
```

### 6.2 Dự trù 3 gói (code, `du_tru_3_goi`)

Gói khác nhau ở **mức** của từng hạng mục; khung lịch (số ngày, giờ đi / về, bữa ăn) giống nhau.

| Hạng mục | Tiết kiệm | Cân bằng | Cao cấp | Số lượng |
|---|---|---|---|---|
| Di chuyển chặng đi / về | xe khách 45 chỗ | limousine / xe đời mới | limousine, hoặc máy bay nếu đường bộ > 8 giờ | số xe = ⌈người / sức chứa⌉; máy bay theo người |
| Lưu trú | khách sạn 2–3★ | khách sạn 4★ | resort 4–5★ | cơ cấu phòng tối ưu (§6.2a) × số đêm |
| Ăn | suất thường | set menu | set menu cao cấp | người × bữa |
| Gala / tiệc tối | không | 1 buổi (nếu gắn kết) | 1 buổi có sân khấu | người |
| Hoạt động | tự tổ chức | team building có đơn vị (gắn kết) / spa, tour nhẹ (nghỉ dưỡng) | trọn gói | người hoặc trọn gói |
| Phát sinh | 5% | 5% | 5% | % tổng |

- Đơn giá: ưu tiên số có trong bài viết tìm được (kèm link), không có thì `data/estimates.json` theo hạng mục × mức (có nhãn "ước tính"). Giá máy bay theo cặp thành phố nếu tìm được, không thì ước tính theo khoảng cách.
- Chặng đi: định vị nơi xuất phát và địa điểm (Nominatim) → km đường ≈ đường chim bay × 1.3; xe khách 50 km/h + 30 phút nghỉ mỗi 3 giờ; máy bay: giờ bay ước tính + 2 giờ thủ tục + đưa đón sân bay.
- Kết quả mỗi gói: bảng khoản mục {hạng mục, mô tả, số lượng, đơn giá, thành tiền, ước tính?, nguồn?}, tổng cả đoàn, mỗi người, chênh so với ngân sách.

### 6.2a Xếp phòng (code)

Theo yêu cầu người dùng: **không mặc định 2 người / phòng** — khách sạn có phòng 2, 3, 4 người…; xếp dựa trên chi phí và số lượng phòng của khách sạn.
- Mỗi khách sạn có danh sách loại phòng `{loai, suc_chua, gia_dem, so_luong?, uoc_tinh, nguon?}` lấy từ bài viết / trang khách sạn tìm được; thiếu thì `estimates.json` cho hạng sao đó (phòng 2, 3, 4 người, giá ước tính, `so_luong` không biết).
- Bài toán: chọn số phòng mỗi loại sao cho tổng sức chứa ≥ số người, mỗi loại ≤ `so_luong` (nếu biết), **tổng tiền / đêm nhỏ nhất**; hoà thì ít phòng hơn. Giải bằng quy hoạch động theo số người (N ≤ 500, ≤ 6 loại phòng).
- Không đủ phòng theo `so_luong` đã biết → mã `THIEU_PHONG`, gợi ý thêm khách sạn thứ hai cùng mức hoặc đổi khách sạn. `so_luong` không biết → vẫn xếp, ghi "cần xác nhận số phòng còn trống với khách sạn" (không khẳng định còn phòng).
- Output hiện cơ cấu phòng (vd "10 phòng 4 người + 2 phòng 3 người + 1 phòng 2 người = 48 chỗ cho 48 người"), giá / đêm từng loại, tổng. Việc ai ở với ai do công ty tự xếp.

### 6.3 Giải thích vượt ngân sách (code, chữ do code dựng; model chỉ thêm lý do định tính)

Khi tổng > ngân sách: (1) số vượt và %, (2) 2–3 khoản đóng góp nhiều nhất vào phần chênh so với gói thấp hơn liền kề (vd "resort 5★: +28 triệu so với 4★"), (3) danh sách cắt giảm tính sẵn, mỗi dòng ghi số tiết kiệm và tổng sau khi cắt (hạ một mức một hạng mục · bớt một đêm · bỏ gala), (4) nếu gói tiết kiệm vẫn vượt: ngân sách tối thiểu cần có và gợi ý nới (bớt ngày, địa điểm gần hơn).

### 6.4 Kế hoạch chi tiết (`lap_ke_hoach`)

- Ngày 1 bắt đầu từ giờ xuất phát (mặc định 06:30 với xe khách, theo giờ bay với máy bay); ngày cuối kết thúc khi về tới nơi xuất phát.
- Mỗi ngày: di chuyển · bữa sáng (tại chỗ ở, nếu có đêm trước) · trưa 11:30–13:30 · tối 18:00–20:00 · hoạt động · nghỉ ngơi. Gắn kết: ≥ 1 khối team building, gala tối (gói có). Nghỉ dưỡng: ≥ 1 khối tự do mỗi ngày, hoạt động nhẹ.
- Quán ăn cho đoàn: ưu tiên nguồn ghi phục vụ đoàn / sức chứa; không rõ thì ghi "cần xác nhận sức chứa".
- **Chi tiết nội dung (yêu cầu người dùng):** mỗi bữa ăn có **thực đơn** (danh sách món, giá / suất, quy cách bàn, đồ uống gồm / không gồm); **gala** có **chương trình theo mốc giờ** (đón khách, khai mạc, tiệc, văn nghệ, trao giải, bốc thăm, bế mạc) + thực đơn + những gì gói gồm / công ty tự lo; mỗi **hoạt động** (team building, tham quan) có **kịch bản**: chủ đề, chia đội, từng trò / điểm dừng theo mốc giờ, đơn vị tổ chức gồm gì, phương án mưa.
  - Nguồn: thực đơn lấy từ trang / bài viết của nhà hàng nếu có (kèm link); không có thì **thực đơn mẫu theo mức gói** trong `data/menus.json` (nhãn "ước tính, cần chốt với nhà hàng"). Chương trình gala và kịch bản hoạt động do **model soạn theo mẫu** (`data/programs.json`: khung mốc giờ theo mục đích và độ dài) — chỉ chữ, không số tiền; giờ các mốc do code chia trong khung thời gian của khối đó.
  - Bảng chi phí tách **từng bữa** (không gộp "ăn uống"), dòng gala tách tiệc / MC-âm thanh, dòng hoạt động ghi gồm những gì; bữa đã gồm trong giá phòng ghi 0đ kèm chú thích.
- Bộ kiểm: `CHONG_GIO`, `DONG_CUA`, `QUA_GIO_KET_THUC` (> 22:00), `ID_KHONG_TON_TAI`, `TRUNG_DIEM`, `THIEU_SUC_CHUA`, `THIEU_PHONG` (chỉ khi nguồn ghi sức chứa < số người). Vượt ngân sách **không** là lỗi chặn — bắt buộc có giải thích §6.3.

### 6.5 Hai lối vào

- **Chấm — `answer(text)`:** `parse_request` bóc từ chữ; tự duyệt như §6.1; output chữ: (A) danh sách địa điểm + 3 gói rồi kế hoạch chi tiết của lựa chọn tự duyệt, (B) bảng 3 gói rồi kế hoạch gói tự duyệt, (C) cả 3 kế hoạch. Cache Tavily / Nominatim ở chế độ `replay`.
- **Web:** form có trường riêng (số người, số ngày, ngày đi, nơi xuất phát, mục đích, kinh phí, địa điểm) gửi thẳng JSON — không cần model bóc chữ; graph với `SqliteSaver`, dừng ở bước duyệt (A, B).
  - `POST /api/trips` (form) → `TripView` (status `choose_destination` | `choose_package` | `ok` | `ask_back` | `refused` | `error`)
  - `POST /api/trips/{id}/approve {destination?, package, headcount?, remove_items?}` → tính lại nếu có sửa → `TripView` (`ok` + kế hoạch)
  - `GET /api/trips/{id}` · `GET /api/health`
- **Màn hình (React):** chi tiết ở [thiết kế web](2026-11-27-web-ui-design.md). form → (A) thẻ địa điểm, mỗi thẻ 3 cột gói + lý do + link / (B) bảng so 3 gói → nút duyệt (có chỉnh số người, bỏ hạng mục) → kế hoạch từng ngày + bảng chi phí + khối "Vì sao vượt ngân sách" khi có. (C) hiện 3 kế hoạch dạng tab.

### 6.6 Dữ liệu

- `Place` (địa điểm / chỗ ở / quán / hoạt động): id, tên, loại, thành phố, lý do, nguồn, số nguồn nhắc tới, toạ độ?, giờ mở (+ ước tính), thời lượng, giá (+ ước tính, nguồn), sức chứa?, hạng sao?.
- `Package`: tier, line_items, total, per_person, over_budget, explanation.
- `data/estimates.json` thêm: xe khách 45 chỗ / limousine theo km, vé máy bay theo khoảng cách, phòng theo hạng sao, suất ăn / set menu theo mức, gala / người, team building / người.
- Cache `data/cache/{tavily,geo}/`; `SEARCH_MODE` live / record / replay.

## 7. Người thiết kế tự quyết (kiểm lại khi đọc)

- Chỉ trong nước. · Phát sinh 5%. · Đường bộ > 8 giờ thì gói cao cấp dùng máy bay.
- Cách A gợi ý 2–3 địa điểm; mỗi địa điểm tính đủ 3 gói (bằng code, không thêm lời gọi model).
- Lối chấm tự duyệt: địa điểm xếp hạng 1; gói cao nhất còn trong ngân sách (B không ngân sách → cân bằng).
- Web dùng form có trường riêng; `answer()` vẫn bóc từ chữ.
- Ngày đi không có → giả định thứ Sáu gần nhất (đi công ty thường cuối tuần), env `TRAVEL_TODAY` để cố định khi chấm.
- Số người hợp lệ 5–500; mục đích nhận "nghỉ dưỡng", "gắn kết", hoặc cả hai (ưu tiên gắn kết cho khối hoạt động).

- **Thiếu dữ liệu tìm kiếm:** `SEARCH_MODE` mặc định `live` cho cả `answer()` và web; chạy bộ câu thử dùng `replay` (cache đã ghi, commit). Không có `TAVILY_API_KEY` hoặc cache thiếu → **chế độ chỉ ước tính**: vẫn dự trù 3 gói và lập lịch bằng hạng mục chung ("khách sạn 4★ tại <địa điểm>", "nhà hàng set menu"), không nêu tên cơ sở nào, mọi số nhãn "ước tính", đầu output ghi rõ "chưa tìm được nguồn trên mạng". Cách A ở chế độ này: gợi ý địa điểm chỉ từ danh sách điểm đến phổ biến trong `data/estimates.json` (có nhãn).
- **Số nào là chuẩn:** tổng ở bước dự trù là **"dự trù"**; khi lập kế hoạch chi tiết, chi phí tính từ chỗ ở / quán / hoạt động cụ thể là **"theo kế hoạch"** và là số chuẩn. Sau khi lập xong kiểm lại ngân sách; lệch so với dự trù thì hiện "dự trù X → theo kế hoạch Y" và chạy giải thích §6.3 nếu vượt.
- **Tìm kiếm cho 3 gói (cách C):** một lượt tìm chung; ứng viên phân mức theo hạng sao / giá; mỗi gói chọn trong nhóm mức của mình (một lần gọi model cho cả 3 gói).
- **Ngân sách** = tổng cả đoàn, trừ khi chữ ghi rõ "mỗi người / /người / một người" thì code nhân số người; output luôn ghi "ngân sách đã hiểu: … cho N người". Web: ô kinh phí có lựa chọn "tổng đoàn / mỗi người".
- **Xếp hạng địa điểm (cách A):** địa điểm có gói cân bằng nằm trong ngân sách xếp trước; cùng nhóm thì theo số nguồn nhắc tới. Lối chấm lấy hạng 1.

## 8. Lịch sử quyết định (27/11)

1. Người đi lẻ, Đà Lạt 2–3 ngày, dữ liệu dựng sẵn → 2. tìm web bằng Tavily, người dùng chọn ứng viên có review → 3. **đổi đối tượng: chuyến đi cả công ty**, ba cách vào, 3 gói, duyệt bởi giám đốc (A, B), C bỏ duyệt và sinh cả 3 kế hoạch.
- Giữ từ các bước trước: model chọn / code tính · Tavily + Nominatim + ước tính + cache · FastAPI một tiến trình + SQLite + React · `answer()` dùng chung graph.

## 9. Để lại cho người xây

Prompt cụ thể · giá trị trong `estimates.json` (ghi nguồn hoặc *tự ước tính*) · định dạng chữ của kế hoạch và bảng chi phí · thuật toán xếp giờ chi tiết (tham lam là đủ) · deploy công khai nếu cần cho người dùng thử.
