import pandas as pd
import numpy as np
import math
from typing import Dict, Any


class CorrelationAnalyzer:
    """Calculates correlation matrices suitable for Recharts rendering."""

    @staticmethod
    def calculate(df: pd.DataFrame) -> Dict[str, Any]:
        cols = [
            "close", "volume", "daily_return", "rsi", "macd",
            "usd_lkr", "inflation", "interest_rate", "trend_score"
        ]
        available_cols = [c for c in cols if c in df.columns]

        df_numeric = df[available_cols].apply(pd.to_numeric, errors="coerce")
        df_numeric = df_numeric.ffill().bfill().dropna()

        if df_numeric.empty or len(df_numeric) < 5:
            return {"columns": [], "pearson": [], "spearman": []}

        pearson_matrix = df_numeric.corr(method="pearson")
        spearman_matrix = df_numeric.corr(method="spearman")

        pearson_list = []
        spearman_list = []

        for c1 in available_cols:
            for c2 in available_cols:
                pval = pearson_matrix.loc[c1, c2]
                sval = spearman_matrix.loc[c1, c2]

                # Convert NaNs/Infs to None or clean float
                pval_clean = float(pval) if not (math.isnan(pval) or math.isinf(pval)) else 0.0
                sval_clean = float(sval) if not (math.isnan(sval) or math.isinf(sval)) else 0.0

                pearson_list.append({"x": c1, "y": c2, "value": round(pval_clean, 4)})
                spearman_list.append({"x": c1, "y": c2, "value": round(sval_clean, 4)})

        return {
            "columns": available_cols,
            "pearson": pearson_list,
            "spearman": spearman_list
        }
