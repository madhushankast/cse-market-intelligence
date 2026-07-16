"""
ForecastTrainer — orchestrates the full training and evaluation pipeline.

Workflow:
    1. Build ForecastDataset from the merged DataFrame
    2. Split into train (80%) / test (20%) — time-ordered, no shuffle
    3. Train all models on the training set
    4. Evaluate each model on the hold-out test set
    5. Identify the best model by lowest MAPE
    6. Generate `horizon`-day forecasts from the best model

Designed to be called by PredictionService with the merged DataFrame
already prepared by the existing data-integration layer.
"""

import pandas as pd
from dataclasses import dataclass
from typing import Optional

from app.forecasting.dataset import ForecastDataset
from app.forecasting.base import EvaluationResult
from app.forecasting.evaluator import ModelEvaluator
from app.forecasting.models.baseline import BaselineModel
from app.forecasting.models.sarimax import SARIMAXModel
from app.forecasting.models.xgboost import XGBoostModel


@dataclass
class TrainingResult:
    """Complete output from a training + evaluation run."""
    evaluations:        dict[str, EvaluationResult]   # model_name → metrics
    forecasts:          dict[str, list[float]]         # model_name → predicted values
    best_model:         str
    best_forecast:      list[float]
    feature_importances: dict[str, float]              # from XGBoost (for SHAP)
    n_train:            int
    n_test:             int
    n_features:         int


class ForecastTrainer:
    """
    Trains and evaluates Baseline, SARIMAX, and XGBoost models on
    the provided merged dataset, then selects the best performer.
    """

    TEST_SIZE = 0.20    # 80 / 20 time-ordered split

    def run(self, df: pd.DataFrame, horizon: int = 7) -> TrainingResult:
        """
        Execute the full training pipeline.

        Args:
            df:      Merged DataFrame (stock + macro + trends) sorted by date.
            horizon: Number of future trading days to forecast.

        Returns:
            TrainingResult with per-model metrics, forecasts, and best model.
        """
        dataset = ForecastDataset(df)
        X_train, X_test, y_train, y_test = dataset.split(test_size=self.TEST_SIZE)

        # Reconstruct train/test DataFrames with all columns for model access
        n_train = len(X_train)
        train_df = dataset.df.iloc[:n_train].copy()
        test_df  = dataset.df.iloc[n_train:].copy()

        models = {
            "baseline": BaselineModel(),
            "sarimax":  SARIMAXModel(),
            "xgboost":  XGBoostModel(),
        }

        evaluations: dict[str, EvaluationResult] = {}
        forecasts:   dict[str, list[float]]       = {}

        for model_name, model in models.items():
            try:
                model.train(train_df)
                eval_result = model.evaluate(test_df)
                forecast    = model.predict(horizon=horizon)
                evaluations[model_name] = eval_result
                forecasts[model_name]   = forecast
            except Exception as exc:
                # Don't let one model failure break the entire pipeline
                evaluations[model_name] = EvaluationResult(
                    model_name=model_name,
                    rmse=999.0, mae=999.0, mape=999.0, r2=0.0,
                    n_test=0,
                    warning=f"Training failed: {str(exc)[:120]}",
                )
                forecasts[model_name] = []

        # Pick best model by lowest MAPE (excluding failed models)
        ranked = sorted(
            [(name, ev) for name, ev in evaluations.items() if ev.mape < 999.0],
            key=lambda x: x[1].mape,
        )
        best_model_name = ranked[0][0] if ranked else "baseline"
        best_forecast   = forecasts.get(best_model_name, [])

        # XGBoost feature importances (for SHAP readiness)
        xgb_model: XGBoostModel = models.get("xgboost")  # type: ignore
        feature_importances = getattr(xgb_model, "feature_importances_", {})

        return TrainingResult(
            evaluations=evaluations,
            forecasts=forecasts,
            best_model=best_model_name,
            best_forecast=best_forecast,
            feature_importances=feature_importances,
            n_train=n_train,
            n_test=len(test_df),
            n_features=len(dataset.feature_names),
        )
