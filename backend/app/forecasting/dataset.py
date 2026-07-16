"""
ForecastDataset — builds the ML feature matrix (X) and target (y) from
the integrated stock + macro + trends DataFrame produced by the existing
preprocessing and data-merger pipeline.

Target:
    y[t] = close[t+1]  (next-day close price)

Features:
    - Raw OHLCV from CSE
    - Technical indicators from IndicatorBuilder (RSI, MACD, SMA, volatility)
    - Macroeconomic indicators from CBSL (USD/LKR, inflation, interest_rate)
    - Search interest from Google Trends (trend_score)
    - Calendar features (day_of_week, month)
"""

import pandas as pd
import numpy as np
from typing import Tuple


# Columns required for the full feature set — any missing are silently dropped
# so the dataset works even when macro/trends data is partially unavailable.
FEATURE_COLUMNS = [
    # Price
    "open", "high", "low", "close", "volume",
    # Technical indicators (produced by IndicatorBuilder)
    "daily_return", "rsi", "macd", "sma_20", "sma_50", "volatility",
    # Macro (CBSL)
    "usd_lkr", "inflation", "interest_rate",
    # Alternative (Google Trends)
    "trend_score",
    # Calendar
    "day_of_week", "month",
]

# Minimum rows needed to train meaningful models
MIN_ROWS = 50


class ForecastDataset:
    """
    Transforms a merged DataFrame into a supervised ML dataset.

    Usage:
        ds = ForecastDataset(df_merged)
        X_train, X_test, y_train, y_test = ds.split(test_size=0.2)
        feature_names = ds.feature_names
    """

    def __init__(self, df: pd.DataFrame):
        """
        Args:
            df: Merged DataFrame containing stock + macro + trends columns,
                as produced by DataMerger.merge() followed by
                ProcessingPipeline.process().
        """
        self._raw = df.copy()
        self._df: pd.DataFrame = pd.DataFrame()
        self._feature_names: list[str] = []
        self._build()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @property
    def df(self) -> pd.DataFrame:
        """Prepared dataset with features + target column."""
        return self._df

    @property
    def feature_names(self) -> list[str]:
        """Names of all feature columns (i.e. everything except 'target')."""
        return self._feature_names

    @property
    def n_rows(self) -> int:
        return len(self._df)

    def split(self, test_size: float = 0.2) -> Tuple[
        pd.DataFrame, pd.DataFrame, pd.Series, pd.Series
    ]:
        """
        Time-aware train/test split (no shuffle — keeps chronological order).

        Returns:
            X_train, X_test, y_train, y_test
        """
        if self.n_rows < MIN_ROWS:
            raise ValueError(
                f"Dataset has only {self.n_rows} usable rows; "
                f"need at least {MIN_ROWS} to train."
            )

        split_idx = int(len(self._df) * (1 - test_size))
        train = self._df.iloc[:split_idx]
        test  = self._df.iloc[split_idx:]

        X_train = train[self._feature_names]
        X_test  = test[self._feature_names]
        y_train = train["target"]
        y_test  = test["target"]

        return X_train, X_test, y_train, y_test

    def get_last_row(self) -> pd.DataFrame:
        """Returns the most recent feature row for one-step-ahead prediction."""
        return self._df[self._feature_names].iloc[[-1]]

    def get_close_series(self) -> pd.Series:
        """The raw close price series (for SARIMAX endogenous input)."""
        return self._df["close"]

    def get_exog(self) -> pd.DataFrame:
        """Exogenous columns for SARIMAX."""
        exog_cols = [c for c in ["usd_lkr", "inflation", "trend_score"] if c in self._df.columns]
        return self._df[exog_cols] if exog_cols else pd.DataFrame()

    # ------------------------------------------------------------------
    # Private: build the feature matrix
    # ------------------------------------------------------------------

    def _build(self) -> None:
        df = self._raw.copy()

        # Ensure date is sorted ascending
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date").reset_index(drop=True)

        # Engineer calendar features
        if "date" in df.columns:
            df["day_of_week"] = df["date"].dt.dayofweek
            df["month"] = df["date"].dt.month

        # Target: next-day close (shift close up by 1)
        df["target"] = df["close"].shift(-1)

        # Drop the last row (no target available)
        df = df.dropna(subset=["target"])

        # Identify which feature columns are actually present
        available = [c for c in FEATURE_COLUMNS if c in df.columns]
        self._feature_names = available

        # Drop rows where any feature or target is NaN
        # (happens naturally at the start due to rolling indicators)
        df = df[available + ["target", "date"] if "date" in df.columns else available + ["target"]]
        df = df.dropna().reset_index(drop=True)

        self._df = df
