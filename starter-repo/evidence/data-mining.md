# Đào data — cách đếm và kết quả

> Nguồn: review **công khai** trên Google Play của 5 app đặt du lịch phổ biến ở VN. Repo chỉ chứa số đã tổng hợp
> (`evidence/review-counts.json`), nhãn tay (`evidence/review-labels.csv`, chỉ có mã băm nội dung — không tên người viết)
> và vài trích dẫn dưới đây. Nguyên bộ review tải về nằm ở `evidence/raw-reviews.jsonl` — **không commit** (`.gitignore`: `evidence/**/raw-*`).

## 1. Cách đếm — viết TRƯỚC khi chạy

- **Data dùng:** review Google Play, `lang=vi`, `country=vn`, sắp theo **mới nhất**, tối đa 2.000 review / app, tải ngày 27/11/2026.
  App: Traveloka (`com.traveloka.android`), Agoda (`com.agoda.mobile.consumer`), Booking.com (`com.booking`), Mytour (`vn.mytour.apps.android`), Klook (`com.klook`).
- **Đếm gì:** 3 nhóm phàn nàn, mỗi nhóm khớp với một vế của pain trong `canvas.md` dòng 3:
  - **P — giá / phí lệch so với lúc xem** (giá tăng lúc thanh toán, phụ thu, phí phát sinh, giá app cao hơn đặt trực tiếp) → vế "dự trù lệch, chi vượt".
  - **R — đã đặt / đã trả nhưng đến nơi không có phòng, hoặc đơn không được xác nhận** → vế "thiếu phòng khi đã đi".
  - **G — đặt cho đoàn / nhóm** (≥3 người, ≥2 phòng, hoá đơn công ty) → vế "app là giá lẻ, không tính cho cả đoàn".
- **Trên tập nào / lọc gì:** review có nội dung ≥ 20 ký tự.
- **Mẫu số:** **review 1–2★ có nội dung** (người đang gặp vấn đề và kể ra) = **1.880**. Không lấy tổng 7.130 làm mẫu số vì 3.818 review không có chữ / quá ngắn.
- **Cách đếm:** regex lọc ứng viên (`evidence/count_reviews.py`: `PRICE`, `ROOM`, `GROUP`), rồi **gán nhãn tay** để đo độ chính xác: toàn bộ ứng viên G (19), mẫu ngẫu nhiên 50 ứng viên P và 30 ứng viên R (`random.Random(15)`). Số "ước tính" = số khớp regex × độ chính xác.
- **Script:** `pip install google-play-scraper` · `python evidence/count_reviews.py` (tải mới) · `python evidence/count_reviews.py --cached` (đếm lại trên cache) · thêm `--show` để in các review khớp.

**Ghi trung thực về quá trình:** regex v1 bắt nhầm nhiều (chữ "khác" khớp cả trong "khách", "phát sinh" khớp "sự cố phát sinh", "giá" khớp "đánh giá"; mẫu chữ có dấu bị lưu dạng NFD nên trượt). Gán nhãn 50 mẫu P ở v1 chỉ đúng **18/50**. Đã sửa thành v2 (ghi chú trong code), rồi lấy mẫu mới và gán nhãn lại — số dưới đây là v2. Ngưỡng giả thuyết trong `evidence/hypothesis.md` **không đổi**.

## 2. Đọc trước, đếm sau

Đã đọc ~150 review 1–2★ đầu tiên (Traveloka, Agoda). Các *kiểu* hành vi thấy được:
- Phàn nàn CSKH / hoàn tiền chậm — nhiều nhất, **không** thuộc pain của nhóm (không đếm).
- Giá nhảy giữa lúc xem và lúc thanh toán; phụ thu / phí xử lý báo sau khi đã trả.
- Đặt và trả tiền rồi, đến nơi khách sạn báo hết phòng / không nhận booking từ app.
- Đặt nhiều phòng: app không cho đặt nhiều phòng cùng lúc, đơn nhiều phòng chỉ được xác nhận một phần; không xuất được hoá đơn VAT cho công ty.

## 3. Kết quả (chạy `--cached` ngày 27/11/2026)

Review tải về: 7.130 (31/12/2016 → 26/11/2026) · có nội dung ≥ 20 ký tự: 3.312 · **1–2★ có nội dung: N = 1.880**.

| Đếm gì | Khớp regex x / N | Nhãn tay: đúng | Ước tính đúng x / N | Ghi chú |
|---|---|---|---|---|
| P — giá / phí lệch so với lúc xem | 104/1.880 (5,5%) | 41/50 (82%) | **≈85/1.880 (4,5%)** | Mytour cao nhất: 10/122 (8,2%) |
| R — đã trả mà không có phòng / không được xác nhận | 115/1.880 (6,1%) | 27/30 (90%) | **≈104/1.880 (5,5%)** | Agoda 54/783 · Mytour 25/122 · Booking 19/151 |
| P hoặc R (một trong hai vế của pain) | 202/1.880 (10,7%) | — | ≈9% *(nhân theo độ chính xác của từng nhóm, tự ước tính)* | 17 review khớp cả P và R |
| G — đặt cho đoàn / nhóm / nhiều phòng / hoá đơn công ty | 19/1.880 (1,0%) | 15/19 (79%) | **15/1.880 (0,8%)** | 21 review ở mọi số sao |
| G và có cả P hoặc R | 5 | — | 5 | đoàn nhiều phòng → trả tiền mà thiếu phòng |

