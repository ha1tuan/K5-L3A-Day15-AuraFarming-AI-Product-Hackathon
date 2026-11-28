# Tóm tắt mô phỏng simulate-1@20261128-014632

Do `python run.py simulate` sinh ra — không sửa tay. Chép bảng sang `cost/cost-estimate.md`.

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| giam_doc_cty_nho | 25 | 2 | 852 | 164 | 1.3 | 4.1 |
| hr_admin | 16 | 3 | 1293 | 249 | 2.0 | 5.1 |
| to_chuc_thuong_xuyen | 9 | 4 | 1928 | 380 | 3.0 | 8.2 |

Tỉ lệ đạt dùng để tính: 34/42 (81%) — lượt run-2@20261128-010334

- Tỉ lệ đạt lấy từ lượt nhóm chọn: eval/run-2.csv (--rate-from).

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | Chi phí / tháng — thấp (430 người) | Chi phí / tháng — cơ sở (1.720 người) | Chi phí / tháng — cao (8.590 người) | Chi phí / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| gemini-3.1-flash-lite (vào 0.25 · ra 1.5 $/1M) | $0.00064 | $0.00079 | $0.00030 | $0.4257 | $1.70 | $8.50 | $0.00099 |
| gpt-5.4-mini (vào 0.75 · ra 4.5 $/1M) | $0.0019 | $0.0024 | $0.00089 | $1.28 | $5.11 | $25.51 | $0.0030 |
| claude-sonnet-5.5 (vào 2.0 · ra 10.0 $/1M) | $0.0047 | $0.0058 | $0.0022 | $3.10 | $12.40 | $61.91 | $0.0072 |

- Chi phí / task thành công = chi phí / phiên ÷ tỉ lệ đạt. Chi phí / câu hỏi đạt = chi phí / phiên ÷ số lượt hỏi trung bình mỗi phiên (2.7) ÷ tỉ lệ đạt — tỉ lệ đạt đo theo từng câu thử.
- Token đo trên model: ollama/qwen2.5:7b. Giá tính theo từng model trong bảng — model khác bộ tách token thì số token thật có thể lệch; ghi rõ "đo trên model X, tính giá model Y" trong cost/cost-estimate.md.
- Phiên lỗi (không tính vào trung bình): 0/50.
