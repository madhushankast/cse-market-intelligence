"""
Baseline (Naïve Persistence) Model.

The simplest possible forecast: tomorrow's price = today's price.
Every research project should benchmark against this — if a complex model
cannot beat the naïve baseline, it is not adding value.

MAPE of ~1–3% is typical for liquid stocks with low day-to-day volatility.
"""

import numpy as np
import pandas as pd
from app.forecasting.base import ForecastModel, EvaluationResult
from app.forecasting.evaluator import ModelEvaluator


class BaselineModel(ForecastModel):
    """
    Naïve persistence model: predicts the last observed close price
    for all future time steps.
    """

    name = "baseline"

    def __init__(self):
        self._last_close: float | None = None

    # ------------------------------------------------------------------
    def train(self, train_df: pd.DataFrame) -> None:
        """
        'Training' simply records the last close price in the training set.
        """
        self._last_close = float(train_df["close"].iloc[-1])

    # ------------------------------------------------------------------
    def predict(self, horizon: int = 7) -> list[float]:
        """
        Returns the last close price repeated `horizon` times.
        """
        if self._last_close is None:
            raise RuntimeError("BaselineModel must be trained before calling predict().")
        return [round(self._last_close, 4)] * horizon

    # ------------------------------------------------------------------
    def evaluate(self, test_df: pd.DataFrame) -> EvaluationResult:
        """
        The naïve model predicts close[t] for every row in the test set.
        (Each prediction is the previous row's close = test target[t-1].)
        """
        if self._last_close is None:
            raise RuntimeError("BaselineModel must be trained before calling evaluate().")

        y_true = test_df["target"].values

        # Naïve: pred[t] = close[t] (the current row's close, not the next)
        y_pred = test_df["close"].values

        return ModelEvaluator.compute(
            model_name=self.name,
            y_true=y_true,
            y_pred=y_pred,
        )
