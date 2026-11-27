"""Xếp phòng: chọn số phòng mỗi loại sao cho đủ chỗ với chi phí/đêm thấp nhất."""
from .types import RoomPlan, RoomType


def allocate_rooms(headcount: int, types: list[RoomType]) -> RoomPlan:
    """DP knapsack: best[s] = (chi phí, số phòng, số phòng mỗi loại) nhỏ nhất để có đúng s chỗ.
    Loại không biết available được coi là đủ nhiều để phủ headcount + sức chứa lớn nhất.
    Kết quả = min best[s] với s >= headcount (hoà -> ít phòng hơn); không đủ chỗ -> lấy hết, ghi short."""
    types = [t for t in types if t.capacity > 0 and t.available != 0]
    if not types:
        return RoomPlan(counts={}, seats=0, cost_per_night=0, short=headcount)
    limit = headcount + max(t.capacity for t in types)
    n = len(types)
    best: list = [None] * (limit + 1)
    best[0] = (0, 0, (0,) * n)
    for i, t in enumerate(types):
        copies = t.available if t.available is not None else -(-limit // t.capacity)
        for _ in range(copies):
            for s in range(limit, t.capacity - 1, -1):
                prev = best[s - t.capacity]
                if prev is None:
                    continue
                counts = prev[2][:i] + (prev[2][i] + 1,) + prev[2][i + 1:]
                cand = (prev[0] + t.price, prev[1] + 1, counts)
                if best[s] is None or cand[:2] < best[s][:2]:
                    best[s] = cand
    enough = [(best[s][0], best[s][1], s) for s in range(headcount, limit + 1) if best[s] is not None]
    if enough:
        cost, _, seats = min(enough)
        short = 0
    else:
        seats = max(s for s in range(limit + 1) if best[s] is not None)
        cost, short = best[seats][0], headcount - seats
    counts = {t.kind: c for t, c in zip(types, best[seats][2]) if c}
    return RoomPlan(counts=counts, seats=seats, cost_per_night=cost, short=short)
