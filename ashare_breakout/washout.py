"""Washout-end scoring for limit-up pullbacks: 0-3 points (S1 / S2 / S4).

Backtest (author, 2026-10-17; Sina daily bars, 8,603 main-board first-board
signals, 2024-01 to 2026-09, window T+1..T+5):
  S1 & S2 & S4 all met -> 10-day re-limit rate 55.8% vs 31.3% baseline
  (+24.5pp, z=9.86, p<0.0001); S1 had the largest marginal contribution.
The score separates *re-limit probability only*; it is not a buy signal and
says nothing about holding returns. S3 (chip distribution) is excluded:
no ground-truth chip data is available in this project.
"""
from __future__ import annotations

def _ma(values, i, k):
    return sum(values[i-k+1:i+1]) / k if i - k + 1 >= 0 else None

def washout_score(bars, t0_index: int, window_indices: list[int]):
    """bars: sequence of (date, open, high, low, close, volume), ascending.
    Returns (score 0-3, detail like 'S1S4') or (None, None) if data is short.
      S1 volume shrinks to an extreme and price stops making new lows
      S2 pullback closes never break T0 low or MA20
      S4 MA5 never crosses below MA20 in the window and flattens/turns up
    """
    if t0_index < 20 or len(window_indices) < 3:
        return None, None
    C = [r[4] for r in bars]; L = [r[3] for r in bars]; V = [r[5] for r in bars]
    pre_vol = sum(V[t0_index-20:t0_index]) / 20
    if pre_vol <= 0:
        return None, None
    prev_week_low = min(L[t0_index-7:t0_index])
    s1 = (min(V[i] for i in window_indices) < 0.5 * pre_vol
          and C[window_indices[-1]] >= prev_week_low and C[window_indices[-2]] >= prev_week_low)
    ma20_last = _ma(C, window_indices[-1], 20)
    s2 = (min(C[i] for i in window_indices) >= bars[t0_index][3]
          and ma20_last is not None and min(C[i] for i in window_indices) >= ma20_last)
    s4 = True
    for i in window_indices:
        a, b = _ma(C, i, 5), _ma(C, i, 20)
        if a is None or b is None or a < b:
            s4 = False; break
    if s4:
        s4 = (_ma(C, window_indices[-1], 5) >= _ma(C, window_indices[-3], 5)
              and ma20_last is not None and C[window_indices[-1]] >= ma20_last)
    detail = "".join(x for x, f in (("S1", s1), ("S2", s2), ("S4", s4)) if f) or "-"
    return int(s1) + int(s2) + int(s4), detail
