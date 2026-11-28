# Giả thuyết — viết TRƯỚC khi tìm bằng chứng (5 phút, commit ngay)

> Điền ở guide bước 1.1. Ôn lại: ngày 2 · lab ngày 2.
> Viết **trước** khi đọc dòng data đầu tiên hay hỏi người đầu tiên, để không sửa cho khớp kết quả. Kết quả ngược giả thuyết vẫn đủ điểm nếu số là thật.

- Ngày giờ viết: 2026-11-27 18:30 (trước khi chạy `evidence/count_reviews.py` lần đầu; giả thuyết chính đã có trong `canvas.md` dòng 4 từ CP1)
- Người dùng chính (một vai cụ thể): giám đốc / người được giao (HR, admin) tổ chức chuyến đi trong nước cho cả công ty 30–200 người với một khoản kinh phí cho trước.
- **Mình nghĩ:** người tổ chức chuyến đi cho cả đoàn gặp khó khi dự trù chi phí vì giá trên app / web là giá lẻ, hay đổi giữa lúc xem và lúc trả tiền, có phí phát sinh, và app không tính cơ cấu phòng / xe cho vài chục người; hậu quả là dự trù lệch, chi vượt ngân sách hoặc thiếu phòng khi đến nơi.
- **Có thể còn cách giải thích khác:** (1) người tổ chức đoàn không dùng app OTA mà thuê công ty tour trọn gói → pain "dự trù" bị đẩy sang công ty tour; (2) lệch giá trên app chủ yếu do tỉ giá / thuế với khách lẻ, không liên quan đến đoàn.
- **Mình đúng nếu thấy:** trong review công khai Google Play của các app đặt du lịch phổ biến ở VN, **≥10% review 1–2★** phàn nàn giá / phí lệch so với lúc xem (giá thay đổi, phụ thu, phí ẩn, tính tiền sai) **và** có **≥10 review** (bất kỳ số sao) kể chuyện đặt cho đoàn / nhóm / nhiều phòng gặp vấn đề.
- **Nguồn sẽ dùng** (≥1 nguồn đạt ngưỡng, guide 1.2): [x] đào data · [ ] phỏng vấn ≥3 · [ ] khảo sát ≥20 — nguồn chính: review công khai Google Play (5 app: Traveloka, Agoda, Booking.com, Mytour, Klook; tiếng Việt, cửa hàng VN) · nguồn để kiểm lại: phỏng vấn ≥3 người từng tổ chức chuyến đi công ty (giám đốc / HR / admin) — chưa làm.

---

## Giả thuyết 2 — báo giá tour đoàn không cho biết tổng chi thật (viết trước khi đếm)

- Ngày giờ viết: 2026-11-27 22:40 (giờ VN), **trước** khi chạy `evidence/dem_bao_gia.py` lần đầu. Lý do thêm: giả thuyết 1 chỉ đạt một phần (`evidence/summary.md` §5) và chưa phân định được người tổ chức đoàn công ty tự dự trù hay thuê công ty tour.
- **Mình nghĩ:** người tổ chức chuyến đi công ty thường xin báo giá tour đoàn; báo giá công khai **không cho biết tổng chi thật** của chuyến đi: phần lớn có danh mục "không bao gồm / chưa bao gồm" nhiều khoản (VAT, phụ thu, chi phí cá nhân, đồ uống, tip…), nhiều trang không nói giá đã gồm VAT / xuất được hoá đơn hay chưa — trong khi công ty cần hoá đơn để hạch toán. Hậu quả: tổng chi thật cao hơn giá báo, kế toán có thể không chấp nhận chứng từ.
- **Có thể còn cách giải thích khác:** (1) trang công khai chỉ là mẫu, báo giá gửi riêng cho công ty đầy đủ hơn; (2) "không bao gồm" chủ yếu là chi phí cá nhân, không làm lệch tổng của công ty.
- **Mẫu (chốt trước):** mọi URL `/du-lich/tour-*.html` trong sitemap công khai của vietnambooking.com (lấy 27/11/2026, robots.txt cho phép), chỉ tour **trong nước**. Nhóm G (tour đoàn): URL chứa `team`, `gala`, `mice`, `khach-doan`, `cho-khach-doan`, `cong-ty` (bỏ trang danh mục). Nhóm S (so sánh): 60 tour trong nước khác, chọn ngẫu nhiên `random.Random(42)`. Tải ≤ 1 trang / giây, chỉ lưu số đếm + trích ≤ 300 ký tự, không lưu nguyên trang vào repo.
- **Cách đếm (chốt trước, bằng code, không đọc tay để chọn):** trên chữ của trang — K1 có mục "không bao gồm" / "chưa bao gồm" và số khoản trong mục đó (đếm dòng gạch đầu dòng / dòng ngắn đến mục kế tiếp) · K2 nhắc "VAT" / "hoá đơn" và ở thế "không bao gồm / chưa bao gồm" · K3 nhắc phụ thu (lễ, tết, cuối tuần, phòng đơn, cao điểm) · K4 không có giá bằng số (chỉ "liên hệ") · K5 có ghi giá thay đổi theo thời điểm / số lượng.
- **Mình đúng nếu thấy (nhóm G):** ≥ 60% trang có mục "không bao gồm" với ≥ 3 khoản **và** ≥ 30% trang ghi VAT / hoá đơn **không bao gồm** hoặc **không nhắc gì** đến VAT / hoá đơn.
- Kiểm tay: đọc lại ≥ 15 trang ngẫu nhiên để tính tỉ lệ đếm đúng của từng K.
