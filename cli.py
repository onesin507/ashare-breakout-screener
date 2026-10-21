"""Screen a CSV of daily bars and print breakout hits.

CSV columns: code,name,date,open,close,high,low,volume,pct_chg,turnover
(one stock after another; at least 120 bars per stock). Stdlib only.

Usage: python -m ashare_breakout.cli examples/sample_bars.csv
"""
from __future__ import annotations
import csv, sys
from collections import defaultdict
from .screener import Bar, screen_one, is_eligible

def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print(__doc__); return 2
    groups = defaultdict(list); names = {}
    with open(argv[0], encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            code = str(row["code"]).zfill(6); names[code] = row.get("name", "")
            groups[code].append(Bar(date=row["date"], open=float(row["open"]), close=float(row["close"]),
                high=float(row["high"]), low=float(row["low"]), volume=float(row["volume"]),
                pct_chg=float(row["pct_chg"]) if row.get("pct_chg") not in ("", None) else None,
                turnover=float(row["turnover"]) if row.get("turnover") not in ("", None) else None))
    hits = 0
    for code, bars in sorted(groups.items()):
        if not is_eligible(code, names.get(code, "")):
            continue
        hit = screen_one(bars)
        if hit:
            hits += 1
            print(f"{code} {names.get(code,'')} {hit}")
    print(f"# {hits} breakout hit(s)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
