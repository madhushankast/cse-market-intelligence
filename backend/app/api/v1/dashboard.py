from fastapi import APIRouter, HTTPException
import pandas as pd
from app.database.connection import SessionLocal
from app.repositories.stock_repository import StockPriceRepository
from app.repositories.job_log_repository import JobLogRepository
from app.forecasting.prediction_service import PredictionService

router = APIRouter()
_pred = PredictionService()


@router.get(
    "/dashboard",
    summary="Get aggregated research dashboard statistics"
)
def get_dashboard():
    db = SessionLocal()
    try:
        stock_repo = StockPriceRepository(db)
        job_repo = JobLogRepository(db)

        # 1. Pipeline Status
        last_pipeline_status, last_pipeline_time = job_repo.get_last_pipeline_status()
        last_update = stock_repo.get_last_updated_date()
        total_records = stock_repo.get_total_count()
        unique_stocks = stock_repo.get_unique_symbols_count()

        pipeline_health = "healthy"
        if last_pipeline_status == "Failed":
            pipeline_health = "unhealthy"

        # 2. Economic Indicators (Removed in updated scope)
        economic_data = {}


        # 3. Top Stocks Latest Closes
        top_symbols = ["COMB", "JKH", "SAMP"]
        stocks_info = []
        for sym in top_symbols:
            try:
                records = stock_repo.get_by_symbol(sym)
                if records:
                    latest_rec = records[-1]
                    prev_close = records[-2].close if len(records) > 1 else latest_rec.close
                    change = ((latest_rec.close - prev_close) / prev_close) * 100
                    stocks_info.append({
                        "symbol": sym,
                        "close": round(float(latest_rec.close), 2),
                        "change_pct": round(float(change), 2),
                        "volume": int(latest_rec.volume)
                    })
            except Exception:
                pass

        # 4. Forecast Summary (Benchmark Stock: COMB)
        forecast_info = None
        try:
            fc = _pred.get_predictions("COMB", horizon=30)
            forecast_info = {
                "symbol": "COMB",
                "prediction": round(float(fc.get("best_prediction", 0.0)), 2),
                "model": fc.get("best_model", "baseline").upper(),
                "confidence": fc.get("confidence", 0.5)
            }
        except Exception:
            pass

        return {
            "market": {
                "total_records": total_records,
                "unique_symbols": unique_stocks,
                "stocks": stocks_info,
                "aspi_benchmark": 13152.40,  # Approx. CSE ASPI as of mid-2025 (estimated)
                "aspi_change": 0.32,
                "aspi_note": "Estimated — real-time ASPI requires CSE live data feed"
            },
            "economic": economic_data,
            "forecast": forecast_info,
            "pipeline": {
                "last_update": last_update,
                "status": pipeline_health,
                "last_run": last_pipeline_time.strftime("%Y-%m-%d %H:%M:%S") if last_pipeline_time else "N/A"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard aggregation failed: {str(e)}")
    finally:
        db.close()
