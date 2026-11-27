import json
from types import SimpleNamespace

import pytest

import agent
import ai
from src.core.orchestration.nodes import trip_nodes as tn
from src.core.orchestration.prompts.trip_prompts import (EXTRACT_SYSTEM, PARSE_SYSTEM, QUERY_SYSTEM,
                                                          SELECT_SYSTEM)

RAW_C = {"headcount": 60, "days": 3, "origin": "Hà Nội", "purpose": "gan_ket", "budget_text": "150 triệu",
         "destination": "Hạ Long", "country": "VN"}
HITS = [
    {"title": "Khách sạn Mường Thanh Hạ Long", "url": "https://a.vn/mt", "domain": "a.vn",
     "snippet": "Khách sạn Mường Thanh Hạ Long 4 sao nhận đoàn."},
    {"title": "Nhà hàng Hồng Hạnh", "url": "https://b.vn/hh", "domain": "b.vn",
     "snippet": "Nhà hàng Hồng Hạnh nhận đoàn 200 khách."},
]
EXTRACT = {"candidates": [
    {"group": "luu_tru", "name": "Khách sạn Mường Thanh Hạ Long", "hit": 1, "stars": 4},
    {"group": "an_uong", "name": "Nhà hàng Hồng Hạnh", "hit": 2}]}
PICK = {"hotel": "luu_tru:khach-san-muong-thanh-ha-long", "restaurants": ["an_uong:nha-hang-hong-hanh"],
        "activities": []}


@pytest.fixture
def world(monkeypatch):
    """Model giả trả JSON theo prompt hệ thống; tìm kiếm / định vị giả."""
    seen = {"parse": [], "raw": dict(RAW_C)}

    def fake(system, user):
        if system == PARSE_SYSTEM:
            seen["parse"].append(user)
            out = seen["raw"]
        elif system == QUERY_SYSTEM:
            out = {}
        elif system == EXTRACT_SYSTEM:
            out = EXTRACT
        elif system == SELECT_SYSTEM:
            out = {t: PICK for t in ("tiet_kiem", "can_bang", "cao_cap")}
        else:
            raise AssertionError("prompt lạ")
        return {"text": json.dumps(out, ensure_ascii=False), "model": "t", "tokens_in": 0, "tokens_out": 0}

    monkeypatch.setattr(tn, "call_model", fake)
    monkeypatch.setattr(tn, "tim_kiem_web", lambda q: HITS)
    monkeypatch.setattr(tn, "dinh_vi", lambda name, near=None, domestic=True: None)
    monkeypatch.setenv("TRAVEL_TODAY", "2026-11-27")
    return seen


def test_answer_c_returns_three_plans_text(world):
    out = agent.answer("60 người từ Hà Nội đi Hạ Long 3 ngày, gắn kết, 150 triệu")["output"]
    for s in ("Ngân sách đã hiểu: 150.000.000đ cho 60 người", "Tiết kiệm", "Cân bằng", "Cao cấp",
              "Khách sạn Mường Thanh Hạ Long", "Nhà hàng Hồng Hạnh", "04/12/2026"):
        assert s in out
    assert "Giá tham khảo; hệ thống không đặt chỗ" in out


def test_answer_estimate_only_names_no_venue(world, monkeypatch):
    monkeypatch.setattr(tn, "tim_kiem_web", lambda q: [])
    out = agent.answer("60 người từ Hà Nội đi Hạ Long 3 ngày, gắn kết, 150 triệu")["output"]
    assert "chưa tìm được nguồn" in out and "Mường Thanh" not in out and "Hồng Hạnh" not in out


def test_answer_ask_back(world):
    world["raw"] = {"headcount": 60, "days": 3, "budget_text": "150 triệu", "destination": "Hạ Long"}
    out = agent.answer("60 người đi Hạ Long 3 ngày 150 triệu")["output"]
    assert out.startswith("Để lập kế hoạch, mình cần thêm:")
    assert "điểm xuất phát" in out and "mục đích" in out and "Tiết kiệm" not in out


def test_answer_refused_out_of_range(world):
    world["raw"] = {**RAW_C, "headcount": 800}
    assert "500" in agent.answer("800 người")["output"]


def test_answer_entry_b_not_supported_yet(world):
    world["raw"] = {**RAW_C, "budget_text": None}
    out = agent.answer("60 người từ Hà Nội đi Hạ Long 3 ngày, gắn kết")["output"]
    assert out.startswith("Bản hiện tại lập kế hoạch khi có cả kinh phí và địa điểm")
    assert "Tiết kiệm" not in out


def test_card_number_not_echoed(world):
    text = ("60 người từ Hà Nội đi Hạ Long 3 ngày, gắn kết, 150 triệu. Đặt luôn giúp tôi, "
            "thanh toán bằng thẻ 4111 1111 1111 1111 hoặc 5500000000000004")
    out = agent.answer(text)["output"]
    assert "4111" not in out and "5500000000000004" not in out
    assert "4111" not in world["parse"][0] and "5500000000000004" not in world["parse"][0]
    assert "không đặt chỗ" in out and "Tiết kiệm" in out
    assert "đã đặt" not in out.lower()


def test_fake_model_falls_back_to_ask_back(monkeypatch):
    monkeypatch.setattr(tn, "call_model", lambda s, u: {"text": "[giả] không phải json", "model": "fake",
                                                         "tokens_in": 0, "tokens_out": 0})
    assert agent.answer("đi chơi")["output"].startswith("Để lập kế hoạch")


def test_gemini_branch_reads_usage(monkeypatch):
    calls = {}

    class Models:
        def generate_content(self, model, contents, config):
            calls.update(model=model, contents=contents, system=config.system_instruction)
            usage = SimpleNamespace(prompt_token_count=12, candidates_token_count=5, thoughts_token_count=3)
            return SimpleNamespace(text='{"a": 1}', usage_metadata=usage)

    monkeypatch.setattr(ai, "MODEL_PROVIDER", "gemini")
    monkeypatch.setattr(ai, "MODEL_NAME", "gemini-x")
    monkeypatch.setattr(ai, "_gemini_client", lambda: SimpleNamespace(models=Models()))
    out = ai.call_model("hệ thống", "người dùng")
    assert out == {"text": '{"a": 1}', "model": "gemini-x", "tokens_in": 12, "tokens_out": 8}
    assert calls == {"model": "gemini-x", "contents": "người dùng", "system": "hệ thống"}
