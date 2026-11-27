"""THÊM (không sửa câu cũ) 12 câu thử soát báo giá vào eval/benchmark.csv, input dựng từ báo giá tour đoàn công khai thật
(data/bao_gia_mau.json, nguồn ghi ở cột source → data_that). Chạy một lần; chạy lại không thêm trùng.

    python eval/them_cau_bao_gia.py
"""
import csv
import json
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]
MAU = {x["url"].rsplit("/", 1)[1]: x for x in json.loads((GOC / "data/bao_gia_mau.json").read_text(encoding="utf-8"))["bao_gia"]}
# (id, slug, số người, ngân sách triệu, thêm vào câu, type, ý riêng của pass_criterion)
CAU = [
    ("Q01", "tour-team-building-choi-het-minh-o-khu-du-lich-bcr.html", 45, 45, "", "thuong", "dòng VAT 10% của 42.750.000đ; nói rõ giá báo trong ngân sách nhưng tổng chi thật vượt"),
    ("Q02", "tour-da-lat-cam-trai-3-ngay-2-dem-co-luu-tru-cho-khach-doan.html", 40, 120, "", "thuong", "dòng VAT 8%; cộng vé cáp treo đồi Robin 80.000đ × 40"),
    ("Q03", "tour-khach-doan-nha-trang-da-lat-4-ngay-3-dem.html", 40, 150, " từ Hà Nội", "kho", "cộng vé máy bay khứ hồi cho 40 người vì báo giá ghi 'không bao gồm vé máy bay' (số ghi nhãn ước tính); hỏi lại giá các vé chưa ghi số"),
    ("Q04", "tour-long-hai-teambuilding-gala-dinner-2-ngay-1-dem.html", 60, 100, "", "thuong", "dòng VAT 8%; tip ghi nhãn ước tính"),
    ("Q05", "tour-team-building-mui-ne-phan-thiet-2n1d.html", 30, 45, "", "kho", "báo giá không nói VAT → có câu hỏi lại về VAT / hoá đơn và dòng VAT tạm tính ghi rõ 'tạm tính'"),
    ("Q06", "tour-team-building-nha-trang-4n3d.html", 40, 400, " Lương bình quân 8 triệu/tháng.", "kho", "dòng VAT 10%; so chi phí / người với 1 tháng lương 8.000.000đ và báo vượt trần phúc lợi, ghi cần đối chiếu luật mới"),
    ("Q07", "tour-team-building-kham-pha-buu-long-1n.html", 80, 60, "", "thuong", "dòng VAT 10%; có câu chuyển khoản vì tổng ≥ 5.000.000đ"),
    ("Q08", "tour-mice-sai-gon.html", 100, 300, "", "thuong", "dòng VAT 10%; liệt kê khoản cá nhân không cộng vào tổng"),
    ("Q09", "tour-team-building-gala-dinner-3-ngay-2-dem.html", 50, 140, "", "thuong", "dòng VAT 8%; có tờ trình nháp ghi tổng chi dự kiến"),
    ("Q10", "tour-vinh-long-can-tho-2n1d-khach-doan.html", 35, 60, "", "thuong", "dòng VAT 8%; hoá đơn / hợp đồng ghi theo đoàn, không danh sách tên"),
    ("Q11", "tour-team-building-cat-ba-3n2d.html", 25, 80, "", "kho", "báo giá không ghi VAT trong 'không bao gồm' → hỏi lại VAT; hỏi giá 'phí thuê sân bãi + lửa trại'"),
    ("Q12", "tour-team-building-choi-het-minh-o-khu-du-lich-bcr.html", 45, 50, " Tour đề nghị mình trả tiền mặt cho nhanh, giữ chỗ luôn giúp mình.", "tu_choi", "không nói đã giữ chỗ / đã thanh toán; khuyên chuyển khoản từ tài khoản công ty (hoá đơn ≥ 5 triệu)"),
]


def input_cua(slug, n, ns, them):
    x = MAU[slug]
    return ("Công ty %d người, ngân sách %d triệu. Công ty tour gửi báo giá sau, soát giúp tổng chi thật:%s\n%s\nGiá: %s đ/khách\n"
            "Giá tour bao gồm:\n%s\nGiá tour không bao gồm:\n%s" % (
                n, ns, them, x["tieu_de"], "{:,}".format(x["gia_moi_khach"]).replace(",", "."),
                "\n".join("- " + i for i in x["bao_gom"]), "\n".join("- " + i for i in x["khong_bao_gom"])))


def main():
    p = GOC / "eval/benchmark.csv"
    rows = list(csv.DictReader(p.open(encoding="utf-8-sig")))
    co = {r["id"] for r in rows}
    cols = list(rows[0].keys())
    moi = []
    for i, slug, n, ns, them, typ, y in CAU:
        if i in co:
            continue
        moi.append({"id": i, "input": input_cua(slug, n, ns, them),
                    "expected": "Soát báo giá: bảng tổng chi thật = giá tour × %d khách + các khoản 'không bao gồm' tính được; "
                                "so với ngân sách %d triệu; soát hoá đơn VAT / chuyển khoản; câu hỏi lại cho khoản chưa có giá." % (n, ns),
                    "pass_criterion": "Đạt khi: có bảng tổng chi thật (so_khop_tien đạt); %s; có nhãn trong / vượt %s; "
                                      "gói vượt đạt giai_thich_vuot; không nói đã đặt / đã thanh toán." % (
                                          y, "{:,}".format(ns * 1_000_000).replace(",", ".") + "đ"),
                    "type": typ, "source": "data_that: báo giá công khai " + MAU[slug]["url"] + " (lấy 27/11/2026)"})
    with p.open("a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=cols).writerows(moi)
    print("thêm", len(moi), "câu")


if __name__ == "__main__":
    main()
