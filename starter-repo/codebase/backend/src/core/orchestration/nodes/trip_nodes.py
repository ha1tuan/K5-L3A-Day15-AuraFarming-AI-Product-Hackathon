"""Các node của graph. Task 5: research (từ khoá -> tìm kiếm -> trích ứng viên -> kiểm nguồn -> xếp hạng).
Task 7 bổ sung: parse_request, select, schedule_node, validate_node, render_node, infeasible_node.
Gọi model CHỈ qua ai.call_model; công cụ qua codebase/tools.py.
"""
import re
import unicodedata
from typing import Optional

from ai import call_model
from tools import dinh_vi, tim_kiem_web  # noqa: F401  (dinh_vi dùng ở các node sau)

from src.core.orchestration.prompts.trip_prompts import EXTRACT_SYSTEM, QUERY_SYSTEM, SELECT_SYSTEM
from src.core.orchestration.utils.utils import _parse_json
from src.core.planning.estimates import Estimates, load_estimates
from src.core.planning.pricing import TIERS, price_packages
from src.core.planning.request import parse_vnd
from src.core.planning.scheduler import load_menus, load_programs, schedule
from src.core.planning.types import Candidate, RoomType, TierPick, TripRequest, Violation
from src.core.planning.validator import validate

GROUPS = ("luu_tru", "an_uong", "hoat_dong")
MAX_QUERIES_PER_GROUP = 3
MAX_HITS_PER_GROUP = 12
LODGING_PER_STAR = 3
LIMITS = {"luu_tru": 9, "an_uong": 8, "hoat_dong": 6}
MAX_REPAIR = 2
REASON_MAX = 200


def _fold(s: str) -> str:
    """Bỏ dấu, chữ thường, gom khoảng trắng — để so tên."""
    s = unicodedata.normalize("NFD", str(s).lower().replace("đ", "d"))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s).strip()


def _slug(group: str, name: str) -> str:
    return "%s:%s" % (group, re.sub(r"[^a-z0-9]+", "-", _fold(name)).strip("-"))


def _default_queries(req: TripRequest) -> dict[str, list[str]]:
    dest = (req.destination or "").strip()
    activity = ["team building", "gala dinner"] if req.purpose != "nghi_duong" else ["tham quan", "spa thư giãn"]
    if req.purpose == "ca_hai":
        activity = ["team building", "tham quan"]
    return {
        "luu_tru": ["khách sạn %d sao %s nhận đoàn" % (s, dest) for s in (3, 4, 5)],
        "an_uong": ["nhà hàng đoàn %s" % dest, "set menu đoàn %s" % dest],
        "hoat_dong": ["%s %s" % (a, dest) for a in activity],
    }


def plan_queries(req: TripRequest) -> dict[str, list[str]]:
    """Model lên từ khoá (≤ 3 mỗi nhóm); JSON hỏng hoặc thiếu nhóm -> bộ mặc định do code ghép."""
    defaults = _default_queries(req)
    user = "Địa điểm: %s\nSố người: %d\nSố ngày: %d\nMục đích: %s" % (
        req.destination, req.headcount, req.days, req.purpose)
    data = _parse_json(call_model(QUERY_SYSTEM, user)["text"])
    out = {}
    for g in GROUPS:
        raw = data.get(g) if isinstance(data, dict) else None
        qs = [q.strip() for q in raw if isinstance(q, str) and q.strip()] if isinstance(raw, list) else []
        out[g] = qs[:MAX_QUERIES_PER_GROUP] or defaults[g]
    return out


def _number_hits(hits_by_group: dict[str, list[dict]]) -> list[dict]:
    """Đánh số toàn cục k = 1.. qua các nhóm; mỗi phần tử: hit + group."""
    flat = []
    for g in GROUPS:
        for h in hits_by_group.get(g, []):
            flat.append({**h, "group": g})
    return flat


def _safe(s) -> str:
    """Bỏ < > để đoạn trích không đóng được khối <du_lieu>."""
    return str(s).replace("<", "(").replace(">", ")")


