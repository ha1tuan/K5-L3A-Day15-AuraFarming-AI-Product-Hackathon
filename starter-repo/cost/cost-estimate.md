# Chi phí khi dùng thật

> Điền ở guide bước 4.2, nộp ở CP4 14:30 Thứ Bảy 28/11. Ôn lại: ngày 13, ngày 1, ngày 14 · lab ngày 13, lab ngày 14. Chấm ở rubric R6.
> Số **không điền tay**: điền `cost/personas.yaml` → `python run.py simulate` → chép bảng trong `cost/simulate-N-summary.md` vào đây.
> Lúc build dùng gói miễn phí vẫn tính theo **giá gói trả phí** — đây là chi phí cho lúc đưa vào dùng thật.

## 1. Đầu vào

- **Persona** (`cost/personas.yaml`): 3 kiểu, nguồn `spec.md` §2 *(tự ước tính, chờ phỏng vấn — `evidence/interviews/CAU_HOI.md` câu 13)*:

  | Persona | Tỉ lệ | Phiên / người / tháng | Lượt hỏi / phiên |
  |---|---:|---:|---:|
  | `giam_doc_cty_nho` — giám đốc / trưởng phòng công ty 20–50 người | 0,50 | 0,5 | 2 |
  | `hr_admin` — HR / admin công ty 50–200 người | 0,35 | 1,0 | 3 |
  | `to_chuc_thuong_xuyen` — người phụ trách sự kiện nội bộ công ty lớn | 0,15 | 4 | 4 |

  Mỗi lượt hỏi lấy ngẫu nhiên một đầu vào loại `thuong` / `kho` trong `eval/benchmark.csv` (gồm cả câu soát báo giá Q01–Q12).
- **Số người dùng thật** 3 kịch bản: thấp **430** · cơ sở **1.720** · cao **8.590** người / tháng. Nguồn: ~85.900 người tổ chức chuyến đi = 10% của 859.048 doanh nghiệp đang hoạt động cuối 2025 (Cục Thống kê, kết quả sơ bộ Tổng điều tra kinh tế 2026, [VietnamPlus](https://www.vietnamplus.vn/ca-nuoc-co-859048-doanh-nghiep-dang-hoat-dong-san-xuat-kinh-doanh-post1123945.vnp)); tỉ lệ 10% và tỉ lệ dùng sản phẩm 0,5% / 2% / 10% *(tự ước tính)*.
- **Giá** 3 mức model (`further-reading/model-prices.md` của repo đề, BTC tra 25/11/2026), USD / 1 triệu token:
  - `gemini-3.1-flash-lite` — vào 0,25 · ra 1,50 — <https://ai.google.dev/gemini-api/docs/pricing> (tầng Nhỏ)
  - `gpt-5.4-mini` — vào 0,75 · ra 4,50 — <https://developers.openai.com/api/docs/pricing> (tầng Nhỏ, **model nhóm định dùng**)
  - `claude-sonnet-5.5` — vào 2,00 · ra 10,00 — <https://platform.claude.com/docs/en/about-claude/pricing> (tầng Lớn)
- **Tỉ lệ đạt** dùng để tính: **34/42 (81%)** — lượt `run-2@20261128-010334` (lượt 2, `eval/run-2.csv`, `--rate-from`)
- Đo token trên model **`ollama/qwen2.5:7b`** (chạy local), tính giá model `gemini-3.1-flash-lite`, `gpt-5.4-mini` và `claude-sonnet-5.5`. Bộ tách token khác nhau nên số token thật trên từng model có thể lệch.

## 2. Kết quả mô phỏng

Lượt mô phỏng: `cost/simulate-1.csv` · run ID `simulate-1@20261128-014632` · **50 phiên** · seed **42** · phiên lỗi **0/50** · trace `traces/simulate-1.jsonl` · tóm tắt `cost/simulate-1-summary.md`

Token và số lần gọi theo persona:

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| giam_doc_cty_nho | 25 | 2 | 852 | 164 | 1.3 | 4.1 |
| hr_admin | 16 | 3 | 1293 | 249 | 2.0 | 5.1 |
| to_chuc_thuong_xuyen | 9 | 4 | 1928 | 380 | 3.0 | 8.2 |

Chi phí (chép từ `cost/simulate-1-summary.md`):

| Model | Chi phí / phiên | Chi phí / task thành công | / tháng — thấp (430) | / tháng — cơ sở (1.720) | / tháng — cao (8.590) | / người / tháng (cơ sở) |
|---|---|---|---|---|---|---|
| gemini-3.1-flash-lite | $0.00064 | $0.00079 | $0.4257 | $1.70 | $8.50 | $0.00099 |
| gpt-5.4-mini | $0.0019 | $0.0024 | $1.28 | $5.11 | $25.51 | $0.0030 |
| claude-sonnet-5.5 | $0.0047 | $0.0058 | $3.10 | $12.40 | $61.91 | $0.0072 |

Chi phí / task thành công = chi phí trung bình mỗi phiên ÷ tỉ lệ đạt — **không coi như đạt 100%**.

Ghi chú: phần lớn việc (tính tiền, xếp lịch, soát báo giá) do code chạy, model chỉ đọc yêu cầu — nên trung bình 1,3–3 lần gọi model / phiên và token rất ít.

## 3. So với impact

- Impact / người / tháng (`spec.md` §2): 2 chuyến / năm ≈ 0,17 chuyến / tháng × 480 phút / chuyến ≈ **80 phút ≈ 1,3 giờ / người tổ chức / tháng** *(tự ước tính, chờ phỏng vấn)*.
- Chi phí / người / tháng (cơ sở, model `gpt-5.4-mini`): **$0.0030** (cả 1.720 người: $5.11 / tháng; kịch bản cao 8.590 người: $25.51 / tháng).
- **Kết luận một dòng — đáng làm không:** chi phí model gần như bằng 0 so với hơn 1 giờ công tiết kiệm mỗi người / tháng, nên tiền model không phải rào cản. Rào cản là chất lượng (34/42, chưa đạt chuẩn) và bằng chứng (số người dùng, tần suất, thời gian đều tự ước tính) → **Iterate**, chưa Go.

## 4. *(Muốn sâu hơn, không bắt buộc)*

- Chi phí ngoài model chưa tính: hosting backend + web, gọi bản đồ (OSRM / OpenStreetMap — hiện dùng máy chủ công cộng miễn phí, dùng thật cần tự host), giờ công người duyệt.
- Đổi `gpt-5.4-mini` sang `gemini-3.1-flash-lite` giảm ~3 lần ($5.11 → $1.70 / tháng ở cơ sở), cần chạy lại bộ câu thử trên model đó trước khi đổi.
