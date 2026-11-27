"""Agent dùng bộ dữ liệu data/*.json (codebase/du_lieu.py) — model giả, không gọi mạng."""
import json
import re

import agent
import du_lieu
import planner
import pytest

LINKS = {v["url"] for vs in du_lieu.D("video_review")["video"].values() for v in vs}


def _req(**kw):
    r = {"so_nguoi": 60, "so_ngay": 3, "so_dem": 2, "muc_dich": "gan_ket", "ngan_sach": 150_000_000,
         "khong_muon": [], "noi_xuat_phat": "Hà Nội", "dia_diem": "Hạ Long"}
    r.update(kw)
    return r


@pytest.fixture
def model(monkeypatch):
    """Model giả: trả JSON bóc tách đặt trước, lịch hợp lệ; đếm số lần bị nhờ dự trù đơn giá."""
    st = {"parse": {}, "du_tru": 0}

    def fake(system, user):
        if system == agent.PARSE_SYSTEM:
            return {"text": json.dumps(st["parse"])}
        if system == agent.DU_TRU_SYSTEM:
            st["du_tru"] += 1
            return {"text": json.dumps({"dia_diem": [{"ten": st["parse"].get("dia_diem"), "ly_do": "x", "chang_di": {"km": 300},
                                                       "goi": {}}]})}
        levels = re.findall(r"tiet_kiem|can_bang|cao_cap", user.split("\n")[0])
        n = st["parse"]["so_ngay"]
        days = [{"ngay": i + 1, "khoi": [{"gio": "07:00–11:00", "viec": "đi", "loai": "di_chuyen"},
                                         {"gio": "14:00–17:00", "viec": "team building", "loai": "team_building"},
                                         {"gio": "17:00–18:00", "viec": "nghỉ", "loai": "tu_do"},
                                         {"gio": "18:00–21:00", "viec": "về", "loai": "di_chuyen"}]} for i in range(n)]
        return {"text": json.dumps({"lich": {lv: days for lv in levels}})}

    monkeypatch.setattr(agent, "call_model", fake)
    monkeypatch.setattr(agent, "dinh_vi", lambda name, near=None, domestic=True: None if "Mây Xanh" in name else {"lat": 1})
    monkeypatch.setattr(agent, "note", lambda *a, **k: None)
    monkeypatch.setenv("TRAVEL_TODAY", "2026-11-27")
    return st


def test_tim_diem_theo_ten_va_bi_danh():
    assert du_lieu.tim_diem_di("Sài Gòn")["id"] == "SGN"
    assert du_lieu.tim_diem_di("tp.HCM")["id"] == "SGN"
    assert du_lieu.tim_diem_den("vịnh Hạ Long")["id"] == "halong"
    assert du_lieu.tim_diem_den("Đà Lạt, Lâm Đồng")["id"] == "dalat"
    assert du_lieu.tim_diem_den("Mũi Né")["id"] == "muine"
    assert du_lieu.tim_diem_den("Hà Giang") is None
    assert du_lieu.tim_diem_di("Hải Dương") is None


def test_ba_goi_tu_du_lieu_khop_tien_va_du_phong():
    req = _req()
    d = du_lieu.dung_diem_den(req, du_lieu.tim_diem_di("Hà Nội"), du_lieu.tim_diem_den("Hạ Long"))
    tongs = [d["calc"][lv]["tong"] for lv, _ in planner.PACKAGES]
    assert tongs == sorted(tongs)
    for lv, _ in planner.PACKAGES:
        g = d["calc"][lv]
        assert all(sl * dg == tt for _, _, sl, _, dg, tt in g["lines"])
        assert sum(x[5] for x in g["lines"]) == g["tong"]
        assert g["phong"]["so_cho"] >= 60 and g["phong"]["thieu"] == 0
        assert not g["flags"]                                    # không đơn giá nào phải thay bằng mặc định
        assert any(h["team_building"] for h in d["raw"][lv]["hoat_dong"]) or lv == "tiet_kiem"