Theo app (1–2★, khớp regex): Traveloka P 40/750 · R 15 · G 11 — Agoda P 43/783 · R 54 · G 7 — Booking.com P 10/151 · R 19 · G 1 — Mytour P 10/122 · R 25 · G 0 — Klook P 1/74 · R 2 · G 0.

## 4. ≥5 ví dụ cụ thể (mã băm nội dung trong `review-labels.csv`, không tên người viết)

1. `98a4051b72` · Agoda 1★ · 27/06/2026 (G): "ứng dụng thiết kế quá tệ việc mà người dùng muốn đặt nhiều phòng cùng 1 lúc theo ý muốn cũng không được."
2. `fe63408397` · Agoda 1★ · 16/08/2023 (G+R): "Đặt 5 phòng (còn chỗ trống) thì 3 phòng đã xác nhận đặt phòng nhưng chủ nhà nhắn tin đề nghị khách hủy cùng 1 lý do (Phòng bảo trì). 2 phòng còn lại thì chờ đúng 24h chủ nhà không xác nhận."
3. `0a2294254e` · Traveloka 1★ · 22/04/2026 (G+R): "Tôi đã đặt 3 phòng 3 ngày ở khách sạn […] gần cả tháng trước trên app, vậy mà bây giờ cận ngày nhận phòng thì khách sạn báo lỗi phần mềm không có phòng để nhận kêu tôi hủy."
4. `b62a3f16d1` · Agoda 1★ · 13/02/2025 (P): "giá hiện trc khi bấm vào là 20 usd , bấm vào xem thì hiện 25 usd , lúc thanh toán thì thuế phí lên 28 usd , payout thêm phí cổng nữa total 32usd , vãi , tăng cả hơn 50% giá gốc rồi"
5. `779a09d512` · Traveloka 1★ · 22/05/2023 (P): "Cứ bấm vào thanh toán là bị tăng giá. Có khi tăng cả triệu."
6. `500c9dc3e1` · Agoda 1★ · 01/09/2024 (G): "Đặt 4 phòng nhận được 3 phòng, 1 phòng hủy vẫn tính tiền 4 phòng."
7. `a1d5f5869d` · Mytour 1★ · 28/06/2024 (P): "Giá trên web thấp hơn các app khác. Nhưng khi đặt thực sự thì được báo lý do này nọ...tăng giá, thay đổi....các phát sinh sẽ cao hơn rất nhiều với dự tính."
8. `6865cdd3ad` · Traveloka 1★ · 13/01/2025 (G): "Mua vé máy bay không suất được hóa đơn VAT để thanh toán công ty"
9. `de988009bd` · Agoda 1★ · 17/06/2024 (R): "đặt phòng xác nhận thanh toán visa trên app ok rồi , khi tới nhận phòng thì khách sạn báo hết phòng ( đêm đó phải ngủ ngoài đường )"

## 5. Giới hạn của data

- Review cho biết người ta **gặp gì** khi đặt qua app, không cho biết **ai** là người tổ chức chuyến đi công ty — phần lớn người viết là khách lẻ / gia đình. G chỉ 0,8% → **data này không chứng minh được** quy mô pain của người tổ chức đoàn 30–200 người.
- Lệch về phía tiêu cực (chỉ đếm 1–2★) và về phía người hay viết review. Không đo được tần suất / số tiền lệch trung bình.
- Mẫu là 2.000 review mới nhất / app: Traveloka, Agoda, Booking chạm trần 2.000 nên khoảng ngày ngắn hơn Mytour, Klook (lấy hết).
- Kết quả tải mới sẽ khác chút vì review mới đến liên tục; nhãn tay khớp theo mã băm nội dung nên vẫn dùng lại được cho review cũ.
- Nhãn tay do **Claude (AI, trợ lý code của nhóm) gán theo định nghĩa ở mục 1**, lý do từng nhãn 0 ghi trong `review-labels.csv`. TV1 cần đọc lại; chưa có người thứ hai gán độc lập.

→ **Kiểm lại bằng:** phỏng vấn ≥3 người từng tổ chức chuyến đi công ty (giám đốc / HR / admin): lần gần nhất có dùng app OTA hay thuê công ty tour, dự trù lệch bao nhiêu so với chi thật, có lần nào thiếu phòng / xe cho đoàn không. **Chưa làm** tại thời điểm viết.
