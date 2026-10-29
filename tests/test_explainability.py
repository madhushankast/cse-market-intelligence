"""
Unit Tests for Dual-Layer Explainability Engine (TreeSHAP + Domain Indicator Heuristics)
"""

import numpy as np
import pandas as pd
import pytest
import lightgbm as lgb

from src.explainability.shap_service import ShapExplanationService
from src.explainability.heuristics_engine import IndicatorHeuristicsEngine
from src.modeling.predict import ModelRegistryService, ForecastPipeline


@pytest.fixture
def trained_lgbm_model_and_features():
    """Generates synthetic dataset and fits a LightGBM regressor for TreeSHAP tests."""
    np.random.seed(42)
    n = 200
    feature_cols = [
        "return_1d", "return_5d", "return_30d", "rsi_14", "macd",
        "sma_ratio_20_50", "parkinson_vol_20d", "aspi_return_30d",
    ]
    X = pd.DataFrame(np.random.normal(0, 1, size=(n, len(feature_cols))), columns=feature_cols)
    X["rsi_14"] = np.random.uniform(25, 75, size=n)
    X["sma_ratio_20_50"] = np.random.uniform(0.9, 1.1, size=n)
    X["parkinson_vol_20d"] = np.random.uniform(0.1, 0.4, size=n)

    # Synthetic return target
    y = 0.4 * X["return_5d"] - 0.3 * X["parkinson_vol_20d"] + 0.2 * (X["rsi_14"] - 50) / 20.0

    model = lgb.LGBMRegressor(n_estimators=30, learning_rate=0.05, verbose=-1, random_state=42)
    model.fit(X, y)

    return model, feature_cols, X


def test_shap_exact_additivity(trained_lgbm_model_and_features):
    """
    Verifies the fundamental Local Accuracy / Efficiency property of Shapley values:
      prediction = base_value + sum(shap_values)
    """
    model, feature_cols, X = trained_lgbm_model_and_features
    service = ShapExplanationService(model=model, feature_names=feature_cols, symbol="TEST_STOCK")

    sample_row = X.iloc[-1:]
    explanation = service.explain_instance(sample_row, top_k=5)

    base_val = explanation["base_value"]
    pred_val = explanation["predicted_return"]
    all_attribs = explanation["all_attributions"]

    # Sum of all Shapley values across all features
    shap_sum = sum(item["shap_impact"] for item in all_attribs)

    # Local accuracy property verification within floating point tolerance
    assert np.isclose(base_val + shap_sum, pred_val, atol=1e-3), (
        f"TreeSHAP efficiency violated: base ({base_val}) + sum ({shap_sum}) != pred ({pred_val})"
    )


def test_shap_positive_and_negative_drivers(trained_lgbm_model_and_features):
    """
    Verifies that top positive and negative drivers are strictly partitioned and sorted.
    """
    model, feature_cols, X = trained_lgbm_model_and_features
    service = ShapExplanationService(model=model, feature_names=feature_cols, symbol="TEST_STOCK")

    sample_row = X.iloc[-1:]
    explanation = service.explain_instance(sample_row, top_k=3)

    for pos in explanation["top_positive_drivers"]:
        assert pos["shap_impact"] > 0, "Top positive driver must have positive impact."
        assert "description" in pos and len(pos["description"]) > 0

    for neg in explanation["top_negative_drivers"]:
        assert neg["shap_impact"] < 0, "Top negative driver must have negative impact."
        assert "description" in neg and len(neg["description"]) > 0


