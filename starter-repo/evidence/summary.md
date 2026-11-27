# Tổng hợp bằng chứng pain

> Điền ở guide bước 1.2, xong trước **CP3 10:00 Thứ Bảy 28/11**. Chấm ở rubric R1.
> Ba nguồn ngang nhau — tối thiểu **≥1 nguồn đạt ngưỡng**. Mạnh nhất: đào data ra insight → hỏi người dùng để kiểm lại (hoặc ngược lại).

## 1. Nguồn đã dùng

| Nguồn | Đạt ngưỡng? | File |
|---|---|---|
| Đào data — review công khai Google Play của 5 app du lịch VN (x/N, %, cách đếm ghi trước, script chạy lại được, ≥5 ví dụ) | ☑ | `evidence/data-mining.md` · `evidence/count_reviews.py` · `evidence/review-counts.json` · `evidence/review-labels.csv` |
| Phỏng vấn (≥3 người ngoài nhóm, đúng người dùng) | ☐ chưa làm | `evidence/interviews/` (mới có `TEMPLATE.md`) |
| Khảo sát (≥20 người ngoài nhóm, đúng người dùng) | ☐ chưa làm | `evidence/survey/` |

## 2. Số chính

Mẫu: 7.130 review mới nhất (Traveloka, Agoda, Booking.com, Mytour, Klook; `lang=vi`, `country=vn`; 31/12/2016 → 26/11/2026). **Mẫu số N = 1.880 review 1–2★ có nội dung ≥ 20 ký tự.**

- **Đặt rồi / trả tiền rồi mà đến nơi không có phòng hoặc đơn không được xác nhận (R):** 115/1.880 (6,1%) khớp từ khoá; nhãn tay đúng 27/30 → **≈104/1.880 (5,5%)**.
- **Giá / phí lúc trả khác lúc xem (P):** 104/1.880 (5,5%) khớp; nhãn tay đúng 41/50 → **≈85/1.880 (4,5%)**.
- **P hoặc R** (hai vế "dự trù lệch" và "thiếu phòng khi đã đi"): 202/1.880 (10,7%) khớp từ khoá.
- **Đặt cho đoàn / nhóm / nhiều phòng / hoá đơn công ty (G):** 19/1.880 (1,0%) khớp; nhãn tay đúng 15/19 → **15/1.880 (0,8%)**; 5 review trong số đó vừa đặt nhiều phòng vừa bị thiếu phòng / lệch giá.
- Phỏng vấn: 0/3 — chưa làm. Khảo sát: chưa làm.

| | Vai | Gặp pain? | Số lần / 1 tháng qua | Lần gần nhất mất | Đang xoay xở bằng |
|---|---|---|---|---|---|
| P1 | *(chưa phỏng vấn)* | | | | |
| P2 | *(chưa phỏng vấn)* | | | | |
| P3 | *(chưa phỏng vấn)* | | | | |

## 3. ≥5 trích dẫn hoặc ví dụ nguyên văn (có nguồn, bỏ tên)

Nguồn: review công khai Google Play; mã = 10 ký tự đầu SHA-1 của nội dung (tra trong `evidence/review-labels.csv`). Không ghi tên người viết.

1. "ứng dụng thiết kế quá tệ việc mà người dùng muốn đặt nhiều phòng cùng 1 lúc theo ý muốn cũng không được." — Agoda 1★, 27/06/2026, `98a4051b72`
2. "Đặt 5 phòng (còn chỗ trống) thì 3 phòng đã xác nhận đặt phòng nhưng chủ nhà nhắn tin đề nghị khách hủy cùng 1 lý do (Phòng bảo trì). 2 phòng còn lại thì chờ đúng 24h chủ nhà không xác nhận." — Agoda 1★, 16/08/2023, `fe63408397`
3. "Tôi đã đặt 3 phòng 3 ngày ở khách sạn […] gần cả tháng trước trên app, vậy mà bây giờ cận ngày nhận phòng thì khách sạn báo lỗi phần mềm không có phòng để nhận kêu tôi hủy." — Traveloka 1★, 22/04/2026, `0a2294254e`
4. "giá hiện trc khi bấm vào là 20 usd , bấm vào xem thì hiện 25 usd , lúc thanh toán thì thuế phí lên 28 usd , payout thêm phí cổng nữa total 32usd , vãi , tăng cả hơn 50% giá gốc rồi" — Agoda 1★, 13/02/2025, `b62a3f16d1`
5. "Đặt 4 phòng nhận được 3 phòng, 1 phòng hủy vẫn tính tiền 4 phòng." — Agoda 1★, 01/09/2024, `500c9dc3e1`
6. "Giá trên web thấp hơn các app khác. Nhưng khi đặt thực sự thì được báo lý do này nọ...tăng giá, thay đổi....các phát sinh sẽ cao hơn rất nhiều với dự tính." — Mytour 1★, 28/06/2024, `a1d5f5869d`
7. "Mua vé máy bay không suất được hóa đơn VAT để thanh toán công ty" — Traveloka 1★, 13/01/2025, `6865cdd3ad`

Thêm 2 ví dụ ở `evidence/data-mining.md` §4.

## 4. Các nguồn có khớp nhau không

Mới có **một nguồn** (đào data) — chưa có nguồn thứ hai để kiểm lại. Data nói: khi đặt qua app OTA, khoảng 1/10 review tiêu cực kể chuyện **giá cuối khác giá đã xem** hoặc **trả tiền rồi mà không có phòng** — đúng hai rủi ro làm hỏng một bản dự trù cho cả đoàn. Nhưng data **không** cho thấy nhiều người tổ chức đoàn dùng app OTA (G chỉ 0,8%). Hai cách hiểu, cần phỏng vấn để phân định: (a) người tổ chức đoàn công ty không dùng app OTA mà gọi công ty tour / khách sạn trực tiếp — pain dự trù nằm ở khâu so báo giá; (b) có dùng nhưng ít viết review.

## 5. Kết luận

Giả thuyết ở `evidence/hypothesis.md`: **phải đổi.**
- Ngưỡng 1 — "≥10% review 1–2★ phàn nàn giá / phí lệch": **không đạt** — ≈4,5% (P riêng), dù P hoặc R gộp lại là 10,7% khớp từ khoá.
- Ngưỡng 2 — "≥10 review kể chuyện đặt cho đoàn / nhóm / nhiều phòng gặp vấn đề": **đạt** — 15 review đúng sau nhãn tay (1–2★).
- Đổi gì: pain "dự trù lệch" có thật nhưng nhỏ hơn mình nghĩ; vế **"đặt rồi mà thiếu phòng"** (≈5,5%) nặng ngang vế giá → giữ ràng buộc `xep_phong_dung` và cảnh báo "không khẳng định còn phòng" trong bản chạy thử.

**Điều vẫn chưa biết:** người tổ chức chuyến đi công ty 30–200 người mất bao lâu cho một bản dự trù, lệch bao nhiêu so với chi thật, có dùng app OTA hay không. Cần ≥3 phỏng vấn (giám đốc / HR / admin) — chưa làm.

## Lịch hẹn (dùng cho CP2 — chỉ ghi vai và giờ, không tên)

| Vai | Giờ hẹn | Đã xong? |
|---|---|---|
| *(nhóm điền khi hẹn được)* | | |
