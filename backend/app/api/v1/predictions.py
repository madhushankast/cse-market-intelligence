"""
Prediction API endpoints.

Routes:
    GET /api/v1/predictions/{symbol}
        Full prediction response with best model, forecast series, and metrics.

    GET /api/v1/predictions/{symbol}/compare
        Model comparison table — RMSE, MAE, MAPE, R² per model.

    GET /api/v1/predictions/{symbol}/history
        Last N close prices for charting (historical + forecast overlay).
"""

from fastapi import APIRouter, HTTPException, Query
from app.forecasting.prediction_service import PredictionService
from app.database.connection import SessionLocal
from app.repositories.stock_repository import StockPriceRepository

router = APIRouter()

# Single shared service instance (with in-memory cache per worker process)
_service = PredictionService()


@router.get("/predictions/{symbol}")
def get_predictions(
    symbol: str,
    horizon: int = Query(default=7, ge=1, le=30, description="Forecast horizon in trading days"),
):
    """
    Generate multi-model forecasts for a given stock symbol.

    Returns current price, per-model next-day predictions, the best model's
    7-day forecast series, and evaluation metrics for all models.
    """
    try:
        result = _service.get_predictions(symbol.upper(), horizon=horizon)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Forecasting failed: {str(e)}"
        )


@router.get("/predictions/{symbol}/compare")
def get_model_comparison(symbol: str):
    """
    Return a side-by-side model performance comparison table.

    Useful for the Model Comparison dashboard page.
    """
    try:
        result = _service.get_model_comparison(symbol.upper())
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Model comparison failed: {str(e)}"
        )


@router.get("/predictions/{symbol}/history")
def get_price_history(
    symbol: str,
    n: int = Query(default=60, ge=10, le=500, description="Number of historical data points"),
):
    """
    Return the last `n` close prices for charting the historical baseline
    before the forecast overlay begins.
    """
    db = SessionLocal()
    try:
        repo = StockPriceRepository(db)
        records = repo.get_by_symbol(symbol.upper())

        if not records:
            raise HTTPException(
                status_code=404,
                detail=f"No price data found for {symbol}. Run ingestion first."
            )

        recent = records[-n:]
        history = [
            {"date": r.date.strftime("%Y-%m-%d") if hasattr(r.date, "strftime") else str(r.date),
             "close": float(r.close)}
            for r in recent
        ]
        return {
            "symbol": symbol.upper(),
            "history": history,
            "count": len(history),
        }
    finally:
        db.close()
