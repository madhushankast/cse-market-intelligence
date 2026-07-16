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
    Wraps xgboost.XGBRegressor for supervised next-day close prediction.

    Feature importance is stored after training as `self.feature_importances_`,
    keyed by feature name — ready for SHAP in Milestone 10.
    """

    name = "xgboost"

    # Hyperparameters — conservatively chosen for datasets of 50–500 rows
    PARAMS = {
        "n_estimators":   200,
        "max_depth":      5,
        "learning_rate":  0.05,
        "subsample":      0.8,
        "colsample_bytree": 0.8,
        "random_state":   42,
        "tree_method":    "hist",   # fast CPU training, no GPU required
        "verbosity":      0,
    }

    def __init__(self):
        self._model = None
        self._feature_names: list[str] = []
        self._last_row: Optional[pd.DataFrame] = None
        self.feature_importances_: dict[str, float] = {}

    # ------------------------------------------------------------------
    def train(self, train_df: pd.DataFrame) -> None:
        """Fit XGBRegressor on training features."""
        from xgboost import XGBRegressor

        feature_cols = [c for c in train_df.columns if c not in ("target", "date")]
        self._feature_names = feature_cols

        X = train_df[feature_cols].values
        y = train_df["target"].values

        self._model = XGBRegressor(**self.PARAMS)
        self._model.fit(X, y)

        # Store last training row for iterative prediction
        self._last_row = train_df[feature_cols].iloc[[-1]].copy()

        # Build feature importance dict for SHAP readiness
        importances = self._model.feature_importances_
        self.feature_importances_ = {
            name: round(float(imp), 6)
            for name, imp in zip(feature_cols, importances)
        }

    # ------------------------------------------------------------------
    def predict(self, horizon: int = 7) -> list[float]:
        """
        Iterative multi-step prediction:
        1. Predict next close from last known features.
        2. Update the 'close' feature with the predicted value.
        3. Repeat for `horizon` steps.
        """
        if self._model is None or self._last_row is None:
            raise RuntimeError("XGBoostModel must be trained before calling predict().")

        predictions = []
        row = self._last_row.copy()

        for _ in range(horizon):
            X = row[self._feature_names].values
            pred = float(self._model.predict(X)[0])
            predictions.append(round(pred, 4))

            # Update 'close' for the next step (simple feature propagation)
            if "close" in row.columns:
                row["close"] = pred
            if "daily_return" in row.columns and pred != 0:
                prev_close = float(self._last_row["close"].iloc[0])
                row["daily_return"] = (pred - prev_close) / prev_close

        return predictions

    # ------------------------------------------------------------------
    def evaluate(self, test_df: pd.DataFrame) -> EvaluationResult:
        """One-step-ahead predictions on each row of the test set."""
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
        )
