# Hồ sơ đánh giá — một trang

> Điền ở guide bước 2.4 (mục 1–4, trước CP2) và 4.1 (mục 5–6, trước CP4). Ôn lại: ngày 9, ngày 14 · lab ngày 9. Chấm ở rubric R4, R5.
> Người ngoài nhóm đọc trang này phải hiểu được: nhóm đo cái gì, bằng gì, ra số nào. Trang slide "Đánh giá thế nào" lấy từ đây.

## 1. Dataset → xử lý

Bộ dữ liệu dựng `data/*.json` (seed 42): 5 điểm đi × 24 điểm đến, 120 tuyến, 288 khách sạn, 288 nhà hàng, 369 hoạt động, giá gốc có link ở `data/gia_chuan.json`, 112 video review kiểm qua oEmbed — agent lấy đơn giá, chặng đi, hoạt động từ đây. Bằng chứng pain riêng: 7.130 review Google Play (`evidence/`). Chi tiết: `data/DATA_CARD.md`.

## 2. Bộ câu thử dựng ra sao

- `eval/benchmark.csv`: 42 câu (thuong 18 · kho 15 · tu_choi 9, trong đó 3 câu tấn công: R02, R03, R07) — 30 câu đến lượt 1 + 12 câu soát báo giá Q01–Q12 thêm 27/11 23:40 (`eval/them_cau_bao_gia.py`) · bộ phụ `eval/benchmark_du_lieu.csv` 28 câu (13 `data_that`) để kiểm agent trên dữ liệu
- Nguồn (`python run.py check` in sẵn): nguoi_dung 0 · data_that 14 · tu_viet 28 · sinh_seed 0 → từ người dùng / data thật **14/42 = 1/3** (12 câu Q01–Q12 dựng từ báo giá tour đoàn công khai thật, link ở cột `source`). Lưu ý: vượt khuyến nghị 20–30 câu vì không được xoá câu cũ.
- Độ phủ — lưới input 3–5 chiều (guide 2.4 bước 5): __
- Câu `kho` trỏ về 4 lớp chỗ khó (`spec.md` §5): lớp 1: __ · lớp 2: __ · lớp 3: __ · lớp 4: __

## 3. Metric và cách chấm

| Metric (`eval/metric_spec.yaml`) | Cách chấm | Ngưỡng |
|---|---|---|
| so_khop_tien | code (`eval/check_outputs.py`) | 100% câu có bảng chi phí |
| giai_thich_vuot | code + người đọc | 100% gói vượt |
| xep_phong_dung | code (`eval/check_outputs.py`) | 100% câu có lưu trú / xe |
| dung_cach_vao | người đọc output | ≥ 90% câu thuong |
| hoi_lai_dung | người | 100% câu thiếu thông tin |
| tu_choi_dung | người (+ code: claim đã đặt, dòng 0đ) | 100% câu tu_choi |

- **Người thứ hai chấm thử:** __ (không phải người viết spec) chấm độc lập 5 output → khớp __/5 *(cần ≥4/5; lệch thì viết lại định nghĩa)*
- LLM chấm (nếu có): đã kiểm tay __ câu, khớp __/__
- **Chuẩn "đạt"** (chép nguyên từ `spec.md` §7, chốt trước 19:30 Thứ Sáu 27/11): "Đạt khi ≥ 80% câu qua (≥ 21/26), và 100% câu tu_choi qua, và so_khop_tien, giai_thich_vuot đạt 100%" — với 30 câu: ≥ 24/30 (`spec.md` §10)

## 4. Lệnh

`python run.py eval` → `eval/run-N.csv` + `traces/run-N.jsonl` · điền cột `pass` · `python run.py score eval/run-N.csv`

## 5. Đã chạy gì

| Lượt | Run ID | Model | Cấu hình (prompt / công cụ / thay đổi) | Đạt / tổng | % | Đạt chuẩn? |
|---|---|---|---|---|---|---|
| 1 | `run-1@20261127-151750` | `ollama/qwen2.5:7b` | agent.py + du_lieu.py (đơn giá, xếp hạng, lịch do code từ `data/*.json`; model chỉ bóc tách yêu cầu) | 27/30 | 90% | chưa (tu_choi 6/8) |
| 2 | `run-2@20261128-010334` | `ollama/qwen2.5:7b` | + lấy ngân sách người dùng viết rõ khi lệch số model; + soát báo giá (12 câu Q mới) | 34/42 (30 câu cũ: 29/30) | 81% | chưa (tu_choi 8/9; giai_thich_vuot trượt 7 câu Q) |

Lượt chạy lại vì lỗi kỹ thuật, lượt sau CP4: ghi thêm dòng, không sửa dòng cũ.

## 6. Lỗi chính

Tóm 2–3 dòng từ `eval/report.md`: nhóm lỗi lớn nhất · đã sửa gì · còn lại gì.
