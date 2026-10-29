"""
Baseline Forecasting Benchmarks
-------------------------------
Provides standard financial benchmarks for 30-day cumulative return forecasting:
  1. Naive Persistence Baseline: Predicts zero return (y_hat = 0.0, martingale).
  2. FB Prophet Baseline: Classical time-series trend + seasonality benchmark
     with robust linear-trend fallback if Prophet is not installed.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Tuple, Union
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class NaiveReturnBaseline:
    """
    Level 0 Naive Persistence Baseline.
    Predicts zero return (y_hat = 0.0) across all samples,
    equivalent to assuming a random walk (P_{t+30} approx P_t).
    """

    def __init__(self, mode: str = "zero", lookback_window: int = 60):
        self.mode = mode
        self.lookback_window = lookback_window
        self.daily_drift: float = 0.0

    def fit(self, X: Any = None, y: Optional[pd.Series] = None) -> NaiveReturnBaseline:
        """
        Fits baseline. For zero return baseline, parameters remain 0.0.
        If mode is 'drift' and historical return series y is provided, calculates drift.
        """
        if self.mode == "drift" and y is not None:
            recent = y.dropna().tail(self.lookback_window)
            self.daily_drift = float(recent.mean()) if len(recent) > 0 else 0.0
        else:
            self.daily_drift = 0.0
        return self

    def predict(self, X: Union[pd.DataFrame, np.ndarray, int]) -> np.ndarray:
        """
        Predict forward cumulative return for a test dataset.
        Returns an array of zeros of shape (len(X),) for Level 0 baseline.
        """
        n_samples = X if isinstance(X, int) else len(X)
        if self.mode == "drift":
            return np.full(n_samples, self.daily_drift * 30.0, dtype=float)
        return np.zeros(n_samples, dtype=float)

    def predict_horizon(self, horizon_days: int = 30) -> float:
        """Predict forward return over single horizon."""
        return float(self.daily_drift * horizon_days)


# Alias for backward compatibility
NaiveBaselineModel = NaiveReturnBaseline


class ProphetBaseline:
    """
    Level 1 FB Prophet Baseline Benchmark.
    Fits additive time-series decomposition (trend + seasonality) on historical log prices,
    forecasts forward out to 30 days, and extracts the implied 30-day cumulative return:
        y_hat_t = log(P_{t+30}) - log(P_t)
    Gracefully falls back to robust log-price linear trend if prophet is not installed.
    """

    def __init__(
        self,
        yearly_seasonality: bool = True,
        weekly_seasonality: bool = True,
        daily_seasonality: bool = False,
    ):
        self.yearly_seasonality = yearly_seasonality
        self.weekly_seasonality = weekly_seasonality
        self.daily_seasonality = daily_seasonality
        self.model = None
        self._is_fitted = False
        self._fallback_trend: Optional[Tuple[float, float]] = None
        self._last_hist_log_price: float = 0.0

    def fit(self, df: pd.DataFrame) -> ProphetBaseline:
        """
        Fit Prophet on DataFrame containing ['date', 'close'].
        """
        close_col = "close" if "close" in df.columns else "close_price"
        date_col = "date" if "date" in df.columns else df.columns[0]

        train_df = pd.DataFrame({
            "ds": pd.to_datetime(df[date_col]),
            "y": np.log(df[close_col].astype(float)),
        }).dropna().sort_values("ds").reset_index(drop=True)

        if len(train_df) == 0:
            raise ValueError("No valid training samples available for ProphetBaseline.")

        self._last_hist_log_price = float(train_df["y"].iloc[-1])

        # Attempt to import and fit Prophet
        try:
            from prophet import Prophet
            self.model = Prophet(
                yearly_seasonality=self.yearly_seasonality,
                weekly_seasonality=self.weekly_seasonality,
                daily_seasonality=self.daily_seasonality,
            )
            # Suppress Prophet internal optimizer logs
            import logging as _py_logging
            _py_logging.getLogger("cmdstanpy").setLevel(_py_logging.WARNING)
            self.model.fit(train_df)
            self._is_fitted = True
        except Exception as exc:
            logger.info("Prophet unavailable (%s). Using robust linear log-price trend benchmark.", exc)
            t = np.arange(len(train_df))
            y = train_df["y"].values
            slope, intercept = np.polyfit(t, y, 1)
            self._fallback_trend = (float(slope), float(intercept))
            self.model = None
            self._is_fitted = True

        return self

    def predict(
        self,
        X: Union[pd.DataFrame, np.ndarray, int],
        horizon_days: int = 30,
    ) -> np.ndarray:
        """
        Generate 30-day cumulative return forecasts for test samples.
        """
        if not self._is_fitted:
            raise RuntimeError("ProphetBaseline is not fitted yet.")

        n_samples = X if isinstance(X, int) else len(X)

        if self.model is not None and isinstance(X, pd.DataFrame) and "date" in X.columns:
            try:
                # Forecast 30 days ahead from test dates
                dates = pd.to_datetime(X["date"])
                future_dates = dates + pd.Timedelta(days=horizon_days)

                df_t0 = pd.DataFrame({"ds": dates})
                df_t30 = pd.DataFrame({"ds": future_dates})

                pred_t0 = self.model.predict(df_t0)["yhat"].values
                pred_t30 = self.model.predict(df_t30)["yhat"].values
                return (pred_t30 - pred_t0).astype(float)
            except Exception as exc:
                logger.warning("Prophet dynamic evaluation failed (%s). Falling back to drift.", exc)

        if self._fallback_trend is not None:
            slope, _ = self._fallback_trend
            pred_return = float(slope * horizon_days)
            return np.full(n_samples, pred_return, dtype=float)

        return np.zeros(n_samples, dtype=float)

    def predict_horizon(self, horizon_days: int = 30) -> Dict[str, float]:
        """
        Forecast single forward return and confidence bounds over horizon_days.
        """
        if not self._is_fitted:
            raise RuntimeError("ProphetBaseline is not fitted yet.")

        if self.model is not None:
            future = self.model.make_future_dataframe(periods=horizon_days, freq="B")
            forecast = self.model.predict(future)
            last_hist_idx = len(future) - horizon_days - 1
            last_hist_y = forecast["yhat"].iloc[last_hist_idx]
            future_y = forecast["yhat"].iloc[-1]
            future_y_lower = forecast["yhat_lower"].iloc[-1]
            future_y_upper = forecast["yhat_upper"].iloc[-1]

            return {
                "predicted_log_return": float(future_y - last_hist_y),
                "lower_bound": float(future_y_lower - last_hist_y),
                "upper_bound": float(future_y_upper - last_hist_y),
            }
        else:
            slope, _ = self._fallback_trend if self._fallback_trend else (0.0, 0.0)
            pred_return = float(slope * horizon_days)
            return {
                "predicted_log_return": pred_return,
                "lower_bound": pred_return - 0.08,
                "upper_bound": pred_return + 0.08,
            }


# Alias for backward compatibility
ProphetBaselineModel = ProphetBaseline
