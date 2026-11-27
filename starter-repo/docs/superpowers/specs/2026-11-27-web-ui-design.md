# Thiết kế web — giao diện cho giám đốc lập kế hoạch du lịch công ty

Ngày: 2026-11-27 · Trạng thái: bản nháp chờ duyệt · Dựa trên: [`spec.md`](../../../spec.md) §4–§6 và [thiết kế hệ thống](2026-11-27-travel-planner-design.md) §2, §6.5

## 1. Mục đích

Giám đốc mở một trang web, điền thông tin chuyến đi, so sánh địa điểm / 3 gói, duyệt, rồi đọc kế hoạch từng giờ kèm bảng chi phí. Trang phải làm rõ ba điều: **tiền bao nhiêu (cả đoàn / mỗi người)**, **số nào là ước tính**, và **vì sao vượt ngân sách**.

Không làm: đăng nhập, lưu lịch sử, đặt chỗ / thanh toán, chỉnh lịch kéo-thả, bản đồ tương tác.

## 2. Công nghệ

| Phần | Chọn | Ghi chú |
|---|---|---|
| Khung | Vite + React 19 + TypeScript | `codebase/web/` |
| Tiện ích CSS | Tailwind CSS v4 (`@tailwindcss/vite`) | bố cục, khoảng cách, responsive, trạng thái |
| SCSS | `sass` | token màu / chữ (`_tokens.scss` → CSS variables), và các khối khó viết bằng class: dòng thời gian lịch, bảng so 3 gói, in ấn |
| Icon | `lucide-react` | không dùng emoji làm icon |
| Gọi API | `fetch` bọc trong `src/api/client.ts` | không thêm thư viện state; `useState` + `useReducer` cho luồng |
| Định tuyến | không dùng router; một màn hình theo `status` của `TripView`, `trip_id` giữ trên URL `?trip=<id>` để tải lại trang không mất | |
| Phục vụ | **Web và backend tách riêng, nói chuyện chỉ qua API** (yêu cầu người dùng). Không commit `dist/`. Dev: Vite proxy `/api` → `BACKEND_URL` (mặc định `:8000`). Deploy: build tĩnh với `VITE_API_URL`; FastAPI bật CORS theo `WEB_ORIGINS` | chạy web cần Node |

**Chia việc Tailwind / SCSS:** Tailwind đọc token từ CSS variables (`@theme` trong `index.css` trỏ tới biến do `_tokens.scss` sinh). Component dùng class Tailwind; chỉ 4 file SCSS module cho khối phức tạp (§6). Không viết mã màu hex trong component.

## 3. Hệ thống thiết kế

Phong cách: doanh nghiệp, đáng tin, dễ đọc số — nền sáng, navy, một màu nhấn xanh cho hành động. Tránh gradient tím/hồng kiểu "AI", tránh vui nhộn.

| Vai trò | Màu | Dùng cho |
|---|---|---|
| primary | `#0F172A` | tiêu đề, thanh trên |
| accent | `#0369A1` | nút chính, link, bước đang làm |
| background / card | `#F8FAFC` / `#FFFFFF` | nền / thẻ |
| muted-fg | `#475569` | chữ phụ |
| border | `#E2E8F0` | viền |
| ok | `#15803D` (nền `#F0FDF4`) | "trong ngân sách" |
| over | `#B91C1C` (nền `#FEF2F2`) | "vượt ngân sách" |
| estimate | `#B45309` (nền `#FFFBEB`) | nhãn "ước tính", "cần xác nhận" |

Trạng thái không chỉ dựa vào màu: luôn kèm icon + chữ ("✓ Trong ngân sách" bằng icon `CircleCheck`, "Vượt 39tr" bằng `TriangleAlert`, "ước tính" bằng chữ có gạch chấm).

