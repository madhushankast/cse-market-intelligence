"""
ModelEvaluator — computes standard regression metrics for time-series
stock price forecasting evaluation.

Metrics:
    RMSE  — Root Mean Squared Error        (lower is better)
    MAE   — Mean Absolute Error            (lower is better)
    MAPE  — Mean Absolute Percentage Error (lower is better, expressed as %)
    R²    — Coefficient of Determination   (higher is better)
"""

import numpy as np
import pandas as pd
from app.forecasting.base import EvaluationResult


class ModelEvaluator:

    @staticmethod
    def compute(
        model_name: str,
        y_true: pd.Series | np.ndarray,
        y_pred: pd.Series | np.ndarray,
        y_base: pd.Series | np.ndarray | None = None,
        warning: str | None = None,
    ) -> EvaluationResult:
        """
        Calculate RMSE, MAE, MAPE, and R² between actuals and predictions.

        Args:
            model_name: Label for the model being evaluated.
            y_true:     Actual close price values (hold-out set).
            y_pred:     Model-predicted close price values.
            y_base:     Optional base close price (close at time t) to calculate direction.
            warning:    Optional warning string forwarded to the result.

        Returns:
            EvaluationResult dataclass.
        """
        y_true = np.array(y_true, dtype=float)
        y_pred = np.array(y_pred, dtype=float)

        n = len(y_true)

        # RMSE
        rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))

        # MAE
        mae = float(np.mean(np.abs(y_true - y_pred)))

        # MAPE
        mape = float(np.mean(np.abs((y_true - y_pred) / np.where(y_true == 0, 1e-8, y_true)))) * 100

        # Directional Accuracy
        if y_base is not None:
            y_base = np.array(y_base, dtype=float)
            actual_up = y_true >= y_base
            pred_up = y_pred >= y_base
            direction_accuracy = float(np.mean(actual_up == pred_up))
        else:
            # Fallback: compare changes element-to-element
            actual_up = np.diff(y_true, prepend=y_true[0]) >= 0
            pred_up = np.diff(y_pred, prepend=y_pred[0]) >= 0
            direction_accuracy = float(np.mean(actual_up == pred_up))

        # R²
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        r2 = float(1 - ss_res / ss_tot) if ss_tot != 0 else 0.0

        return EvaluationResult(
            model_name=model_name,
            rmse=round(rmse, 4),
            mae=round(mae, 4),
            mape=round(mape, 4),
            direction_accuracy=round(direction_accuracy, 4),
            r2=round(r2, 4),
            n_test=n,
            warning=warning,
        )

