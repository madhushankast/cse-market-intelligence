"""
Master Daily MLOps Pipeline Execution Script
--------------------------------------------
Executes daily post-market close workflow (15:00 SLST / Mon-Fri):
  Stage 1: Syncs official CSE API feeds (ASPI + 26 equities) into database.
  Stage 2: Queries full expanding history from database and extracts technical features.
  Stage 3: Retrains Multi-Quantile LightGBM models (P10, P50, P90) on expanded history.
  Stage 4: Generates 30-day forecast cone, TreeSHAP attributions, and heuristic signals.
  Stage 5: Persists prediction payloads into `forecast_predictions` table.
  Stage 6: Records full audit execution metrics in `pipeline_runs`.
"""

from __future__ import annotations

import argparse
import datetime
import logging
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional

# Safe console output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from src.database.session import engine, SessionLocal
from src.database.models import StockPrice, ASPIIndex, ForecastPrediction, PipelineRun
from src.ingestion.daily_sync import sync_daily_cse_market, upsert_records_chunked
from src.features.technical_features import TechnicalFeaturePipeline
from src.modeling.train_lightgbm import QuantileLightGBMTrainer
from src.modeling.predict import ForecastPipeline
from src.explainability.shap_service import ShapExplanationService
from src.explainability.heuristics_engine import IndicatorHeuristicsEngine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("daily_pipeline")