- **Chữ:** *Be Vietnam Pro* (400/600/700) — hỗ trợ dấu tiếng Việt đầy đủ *(người thiết kế tự chọn thay Plus Jakarta Sans mà công cụ gợi ý, vì giao diện toàn tiếng Việt)*. Số tiền dùng `font-variant-numeric: tabular-nums` để cột thẳng hàng. Nội dung 16px, dòng 1.5.
- **Tiền:** `1.250.000đ` trong bảng chi tiết; dạng gọn `146,2 tr` ở thẻ / tiêu đề. Hàm `formatVnd`, `formatVndShort` trong `src/lib/format.ts`.
- **Khoảng cách:** thang 4/8/12/16/24/32/48; thẻ bo 12px, bóng nhẹ.
- **Truy cập:** tương phản ≥ 4.5:1, vòng focus 3px màu accent, mọi input có `<label>`, lỗi hiện ngay dưới ô, vùng bấm ≥ 44px, tôn trọng `prefers-reduced-motion`, link "bỏ qua tới nội dung".
- **Responsive:** 375 / 768 / 1024 / 1440. Bảng 3 gói: ≥ 1024 ba cột cạnh nhau; nhỏ hơn thì tab chọn gói. Bảng chi phí cuộn ngang trong khung riêng.

## 4. Luồng màn hình

```
[1 Form] ──POST /api/trips──► (đang xử lý) ──► status
   ├─ ask_back            → quay lại Form, câu hỏi hiện ở đầu form, ô thiếu được tô
   ├─ refused / error     → hộp thông báo + nút "Sửa yêu cầu"
   ├─ choose_destination  → [2A Chọn địa điểm]  ─┐
   ├─ choose_package      → [2B Chọn gói]        ─┴─ POST /approve ─► [3 Kế hoạch]
   └─ ok (cách C)         → [3 Kế hoạch] có 3 tab gói
```

Thanh bước trên đầu: **1 Thông tin · 2 Chọn & duyệt · 3 Kế hoạch** (cách C hiện "bước 2: bỏ qua — đã có cả kinh phí và địa điểm").

### 4.1 Màn 1 — Form thông tin chuyến đi

```
┌ Lập kế hoạch chuyến đi công ty ───────────────────────────────┐
│ Số người*  [ 60 ]      Số ngày*  [ 3 ▾ ]   Ngày đi  [📅 ]      │
│ Xuất phát* [ Hà Nội        ]                                   │
│ Mục đích*  (●) Gắn kết  ( ) Nghỉ dưỡng  ( ) Cả hai             │
│ ─ Bạn đã có gì? (ít nhất một) ─────────────────────────────── │
│ Kinh phí   [ 150.000.000 ] đ   (●) tổng đoàn ( ) mỗi người     │
│ Địa điểm   [ Hạ Long       ]  để trống nếu muốn được gợi ý      │
│                                                                │
│ Hệ thống sẽ: gợi ý địa điểm (chỉ kinh phí) · dự trù 3 gói      │
│ (chỉ địa điểm) · lập luôn 3 kế hoạch (có cả hai)   ← đổi theo ô │
│                                       [ Lập kế hoạch → ]       │
└────────────────────────────────────────────────────────────────┘
```
- Dòng "Hệ thống sẽ…" đổi ngay khi điền / xoá kinh phí, địa điểm — người dùng biết trước cách A/B/C.
- Kiểm ở trình duyệt: số người 5–500, số ngày 1–7, phải có kinh phí hoặc địa điểm. Kinh phí tự chèn dấu chấm khi gõ.
- Gửi xong: nút chuyển "Đang lập…", form khoá. Vì API đồng bộ (có thể 20–60 giây), hiện **khung chờ có các bước chạy lần lượt theo thời gian** ("Đang tìm địa điểm… → Đang tính chi phí… → Đang xếp lịch…") — chỉ là gợi ý tiến độ, không giả vờ đó là trạng thái thật của máy chủ; có nút Huỷ (AbortController).

### 4.2 Màn 2A — Chọn địa điểm (cách A)

