"""
PermutationExplainer — model-agnostic feature importance via permutation.

Works with ANY model that implements predict() — Baseline, SARIMAX, XGBoost,
or any future model. Used as the universal fallback when model-specific
explainers (SHAP, coefficient analysis) are unavailable or fail.

Algorithm:
    For each feature f:
        1. Create a perturbed copy of the test set where column f is shuffled
        2. Compute mean absolute prediction change: Δ = mean|pred_original − pred_perturbed|
        3. Δ represents how much the model "relies on" feature f (in LKR)

    Features with large Δ are most important.

Limitation:
    - Values are unsigned (no direction information from permutation alone)
    - Direction is inferred from correlation between feature and target in training data
    - Slower than SHAP (~1s per feature for 100-row test set)

Reference:
    Breiman, "Random Forests" (2001) — original permutation importance idea.
    Fisher, Rudin & Dominici, "All Models are Wrong" (2018) — model-agnostic version.
"""

import logging
import numpy as np
import pandas as pd
from typing import Optional

from app.explainability.base import BaseExplainer
from app.explainability.schemas import PredictionExplanation, FeatureImpact
from app.explainability.utils import format_feature_name, top_n_features

logger = logging.getLogger(__name__)

N_REPEATS = 5       # number of shuffle repeats to stabilise estimates
N_SAMPLES  = 50     # max test rows to evaluate (speed cap)
TOP_N      = 10     # features to return


class PermutationExplainer(BaseExplainer):
    """
    Model-agnostic permutation importance — universal fallback explainer.
    Trains on the train_df passed at init so it can measure prediction change.
    """

    name = "permutation_importance"

    def explain(
        self,
        model,
        features: pd.DataFrame,
        prediction: float,
        symbol: str,
        confidence: float,
        train_df: Optional[pd.DataFrame] = None,
        test_df:  Optional[pd.DataFrame] = None,
    ) -> PredictionExplanation:
        """
        Compute permutation importance for the model.

        Args:
            model:      Any trained ForecastModel instance
            features:   Last-row feature DataFrame (used for fallback single-row mode)
            prediction: Next-day close price prediction (LKR)
            symbol:     Stock ticker
            confidence: Heuristic confidence score
            train_df:   Training DataFrame (used to infer feature-target correlation)
            test_df:    Test DataFrame (permuted for importance calculation)

        Returns:
            PredictionExplanation with unsigned (direction-inferred) feature impacts
        """
        feature_cols = getattr(model, "_feature_names", list(features.columns))
        feature_cols = [c for c in feature_cols if c not in ("target", "date")]
        warning: Optional[str] = None

        if test_df is None or len(test_df) < 5:
            # Can't do permutation without test data → use features directly
            return self._single_row_fallback(
                model, features, feature_cols, prediction, symbol, confidence
            )

        # Cap test size for speed
        test_sample = test_df.iloc[:N_SAMPLES].copy()
        X_cols = [c for c in feature_cols if c in test_sample.columns]

        if not X_cols:
            return self._single_row_fallback(
                model, features, feature_cols, prediction, symbol, confidence
            )

        X_test = test_sample[X_cols].values
        y_true = test_sample["target"].values if "target" in test_sample.columns else None

        # Baseline predictions (no permutation)
        try:
            baseline_preds = model._model.predict(X_test)  # type: ignore
        except Exception:
            return self._single_row_fallback(
                model, features, feature_cols, prediction, symbol, confidence
            )

        importances: dict[str, float] = {}

        for i, col in enumerate(X_cols):
            delta_sum = 0.0
            for _ in range(N_REPEATS):
                X_perm = X_test.copy()
                np.random.shuffle(X_perm[:, i])
                perm_preds = model._model.predict(X_perm)  # type: ignore
                delta_sum += float(np.mean(np.abs(baseline_preds - perm_preds)))
            importances[col] = delta_sum / N_REPEATS

        # Infer direction from training-set correlation (if available)
        correlations: dict[str, float] = {}
        if train_df is not None and "target" in train_df.columns:
            for col in X_cols:
                if col in train_df.columns:
                    try:
                        correlations[col] = float(
                            train_df[col].corr(train_df["target"])
                        )
                    except Exception:
                        correlations[col] = 0.0

        # Build top features
        sorted_imp = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:TOP_N]
        top_features = []
        for feat, imp in sorted_imp:
            corr   = correlations.get(feat, 0.0)
            signed = imp if corr >= 0 else -imp
            top_features.append(FeatureImpact(
                feature=format_feature_name(feat),
                impact=round(signed, 4),
                abs_impact=round(imp, 4),
                direction="positive" if signed >= 0 else "negative",
            ))

        logger.info(
            f"Permutation importance computed for {symbol}: "
            f"{len(top_features)} features, model={getattr(model, 'name', '?')}"
        )

        return PredictionExplanation(
            symbol=symbol,
            prediction=round(prediction, 4),
            model=getattr(model, "name", type(model).__name__),
            confidence=round(confidence, 4),
            top_features=top_features,
            explanation_method=self.name,
            baseline_value=None,
            warning=warning,
        )

    def _single_row_fallback(
        self,
        model,
        features: pd.DataFrame,
        feature_cols: list[str],
        prediction: float,
        symbol: str,
        confidence: float,
    ) -> PredictionExplanation:
        """
        When test data is unavailable, use the existing gain-based importances
        from the model (XGBoost) or return empty list with a warning.
        """
        importances = getattr(model, "feature_importances_", {})
        top_features: list[FeatureImpact] = []

        if importances:
            sorted_imp = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:TOP_N]
            max_val = sorted_imp[0][1] if sorted_imp else 1.0
            scale   = (prediction * 0.05) / max_val if max_val > 0 and prediction > 0 else 1.0

            for feat, val in sorted_imp:
                feat_val = 0.0
                if feat in features.columns:
                    feat_val = float(features[feat].iloc[0])
                signed = val * scale * (1 if feat_val >= 0 else -1)
                top_features.append(FeatureImpact(
                    feature=format_feature_name(feat),
                    impact=round(signed, 4),
                    abs_impact=round(val * scale, 4),
                    direction="positive" if signed >= 0 else "negative",
                ))

        return PredictionExplanation(
            symbol=symbol,
            prediction=round(prediction, 4),
            model=getattr(model, "name", type(model).__name__),
            confidence=round(confidence, 4),
            top_features=top_features,
            explanation_method=self.name + "_fallback",
            baseline_value=None,
            warning="Permutation test data unavailable — using gain-based importance approximation.",
        )
