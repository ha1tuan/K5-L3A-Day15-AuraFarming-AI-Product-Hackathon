"""Các node của graph. Task 5: research (từ khoá -> tìm kiếm -> trích ứng viên -> kiểm nguồn -> xếp hạng).
Task 7 bổ sung: parse_request, select, schedule_node, validate_node, render_node, infeasible_node.
Gọi model CHỈ qua ai.call_model; công cụ qua codebase/tools.py.
"""
import re
import unicodedata
from typing import Optional

from ai import call_model
from tools import dinh_vi, tim_kiem_web  # noqa: F401  (dinh_vi dùng ở các node sau)

from src.core.orchestration.prompts.trip_prompts import EXTRACT_SYSTEM, QUERY_SYSTEM
from src.core.orchestration.utils.utils import _parse_json
from src.core.planning.request import parse_vnd
from src.core.planning.types import Candidate, RoomType, TripRequest

GROUPS = ("luu_tru", "an_uong", "hoat_dong")
MAX_QUERIES_PER_GROUP = 3
MAX_HITS_PER_GROUP = 12
LODGING_PER_STAR = 3
LIMITS = {"luu_tru": 9, "an_uong": 8, "hoat_dong": 6}


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


def _extract_prompt(flat: list[dict]) -> str:
    lines = ["<du_lieu>"]
    for k, h in enumerate(flat, 1):
        lines.append("[%d] (nhóm: %s) %s | %s | %s" % (k, h["group"], h.get("title", ""), h.get("domain", ""),
                                                       h.get("snippet", "")))
    lines.append("</du_lieu>")
    return "\n".join(lines)


def _price_in_snippet(text, snippet: str) -> Optional[int]:
    """Giá chỉ nhận khi chuỗi nguyên văn nằm trong đoạn trích và parse ra > 0."""
    if not isinstance(text, str) or not text.strip() or text.strip().lower() not in snippet.lower():
        return None
    # parse_vnd đọc sai "350.000đ" (đ nằm trong lookahead chữ cái) -> bỏ ký hiệu tiền trước khi parse.
    v = parse_vnd(re.sub(r"(?i)\s*(đ|₫|vnd|vnđ)(?![a-zà-ỹ])", "", text))
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
