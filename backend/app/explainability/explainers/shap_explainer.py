"""
Real SHAP explainer using TreeExplainer for XGBoost models.

SHAP (SHapley Additive exPlanations) uses game-theory-based Shapley values to
assign each feature a signed contribution to a specific prediction.

Why TreeExplainer?
    - Exact (not approximate) for tree-based models
    - O(TLD) complexity — fast even for 200-estimator forests
    - Values are in output space (LKR), not probability space
    - Produces `expected_value` (base value) = average model output over training set

Reference: Lundberg & Lee, "A Unified Approach to Interpreting Model Predictions", NeurIPS 2017
"""

import logging
import numpy as np
import pandas as pd
from typing import Optional

from app.explainability.base import BaseExplainer
from app.explainability.schemas import PredictionExplanation, FeatureImpact
from app.explainability.utils import format_feature_name

logger = logging.getLogger(__name__)


class SHAPExplainer(BaseExplainer):
    """
    Computes SHAP values for XGBoost models using shap.TreeExplainer.

    Only call this for models that expose `._model` as an XGBRegressor.
    For SARIMAX, use SARIMAXExplainer. For Baseline, use PermutationExplainer.
    """

    name = "shap"

    def explain(
        self,
        model,
        features: pd.DataFrame,
        prediction: float,
        symbol: str,
        confidence: float,
    ) -> PredictionExplanation:
        """
        Compute per-sample SHAP values for a single prediction row.

        Steps:
            1. Extract the underlying XGBRegressor from XGBoostModel wrapper
            2. Create TreeExplainer (uses exact path-dependent algorithm)
            3. Compute shap_values for the feature row (shape: [1, n_features])
            4. Map each SHAP value → FeatureImpact (signed, in LKR)
            5. Return top-10 by absolute value

        Args:
            model:      Trained XGBoostModel instance (must have ._model attribute)
            features:   Single-row DataFrame with feature columns
            prediction: Predicted next-day close price (LKR)
            symbol:     Stock ticker
            confidence: Heuristic confidence from EvaluationResult

        Returns:
            PredictionExplanation with real SHAP values
        """
        import shap

        # Unwrap the XGBRegressor from our wrapper class
        xgb_regressor = getattr(model, "_model", None)
        feature_names  = getattr(model, "_feature_names", list(features.columns))

        if xgb_regressor is None:
            raise ValueError(
                f"SHAPExplainer requires a trained XGBoostModel with ._model attribute. "
                f"Got: {type(model).__name__}"
            )

        # Align feature columns to what the model was trained on
        feat_cols = [c for c in feature_names if c in features.columns]
        X_row = features[feat_cols].values  # shape: (1, n_features)

        # Create TreeExplainer — fast and exact for XGBoost.
        # Fall back to model-agnostic shap.Explainer if tree loading fails (common with some XGBoost/SHAP version mismatches).
        try:
            explainer = shap.TreeExplainer(xgb_regressor)
            shap_values = explainer.shap_values(X_row)
            base_value = float(explainer.expected_value)
        except Exception as e:
            logger.warning(f"TreeExplainer failed: {e}. Falling back to general Explainer.")
            # Wrap predict as a callable function so shap.Explainer can run model-agnostic estimation
            predict_fn = lambda x: xgb_regressor.predict(x)
            explainer = shap.Explainer(predict_fn, features[feat_cols])
            shap_values_obj = explainer(features[feat_cols])
            # Handle shap 0.44+ explanation object
            if hasattr(shap_values_obj, "values"):
                shap_values = shap_values_obj.values
                base_value = float(shap_values_obj.base_values[0])
            else:
                shap_values = shap_values_obj
                base_value = float(prediction) # fallback approximation



        # shap_values can be 2-D for regression; flatten to 1-D
        if hasattr(shap_values, "ndim") and shap_values.ndim == 2:
            sv = shap_values[0]
        else:
            sv = np.array(shap_values).flatten()

        # Build FeatureImpact list from SHAP values
        raw_impacts = list(zip(feat_cols, sv.tolist()))

        # Sort by absolute SHAP value, take top 10
        raw_impacts.sort(key=lambda x: abs(x[1]), reverse=True)
        top10 = raw_impacts[:10]

        top_features = [
            FeatureImpact(
                feature=format_feature_name(feat),
                impact=round(float(val), 4),
                abs_impact=round(abs(float(val)), 4),
                direction="positive" if val >= 0 else "negative",
            )
            for feat, val in top10
        ]

        logger.info(
            f"SHAP computed for {symbol}: base={base_value:.2f}, "
            f"top_feature={top10[0][0] if top10 else 'none'}"
        )

        return PredictionExplanation(
            symbol=symbol,
            prediction=round(prediction, 4),
            model=getattr(model, "name", "xgboost"),
            confidence=round(confidence, 4),
            top_features=top_features,
            explanation_method=self.name,
            baseline_value=round(base_value, 4),
            warning=None,
        )
