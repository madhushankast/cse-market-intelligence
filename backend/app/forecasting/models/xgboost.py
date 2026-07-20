"""
XGBoost Model — Gradient Boosted Trees for next-day close price prediction.

Why XGBoost for CSE?
    - Handles non-linear relationships between technical and macro features
    - Robust to missing values (built-in NaN handling)
    - Feature importance is tracked — ready for SHAP explainability (Milestone 10)
    - Frequently outperforms linear models on tabular financial data

Training strategy:
    - Walk-forward cross-validation is NOT used here (too slow for on-demand API);
      instead we use a single 80/20 time-aware split.
    - Hyperparameters are conservatively tuned for small/medium datasets.
"""

import numpy as np
import pandas as pd
from typing import Optional

from app.forecasting.base import ForecastModel, EvaluationResult
from app.forecasting.evaluator import ModelEvaluator


class XGBoostModel(ForecastModel):
    """
    Wraps xgboost.XGBRegressor for supervised 30-day close price prediction.
    """

    name = "xgboost"

    # Hyperparameters — conservatively chosen for small/medium datasets
    PARAMS = {
        "n_estimators":   200,
        "max_depth":      5,
        "learning_rate":  0.05,
        "subsample":      0.8,
        "colsample_bytree": 0.8,
        "random_state":   42,
        "tree_method":    "hist",
        "verbosity":      0,
    }

    def __init__(self):
        self._model = None
        self._feature_names: list[str] = []
        self._last_row: Optional[pd.DataFrame] = None
        self.feature_importances_: dict[str, float] = {}
        self._last_close = 0.0

    # ------------------------------------------------------------------
    def train(self, train_df: pd.DataFrame) -> None:
        """Fit XGBRegressor on training Close(t+30)."""
        from xgboost import XGBRegressor

        # Keep all features except target, date, and symbol
        ignored_cols = ("target", "date", "symbol")
        feature_cols = [c for c in train_df.columns if c not in ignored_cols]
        self._feature_names = feature_cols

        X = train_df[feature_cols].values
        y = train_df["target"].values

        self._model = XGBRegressor(**self.PARAMS)
        self._model.fit(X, y)

        # Store last training row and last close price
        self._last_row = train_df[feature_cols].iloc[[-1]].copy()
        self._last_close = float(train_df["close"].iloc[-1])

        # Build feature importance dict for SHAP
        importances = self._model.feature_importances_
        self.feature_importances_ = {
            name: round(float(imp), 6)
            for name, imp in zip(feature_cols, importances)
        }

    def predict(
        self,
        horizon: int = 30,
        latest_row: Optional[pd.DataFrame] = None,
        latest_close: Optional[float] = None,
        full_df: Optional[pd.DataFrame] = None,
        technical_score: Optional[float] = None,
        technical_confidence: Optional[float] = None,
    ) -> list[float]:
        """Predict expected 30-day close and project linear path."""
        if self._model is None or (self._last_row is None and latest_row is None and full_df is None):
            raise RuntimeError("XGBoostModel must be trained before calling predict().")

        row = self._last_row
        last_close = self._last_close

        if full_df is not None:
            last_close = float(full_df["close"].iloc[-1])
            from app.forecasting.dataset import ForecastDataset
            dataset = ForecastDataset(full_df)
            row = dataset.get_last_row()
        else:
            if latest_row is not None:
                row = latest_row
            if latest_close is not None:
                last_close = latest_close

        X = row[self._feature_names].values
        pred_val = float(self._model.predict(X)[0])

        # Apply post-processing technical signal adjustment
        adjustment = self.compute_technical_adjustment(
            predicted_price=pred_val,
            last_close=last_close,
            technical_score=technical_score,
            technical_confidence=technical_confidence,
        )
        adjusted_pred_val = pred_val + adjustment

        # Project a linear path from current close to predicted 30-day close price
        prices = [
            round(last_close + (i + 1) * (adjusted_pred_val - last_close) / horizon, 4)
            for i in range(horizon)
        ]

        return prices

    # ------------------------------------------------------------------
    def evaluate(self, test_df: pd.DataFrame) -> EvaluationResult:
        """Evaluate predictions on the hold-out test set."""
        if self._model is None:
            raise RuntimeError("XGBoostModel must be trained before calling evaluate().")

        feature_cols = [c for c in self._feature_names if c in test_df.columns]
        X_test = test_df[feature_cols].values
        y_true = test_df["target"].values
        y_pred = self._model.predict(X_test)

        return ModelEvaluator.compute(
            model_name=self.name,
            y_true=y_true,
            y_pred=y_pred,
            y_base=test_df["close"].values,
        )

