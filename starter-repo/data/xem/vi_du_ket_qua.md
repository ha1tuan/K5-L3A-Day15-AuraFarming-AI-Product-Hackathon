# Ví dụ kết quả chạy trên bộ dữ liệu

Sinh bằng `python data/xuat_bang.py` (chạy `data/tinh_thu.py`). Mọi số do code tính trên `data/*.json`; giá là tham khảo / ước tính, khách sạn và nhà hàng là tên dựng.


## `python data/tinh_thu.py --tu 'Hà Nội' --den 'Hạ Long' --nguoi 40 --ngay 3 --muc-dich gan_ket --ngan-sach 150tr`

```text
Hà Nội → Hạ Long · 40 người · 3 ngày · Gắn kết đội nhóm · ngân sách đã hiểu: 150.000.000đ cho 40 người

■ Gói Tiết kiệm: 109.922.400đ cả đoàn · 2.748.060đ/người · xe xe_45_cho đường bộ 166 km (~3.8 giờ/chiều)
  TRONG ngân sách: chênh 40.077.600đ
  - [Di chuyển] Thuê 1 xe xe_45_cho (512 km, có tài xế): 512 × 11.500đ = 5.888.000đ (ước tính)
  - [Di chuyển] Phí lưu đêm tài xế: 2 × 500.000đ = 1.000.000đ (ước tính)
  - [Lưu trú] Khách sạn Hướng Dương Hạ Long (tên dựng) 2★: 10 phòng 4 người (40 người): 2 × 6.900.000đ = 13.800.000đ (ước tính)
  - [Ăn uống] Nhà hàng Thuyền Rồng Hạ Long (tên dựng): 40 người × 5 bữa chính (sức chứa 80): 200 × 170.000đ = 34.000.000đ (ước tính)
  - [Hoạt động] Chèo kayak vịnh Hạ Long (tham quan): 40 × 200.000đ = 8.000.000đ (ước tính)
  - [Hoạt động] Sun World Hạ Long (cáp treo Nữ Hoàng) (tham quan): 40 × 350.000đ = 14.000.000đ (ước tính)
  - [Hoạt động] Du thuyền vịnh Hạ Long (hang Sửng Sốt, đảo Ti Tốp) (tham quan): 40 × 450.000đ = 18.000.000đ (ước tính)
  - [Hoạt động] Tiệc BBQ ngoài trời cho đoàn (tên dựng) - Hạ Long (tiet_kiem): 40 × 250.000đ = 10.000.000đ (ước tính)
  - [Phát sinh] Dự phòng phát sinh 5%: 1 × 5.234.400đ = 5.234.400đ (ước tính)

■ Gói Cân bằng: 173.082.000đ cả đoàn · 4.327.050đ/người · xe xe_29_cho đường bộ 166 km (~3.8 giờ/chiều)
  VƯỢT ngân sách: chênh 23.082.000đ
  - [Di chuyển] Thuê 2 xe xe_29_cho (512 km, có tài xế): 1024 × 10.000đ = 10.240.000đ (ước tính)
  - [Di chuyển] Phí lưu đêm tài xế: 4 × 500.000đ = 2.000.000đ (ước tính)
  - [Lưu trú] Resort Đông Á Hạ Long (tên dựng) 4★: 10 phòng 4 người (40 người): 2 × 16.800.000đ = 33.600.000đ (ước tính)
  - [Ăn uống] Nhà hàng Gió Biển Hạ Long (tên dựng): 40 người × 5 bữa chính (sức chứa 150): 200 × 245.000đ = 49.000.000đ (ước tính)
  - [Hoạt động] Sun World Hạ Long (cáp treo Nữ Hoàng) (tham quan): 40 × 350.000đ = 14.000.000đ (ước tính)
  - [Hoạt động] Du thuyền vịnh Hạ Long (hang Sửng Sốt, đảo Ti Tốp) (tham quan): 40 × 450.000đ = 18.000.000đ (ước tính)
  - [Hoạt động] Chèo kayak vịnh Hạ Long (tham quan): 40 × 200.000đ = 8.000.000đ (ước tính)
  - [Hoạt động] Team building ngoài trời (đơn vị tổ chức, tên dựng) - Hạ Long (can_bang): 40 × 300.000đ = 12.000.000đ (ước tính)
  - [Hoạt động] Gala dinner có sân khấu, âm thanh, MC (tên dựng) - Hạ Long (can_bang): 40 × 450.000đ = 18.000.000đ (ước tính)
  - [Phát sinh] Dự phòng phát sinh 5%: 1 × 8.242.000đ = 8.242.000đ (ước tính)
  Vì sao vượt: vượt 23.082.000đ (15.4%). Khoản lớn nhất: Nhà hàng Gió Biển Hạ Long (tên dựng): 40 người × 5 49.000.000đ; Resort Đông Á Hạ Long (tên dựng) 4★: 10 phòng 4 ng 33.600.000đ; Du thuyền vịnh Hạ Long (hang Sửng Sốt, đảo Ti Tốp) 18.000.000đ
    · Bỏ gala dinner: tiết kiệm 18.900.000đ → còn 154.182.000đ
    · Bớt 1 ngày (2 ngày): tiết kiệm 48.930.000đ → còn 124.152.000đ
    · Hạ xuống gói Tiết kiệm: tiết kiệm 63.159.600đ → còn 109.922.400đ

■ Gói Đầy đủ: 299.006.400đ cả đoàn · 7.475.160đ/người · xe limousine_18_cho đường bộ 166 km (~3.8 giờ/chiều)
  VƯỢT ngân sách: chênh 149.006.400đ
  - [Di chuyển] Thuê 3 xe limousine_18_cho (512 km, có tài xế): 1536 × 13.000đ = 19.968.000đ (ước tính)
  - [Di chuyển] Phí lưu đêm tài xế: 6 × 500.000đ = 3.000.000đ (ước tính)
  - [Lưu trú] Resort Vạn Xuân Hạ Long (tên dựng) 5★: 10 phòng 4 người (40 người): 2 × 45.900.000đ = 91.800.000đ (ước tính)
  - [Ăn uống] Bếp Quê Hạ Long (tên dựng): 40 người × 5 bữa chính (sức chứa 200): 200 × 370.000đ = 74.000.000đ (ước tính)
  - [Hoạt động] Du thuyền vịnh Hạ Long (hang Sửng Sốt, đảo Ti Tốp) (tham quan): 40 × 450.000đ = 18.000.000đ (ước tính)
  - [Hoạt động] Sun World Hạ Long (cáp treo Nữ Hoàng) (tham quan): 40 × 350.000đ = 14.000.000đ (ước tính)
  - [Hoạt động] Chèo kayak vịnh Hạ Long (tham quan): 40 × 200.000đ = 8.000.000đ (ước tính)
  - [Hoạt động] Team building ngoài trời (đơn vị tổ chức, tên dựng) - Hạ Long (day_du): 40 × 550.000đ = 22.000.000đ (ước tính)
  - [Hoạt động] Gala dinner có sân khấu, âm thanh, MC (tên dựng) - Hạ Long (day_du): 40 × 850.000đ = 34.000.000đ (ước tính)
  - [Phát sinh] Dự phòng phát sinh 5%: 1 × 14.238.400đ = 14.238.400đ (ước tính)
  Vì sao vượt: vượt 149.006.400đ (99.3%). Khoản lớn nhất: Resort Vạn Xuân Hạ Long (tên dựng) 5★: 10 phòng 4  91.800.000đ; Bếp Quê Hạ Long (tên dựng): 40 người × 5 bữa chính 74.000.000đ; Gala dinner có sân khấu, âm thanh, MC (tên dựng) - 34.000.000đ
    · Bỏ gala dinner: tiết kiệm 35.700.000đ → còn 263.306.400đ
    · Bớt 1 ngày (2 ngày): tiết kiệm 91.707.000đ → còn 207.299.400đ
    · Hạ xuống gói Cân bằng: tiết kiệm 125.924.400đ → còn 173.082.000đ

Video review:
  ▶ [review] Kinh nghiệm du lịch HẠ LONG - Lịch trình chi tiết 2N1Đ cùng top trải n · Tripdi · https://www.youtube.com/watch?v=YvBiGxfhsJc
  ▶ [review] Du Lịch Hạ Long 3 Ngày 2 Đêm Tự Túc - Lịch Trình Chi Tiết · Hải Phòng Trong Tôi · https://www.youtube.com/watch?v=L3aRY4maQ6Q
  ▶ [team_building] Kỷ niệm Chương trình Team Building Hạ Long 2026 · Dược Phẩm Trung Ương I - Pharbaco · https://www.youtube.com/watch?v=odA0VIllQyw
  ▶ [team_building] TEAMBUILDING hạ long 2025 · team building quảng ninh  · https://www.youtube.com/watch?v=wHxKoWaB9Vo
```


