"""
PredictionService — high-level facade used by the API layer.

Responsibilities:
    1. Fetch stock data from the repository
    2. Run macro + trends integration (reusing the existing merger)
    3. Pass the merged DataFrame to ForecastTrainer
    4. Cache results per (symbol, date) to avoid re-training on every request
    5. Format and return structured response dicts ready for JSON serialization

Cache strategy:
    - Simple in-memory dict keyed by (symbol, training_date)
    - Cleared automatically when the date changes (i.e. each trading day)
    - Suitable for a single-process API server; replace with Redis for multi-worker
"""

import logging
from datetime import date, datetime, timezone
from typing import Optional

import pandas as pd

from app.database.connection import SessionLocal
from app.repositories.stock_repository import StockPriceRepository
from app.preprocessing.pipeline import ProcessingPipeline
from app.data_sources.cbsl.service import CBSLService
from app.data_sources.trends.service import TrendsService
from app.integration.merger import DataMerger
from app.forecasting.trainer import ForecastTrainer, TrainingResult

logger = logging.getLogger(__name__)


class PredictionService:
    """
    Orchestrates data fetching, merging, training, and result formatting.
    Thread-safety note: the cache dict is not locked — acceptable for
    single-worker Uvicorn. Add a threading.Lock for multi-threaded workers.
    """

    def __init__(self):
        self._pipeline    = ProcessingPipeline()
        self._cbsl        = CBSLService()
        self._trends      = TrendsService()
        self._merger      = DataMerger()
        self._trainer     = ForecastTrainer()
        # In-memory cache: (symbol, date_str) → TrainingResult
        self._cache: dict[tuple, TrainingResult] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_predictions(self, symbol: str, horizon: int = 7) -> dict:
        """
        Main prediction endpoint response builder.

        Returns a rich dict with current price, per-model predictions,
        best model info, 7-day forecast series, and metrics.
        """
        result = self._get_or_train(symbol, horizon)
        df = self._get_merged_df(symbol)

        current_price = float(df["close"].iloc[-1]) if len(df) > 0 else None
        last_date = df["date"].iloc[-1] if "date" in df.columns else None

        # Build 7-day forecast dates (skip weekends naively)
        forecast_dates = self._trading_dates(last_date, horizon)

        # Per-model next-day prediction
        model_preds = {}
        for model_name, ev in result.evaluations.items():
            vals = result.forecasts.get(model_name, [])
            model_preds[model_name] = {
                "next_day_value": vals[0] if vals else None,
                "rmse": ev.rmse,
                "mae":  ev.mae,
                "mape": ev.mape,
                "r2":   ev.r2,
                "confidence": ev.confidence(),
                "star_rating": ev.star_rating(),
                "warning": ev.warning,
            }

        best_ev = result.evaluations.get(result.best_model)
        best_forecast = result.best_forecast

        return {
            "symbol":             symbol,
            "current_price":      round(current_price, 4) if current_price else None,
            "predictions":        model_preds,
            "best_model":         result.best_model,
            "best_prediction":    round(best_forecast[0], 4) if best_forecast else None,
            "confidence":         best_ev.confidence() if best_ev else None,
            "forecast_horizon_days": horizon,
            "forecast_dates":     forecast_dates,
            "forecast_values":    best_forecast,
            "data_points_used":   result.n_train + result.n_test,
            "n_features":         result.n_features,
            "trained_at":         datetime.now(timezone.utc).isoformat(),
            "warning":            best_ev.warning if best_ev else None,
        }

    def get_model_comparison(self, symbol: str) -> dict:
        """
        Model comparison response builder — used by the /compare endpoint.
        """
        horizon = 7
        result = self._get_or_train(symbol, horizon)

        comparison = []
        for model_name, ev in result.evaluations.items():
            comparison.append({
                "model":        model_name,
                "rmse":         ev.rmse,
                "mae":          ev.mae,
                "mape":         ev.mape,
                "r2":           ev.r2,
                "confidence":   ev.confidence(),
                "star_rating":  ev.star_rating(),
                "n_test":       ev.n_test,
                "warning":      ev.warning,
            })

        # Sort by MAPE ascending (best first)
        comparison.sort(key=lambda x: x["mape"])

        return {
            "symbol":              symbol,
            "best_model":          result.best_model,
            "comparison":          comparison,
            "feature_importances": result.feature_importances,
            "n_train":             result.n_train,
            "n_test":              result.n_test,
            "evaluated_at":        datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_or_train(self, symbol: str, horizon: int) -> TrainingResult:
        """Return cached TrainingResult or trigger a fresh training run."""
        cache_key = (symbol, date.today().isoformat())
        if cache_key in self._cache:
            logger.info(f"Cache hit for {symbol} on {date.today().isoformat()}")
            return self._cache[cache_key]

        logger.info(f"Training forecasting models for {symbol}...")
        df = self._get_merged_df(symbol)
        result = self._trainer.run(df, horizon=horizon)

        self._cache[cache_key] = result
        return result

    def _get_merged_df(self, symbol: str) -> pd.DataFrame:
        """
        Full data assembly: DB → preprocessing → macro → trends → merge.
        Mirrors the logic in analytics.py but returns the full DataFrame.
        """
        db = SessionLocal()
        try:
            repo = StockPriceRepository(db)
            records = repo.get_by_symbol(symbol)

            if not records:
                raise ValueError(f"No stock data found in DB for symbol '{symbol}'. "
                                 "Run ingestion first via POST /stocks/{symbol}/ingest")

            raw = [{
                "symbol": r.symbol,
                "date":   r.date,
                "open":   r.open,
                "high":   r.high,
                "low":    r.low,
                "close":  r.close,
                "volume": r.volume,
            } for r in records]

            df_stock = pd.DataFrame(raw)
        finally:
            db.close()

        # Technical indicators
        df_processed = self._pipeline.process(df_stock)

        # Macro + trends (best-effort — failures return empty DataFrames)
        try:
            df_macro = self._cbsl.get_macro_indicators()
        except Exception as e:
            logger.warning(f"CBSL fetch failed: {e} — proceeding without macro data")
            df_macro = pd.DataFrame(columns=["date", "inflation", "usd_lkr", "interest_rate"])

        try:
            df_trends = self._trends.get_search_trends("CSE")
        except Exception as e:
            logger.warning(f"Trends fetch failed: {e} — proceeding without trend data")
            df_trends = pd.DataFrame(columns=["date", "trend_score"])

        # Merge
        df_merged = self._merger.merge(df_processed, df_macro, df_trends)
        return df_merged

    @staticmethod
    def _trading_dates(last_date, horizon: int) -> list[str]:
        """Generate `horizon` approximate future trading dates (Mon–Fri)."""
        if last_date is None:
            return []
        try:
            current = pd.Timestamp(last_date)
        except Exception:
            return []

        dates = []
        while len(dates) < horizon:
            current += pd.Timedelta(days=1)
            if current.dayofweek < 5:   # Mon=0 … Fri=4
                dates.append(current.strftime("%Y-%m-%d"))
        return dates
