"""Limit-up pullback analysis: callback (T+1..T+10) and N-shape (T+1..T+8).

Definitions (author's backtests, main-board 10cm first boards only):
  T0 = first limit-up day: today's gain >= 9.5% and yesterday was not a
       limit-up. ChiNext is excluded here on purpose — applying a 9.5%
       threshold to 20cm boards once polluted 36% of signals with fakes.
  A pullback *survives* if no window close/low breaks T0's low.
  Drawdown is measured against T0's close; shallow is better (see
  docs/research-notes.md: <3% group strongly positive, 8-15% negative).
  Entry markers reported, not recommended: first bullish bar in the window
  ("first yang") and any second limit-up day (chasing it backtested worst).
"""
from __future__ import annotations
from .screener import Bar, _pct_changes

def is_first_board(bars: list[Bar], i: int, limit_pct: float = 9.5) -> bool:
    if i <= 0 or i >= len(bars):
        return False
    pct = _pct_changes(bars)
    return pct[i] >= limit_pct and pct[i - 1] < limit_pct

def analyze_pullback(bars: list[Bar], t0: int, window: int = 10):
    """Analyse the pullback after a first board at index t0. None if the
    window is not fully available yet."""
    bars = sorted(bars, key=lambda b: b.date)
    if t0 < 1 or t0 + window >= len(bars):
        return None
    pct = _pct_changes(bars)
    if not is_first_board(bars, t0):
        return None
    t0bar = bars[t0]
    win = bars[t0 + 1: t0 + 1 + window]
    survived = min(b.low for b in win) >= t0bar.low
    min_close_ret = min(b.close / t0bar.close - 1 for b in win)
    drawdown_pct = round(-min_close_ret * 100, 2) if min_close_ret < 0 else 0.0
    first_yang = next((k + 1 for k, b in enumerate(win) if b.close > b.open), None)
    second_board = next((k + 1 for k in range(len(win)) if pct[t0 + 1 + k] >= 9.5), None)
    if drawdown_pct < 3:
        bucket = "<3%"
    elif drawdown_pct < 8:
        bucket = "3-8%"
    elif drawdown_pct <= 15:
        bucket = "8-15%"
    else:
        bucket = ">15%"
    return {"t0_date": t0bar.date, "window": window, "survived": survived,
            "drawdown_pct": drawdown_pct, "drawdown_bucket": bucket,
            "first_yang_offset": first_yang, "second_board_offset": second_board}

def scan_pullbacks(bars: list[Bar], window: int = 10):
    """All completed first-board pullbacks in a bar series."""
    bars = sorted(bars, key=lambda b: b.date)
    out = []
    for i in range(1, len(bars)):
        r = analyze_pullback(bars, i, window)
        if r:
            out.append(r)
    return out