## `python data/tinh_thu.py --tu TP.HCM --den 'Vũng Tàu' --nguoi 30 --ngay 2 --muc-dich nghi_duong`

```text
TP.HCM → Vũng Tàu · 30 người · 2 ngày · Nghỉ dưỡng

■ Gói Tiết kiệm: 27.781.950đ cả đoàn · 926.065đ/người · xe xe_45_cho đường bộ 83 km (~1.7 giờ/chiều)
  - [Di chuyển] Thuê 1 xe xe_45_cho (286 km, có tài xế): 286 × 11.500đ = 3.289.000đ (ước tính)
  - [Di chuyển] Phí lưu đêm tài xế: 1 × 500.000đ = 500.000đ (ước tính)
  - [Lưu trú] Khách sạn Hướng Dương Vũng Tàu (tên dựng) 2★: 1 phòng 2 người + 7 phòng 4 người (30 người): 1 × 5.720.000đ = 5.720.000đ (ước tính)
  - [Ăn uống] Nhà hàng Hội Ngộ Vũng Tàu (tên dựng): 30 người × 3 bữa chính (sức chứa 80): 90 × 185.000đ = 16.650.000đ (ước tính)
  - [Hoạt động] Bãi Sau (tham quan): 30 × 0đ = 0đ (ước tính)
  - [Hoạt động] Hải đăng Vũng Tàu (tham quan): 30 × 10.000đ = 300.000đ (ước tính)
  - [Hoạt động] Thời gian tự do nghỉ ngơi tại nơi ở: 30 × 0đ = 0đ
  - [Phát sinh] Dự phòng phát sinh 5%: 1 × 1.322.950đ = 1.322.950đ (ước tính)

■ Gói Cân bằng: 59.577.000đ cả đoàn · 1.985.900đ/người · xe xe_29_cho đường bộ 83 km (~1.7 giờ/chiều)
  - [Di chuyển] Thuê 2 xe xe_29_cho (286 km, có tài xế): 572 × 10.000đ = 5.720.000đ (ước tính)
  - [Di chuyển] Phí lưu đêm tài xế: 2 × 500.000đ = 1.000.000đ (ước tính)
  - [Lưu trú] Resort Trường Sơn Vũng Tàu (tên dựng) 4★: 1 phòng 2 người + 7 phòng 4 người (30 người): 1 × 13.270.000đ = 13.270.000đ (ước tính)
  - [Ăn uống] Buffet Đại Dương Vũng Tàu (tên dựng): 30 người × 3 bữa chính (sức chứa 100): 90 × 250.000đ = 22.500.000đ (ước tính)
  - [Hoạt động] Hải đăng Vũng Tàu (tham quan): 30 × 10.000đ = 300.000đ (ước tính)
  - [Hoạt động] Bạch Dinh (tham quan): 30 × 15.000đ = 450.000đ (ước tính)
  - [Hoạt động] Spa, massage thư giãn (tên dựng) - Vũng Tàu (can_bang): 30 × 450.000đ = 13.500.000đ (ước tính)
  - [Hoạt động] Thời gian tự do nghỉ ngơi tại nơi ở: 30 × 0đ = 0đ
  - [Phát sinh] Dự phòng phát sinh 5%: 1 × 2.837.000đ = 2.837.000đ (ước tính)

■ Gói Đầy đủ: 128.578.800đ cả đoàn · 4.285.960đ/người · xe limousine_18_cho đường bộ 83 km (~1.7 giờ/chiều)
  - [Di chuyển] Thuê 2 xe limousine_18_cho (286 km, có tài xế): 572 × 13.000đ = 7.436.000đ (ước tính)
  - [Di chuyển] Phí lưu đêm tài xế: 2 × 500.000đ = 1.000.000đ (ước tính)
  - [Lưu trú] Resort Vạn Xuân Vũng Tàu (tên dựng) 5★: 1 phòng 2 người + 7 phòng 4 người (30 người): 1 × 33.320.000đ = 33.320.000đ (ước tính)
  - [Ăn uống] Nhà hàng Thuyền Rồng Vũng Tàu (tên dựng): 30 người × 3 bữa chính (sức chứa 60): 90 × 405.000đ = 36.450.000đ (ước tính)
  - [Hoạt động] Bạch Dinh (tham quan): 30 × 15.000đ = 450.000đ (ước tính)
  - [Hoạt động] Hải đăng Vũng Tàu (tham quan): 30 × 10.000đ = 300.000đ (ước tính)
  - [Hoạt động] Spa, massage thư giãn (tên dựng) - Vũng Tàu (day_du): 30 × 900.000đ = 27.000.000đ (ước tính)
  - [Hoạt động] Tiệc BBQ ngoài trời cho đoàn (tên dựng) - Vũng Tàu (day_du): 30 × 550.000đ = 16.500.000đ (ước tính)
  - [Hoạt động] Thời gian tự do nghỉ ngơi tại nơi ở: 30 × 0đ = 0đ
  - [Phát sinh] Dự phòng phát sinh 5%: 1 × 6.122.800đ = 6.122.800đ (ước tính)

Video review:
  ▶ [review] Du Lịch Vũng Tàu Mới Nhất 2026 | Hướng Dẫn Tất Tần Tật Đi Đâu Ăn Gì Ch · Nhật Ký Du Lịch · https://www.youtube.com/watch?v=i-tjHeT79U8
  ▶ [review] Hướng Dẫn Du Lịch Vũng Tàu 2025 | Ăn Gì Chơi Gì Tại Vũng Tàu Chi Tiết  · Nhật Ký Du Lịch · https://www.youtube.com/watch?v=yXOjiRW3LwE
  ▶ [review] Top 20 địa điểm du lịch Vũng Tàu nên đi nhất trong 2022 · Blog Du Lịch · https://www.youtube.com/watch?v=5qxx4UmrOnI
  ▶ [team_building] TEAM BUILDING ALPLA VIỆT NAM | VŨNG TÀU 2026 · Du Lịch Ocean · https://www.youtube.com/watch?v=YJo5kfhMW3g
  ▶ [team_building] Đi Team Building Có Gì Vui? Vũng Tàu 2 Ngày 1 Đêm · Toàn Saigon · https://www.youtube.com/watch?v=PfnaTRExs0A
```