```
Ngân sách 150 tr · 60 người · 3N2Đ · từ Hà Nội · gắn kết
┌ Hạ Long ───────────────┐ ┌ Ninh Bình ─────────────┐ ┌ Đà Nẵng ─────────────┐
│ 🚌 Xe khách · ~3h      │ │ 🚌 ~2h                 │ │ ✈ Máy bay · ~1h20     │
│ Tiết kiệm   118 tr ✓   │ │ 104 tr ✓               │ │ 152 tr ⚠ vượt 2 tr    │
│ Cân bằng    146 tr ✓   │ │ 129 tr ✓               │ │ 181 tr ⚠              │
│ Cao cấp     189 tr ⚠   │ │ 163 tr ⚠               │ │ 230 tr ⚠              │
│ Vì sao hợp: biển, bãi  │ │ …                      │ │ …                     │
│ cát rộng cho team…     │ │                        │ │                       │
│ Tham khảo: 3 bài · 2 video ▸                       │ │                       │
│ [ Chọn Hạ Long ]       │ │ [ Chọn Ninh Bình ]     │ │ [ Chọn Đà Nẵng ]      │
└────────────────────────┘ └────────────────────────┘ └───────────────────────┘
```
Chọn địa điểm → mở bảng 3 gói của nơi đó (dùng chung component với 2B), chọn gói → duyệt.

### 4.3 Màn 2B — So 3 gói và duyệt (cách B, và bước sau 2A)

```
                Tiết kiệm        Cân bằng ★gợi ý     Cao cấp
Di chuyển       Xe 45 chỗ ×2     Limousine ×4        Limousine ×4
Lưu trú         KS 3★            KS 4★               Resort 5★
  Phòng         15×4ng           10×4ng+6×3ng+1×2ng  …
Ăn uống         Suất thường      Set menu            Set cao cấp
Gala            —                1 buổi              Sân khấu
Hoạt động       Tự tổ chức       Team building       Trọn gói
──────────────────────────────────────────────────────────────
Tổng đoàn       118,4 tr ✓       146,2 tr ✓          189,0 tr ⚠ vượt 39 tr
Mỗi người       1,97 tr          2,44 tr             3,15 tr
                (○)              (●)                 (○)   ← chọn gói
▸ Chi tiết từng khoản (bảng mở rộng: số lượng × đơn giá, nhãn ước tính, link nguồn)
▸ Vì sao gói Cao cấp vượt? (khối giải thích, §4.5)

Chỉnh trước khi duyệt:  Số người [ 60 ]   Bỏ hạng mục: [ ] Gala  [ ] Team building
                                         [ Tính lại ]   [ Duyệt & lập kế hoạch → ]
```
- "★ gợi ý" = gói cao nhất còn trong ngân sách (cùng quy tắc tự duyệt của lối chấm).
- Sửa số người / bỏ hạng mục rồi bấm Duyệt → gửi `POST /approve` kèm `headcount`, `remove_items`; máy chủ tính lại. *(Nút "Tính lại" riêng chỉ có nếu API thêm điểm `/requote`; bản đầu gộp vào Duyệt — người thiết kế tự quyết để không đổi API.)*

### 4.4 Màn 3 — Kế hoạch chi tiết

```
Hạ Long · Gói Cân bằng · 60 người · 12–14/12      [In / PDF]
┌ Tổng 146,2 tr ✓ trong ngân sách 150 tr ─ mỗi người 2,44 tr ┐
│ dự trù 141,0 tr → theo kế hoạch 146,2 tr (khách sạn cụ thể đắt hơn mức chung) │
└──────────────────────────────────────────────────────────────┘
[Ngày 1 · T6 12/12] [Ngày 2] [Ngày 3]          | Bảng chi phí |
06:30 ●─ Xuất phát từ Hà Nội · limousine ×4 · 3h30
10:00 ●─ Nhận phòng sớm: KS Mường Thanh … ↗ nguồn   cần xác nhận số phòng
11:30 ●─ Ăn trưa: Nhà hàng … (set menu, 60 suất) ↗   ước tính
14:00 ●─ Team building bãi Cháy · 3h ↗
18:00 ●─ Gala tối …
21:00 ●─ Nghỉ
```
- Dòng thời gian dọc (SCSS module): giờ bên trái, chấm theo loại (di chuyển / ăn / ở / hoạt động / nghỉ, mỗi loại một icon), mỗi mục có lý do một dòng, link nguồn mở tab mới, nhãn "ước tính" / "cần xác nhận…".
- **Không có bảng chi phí ở màn kế hoạch** (yêu cầu người dùng): chỉ giữ ô tóm tắt tổng đoàn / mỗi người / trong-vượt ngân sách. Bảng chi phí từng khoản nằm ở màn so 3 gói (2B).
- Cách C: 3 tab gói ở trên cùng, tab mang nhãn ✓ / ⚠; dưới tab là cùng bố cục.
- Nút In: CSS `@media print` gọn (bỏ thanh trên, mở hết các ngày) — giám đốc thường gửi cho kế toán.

