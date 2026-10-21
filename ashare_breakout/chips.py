"""Simplified chip-distribution estimate from daily bars (model, not truth).

Each of the last `window` bars contributes its volume as a triangular
distribution over [low, high] peaking at the close, decayed by
0.995 ** days_ago, binned at `bin_width`. This mirrors the estimator the
author uses for ranking (profit ratio / trapped supply overhead).

It is a *model estimate* for relative comparison only. It is not exchange
or vendor chip data, and it was deliberately NOT used as a screening
signal in the washout score (no ground truth to validate against).
"""
from __future__ import annotations
from .screener import Bar

def estimate_chips(bars: list[Bar], window: int = 500, decay: float = 0.995,
                   bin_width: float = 0.2):
    bars = sorted(bars, key=lambda b: b.date)[-window:]
    n = len(bars)
    if n < 60:
        return None
    price = bars[-1].close
    lo_all, hi_all = min(b.low for b in bars), max(b.high for b in bars)
    if hi_all <= lo_all:
        return None
    nbins = int((hi_all - lo_all) / bin_width) + 2
    chips = [0.0] * nbins
    for j, b in enumerate(bars):
        w = decay ** (n - 1 - j)
        if b.volume <= 0:
            continue
        if b.high <= b.low:
            chips[int((b.close - lo_all) / bin_width)] += b.volume * w
            continue
        b0, b1 = int((b.low - lo_all) / bin_width), int((b.high - lo_all) / bin_width)
        bc = int((b.close - lo_all) / bin_width)
        tri = []
        for idx in range(b0, b1 + 1):
            tri.append((idx - b0 + 1) / max(bc - b0 + 1, 1) if idx <= bc
                       else (b1 - idx + 1) / max(b1 - bc + 1, 1))
        s = sum(tri)
        for k, idx in enumerate(range(b0, b1 + 1)):
            chips[idx] += b.volume * w * tri[k] / s
    total = sum(chips)
    if total <= 0:
        return None
    centers = [lo_all + (i + 0.5) * bin_width for i in range(nbins)]
    profit = sum(c for c, ctr in zip(chips, centers) if ctr < price) / total * 100
    trap15 = sum(c for c, ctr in zip(chips, centers) if price <= ctr <= price * 1.15) / total * 100
    cum, median_cost = 0.0, centers[-1]
    for c, ctr in zip(chips, centers):
        cum += c
        if cum >= total / 2:
            median_cost = ctr
            break
    return {"profit_ratio_pct": round(profit, 1), "trapped_within_15pct_pct": round(trap15, 1),
            "median_cost": round(median_cost, 2), "current_price": price, "bars_used": n}
