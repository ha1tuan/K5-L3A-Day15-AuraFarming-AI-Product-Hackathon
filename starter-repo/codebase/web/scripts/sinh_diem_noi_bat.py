"""Sinh codebase/web/src/lib/featured.ts cho trang giới thiệu: 24 điểm đến + video review đã kiểm link + giá tham khảo
(gói Tiết kiệm, 30 người, 3 ngày 2 đêm, từ điểm đi gần nhất — tính bằng codebase/du_lieu.py, không nhập tay).

    .venv/bin/python codebase/web/scripts/sinh_diem_noi_bat.py
"""
import json
import os
import re
import sys

GOC = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, GOC)
import du_lieu  # noqa: E402

out = []
for den in du_lieu.D("diem_den")["diem_den"]:
    best = None
    for tu in du_lieu.D("diem_den")["diem_di"]:
        t = du_lieu.tuyen(tu, den)
        if t["duong_bo_km"] == 0:
            continue
        km = t["duong_bo_km"] if t["duong_bo_km"] is not None else (t["duong_bay"] or {}).get("km", 9999) * 1.5
        km *= 1.0 if tu["id"] in ("HAN", "SGN", "DAD") else 1.3        # ưu tiên 3 thành phố lớn khi gần ngang nhau
        if best is None or km < best[0]:
            best = (km, tu)
    tu = best[1]
    req = {"so_nguoi": 30, "so_ngay": 3, "so_dem": 2, "muc_dich": "ca_hai", "ngan_sach": None, "khong_muon": []}
    d = du_lieu.dung_diem_den(req, tu, den)
    vids = []
    for v in du_lieu.D("video_review")["video"].get(den["id"], []):
        m = re.search(r"v=([\w-]{11})", v["url"])
        if m:
            vids.append({"id": m.group(1), "title": v["tieu_de"], "channel": v["kenh"], "kind": v["loai"]})
    out.append({"id": den["id"], "name": den["ten"], "province": den["tinh"], "region": den["mien"], "desc": den["mo_ta"],
                "season": den["mua_dep_thang"], "scenery": den["loai_canh"], "fit": den["phu_hop"],
                "island": den["dao_chi_duong_bay"], "from": tu["ten"],
                "travel": d["raw"]["tiet_kiem"]["_chang"]["mo_ta"], "hours": d["raw"]["tiet_kiem"]["_chang"]["gio"],
                "price_from": d["calc"]["tiet_kiem"]["moi_nguoi"], "price_mid": d["calc"]["can_bang"]["moi_nguoi"],
                "videos": vids})
p = os.path.join(GOC, "web", "src", "lib", "featured.ts")
with open(p, "w", encoding="utf-8") as f:
    f.write("// SINH TỰ ĐỘNG bởi scripts/sinh_diem_noi_bat.py từ data/*.json — không sửa tay.\n"
            "// price_from / price_mid: gói Tiết kiệm / Cân bằng mỗi người, 30 người, 3N2Đ, từ điểm đi gần nhất (tham khảo).\n")
    f.write("export interface FeaturedVideo { id: string; title: string; channel: string; kind: string }\n")
    f.write("export interface Featured { id: string; name: string; province: string; region: 'Bắc' | 'Trung' | 'Nam'; desc: string; "
            "season: string; scenery: string[]; fit: { nghi_duong: number; gan_ket: number }; island: boolean; from: string; "
            "travel: string; hours: number; price_from: number; price_mid: number; videos: FeaturedVideo[] }\n")
    f.write("export const FEATURED: Featured[] = " + json.dumps(out, ensure_ascii=False, indent=1) + ";\n")
print(len(out), "điểm đến,", sum(len(x["videos"]) for x in out), "video →", p)
