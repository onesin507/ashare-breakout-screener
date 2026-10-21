"""Experimental: fetch daily bars from Tencent's public quote endpoint and
emit this project's CSV format (code,name,date,open,close,high,low,volume,
pct_chg,turnover).

Endpoint shape (public, no key): web.ifzq.gtimg.cn/appstock/app/fqkline/get
with param=<sh|sz><code>,day,<start>,<end>,<count>,qfq

Status: the *parser* is unit-tested offline; the live endpoint is provided
by a third party, may change or be unreachable from some networks, and its
terms apply. Turnover is not returned by this endpoint and is left blank
(the screener's turnover rule is skipped when the column is empty).
If fetching fails for you, any other source that can produce the CSV
format works just as well — the screener does not care where bars came from.
"""
from __future__ import annotations
import json, urllib.request

URL = "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={mkt}{code},day,,,{count},qfq"
HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://gu.qq.com/"}

def market_prefix(code: str) -> str:
    return "sh" if str(code).zfill(6)[0] == "6" else "sz"

def parse_fqkline(payload: dict, code: str):
    """payload -> list of dict rows (date/open/close/high/low/volume).
    Accepts the qfqday (preferred) or day arrays."""
    node = payload.get("data", {}).get(market_prefix(code) + str(code).zfill(6), {})
    rows = node.get("qfqday") or node.get("day") or []
    out, prev_close = [], None
    for r in rows:
        date, o, c, h, l, v = r[0], float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5])
        pct = round((c / prev_close - 1) * 100, 2) if prev_close else 0.0
        out.append({"code": str(code).zfill(6), "date": date, "open": o, "close": c,
                    "high": h, "low": l, "volume": v, "pct_chg": pct, "turnover": ""})
        prev_close = c
    return out

def fetch_bars(code: str, count: int = 320, timeout: int = 20):
    url = URL.format(mkt=market_prefix(code), code=str(code).zfill(6), count=count)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = json.loads(resp.read().decode("utf-8", "ignore"))
    return parse_fqkline(payload, code)

if __name__ == "__main__":  # python -m ashare_breakout.fetch_tencent 002962
    import csv, sys
    rows = fetch_bars(sys.argv[1])
    wcsv = csv.DictWriter(sys.stdout, fieldnames=["code", "name", "date", "open", "close", "high", "low", "volume", "pct_chg", "turnover"])
    wcsv.writeheader()
    for r in rows:
        wcsv.writerow({**r, "name": ""})
