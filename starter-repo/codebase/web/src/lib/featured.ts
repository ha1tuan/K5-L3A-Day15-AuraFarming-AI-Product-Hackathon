// SINH TỰ ĐỘNG bởi scripts/sinh_diem_noi_bat.py từ data/*.json — không sửa tay.
// price_from / price_mid: gói Tiết kiệm / Cân bằng mỗi người, 30 người, 3N2Đ, từ điểm đi gần nhất (tham khảo).
export interface FeaturedVideo { id: string; title: string; channel: string; kind: string }
export interface Featured { id: string; name: string; province: string; region: 'Bắc' | 'Trung' | 'Nam'; desc: string; season: string; scenery: string[]; fit: { nghi_duong: number; gan_ket: number }; island: boolean; from: string; travel: string; hours: number; price_from: number; price_mid: number; videos: FeaturedVideo[] }
export const FEATURED: Featured[] = [
 {
  "id": "halong",
  "name": "Hạ Long",
  "province": "Quảng Ninh",
  "region": "Bắc",
  "desc": "vịnh di sản, du thuyền, khu vui chơi, resort nhận đoàn lớn",
  "season": "4–10",
  "scenery": [
   "bien",
   "vinh"
  ],
  "fit": {
   "nghi_duong": 3,
   "gan_ket": 3
  },
  "island": false,
  "from": "Hải Phòng",
  "travel": "xe 45 chỗ đường bộ 55 km",
  "hours": 1.1,
  "price_from": 2109000,
  "price_mid": 4288000,
  "videos": [
   {
    "id": "YvBiGxfhsJc",
    "title": "Kinh nghiệm du lịch HẠ LONG - Lịch trình chi tiết 2N1Đ cùng top trải nghiệm đáng giá nhất",
    "channel": "Tripdi",
    "kind": "review"
   },
   {
    "id": "L3aRY4maQ6Q",
    "title": "Du Lịch Hạ Long 3 Ngày 2 Đêm Tự Túc - Lịch Trình Chi Tiết",
    "channel": "Hải Phòng Trong Tôi",
    "kind": "review"
   },
   {
    "id": "odA0VIllQyw",
    "title": "Kỷ niệm Chương trình Team Building Hạ Long 2026",
    "channel": "Dược Phẩm Trung Ương I - Pharbaco",
    "kind": "team_building"
   },
   {
    "id": "wHxKoWaB9Vo",
    "title": "TEAMBUILDING hạ long 2025",
    "channel": "team building quảng ninh ",
    "kind": "team_building"
   }
  ]
 },
 {
  "id": "catba",
  "name": "Cát Bà",
  "province": "Hải Phòng",
  "region": "Bắc",
  "desc": "đảo có phà, vịnh Lan Hạ, kayak, rừng quốc gia",
  "season": "5–9",
  "scenery": [
   "bien",
   "dao",
   "rung"
  ],
  "fit": {
   "nghi_duong": 2,
   "gan_ket": 3
  },
  "island": false,
  "from": "Hải Phòng",
  "travel": "xe 45 chỗ đường bộ 52 km",
  "hours": 2.0,
  "price_from": 2459000,
  "price_mid": 4242000,
  "videos": [
   {
    "id": "SOcyOUddAIM",
    "title": "KINH NGHIỆM DU LỊCH CÁT BÀ TỰ TÚC CHI TIẾT TỪ A - Z",
    "channel": "Xẻo Travel",
    "kind": "review"
   },
   {
    "id": "leOBCm1PFKw",
    "title": "Trọn bộ kinh nghiệm du lịch Cát Bà: Ăn gì, chơi gì, ở đâu?",
    "channel": "Wiki Du lịch",
    "kind": "review"
   },
   {
    "id": "5pLXSTSw2pk",
    "title": "Du Lịch Cát Bà 2026 | Review Toàn Bộ Thị Trấn Biển Đẹp Bậc Nhất Miền Bắc",
    "channel": "Hải Phòng Trong Tôi",
    "kind": "review"
   },
   {
    "id": "7x_8TP81p00",
    "title": "CÁT BÀ ODYSSEY | YIC ONE TEAM BUILDING 2026",
    "channel": "YIC HIDDEN CHAMPION ",
    "kind": "team_building"
   },
   {
    "id": "vpTjwGHm3fA",
    "title": "TVL TEAM BUILDING CÁT BÀ 2026",
    "channel": "Inox Quốc Tế TVL",
    "kind": "team_building"
   }
  ]
 },
 {
  "id": "samson",
  "name": "Sầm Sơn",
  "province": "Thanh Hoá",
  "region": "Bắc",
  "desc": "biển giá mềm, hải sản, nhiều nhà hàng nhận đoàn đông",
  "season": "5–8",
  "scenery": [
   "bien"
  ],
  "fit": {
   "nghi_duong": 2,
   "gan_ket": 3
  },
  "island": false,
  "from": "Hà Nội",
  "travel": "xe 45 chỗ đường bộ 187 km",
  "hours": 4.2,
  "price_from": 1785000,
  "price_mid": 3320000,
  "videos": [
   {
    "id": "Z7UKqKgy-bE",
    "title": "KINH NGHIỆM DU LỊCH SẦM SƠN TỰ TÚC CHI TIẾT TỪ A - Z",
    "channel": "Xẻo Travel",
    "kind": "review"
   },
   {
    "id": "28n7knh-uf8",
    "title": "Du Lịch Biển Sầm Sơn Thanh Hóa 2025 | Hướng Dẫn Ăn Gì Chơi Gì Tại Sầm Sơn Chi Tiết Và Mới Nhất",
    "channel": "Nhật Ký Du Lịch",
    "kind": "review"
   },
   {
    "id": "8RiDq3FSXuQ",
    "title": "Lịch trình du lịch Sầm Sơn 2 ngày 1 đêm & những lưu  ý \"xương máu\" để không bị chặt chém",
    "channel": "Wiki Du lịch",
    "kind": "review"
   },
   {
    "id": "-7sKPSlbhaQ",
    "title": "[Team Building 2025] Nitto Việt Nam (11/07/2025) | Sầm Sơn - Thanh Hóa",
    "channel": "Sen Xanh Event & Teambuilding",
    "kind": "team_building"
   },
   {
    "id": "so8-EsyXQwU",
    "title": "Du lịch Sầm Sơn Team Building - Dệt May Minh Quân Mỹ Đức",
    "channel": "LET'S TOUR",
    "kind": "team_building"
   }
  ]
 },
 {
  "id": "cualo",
  "name": "Cửa Lò",
  "province": "Nghệ An",
  "region": "Bắc",
  "desc": "biển bình dân, gần quê Bác, đảo Ngư",
  "season": "5–8",
  "scenery": [
   "bien"
  ],
  "fit": {
   "nghi_duong": 2,
   "gan_ket": 2
  },
  "island": false,
  "from": "Hà Nội",
  "travel": "xe 45 chỗ đường bộ 320 km",
  "hours": 7.4,
  "price_from": 1919000,
  "price_mid": 3703000,
  "videos": [
   {
    "id": "z95Ym91fUfI",
    "title": "Du lịch biển Cửa Lò Nghệ An cùng gia đình người đông như kiến",
    "channel": "Lúa miền Trung ",
    "kind": "review"
   },
   {
    "id": "vvFuN-B89jM",
    "title": "KINH NGHIỆM DU LỊCH CỬA LÒ TỰ TÚC CHI TIẾT TỪ A - Z | ĂN GÌ, CHƠI GÌ, Ở ĐÂU??",
    "channel": "Xẻo Travel",
    "kind": "review"
   },
   {
    "id": "iqJRhYi_tRI",
    "title": "Du Lịch Đảo Lan Châu - Biển Cửa Lò Nghệ An 2026 | Ăn Gì Chơi Gì Ở Đâu Chi Tiết Và Mới Nhất",
    "channel": "Nhật Ký Du Lịch",
    "kind": "review"
   },
   {
    "id": "S3dGmRLCu54",
    "title": "Team Building Cửa Lò 2025 | Không Khí Nhiệt Huyết & Gắn Kết",
    "channel": "CỬA LÒ TRAVEL ",
    "kind": "team_building"
   }
  ]
 },
 {
  "id": "ninhbinh",
  "name": "Ninh Bình",
  "province": "Ninh Bình",
  "region": "Bắc",
  "desc": "Tràng An, Tam Cốc, Bái Đính; gần Hà Nội, hợp đi 1–2 ngày",
  "season": "1–6",
  "scenery": [
   "di_san",
   "nui"
  ],
  "fit": {
   "nghi_duong": 2,
   "gan_ket": 2
  },
  "island": false,
  "from": "Hà Nội",
  "travel": "xe 45 chỗ đường bộ 114 km",
  "hours": 2.3,
  "price_from": 2123000,
  "price_mid": 3743000,
  "videos": [
   {
    "id": "d3R-VcIB3d4",
    "title": "3 ngày du lịch một mình Ninh Bình ᨒོ  solo trip vlog",
    "channel": "hà vy",
    "kind": "review"
   },
   {
    "id": "YXCVMnr7SYs",
    "title": "KINH NGHIỆM DU LỊCH NINH BÌNH TỰ TÚC CHI TIẾT",
    "channel": "Xẻo Travel",
    "kind": "review"
   },
   {
    "id": "7as0dl2aujg",
    "title": "DU LỊCH NINH BÌNH. Review Thung Nham , Tam Cốc , Phố Cổ Hoa Lư, Chùa Bái Đính . Vietnam travel",
    "channel": "Toro Pan",
    "kind": "review"
   },
   {
    "id": "ywM7PU6kxu8",
    "title": "Những Khoảnh Khắc Ấn Tượng Team Building 2023 tại Ninh Bình | GreenYellow Vietnam Team Outing 2023",
    "channel": "GreenYellow Vietnam",
    "kind": "team_building"
   },
   {
    "id": "hZOm6pOph9I",
    "title": "Amazing Race Ninh Binh [Amanotes Team Building 2022] - FULL | Exotic Vietnam",
    "channel": "Exotic Vietnam",
    "kind": "team_building"
   }
  ]
 },
 {
  "id": "sapa",
  "name": "Sa Pa",
  "province": "Lào Cai",
  "region": "Bắc",
  "desc": "núi, Fansipan, bản làng; đường cao tốc từ Hà Nội",
  "season": "9–5",
  "scenery": [
   "nui"
  ],
  "fit": {
   "nghi_duong": 3,
   "gan_ket": 2
  },
  "island": false,
  "from": "Hà Nội",
  "travel": "xe 45 chỗ đường bộ 330 km",
  "hours": 7.6,
  "price_from": 2412000,
  "price_mid": 4865000,
  "videos": [
   {
    "id": "s8zeA6_y_IE",
    "title": "Kinh Nghiệm Du Lịch Sa Pa Tự Túc Chi Tiết Nhất 2026",
    "channel": "Xẻo Travel",
    "kind": "review"
   },
   {
    "id": "DUK1kWtZB8Y",
    "title": "Review Best View Sa Pa: Địa điểm check-in săn mây đẹp nhất Sapa hiện nay?",
    "channel": "Hoàng Long",
    "kind": "review"
   },
   {
    "id": "E3qGiPSYxHk",
    "title": "Chương trình Teambuilding Cuộc Đua Kỳ Thú VP Bank tại Sa Pa - Đoàn Kết Đổi Mới, Bứt Phá Vươn Xa",
    "channel": "Ruộng Bậc Thang Travel",
    "kind": "team_building"
   },
   {
    "id": "kKUNAvAQ8wQ",
    "title": "COMPANY TRIP 2025 KAROFI GROUP – ĐỢT I | Sa Pa – Bản Mây",
    "channel": "Sen Xanh Event & Teambuilding",
    "kind": "team_building"
   }
  ]
 },
 {
  "id": "mocchau",
  "name": "Mộc Châu",
  "province": "Sơn La",
  "region": "Bắc",
  "desc": "cao nguyên, đồi chè, mùa hoa, cắm trại",
  "season": "11–4",
  "scenery": [
   "nui",
   "dong_co"
  ],
  "fit": {
   "nghi_duong": 2,
   "gan_ket": 2
  },
  "island": false,
  "from": "Hà Nội",
  "travel": "xe 45 chỗ đường bộ 167 km",
  "hours": 3.8,
  "price_from": 2345000,
  "price_mid": 4172000,
  "videos": [
   {
    "id": "lM4o5pz1S6c",
    "title": "Review du lịch Mộc Châu: đi mùa nào đẹp, ăn chơi tới bến chưa đến 2 triệu đồng",
    "channel": "Wiki Du lịch",
    "kind": "review"
   },
   {
    "id": "4Kas7VjrN_I",
    "title": "Bí kíp du lịch Mộc Châu trong 2 ngày 1 đêm - Tối ưu hóa thời gian, tận hưởng trọn vẹn",
    "channel": "DU LỊCH MỘC CHÂU",
    "kind": "review"
   },
   {
    "id": "5lxi9-mXt_0",
    "title": "Có Nên Đi Du Lịch Mộc Châu? Sự Thật Có Đẹp Như Lời Đồn? 😱",
    "channel": "Đi Để Cảm Nhận",
    "kind": "review"
   },
   {
    "id": "BuBcTOSsYpU",
    "title": "Team Minh Hằng - TT Miền Đông- Mộc Châu-Sapa- Ninh Bình Hà Nội - Hành Trình Về Nguồn T12.2025",
    "channel": "Ghiền du lịch teambuilding",
    "kind": "team_building"
   },
   {
    "id": "9IJ3VAUodNo",
    "title": "VDG TeamBuilding Mộc Châu - Mai Châu 2026",
    "channel": "jsc VUA ĐÓNG GÓI",
    "kind": "team_building"
   }
  ]
 },
 {
  "id": "tamdao",
  "name": "Tam Đảo",
  "province": "Vĩnh Phúc",
  "region": "Bắc",
  "desc": "thị trấn trên núi gần Hà Nội, mát mùa hè, ít khách sạn lớn",
  "season": "5–9",
  "scenery": [
   "nui"
  ],
  "fit": {
   "nghi_duong": 2,
   "gan_ket": 1
  },
  "island": false,
  "from": "Hà Nội",
  "travel": "xe 45 chỗ đường bộ 68 km",
  "hours": 1.4,
  "price_from": 2008000,
  "price_mid": 3445000,
  "videos": [
   {
    "id": "g2SpS9ag_w8",
    "title": "Review du lịch Tam Đảo có phải cực kỳ đắt đỏ như lời đồn? Đi mùa nào đẹp nhất?",
    "channel": "Wiki Du lịch",
    "kind": "review"
   },
   {
    "id": "9r9B4xHiUgE",
    "title": "Du Lịch Tam Đảo 2026 | Ăn Gì Chơi Gì Ở Đâu Chi Tiết Và Mới Nhất",
    "channel": "Nhật Ký Du Lịch",
    "kind": "review"
   },
   {
    "id": "rAhPNKLfLLA",
    "title": "Kinh Nghiệm Du Lịch Tam Đảo Tự Túc Chi Tiết Mới Nhất",
    "channel": "Xẻo Travel",
    "kind": "review"
   },
   {
    "id": "Q85OXoMkWB8",
    "title": "Team building song ngữ KISCO tại sân golf Tam Đảo 2026",
    "channel": "Trần Vũ",
    "kind": "team_building"
   },
   {
    "id": "2lwWLvKawYc",
    "title": "[TEAMBUILDING TAM ĐẢO] Khoảnh khắc BÙNG CHÁY!!! - Sinh nhật 7 tuổi FU Guitar Club",
    "channel": "FU Guitar Club",
    "kind": "team_building"
   }
  ]
 },
 {
  "id": "bavi",
  "name": "Ba Vì",
  "province": "Hà Nội",
  "region": "Bắc",
  "desc": "resort sinh thái, sân team building lớn, đi về trong ngày",
  "season": "quanh năm",
  "scenery": [
   "nui",
   "rung"
  ],
  "fit": {
   "nghi_duong": 2,
   "gan_ket": 3
  },
  "island": false,
  "from": "Hà Nội",
  "travel": "xe 45 chỗ đường bộ 66 km",
  "hours": 1.3,
  "price_from": 2327000,
  "price_mid": 3756000,
  "videos": [
   {
    "id": "hcXSbn8LHzM",
    "title": "Du lịch Ba Vì trong 1 ngày: Đi đâu, chơi gì, ăn gì? | Hanoi Review",
    "channel": "HTV - Đài Hà Nội",
    "kind": "review"
   },
   {
    "id": "PuEjUyga6o4",
    "title": "Du Lịch Ba Vì Hà Nội 2026 | Hướng Dẫn Ăn Gì Chơi Gì Ở Đâu Chi Tiết Và Mới Nhất",
    "channel": "Nhật Ký Du Lịch",
    "kind": "review"
   },
   {
    "id": "_bTbsOi_j00",
    "title": "TOP 8 Địa điểm du lịch giá rẻ tại Bà Vì Hà Nội siêu đẹp không thể bỏ qua | TOPBAG.vn",
    "channel": "TOPBAG",
    "kind": "review"
   },
   {
    "id": "wRqDfTHb7SI",
    "title": "Sân chơi team building ngoài trời lý tưởng tại Ba Vì #teambuilding #bavi #hoatdongngoaitroi",
    "channel": "Đông - Người ba vì",
    "kind": "team_building"
   },
   {
    "id": "rPuR0oJ4frM",
    "title": "Game Tháp Maslow tổ chức ở Ba Vì chạy bay tóc",
    "channel": "Thổ địa Ba Vì",
    "kind": "team_building"
   }
  ]
 },
 {
  "id": "phongnha",
  "name": "Quảng Bình (Phong Nha)",
  "province": "Quảng Bình",
  "region": "Trung",
  "desc": "hang động, zipline, mạo hiểm; biển Nhật Lệ",
  "season": "3–8",
  "scenery": [
   "hang_dong",
   "bien"
  ],
  "fit": {
   "nghi_duong": 1,
   "gan_ket": 3
  },
  "island": false,
  "from": "Đà Nẵng",
  "travel": "xe 45 chỗ đường bộ 346 km",
  "hours": 7.9,
  "price_from": 2517000,
  "price_mid": 4646000,
  "videos": [
   {
    "id": "I1igL0nTMI0",
    "title": "TOP các điểm du lịch đẹp nhất Quảng Bình 2025",
    "channel": "QUANGBINHGO- KINH NGHIỆM DU LỊCH QUẢNG BÌNH",
    "kind": "review"
   },
   {
    "id": "x4xxs9JAZp0",
    "title": "TOUR QUẢNG BÌNH 3 NGÀY 2 ĐÊM",
    "channel": "Netin Travel - Tour Du lịch Quảng Bình",
    "kind": "review"
   },
   {
    "id": "O1r-qrVvicY",
    "title": "Phần 1 - Review chuyến đi Quảng Bình 4 ngày 3 đêm #travel #trendingshorts #travelvlog #quangbinh",
    "channel": "Tien Pham",
    "kind": "review"
   },
   {
    "id": "6RweMyEKX1o",
    "title": "HTCONS - TEAMBUILDING QUẢNG BÌNH 2026 by UNTRA GROUP",
    "channel": "UNTRA GROUP - Du Lịch Độc Đáo",
    "kind": "team_building"
   }
  ]
 },
 {
  "id": "hue",
  "name": "Huế",
  "province": "Thừa Thiên Huế",
  "region": "Trung",
  "desc": "cố đô, lăng tẩm, ca Huế trên sông Hương",
  "season": "1–8",
  "scenery": [
   "di_san",
   "thanh_pho"
  ],
  "fit": {
   "nghi_duong": 2,
   "gan_ket": 2
  },
  "island": false,
  "from": "Đà Nẵng",
  "travel": "xe 45 chỗ đường bộ 103 km",
  "hours": 2.1,
  "price_from": 2360000,
  "price_mid": 3947000,
  "videos": [
   {
    "id": "XIs0d5ORrGQ",
    "title": "Huế 1 Ngày Lang Thang Cố Đô | Vlog Du Lịch Huế Chill Nhất",
    "channel": "Cuong Cowboy",
    "kind": "review"
   },
   {
    "id": "yOKNunmKLwI",
    "title": "Kinh Nghiệm Du Lịch Huế Từ A-Z - Tất Tần Tật Ăn Gì Chơi Gì?",
    "channel": "Xẻo Travel",
    "kind": "review"
   },
   {
    "id": "941sfYBOHow",
    "title": "KINH NGHIỆM DU LỊCH HUẾ TỰ TÚC TIẾT KIỆM CHI PHÍ",
    "channel": "Xẻo Travel",
    "kind": "review"
   },
   {
    "id": "f2z84rw05gA",
    "title": "Team building Aeon Huế đợt 3 ( quẩy hết mình)",
    "channel": "Nguyên Huy Thân",
    "kind": "team_building"
   }
  ]
 },
 {
  "id": "danang",
  "name": "Đà Nẵng",
  "province": "Đà Nẵng",
  "region": "Trung",
  "desc": "biển, Bà Nà, nhiều resort và hội trường cho đoàn lớn",
  "season": "2–8",
  "scenery": [
   "bien",
   "thanh_pho",
   "nui"
  ],
  "fit": {
   "nghi_duong": 3,
   "gan_ket": 3
  },
  "island": false,
  "from": "Hà Nội",
  "travel": "máy bay HAN-DAD + xe 45 chỗ tại chỗ",
  "hours": 3.2,
  "price_from": 4956000,
  "price_mid": 6764000,
  "videos": [
   {
    "id": "PSqscwxujno",
    "title": "HƯỚNG DẪN DU LỊCH ĐÀ NẴNG TẤT TẦN TẬT . NAMAN RETREAT và MIKAZUKI . DA NANG VIET NAM TRAVEL GUIDE",
    "channel": "Toro Pan",
    "kind": "review"
   },
   {
    "id": "R0WpONfPQT8",
    "title": "KINH NGHIỆM DU LỊCH ĐÀ NẴNG TỰ TÚC GIÁ RẺ",
    "channel": "Xẻo Travel",
    "kind": "review"
   },
   {
    "id": "eM1lU_h1ZY4",
    "title": "HƯỚNG DẪN DU LỊCH ĐÀ NẴNG TỰ TÚC . KDL Núi Thần Tài, Vinpearl Nam Hội An , Quán ăn Ngon Đà Nẵng",
    "channel": "Toro Pan",
    "kind": "review"
   },
   {
    "id": "GXBivOpVHjU",
    "title": "IIG Teambuilding Đà Nẵng Kỷ Niệm 20 Năm",
    "channel": "Color Events Official",
    "kind": "team_building"
   },
   {
    "id": "0fAzSyyE50A",
    "title": "Trải nghiệm team building siêu hoạt náo tại biển Mỹ Khê Đà Nẵng 🥳🥳 #danang24 #dulich #travel",
    "channel": "Trùm Du Lịch",
    "kind": "team_building"
   }
  ]
 },
 {
  "id": "hoian",
  "name": "Hội An",
  "province": "Quảng Nam",
  "region": "Trung",
  "desc": "phố cổ, rừng dừa, Cù Lao Chàm, resort ven biển",
  "season": "2–8",
  "scenery": [
   "di_san",
   "bien"
  ],
  "fit": {
   "nghi_duong": 3,
   "gan_ket": 2
  },
  "island": false,
  "from": "Đà Nẵng",
  "travel": "xe 45 chỗ đường bộ 31 km",
  "hours": 0.6,
  "price_from": 2914000,
  "price_mid": 5365000,
  "videos": [
   {
    "id": "QCYJGIq2oaA",
    "title": "Du Lịch Hội An 2N1Đ Mới Nhất 2026 | Hướng Dẫn Trọn Vẹn Đi Đâu Ăn Gì Chơi Gì Chi Tiết Nhất",
    "channel": "Nhật Ký Du Lịch",
    "kind": "review"
   },
   {
    "id": "gfeh3Q26E68",
    "title": "Hội An 2026 Các Quán Ăn Bao Ngon, Các Điểm Chơi Cực Chất Bạn Nên Biết Khi Du Lịch Hội An",
    "channel": "Hải Du Lịch Bụi ",
    "kind": "review"
   },
   {
    "id": "x5Fa62DyL7Q",
    "title": "KINH NGHIỆM DU LỊCH HỘI AN TỰ TÚC CHI TIẾT NHẤT",
    "channel": "Xẻo Travel",
    "kind": "review"
   },
   {
    "id": "6995uyDqsag",
    "title": "AMAZING RACE HỘI AN - KAFI | VIETTEAM GROUP Tổ chức sự kiện - Team Building",
    "channel": "Vietteam Group - Event & Team Building",
    "kind": "team_building"
   },
   {
    "id": "OTOwgVOhNSk",
    "title": "F88 TỔ CHỨC TEAMBUILDING & GALA DINNER TẠI HỘI AN | 05-06/6/2026 - Đất Việt Tour",
    "channel": "Đất Việt Tour",
    "kind": "team_building"
   }
  ]
 },
 {
  "id": "quynhon",
  "name": "Quy Nhơn",
  "province": "Bình Định",
  "region": "Trung",
  "desc": "biển, Kỳ Co - Eo Gió, resort mới",
  "season": "3–9",
  "scenery": [
   "bien"
  ],
  "fit": {
   "nghi_duong": 3,
   "gan_ket": 3
  },
  "island": false,
  "from": "Đà Nẵng",
  "travel": "xe 45 chỗ đường bộ 359 km",
  "hours": 8.2,
  "price_from": 2303000,
  "price_mid": 5050000,
  "videos": [
   {
    "id": "2LY0wgSZAFc",
    "title": "Review Du lịch Quy Nhơn 5 ngày 4 đêm | Quy nhơn 2024",
    "channel": "Dark Prince Traveler",
    "kind": "review"
   },
   {
    "id": "g5DUPG3kELA",
    "title": "KINH NGHIỆM DU LỊCH QUY NHƠN TỰ TÚC CHI TIẾT MỚI NHẤT",
    "channel": "Xẻo Travel",
    "kind": "review"
   },
   {
    "id": "xRCfEbFb6t0",
    "title": "HƯỚNG DẪN DU LỊCH QUY NHƠN - BÌNH ĐỊNH. Quán ăn ngon tại Quy Nhơn . Ăn gì Chơi gì tại Quy Nhơn",
    "channel": "Toro Pan",
    "kind": "review"
   },
   {
    "id": "g-YPpIeY-YA",
    "title": "600 PAX SEPPLUS BÌNH ĐỊNH | TOUR TEAM BUILDING KỲ CO 1 NGÀY - QUY NHƠN TOURIST",
    "channel": "QUY NHƠN TOURIST",
    "kind": "team_building"
   },
   {
    "id": "Zhnl5xNDg8A",
    "title": "Teambuilding & Gala Dinner Maple Labs | Quy Nhơn 2025",
    "channel": "AKTeam Professional Teambuilding",
    "kind": "team_building"
   }
  ]
 },
 {
  "id": "phuyen",
  "name": "Phú Yên (Tuy Hoà)",
  "province": "Phú Yên",
  "region": "Trung",
  "desc": "biển hoang sơ, Gành Đá Đĩa, ít đông khách",
  "season": "3–8",
  "scenery": [
   "bien"
  ],
  "fit": {
   "nghi_duong": 2,
   "gan_ket": 2
  },
  "island": false,
  "from": "Đà Nẵng",
  "travel": "xe 45 chỗ đường bộ 456 km",
  "hours": 10.6,
  "price_from": 2526000,
  "price_mid": 5742000,
  "videos": [
   {
    "id": "mX6A63VG7YM",
    "title": "KINH NGHIỆM DU LỊCH PHÚ YÊN TỰ TÚC CHI TIẾT TỪ A - Z",
    "channel": "Xẻo Travel",
    "kind": "review"
   },
   {
    "id": "edaIamAJb6E",
    "title": "HƯỚNG DẪN DU LỊCH PHÚ YÊN , Ăn gì chơi gì tại PHÚ YÊN - QUY NHƠN",
    "channel": "Toro Pan",
    "kind": "review"
   },
   {
    "id": "yVixd42cOAk",
    "title": "Du lịch Phú Yên | Chợ hải sản sáng sớm và Món bánh xèo mực siêu rẻ ở Làng chài An Hải | #GauHamDi 47",
    "channel": "Gấu Ham Đi",
    "kind": "review"
   },
   {
    "id": "MiYHz08bTfc",
    "title": "RECAP TEAM BUILDING PHÚ YÊN 2026",
    "channel": "Win Win Official",
    "kind": "team_building"
   },
   {
    "id": "vvc8R_O2VaI",
    "title": "Chương trình Team Building Phú Yên 2026 - Quý công ty TEDI SOUTH - 100 khách",
    "channel": "Alpha Travels",
    "kind": "team_building"
   }
  ]
 },
 {
  "id": "nhatrang",
  "name": "Nha Trang",
  "province": "Khánh Hoà",
  "region": "Trung",
  "desc": "biển, tour đảo, khu vui chơi, nhiều resort lớn",
  "season": "1–8",
  "scenery": [
   "bien",
   "dao"
  ],
  "fit": {
   "nghi_duong": 3,
   "gan_ket": 3
  },
  "island": false,
  "from": "TP.HCM",
  "travel": "xe 45 chỗ đường bộ 412 km",
  "hours": 9.2,
  "price_from": 3589000,
  "price_mid": 7629000,
  "videos": [
   {
    "id": "Q7Mmb7xlYQA",
    "title": "HƯỚNG DẪN DU LỊCH NHA TRANG . Ăn gì chơi gì Tại Nha Trang. Review Đảo khỉ, resort đẹp Nha Trang",
    "channel": "Toro Pan",
    "kind": "review"
   },
   {
    "id": "SYW7DZUKzfM",
    "title": "solo trip đầu đời ở Nha Trang | ngan's diary 📓",
    "channel": "Con Ngan",
    "kind": "review"
   },
   {
    "id": "_CZyMkHXjKQ",
    "title": "TOP 10 ĐIỂM THAM QUAN NHA TRANG HOT NHẤT 2025 | REVIEW KINH NGHIỆM DU LỊCH NHA TRANG MỚI NHẤT",
    "channel": "NL Channel",
    "kind": "review"
   },
   {
    "id": "y447JkiEYiU",
    "title": "Team Building cùng IAN Solar ở Nha Trang p2 (23-24/11/2026)",
    "channel": "Tran Tinh",
    "kind": "team_building"
   },
   {
    "id": "dtEPsMIdfcw",
    "title": "Team Building cùng IAN Solar tại Nha Trang p1 (22/11/2026)",
    "channel": "Phi Tính Vlog",
    "kind": "team_building"
   }
  ]
 },
 {
  "id": "dalat",
  "name": "Đà Lạt",
  "province": "Lâm Đồng",
  "region": "Trung",
  "desc": "cao nguyên mát, đồi thông, không có biển; đường đèo",
  "season": "11–4",
  "scenery": [
   "nui",
   "thanh_pho"
  ],
  "fit": {
   "nghi_duong": 3,
   "gan_ket": 3
  },
  "island": false,
  "from": "TP.HCM",
  "travel": "xe 45 chỗ đường bộ 301 km",
  "hours": 7.0,
  "price_from": 2359000,
  "price_mid": 4169000,
  "videos": [
   {
    "id": "lNQwvC_P6-0",
    "title": "Du Lịch ĐÀ LẠT 2026. Lịch Trình 3 Ngày 2 Đêm Ăn Gì Chơi Gì Tại Đà Lạt. Làng Cù Lần, Lạc Hư Cổ Trấn..",
    "channel": "Toro Pan",
    "kind": "review"
   },
   {
    "id": "OV1urvr4jos",
    "title": "Đà Lạt lạnh teo, cải tạo hồ Xuân Hương, khai mạc Festival?",
    "channel": "ĐÀ LẠT STREET (NHÂN LA CÀ)",
    "kind": "review"
   },
   {
    "id": "ONNqtYuejvc",
    "title": "Du Lịch Đà Lạt 4N3Đ Mới Nhất 2026 | Trọn Vẹn Ăn Gì Chơi Gì Đi Đâu Ngắm Cảnh Đẹp Siêu Chi Tiết",
    "channel": "Nhật Ký Du Lịch",
    "kind": "review"
   },
   {
    "id": "BZGBf8WyGeg",
    "title": "Hành trình Team Building 2025 tại Đà Lạt cùng công ty MAC USA ONE tiêu chuẩn 5 sao| BI Travel",
    "channel": "BI Travel Official",
    "kind": "team_building"
   },
   {
    "id": "ey-pQ9MuJag",
    "title": "TEAM BUILDING TẠI ĐÀ LẠT | TRÒ CHƠI HẤP DẪN | QUÀ TẶNG GIÁ TRỊ LÊN ĐẾN HÀNG TRIỆU ĐỒNG",
    "channel": "Bazan Travel",
    "kind": "team_building"
   }
  ]
 },
 {
  "id": "muine",
  "name": "Phan Thiết - Mũi Né",
  "province": "Bình Thuận",
  "region": "Nam",
  "desc": "đồi cát, resort biển, cao tốc từ TP.HCM",
  "season": "11–4",
  "scenery": [
   "bien",
   "doi_cat"
  ],
  "fit": {
   "nghi_duong": 3,
   "gan_ket": 3
  },
  "island": false,
  "from": "TP.HCM",
  "travel": "xe 45 chỗ đường bộ 226 km",
  "hours": 5.0,
  "price_from": 2247000,
  "price_mid": 3858000,
  "videos": [
   {
    "id": "7vOeDlyrbug",
    "title": "YDL #297: Phan Thiết - Mũi Né cảnh đẹp, nhiều món ngon: lẩu thả, bánh căn, trứng mực | Yêu Máy Bay",
    "channel": "Yêu Máy Bay",
    "kind": "review"
   },
   {
    "id": "QcCXgh-OXqc",
    "title": "Đồ ăn Phan Thiết quá ngon! 2N1Đ khám phá Mũi Né, Bàu Trắng & food tour đặc sản 🇻🇳",
    "channel": "Leo Singto",
    "kind": "review"
   },
   {
    "id": "UPpky126WY4",
    "title": "Du Lịch Mũi Né - Phan Thiết 2026 | Đi Đâu Chơi Gì Ăn Gì Chi Tiết Và Mới Nhất",
    "channel": "Nhật Ký Du Lịch",
    "kind": "review"
   },
   {
    "id": "B_qGXKvW0L4",
    "title": "Hành trình du lịch Teambuilding 3 ngày tại Mũi Né - Phan Thiết | Chai lọ mỹ phẩm Salub Việt Nam",
    "channel": "Salub Viet Nam",
    "kind": "team_building"
   },
   {
    "id": "6HanYGH9cbk",
    "title": "TEAMBUILDING PHAN THIẾT - MŨI NÉ 2025",
    "channel": "VinaGreen Plus Official",
    "kind": "team_building"
   }
  ]
 },
 {
  "id": "vungtau",
  "name": "Vũng Tàu",
  "province": "Bà Rịa - Vũng Tàu",
  "region": "Nam",
  "desc": "biển gần TP.HCM, đi 2 ngày 1 đêm phổ biến",
  "season": "11–4",
  "scenery": [
   "bien",
   "thanh_pho"
  ],
  "fit": {
   "nghi_duong": 2,
   "gan_ket": 3
  },
  "island": false,
  "from": "TP.HCM",
  "travel": "xe 45 chỗ đường bộ 83 km",
  "hours": 1.7,
  "price_from": 2013000,
  "price_mid": 3606000,
  "videos": [
   {
    "id": "i-tjHeT79U8",
    "title": "Du Lịch Vũng Tàu Mới Nhất 2026 | Hướng Dẫn Tất Tần Tật Đi Đâu Ăn Gì Chơi Gì Chi Tiết Nhất",
    "channel": "Nhật Ký Du Lịch",
    "kind": "review"
   },
   {
    "id": "yXOjiRW3LwE",
    "title": "Hướng Dẫn Du Lịch Vũng Tàu 2025 | Ăn Gì Chơi Gì Tại Vũng Tàu Chi Tiết Và Mới Nhất",
    "channel": "Nhật Ký Du Lịch",
    "kind": "review"
   },
   {
    "id": "5qxx4UmrOnI",
    "title": "Top 20 địa điểm du lịch Vũng Tàu nên đi nhất trong 2022",
    "channel": "Blog Du Lịch",
    "kind": "review"
   },
   {
    "id": "YJo5kfhMW3g",
    "title": "TEAM BUILDING ALPLA VIỆT NAM | VŨNG TÀU 2026",
    "channel": "Du Lịch Ocean",
    "kind": "team_building"
   },
   {
    "id": "PfnaTRExs0A",
    "title": "Đi Team Building Có Gì Vui? Vũng Tàu 2 Ngày 1 Đêm",
    "channel": "Toàn Saigon",
    "kind": "team_building"
   }
  ]
 },
 {
  "id": "hotram",
  "name": "Hồ Tràm - Long Hải",
  "province": "Bà Rịa - Vũng Tàu",
  "region": "Nam",
  "desc": "resort biển cao cấp, sân team building trên cát",
  "season": "11–4",
  "scenery": [
   "bien",
   "rung"
  ],
  "fit": {
   "nghi_duong": 3,
   "gan_ket": 3
  },
  "island": false,
  "from": "TP.HCM",
  "travel": "xe 45 chỗ đường bộ 108 km",
  "hours": 2.2,
  "price_from": 2375000,
  "price_mid": 4964000,
  "videos": [
   {
    "id": "fYoPzHOhFvA",
    "title": "Top 5 Khách sạn Đẹp Nhất Hồ Tràm - Long Hải - Phước Hải",
    "channel": "Review Du Lịch Việt Nam",
    "kind": "review"
   },
   {
    "id": "xhaJHVWC-BQ",
    "title": "Khám Phá Hồ Tràm - Vũng Tàu 2025 | Hướng Dẫn Những Điểm Vui Chơi Tắm Biển Chi Tiết Và Mới Nhất",
    "channel": "Nhật Ký Du Lịch",
    "kind": "review"
   },
   {
    "id": "iK1kUH4hDw0",
    "title": "Tour Du lịch Long Hải Hồ Tràm 1 Hướng Dẫn Viên Chuyên Nghiệp",
    "channel": "NẮNG MỚI ",
    "kind": "review"
   },
   {
    "id": "ERHJ_lrqM-8",
    "title": "[Official Recap] Team Building Hồ Tràm 2026 | Mừng HQG 16 Năm Thành Lập",
    "channel": "Công Nghệ HQG",
    "kind": "team_building"
   },
   {
    "id": "k7AidVaaT5Y",
    "title": "Mắt Kính TUYẾT HÀ Du Lịch Hồ Tràm Kết Hợp TEAMBUILDING SUMMER VACATION",
    "channel": "Công Ty TNHH Du Lịch INTOUR",
    "kind": "team_building"
   }
  ]
 },
 {
  "id": "phuquoc",
  "name": "Phú Quốc",
  "province": "Kiên Giang",
  "region": "Nam",
  "desc": "đảo; chỉ tính đường bay cho đoàn",
  "season": "11–4",
  "scenery": [
   "bien",
   "dao"
  ],
  "fit": {
   "nghi_duong": 3,
   "gan_ket": 3
  },
  "island": true,
  "from": "Cần Thơ",
  "travel": "máy bay VCA-PQC + xe 45 chỗ tại chỗ",
  "hours": 2.8,
  "price_from": 4681000,
  "price_mid": 7398000,
  "videos": [
   {
    "id": "SUFK6URuMmc",
    "title": "REVIEW TOP NHỮNG ĐIỂM THAM QUAN DU LỊCH ĐẢO NGỌC - PHÚ QUỐC",
    "channel": "Bước Lang Thang Vlogs",
    "kind": "review"
   },
   {
    "id": "RfbQ4PHS5cQ",
    "title": "Kinh nghiệm Du lịch Phú Quốc Mới nhất Chi tiết nhất từ A - Z | Tico Travel",
    "channel": "Lalago",
    "kind": "review"
   },
   {
    "id": "LjnaZdZAmKw",
    "title": "Top 6 địa điểm du lịch Phú Quốc Đẹp Nhất | Đi rồi mới thấy xứng đáng!",
    "channel": "Xẻo Travel",
    "kind": "review"
   },
   {
    "id": "oUTav08ZoUk",
    "title": "Team Building và Gala Dinner Phú Quốc 3N2Đ | Vietnam Booking",
    "channel": "Vietnam Booking",
    "kind": "team_building"
   }
  ]
 },
 {
  "id": "condao",
  "name": "Côn Đảo",
  "province": "Bà Rịa - Vũng Tàu",
  "region": "Nam",
  "desc": "đảo, di tích nhà tù, lặn biển; chuyến bay ít ghế, khó cho đoàn lớn",
  "season": "3–9",
  "scenery": [
   "bien",
   "dao",
   "di_tich"
  ],
  "fit": {
   "nghi_duong": 3,
   "gan_ket": 1
  },
  "island": true,
  "from": "TP.HCM",
  "travel": "máy bay SGN-VCS + xe 45 chỗ tại chỗ",
  "hours": 2.8,
  "price_from": 4268000,
  "price_mid": 6840000,
  "videos": [
   {
    "id": "GkuAXFcBWhM",
    "title": "Du Lịch Côn Đảo Mùa Đẹp Nhất 2026 | Hướng Dẫn Chi Tiết Và Mới Nhất",
    "channel": "Nhật Ký Du Lịch",
    "kind": "review"
   },
   {
    "id": "60nVkAILOTU",
    "title": "48 Giờ Khám Phá Côn Đảo: Ăn Gì - Chơi Gì? | Quan không gờ",
    "channel": "Quan không gờ",
    "kind": "review"
   },
   {
    "id": "4OcDK5wkB9U",
    "title": "Côn Đảo - Ký Sự 2 Ngày Đêm Reivew Du Lịch Và Khám Phá Vẽ Đẹp Tư Nhiên, Hùng Vỹ Đầy Linh Thiêng",
    "channel": "Phan Thành Luân BĐS ",
    "kind": "review"
   },
   {
    "id": "XCNgvcqPhw4",
    "title": "TEAM BUILDING CÔN ĐẢO 2026 | TIẾN PHÁT GROUP",
    "channel": "Tiến Phát Group",
    "kind": "team_building"
   },
   {
    "id": "hK6F1QT_7NE",
    "title": "SGU Team building - vận động biển tại Côn Đảo Resort 2019",
    "channel": "Nguyễn Hoàng Tuấn",
    "kind": "team_building"
   }
  ]
 },
 {
  "id": "cantho",
  "name": "Cần Thơ",
  "province": "Cần Thơ",
  "region": "Nam",
  "desc": "chợ nổi, vườn trái cây, sông nước miền Tây",
  "season": "quanh năm",
  "scenery": [
   "song_nuoc",
   "thanh_pho"
  ],
  "fit": {
   "nghi_duong": 1,
   "gan_ket": 2
  },
  "island": false,
  "from": "TP.HCM",
  "travel": "xe 45 chỗ đường bộ 172 km",
  "hours": 3.9,
  "price_from": 1905000,
  "price_mid": 3877000,
  "videos": [
   {
    "id": "1FNAr3OLyPM",
    "title": "Kinh Nghiệm Du Lịch Cần Thơ Tự Túc Chi Tiết Từ A - Z",
    "channel": "Xẻo Travel",
    "kind": "review"
   },
   {
    "id": "u-CvjUwEaJ8",
    "title": "758. Du lịch Cần Thơ - Những điểm tham quan không thể bỏ qua khi về vùng Tây Đô gạo trắng nước trong",
    "channel": "CuongCanCook Official",
    "kind": "review"
   },
   {
    "id": "HJ7imaVKu9Q",
    "title": "Du lịch cần thơ trải nghiệm các trò chơi nước khu du lịch ông đề",
    "channel": "Cuộc Sống Vlog59",
    "kind": "review"
   },
   {
    "id": "VAu6gRa1ZVY",
    "title": "Team Building - Zingplay 2025 | Cần Thơ",
    "channel": "DeltaflyMedia",
    "kind": "team_building"
   },
   {
    "id": "wjoL-NUdReU",
    "title": "Team Building Vietbank KV 6 \"Vươn tầm khát vọng\" tại Cần Thơ ngày 25–26/7/2026",
    "channel": "Vietbank Ngân hàng TMCP Việt Nam Thương Tín",
    "kind": "team_building"
   }
  ]
 },
 {
  "id": "tayninh",
  "name": "Tây Ninh (Núi Bà Đen)",
  "province": "Tây Ninh",
  "region": "Nam",
  "desc": "núi Bà Đen cáp treo, tâm linh; đi về trong ngày từ TP.HCM",
  "season": "quanh năm",
  "scenery": [
   "nui",
   "tam_linh"
  ],
  "fit": {
   "nghi_duong": 1,
   "gan_ket": 2
  },
  "island": false,
  "from": "TP.HCM",
  "travel": "xe 45 chỗ đường bộ 115 km",
  "hours": 2.3,
  "price_from": 2621000,
  "price_mid": 4097000,
  "videos": [
   {
    "id": "tuWGDE5GfsA",
    "title": "Kinh Nghiệm Du Lịch TÂY NINH TỰ TÚC 2N1Đ | PHẦN 1 Khám Phá SunWorld NÚI BÀ & Đặc Sản GÀ RẪY TÂY NINH",
    "channel": "Say Cooking & Sharing",
    "kind": "review"
   },
   {
    "id": "ITDw2ih48Dg",
    "title": "HƯỚNG DẪN DU LỊCH NÚI BÀ ĐEN - TÂY NINH. Ăn gì chơi gì ở TÂY NINH . Tay Ninh Ba Den mountain tourism",
    "channel": "Toro Pan",
    "kind": "review"
   },
   {
    "id": "RjfjY719DSY",
    "title": "NÚI BÀ ĐEN LÀ ĐIỂM DU LỊCH TÂM LINH NỔI TIẾNG",
    "channel": "Phạm Ký Nhất ",
    "kind": "review"
   }
  ]
 }
];
