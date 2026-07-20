"""
Utility helpers for the explainability module.
"""

import pandas as pd
from typing import Optional


def safe_feature_value(features: Optional[pd.DataFrame], col: str) -> Optional[float]:
    """
    Safely extract a scalar feature value from a single-row DataFrame.

    Returns None if the column is absent or the value is NaN.
    """
    if features is None or col not in features.columns:
        return None
    val = features[col].iloc[0]
    try:
        f = float(val)
        import math
        return None if math.isnan(f) or math.isinf(f) else f
    except (TypeError, ValueError):
        return None


def top_n_features(
    importances: dict[str, float],
    n: int = 10,
) -> list[tuple[str, float]]:
    """
    Return top-N features sorted by absolute importance descending.
    """
    return sorted(importances.items(), key=lambda x: abs(x[1]), reverse=True)[:n]


def format_feature_name(name: str) -> str:
    """
    Convert snake_case feature names to a human-readable label.
    """
    overrides = {
        "usd_lkr":           "Exchange rate pressure (USD/LKR)",
        "usd_lkr_age":       "Exchange rate release age",
        "inflation":         "Inflation rate",
        "inflation_age":     "Inflation release age",
        "interest_rate":     "Interest rate policy",
        "interest_rate_age": "Interest rate release age",
        "trend_score":       "Investor search interest",
        "trend_score_age":   "Search interest release age",
        "trend_lag_1":       "Investor search interest (1-day lag)",
        "trend_lag_3":       "Investor search interest (3-day lag)",
        "trend_lag_5":       "Investor search interest (5-day lag)",
        "trend_lag_7":       "Investor search interest (7-day lag)",
        "sma_20":            "20-day price momentum",
        "sma_50":            "50-day price momentum",
        "rsi":               "Market momentum indicator (RSI)",
        "macd":              "MACD trend oscillator",
        "volatility":        "Price volatility",
        "daily_return":      "Previous daily return",
        "volume":            "Trading volume",
        "day_of_week":       "Day of the week effect",
        "month":             "Monthly calendar effect"
    }
    return overrides.get(name, name.replace("_", " ").title())
