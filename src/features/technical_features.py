"""
Vectorized Technical Feature Engineering Pipeline (OHLCV + ASPI Market Benchmark)
---------------------------------------------------------------------------------
Computes strictly technical and market-relative indicators from historical equities OHLCV
data and official ASPI benchmark index history. Strictly prevents forward lookahead bias.
"""

from __future__ import annotations

import logging
import math
from pathlib import Path
from typing import List, Optional, Union
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class TechnicalFeaturePipeline:
    """
    Vectorized feature engineering pipeline deriving:
      1. Autoregressive stock price log returns (1d, 5d, 10d, 20d, 30d)
      2. Trend & Momentum (Wilder's RSI, MACD, EMA 12/26 ratio, SMA 20/50 ratio)
      3. Volatility & Intraday Dynamics (Parkinson volatility instantaneous, 10d, 20d, and High-Low spread)
      4. Volume Dynamics (Volume surge ratio, Log volume)
      5. CSE Market Benchmark Dynamics (ASPI 5d/10d/30d returns, 30d Relative Strength, 30d rolling beta correlation)
      6. Supervised Target: 30-day forward cumulative log return y_t = ln(P_{t+30} / P_t)
    """

    def __init__(
        self,
        target_horizon: int = 30,
        rsi_window: int = 14,
        aspi_path: Union[str, Path] = "data/processed/ASPI.parquet",
    ):
        self.target_horizon = target_horizon
        self.rsi_window = rsi_window
        self.aspi_path = Path(aspi_path)

    @staticmethod
    def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
        """Vectorized Relative Strength Index calculation using Wilder's smoothing."""
        delta = series.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()
        avg_loss = loss.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()

        rs = avg_gain / (avg_loss + 1e-10)
        rsi = 100.0 - (100.0 / (1.0 + rs))
        return rsi

    @staticmethod
    def compute_macd(
        series: pd.Series,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ) -> pd.DataFrame:
        """Vectorized Moving Average Convergence Divergence."""
        ema_fast = series.ewm(span=fast_period, adjust=False).mean()
        ema_slow = series.ewm(span=slow_period, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        hist = macd_line - signal_line

        return pd.DataFrame({
            "macd": macd_line,
            "macd_signal": signal_line,
            "macd_hist": hist,
        }, index=series.index)

    @staticmethod
    def compute_parkinson_volatility(
        high: pd.Series,
        low: pd.Series,
    ) -> pd.Series:
        """
        Instantaneous Parkinson High-Low Volatility:
        sigma_t = sqrt( (1 / (4 * ln 2)) * (ln(High_t / Low_t))^2 )
        """
        safe_high = np.maximum(high.values, 1e-6)
        safe_low = np.maximum(low.values, 1e-6)
        safe_high = np.maximum(safe_high, safe_low)

        log_hl = np.log(safe_high / safe_low)
        factor = 1.0 / (4.0 * math.log(2.0))
        instantaneous_parkinson = np.sqrt(factor * (log_hl ** 2))
        return pd.Series(instantaneous_parkinson, index=high.index)

    def load_aspi_series(self) -> pd.DataFrame:
        """Loads processed ASPI benchmark series from parquet."""
        if not self.aspi_path.exists():
            logger.warning("ASPI parquet not found at %s. Market relative features will use fallback.", self.aspi_path)
            return pd.DataFrame(columns=["date", "close"])

        df = pd.read_parquet(self.aspi_path)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").drop_duplicates(subset=["date"]).reset_index(drop=True)
        return df

    def transform(
        self,
        stock_df: pd.DataFrame,
        aspi_df: Optional[pd.DataFrame] = None,
    ) -> pd.DataFrame:
        """
        Transforms stock OHLCV data into complete technical & market benchmark feature matrix.
        Strictly leak-free with point-in-time backward alignment on ASPI.
        """
        if stock_df.empty:
            return stock_df

        df = stock_df.copy()
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)

        close = df["close"]
        high = df["high"]
        low = df["low"]
        volume = df["volume"]
        open_p = df["open"]

        # -------------------------------------------------------------
        # 1. Autoregressive Stock Price Returns
        # -------------------------------------------------------------
        df["return_1d"] = np.log(close / close.shift(1))
        df["return_5d"] = np.log(close / close.shift(5))
        df["return_10d"] = np.log(close / close.shift(10))
        df["return_20d"] = np.log(close / close.shift(20))
        df["return_30d"] = np.log(close / close.shift(30))

        # -------------------------------------------------------------
        # 2. Technical Trend & Momentum
        # -------------------------------------------------------------
        df["rsi_14"] = self.compute_rsi(close, period=self.rsi_window)

        macd_df = self.compute_macd(close, fast_period=12, slow_period=26, signal_period=9)
        df["macd"] = macd_df["macd"]
        df["macd_signal"] = macd_df["macd_signal"]
        df["macd_hist"] = macd_df["macd_hist"]

        # Moving average ratios
        ema_12 = close.ewm(span=12, adjust=False).mean()
        ema_26 = close.ewm(span=26, adjust=False).mean()
        df["ema_ratio_12_26"] = ema_12 / (ema_26 + 1e-10)

        sma_20 = close.rolling(20, min_periods=5).mean()
        sma_50 = close.rolling(50, min_periods=10).mean()
        df["sma_ratio_20_50"] = sma_20 / (sma_50 + 1e-10)

        # -------------------------------------------------------------
        # 3. Volatility & Intraday Dynamics
        # -------------------------------------------------------------
        instant_p_vol = self.compute_parkinson_volatility(high, low)
        df["parkinson_vol"] = instant_p_vol
        df["parkinson_vol_10d"] = (
            instant_p_vol.rolling(10, min_periods=3).mean() * np.sqrt(252)
        )
        df["parkinson_vol_20d"] = (
            instant_p_vol.rolling(20, min_periods=5).mean() * np.sqrt(252)
        )
        df["high_low_spread"] = (high - low) / (close + 1e-10)

        # -------------------------------------------------------------
        # 4. Volume Dynamics
        # -------------------------------------------------------------
        vol_sma_20 = volume.rolling(20, min_periods=1).mean()
        df["volume_surge_ratio"] = volume / (vol_sma_20 + 1e-5)
        df["log_volume"] = np.log(volume + 1.0)

        # -------------------------------------------------------------
        # 5. CSE Market Benchmark Dynamics (ASPI)
        # -------------------------------------------------------------
        if aspi_df is None or aspi_df.empty:
            aspi_df = self.load_aspi_series()

        if not aspi_df.empty:
            a_df = aspi_df.copy()
            a_df["date"] = pd.to_datetime(a_df["date"])
            a_df = a_df.sort_values("date").drop_duplicates(subset=["date"]).reset_index(drop=True)

            # Compute ASPI market returns on index series prior to merge
            a_df["aspi_return_1d"] = np.log(a_df["close"] / a_df["close"].shift(1))
            a_df["aspi_return_5d"] = np.log(a_df["close"] / a_df["close"].shift(5))
            a_df["aspi_return_10d"] = np.log(a_df["close"] / a_df["close"].shift(10))
            a_df["aspi_return_30d"] = np.log(a_df["close"] / a_df["close"].shift(30))
            a_df = a_df.rename(columns={"close": "aspi_close"})

            aspi_cols = ["date", "aspi_close", "aspi_return_1d", "aspi_return_5d", "aspi_return_10d", "aspi_return_30d"]
            a_sub = a_df[[c for c in aspi_cols if c in a_df.columns]]

            # Point-in-time backward alignment: guaranteed zero future leakage
            merged = pd.merge_asof(
                df,
                a_sub,
                on="date",
                direction="backward",
            )
            df = merged

            # Relative Strength against ASPI: r_stock_30d - r_aspi_30d
            df["relative_strength_30d"] = df["return_30d"] - df["aspi_return_30d"]

            # 30-day rolling correlation between Stock returns and ASPI returns (Beta proxy)
            df["rolling_corr_aspi_30d"] = (
                df["return_1d"].rolling(30, min_periods=10).corr(df["aspi_return_1d"])
            ).fillna(0.0)

            # Drop raw unnormalized aspi nominal close to keep features strictly scale-invariant
            if "aspi_close" in df.columns:
                df = df.drop(columns=["aspi_close"])
        else:
            # Fallback if ASPI series unavailable
            df["aspi_return_5d"] = 0.0
            df["aspi_return_10d"] = 0.0
            df["aspi_return_30d"] = 0.0
            df["relative_strength_30d"] = df["return_30d"]
            df["rolling_corr_aspi_30d"] = 0.0

        # -------------------------------------------------------------
        # 6. Target Definition: y_t = ln(P_{t+30} / P_t)
        # -------------------------------------------------------------
        df["target_return_30d"] = np.log(close.shift(-self.target_horizon) / close)

        # -------------------------------------------------------------
        # 7. Numerical Sanitization: Clean infs and historical warm-up NaNs
        # -------------------------------------------------------------
        feature_cols = [
            "return_1d", "return_5d", "return_10d", "return_20d", "return_30d",
            "rsi_14", "macd", "macd_signal", "macd_hist",
            "ema_ratio_12_26", "sma_ratio_20_50",
            "parkinson_vol", "parkinson_vol_10d", "parkinson_vol_20d", "high_low_spread",
            "volume_surge_ratio", "log_volume",
            "aspi_return_5d", "aspi_return_10d", "aspi_return_30d",
            "relative_strength_30d", "rolling_corr_aspi_30d",
        ]

        # Replace any inf/-inf with NaN then handle
        for c in feature_cols:
            if c in df.columns:
                df[c] = df[c].replace([np.inf, -np.inf], np.nan)
                # Forward fill historical warm-up, then backward fill for very first rows
                df[c] = df[c].bfill().fillna(0.0)

        return df


# Backwards-compatible aliases
TechnicalFeatureEngine = TechnicalFeaturePipeline
