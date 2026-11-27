"""Xuất data/*.json ra dạng bảng để XEM bằng mắt: data/xem/*.csv (+ bo_du_lieu.xlsx nếu có openpyxl).

    python data/xuat_bang.py

Nguồn sự thật vẫn là data/*.json (agent và bộ tính đọc JSON). Thư mục xem/ chỉ là bản trình bày,
sinh lại được bất cứ lúc nào. CSV ghi UTF-8 có BOM để Excel mở đúng tiếng Việt.
"""
import csv
import json
import subprocess
import sys
from pathlib import Path

THU_MUC = Path(__file__).resolve().parent
RA = THU_MUC / "xem"


def doc(ten):
    return json.loads((THU_MUC / ten).read_text(encoding="utf-8"))


def bang():
    dd = doc("diem_den.json")
    ten_den = {d["id"]: d["ten"] for d in dd["diem_den"]}
    ten_di = {d["id"]: d["ten"] for d in dd["diem_di"]}
    dc, ks, nh, hd, vd, gc = doc("di_chuyen.json"), doc("khach_san.json"), doc("nha_hang.json"), doc("hoat_dong.json"), doc("video_review.json"), doc("gia_chuan.json")
    so_video = {k: len(v) for k, v in vd["video"].items()}
    out = {}
    out["1_diem_den"] = [{"Mã": d["id"], "Điểm đến": d["ten"], "Tỉnh": d["tinh"], "Miền": d["mien"], "Loại cảnh": ", ".join(d["loai_canh"]),
                          "Sân bay gần": d["san_bay"] or "", "Đảo (chỉ bay)": "có" if d["dao_chi_duong_bay"] else "",
                          "Có phà": "có" if d["co_pha"] else "", "Nhóm giá": d["nhom_gia"], "Có KS 5 sao": "có" if d["co_khach_san_5_sao"] else "không",
                          "Hợp nghỉ dưỡng (0-3)": d["phu_hop"]["nghi_duong"], "Hợp gắn kết (0-3)": d["phu_hop"]["gan_ket"],
                          "Mùa đẹp (tháng)": d["mua_dep_thang"], "Mô tả": d["mo_ta"], "Số video": so_video.get(d["id"], 0)} for d in dd["diem_den"]]
    out["2_diem_di"] = [{"Mã": d["id"], "Điểm đi": d["ten"], "Sân bay": d["san_bay"], "Vĩ độ": d["lat"], "Kinh độ": d["lon"]} for d in dd["diem_di"]]
    out["3_tuyen_di_chuyen"] = [{"Từ": ten_di[t["tu"]], "Đến": ten_den[t["den"]],
                                 "Đường bộ (km)": "" if t["duong_bo_km"] is None else t["duong_bo_km"],
                                 "Đường bộ (giờ)": "" if t["duong_bo_gio"] is None else t["duong_bo_gio"],
                                 "Chặng bay": (t["duong_bay"] or {}).get("chang", ""),
                                 "Giờ bay": (t["duong_bay"] or {}).get("gio_bay", ""),
                                 "Vé 1 chiều/người (đ)": (t["duong_bay"] or {}).get("gia_ve_mot_chieu", ""),
                                 "Vé ước tính": ("có" if (t["duong_bay"] or {}).get("uoc_tinh") else "không") if t["duong_bay"] else "",
                                 "Km sân bay → nơi đến": (t["duong_bay"] or {}).get("km_san_bay_toi_diem_den", ""),
                                 "Ghi chú": t["ghi_chu"]} for t in dc["tuyen"]]
    out["4_loai_xe"] = [{"Loại xe": x["loai"], "Số chỗ (khách)": x["so_cho"], "Đơn giá (đ/km)": x["don_gia_km"], "Ước tính": "có"} for x in dc["xe"]]
    out["5_khach_san"] = []
    for k in ks:
        p = {x["suc_chua"]: x for x in k["loai_phong"]}
        ti = k["tien_ich"]
        out["5_khach_san"].append({"Mã": k["id"], "Tên (tên dựng)": k["ten"], "Điểm đến": ten_den[k["diem_den"]], "Mức gói": k["muc"],
                                    "Hạng sao": k["hang_sao"], "Loại": k["loai"],
                                    **{f"Phòng {s} người: giá/đêm": p[s]["gia_dem"] if s in p else "" for s in (2, 3, 4)},
                                    **{f"Phòng {s} người: số phòng": p[s]["so_luong"] if s in p else "" for s in (2, 3, 4)},
                                    "Tổng phòng": k["tong_phong"], "Sức chứa tối đa (người)": k["suc_chua_toi_da"],
                                    "Hồ bơi": "có" if ti["ho_boi"] else "", "Bãi biển riêng": "có" if ti["bai_bien_rieng"] else "",
                                    "Spa": "có" if ti["spa"] else "", "Khuôn viên team building (người)": ti["khuon_vien_team_building_nguoi"] or "",
                                    "Hội trường (chỗ)": ti["hoi_truong_cho"] or "",
                                    "Điểm hợp nghỉ dưỡng": k["phu_hop"]["nghi_duong"], "Điểm hợp gắn kết": k["phu_hop"]["gan_ket"]})
    out["6_nha_hang"] = [{"Mã": x["id"], "Tên (tên dựng)": x["ten"], "Điểm đến": ten_den[x["diem_den"]], "Mức gói": x["muc"],
                          "Sức chứa (người)": x["suc_chua"], "Giá/người/bữa (đ)": x["gia_nguoi_bua"], "Mở": x["gio_mo"], "Đóng": x["gio_dong"],
                          "Nhận đoàn": "có" if x["nhan_doan"] else "không"} for x in nh]
    tm = {"nghi_duong": "nghỉ dưỡng", "gan_ket": "gắn kết"}
    out["7_hoat_dong"] = [{"Mã": x["id"], "Tên": x["ten"], "Điểm đến": ten_den[x["diem_den"]], "Loại": x["loai"],
                           "Mục đích": ", ".join(tm[m] for m in x["muc_dich"]), "Dùng cho gói": ", ".join(x["muc"]),
                           "Giá/người (đ)": x["gia_nguoi"], "Thời lượng (phút)": x["thoi_luong_phut"], "Mở": x["gio_mo"], "Đóng": x["gio_dong"],
                           "Đóng cửa thứ": ", ".join({0: "Hai"}.get(i, str(i)) for i in x["ngay_dong_cua"]),
                           "Sức chứa/lượt": x["suc_chua"] or "", "Tên dựng": "có" if x["ten_dung"] else "tên thật",
                           "Giá ước tính": "có" if x["uoc_tinh"] else ""} for x in hd]
    out["8_video_review"] = [{"Điểm đến": ten_den[k], "Loại": v["loai"], "Tiêu đề": v["tieu_de"], "Kênh": v["kenh"], "Link": v["url"]}
                             for k, ds in vd["video"].items() for v in ds]
    out["9_gia_chuan_nguon"] = []
    for nhom, gt in gc.items():
        if isinstance(gt, dict) and "moc" in gt:
            for m in gt["moc"]:
                out["9_gia_chuan_nguon"].append({"Nhóm giá": nhom, "Mốc": m.get("mo_ta") or m.get("chang") or m.get("tuyen") or m.get("noi", ""),
                                                 "Giá / khoảng": str(m.get("khoang") or m.get("tu") or m.get("gia_nguoi") or ""),
                                                 "Độ tin cậy": m.get("do_tin_cay", ""), "Nguồn": m.get("nguon", ""), "Ghi chú": m.get("ghi_chu", "")})
    return out


