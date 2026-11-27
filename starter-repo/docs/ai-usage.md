# Khai báo dùng AI

README của nhóm có mục "Dùng AI vào việc gì" (2–3 dòng, bắt buộc). Ghi chi tiết vào bảng dưới đây.

> Luật của đề: dùng AI để làm bài thoải mái, nhưng **ai không giải thích được phần có tên mình thì phần đó nhận 0 điểm**. Khai thiếu không bị trừ; giấu mới bị.

| Việc | Công cụ AI | AI làm gì | Người kiểm/sửa gì | Ai phụ trách |
|---|---|---|---|---|
| Code bản chạy thử | Claude Code (Opus) | Viết `codebase/agent.py` (workflow), `codebase/guardrails.py`, `codebase/planner.py`, `codebase/tools.py`, `tests/test_guardrails.py` | Phan Văn Diện đọc lại, chạy `pytest` (13 test) và `eval --try` | Phan Văn Diện |
| Prompt / thiết kế lời gọi mô hình | Claude Code (Opus) | Viết 3 prompt (PARSE / DU_TRU / LICH) trong `agent.py`: model chỉ trả hạng mục + đơn giá, không trả tổng | Phan Văn Diện | Phan Văn Diện |
| Đào data (viết script đếm, gợi ý nhãn) | Claude Code (Opus) | Viết `evidence/count_reviews.py`, tải review Google Play công khai, **gán nhãn** 99 review mẫu (`evidence/review-labels.csv`) | Nhãn do AI gán — **chưa** có người kiểm lại; TV cần đọc lại ≥20 nhãn | Phan Văn Diện |
| Rà câu hỏi phỏng vấn / khảo sát | | Chỉ rà câu dẫn dắt | | |
| Viết câu thử (benchmark) | Claude Code (Opus) | Viết thêm K11, R06, R07, R08 (2 câu phỏng theo review thật, 2 câu tấn công tự viết) | Mỗi câu thử có `source` | Phan Văn Diện |
| Sinh data `synthetic` (nếu có) | | | Seed __ · kiểm tay __ dòng | |
| Chấm cột `pass` bằng LLM (nếu có) | Claude Code (Opus) + `eval/check_outputs.py` | Code kiểm phép tính / sức chứa; Claude đọc output theo `pass_criterion`, ghi lý do ở cột `ghi_chu` của `eval/run-1.csv` | Người trong nhóm cần chấm lại độc lập ≥5 câu (guide 2.4) — chưa làm | Phan Văn Diện |
| Slide, văn bản | | | | |

**Không dùng AI để:** tạo người được phỏng vấn, trích dẫn, câu trả lời khảo sát; sửa kết quả các lượt đã chạy (`eval/run-*.csv`, `cost/simulate-*.csv`, `traces/`).
