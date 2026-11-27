# Data card: dữ liệu bản chạy thử dùng

> Bản đầu (CP2). Không commit dữ liệu cá nhân thật; cache chỉ giữ tiêu đề, link, trích ≤ 2 câu.

## Dataset 1 · Cache kết quả tìm kiếm (Tavily + Nominatim)

| File | Nội dung | Số dòng | Nhãn |
|---|---|---|---|
| `gia_chuan.json` | Giá gốc: vé máy bay, thuê xe, phòng theo nhóm điểm đến × hạng sao, ăn, team building, gala, spa, BBQ, phà. **Mỗi số có link + ngày xem + độ tin cậy** | 8 nhóm giá | thật (có nguồn) + ước tính |
| `diem_den.json` | **5 điểm đi** (Hà Nội, Hải Phòng, Đà Nẵng, TP.HCM, Cần Thơ) · **24 điểm đến** 3 miền: toạ độ, sân bay gần, đảo/phà, loại cảnh, nhóm giá, có 5 sao không, **mức phù hợp nghỉ dưỡng / gắn kết (0–3)**, mùa đẹp | 5 + 24 | tên thật; mức phù hợp *(tự ước tính)* |
| `di_chuyen.json` | 4 loại xe + **120 tuyến** (5 × 24): km, giờ đường bộ, chặng bay, giá vé, km sân bay → điểm đến | 120 | `synthetic` (tính từ toạ độ + giá chuẩn) |
| `khach_san.json` | 24 × 3 mức × 4 khách sạn: phòng 2/3/4 người (giá, số phòng), **tiện ích** (hồ bơi, bãi biển riêng, spa, khuôn viên team building, hội trường), **điểm phù hợp mục đích** | 288 | `synthetic`, **tên dựng** |
| `nha_hang.json` | 24 × 3 mức × 4 quán: sức chứa, giá/người/bữa, giờ mở | 288 | `synthetic`, **tên dựng** |
| `hoat_dong.json` | **105 điểm tham quan tên thật** gắn mục đích + dịch vụ đoàn theo mức (team building, gala, spa, BBQ, tự do) | 369 | tên thật + giá ước tính; dịch vụ tên dựng |
| `muc_goi.json` | Quy tắc 3 gói + **hoạt động theo mục đích × gói** + khung giờ + giới hạn (5–500 người, 1–7 ngày) | 1 | quy tắc nhóm tự đặt |
| `video_review.json` | Video YouTube review + team building cho từng điểm đến, **mỗi link đã kiểm qua oEmbed** | xem dưới | link thật |

## Script

| Lệnh | Làm gì |
|---|---|
| Dùng để làm gì | nguồn cho công cụ `tim_kiem_web`, `dinh_vi` khi chạy bộ câu thử ở chế độ `replay` |
| Từ đâu | Tavily Search API, Nominatim / OpenStreetMap; ghi lại bằng `SEARCH_MODE=record` |
| Xử lý những bước gì | chỉ giữ tiêu đề, link, tên miền, trích ≤ 2 câu; bỏ tên người viết; mỗi truy vấn một file `data/cache/{tavily,geo}/<sha1>.json` |
| Số dòng / số đoạn | __ (điền sau khi ghi cache ở Task 1) |
| Phiên bản / ngày lấy | __ |
| Nhãn | thật (trích đoạn công khai) |
| Giới hạn | giá phòng / suất ăn cho đoàn hiếm khi có trên mạng; kết quả thay đổi theo thời gian; không kiểm được còn phòng |

## Dataset 2 · Bảng đơn giá ước tính (`data/estimates.json`)

| | |
|---|---|
| Dùng để làm gì | đơn giá khi bài viết không có giá (xe, phòng theo hạng sao, suất ăn, gala, team building) |
| Từ đâu | nhóm tự ước tính; dòng nào có nguồn thì ghi link |
| Xử lý những bước gì | __ |
| Số dòng / số đoạn | __ |
| Phiên bản / ngày lấy | __ |
| Nhãn | `synthetic` *(tự ước tính)* — mọi số dùng từ bảng này mang nhãn "ước tính" trong output |
| Giới hạn | không phản ánh giá mùa cao điểm / giá thương lượng cho đoàn |

## Dataset 3 · Bộ câu thử (`eval/benchmark.csv`)

| | |
|---|---|
| Dùng để làm gì | đo theo `eval/metric_spec.yaml` |
| Từ đâu | nhóm tự viết từ kịch bản `spec.md` §5 (`tu_viet`) |
| Số dòng / số đoạn | 26 (thuong 11 · kho 10 · tu_choi 5) |
| Nhãn | `synthetic` |
| Giới hạn | **chưa có câu từ lời người dùng thật** — cần ≥ 9 câu `nguoi_dung` từ phỏng vấn giám đốc / người tổ chức trước CP3 |
