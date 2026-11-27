# Data card: dữ liệu bản chạy thử dùng

> Dữ liệu chạy thử cho agent lập kế hoạch du lịch công ty (Track C). Phục vụ 2 chiều:
> **nhập địa điểm → chi phí 3 gói** (Tiết kiệm · Cân bằng · Đầy đủ) và **nhập kinh phí → gợi ý địa điểm**, theo **mục đích** nghỉ dưỡng / gắn kết đội nhóm / cả hai, kèm **video review**.
> Dữ liệu tự dựng **không phải bằng chứng pain** (bằng chứng ở `evidence/`).

## Tóm tắt

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
| `python data/sinh_du_lieu.py` | Sinh 6 file JSON, **seed 42**. Chạy lại ra đúng cùng nội dung (đã kiểm hash) |
| `python data/lay_video_review.py` | Lấy video review (cần mạng, ~6 phút; chạy lại chỉ lấy điểm còn thiếu, `--lam-moi` lấy lại tất cả) |
| `python data/tinh_thu.py …` | **Bộ tính tham chiếu** chạy cả 2 chiều trên dữ liệu này, mọi số do code tính. Dùng để kiểm dữ liệu đủ cho bài toán và tính đáp án bộ câu thử |

```bash
python data/tinh_thu.py --tu "Hà Nội" --den "Hạ Long" --nguoi 40 --ngay 3 --muc-dich gan_ket --ngan-sach 150tr
python data/tinh_thu.py --tu SGN --ngan-sach 3tr --moi-nguoi --nguoi 60 --ngay 3 --muc-dich nghi_duong
```

## Cách dựng

- **Tên thật vs tên dựng:** điểm đi, điểm đến, điểm tham quan (Bà Nà, Tràng An, Fansipan…) là tên thật, **giá vé, giờ mở, ngày đóng là ước tính**. Khách sạn, nhà hàng, đơn vị team building, gala là **tên dựng** (hậu tố "(tên dựng)", `"ten_dung": true`), không nêu tên cơ sở thật với giá không kiểm được.
- **Giá:** phòng = giá chuẩn theo nhóm điểm đến × hạng sao × ngẫu nhiên 0,85–1,2; phòng 3, 4 người = × 1,35 / 1,6. Ăn = giá chuẩn theo mức × hệ số nhóm × 0,85–1,15. Làm tròn 10.000đ / 5.000đ.
- **Di chuyển:** đường bộ = chim bay × 1,3; xe 50 km/h + 30 phút nghỉ mỗi 3 giờ; phà +1 giờ. Điểm không có sân bay gắn sân bay gần (vd Vũng Tàu → Tân Sơn Nhất, Sa Pa → Nội Bài) rồi đi xe. Đảo (Phú Quốc, Côn Đảo) chỉ đường bay. Vé: mốc có nguồn nếu có, không thì 600.000đ + 900đ/km *(tự ước tính, khớp các mốc ±20%)*.
- **Mục đích:** điểm tham quan gắn `nghi_duong` / `gan_ket` theo tính chất (biển, spa, cảnh nhẹ → nghỉ dưỡng; kayak, zipline, cano, công viên nước → gắn kết). Khách sạn có điểm phù hợp tính từ tiện ích. Điểm đến có mức 0–3 *(tự ước tính, nhóm nên kiểm lại bằng phỏng vấn)*.
- **Chỗ khó cài sẵn** (đếm từ dữ liệu): 72 khách sạn không có phòng 4 người · 72 khách sạn ít phòng (số phòng chia 6; tổng 78 khách sạn ≤40 phòng) · 72 quán 25 chỗ chỉ mở trưa (mỗi điểm đến × mức một quán) · 10 điểm đến không có 5 sao (gói Đầy đủ dùng 4 sao tốt nhất) · 13 điểm tham quan giới hạn sức chứa/lượt · Cát Bà có phà · Phú Quốc, Côn Đảo chỉ bay · Đà Nẵng → Đà Nẵng, Cần Thơ → Cần Thơ là cùng nơi · 69/120 tuyến đường bộ trên 12 giờ. Điểm tham quan gắn mục đích: 77 nghỉ dưỡng, 39 gắn kết (một điểm có thể gắn cả hai).

## Video review

