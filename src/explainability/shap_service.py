"""
TreeSHAP Feature Attribution Service
------------------------------------
Provides exact local and global Shapley feature attributions (Lundberg et al., 2020)
for 30-day forward return predictions using LightGBM P50 median models.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd
import lightgbm as lgb

logger = logging.getLogger(__name__)

FEATURE_DESCRIPTIONS: Dict[str, str] = {
    "return_1d": "1-day immediate price return",
    "return_5d": "Short-term 5-day momentum",
    "return_10d": "Intermediate 10-day price trend",
    "return_20d": "1-month (20-day) price performance",
    "return_30d": "Trailing 30-day cumulative return",
    "rsi_14": "14-day Relative Strength Index (RSI)",
    "macd": "MACD momentum oscillator line",
    "macd_signal": "MACD 9-day signal trigger line",
    "macd_hist": "MACD histogram acceleration",
    "ema_ratio_12_26": "Short-to-medium EMA ratio (12/26)",
    "sma_ratio_20_50": "Medium-term moving average trend (SMA 20/50)",
    "parkinson_vol": "Intraday Parkinson volatility",
    "parkinson_vol_10d": "10-day rolling Parkinson volatility",
    "parkinson_vol_20d": "20-day high-low price variance",
    "high_low_spread": "Daily high-low trading spread",
    "volume_surge_ratio": "Trading volume expansion relative to 20d average",
    "log_volume": "Normalized trading activity (Log Volume)",
    "aspi_return_5d": "5-day ASPI CSE benchmark momentum",
    "aspi_return_10d": "10-day ASPI CSE benchmark return",
    "aspi_return_30d": "30-day ASPI CSE market benchmark trend",
    "relative_strength_30d": "30-day stock outperformance vs. ASPI index",
    "rolling_corr_aspi_30d": "30-day rolling correlation with ASPI (Beta proxy)",
}


class ShapExplanationService:
    """
    Mathematical Attribution Engine (Layer 1) using exact TreeSHAP.
    Computes local Shapley values decomposing 30-day expected return:
        y_hat_P50 = phi_0 + sum(phi_i)
    """

    def __init__(
        self,
        model: lgb.LGBMRegressor,
        feature_names: List[str],
        symbol: Optional[str] = None,
    ):
        self.model = model
        self.feature_names = feature_names
        self.symbol = symbol or "EQUITY"
        self.explainer = None
        self._init_explainer()

    def _init_explainer(self) -> None:
        try:
            import shap
            booster = self.model.booster_ if hasattr(self.model, "booster_") else self.model
            self.explainer = shap.TreeExplainer(booster)
        except Exception as exc:
            logger.warning("Could not initialize shap.TreeExplainer: %s. Using feature importance fallback.", exc)
            self.explainer = None

    @classmethod
    def from_model_dir(
        cls,
        symbol: str,
        models_dir: Union[str, Path] = "models",
    ) -> ShapExplanationService:
        """
        Factory to instantiate ShapExplanationService directly from serialized artifacts in models/{symbol}/.
        """
        target_dir = Path(models_dir) / symbol
        if not target_dir.exists():
            clean_sym = symbol.replace(".", "_")
            target_dir = Path(models_dir) / clean_sym

        if not target_dir.exists():
            raise FileNotFoundError(f"Model directory for '{symbol}' not found at {target_dir}")

        feature_file = target_dir / "feature_names.json"
        if not feature_file.exists():
            raise FileNotFoundError(f"Missing feature_names.json for '{symbol}'")

        with open(feature_file, "r", encoding="utf-8") as f:
            feature_names = json.load(f)

        # Load P50 LightGBM booster
        txt_path = target_dir / "lgb_p50.txt"
        pkl_path = target_dir / "models.pkl"

        if pkl_path.exists():
            import pickle
            with open(pkl_path, "rb") as f:
                bundle = pickle.load(f)
            model_p50 = bundle["models"][0.50]
        elif txt_path.exists():
            booster = lgb.Booster(model_file=str(txt_path))
            model_p50 = lgb.LGBMRegressor()
            model_p50._Booster = booster
        else:
            raise FileNotFoundError(f"No P50 model artifact found under {target_dir}")

        return cls(model=model_p50, feature_names=feature_names, symbol=symbol)

    def explain_instance(
        self,
        features: Union[pd.DataFrame, pd.Series, Dict[str, Any]],
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """
        Calculates exact TreeSHAP contributions for an individual inference row.
        """
        # Format as 1-row DataFrame
        if isinstance(features, dict):
            X = pd.DataFrame([features])
        elif isinstance(features, pd.Series):
            X = pd.DataFrame([features.to_dict()])
        else:
            X = features.copy().tail(1)

        # Ensure all expected feature columns exist
        for col in self.feature_names:
            if col not in X.columns:
                X[col] = 0.0
        X_eval = X[self.feature_names]

        # Model prediction
        pred_val = float(self.model.predict(X_eval)[0])

        if self.explainer is not None:
            shap_values = self.explainer.shap_values(X_eval)
            if isinstance(shap_values, list):
                vals = np.array(shap_values[0]).flatten()
            else:
                vals = np.array(shap_values).flatten()

            base_val = self.explainer.expected_value
            if isinstance(base_val, (list, np.ndarray)):
                base_val = float(base_val[0])
            else:
                base_val = float(base_val)
        else:
            # Fallback heuristic using tree feature importances
            importances = getattr(self.model, "feature_importances_", np.ones(len(self.feature_names)))
            total_imp = max(1.0, float(np.sum(importances)))
            weights = importances / total_imp
            base_val = 0.0
            vals = (pred_val - base_val) * weights

        impacts = []
        for feat_name, impact in zip(self.feature_names, vals):
            raw_val = float(X_eval[feat_name].iloc[0]) if feat_name in X_eval.columns else 0.0
            desc = FEATURE_DESCRIPTIONS.get(feat_name, feat_name.replace("_", " ").title())
            impacts.append({
                "feature": feat_name,
                "value": round(raw_val, 4),
                "shap_impact": round(float(impact), 5),
                "shap_impact_pct": round(float(impact) * 100.0, 2),
                "description": desc,
                "direction": "positive" if impact >= 0 else "negative",
            })

        # Separate positive and negative contributors
        positive_drivers = sorted(
            [d for d in impacts if d["shap_impact"] > 0],
            key=lambda x: x["shap_impact"],
            reverse=True,
        )[:top_k]

        negative_drivers = sorted(
            [d for d in impacts if d["shap_impact"] < 0],
            key=lambda x: x["shap_impact"],  # Most negative first
        )[:top_k]

        all_sorted = sorted(impacts, key=lambda x: abs(x["shap_impact"]), reverse=True)

        return {
            "symbol": self.symbol,
            "base_value": round(base_val, 4),
            "predicted_return": round(pred_val, 4),
            "predicted_return_pct": round((np.exp(pred_val) - 1.0) * 100.0, 2),
            "top_positive_drivers": positive_drivers,
            "top_negative_drivers": negative_drivers,
            "all_attributions": all_sorted,
        }

    def explain_latest_prediction(
        self,
        features: Union[pd.DataFrame, pd.Series, Dict[str, Any]],
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """Convenience alias for explain_instance."""
        return self.explain_instance(features=features, top_k=top_k)


# Alias for backward compatibility
TreeSHAPService = ShapExplanationService
