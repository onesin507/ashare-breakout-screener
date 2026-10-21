"""First-board identification and next-day promotion helpers.

Board-aware limit thresholds: main board 9.5%, ChiNext (300/301) 19.5%,
STAR/BSE are outside this project's universe. A *first board* is a limit-up
day whose previous day was not a limit-up. *Promotion* = the next trading
day is also a limit-up.

Author's study (20,973 first boards since 2024-01, daily-bar reconstruction):
base promotion rate 16.53%, and turnover showed no predictive power across
buckets (all ~16-17.6%) — see docs/research-notes.md. Seal time / seal size /
intraday break counts cannot be reconstructed from daily bars and the
exchange limit-up pool only retains ~2 days of history, so those factors are
reference-only in the author's intraday workflow.
"""
from __future__ import annotations

def limit_threshold_pct(code: str) -> float:
    c = str(code).strip().zfill(6)[-6:]
    return 19.5 if c.startswith(("300", "301")) else 9.5

def is_limit_up(pct_chg: float, code: str) -> bool:
    return pct_chg >= limit_threshold_pct(code)

def is_first_board(pct_today: float, pct_yesterday: float, code: str) -> bool:
    return is_limit_up(pct_today, code) and not is_limit_up(pct_yesterday, code)

def promoted(pct_next_day: float, code: str) -> bool:
    return is_limit_up(pct_next_day, code)
