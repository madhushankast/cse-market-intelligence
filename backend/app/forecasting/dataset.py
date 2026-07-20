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


# Columns required for the full feature set
FEATURE_COLUMNS = [
    # Price
    "open", "high", "low", "close", "volume",
    # Technical indicators
    "daily_return", "log_return", "high_low_pct", "open_close_pct",
    "sma_10", "sma_20", "sma_50", "ema_20", "ema_50",
    "rsi", "macd", "macd_signal", "roc",
    "upper_bb", "middle_bb", "lower_bb", "atr",
    "obv", "volume_ma", "volatility",
    # Lag features
    "lag_1", "lag_2", "lag_3", "lag_5", "lag_10", "lag_20",
    # Rolling features
    "rolling_mean", "rolling_std",
    # Calendar
    "day_of_week", "month",
]

# Minimum rows needed to train meaningful models
MIN_ROWS = 50


class ForecastDataset:
    """
    Transforms a stock DataFrame into a supervised ML dataset.
    """

    def __init__(self, df: pd.DataFrame):
        self._raw = df.copy()
        self._df: pd.DataFrame = pd.DataFrame()
        self._full_df: pd.DataFrame = pd.DataFrame()
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
        """Returns the most recent feature row for prediction."""
        cols = self._feature_names
        return self._full_df[cols].ffill().bfill().iloc[[-1]]

    def get_close_series(self) -> pd.Series:
        """The raw close price series (for SARIMAX endogenous input)."""
        return self._df["close"]

    def get_exog(self) -> pd.DataFrame:
        """Exogenous columns for SARIMAX (technical indicators)."""
        exog_cols = [c for c in self._feature_names if c not in ("close", "open", "high", "low", "volume", "day_of_week", "month")]
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

        # Generate lag features for close price
        for lag in [1, 2, 3, 5, 10, 20]:
            df[f"lag_{lag}"] = df["close"].shift(lag)

        # Generate rolling statistics for close price
        df["rolling_mean"] = df["close"].rolling(20).mean()
        df["rolling_std"] = df["close"].rolling(20).std()

        # Target: Close price after 30 trading days
        df["target"] = df["close"].shift(-30)

        # Identify which feature columns are actually present
        available = [c for c in FEATURE_COLUMNS if c in df.columns]
        self._feature_names = available

        self._full_df = df.copy()
        
        # Drop rows where any feature or target is NaN for model training
        df_clean = df.dropna(subset=available + ["target"]).reset_index(drop=True)
        self._df = df_clean

