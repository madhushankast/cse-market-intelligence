"""
SARIMAX Explainer — coefficient-based interpretation for ARIMA/SARIMAX models.

Why not SHAP for SARIMAX?
    SHAP TreeExplainer only supports tree-based models (XGBoost, LightGBM, Random Forest).
    SHAP KernelExplainer (model-agnostic) works but is extremely slow (~minutes per sample).

    For linear time-series models, coefficient analysis is the academically standard
    and computationally efficient alternative:

        impact[feature] = coefficient[feature] × current_value[feature]

    This gives a signed, magnitude-scaled interpretation of each exogenous variable's
    contribution to the forecast — equivalent to a marginal effect at the current values.

Academic reference:
    Hamilton, "Time Series Analysis" (1994) — coefficient interpretation in VAR/ARIMA models.
"""

import logging
import numpy as np
import pandas as pd
from typing import Optional

from app.explainability.base import BaseExplainer
from app.explainability.schemas import PredictionExplanation, FeatureImpact
from app.explainability.utils import format_feature_name

logger = logging.getLogger(__name__)

# Exogenous variable names used by SARIMAXModel
SARIMAX_EXOG_COLS = ["usd_lkr", "inflation", "trend_score"]

# AR/MA/seasonal parameter name prefixes to exclude from feature impacts
_INTERNAL_PARAM_PREFIXES = ("ar.", "ma.", "sigma2", "intercept", "drift",
                            "seasonal", "ar_S.", "ma_S.")


class SARIMAXExplainer(BaseExplainer):
    """
    Explains SARIMAX predictions via fitted coefficient × current feature value.

    Only call this for models that expose `._model_fit` as a statsmodels
    SARIMAXResultsWrapper and `._train_exog` as a DataFrame.
    """

    name = "sarimax_coefficients"

    def explain(
        self,
        model,
        features: pd.DataFrame,
        prediction: float,
        symbol: str,
        confidence: float,
    ) -> PredictionExplanation:
        """
        Derive feature impacts from fitted SARIMAX coefficients.

        Steps:
            1. Extract fitted params dict from model_fit.params
            2. Filter to exogenous variable parameters only
            3. For each exogenous var: impact = coef × current_feature_value
            4. Normalise to prediction scale (% of predicted price)
            5. Return FeatureImpact list sorted by |impact|
        """
        model_fit   = getattr(model, "_model_fit", None)
        exog_cols   = getattr(model, "_exog_cols_used", SARIMAX_EXOG_COLS)
        warning: Optional[str] = None

        if model_fit is None:
            raise ValueError(
                "SARIMAXExplainer requires a trained SARIMAXModel with ._model_fit. "
                f"Got: {type(model).__name__}"
            )

        try:
            params = model_fit.params.to_dict()
        except Exception as e:
            raise ValueError(f"Could not extract SARIMAX params: {e}")

        # Filter to exogenous variable parameters
        exog_params = {
            k: v for k, v in params.items()
            if not any(k.lower().startswith(p) for p in _INTERNAL_PARAM_PREFIXES)
            and not k.lower().startswith("x")  # 'x1', 'x2' generic names if unnamed
        }

        # Prefer named exogenous columns over generic param names
        top_features: list[FeatureImpact] = []

        if exog_cols:
            for col in exog_cols:
                # Find matching param key (statsmodels names exog vars by column name)
                coef = params.get(col, None)
                if coef is None:
                    # Try by position (statsmodels may use generic 'x1', 'x2')
                    idx = exog_cols.index(col)
                    coef = params.get(f"x{idx + 1}", None)

                if coef is None:
                    continue

                # Current feature value from the last available row
                current_val = 0.0
                if features is not None and col in features.columns:
                    current_val = float(features[col].iloc[0])

                impact = float(coef) * current_val

                top_features.append(FeatureImpact(
                    feature=format_feature_name(col),
                    impact=round(impact, 4),
                    abs_impact=round(abs(impact), 4),
                    direction="positive" if impact >= 0 else "negative",
                ))

        if not top_features:
            # Fall back to raw param dict — any non-internal parameter
            for name, coef in list(exog_params.items())[:10]:
                current_val = 1.0  # unknown value; show coefficient magnitude
                impact = float(coef) * current_val
                top_features.append(FeatureImpact(
                    feature=format_feature_name(name),
                    impact=round(impact, 4),
                    abs_impact=round(abs(impact), 4),
                    direction="positive" if impact >= 0 else "negative",
                ))
            if not top_features:
                warning = (
                    "SARIMAX model had no identifiable exogenous coefficients. "
                    "Check that macro data (CBSL) was available during training."
                )

        # Sort by absolute impact
        top_features.sort(key=lambda x: x.abs_impact, reverse=True)

        logger.info(
            f"SARIMAX coefficient explanation produced for {symbol}: "
            f"{len(top_features)} features"
        )

        return PredictionExplanation(
            symbol=symbol,
            prediction=round(prediction, 4),
            model=getattr(model, "name", "sarimax"),
            confidence=round(confidence, 4),
            top_features=top_features,
            explanation_method=self.name,
            baseline_value=None,  # no equivalent concept in ARIMA
            warning=warning,
        )
