import pandas as pd
import warnings
from typing import List, Dict, Any


class GrangerCausalityTester:
    """Computes Granger Causality p-values to detect leading indicators."""

    @staticmethod
    def test_causality(df: pd.DataFrame, max_lag: int = 5) -> List[Dict[str, Any]]:
        from statsmodels.tsa.stattools import grangercausalitytests

        exog_vars = ["usd_lkr", "inflation", "trend_score"]
        results = []

        target = "daily_return" if "daily_return" in df.columns else "close"
        if target not in df.columns or len(df) < 15:
            return results

        for var in exog_vars:
            if var not in df.columns:
                continue

            test_df = df[[target, var]].dropna()
            if len(test_df) < 15:
                continue

            # Verify neither column is constant (variance > 0)
            if test_df[target].var() < 1e-8 or test_df[var].var() < 1e-8:
                continue

            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    # statsmodels expects [y, x] where we test if x Granger-causes y
                    test_res = grangercausalitytests(
                        test_df[[target, var]].values,
                        maxlag=max_lag,
                        verbose=False
                    )

                best_lag = 1
                min_p_val = 1.0

                for lag in range(1, max_lag + 1):
                    # Extract the p-value of ssr_chi2test
                    p_val = float(test_res[lag][0]["ssr_chi2test"][1])
                    if p_val < min_p_val:
                        min_p_val = p_val
                        best_lag = lag

                results.append({
                    "variable": var,
                    "target": target,
                    "best_lag": best_lag,
                    "p_value": round(min_p_val, 4),
                    "significant": min_p_val < 0.05,
                    "max_lag_tested": max_lag
                })
            except Exception:
                continue

        return results
