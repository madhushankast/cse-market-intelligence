"""
Prediction Route Handler
------------------------
Endpoints:
  - GET  /api/v1/stocks: Available CSE stock tickers & latest market quotes.
  - POST /api/v1/predict: 30-day forecast cone (P10, P50, P90), SHAP, & heuristics.
  - GET  /api/v1/predict/{symbol}: Convenience GET forecast endpoint.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
import pandas as pd
import yaml

from src.modeling.predict import ModelRegistryService

logger = logging.getLogger(__name__)

router = APIRouter()
registry_service = ModelRegistryService()


class PredictionRequest(BaseModel):
    symbol: str = Field(..., description="CSE stock symbol (e.g. 'JKH_N0000', 'COMB_N0000', 'JKH')")
    horizon_days: int = Field(default=30, ge=5, le=90, description="Forecast horizon in trading days")
    explain: bool = Field(default=True, description="Whether to include TreeSHAP and heuristic explainability")


def _load_tickers_metadata() -> Dict[str, Dict[str, Any]]:
    """Loads tickers.yaml metadata mapping if available."""
    tickers_path = Path("configs/tickers.yaml")
    meta_map = {}
    if tickers_path.exists():
        try:
            with open(tickers_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                for item in data.get("tickers", []):
                    sym = item.get("symbol", "")
                    clean_sym = sym.replace(".", "_")
                    code = item.get("code", sym.split(".")[0])
                    meta_map[clean_sym] = item
                    meta_map[sym] = item
                    meta_map[code] = item
        except Exception as exc:
            logger.warning("Could not parse configs/tickers.yaml: %s", exc)
    return meta_map


@router.get("/stocks", summary="List Available CSE Equities")
def list_available_stocks():
    """
    Returns list of all 26 processed CSE equities with latest close price, date, and metadata.
    """
    processed_dir = Path("data/processed")
    if not processed_dir.exists():
        raise HTTPException(status_code=500, detail="Processed data directory not found.")

    parquet_files = sorted(processed_dir.glob("*.parquet"))
    meta_map = _load_tickers_metadata()
    stocks = []

    for pf in parquet_files:
        symbol = pf.stem
        if symbol == "ASPI":
            continue

        try:
            df = pd.read_parquet(pf, columns=["date", "close", "volume"])
            if df.empty:
                continue
            latest = df.iloc[-1]
            date_val = str(pd.to_datetime(latest["date"]).date())

            meta = meta_map.get(symbol, {})
            name = meta.get("name", symbol.split("_")[0] + " PLC")
            code = meta.get("code", symbol.split("_")[0])
            sector = meta.get("sector", "Equities")

            stocks.append({
                "symbol": symbol,
                "code": code,
                "name": name,
                "sector": sector,
                "latest_close": round(float(latest["close"]), 2),
                "latest_date": date_val,
                "latest_volume": int(latest["volume"]),
            })
        except Exception as exc:
            logger.warning("Could not read parquet for %s: %s", symbol, exc)

    return {
        "status": "success",
        "count": len(stocks),
        "data": stocks,
    }


@router.post("/predict", summary="Generate Multi-Quantile Forecast (POST)")
def predict_stock_post(request: PredictionRequest):
    """
    Generate 30-day ahead multi-quantile forecast cone (P10, P50, P90),
    TreeSHAP feature attributions, and domain indicator heuristic cards.
    """
    try:
        forecast = registry_service.predict(
            symbol=request.symbol,
            horizon_days=request.horizon_days,
            explain=request.explain,
        )
        return {
            "status": "success",
            "data": forecast,
        }
    except FileNotFoundError as fnf:
        raise HTTPException(status_code=404, detail=str(fnf))
    except Exception as exc:
        logger.error("Prediction error for %s: %s", request.symbol, exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(exc)}")


@router.get("/predict/{symbol}", summary="Generate Multi-Quantile Forecast (GET)")
def predict_stock_get(
    symbol: str,
    horizon_days: int = Query(default=30, ge=5, le=90, description="Forecast horizon in trading days"),
    explain: bool = Query(default=True, description="Whether to include TreeSHAP and heuristic explainability"),
):
    """
    Convenience GET endpoint to generate 30-day forecast cone and explainability for a symbol.
    """
    try:
        forecast = registry_service.predict(
            symbol=symbol,
            horizon_days=horizon_days,
            explain=explain,
        )
        return {
            "status": "success",
            "data": forecast,
        }
    except FileNotFoundError as fnf:
        raise HTTPException(status_code=404, detail=str(fnf))
    except Exception as exc:
        logger.error("Prediction error for %s: %s", symbol, exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(exc)}")


@router.get("/benchmarks", summary="Get Purged Walk-Forward Cross-Validation Benchmarks")
def get_benchmarks_summary():
    """
    Returns empirical cross-validation metrics across all 26 equities comparing
    Multi-Quantile LightGBM against Naive and Prophet baselines.
    """
    report_file = Path("reports/cv_benchmark_summary.csv")
    if not report_file.exists():
        raise HTTPException(status_code=404, detail="Benchmark summary report not found.")

    try:
        df = pd.read_csv(report_file)
        records = df.to_dict(orient="records")
        return {
            "status": "success",
            "count": len(records),
            "data": records,
        }
    except Exception as exc:
        logger.error("Error reading benchmark report: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to load benchmark report.")


@router.get("/predictions/history/{symbol}", summary="Get Historical Predictions for Symbol")
def get_prediction_history(symbol: str, limit: int = 30):
    """
    Returns historical 30-day ahead forecasts stored in the database for the given equity.
    """
    from src.database.session import SessionLocal
    from src.database.models import ForecastPrediction

    clean_sym = symbol.replace(".", "_")
    session = SessionLocal()
    try:
        rows = (
            session.query(ForecastPrediction)
            .filter(ForecastPrediction.symbol == clean_sym)
            .order_by(ForecastPrediction.as_of_date.desc())
            .limit(limit)
            .all()
        )
        data = [
            {
                "id": r.id,
                "symbol": r.symbol,
                "as_of_date": str(r.as_of_date),
                "current_price": float(r.current_price),
                "price_p10": float(r.price_p10),
                "price_p50": float(r.price_p50),
                "price_p90": float(r.price_p90),
                "expected_pct_change": float(r.expected_pct_change),
                "created_at": str(r.created_at) if r.created_at else None,
            }
            for r in rows
        ]
        return {
            "status": "success",
            "symbol": clean_sym,
            "count": len(data),
            "data": data,
        }
    except Exception as exc:
        logger.error("Error querying prediction history for %s: %s", symbol, exc)
        raise HTTPException(status_code=500, detail="Failed to fetch prediction history.")
    finally:
        session.close()


@router.post("/pipeline/trigger", summary="Trigger Automated Ingestion, Retraining, and Prediction")
def trigger_daily_pipeline(
    symbols: Optional[List[str]] = Query(default=None),
    sync_live: bool = Query(default=True),
    retrain: bool = Query(default=False),
):
    """
    Manually triggers the daily ingestion, expanding model retraining, and forecast generation job.
    """
    from scripts.daily_pipeline_job import run_daily_pipeline

    try:
        res = run_daily_pipeline(
            symbols=symbols,
            sync_live=sync_live,
            retrain=retrain,
        )
        return {
            "status": "success",
            "message": "Pipeline execution triggered successfully",
            "result": res,
        }
    except Exception as exc:
        logger.error("Pipeline trigger error: %s", exc)
        raise HTTPException(status_code=500, detail=f"Pipeline trigger failed: {str(exc)}")