def _extract_prompt(flat: list[dict]) -> str:
    lines = ["<du_lieu>"]
    for k, h in enumerate(flat, 1):
        lines.append("[%d] (nhóm: %s) %s | %s | %s" % (k, h["group"], _safe(h.get("title", "")),
                                                       _safe(h.get("domain", "")), _safe(h.get("snippet", ""))))
    lines.append("</du_lieu>")
    return "\n".join(lines)


def _price_in_snippet(text, snippet: str) -> Optional[int]:
    """Giá chỉ nhận khi chuỗi nguyên văn nằm trong đoạn trích và parse ra > 0."""
    if not isinstance(text, str) or not text.strip() or text.strip().lower() not in snippet.lower():
        return None
    v = parse_vnd(text)
    return v if v and v > 0 else None


def _count_in_snippet(text, snippet: str) -> Optional[int]:
    if not isinstance(text, str) or not text.strip() or text.strip().lower() not in snippet.lower():
        return None
    m = re.search(r"\d+", text.replace(".", "").replace(",", ""))
    v = int(m.group()) if m else 0
    return v if v > 0 else None


def _int(v) -> Optional[int]:
    try:
        return int(v) if v is not None and not isinstance(v, bool) else None
    except (TypeError, ValueError):
        return None


def _room_types(raw, hit: dict) -> list[RoomType]:
    rooms = []
    for r in raw if isinstance(raw, list) else []:
        if not isinstance(r, dict):
            continue
        price = _price_in_snippet(r.get("price_text"), hit["snippet"])
        cap = _int(r.get("capacity"))
        if price is None or not cap or cap <= 0 or not str(r.get("kind") or "").strip():
            continue
        rooms.append(RoomType(kind=str(r["kind"]).strip(), capacity=cap, price=price,
                              available=_count_in_snippet(r.get("available_text"), hit["snippet"]),
                              estimated=False, source_url=hit["url"]))
    return rooms


def extract_candidates(req: TripRequest, hits_by_group: dict[str, list[dict]]) -> list[Candidate]:
    """Model trích ứng viên từ các hit đánh số; code kiểm hit tồn tại, tên có trong hit, giá/sức chứa có trong đoạn trích."""
    flat = _number_hits(hits_by_group)
    if not flat:
        return []
    data = _parse_json(call_model(EXTRACT_SYSTEM, _extract_prompt(flat))["text"])
    items = data.get("candidates") if isinstance(data, dict) else None
    cands = []
    for it in items if isinstance(items, list) else []:
        if not isinstance(it, dict):
            continue
        k, name, group = _int(it.get("hit")), it.get("name"), it.get("group")
        if k is None or not 1 <= k <= len(flat) or group not in GROUPS:
            continue
        if not isinstance(name, str) or not _fold(name):
            continue
        hit = flat[k - 1]
        if _fold(name) not in _fold("%s %s" % (hit.get("title", ""), hit.get("snippet", ""))):
            continue
        snippet = hit.get("snippet", "")
        c = Candidate(id=_slug(group, name), name=name.strip(), group=group,
                      reason=str(it.get("reason") or "").strip(), source_url=hit["url"],
                      domain=hit.get("domain", ""))
        stars = _int(it.get("stars"))
        if group == "luu_tru":
            c.stars = stars if stars in (1, 2, 3, 4, 5) else None
            c.room_types = _room_types(it.get("room_types"), hit)
        else:
            c.price_per_pax = _price_in_snippet(it.get("price_text"), snippet)
            if c.price_per_pax:
                c.price_source_url = hit["url"]
        c.capacity = _count_in_snippet(it.get("capacity_text"), snippet)
        cands.append(c)
    return cands


def _merge(base: Candidate, other: Candidate) -> None:
    """Gộp trường còn thiếu của bản trùng vào bản đầu."""
    for f in ("reason", "stars", "price_per_pax", "price_source_url", "capacity"):
        if not getattr(base, f) and getattr(other, f):
            setattr(base, f, getattr(other, f))
    if not base.room_types and other.room_types:
        base.room_types = other.room_types
    if not base.menu_items and other.menu_items:
        base.menu_items = other.menu_items


