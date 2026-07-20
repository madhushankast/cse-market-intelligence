from fastapi import APIRouter, HTTPException, Query
from app.forecasting.prediction_service import PredictionService

router = APIRouter()
_service = PredictionService()


@router.get(
    "/forecast/{symbol}",
    summary="Get 7-day ahead forecast for a stock symbol"
)
def get_forecast(
    symbol: str,
    horizon: int = Query(default=7, ge=1, le=30, description="Forecast horizon in trading days"),
    model: str = Query(default=None, description="Specify model: 'sarimax', 'xgboost', 'baseline'")
):
    """
    Returns next 7 days forecast prices, dates, confidence intervals, and metrics.
    Supports model override query parameter (e.g. ?model=xgboost).
    """
    try:
        res = _service.get_predictions(symbol.upper(), horizon=horizon)
        
        best_model = res.get("best_model", "unknown")
        selected_model = model.lower() if model and model.lower() in ["sarimax", "xgboost", "baseline"] else best_model
        
        selected_metrics = res.get("predictions", {}).get(selected_model, {})
        
        forecast_dates = res.get("forecast_dates", [])
        
        # If the selected model is the best model, use the pre-resolved best forecast arrays
        if selected_model == best_model:
            forecast_values = res.get("forecast_values", [])
            forecast_intervals = res.get("forecast_intervals", [])
        else:
            forecast_values = selected_metrics.get("forecast_values", [])
            forecast_intervals = selected_metrics.get("intervals", [])
            
        forecast_list = []
        for i, d in enumerate(forecast_dates):
            v = forecast_values[i] if i < len(forecast_values) else 0.0
            interval = forecast_intervals[i] if i < len(forecast_intervals) else (v, v)
            forecast_list.append({
                "date": d,
                "price": round(float(v), 2),
                "lower": round(float(interval[0]), 2),
                "upper": round(float(interval[1]), 2)
            })
        
        return {
            "symbol": symbol.upper(),
            "model": selected_model.upper(),
            "horizon": horizon,
            "forecast": forecast_list,
            "metrics": {
                "MAE": round(float(selected_metrics.get("mae", 0.0)), 4),
                "RMSE": round(float(selected_metrics.get("rmse", 0.0)), 4),
                "Accuracy": round(float(selected_metrics.get("direction_accuracy", 0.0)) * 100, 2)
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate forecast: {str(e)}"
        )


@router.post("/forecast/cache/clear", summary="Clear prediction cache to force model retraining")
def clear_forecast_cache():
    _service._cache.clear()
    return {"status": "ok", "message": "Forecast model cache cleared."}