def test_heuristics_engine_boundary_cases():
    """
    Verifies boundary technical states against bullish and bearish return projections.
    """
    engine = IndicatorHeuristicsEngine()

    # Case 1: Bullish prediction with healthy RSI (48.0) -> Supporting
    bullish_row = {
        "rsi_14": 48.0,
        "sma_ratio_20_50": 1.05,
        "parkinson_vol_20d": 0.22,
        "aspi_return_30d": 0.04,
        "macd_hist": 0.35,
        "volume_surge_ratio": 1.8,
    }
    cards = engine.evaluate_alignment(bullish_row, predicted_return_p50=0.06)
    rsi_card = next(c for c in cards if c["indicator"] == "RSI (14)")
    assert rsi_card["status"] == "Supporting"
    assert rsi_card["signal"] == "Bullish"

    sma_card = next(c for c in cards if c["indicator"] == "SMA 20/50 Trend")
    assert sma_card["status"] == "Supporting"

    # Case 2: Bullish prediction with overbought RSI (82.0) -> Rejecting / Risk
    overbought_row = bullish_row.copy()
    overbought_row["rsi_14"] = 82.0
    cards_ob = engine.evaluate_alignment(overbought_row, predicted_return_p50=0.06)
    rsi_ob_card = next(c for c in cards_ob if c["indicator"] == "RSI (14)")
    assert rsi_ob_card["status"] == "Rejecting / Risk"
    assert rsi_ob_card["signal"] == "Bearish"

    # Case 3: Bearish prediction with oversold RSI (24.0) -> Rejecting / Risk (Divergence / Bounce potential)
    oversold_row = bullish_row.copy()
    oversold_row["rsi_14"] = 24.0
    cards_os = engine.evaluate_alignment(oversold_row, predicted_return_p50=-0.08)
    rsi_os_card = next(c for c in cards_os if c["indicator"] == "RSI (14)")
    assert rsi_os_card["status"] == "Rejecting / Risk"

    # Case 4: High volatility (Parkinson = 48%) on bullish forecast -> Rejecting / Risk
    high_vol_row = bullish_row.copy()
    high_vol_row["parkinson_vol_20d"] = 0.48
    cards_vol = engine.evaluate_alignment(high_vol_row, predicted_return_p50=0.05)
    vol_card = next(c for c in cards_vol if "Parkinson" in c["indicator"])
    assert vol_card["status"] == "Rejecting / Risk"

    # Ensure all cards adhere strictly to canonical status taxonomy
    allowed_statuses = {"Supporting", "Rejecting / Risk", "Neutral"}
    for card in cards:
        assert card["status"] in allowed_statuses
        assert "indicator" in card
        assert "value" in card
        assert "explanation" in card


def test_unified_prediction_payload_schema():
    """
    Verifies that ModelRegistryService creates the complete payload schema
    with forecast cone, TreeSHAP attributions, and indicator heuristic cards.
    """
    service = ModelRegistryService(
        raw_dir="data/raw",
        processed_dir="data/processed",
        models_dir="models",
    )

    # Use JKH_N0000 which was serialized in Phase 3
    payload = service.predict("JKH_N0000", horizon_days=30, explain=True)

    # Root keys
    assert payload["symbol"] == "JKH_N0000"
    assert "current_price" in payload and payload["current_price"] > 0
    assert payload["horizon_days"] == 30
    assert "target_returns" in payload
    assert "target_prices" in payload
    assert "cone_trajectory" in payload
    assert "shap_explanation" in payload
    assert "indicator_heuristics" in payload

    # Target prices monotonicity
    tp = payload["target_prices"]
    assert tp["price_p10"] <= tp["price_p50"] <= tp["price_p90"], "Target prices must satisfy P10 <= P50 <= P90."

    # SHAP explanation structure
    shap_info = payload["shap_explanation"]
    assert "base_value" in shap_info
    assert "predicted_return" in shap_info
    assert isinstance(shap_info["top_positive_drivers"], list)
    assert isinstance(shap_info["top_negative_drivers"], list)

    # Indicator heuristics structure
    heuristics = payload["indicator_heuristics"]
    assert isinstance(heuristics, list)
    assert len(heuristics) >= 4
    for h in heuristics:
        assert "indicator" in h
        assert "status" in h
        assert "explanation" in h
