import sys
import os
import unittest
import pandas as pd
import numpy as np

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.analytics.correlation import CorrelationAnalyzer
from app.analytics.causality import GrangerCausalityTester
from app.analytics.lag import LagAnalyzer


class TestAnalyticsEngine(unittest.TestCase):

    def setUp(self):
        # Create a mock dataset with linear relationships
        dates = pd.date_range(start="2026-01-01", periods=100)
        close = np.linspace(150, 180, 100) + np.random.normal(0, 0.5, 100)
        
        # Google Trends score leads stock price changes by 2 days (idealized lag)
        trend_score = np.linspace(40, 70, 100)
        trend_score[2:] = trend_score[:-2]  # shift trend forward
        
        self.df = pd.DataFrame({
            "date": dates,
            "close": close,
            "volume": np.random.randint(1000, 5000, 100),
            "daily_return": pd.Series(close).pct_change().fillna(0.0),
            "rsi": np.random.uniform(30, 70, 100),
            "usd_lkr": np.linspace(320, 310, 100) + np.random.normal(0, 0.1, 100),
            "inflation": np.random.uniform(4, 5, 100),
            "interest_rate": np.random.uniform(8, 9, 100),
            "trend_score": trend_score
        })

    def test_correlation_analysis(self):
        res = CorrelationAnalyzer.calculate(self.df)
        self.assertIn("columns", res)
        self.assertIn("close", res["columns"])
        self.assertIn("usd_lkr", res["columns"])
        self.assertTrue(len(res["pearson"]) > 0)
        self.assertTrue(len(res["spearman"]) > 0)

    def test_granger_causality(self):
        res = GrangerCausalityTester.test_causality(self.df, max_lag=3)
        self.assertTrue(isinstance(res, list))
        # Checks structure of causality result
        for test in res:
            self.assertIn("variable", test)
            self.assertIn("p_value", test)
            self.assertIn("significant", test)

    def test_lag_analysis(self):
        res = LagAnalyzer.calculate_lag_correlations(self.df, max_lag=5)
        self.assertIn("trend_score", res)
        self.assertIn("usd_lkr", res)
        
        # Verify length is equal to 2 * max_lag + 1
        self.assertEqual(len(res["trend_score"]), 11)
        for pt in res["trend_score"]:
            self.assertIn("lag", pt)
            self.assertIn("correlation", pt)
            self.assertTrue(-1.0 <= pt["correlation"] <= 1.0)


if __name__ == "__main__":
    unittest.main()
