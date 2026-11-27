"""Chấm bằng code các phần đo được của eval/metric_spec.yaml — hỗ trợ điền cột pass (không tự ghi vào run-N.csv).

    python eval/check_outputs.py eval/run-1.csv            # in kết quả kiểm từng câu
    python eval/check_outputs.py eval/run-1.csv --json     # in JSON

Kiểm trên CHỮ output (không đọc code agent):
  so_khop_tien   mỗi dòng số lượng × đơn giá = thành tiền · tổng = cộng các dòng · phát sinh = 5% phần còn lại (làm tròn
                 1.000đ) · mỗi người = tổng / số người (làm tròn 1.000đ)
  xep_phong_dung tổng chỗ của cơ cấu phòng ≥ số người · số xe × sức chứa ≥ số người
  zero_line      có dòng chi phí 0đ không
  claims         có câu khẳng định đã đặt / đã giữ chỗ / đã cọc không (bỏ qua câu phủ định)
  budget_labels  số gói có nhãn trong / vượt ngân sách
Các ý còn lại của pass_criterion (đúng nhánh, hỏi lại đúng, giải thích hợp lý…) do người chấm đọc output.
"""
import csv
import json
import re
import sys

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

csv.field_size_limit(10 ** 8)
MONEY = r"([\d.]+)đ"


def money(s):
    return int(s.replace(".", ""))


def packages(out):
    """Tách các bảng chi phí: mỗi bảng → {"rows": [(qty, price, total, name)], "tong", "moi_nguoi", "n", "cho", "head"}."""
    res = []
    cur = None
    for line in out.splitlines():
        if line.startswith("### "):
            cur = {"head": line, "rows": [], "tong": None, "moi_nguoi": None, "n": None, "cho": None, "xe": []}
            res.append(cur)
            continue
        if cur is None:
            continue
        m = re.match(r"\|\s*(.+?)\s*\|\s*([\d.]+)\s+(\S+)\s*\|\s*" + MONEY + r"\s*\|\s*" + MONEY + r"\s*\|", line)
        if m:
            name, qty, unit, price, total = m.groups()
            cur["rows"].append((money(qty), money(price), money(total), name, unit))
            mx = re.search(r"\((\d+) chỗ", name)
            if unit in ("xe",) and mx:
                cur["xe"].append((money(qty), int(mx.group(1))))
            continue
        m = re.match(r"\|\s*\*\*Tổng cả đoàn\*\*.*\*\*" + MONEY + r"\*\*", line)
        if m:
            cur["tong"] = money(m.group(1))
        m = re.match(r"\|\s*\*\*Mỗi người\*\* \((\d+) người\).*\*\*" + MONEY + r"\*\*", line)
        if m:
            cur["n"], cur["moi_nguoi"] = int(m.group(1)), money(m.group(2))
        m = re.search(r"=\s*(\d+) chỗ cho (\d+) người", line)
        if m:
            cur["cho"] = int(m.group(1))
    return [p for p in res if p["rows"]]


def check_money(p):
    errs = []
    for qty, price, total, name, _ in p["rows"]:
        if qty * price != total:
            errs.append("dòng '%s': %d × %d ≠ %d" % (name[:40], qty, price, total))
    rows = [r for r in p["rows"] if not r[3].startswith("Phát sinh")]
    ps = [r for r in p["rows"] if r[3].startswith("Phát sinh")]
    sub = sum(r[2] for r in rows)
    if ps:
        exp = int(round(sub * 0.05 / 1000.0)) * 1000
        if ps[0][2] != exp:
            errs.append("phát sinh %d ≠ 5%% × %d = %d" % (ps[0][2], sub, exp))
    tong = sub + sum(r[2] for r in ps)
    if p["tong"] != tong:
        errs.append("tổng %s ≠ cộng dòng %d" % (p["tong"], tong))
    if p["n"] and p["moi_nguoi"] is not None:
        exp = int(round(tong / p["n"] / 1000.0)) * 1000
        if p["moi_nguoi"] != exp:
            errs.append("mỗi người %d ≠ %d" % (p["moi_nguoi"], exp))
    return errs


def check_capacity(p):
    errs = []
    n = p["n"]
    has_lodging = any(r[3].startswith("Lưu trú") for r in p["rows"])
    if has_lodging and n:
        extra = sum(r[0] for r in p["rows"] if "Cơ sở thứ hai" in r[3])
        if p["cho"] is None:
            errs.append("có lưu trú nhưng không ghi cơ cấu phòng")
        elif p["cho"] < n and not extra:
            errs.append("phòng %d chỗ < %d người" % (p["cho"], n))
    for so_xe, suc in p["xe"]:
        if n and so_xe * suc < n:
            errs.append("xe %d × %d chỗ < %d người" % (so_xe, suc, n))
    return errs


CLAIM = re.compile(r"[^.\n]*\b(đã|vừa)\s+(đặt|giữ chỗ|giữ phòng|cọc|chuyển khoản|thanh toán)[^.\n]*", re.I)


def check_case(out):
    ps = packages(out)
    claims = [m.group(0).strip() for m in CLAIM.finditer(out) if not re.search(r"không|chưa", m.group(0), re.I)]
    return {
        "so_bang": len(ps),
        "so_khop_tien": {p["head"][4:60]: check_money(p) for p in ps},
        "xep_phong_dung": {p["head"][4:60]: check_capacity(p) for p in ps},
        "zero_line": bool(re.search(r"\|\s*0đ\s*\|", out)),
        "claims": claims,
        "budget_labels": len(re.findall(r"trong ngân sách|vượt ngân sách", " ".join(p["head"] for p in ps))),
    }


def main(path):
    with open(path, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    allres = {}
    for r in rows:
        res = check_case(r.get("output", ""))
        allres[r["id"]] = res
        if "--json" in sys.argv:
            continue
        money_bad = {k: v for k, v in res["so_khop_tien"].items() if v}
        cap_bad = {k: v for k, v in res["xep_phong_dung"].items() if v}
        print("%-4s %-8s bảng=%d tiền=%s phòng/xe=%s 0đ=%s claim=%s nhãn_NS=%d" % (
            r["id"], r["type"], res["so_bang"], "OK" if not money_bad else money_bad,
            "OK" if not cap_bad else cap_bad, res["zero_line"], res["claims"] or "-", res["budget_labels"]))
    if "--json" in sys.argv:
        print(json.dumps(allres, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1])
