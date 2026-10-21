import unittest
from ashare_breakout import Bar
from ashare_breakout.pullback import analyze_pullback, scan_pullbacks
from ashare_breakout.chips import estimate_chips
from ashare_breakout.first_board import is_first_board, promoted
from ashare_breakout.fetch_tencent import parse_fqkline

def series(closes, vols=None):
    import datetime
    d0 = datetime.date(2025, 1, 1)
    bars, prev = [], None
    for i, c in enumerate(closes):
        pct = round((c / prev - 1) * 100, 2) if prev else 0.0
        bars.append(Bar(date=str(d0 + datetime.timedelta(days=i)), open=c,
                        close=c, high=c * 1.005, low=c * 0.995,
                        volume=(vols[i] if vols else 1000), pct_chg=pct, turnover=2.0))
        prev = c
    return bars

class TestPullback(unittest.TestCase):
    def test_surviving_shallow_pullback(self):
        closes = [10.0] * 5 + [11.0] + [10.8, 10.7, 10.75, 10.8, 10.85, 10.9, 10.95, 11.0, 11.05, 11.1]
        bars = series(closes)
        bars[5] = Bar(date=bars[5].date, open=10.2, close=11.0, high=11.0, low=10.1, volume=3000, pct_chg=10.0, turnover=6.0)
        r = analyze_pullback(bars, 5, window=8)
        self.assertIsNotNone(r)
        self.assertTrue(r["survived"])
        self.assertEqual(r["drawdown_bucket"], "<3%")
    def test_first_board_and_promotion(self):
        self.assertTrue(is_first_board(9.9, 2.0, "600000"))
        self.assertFalse(is_first_board(9.9, 10.1, "600000"))
        self.assertTrue(is_first_board(19.8, 5.0, "300001"))
        self.assertTrue(promoted(10.0, "600000"))
        self.assertFalse(promoted(5.0, "600000"))
        self.assertTrue(promoted(19.8, "300001"))

class TestChips(unittest.TestCase):
    def test_chips_runs(self):
        bars = series([10.0 + (i % 7) * 0.05 for i in range(120)])
        est = estimate_chips(bars)
        self.assertIsNotNone(est)
        self.assertIn("profit_ratio_pct", est)

class TestFetchParser(unittest.TestCase):
    def test_parse(self):
        payload = {"data": {"sz000001": {"qfqday": [["2025-01-01", "10.0", "10.0", "10.1", "9.9", "1000"],
                                                     ["2025-01-02", "10.0", "11.0", "11.0", "10.0", "2000"]]}}}
        rows = parse_fqkline(payload, "000001")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1]["pct_chg"], 10.0)

if __name__ == "__main__":
    unittest.main()
