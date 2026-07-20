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
    forecast_intervals:  dict[str, list[tuple[float, float]]]
    best_intervals:      list[tuple[float, float]]
    technical_score:     Optional[float] = None
    technical_confidence: Optional[float] = None
    technical_adjustment: Optional[float] = None


class ForecastTrainer:
    """
    Trains and evaluates Baseline, SARIMAX, and XGBoost models on
    the provided merged dataset, then selects the best performer.
    """

    TEST_SIZE = 0.20    # 80 / 20 time-ordered split

    def run(self, df: pd.DataFrame, horizon: int = 30) -> TrainingResult:
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
        intervals:   dict[str, list[tuple[float, float]]] = {}

        # Calculate technical signals for post-processing adjustment
        technical_score = None
        technical_confidence = None
        try:
            from app.analytics.technical_signal import TechnicalSignalEngine
            tech_res = TechnicalSignalEngine.calculate(df)
            if "error" not in tech_res:
                technical_score = float(tech_res["score"])
                technical_confidence = float(tech_res["confidence"])
        except Exception:
            pass

        for model_name, model in models.items():
            try:
                model.train(train_df)
                eval_result = model.evaluate(test_df)
                forecast    = model.predict(
                    horizon=horizon,
                    full_df=df,
                    technical_score=technical_score,
                    technical_confidence=technical_confidence
                )
                evaluations[model_name] = eval_result
                forecasts[model_name]   = forecast

                # Retrieve confidence intervals or fallback to heuristic (1.96 * RMSE)
                if getattr(model, "last_confidence_intervals", None):
                    intervals[model_name] = model.last_confidence_intervals
                else:
                    rmse = eval_result.rmse
                    intervals[model_name] = [
                        (round(val - 1.96 * rmse, 4), round(val + 1.96 * rmse, 4))
                        for val in forecast
                    ]
            except Exception as exc:
                # Don't let one model failure break the entire pipeline
                eval_result = EvaluationResult(
                    model_name=model_name,
                    rmse=999.0, mae=999.0, mape=999.0,
                    direction_accuracy=0.0, r2=0.0,
                    n_test=0,
                    warning=f"Training failed: {str(exc)[:120]}",
                )
                evaluations[model_name] = eval_result
                forecasts[model_name] = []
                intervals[model_name] = []

        # Pick best model by weighted selection score (lowest score is best)
        # Score = 0.4*RMSE + 0.2*MAE + 0.2*MAPE + 0.2*(100 - DirAcc*100)
        def compute_selection_score(ev):
            da_pct = ev.direction_accuracy * 100 if ev.direction_accuracy <= 1.0 else ev.direction_accuracy
            return 0.4 * ev.rmse + 0.2 * ev.mae + 0.2 * ev.mape + 0.2 * (100.0 - da_pct)

        ranked = sorted(
            [(name, ev) for name, ev in evaluations.items() if ev.rmse < 999.0],
            key=lambda x: compute_selection_score(x[1])
        )
        best_model_name = ranked[0][0] if ranked else "baseline"
        best_forecast   = forecasts.get(best_model_name, [])
        best_intervals  = intervals.get(best_model_name, [])

        # XGBoost feature importances (for SHAP readiness)
        xgb_model: XGBoostModel = models.get("xgboost")  # type: ignore
        feature_importances = getattr(xgb_model, "feature_importances_", {})

        # Calculate the actual LKR adjustment applied to the best model
        technical_adjustment = 0.0
        if best_model_name in models and technical_score is not None and technical_confidence is not None:
            best_model_obj = models[best_model_name]
            last_close = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            technical_adjustment = best_model_obj.compute_technical_adjustment(
                predicted_price=0.0,
                last_close=last_close,
                technical_score=technical_score,
                technical_confidence=technical_confidence
            )

        return TrainingResult(
            evaluations=evaluations,
            forecasts=forecasts,
            best_model=best_model_name,
            best_forecast=best_forecast,
            feature_importances=feature_importances,
            n_train=n_train,
            n_test=len(test_df),
            n_features=len(dataset.feature_names),
            forecast_intervals=intervals,
            best_intervals=best_intervals,
            technical_score=technical_score,
            technical_confidence=technical_confidence,
            technical_adjustment=technical_adjustment,
        )