def ground_and_rank(cands: list[Candidate]) -> dict[str, list[Candidate]]:
    """Gộp trùng theo tên chuẩn hoá, mentions = số tên miền khác nhau, xếp giảm dần, giới hạn mỗi nhóm."""
    merged: dict[str, Candidate] = {}
    domains: dict[str, set] = {}
    for c in cands:
        if c.id in merged:
            _merge(merged[c.id], c)
        else:
            merged[c.id] = c
            domains[c.id] = set()
        if c.domain:
            domains[c.id].add(c.domain)
    for cid, c in merged.items():
        c.mentions = max(1, len(domains[cid]))
    ranked: dict[str, list[Candidate]] = {}
    for g in GROUPS:
        items = sorted((c for c in merged.values() if c.group == g), key=lambda c: -c.mentions)
        if g == "luu_tru":
            per_star: dict = {}
            kept = []
            for c in items:
                if per_star.get(c.stars, 0) < LODGING_PER_STAR:
                    per_star[c.stars] = per_star.get(c.stars, 0) + 1
                    kept.append(c)
            items = kept
        if items:
            ranked[g] = items[:LIMITS[g]]
    return ranked


def research(state: dict) -> dict:
    """Node research: trả state riêng phần {"ranked", "estimate_only"}; không có kết quả tìm kiếm -> estimate_only."""
    req: TripRequest = state["request"]
    queries = plan_queries(req)
    hits_by_group: dict[str, list[dict]] = {}
    for g in GROUPS:
        seen, hits = set(), []
        for q in queries[g]:
            for h in tim_kiem_web(q):
                if h.get("url") and h["url"] not in seen:
                    seen.add(h["url"])
                    hits.append(h)
        hits_by_group[g] = hits[:MAX_HITS_PER_GROUP]
    if not any(hits_by_group.values()):
        return {"ranked": {}, "estimate_only": True}
    ranked = ground_and_rank(extract_candidates(req, hits_by_group))
    return {"ranked": ranked, "estimate_only": not ranked}


def _select_prompt(req: TripRequest, ranked: dict, violations: Optional[list]) -> str:
    lines = ["Địa điểm: %s" % _safe(req.destination), "Số người: %d" % req.headcount,
             "Số ngày: %d, số đêm: %d" % (req.days, req.nights), "Mục đích: %s" % req.purpose,
             "Số bữa cần chọn quán: %d" % max(1, 2 * req.days - 1), "<du_lieu>"]
    for g in GROUPS:
        for c in ranked.get(g, []):
            star = " | %d sao" % c.stars if c.stars else ""
            lines.append("%s | nhóm: %s | %s%s | nguồn: %d trang | %s" % (
                c.id, g, _safe(c.name), star, c.mentions, _safe(c.reason)))
    lines.append("</du_lieu>")
    if violations:
        lines.append("vi_pham (lần chọn trước):")
        lines += ["- %s: %s" % (v.code, _safe(v.message)) for v in violations]
    return "\n".join(lines)


def _empty_picks() -> dict[str, TierPick]:
    return {t: TierPick() for t in TIERS}


