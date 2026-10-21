# Research notes (author's backtests, aggregate results only)

All studies: full A-share universe excluding ST/*ST, STAR Market, BSE/NEEQ
(ChiNext included unless a study says main-board only). Daily bars, no fees.
These are historical studies by the maintainer, not guarantees; sample
windows and known limitations are stated with each result.

## Consolidation breakout — parameter study
See the README: tightening range 25%->20%, breakout gain 4%->6% and volume
ratio 2.5->3.0 lifted the 20-day win rate from 46.3% (814 signals) to 51.6%
(221 signals) over 2021-01 – 2026-09, out-of-sample 53.1%. Regime-dependent.

## Limit-up pullback (callback v2; main-board 10cm first boards)
8,603 non-overlapping signals, 2024-01 – 2026-09. Entry timing, 20-day
holding: A (buy T+2 close) win rate 53.26%, mean +4.54%; D (first bullish
bar's close) 52.4% / +4.54% with the best 5-day payoff ratio (1.94).
Methodology note: v1 of this study misread ChiNext 9.5–19% days as 10cm
first boards (36% fake signals); v2 excludes ChiNext entirely.
`pullback.py` implements the pattern side of this study.

## N-shape (classic)
First board, pullback T+1..T+8 that never breaks T0's low. Shallow
pullbacks dominate: the <3% drawdown group, bought at the first bullish
bar, returned a 56.63% 20-day win rate / +6.50% mean (n=5,829); the 8–15%
group was negative (-4.87% mean). Chasing the second limit-up day was the
worst entry of all five tested (~43.5% win rate) — the pattern's edge, such
as it is, sits in the pullback, not in chasing the second board.

## First-board quality factors
20,973 first boards since 2024-01 (daily-bar reconstruction): next-day
promotion rate 16.53%. Turnover had *no* predictive power (every bucket
~16–17.6%), so this project ignores turnover for first boards. Seal time,
seal size and intraday break counts cannot be backtested — the exchange
limit-up pool only retains about two days of history — so the author's
intraday workflow treats them as reference-only. `first_board.py` holds
the identification/promotion logic.

## Washout score (S1/S2/S4)
8,603 main-board first-board signals, 2024-01 – 2026-09: all three signals
met -> 10-day re-limit rate 55.8% vs 31.3% baseline (p<0.0001). It separates
re-limit probability only; holding returns after the trigger were ~0.
Implemented in `washout.py`.

## Fund-flow falsification filter (preliminary, not a default rule)
Short window 2026-09-17 – 2026-10-14 (n=204): pullbacks whose cumulative
large + extra-large order flow stayed >= 0 re-limited within 10 days at
64.8% vs 40.6% (Fisher p=0.0012). Order-size buckets are a statistical
convention, not a read on intent: flow is used only to *rule out* persistent
distribution, never to prove accumulation. The underlying intraday fund-flow
dataset is not public, so this study is documented here but not shipped as
code; it needs a larger sample before it could become a rule.
