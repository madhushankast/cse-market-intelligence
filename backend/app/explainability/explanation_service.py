"""
ExplanationService — decides which explainer to use based on the model type
and orchestrates explanation generation, database logging, and visual data building.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
import pandas as pd

from app.database.connection import SessionLocal, create_tables
from app.models.prediction_explanation import PredictionExplanationLog
from app.explainability.schemas import PredictionExplanation, FeatureImpact, VisualizationData
from app.explainability.explainers.shap_explainer import SHAPExplainer
from app.explainability.explainers.sarimax_explainer import SARIMAXExplainer
from app.explainability.explainers.permutation_explainer import PermutationExplainer
from app.explainability.visualizations import ExplanationVisualizer
from app.explainability.utils import format_feature_name
from app.forecasting.prediction_service import PredictionService

logger = logging.getLogger(__name__)


class ExplanationService:
    """
    Decodes the model type, routes to the appropriate explainer,
    constructs visual metrics, and logs the result to SQLite.
    """

    def __init__(self):
        self._shap = SHAPExplainer()
        self._sarimax = SARIMAXExplainer()
        self._permutation = PermutationExplainer()
        self._pred_service = PredictionService()
        # Initialize tables just in case they aren't created yet
        create_tables()

    def explain_prediction(
        self,
        symbol: str,
        horizon: int = 7,
        model_override: Optional[str] = None,
        include_viz: bool = False,
    ) -> PredictionExplanation:
        """
        Explains a prediction using model-specific explainability strategies.
        """
        symbol = symbol.upper()
        # 1. Fetch merged dataframe and trainer details
        df_merged = self._pred_service._get_merged_df(symbol)
        training = self._pred_service._get_or_train(symbol, horizon)

        # 2. Select model
        best_name = model_override or training.best_model
        best_result = training.evaluations.get(best_name)
        confidence = best_result.confidence() if best_result else 0.5

        # Extract predictions
        forecasts = training.forecasts.get(best_name, [])
        best_prediction = forecasts[0] if forecasts else None

        if best_prediction is None:
            return self._placeholder(symbol, confidence, f"No forecast available for model {best_name}")

        # Get last row for prediction features
        from app.forecasting.dataset import ForecastDataset
        dataset = ForecastDataset(df_merged)
        last_row = dataset.get_last_row()

        # Re-fit / fetch the actual model object
        model_obj = self._get_model_object(best_name, df_merged)

        # 3. Route to proper explainer
        explanation = None
        try:
            if best_name == "xgboost":
                explanation = self._shap.explain(
                    model=model_obj,
                    features=last_row,
                    prediction=best_prediction,
                    symbol=symbol,
                    confidence=confidence,
                )
            elif best_name == "sarimax":
                explanation = self._sarimax.explain(
                    model=model_obj,
                    features=last_row,
                    prediction=best_prediction,
                    symbol=symbol,
                    confidence=confidence,
                )
            else:
                # Baseline or other model fallback: Permutation Importance
                X_train, X_test, y_train, y_test = dataset.split(test_size=0.2)
                train_df = dataset.df.iloc[:len(X_train)].copy()
                test_df = dataset.df.iloc[len(X_train):].copy()

                explanation = self._permutation.explain(
                    model=model_obj,
                    features=last_row,
                    prediction=best_prediction,
                    symbol=symbol,
                    confidence=confidence,
                    train_df=train_df,
                    test_df=test_df,
                )
        except Exception as e:
            logger.warning(f"Primary explainer failed for {best_name}: {e}. Falling back to permutation.")
            try:
                # Generic fallback
                explanation = self._permutation.explain(
                    model=model_obj,
                    features=last_row,
                    prediction=best_prediction,
                    symbol=symbol,
                    confidence=confidence,
                )
            except Exception as fe:
                return self._placeholder(symbol, confidence, f"All explainers failed: {fe}")

        # Ensure correct formatting of feature names
        formatted_features = []
        for feat in explanation.top_features:
            formatted_features.append(FeatureImpact(
                feature=format_feature_name(feat.feature),
                impact=feat.impact,
                abs_impact=feat.abs_impact,
                direction=feat.direction
            ))
        explanation.top_features = formatted_features

        # 4. Visualization Data
        if include_viz:
            explanation.visualization_data = ExplanationVisualizer.build(explanation)

        # 5. Database Logging (Asynchronous/Non-blocking in API)
        self._log_to_db(explanation)

        return explanation

    def _get_model_object(self, model_name: str, df: pd.DataFrame):
        from app.forecasting.dataset import ForecastDataset
        from app.forecasting.models.baseline import BaselineModel
        from app.forecasting.models.sarimax import SARIMAXModel
        from app.forecasting.models.xgboost import XGBoostModel

        dataset = ForecastDataset(df)
        n_train = int(len(dataset.df) * 0.80)
        train_df = dataset.df.iloc[:n_train]

        model_map = {
            "baseline": BaselineModel,
            "sarimax":  SARIMAXModel,
            "xgboost":  XGBoostModel,
        }
        ModelClass = model_map.get(model_name, XGBoostModel)
        model = ModelClass()
        model.train(train_df)
        return model

    def _log_to_db(self, exp: PredictionExplanation):
        db = SessionLocal()
        try:
            # Delete old entries for this symbol/model to prevent bloating
            db.query(PredictionExplanationLog).filter(
                PredictionExplanationLog.symbol == exp.symbol,
                PredictionExplanationLog.model == exp.model
            ).delete()

            # Insert new feature impacts
            for idx, feat in enumerate(exp.top_features):
                log_entry = PredictionExplanationLog(
                    symbol=exp.symbol,
                    model=exp.model,
                    prediction=exp.prediction,
                    confidence=exp.confidence,
                    baseline_value=exp.baseline_value,
                    explanation_method=exp.explanation_method,
                    feature_name=feat.feature,
                    impact=feat.impact,
                    abs_impact=feat.abs_impact,
                    direction=feat.direction,
                    feature_rank=idx + 1,
                    warning=exp.warning,
                )
                db.add(log_entry)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to log explanation to database: {e}")
        finally:
            db.close()

    def _placeholder(self, symbol: str, confidence: float, warning: str) -> PredictionExplanation:
        return PredictionExplanation(
            symbol=symbol,
            prediction=0.0,
            model="unknown",
            confidence=confidence,
            top_features=[],
            explanation_method="placeholder",
            baseline_value=None,
            warning=warning,
        )