def select_for_tiers(req: TripRequest, ranked: dict, violations: Optional[list] = None,
                     est: Optional[Estimates] = None, sink: Optional[list] = None) -> dict[str, TierPick]:
    """Một lần gọi model chọn cơ sở cho 3 gói. Code bỏ id không có trong ranked (ghi ID_KHONG_TON_TAI vào sink)
    và hạ khách sạn sai hạng sao của gói về None (mức chung). Không có ứng viên -> không gọi model."""
    if not any(ranked.get(g) for g in GROUPS):
        return _empty_picks()
    est = est or load_estimates()
    known = {g: {c.id: c for c in ranked.get(g, [])} for g in GROUPS}
    data = _parse_json(call_model(SELECT_SYSTEM, _select_prompt(req, ranked, violations))["text"])
    data = data if isinstance(data, dict) else {}
    picks = {}
    for tier in TIERS:
        raw = data.get(tier) if isinstance(data.get(tier), dict) else {}

        def keep(ids, group) -> list[str]:
            out = []
            for i in ids if isinstance(ids, list) else []:
                if i in known[group]:
                    out.append(i)
                elif isinstance(i, str) and sink is not None:
                    sink.append(Violation("ID_KHONG_TON_TAI", "Id %s không có trong danh sách ứng viên" % i, i))
            return out

        hotel = raw.get("hotel")
        if isinstance(hotel, str) and hotel.strip().lower() in ("", "null", "none"):
            hotel = None
        if isinstance(hotel, str) and hotel not in known["luu_tru"]:
            if sink is not None:
                sink.append(Violation("ID_KHONG_TON_TAI", "Id %s không có trong danh sách ứng viên" % hotel, hotel))
            hotel = None
        if isinstance(hotel, str) and known["luu_tru"][hotel].stars != est.tier_stars[tier]:
            hotel = None
        restaurants, activities = keep(raw.get("restaurants"), "an_uong"), keep(raw.get("activities"), "hoat_dong")
        chosen = set(restaurants + activities + ([hotel] if isinstance(hotel, str) else []))
        reasons = raw.get("reasons") if isinstance(raw.get("reasons"), dict) else {}
        picks[tier] = TierPick(hotel=hotel if isinstance(hotel, str) else None, restaurants=restaurants,
                               activities=activities,
                               reasons={k: v[:REASON_MAX] for k, v in reasons.items()
                                        if k in chosen and isinstance(v, str)})
    return picks


def select(state: dict) -> dict:
    """Node select: {"picks", "pick_violations"}; ranked rỗng / estimate_only -> không gọi model."""
    ranked = {} if state.get("estimate_only") else state.get("ranked") or {}
    sink: list = []
    picks = select_for_tiers(state["request"], ranked, state.get("violations"), state.get("est"), sink)
    return {"picks": picks, "pick_violations": sink}


def _by_id(ranked: dict) -> dict:
    return {c.id: c for items in (ranked or {}).values() for c in items}


def price(state: dict) -> dict:
    """Node price: khách sạn theo pick -> Candidate, rồi price_packages."""
    by_id = _by_id(state.get("ranked"))
    hotels = {t: by_id.get(p.hotel) for t, p in state["picks"].items()}
    est = state.get("est") or load_estimates()
    return {"packages": price_packages(state["request"], state.get("origin_pt"), state.get("dest_pt"), hotels, est)}


def schedule_node(state: dict) -> dict:
    """Node schedule: một Plan cho mỗi gói; menus/programs lấy từ state nếu có, không thì từ data/."""
    est = state.get("est") or load_estimates()
    menus = state.get("menus") or load_menus()
    programs = state.get("programs") or load_programs()
    ranked = state.get("ranked") or {}
    return {"plans": [schedule(state["request"], pkg, state["picks"].get(pkg.tier) or TierPick(), ranked, est,
                               menus, programs) for pkg in state["packages"]]}


def validate_node(state: dict) -> dict:
    """Node validate: vi phạm của từng gói + id lạ của bước chọn. repair_round = số lần sửa đã chạy
    (lần kiểm đầu giữ 0; mỗi lần kiểm sau một lượt sửa tăng 1). Hết lần sửa mà còn vi phạm -> trả thêm
    "warnings" (nối vào cảnh báo cũ) để router giữ thuần."""
    req = state["request"]
    found = list(state.get("pick_violations") or [])
    for plan, pkg in zip(state["plans"], state["packages"]):
        found += validate(req, plan, pkg)
    rounds = state.get("repair_round", 0) + (1 if "violations" in state else 0)
    out = {"violations": found, "repair_round": rounds}
    if found and rounds >= MAX_REPAIR:
        out["warnings"] = list(state.get("warnings") or []) + [
            "Kế hoạch còn %d điểm chưa đạt sau %d lần sửa, cần kiểm tra lại: %s" % (
                len(found), rounds, "; ".join(v.message for v in found[:5]))]
    return out


def route_after_validate(state: dict) -> str:
    """"repair" nếu còn vi phạm và chưa đủ MAX_REPAIR lần sửa; không thì "explain" (giữ kế hoạch).
    Hàm thuần: cảnh báo do validate_node trả."""
    if state.get("violations") and state.get("repair_round", 0) < MAX_REPAIR:
        return "repair"
    return "explain"
