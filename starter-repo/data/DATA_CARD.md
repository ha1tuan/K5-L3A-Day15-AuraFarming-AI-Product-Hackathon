# Data card: dữ liệu bản chạy thử dùng

> Một trang. Dữ liệu chạy thử cho agent lập kế hoạch du lịch công ty (Track C): đầu vào điểm đi, điểm đến, số người, kinh phí, số ngày → 3 kế hoạch **Tiết kiệm · Cân bằng · Đầy đủ**.
> Dữ liệu tự dựng **không phải bằng chứng pain** (bằng chứng ở `evidence/`).

## Tóm tắt

| File | Nội dung | Số dòng | Nhãn |
|---|---|---|---|
| `gia_chuan.json` | Giá chuẩn: vé máy bay, thuê xe, phòng theo hạng sao, suất ăn, team building, gala; **mỗi số có link + ngày xem + độ tin cậy** | 6 nhóm giá | thật (có nguồn) + ước tính |
| `diem_den.json` | 3 điểm đi (Hà Nội, Đà Nẵng, TP.HCM) · 6 điểm đến (Hạ Long, Sầm Sơn, Đà Nẵng - Hội An, Nha Trang, Đà Lạt, Phú Quốc), toạ độ xấp xỉ | 3 + 6 | thật (công khai) |
| `di_chuyen.json` | 4 loại xe + 18 tuyến điểm đi × điểm đến: km và giờ đường bộ, chặng bay, giá vé | 18 tuyến | `synthetic` (tính từ toạ độ + giá chuẩn) |
| `khach_san.json` | 6 điểm đến × 3 mức × 3 khách sạn, mỗi khách sạn có loại phòng 2/3/4 người, giá/đêm, số phòng | 54 | `synthetic`, **tên dựng** |
| `nha_hang.json` | 6 × 3 mức × 3 quán: sức chứa, giá/người/bữa, giờ mở | 54 | `synthetic`, **tên dựng** |
| `hoat_dong.json` | Điểm tham quan **tên thật** (giá, giờ ước tính) + team building, gala theo mức | 51 | tên thật + giá ước tính |
| `muc_goi.json` | Quy tắc 3 gói: hạng sao, loại xe, mức ăn, có team building/gala không, khi nào đi máy bay, khung giờ | 1 | quy tắc nhóm tự đặt |

## Cách dựng

- **Script:** `python data/sinh_du_lieu.py` (chỉ thư viện chuẩn), **seed = 42**. Chạy lại ra đúng cùng nội dung (đã kiểm: hash 6 file trùng nhau giữa 2 lần chạy). `--kiem` chỉ in bảng kiểm, không ghi file.
- **Giá:** sinh quanh giá chuẩn trong `gia_chuan.json` (phòng: ×0,85–1,2; ăn: ×0,85–1,15 × hệ số điểm đến), làm tròn 10.000đ / 5.000đ. Phòng 3, 4 người = giá phòng đôi × 1,35 / 1,6.
- **Di chuyển:** đường bộ = khoảng cách chim bay × 1,3; xe 50 km/h + 30 phút nghỉ mỗi 3 giờ. Đường bay 700 km/h + thủ tục, đưa đón 2,5 giờ. Vé: dùng mốc có nguồn nếu có (HAN-PQC, HAN-CXR), không thì 600.000đ + 900đ/km (*tự ước tính*, khớp các mốc trong khoảng ±20%).
- **Tên dựng:** khách sạn, nhà hàng có hậu tố "(tên dựng)" và `"ten_dung": true`. Không nêu tên cơ sở thật với giá không kiểm được. Điểm tham quan (Bà Nà, VinWonders, vịnh Hạ Long…) là tên thật, giá và giờ mở **ước tính**.
- **Chỗ khó cài sẵn** (để bộ câu thử chạm được, tránh "data quá sạch"): 18 khách sạn không có phòng 4 người · 21 khách sạn nhỏ (≤40 phòng) → đoàn lớn thiếu phòng · mỗi điểm đến có quán 25 chỗ chỉ mở trưa · 3 điểm đóng cửa thứ Hai · 4 tour giới hạn sức chứa (80–150) · Sầm Sơn thiếu 5 sao cho gói Đầy đủ · Phú Quốc chỉ đường bay · Đà Nẵng → Đà Nẵng - Hội An là cùng nơi · 10 tuyến đường bộ trên 12 giờ.

## Nguồn giá (xem 27/11/2026) và độ tin cậy

| Nhóm giá | Mốc có nguồn | Độ tin cậy |
|---|---|---|
| Vé máy bay | blog Vietnam Tourism 2026 (HAN-PQC 1,2–2tr, HAN-CXR 1–1,8tr, SGN-HAN 1–1,7tr); trang Vietnam Airlines (giá "từ" theo ngày) | vừa / cao |
| Thuê xe | báo giá mẫu 45 chỗ HN - Hạ Long 400 km = 4,5tr; VnExpress 16 chỗ 200 km ≈ 1,8tr | **thấp** (mẫu "20xx", bài cũ) |
| Phòng | KAYAK Đà Lạt 3★ 261.000–757.000đ, 4★ từ 968.000đ; bài Vinpearl về Phú Quốc (tính theo người, tự quảng bá) | vừa / thấp |
| Ăn | Nha Trang tầm trung 200.000–300.000đ/người; InterContinental Nha Trang set trưa 350.000đ++ | vừa / cao |
| Team building, gala | không tìm được giá theo người đáng tin | **ước tính** |

Link đầy đủ trong `gia_chuan.json`.

## Kiểm tra và giới hạn

- **Bảng kiểm** (in khi chạy script): gói Tiết kiệm Hà Nội → Sầm Sơn 3N2Đ, 40 người (xe 45 chỗ, 10 phòng 4 người, 5 bữa) ≈ **1,44 triệu/người**. Tour ghép đoàn có nguồn: **2,8–3,25 triệu/người**. Lệch vì (1) tour gồm lợi nhuận công ty lữ hành, hướng dẫn viên, bảo hiểm, vé tham quan; (2) giá xe dựa trên nguồn cũ, có thể thấp. Bản đầu giá ăn 150.000đ → nâng lên 200.000đ (cận dưới mốc có nguồn) sau bảng kiểm.
- **Giới hạn:** giá thay đổi theo mùa, ngày lễ (chưa mô hình hoá cao điểm) · số phòng, sức chứa là giả lập · thời gian đường bộ đường dài có thể cao hơn thực tế (hệ số 1,3) · chưa tính phí cầu đường, VAT riêng.
- **Người kiểm tay:** __ (điền tên) · số dòng đã kiểm: __ / 165. *Đề yêu cầu ghi người kiểm và số dòng đã kiểm tay.*

## Dữ liệu tham khảo không đưa vào repo (`data/raw/`, đã `.gitignore`)

| Bộ | Nguồn · giấy phép | Vì sao không dùng / không commit |
|---|---|---|
| SeanA91/vietnam | [Hugging Face](https://huggingface.co/datasets/SeanA91/vietnam) · MIT · commit `6508874` | Lịch trình thật của **một người** (Anh → VN, giá £, không có số người). Chỉ tham khảo định dạng kế hoạch từng dòng; không commit vì là chuyến đi thật của người thật |
| Vietnam Tour Bookings | [Kaggle](https://www.kaggle.com/datasets/ngchno/vietnam-tour-bookings) · CC0 | Dữ liệu giả lập luyện làm sạch (trùng mã, giá âm, nhãn sai chính tả), số người 1–5, không có số ngày / lịch trình; giá mọi điểm đến gần như ngang nhau → không dùng làm nguồn giá |
