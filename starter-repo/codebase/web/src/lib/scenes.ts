// Ảnh phong cảnh Việt Nam từ Wikimedia Commons (giấy phép CC BY / CC BY-SA / CC0 — ghi công ở chân trang).
// src: bản 1920px · src4k: bản 3840px (4K). Lấy & kiểm link 28/11/2026 qua Commons API; ảnh gốc ≥ 5000px.
export interface Scene { id: string; name: string; province: string; w: number; h: number; src: string; src4k: string; page: string; license: string; artist: string }
export const SCENES: Scene[] = [
 {
  "id": "goldenbridge",
  "name": "Cầu Vàng · Bà Nà",
  "province": "Đà Nẵng",
  "w": 5710,
  "h": 3896,
  "src": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/98/Aerial_view_of_the_Golden_Bridge%2C_Ba_Na_Hills%2C_Da_Nang%2C_Vietnam.jpg/1920px-Aerial_view_of_the_Golden_Bridge%2C_Ba_Na_Hills%2C_Da_Nang%2C_Vietnam.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
  "src4k": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/98/Aerial_view_of_the_Golden_Bridge%2C_Ba_Na_Hills%2C_Da_Nang%2C_Vietnam.jpg/3840px-Aerial_view_of_the_Golden_Bridge%2C_Ba_Na_Hills%2C_Da_Nang%2C_Vietnam.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
  "page": "https://commons.wikimedia.org/wiki/File:Aerial_view_of_the_Golden_Bridge,_Ba_Na_Hills,_Da_Nang,_Vietnam.jpg",
  "license": "CC BY-SA 4.0",
  "artist": "Vivu Vietnam"
 },
 {
  "id": "halong",
  "name": "Hạ Long",
  "province": "Quảng Ninh",
  "w": 13612,
  "h": 4534,
  "src": "https://thumb.wikimedia.org/wikipedia/commons/thumb/d/d5/H%E1%BA%A1_Long_Bay%2C_Ti_T%E1%BB%91p_Island%2C_2020-01_CN-01.jpg/1920px-H%E1%BA%A1_Long_Bay%2C_Ti_T%E1%BB%91p_Island%2C_2020-01_CN-01.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
  "src4k": "https://thumb.wikimedia.org/wikipedia/commons/thumb/d/d5/H%E1%BA%A1_Long_Bay%2C_Ti_T%E1%BB%91p_Island%2C_2020-01_CN-01.jpg/3840px-H%E1%BA%A1_Long_Bay%2C_Ti_T%E1%BB%91p_Island%2C_2020-01_CN-01.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
  "page": "https://commons.wikimedia.org/wiki/File:H%E1%BA%A1_Long_Bay,_Ti_T%E1%BB%91p_Island,_2020-01_CN-01.jpg",
  "license": "CC BY-SA 4.0",
  "artist": "Steffen Schmitz"
 },
 {
  "id": "khaupha",
  "name": "Đèo Khau Phạ · Mù Cang Chải",
  "province": "Yên Bái",
  "w": 5897,
  "h": 3937,
  "src": "https://thumb.wikimedia.org/wikipedia/commons/thumb/e/e8/Khau_Ph%E1%BA%A1_Pass%2C_Vietnam_%28Unsplash%29.jpg/1920px-Khau_Ph%E1%BA%A1_Pass%2C_Vietnam_%28Unsplash%29.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
  "src4k": "https://thumb.wikimedia.org/wikipedia/commons/thumb/e/e8/Khau_Ph%E1%BA%A1_Pass%2C_Vietnam_%28Unsplash%29.jpg/3840px-Khau_Ph%E1%BA%A1_Pass%2C_Vietnam_%28Unsplash%29.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
  "page": "https://commons.wikimedia.org/wiki/File:Khau_Ph%E1%BA%A1_Pass,_Vietnam_(Unsplash).jpg",
  "license": "CC0",
  "artist": "Doan Tuan danny_pham93"
 },
 {
  "id": "trangan",
  "name": "Tràng An",
  "province": "Ninh Bình",
  "w": 5845,
  "h": 3902,
  "src": "https://thumb.wikimedia.org/wikipedia/commons/thumb/b/b3/Trang_An_Landscape_Complex%2C_Ninh_Binh_Province%2C_Vietnam%2C_20240202_1404_5216.jpg/1920px-Trang_An_Landscape_Complex%2C_Ninh_Binh_Province%2C_Vietnam%2C_20240202_1404_5216.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
  "src4k": "https://thumb.wikimedia.org/wikipedia/commons/thumb/b/b3/Trang_An_Landscape_Complex%2C_Ninh_Binh_Province%2C_Vietnam%2C_20240202_1404_5216.jpg/3840px-Trang_An_Landscape_Complex%2C_Ninh_Binh_Province%2C_Vietnam%2C_20240202_1404_5216.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
  "page": "https://commons.wikimedia.org/wiki/File:Trang_An_Landscape_Complex,_Ninh_Binh_Province,_Vietnam,_20240202_1404_5216.jpg",
  "license": "CC BY 4.0",
  "artist": "Jakub Hałun"
 },
 {
  "id": "hoian",
  "name": "Phố cổ Hội An",
  "province": "Quảng Nam",
  "w": 5433,
  "h": 3622,
  "src": "https://thumb.wikimedia.org/wikipedia/commons/thumb/0/01/Hoi_An_%28I%29.jpg/1920px-Hoi_An_%28I%29.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
  "src4k": "https://thumb.wikimedia.org/wikipedia/commons/thumb/0/01/Hoi_An_%28I%29.jpg/3840px-Hoi_An_%28I%29.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
  "page": "https://commons.wikimedia.org/wiki/File:Hoi_An_(I).jpg",
  "license": "CC BY 4.0",
  "artist": "Supanut Arunoprayote"
 },
 {
  "id": "danang",
  "name": "Sông Cu Đê · Đà Nẵng",
  "province": "Đà Nẵng",
  "w": 12152,
  "h": 4487,
  "src": "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/5b/Cu_%C4%90%C3%AA_River%2C_Da_Nang.jpg/1920px-Cu_%C4%90%C3%AA_River%2C_Da_Nang.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
  "src4k": "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/5b/Cu_%C4%90%C3%AA_River%2C_Da_Nang.jpg/3840px-Cu_%C4%90%C3%AA_River%2C_Da_Nang.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
  "page": "https://commons.wikimedia.org/wiki/File:Cu_%C4%90%C3%AA_River,_Da_Nang.jpg",
  "license": "CC BY-SA 4.0",
  "artist": "Christopher Crouzet"
 },
 {
  "id": "hanoi",
  "name": "Hà Nội sau mưa",
  "province": "Hà Nội",
  "w": 13087,
  "h": 4455,
  "src": "https://thumb.wikimedia.org/wikipedia/commons/thumb/2/20/Sunset_over_Hanoi_After_the_Rain.jpg/1920px-Sunset_over_Hanoi_After_the_Rain.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
  "src4k": "https://thumb.wikimedia.org/wikipedia/commons/thumb/2/20/Sunset_over_Hanoi_After_the_Rain.jpg/3840px-Sunset_over_Hanoi_After_the_Rain.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
  "page": "https://commons.wikimedia.org/wiki/File:Sunset_over_Hanoi_After_the_Rain.jpg",
  "license": "CC BY-SA 4.0",
  "artist": "Christopher Crouzet"
 },
 {
  "id": "hue",
  "name": "Đại Nội Huế",
  "province": "Thừa Thiên Huế",
  "w": 5458,
  "h": 3639,
  "src": "https://thumb.wikimedia.org/wikipedia/commons/thumb/8/86/Imperial_City_on_an_atmospheric_day.jpg/1920px-Imperial_City_on_an_atmospheric_day.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
  "src4k": "https://thumb.wikimedia.org/wikipedia/commons/thumb/8/86/Imperial_City_on_an_atmospheric_day.jpg/3840px-Imperial_City_on_an_atmospheric_day.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
  "page": "https://commons.wikimedia.org/wiki/File:Imperial_City_on_an_atmospheric_day.jpg",
  "license": "CC BY 2.0",
  "artist": "Kandukuru Nagarjun"
 },
 {
  "id": "phongnha",
  "name": "Phong Nha – Kẻ Bàng",
  "province": "Quảng Bình",
  "w": 5552,
  "h": 3309,
  "src": "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/72/Cueva_Para%C3%ADso%2C_Parque_Nacional_Phong_Nha_-_Ke_Bang%2C_Vietnam_%2841309962172%29.jpg/1920px-Cueva_Para%C3%ADso%2C_Parque_Nacional_Phong_Nha_-_Ke_Bang%2C_Vietnam_%2841309962172%29.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
  "src4k": "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/72/Cueva_Para%C3%ADso%2C_Parque_Nacional_Phong_Nha_-_Ke_Bang%2C_Vietnam_%2841309962172%29.jpg/3840px-Cueva_Para%C3%ADso%2C_Parque_Nacional_Phong_Nha_-_Ke_Bang%2C_Vietnam_%2841309962172%29.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
  "page": "https://commons.wikimedia.org/wiki/File:Cueva_Para%C3%ADso,_Parque_Nacional_Phong_Nha_-_Ke_Bang,_Vietnam_(41309962172).jpg",
  "license": "CC BY 2.0",
  "artist": "Edgardo W. Olivera"
 },
 {
  "id": "sapa",
  "name": "Ruộng bậc thang Sa Pa",
  "province": "Lào Cai",
  "w": 5776,
  "h": 3856,
  "src": "https://thumb.wikimedia.org/wikipedia/commons/thumb/2/2c/Road_and_paddy_fields_in_Sa_Pa%2C_Vietnam%2C_20240126_1203_3590.jpg/1920px-Road_and_paddy_fields_in_Sa_Pa%2C_Vietnam%2C_20240126_1203_3590.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
  "src4k": "https://thumb.wikimedia.org/wikipedia/commons/thumb/2/2c/Road_and_paddy_fields_in_Sa_Pa%2C_Vietnam%2C_20240126_1203_3590.jpg/3840px-Road_and_paddy_fields_in_Sa_Pa%2C_Vietnam%2C_20240126_1203_3590.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
  "page": "https://commons.wikimedia.org/wiki/File:Road_and_paddy_fields_in_Sa_Pa,_Vietnam,_20240126_1203_3590.jpg",
  "license": "CC BY 4.0",
  "artist": "Jakub Hałun"
 },
 {
  "id": "phuquoc",
  "name": "Phú Quốc",
  "province": "Kiên Giang",
  "w": 6000,
  "h": 4000,
  "src": "https://thumb.wikimedia.org/wikipedia/commons/thumb/8/85/Amazing_beach_on_Phu_Quoc_island_Vietnam_%2838647607275%29.jpg/1920px-Amazing_beach_on_Phu_Quoc_island_Vietnam_%2838647607275%29.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
  "src4k": "https://thumb.wikimedia.org/wikipedia/commons/thumb/8/85/Amazing_beach_on_Phu_Quoc_island_Vietnam_%2838647607275%29.jpg/3840px-Amazing_beach_on_Phu_Quoc_island_Vietnam_%2838647607275%29.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
  "page": "https://commons.wikimedia.org/wiki/File:Amazing_beach_on_Phu_Quoc_island_Vietnam_(38647607275).jpg",
  "license": "CC BY 2.0",
  "artist": "dronepicr"
 }
];
export const scene = (id: string) => SCENES.find(s => s.id === id)!;
