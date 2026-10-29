"""
Explainability Route Handler
----------------------------
Endpoint: GET /api/v1/explain/{symbol}
Provides standalone dual-layer explainability:
  1. TreeSHAP mathematical feature attributions (positive & negative drivers).
  2. Rule-based retail investor heuristic badges ('Supporting' vs 'Rejecting / Risk').
"""

from __future__ import annotations

import logging
from fastapi import APIRouter, HTTPException, Query

from src.modeling.predict import ModelRegistryService

logger = logging.getLogger(__name__)

router = APIRouter()
registry_service = ModelRegistryService()


@router.get("/explain/{symbol}", summary="Retrieve Standalone Model Explainability")
def explain_stock_forecast(
    symbol: str,
    horizon_days: int = Query(default=30, ge=5, le=90, description="Forecast horizon in trading days"),
):
    """
    Retrieve TreeSHAP feature drivers and domain indicator validation cards
    for the latest 30-day forecast of the specified CSE stock symbol.
    """
    try:
        forecast = registry_service.predict(
            symbol=symbol,
            horizon_days=horizon_days,
            explain=True,
        )

        p50_ret = forecast["target_returns"]["p50_log_return"]
        direction = "bullish" if p50_ret > 0 else "bearish"

        return {
            "status": "success",
            "symbol": forecast["symbol"],
            "as_of_date": forecast["as_of_date"],
            "current_price": forecast["current_price"],
            "predicted_log_return": p50_ret,
            "expected_pct_change": forecast["target_returns"]["expected_pct_change"],
            "forecast_direction": direction,
            "target_prices": forecast["target_prices"],
            "shap_explanation": forecast.get("shap_explanation", {}),
            "indicator_heuristics": forecast.get("indicator_heuristics", []),
        }
    except FileNotFoundError as fnf:
        raise HTTPException(status_code=404, detail=str(fnf))
    except Exception as exc:
        logger.error("Explainability error for %s: %s", symbol, exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Explainability error: {str(exc)}")
