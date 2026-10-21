import unittest
from ashare_breakout import Bar, screen_one, is_eligible, washout_score

def flat_bars(n=130, price=10.0, vol=1_000_000):
    import datetime
    d0 = datetime.date(2025, 1, 1)
    return [Bar(date=str(d0 + datetime.timedelta(days=i)), open=price, close=price,
                high=price*1.01, low=price*0.99, volume=vol, pct_chg=0.0, turnover=1.0)
            for i in range(n)]

class TestScreener(unittest.TestCase):
    def test_breakout_hit(self):
        bars = flat_bars()
        bars.append(Bar(date="2025-06-10", open=10.0, close=10.8, high=10.9, low=9.95,
                        volume=3_500_000, pct_chg=8.0, turnover=5.0))
        self.assertIsNotNone(screen_one(bars))
    def test_no_breakout_on_flat_day(self):
        bars = flat_bars()
        bars.append(Bar(date="2025-06-10", open=10.0, close=10.05, high=10.1, low=9.95,
                        volume=1_000_000, pct_chg=0.5, turnover=1.2))
        self.assertIsNone(screen_one(bars))
    def test_universe(self):
        self.assertFalse(is_eligible("688001", "Example"))
        self.assertFalse(is_eligible("830001", "Example"))
        self.assertFalse(is_eligible("000001", "*ST Example"))
        self.assertTrue(is_eligible("300001", "Example"))   # ChiNext stays in
        self.assertTrue(is_eligible("002962", "Example"))
    def test_washout_short_window(self):
        bars = [(f"d{i}", 10, 10.1, 9.9, 10, 100) for i in range(30)]
        self.assertEqual(washout_score(bars, 25, [26, 27]), (None, None))

if __name__ == "__main__":
    unittest.main()
