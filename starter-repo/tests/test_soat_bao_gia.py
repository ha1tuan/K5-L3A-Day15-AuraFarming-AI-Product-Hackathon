"""Soát báo giá tour đoàn (codebase/soat_bao_gia.py) trên báo giá công khai thật ở data/bao_gia_mau.json."""
import json
import os
import sys

import agent
import soat_bao_gia as S

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "eval"))
import check_outputs as C  # noqa: E402

MAU = {x["url"].rsplit("/", 1)[1]: x for x in json.load(open(os.path.join(S.DATA, "bao_gia_mau.json"), encoding="utf-8"))["bao_gia"]}


def _input(slug, n=40, ns=100, them=""):
    x = MAU[slug]
    return ("Công ty %d người%s, ngân sách %d triệu. Công ty tour gửi báo giá sau, soát giúp:\n%s\nGiá: %s đ/khách\n"
            "Giá tour bao gồm:\n%s\nGiá tour không bao gồm:\n%s" % (
                n, them, ns, x["tieu_de"], "{:,}".format(x["gia_moi_khach"]).replace(",", "."),
                "\n".join("- " + i for i in x["bao_gom"]), "\n".join("- " + i for i in x["khong_bao_gom"])))


def _run(text, monkeypatch):
    monkeypatch.setattr(agent, "note", lambda *a, **k: None)
    monkeypatch.setattr(agent, "call_model", lambda s, u: (_ for _ in ()).throw(AssertionError("không được gọi model")))
    return agent.answer(text)["output"]


def test_bcr_vat_10_va_tong_that(monkeypatch):
    out = _run(_input("tour-team-building-choi-het-minh-o-khu-du-lich-bcr.html", 45, 45), monkeypatch)
    assert "950.000đ/khách × 45 = 42.750.000đ" in out
    assert "| Thuế VAT 10%" in out and "4.275.000đ" in out
    assert "❌ vượt ngân sách" in out and "nằm trong" in out          # giá báo trong NS, tổng thật vượt
    ck = C.check_case(out)
    assert ck["so_bang"] == 1 and all(not v for v in ck["so_khop_tien"].values())


def test_ve_co_gia_duoc_cong(monkeypatch):
    out = _run(_input("tour-da-lat-cam-trai-3-ngay-2-dem-co-luu-tru-cho-khach-doan.html", 40, 120), monkeypatch)
    assert "Vé cáp treo đồi Robin" in out and "80.000đ" in out and "| Thuế VAT 8%" in out
    assert "Khoản cá nhân, công ty không phải chịu" in out


def test_khong_noi_vat_thi_hoi_va_tam_tinh(monkeypatch):
    out = _run(_input("tour-team-building-mui-ne-phan-thiet-2n1d.html", 30, 50), monkeypatch)
    assert "không nói" in out and "Thuế VAT 10%" in out


def test_thieu_so_nguoi_thi_hoi_lai(monkeypatch):
    t = _input("tour-team-building-choi-het-minh-o-khu-du-lich-bcr.html").replace("Công ty 40 người", "Công ty mình")
    out = _run(t, monkeypatch)
    assert out.startswith("Để soát báo giá") and "số người" in out and "| Hạng mục" not in out


def test_tran_phuc_loi(monkeypatch):
    out = _run(_input("tour-team-building-nha-trang-4n3d.html", 40, 400) + "\nLương bình quân 8 triệu/tháng.", monkeypatch)
    assert "vượt trần" in out


def test_cau_cu_khong_vao_nhanh_bao_gia():
    assert not S.la_bao_gia("Công ty mình 60 người, xuất phát từ Hà Nội, muốn đi Hạ Long 3 ngày 2 đêm, ngân sách 150 triệu.")
