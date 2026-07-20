import pandas as pd
import math
from typing import Dict, List, Any


class LagAnalyzer:
    """Computes cross-correlation between exogenous features and stock price returns."""

    @staticmethod
    def calculate_lag_correlations(df: pd.DataFrame, max_lag: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        results = {}
        exog_vars = ["usd_lkr", "inflation", "trend_score"]
        target = "daily_return" if "daily_return" in df.columns else "close"

        if target not in df.columns or df[target].var() < 1e-8:
            return results

        for var in exog_vars:
            if var not in df.columns or df[var].var() < 1e-8:
                continue

            var_lags = []
            for lag in range(-max_lag, max_lag + 1):
                try:
                    # Positive lag: exogenous variable today correlates with stock target in `lag` days
                    # Shift target backwards by lag to align past macro with future target
                    corr = float(df[var].corr(df[target].shift(-lag)))
                    corr_clean = corr if not (math.isnan(corr) or math.isinf(corr)) else 0.0
                    var_lags.append({
                        "lag": lag,
                        "correlation": round(corr_clean, 4)
                    })
                except Exception:
                    var_lags.append({
                        "lag": lag,
                        "correlation": 0.0
                    })
            results[var] = var_lags

        return results