def run_daily_pipeline(
    symbols: Optional[List[str]] = None,
    sync_live: bool = True,
    retrain: bool = True,
) -> Dict[str, Any]:
    """
    Executes end-to-end automated daily pipeline.
    """
    overall_start = time.time()
    session = SessionLocal()

    print("\n" + "=" * 90)
    print("      COLOMBO STOCK EXCHANGE (CSE): DAILY MLOPS RETRAINING & FORECAST PIPELINE")
    print(f"      Execution Date: {datetime.date.today()} | Database: {engine.url}")
    print("=" * 90)

    total_ingested = 0
    total_retrained = 0
    predictions_stored = 0

    try:
        # -------------------------------------------------------------
        # STAGE 1: Daily CSE Market Ingestion
        # -------------------------------------------------------------
        if sync_live:
            print("\n[STAGE 1/4] Synchronizing Live CSE Market Data into Database...")
            sync_res = sync_daily_cse_market(session=session)
            total_ingested = sync_res.get("total_records_ingested", 0)
            print(f"    [+] Ingestion Complete: {sync_res['equities_synced']} Equities | {total_ingested} Bars Synced")
            print(f"    [+] ASPI Status: {sync_res['aspi_ok']} (LKR {sync_res['aspi_value']})")
        else:
            print("\n[STAGE 1/4] Skipping live sync (--no-sync flag active). Using existing DB records.")

        # -------------------------------------------------------------
        # Load ASPI Benchmark Index from DB
        # -------------------------------------------------------------
        aspi_rows = session.query(ASPIIndex).order_by(ASPIIndex.date.asc()).all()
        if not aspi_rows:
            raise RuntimeError("No ASPI benchmark records found in database. Run backfill first.")

        aspi_df = pd.DataFrame([{
            "date": pd.to_datetime(r.date),
            "close": float(r.close),
            "high": float(r.high) if r.high else float(r.close),
            "low": float(r.low) if r.low else float(r.close),
        } for r in aspi_rows])

        feature_pipeline = TechnicalFeaturePipeline()
        heuristics_engine = IndicatorHeuristicsEngine()

        # -------------------------------------------------------------
        # Target Equities Selection
        # -------------------------------------------------------------
        if not symbols:
            db_symbols = session.query(StockPrice.symbol).distinct().all()
            symbols = sorted([r[0] for r in db_symbols])

        print(f"\n[STAGE 2/4] Processing Expanding History for {len(symbols)} Equities...")

        models_base_dir = Path("models")
        models_base_dir.mkdir(parents=True, exist_ok=True)

        prediction_records = []

        for idx, sym in enumerate(symbols, 1):
            t0 = time.time()
            clean_sym = sym.replace(".", "_")

            # Query full expanding history from database
            price_rows = (
                session.query(StockPrice)
                .filter(StockPrice.symbol == clean_sym)
                .order_by(StockPrice.date.asc())
                .all()
            )

            if len(price_rows) < 50:
                print(f"    [{idx:02d}/{len(symbols):02d}] ⚠️ {clean_sym:15s}: Insufficient history ({len(price_rows)} rows), skipping.")
                continue

            stock_df = pd.DataFrame([{
                "date": pd.to_datetime(r.date),
                "open": float(r.open),
                "high": float(r.high),
                "low": float(r.low),
                "close": float(r.close),
                "volume": float(r.volume),
            } for r in price_rows])

            # Generate technical features & stationary targets
            df_features = feature_pipeline.transform(stock_df, aspi_df=aspi_df)
            available_features = [c for c in feature_pipeline.feature_columns if c in df_features.columns]

            target_col = "target_return_30d" if "target_return_30d" in df_features.columns else "target_log_return_30d"

            # -------------------------------------------------------------
            # STAGE 3: Incremental / Expanding Retraining
            # -------------------------------------------------------------
            model_dir = models_base_dir / clean_sym

            if retrain or not (model_dir / "models.pkl").exists():
                trainer = QuantileLightGBMTrainer(quantiles=[0.10, 0.50, 0.90])
                models = trainer.fit_final_models(df_features, available_features, target_col=target_col)
                trainer.save_artifacts(model_dir)
                total_retrained += 1
            else:
                trainer = QuantileLightGBMTrainer.load_artifacts(model_dir)
                models = trainer.models

            # -------------------------------------------------------------
            # STAGE 4: Inference & Dual-Layer Explainability
            # -------------------------------------------------------------
            pipeline = ForecastPipeline(models, available_features, horizon_days=30)
            latest_row = df_features.tail(1)
            current_price = float(latest_row["close"].iloc[0])
            last_date = pd.to_datetime(latest_row["date"].iloc[0])

            forecast_res = pipeline.predict_from_features(latest_row, current_price, last_date)

            # TreeSHAP mathematical attribution
            p50_model = models.get(0.50)
            shap_drivers = {}
            if p50_model is not None:
                shap_svc = ShapExplanationService(p50_model, available_features, symbol=clean_sym)
                shap_drivers = shap_svc.explain_instance(latest_row, top_k=5)

            # Indicator heuristics alignment
            p50_log_ret = forecast_res["target_returns"]["p50_log_return"]
            heuristic_cards = heuristics_engine.evaluate_alignment(latest_row, p50_log_ret)

            # Prepare DB record
            prediction_records.append({
                "symbol": clean_sym,
                "as_of_date": last_date.date(),
                "current_price": current_price,
                "price_p10": forecast_res["target_prices"]["price_p10"],
                "price_p50": forecast_res["target_prices"]["price_p50"],
                "price_p90": forecast_res["target_prices"]["price_p90"],
                "expected_pct_change": forecast_res["target_returns"]["expected_pct_change"],
                "target_returns": forecast_res["target_returns"],
                "cone_trajectory": forecast_res["cone_trajectory"],
                "shap_drivers": shap_drivers,
                "heuristic_signals": heuristic_cards,
            })

            elapsed_stock = time.time() - t0
            p50_str = f"LKR {forecast_res['target_prices']['price_p50']:.2f}"
            pct_str = f"{forecast_res['target_returns']['expected_pct_change']:+.2f}%"
            print(f"    [{idx:02d}/{len(symbols):02d}] ✅ {clean_sym:15s}: {len(price_rows)} rows | P50: {p50_str} ({pct_str}) | {elapsed_stock:.1f}s")

        # -------------------------------------------------------------
        # STAGE 5: Persist Predictions into Database
        # -------------------------------------------------------------
        print("\n[STAGE 3/4] Persisting Forecast Predictions into `forecast_predictions`...")
        if prediction_records:
            upsert_records_chunked(
                session,
                ForecastPrediction,
                prediction_records,
                conflict_keys=["symbol", "as_of_date"],
            )
            predictions_stored = len(prediction_records)
            print(f"    [+] Stored {predictions_stored} latest forecast predictions in database.")

        # -------------------------------------------------------------
        # STAGE 6: Record Pipeline Execution Audit Log
        # -------------------------------------------------------------
        print("\n[STAGE 4/4] Recording Execution Audit Log in `pipeline_runs`...")
        total_duration = time.time() - overall_start
        audit_run = PipelineRun(
            run_date=datetime.date.today(),
            job_name="DAILY_RETRAIN_PREDICT_JOB",
            status="SUCCESS",
            records_ingested=total_ingested,
            models_retrained=total_retrained,
            duration_seconds=round(total_duration, 2),
            message=(
                f"Successfully processed {len(symbols)} equities: "
                f"{total_retrained} models retrained, {predictions_stored} predictions generated."
            ),
        )
        session.add(audit_run)
        session.commit()

        print("\n" + "=" * 90)
        print(f"🎉 DAILY MLOPS PIPELINE COMPLETED in {total_duration:.1f}s")
        print(f"   - Models Retrained on Expanding History: {total_retrained}")
        print(f"   - Predictions Generated & Persisted: {predictions_stored}")
        print(f"   - Database Engine: {engine.url}")
        print("=" * 90 + "\n")

        return {
            "status": "success",
            "models_retrained": total_retrained,
            "predictions_stored": predictions_stored,
            "duration_seconds": round(total_duration, 2),
        }

    except Exception as exc:
        session.rollback()
        logger.error("Daily pipeline job failed: %s", exc, exc_info=True)
        # Log failure
        total_duration = time.time() - overall_start
        fail_audit = PipelineRun(
            run_date=datetime.date.today(),
            job_name="DAILY_RETRAIN_PREDICT_JOB",
            status="FAILED",
            records_ingested=total_ingested,
            models_retrained=total_retrained,
            duration_seconds=round(total_duration, 2),
            message=f"Pipeline failed: {str(exc)}",
        )
        session.add(fail_audit)
        session.commit()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run daily market sync, expanding retraining, and forecasting.")
    parser.add_argument("--symbols", nargs="*", default=None, help="Optional subset of symbols to process.")
    parser.add_argument("--no-sync", action="store_true", help="Skip live API sync and use existing DB records.")
    parser.add_argument("--no-retrain", action="store_true", help="Skip model retraining and generate forecasts only.")

    args = parser.parse_args()

    run_daily_pipeline(
        symbols=args.symbols,
        sync_live=not args.no_sync,
        retrain=not args.no_retrain,
    )