def test_dao_chi_di_may_bay():
    req = _req(noi_xuat_phat="TP.HCM", dia_diem="Phú Quốc", muc_dich="nghi_duong", so_nguoi=30, so_ngay=4, so_dem=3)
    d = du_lieu.dung_diem_den(req, du_lieu.tim_diem_di("TP.HCM"), du_lieu.tim_diem_den("Phú Quốc"))
    assert all(d["calc"][lv]["kieu_di"] == "ve" for lv, _ in planner.PACKAGES)
    assert not any("team building" in h["ten"].lower() for lv in d["raw"] for h in d["raw"][lv]["hoat_dong"])


def test_goi_y_diem_den_hop_muc_dich_va_ngan_sach():
    req = _req(noi_xuat_phat="Đà Nẵng", dia_diem=None, so_nguoi=50, so_ngay=2, so_dem=1, ngan_sach=200_000_000)
    ds = du_lieu.goi_y_diem_den(req, du_lieu.tim_diem_di("Đà Nẵng"))
    assert 2 <= len(ds) <= 3
    for d in ds:
        assert d["den"]["phu_hop"]["gan_ket"] >= 2
        assert d["calc"]["tiet_kiem"]["tong"] <= 200_000_000


def test_goi_y_khi_ngan_sach_qua_thap_van_tra_noi_re_nhat():
    req = _req(noi_xuat_phat="TP.HCM", dia_diem=None, so_nguoi=60, ngan_sach=3_000_000)
    ds = du_lieu.goi_y_diem_den(req, du_lieu.tim_diem_di("TP.HCM"))
    assert ds and all(d["calc"]["tiet_kiem"]["tong"] > 3_000_000 for d in ds)


def test_answer_cach_c_dung_du_lieu_khong_goi_model_du_tru(model):
    model["parse"] = {"so_nguoi": 60, "noi_xuat_phat": "Hà Nội", "muc_dich": "gan_ket", "so_ngay": 3, "so_dem": 2,
                      "ngan_sach_tong": 150000000, "dia_diem": "Hạ Long"}
    out = agent.answer("60 người từ Hà Nội đi Hạ Long 3 ngày 2 đêm gắn kết, 150 triệu")["output"]
    assert model["du_tru"] == 0
    assert out.count("### Gói ") == 3
    assert "data/*.json" in out and "Thông tin thêm về Hạ Long" in out
    assert "tên dựng" not in out                                  # không in tên khách sạn / quán dựng
    yt = set(re.findall(r"https://www\.youtube\.com/watch\?v=[\w-]+", out))
    assert yt and yt <= LINKS
    assert "Vì sao vượt" in out                                   # 150tr < gói tiết kiệm → có giải thích


def test_answer_cach_a_goi_y_tu_du_lieu(model):
    model["parse"] = {"so_nguoi": 50, "noi_xuat_phat": "Đà Nẵng", "muc_dich": "gan_ket", "so_ngay": 2, "so_dem": 1,
                      "ngan_sach_tong": 200000000}
    out = agent.answer("Ngân sách 200 triệu cho 50 người, đi từ Đà Nẵng, 2 ngày 1 đêm, gắn kết")["output"]
    assert model["du_tru"] == 0
    assert "Gợi ý địa điểm" in out and "Video review từng nơi" in out


def test_answer_ngoai_du_lieu_quay_ve_model(model):
    model["parse"] = {"so_nguoi": 30, "noi_xuat_phat": "Hà Nội", "muc_dich": "nghi_duong", "so_ngay": 3, "so_dem": 2,
                      "dia_diem": "Hà Giang", "dia_diem_xac_dinh": True}
    out = agent.answer("30 người từ Hà Nội đi Hà Giang 3 ngày nghỉ dưỡng")["output"]
    assert model["du_tru"] == 1
    assert "Thông tin thêm" not in out


