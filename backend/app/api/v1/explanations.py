"""
Explanation API Router.

Exposes the explainability module endpoints to the web frontend.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.explainability.explanation_service import ExplanationService
from app.explainability.schemas import PredictionExplanation

router = APIRouter()
_service = ExplanationService()


@router.get(
    "/predictions/{symbol}/explanation",
    response_model=PredictionExplanation,
    summary="Explain a stock price prediction using AI model explainers",
    description="Returns SHAP values for XGBoost, parameter coefficients for SARIMAX, and permutation importance as fallback."
)
def get_explanation(
    symbol: str,
    horizon: int = Query(default=7, ge=1, le=30, description="Forecast horizon"),
    model: Optional[str] = Query(default=None, description="Specify model: 'xgboost', 'sarimax', 'baseline'"),
    include_viz: bool = Query(default=True, description="Whether to compute Recharts-compatible chart data"),
):
    try:
        result = _service.explain_prediction(
            symbol=symbol,
            horizon=horizon,
            model_override=model,
            include_viz=include_viz
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate explanation: {str(e)}")
