"""Consolidation-breakout screening rules (high-win-rate variant).

Universe (author's standing rule): all A-shares excluding ST/*ST, the STAR
Market (688/689), the Beijing Stock Exchange and NEEQ (4/8/920 prefixes).
ChiNext (300/301) stays IN.

Rules on daily bars, T = last bar:
  1. Consolidation: (max high - min low) / min low over the prior 60 bars
     (excluding T) < 20%, and the largest single-day gain in that window < 9%.
  2. Breakout on T (all must hold):
       close > prior-60-bar high
       daily gain >= 6%
       volume ratio (T volume / prior-20-bar mean volume) >= 3.0
       turnover >= 3%
  3. Market context (CSI 300 vs its 60-day line) is *reference only* and
     never blocks a signal. See `market_reference()`.

Ranking helper: `bottom_start_check()` flags the textbook bottom-launch
profile (pre-20-day gain < 15% and close still >10% below the 120-day high
before the breakout), modelled on the author's reference case.

This is research tooling, not investment advice.
"""
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Bar:
    date: str
    open: float
    close: float
    high: float
    low: float
    volume: float
    pct_chg: float | None = None   # %; computed from closes if omitted
    turnover: float | None = None  # %

@dataclass
class ScreenerConfig:
    consolidation_days: int = 60
    max_range_pct: float = 0.20
    max_prior_gain_pct: float = 9.0
    min_breakout_gain_pct: float = 6.0
    volume_window: int = 20
    min_volume_ratio: float = 3.0
    min_turnover_pct: float = 3.0
    min_bars: int = 120

def is_eligible(code: str, name: str = "") -> bool:
    """Universe filter described in the module docstring."""
    c = str(code).strip().zfill(6)[-6:]
    if "ST" in (name or "").upper():
        return False
    if c.startswith(("688", "689")):   # STAR Market
        return False
    if c[0] in ("4", "8") or c.startswith("920"):  # BSE / NEEQ
        return False
    return True

def _pct_changes(bars):
    out = []
    for i, b in enumerate(bars):
        if b.pct_chg is not None:
            out.append(float(b.pct_chg))
        elif i and bars[i-1].close:
            out.append((b.close / bars[i-1].close - 1) * 100)
        else:
            out.append(0.0)
    return out

def screen_one(bars: list[Bar], cfg: ScreenerConfig = ScreenerConfig()):
    """Return a hit dict if the last bar is a breakout signal, else None."""
    bars = sorted(bars, key=lambda b: b.date)
    if len(bars) < cfg.min_bars:
        return None
    pct = _pct_changes(bars)
    t = bars[-1]
    prior = bars[-1 - cfg.consolidation_days:-1]
    if len(prior) < cfg.consolidation_days:
        return None
    hi60, lo60 = max(b.high for b in prior), min(b.low for b in prior)
    if lo60 <= 0:
        return None
    rng = (hi60 - lo60) / lo60
    if rng >= cfg.max_range_pct:
        return None
    prior_pct = pct[-1 - cfg.consolidation_days:-1]
    if prior_pct and max(prior_pct) >= cfg.max_prior_gain_pct:
        return None
    if not t.close > hi60:
        return None
    if pct[-1] < cfg.min_breakout_gain_pct:
        return None
    prior_vol = bars[-1 - cfg.volume_window:-1]
    ma_vol = sum(b.volume for b in prior_vol) / len(prior_vol)
    if ma_vol <= 0:
        return None
    vol_ratio = t.volume / ma_vol
    if vol_ratio < cfg.min_volume_ratio:
        return None
    if t.turnover is not None and t.turnover < cfg.min_turnover_pct:
        return None
    return {
        "date": t.date, "close": round(t.close, 2),
        "gain_pct": round(pct[-1], 2), "volume_ratio": round(vol_ratio, 2),
        "turnover_pct": t.turnover,
        "range_60d_pct": round(rng * 100, 2),
        "bottom_start": bottom_start_check(bars),
    }

def bottom_start_check(bars: list[Bar]):
    """(pre20_gain_pct, distance_to_120d_high_pct, passed) or None."""
    bars = sorted(bars, key=lambda b: b.date)
    if len(bars) < 140:
        return None
    c_t = bars[-1].close
    pre20 = (c_t / bars[-22].close - 1) * 100
    hhv120 = max(b.high for b in bars[-121:-1])
    dist = (hhv120 - c_t) / hhv120 * 100 if hhv120 > 0 else 0.0
    return {"pre20_gain_pct": round(pre20, 1), "dist_to_120d_high_pct": round(dist, 1),
            "passed": bool(pre20 < 15 and dist > 10)}

def market_reference(index_closes: list[float]):
    """CSI 300 vs 60-day MA: display-only context, never a filter."""
    if len(index_closes) < 60:
        return None
    ma60 = sum(index_closes[-60:]) / 60
    last = index_closes[-1]
    return {"close": last, "ma60": round(ma60, 2), "above_ma60": last > ma60,
            "note": "strong-market reference" if last > ma60 else "weak-market reference: discount breakout win rate"}
