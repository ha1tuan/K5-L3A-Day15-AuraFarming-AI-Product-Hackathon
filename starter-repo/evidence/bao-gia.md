# Đào data 2 — báo giá tour đoàn công khai có cho biết tổng chi thật không

> Nguồn thứ hai cho `evidence/summary.md`. Giả thuyết, mẫu, cách đếm, ngưỡng ghi **trước** khi đếm: `evidence/hypothesis.md` → "Giả thuyết 2" (commit `5a240e8`, 27/11 22:40).
> Script: `evidence/dem_bao_gia.py` (chạy lại: `python evidence/dem_bao_gia.py`) · số: `evidence/bao-gia-counts.json` · từng trang: `evidence/bao-gia-labels.csv` · danh sách URL: `evidence/vietnambooking_tour_urls.txt`.

## 1. Mẫu

- Nguồn: sitemap công khai của vietnambooking.com (robots.txt cho phép `/du-lich/`), lấy 27/11/2026 → 1.267 URL tour, lọc còn **770 tour trong nước** (bỏ trang danh mục và tour nước ngoài theo tên URL).
- **Nhóm G — tour đoàn / team building / MICE:** mọi URL có `team`, `gala`, `mice`, `khach-doan`, `cong-ty` → **30 trang**.
- **Nhóm S — so sánh:** 60 tour trong nước khác, chọn ngẫu nhiên `random.Random(42)`.
- Tải ≤ 1 trang / giây; repo chỉ giữ số đếm + trích ≤ 300 ký tự mục "không bao gồm" (`data/bao_gia_mau.json` giữ giá / khách + 2 mục "bao gồm / không bao gồm" của 30 trang nhóm G, có link).

## 2. Kết quả (N = 30 trang tour đoàn)

| Đếm (định nghĩa trong `hypothesis.md`) | Nhóm G (tour đoàn) | Nhóm S (tour thường) |
|---|---|---|
| K1 — có mục "không bao gồm / chưa bao gồm" | **30/30 (100%)** | 53/60 (88%) |
| K1 — mục đó có ≥ 3 khoản | **26/30 (87%)** | 45/60 (75%) |
| K2 — VAT / hoá đơn nằm trong "không bao gồm" | **25/30 (83%)** | 46/60 (77%) |
| K2 — VAT / hoá đơn ghi "đã bao gồm" | **0/30** | 2/60 |
| K3 — có nhắc phụ thu (lễ, cuối tuần, phòng đơn…) | 22/30 (73%) | 42/60 (70%) |
| K4 — chỉ "liên hệ", không có giá số | 0/30 | 0/60 |
| **Ngưỡng: ≥ 3 khoản "không bao gồm" VÀ VAT không bao gồm / không nhắc** | **25/30 (83%)** | 43/60 (72%) |

**Đếm thêm sau khi xem kết quả (không thuộc ngưỡng ghi trước):** 10/30 trang tour đoàn ghi nguyên văn *"Nếu quý khách có nhu cầu xuất hóa đơn, công ty du lịch sẽ phụ thu thêm 10% trên giá tour"*; 14/30 ghi "Thuế VAT 8%" không bao gồm; 10/30 để vé tham quan / cáp treo ngoài giá tour.

**Ngưỡng ghi trước** (≥ 60% có ≥ 3 khoản "không bao gồm" **và** ≥ 30% VAT không bao gồm / không nhắc): **đạt** — 87% và 83%.

## 3. Ví dụ nguyên văn (trang công khai, link trong `evidence/bao-gia-labels.csv`)

1. "Hóa đơn giá trị gia tăng (VAT). Nếu quý khách có nhu cầu xuất hóa đơn, công ty du lịch sẽ phụ thu thêm 10% trên giá tour." — tour team building BCR (950.000đ/khách), mục *không bao gồm*.
2. "Thuế VAT 10% · Nếu quý khách có nhu cầu xuất hóa đơn, công ty du lịch sẽ phụ thu thêm 10% trên giá tour." — tour MICE Sài Gòn, mục *không bao gồm*.
3. "Thuế VAT 8% (nếu quý khách có nhu cầu)." — tour khách đoàn miền Tây 2N1Đ, mục *không bao gồm*.
4. "Vé cáp treo VinWonders (880.000 vé/ khách cao trên 1m4)." · "Vé máy bay khứ hồi." — tour khách đoàn Nha Trang – Đà Lạt 4N3Đ "đi bằng máy bay giá rẻ", mục *không bao gồm*.
5. "Phí thuê sân bãi + Lửa trại (nếu có)" — tour team building Cát Bà 3N2Đ, mục *không bao gồm* (không ghi số tiền).

## 4. Kiểm tay

- 15 trang đầu nhóm G: đọc trích đoạn "không bao gồm" so với số đếm của script (cột `kiem_tay` trong `bao-gia-labels.csv`) — số khoản và nhãn VAT khớp 15/15 **sau 2 lần sửa script** (ghi lại vì sao):
  1. Mục "không bao gồm" bị đếm lố khoản ở vài trang (21, 13, 30 khoản) vì đoạn "Những thông tin cần lưu ý khác" không được nhận là mục mới → thêm vào danh sách đầu mục.
  2. K3 "phụ thu" ban đầu 30/30 — sai: chân trang có địa chỉ đường **Phạm Phú Thứ** (bỏ dấu = "pham phu thu") → bỏ trường hợp này, còn 22/30.
- Người kiểm: Claude (AI) đọc trích đoạn — **nhóm cần một người kiểm lại** ít nhất 10 trang và điền tên.

## 5. Vì sao quan trọng — và giới hạn

- Với công ty, **hoá đơn là bắt buộc** để hạch toán chi phí (`data/quy_tac_chung_tu.json`, nguồn tư vấn thuế) → 25/30 báo giá tour đoàn công khai **chưa gồm** khoản này: giá báo luôn thấp hơn số công ty phải chi 8–10%, chưa kể vé, tip, vé máy bay ghi "không bao gồm". Ví dụ tính bằng code (`codebase/soat_bao_gia.py`): tour BCR 45 khách giá báo 42.750.000đ → tổng chi thật ≈ 49.275.000đ (+15%); tour Nha Trang – Đà Lạt "giá rẻ" 40 khách từ Hà Nội: 99.600.000đ → ≈ 265.968.000đ (+167%: vé máy bay ước tính 112.000.000đ và vé cáp treo VinWonders 880.000đ × 40 nằm ngoài giá).
- **Giới hạn:** một trang web (vietnambooking), 30 trang tour đoàn; trang công khai là mẫu, báo giá gửi riêng cho công ty có thể đầy đủ hơn — cần phỏng vấn để biết báo giá thật công ty nhận có giống không (câu hỏi trong `evidence/interviews/CAU_HOI.md`). Lọc tour nước ngoài theo tên URL có thể sót / lọc nhầm vài trang ở nhóm S (không ảnh hưởng nhóm G — đã đọc tên cả 30).