def vi_du():
    """Chạy bộ tính tham chiếu trên vài đầu vào để thấy data dùng thế nào."""
    lenh = [["--tu", "Hà Nội", "--den", "Hạ Long", "--nguoi", "40", "--ngay", "3", "--muc-dich", "gan_ket", "--ngan-sach", "150tr"],
            ["--tu", "TP.HCM", "--den", "Vũng Tàu", "--nguoi", "30", "--ngay", "2", "--muc-dich", "nghi_duong"],
            ["--tu", "TP.HCM", "--ngan-sach", "3tr", "--moi-nguoi", "--nguoi", "60", "--ngay", "3", "--muc-dich", "nghi_duong"],
            ["--tu", "Hà Nội", "--ngan-sach", "20tr", "--nguoi", "50", "--ngay", "3", "--muc-dich", "gan_ket"]]
    md = ["# Ví dụ kết quả chạy trên bộ dữ liệu\n", "Sinh bằng `python data/xuat_bang.py` (chạy `data/tinh_thu.py`). Mọi số do code tính trên `data/*.json`; giá là tham khảo / ước tính, khách sạn và nhà hàng là tên dựng.\n"]
    for l in lenh:
        kq = subprocess.run([sys.executable, str(THU_MUC / "tinh_thu.py"), *l], capture_output=True, text=True, encoding="utf-8")
        md += [f"\n## `python data/tinh_thu.py {' '.join(repr(x) if ' ' in x else x for x in l)}`\n", "```text", (kq.stdout or kq.stderr).rstrip(), "```\n"]
    return "\n".join(md)


def main():
    RA.mkdir(exist_ok=True)
    out = bang()
    for ten, dong in out.items():
        with open(RA / f"{ten}.csv", "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=list(dong[0].keys()))
            w.writeheader()
            w.writerows(dong)
    (RA / "vi_du_ket_qua.md").write_text(vi_du(), encoding="utf-8")
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill
        from openpyxl.utils import get_column_letter
        wb = Workbook()
        wb.remove(wb.active)
        for ten, dong in out.items():
            ws = wb.create_sheet(ten[:31])
            cot = list(dong[0].keys())
            ws.append(cot)
            for r in dong:
                ws.append([r[c] for c in cot])
            for c in ws[1]:
                c.font = Font(bold=True, color="FFFFFF")
                c.fill = PatternFill("solid", fgColor="1F6FEB")
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions
            for i, c in enumerate(cot, 1):
                dai = max(len(str(c)), *(len(str(r[c])) for r in dong[:200]))
                ws.column_dimensions[get_column_letter(i)].width = min(60, max(10, dai + 2))
        wb.save(RA / "bo_du_lieu.xlsx")
        print("đã ghi bo_du_lieu.xlsx")
    except ImportError:
        print("(không có openpyxl: chỉ xuất CSV)")
    for ten, dong in out.items():
        print(f"  {ten}.csv: {len(dong)} dòng")
    print("  vi_du_ket_qua.md")


if __name__ == "__main__":
    main()