@pytest.mark.parametrize("tu,den,md,ngay", [("Hà Nội", "Hạ Long", "gan_ket", 3), ("TP.HCM", "Phú Quốc", "nghi_duong", 4),
                                            ("Đà Nẵng", "Hội An", "ca_hai", 2), ("Cần Thơ", "Đà Lạt", "ca_hai", 5),
                                            ("Hải Phòng", "Sa Pa", "gan_ket", 3), ("Hà Nội", "Ninh Bình", "ca_hai", 1)])
def test_lich_code_hop_le_va_khop_tien(tu, den, md, ngay):
    req = _req(noi_xuat_phat=tu, dia_diem=den, muc_dich=md, so_ngay=ngay, so_dem=ngay - 1, so_nguoi=45)
    d = du_lieu.dung_diem_den(req, du_lieu.tim_diem_di(tu), du_lieu.tim_diem_den(den))
    for lv, _ in planner.PACKAGES:
        lich = d["lich"][lv]
        assert agent.kiem_lich_trinh(req, lich) == []
        viec = " ".join(k["viec"] for day in lich for k in day["khoi"])
        for h in d["raw"][lv]["hoat_dong"]:                  # mọi hoạt động đã tính tiền đều có trong lịch
            assert h["ten"].startswith("Vé phà") or h["ten"] in viec
        for day in lich:
            gio = [(k["gio"][:5], k["gio"].split("–")[1][:5]) for k in day["khoi"] if "+1" not in k["gio"]]
            assert all(b2 >= a1 for (_, a1), (b2, _) in zip(gio, gio[1:]))   # không chồng giờ


def test_parse_khong_nhan_muc_dich_model_tu_dien(model):
    model["parse"] = {"so_nguoi": 60, "noi_xuat_phat": "Hà Nội", "muc_dich": "gan_ket", "so_ngay": 3, "so_dem": 2,
                      "ngan_sach_tong": 150000000}
    out = agent.answer("Công ty 60 người từ Hà Nội đi chơi 3 ngày, ngân sách 150 triệu")["output"]
    assert out.startswith("Để dự trù") and "mục đích" in out


def test_bo_tach_bang_code_khi_model_khong_tra_json(monkeypatch):
    monkeypatch.setattr(agent, "call_model", lambda s, u: {"text": "[giả] không phải json"})
    monkeypatch.setattr(agent, "note", lambda *a, **k: None)
    monkeypatch.setenv("TRAVEL_TODAY", "2026-11-27")
    out = agent.answer("40 nhân viên từ Sài Gòn đi Vũng Tàu 2 ngày 1 đêm nghỉ dưỡng, mỗi người 3 triệu")["output"]
    assert "Ngân sách đã hiểu: **120.000.000đ cho 40 người**" in out and out.count("### Gói ") == 3


def test_dia_diem_khong_dinh_vi_duoc_thi_hoi_lai(model):
    model["parse"] = {"so_nguoi": 50, "noi_xuat_phat": "Hà Nội", "muc_dich": "gan_ket", "so_ngay": 2, "so_dem": 1,
                      "ngan_sach_tong": 100000000, "dia_diem": "Làng Mây Xanh Tà Phìn Hồ", "dia_diem_xac_dinh": True}
    out = agent.answer("50 người từ Hà Nội đi Làng Mây Xanh Tà Phìn Hồ 2 ngày, gắn kết, 100 triệu")["output"]
    assert "không tìm được" in out and "| Hạng mục" not in out and model["du_tru"] == 0


def test_xuat_phat_tu_diem_den_khac(model):
    model["parse"] = {"so_nguoi": 12, "noi_xuat_phat": "Nha Trang", "muc_dich": "nghi_duong", "so_ngay": 2, "so_dem": 1,
                      "ngan_sach_tong": 30000000, "dia_diem": "Đà Lạt"}
    out = agent.answer("12 người từ Nha Trang đi Đà Lạt 2 ngày 1 đêm, nghỉ dưỡng, 30 triệu")["output"]
    assert model["du_tru"] == 0 and out.count("### Gói ") == 3 and "xe 16 chỗ" in out