- **Cách lấy:** tìm trên YouTube 2 câu "review du lịch <nơi>" và "team building <nơi>" → lấy mã video theo thứ tự YouTube xếp → **kiểm từng link qua oEmbed chính thức** (video còn tồn tại, công khai; lấy tiêu đề + kênh từ YouTube) → chỉ giữ video có **tên nơi trong tiêu đề** (so không dấu) → tối đa 3 review + 2 team building / nơi. Không tải video, không lưu ảnh hay bình luận.
- **Kết quả (kiểm 27/11/2026):** 119 video lấy được → **loại thủ công 7** (đọc từng tiêu đề; lý do ghi ở `da_loai_thu_cong` trong file: 2 trùng tiêu đề, 2 quay ở Đà Lạt chứ không phải Tây Ninh, 1 nội dung chê bai, 2 không phải team building công ty) → còn **112 video: 70 review + 42 team building**, 24/24 điểm đến có review, 23/24 có video team building (Tây Ninh không còn video đúng nơi). Không trùng link.
- **Giới hạn:** thứ tự do YouTube xếp, nhóm chỉ lọc theo tiêu đề, chưa xem hết nội dung; video có thể bị gỡ sau ngày kiểm (`ngay_kiem` trong file). Nên xem qua video sẽ chiếu trước khi demo.

## Nguồn giá (xem 27/11/2026) và độ tin cậy

| Nhóm giá | Mốc có nguồn | Độ tin cậy |
|---|---|---|
| Vé máy bay | blog Vietnam Tourism 2026 (HAN-PQC 1,2–2tr, HAN-CXR 1–1,8tr, SGN-HAN 1–1,7tr); Vietnam Airlines (giá "từ" theo ngày) | vừa / cao |
| Thuê xe | báo giá mẫu 45 chỗ HN - Hạ Long 400 km = 4,5tr; VnExpress 16 chỗ 200 km ≈ 1,8tr | **thấp** |
| Phòng | KAYAK Đà Lạt 3★ 261.000–757.000đ, 4★ từ 968.000đ; bài Vinpearl Phú Quốc (theo người, tự quảng bá) | vừa / thấp |
| Ăn | Nha Trang tầm trung 200.000–300.000đ/người; InterContinental Nha Trang set trưa 350.000đ++ | vừa / cao |
| Team building, gala, spa, BBQ, phà | không tìm được giá theo người đáng tin | **ước tính** |

Link đầy đủ trong `gia_chuan.json`.

## Kiểm tra

- **So với giá tour có nguồn:** gói Tiết kiệm Hà Nội → Hạ Long 3 ngày, 40 người, gắn kết (`tinh_thu.py`) = **2,75 triệu/người**; tour ghép đoàn có nguồn: Sầm Sơn 3N2Đ 2,8–3,25 triệu, Hạ Long 3N2Đ 3,16 triệu. Cùng khoảng. (Bản đầu giá ăn 150.000đ cho ra 1,44 triệu/người, thấp hơn mốc có nguồn → nâng lên 200.000đ.)
- **Bộ tính tham chiếu:** tổng các dòng = tổng gói (kiểm bằng `--json`); đoàn 500 người báo đúng CHIA_QUAN, CHIA_2_KHACH_SAN, BO_DIEM_SUC_CHUA; điểm đến ngoài dữ liệu, số người ngoài 5–500 bị từ chối; ngân sách quá thấp báo ngân sách tối thiểu.
- **Giới hạn:** giá chưa tính mùa cao điểm, lễ Tết · số phòng, sức chứa là giả lập · thời gian đường bộ dài có thể cao hơn thực tế (hệ số 1,3) · không kiểm cặp sân bay có chuyến bay thẳng hay không, không giới hạn số ghế (Côn Đảo thực tế ít ghế) · chưa tính phí cầu đường, VAT riêng, hướng dẫn viên, bảo hiểm.
- **Người kiểm tay:** __ (điền tên) · số dòng đã kiểm: __. *Đề yêu cầu ghi người kiểm và số dòng đã kiểm tay.*

## Dữ liệu tham khảo không đưa vào repo (`data/raw/`, đã `.gitignore`)

| Bộ | Nguồn · giấy phép | Vì sao không dùng / không commit |
|---|---|---|
| SeanA91/vietnam | [Hugging Face](https://huggingface.co/datasets/SeanA91/vietnam) · MIT · commit `6508874` | Lịch trình thật của **một người** (Anh → VN, giá £, không có số người). Chỉ tham khảo định dạng; không commit vì là chuyến đi thật của người thật |
| Vietnam Tour Bookings | [Kaggle](https://www.kaggle.com/datasets/ngchno/vietnam-tour-bookings) · CC0 | Dữ liệu giả lập luyện làm sạch (trùng mã, giá âm, nhãn sai chính tả), 1–5 người, không có số ngày / lịch trình |
