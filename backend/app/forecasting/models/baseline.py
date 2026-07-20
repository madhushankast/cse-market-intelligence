"""
Baseline (Naïve Persistence) Model.

The simplest possible forecast: tomorrow's price = today's price.
Every research project should benchmark against this — if a complex model
cannot beat the naïve baseline, it is not adding value.

MAPE of ~1–3% is typical for liquid stocks with low day-to-day volatility.
"""

import numpy as np
import pandas as pd
from typing import Optional
from app.forecasting.base import ForecastModel, EvaluationResult
from app.forecasting.evaluator import ModelEvaluator


class BaselineModel(ForecastModel):
    """
    Baseline moving average model: predicts Close(t+30) will be equal to the
    current 20-day rolling moving average of the close price.
    """

    name = "baseline"

    def __init__(self):
        self._last_close = 0.0
        self._ma_pred = 0.0

    # ------------------------------------------------------------------
    def train(self, train_df: pd.DataFrame) -> None:
        """Store the moving average from the end of training set."""
        self._last_close = float(train_df["close"].iloc[-1])
        # Compute 20-day simple moving average
        sma_series = train_df["close"].rolling(20).mean()
        self._ma_pred = float(sma_series.iloc[-1]) if len(train_df) >= 20 else self._last_close

    # ------------------------------------------------------------------
    def predict(
        self,
        horizon: int = 30,
        latest_row: Optional[pd.DataFrame] = None,
        latest_close: Optional[float] = None,
        full_df: Optional[pd.DataFrame] = None,
        technical_score: Optional[float] = None,
        technical_confidence: Optional[float] = None,
    ) -> list[float]:
        """Project price trajectory from last close to moving average prediction."""
        last_close = self._last_close
        ma_pred = self._ma_pred

        if full_df is not None:
            last_close = float(full_df["close"].iloc[-1])
            sma_series = full_df["close"].rolling(20).mean()
            ma_pred = float(sma_series.iloc[-1]) if len(full_df) >= 20 else last_close
        else:
            if latest_close is not None:
                last_close = latest_close
            if latest_row is not None and "sma_20" in latest_row.columns:
                ma_pred = float(latest_row["sma_20"].iloc[0])

        # Apply post-processing technical signal adjustment
        adjustment = self.compute_technical_adjustment(
            predicted_price=ma_pred,
            last_close=last_close,
            technical_score=technical_score,
            technical_confidence=technical_confidence,
        )
        adjusted_ma_pred = ma_pred + adjustment

        prices = [
            round(last_close + (i + 1) * (adjusted_ma_pred - last_close) / horizon, 4)
            for i in range(horizon)
        ]
        return prices

    # ------------------------------------------------------------------
    def evaluate(self, test_df: pd.DataFrame) -> EvaluationResult:
        """Score the moving average predictions against actual 30-day close prices."""
        y_true = test_df["target"].values
        
        # Predict Close(t+30) at each index in test_df using 20-day MA
        y_pred_series = test_df["close"].rolling(20).mean().fillna(test_df["close"])
        y_pred = y_pred_series.values

        return ModelEvaluator.compute(
            model_name=self.name,
            y_true=y_true,
            y_pred=y_pred,
            y_base=test_df["close"].values,
        )

