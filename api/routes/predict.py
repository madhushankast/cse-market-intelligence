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


class PipelineTriggerRequest(BaseModel):
    symbols: Optional[List[str]] = Field(default=None, description="Optional list of symbols to sync/retrain (None = all 26 equities)")
    sync_live: bool = Field(default=True, description="Fetch latest EOD bars from official CSE API")
    retrain: bool = Field(default=False, description="Whether to retrain LightGBM quantile models on expanded history")


@router.get("/pipeline/status", summary="Get Dataset Freshness, Last Updated Dates, and Pipeline Audit Log")
def get_pipeline_status():
    """
    Returns exact data freshness dates (start date, latest updated date, total trading days)
    for ASPI and all 26 CSE equities, plus recent execution audit logs from `pipeline_runs`.
    """
    processed_dir = Path("data/processed")
    models_dir = Path("models")
    meta_map = _load_tickers_metadata()

    # 1. Inspect ASPI benchmark parquet
    aspi_info = {
        "symbol": "ASPI",
        "name": "All Share Price Index (CSE Benchmark)",
        "min_date": None,
        "latest_date": None,
        "total_rows": 0,
        "latest_close": None,
    }
    aspi_path = processed_dir / "ASPI.parquet"
    if aspi_path.exists():
        try:
            aspi_df = pd.read_parquet(aspi_path)
            if not aspi_df.empty:
                dates = pd.to_datetime(aspi_df["date"])
                aspi_info["min_date"] = str(dates.min().date())
                aspi_info["latest_date"] = str(dates.max().date())
                aspi_info["total_rows"] = int(len(aspi_df))
                aspi_info["latest_close"] = round(float(aspi_df["close"].iloc[-1]), 2)
        except Exception as exc:
            logger.warning("Could not inspect ASPI.parquet: %s", exc)

    # 2. Inspect all 26 equities parquets & model artifacts
    equities = []
    total_bars = 0
    trained_models_count = 0
    latest_equity_dates = []

    if processed_dir.exists():
        for pf in sorted(processed_dir.glob("*.parquet")):
            symbol = pf.stem
            if symbol == "ASPI":
                continue
            try:
                df = pd.read_parquet(pf, columns=["date", "close", "volume"])
                if df.empty:
                    continue
                dates = pd.to_datetime(df["date"])
                min_d = str(dates.min().date())
                max_d = str(dates.max().date())
                latest_equity_dates.append(max_d)
                row_count = int(len(df))
                total_bars += row_count

                latest = df.iloc[-1]
                meta = meta_map.get(symbol, {})
                model_exists = (models_dir / symbol / "models.pkl").exists()
                if model_exists:
                    trained_models_count += 1

                equities.append({
                    "symbol": symbol,
                    "code": meta.get("code", symbol.split("_")[0]),
                    "name": meta.get("name", symbol.split("_")[0] + " PLC"),
                    "sector": meta.get("sector", "Equities"),
                    "min_date": min_d,
                    "latest_date": max_d,
                    "total_rows": row_count,
                    "latest_close": round(float(latest["close"]), 2),
                    "latest_volume": int(latest["volume"]),
                    "model_trained": model_exists,
                })
            except Exception as exc:
                logger.warning("Could not inspect parquet for %s: %s", symbol, exc)

    # 3. Query database row counts & recent pipeline runs
    recent_runs = []
    db_engine_label = "SQLite Local"
    db_stock_count = 0
    db_aspi_count = 0
    db_predictions_count = 0
    try:
        from sqlalchemy import func
        from src.database.session import Base, engine, SessionLocal
        from src.database.models import PipelineRun, StockPrice, ASPIIndex, ForecastPrediction

        if engine.dialect.name == "postgresql":
            db_engine_label = "Supabase PostgreSQL"
        Base.metadata.create_all(bind=engine)
        session = SessionLocal()
        try:
            db_stock_count = int(session.query(func.count(StockPrice.symbol)).scalar() or 0)
            db_aspi_count = int(session.query(func.count(ASPIIndex.date)).scalar() or 0)
            db_predictions_count = int(session.query(func.count(ForecastPrediction.id)).scalar() or 0)

            # Merge DB latest dates & counts so ephemeral containers reflect live Supabase DB state
            db_sym_stats = {
                row[0]: {"min_date": str(row[1]), "latest_date": str(row[2]), "total_rows": int(row[3])}
                for row in session.query(
                    StockPrice.symbol,
                    func.min(StockPrice.date),
                    func.max(StockPrice.date),
                    func.count(StockPrice.date),
                )
                .group_by(StockPrice.symbol)
                .all()
            }
            for eq in equities:
                st = db_sym_stats.get(eq["symbol"])
                if st:
                    if not eq["latest_date"] or st["latest_date"] > eq["latest_date"]:
                        eq["latest_date"] = st["latest_date"]
                    if st["total_rows"] > eq["total_rows"]:
                        eq["total_rows"] = st["total_rows"]

            latest_equity_dates = [eq["latest_date"] for eq in equities if eq.get("latest_date")]

            rows = (
                session.query(PipelineRun)
                .order_by(PipelineRun.id.desc())
                .limit(10)
                .all()
            )
            recent_runs = [
                {
                    "id": r.id,
                    "run_date": str(r.run_date),
                    "job_name": r.job_name,
                    "status": r.status,
                    "records_ingested": int(r.records_ingested or 0),
                    "models_retrained": int(r.models_retrained or 0),
                    "duration_seconds": float(r.duration_seconds or 0.0),
                    "message": (r.message or "")[:240],
                    "created_at": str(r.created_at) if r.created_at else str(r.run_date),
                }
                for r in rows
            ]
        finally:
            session.close()
    except Exception as exc:
        logger.warning("Could not query pipeline_runs: %s", exc)

    max_equity_date = max(latest_equity_dates) if latest_equity_dates else None
    min_equity_date = min(latest_equity_dates) if latest_equity_dates else None

    return {
        "status": "success",
        "data": {
            "summary": {
                "total_equities": len(equities),
                "trained_models_count": trained_models_count,
                "total_bars": max(total_bars + int(aspi_info["total_rows"] or 0), db_stock_count + db_aspi_count),
                "latest_market_date": aspi_info["latest_date"] or max_equity_date,
                "latest_equity_date": max_equity_date,
                "oldest_equity_date": min_equity_date,
                "database_engine": db_engine_label,
                "db_stock_bars": db_stock_count,
                "db_aspi_bars": db_aspi_count,
                "db_predictions_count": db_predictions_count,
            },
            "aspi": aspi_info,
            "equities": equities,
            "recent_runs": recent_runs,
        },
    }


@router.post("/pipeline/trigger", summary="Trigger Automated Ingestion, Retraining, and Prediction")
def trigger_daily_pipeline(
    request: Optional[PipelineTriggerRequest] = None,
    symbols: Optional[List[str]] = Query(default=None),
    sync_live: bool = Query(default=True),
    retrain: bool = Query(default=False),
):
    """
    Manually triggers the daily ingestion, optional model retraining, and forecast generation job,
    then clears the in-memory ModelRegistryService cache so updated dates and prices take effect immediately.
    """
    from scripts.daily_pipeline_job import run_daily_pipeline

    target_symbols = request.symbols if (request and request.symbols) else symbols
    do_sync = request.sync_live if request is not None else sync_live
    do_retrain = request.retrain if request is not None else retrain

    try:
        res = run_daily_pipeline(
            symbols=target_symbols,
            sync_live=do_sync,
            retrain=do_retrain,
        )
        registry_service.clear_cache()
        return {
            "status": "success",
            "message": "Pipeline execution completed and model cache refreshed.",
            "result": res,
        }
    except Exception as exc:
        logger.error("Pipeline trigger error: %s", exc)
        raise HTTPException(status_code=500, detail=f"Pipeline trigger failed: {str(exc)}")