### 4.5 Khối "Vì sao vượt ngân sách"

```
⚠ Gói Cao cấp vượt 39,0 tr (26%) so với ngân sách 150 tr
Nguyên nhân chính so với gói Cân bằng:
  • Resort 5★ thay KS 4★        +28,0 tr
  • Gala có sân khấu            +11,0 tr
Cách đưa về trong ngân sách:
  ☐ Hạ resort xuống KS 4★       −28,0 tr → 161,0 tr (vẫn vượt 11 tr)
  ☐ Bỏ sân khấu gala            −11,0 tr
  ☐ Bớt 1 đêm                   −24,5 tr
```
Chữ và số lấy nguyên từ `explanation` của API — web không tự tính tiền. Ô tích chỉ là gợi ý để đưa sang phần "Bỏ hạng mục" ở màn 2B (cách A, B); ở cách C chỉ hiển thị.

## 5. Hợp đồng dữ liệu với API

Kiểu TypeScript trong `src/api/types.ts`, khớp `codebase/backend/src/api/schemas.py` (Task 9′ sẽ chốt tên trường; đây là bản đề xuất):

```ts
type Status = 'choose_destination' | 'choose_package' | 'ok' | 'ask_back' | 'refused' | 'error';
interface TripView { trip_id: string; status: Status; message: string;
  request?: TripRequestEcho;            // "đã hiểu": số người, ngân sách, cách vào…
  destinations?: DestinationOption[];   // 2A
  packages?: Package[];                 // 2B, và cả 3 gói ở C
  plans?: Plan[];                       // 1 phần tử (A, B) hoặc 3 (C)
  missing_fields?: string[]; }          // ask_back → tô ô thiếu
interface Package { tier: 'tiet_kiem'|'can_bang'|'cao_cap'; line_items: LineItem[];
  total: number; per_person: number; over_budget: number | null; recommended: boolean;
  explanation?: Explanation; }
interface LineItem { category: string; description: string; qty: number; unit: string;
  unit_price: number; amount: number; estimated: boolean; source_url?: string; }
```
Thêm một trường so với thiết kế hệ thống: `missing_fields` (để tô ô thiếu) và `recommended` (gói gợi ý) — ghi vào Task 9′.

## 6. Cấu trúc thư mục

```
codebase/web/
  index.html  vite.config.ts  package.json  tsconfig.json
  src/
    main.tsx  App.tsx                 # máy trạng thái theo TripView.status
    index.css                         # @import "tailwindcss"; @theme → var(--…)
    styles/_tokens.scss  _print.scss  # token màu, chữ, khoảng cách; in ấn
    api/client.ts  api/types.ts
    lib/format.ts                     # formatVnd, formatVndShort, ngày tiếng Việt
    components/
      StepBar.tsx  TripForm.tsx  LoadingSteps.tsx  Notice.tsx
      DestinationCard.tsx
      PackageCompare.tsx + PackageCompare.module.scss
      CostTable.tsx  OverBudget.tsx  EstimateBadge.tsx  BudgetBadge.tsx  SourceLinks.tsx
      PlanView.tsx  DayTimeline.tsx + DayTimeline.module.scss
  dist/                               # build, commit
```

## 7. Kiểm tra

- Vitest + Testing Library cho: `format.ts`; `TripForm` (dòng "Hệ thống sẽ…" đổi theo ô, chặn gửi khi thiếu); `App` render đúng màn theo từng `status` với dữ liệu mẫu `src/api/fixtures/*.json`.
- Dữ liệu mẫu cũng dùng cho chế độ `?demo=1` để duyệt giao diện khi backend chưa xong.
- Trước khi giao: chạy qua checklist truy cập (focus, tương phản, 375px không cuộn ngang).

## 8. Người thiết kế tự quyết (kiểm lại khi đọc)

Font Be Vietnam Pro · không router, `?trip=` trên URL · khung chờ tiến độ theo thời gian (API đồng bộ) · gộp "tính lại" vào nút Duyệt · thêm `missing_fields`, `recommended` vào API · màu riêng cho "ước tính" (hổ phách) · có nút In.
