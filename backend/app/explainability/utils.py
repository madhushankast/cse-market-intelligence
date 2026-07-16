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
    e.g. 'sma_20' → 'SMA 20', 'usd_lkr' → 'USD/LKR'
    """
    overrides = {
        "usd_lkr":      "USD/LKR",
        "sma_20":       "SMA 20",
        "sma_50":       "SMA 50",
        "rsi":          "RSI",
        "macd":         "MACD",
        "trend_score":  "Google Trends",
        "daily_return": "Daily Return",
        "interest_rate":"Interest Rate",
        "day_of_week":  "Day of Week",
    }
    return overrides.get(name, name.replace("_", " ").title())
