"""
Integration Tests for FastAPI Serving Layer
-------------------------------------------
Verifies REST API endpoints:
  - GET  /health: Liveness, uptime, and model inventory.
  - GET  /api/v1/stocks: Available 26 equities list & latest quotes.
  - POST /api/v1/predict: Multi-quantile forecast cone, TreeSHAP, and heuristics.
  - GET  /api/v1/predict/{symbol}: Convenience GET forecast endpoint.
  - GET  /api/v1/explain/{symbol}: Standalone explainability payload.
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health_endpoint():
    """Verifies server health probe, uptime, and 26-model inventory."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "cse-market-intelligence-api"
    assert data["version"] == "2.0.0"
    assert data["models_count"] == 26
    assert data["available_equities_count"] == 26
    assert "JKH_N0000" in data["available_models"]


def test_root_endpoint():
    """Verifies root endpoint documentation metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "endpoints" in data
    assert "docs_url" in data


def test_stocks_list_endpoint():
    """Verifies /api/v1/stocks returns all 26 CSE equities with quotes."""
    response = client.get("/api/v1/stocks")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert payload["count"] == 26
    stocks = payload["data"]
    assert len(stocks) == 26

    # Verify item schema
    symbols = [s["symbol"] for s in stocks]
    assert "JKH_N0000" in symbols
    assert "COMB_N0000" in symbols
    assert "SAMP_N0000" in symbols

    sample = next(s for s in stocks if s["symbol"] == "JKH_N0000")
    assert "name" in sample
    assert "latest_close" in sample and sample["latest_close"] > 0
    assert "latest_date" in sample


def test_predict_post_endpoint():
    """Verifies POST /api/v1/predict generates forecast cone and explainability."""
    req_body = {
        "symbol": "JKH_N0000",
        "horizon_days": 30,
        "explain": True,
    }
    response = client.post("/api/v1/predict", json=req_body)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "success"
    forecast = res_data["data"]

    # Cone properties
    assert forecast["symbol"] == "JKH_N0000"
    assert forecast["current_price"] > 0
    assert forecast["horizon_days"] == 30
    tp = forecast["target_prices"]
    assert tp["price_p10"] <= tp["price_p50"] <= tp["price_p90"]
    assert len(forecast["cone_trajectory"]) == 30

    # Dual-layer explainability fields
    assert "shap_explanation" in forecast
    shap_info = forecast["shap_explanation"]
    assert "top_positive_drivers" in shap_info
    assert "top_negative_drivers" in shap_info

    assert "indicator_heuristics" in forecast
    heuristics = forecast["indicator_heuristics"]
    assert len(heuristics) >= 4
    for h in heuristics:
        assert h["status"] in {"Supporting", "Rejecting / Risk", "Neutral"}


def test_predict_get_convenience_endpoint():
    """Verifies GET /api/v1/predict/{symbol} convenience endpoint."""
    response = client.get("/api/v1/predict/COMB_N0000?horizon_days=30&explain=true")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "success"
    forecast = res_data["data"]
    assert forecast["symbol"] == "COMB_N0000"
    assert forecast["current_price"] > 0
    assert "target_prices" in forecast


def test_explain_endpoint():
    """Verifies GET /api/v1/explain/{symbol} standalone explainability."""
    response = client.get("/api/v1/explain/SAMP_N0000")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "success"
    assert res_data["symbol"] == "SAMP_N0000"
    assert "predicted_log_return" in res_data
    assert "forecast_direction" in res_data
    assert "shap_explanation" in res_data
    assert "indicator_heuristics" in res_data


def test_predict_not_found():
    """Verifies 404 response on unknown symbol."""
    response = client.get("/api/v1/predict/NONEXISTENT_STOCK")
    assert response.status_code == 404