## `python data/tinh_thu.py --tu TP.HCM --ngan-sach 3tr --moi-nguoi --nguoi 60 --ngay 3 --muc-dich nghi_duong`

```text
Gợi ý từ TP.HCM · 60 người · 3 ngày · Nghỉ dưỡng · ngân sách đã hiểu: 180.000.000đ cho 60 người
7 nơi vừa ngân sách. Top 3:

1. Hồ Tràm - Long Hải (Nam) · điểm 57.8 · resort biển cao cấp, sân team building trên cát
   Tiết kiệm     125.693.400đ (2.094.890đ/người) ✓
   Cân bằng      248.619.000đ (4.143.650đ/người) vượt
   Đầy đủ        459.891.600đ (7.664.860đ/người) vượt
   → đề xuất gói Tiết kiệm, xe xe_45_cho đường bộ 108 km
  ▶ [review] Top 5 Khách sạn Đẹp Nhất Hồ Tràm - Long Hải - Phước Hải · Review Du Lịch Việt Nam · https://www.youtube.com/watch?v=fYoPzHOhFvA
  ▶ [review] Khám Phá Hồ Tràm - Vũng Tàu 2025 | Hướng Dẫn Những Điểm Vui Chơi Tắm B · Nhật Ký Du Lịch · https://www.youtube.com/watch?v=xhaJHVWC-BQ
  ▶ [review] Tour Du lịch Long Hải Hồ Tràm 1 Hướng Dẫn Viên Chuyên Nghiệp · NẮNG MỚI  · https://www.youtube.com/watch?v=iK1kUH4hDw0
  ▶ [team_building] [Official Recap] Team Building Hồ Tràm 2026 | Mừng HQG 16 Năm Thành Lậ · Công Nghệ HQG · https://www.youtube.com/watch?v=ERHJ_lrqM-8
  ▶ [team_building] Mắt Kính TUYẾT HÀ Du Lịch Hồ Tràm Kết Hợp TEAMBUILDING SUMMER VACATION · Công Ty TNHH Du Lịch INTOUR · https://www.youtube.com/watch?v=k7AidVaaT5Y

2. Phan Thiết - Mũi Né (Nam) · điểm 55.0 · đồi cát, resort biển, cao tốc từ TP.HCM
   Tiết kiệm     107.767.800đ (1.796.130đ/người) ✓
   Cân bằng      192.528.000đ (3.208.800đ/người) vượt
   Đầy đủ        381.742.200đ (6.362.370đ/người) vượt
   → đề xuất gói Tiết kiệm, xe xe_45_cho đường bộ 226 km
  ▶ [review] YDL #297: Phan Thiết - Mũi Né cảnh đẹp, nhiều món ngon: lẩu thả, bánh  · Yêu Máy Bay · https://www.youtube.com/watch?v=7vOeDlyrbug
  ▶ [review] Đồ ăn Phan Thiết quá ngon! 2N1Đ khám phá Mũi Né, Bàu Trắng & food tour · Leo Singto · https://www.youtube.com/watch?v=QcCXgh-OXqc
  ▶ [review] Du Lịch Mũi Né - Phan Thiết 2026 | Đi Đâu Chơi Gì Ăn Gì Chi Tiết Và Mớ · Nhật Ký Du Lịch · https://www.youtube.com/watch?v=UPpky126WY4
  ▶ [team_building] Hành trình du lịch Teambuilding 3 ngày tại Mũi Né - Phan Thiết | Chai  · Salub Viet Nam · https://www.youtube.com/watch?v=B_qGXKvW0L4
  ▶ [team_building] TEAMBUILDING PHAN THIẾT - MŨI NÉ 2025 · VinaGreen Plus Official · https://www.youtube.com/watch?v=6HanYGH9cbk

3. Đà Lạt (Trung) · điểm 53.0 · cao nguyên mát, đồi thông, không có biển; đường đèo
   Tiết kiệm     116.661.300đ (1.944.355đ/người) ✓
   Cân bằng      207.438.000đ (3.457.300đ/người) vượt
   Đầy đủ        396.862.200đ (6.614.370đ/người) vượt
   → đề xuất gói Tiết kiệm, xe xe_45_cho đường bộ 301 km
  ▶ [review] Du Lịch ĐÀ LẠT 2026. Lịch Trình 3 Ngày 2 Đêm Ăn Gì Chơi Gì Tại Đà Lạt. · Toro Pan · https://www.youtube.com/watch?v=lNQwvC_P6-0
  ▶ [review] Đà Lạt lạnh teo, cải tạo hồ Xuân Hương, khai mạc Festival? · ĐÀ LẠT STREET (NHÂN LA CÀ) · https://www.youtube.com/watch?v=OV1urvr4jos
  ▶ [review] Du Lịch Đà Lạt 4N3Đ Mới Nhất 2026 | Trọn Vẹn Ăn Gì Chơi Gì Đi Đâu Ngắm · Nhật Ký Du Lịch · https://www.youtube.com/watch?v=ONNqtYuejvc
  ▶ [team_building] Hành trình Team Building 2025 tại Đà Lạt cùng công ty MAC USA ONE tiêu · BI Travel Official · https://www.youtube.com/watch?v=BZGBf8WyGeg
  ▶ [team_building] TEAM BUILDING TẠI ĐÀ LẠT | TRÒ CHƠI HẤP DẪN | QUÀ TẶNG GIÁ TRỊ LÊN ĐẾN · Bazan Travel · https://www.youtube.com/watch?v=ey-pQ9MuJag
```


## `python data/tinh_thu.py --tu 'Hà Nội' --ngan-sach 20tr --nguoi 50 --ngay 3 --muc-dich gan_ket`

```text
Gợi ý từ Hà Nội · 50 người · 3 ngày · Gắn kết đội nhóm · ngân sách đã hiểu: 20.000.000đ cho 50 người
Không nơi nào vừa ngân sách. Cần tối thiểu 83.697.600đ (gói rẻ nhất: Sầm Sơn).
```
