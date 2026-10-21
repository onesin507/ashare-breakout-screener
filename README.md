# ashare-breakout-screener

A-share consolidation-breakout screener — long sideways base, then a
high-volume breakout — plus a washout-end score for limit-up pullbacks.
Pure Python (standard library only), driven by plain CSV daily bars, so
anyone can run, audit and extend it.

**A股长期盘整放量突破选股器**：60 日窄幅盘整后放量突破，外加涨停回调的
洗盘结束评分（S1/S2/S4）。零第三方依赖，输入普通 CSV 日线即可运行，
规则全部写在代码里、可复核。

> Research tooling only — not investment advice, and no return is promised.
> 本项目只是研究工具，不构成投资建议，也不承诺任何收益。

## The rules / 选股规则

Universe: all A-shares **excluding** ST/*ST, the STAR Market (688/689) and
the Beijing Stock Exchange / NEEQ (4/8/920). ChiNext (300/301) stays in.

标的池：全 A，剔除 ST/*ST、科创板、北交所/新三板，创业板保留。

| Step | Rule |
|---|---|
| Consolidation 盘整 | Prior 60 bars (excl. T): (high−low)/low < 20%, and max single-day gain in the window < 9% |
| Breakout 突破 (T day, all) | Close > prior-60-bar high; gain ≥ 6%; volume / prior-20-bar mean volume ≥ 3.0; turnover ≥ 3% |
| Minimum history | ≥ 120 bars |
| Market context 大盘 | CSI 300 vs its 60-day line is shown as **reference only — it never blocks a signal**（只参考、不拦截；弱市时自行给胜率打折） |
| Ranking 排序参考 | Bottom-launch profile: pre-20-day gain < 15% and price still >10% below the 120-day high before breakout; sparse trapped supply overhead is preferred |

### Washout score / 洗盘评分 (0–3)

For a stock pulling back after a first limit-up board, `washout_score()`
awards one point each for: **S1** volume shrinks below 50% of the pre-board
20-day mean and price stops making new lows; **S2** pullback closes never
break the board day's low or MA20; **S4** MA5 never crosses below MA20 in
the window and flattens/turns up at the end. S3 (chip distribution) is
deliberately excluded — this project has no ground-truth chip data.

## Quick start / 快速开始

```bash
python -m unittest discover -s tests -v     # run the tests
python -m ashare_breakout.cli examples/sample_bars.csv
```

CSV columns: `code,name,date,open,close,high,low,volume,pct_chg,turnover`
— one stock after another, at least 120 bars each. The bundled sample is
synthetic and contains exactly one textbook breakout, so the expected
output is one hit.

Library use:

```python
from ashare_breakout import Bar, screen_one, is_eligible, washout_score
hit = screen_one(bars)   # dict on a breakout day, else None
```

## Research notes / 回测笔记（作者研究，样本与局限如实标注）

- **Parameter study (consolidation breakout):** tightening the original
  rules (range 25%→20%, breakout gain 4%→6%, volume ratio 2.5→3.0) raised
  the 20-day win rate in the author's 2021-01 – 2026-09 study from 46.3%
  (814 signals) to 51.6% (221 signals), with out-of-sample (2024 – 2026-09)
  at 53.1%. Sample sizes are modest and results are strongly
  regime-dependent (much weaker in bear years).
- **Washout score:** on 8,603 main-board first-board signals
  (2024-01 – 2026-09), S1+S2+S4 all met → 10-day re-limit rate 55.8% vs
  31.3% baseline (+24.5pp, p<0.0001). The score separates re-limit
  *probability* only; buying on the trigger day showed ≈0 holding return
  in the same study.
- **Fund-flow filter (preliminary, not in the default rules):** on a short
  2026-09-17 – 2026-10-14 window (n=204), pullbacks whose cumulative
  large + extra-large order flow stayed ≥ 0 re-limited within 10 days at
  64.8% vs 40.6% (Fisher p=0.0012). Order-size buckets are a statistical
  convention, not proof of intent — treat flow as a falsification filter
  (rule out persistent distribution), never as proof of accumulation.
  This needs a larger sample before it belongs in the formula.

## Layout / 目录

```
ashare_breakout/   screener.py (rules) · washout.py (S1/S2/S4) · cli.py
examples/          sample_bars.csv (synthetic, 1 textbook breakout)
tests/             unittest suite for the rules and the universe filter
```

## Roadmap / 后续

- Optional public-data fetcher (Tencent/Sina daily bars) behind the same CSV interface
- N-shape and limit-up-pullback screeners, ported from the author's private research scripts
- Larger-sample re-validation of the fund-flow falsification filter

## Maintainer / 维护者

Maintained by [@onesin507](https://github.com/onesin507) — primary maintainer.
Issues and pull requests are welcome; please include the bars (or a generator)
that reproduce any rule dispute.

## License

MIT — see [LICENSE](LICENSE).
