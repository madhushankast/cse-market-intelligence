from datetime import date, datetime, timezone
import logging
from typing import Optional

import pandas as pd

from app.database.connection import SessionLocal
from app.forecasting.trainer import ForecastTrainer, TrainingResult
from app.preprocessing.pipeline import ProcessingPipeline
from app.repositories.stock_repository import StockPriceRepository

logger = logging.getLogger(__name__)


class PredictionService:
    """
    Orchestrates data fetching, training, and result formatting.
    """

    def __init__(self):
        self._pipeline = ProcessingPipeline()
        self._trainer = ForecastTrainer()
        # In-memory cache: (symbol, date_str) → TrainingResult
        self._cache: dict[tuple, TrainingResult] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_predictions(self, symbol: str, horizon: int = 30) -> dict:
        """
        Main prediction endpoint response builder.

        Returns a rich dict with current price, per-model predictions,
        best model info, 30-day forecast series, and metrics.
        """
        result = self._get_or_train(symbol, horizon)
        df = self._get_merged_df(symbol)

        current_price = float(df["close"].iloc[-1]) if len(df) > 0 else None
        last_date = df["date"].iloc[-1] if "date" in df.columns else None

        # Build 30-day forecast dates (skip weekends naively)
        forecast_dates = self._trading_dates(last_date, horizon)

        # Per-model prediction trajectory/values
        model_preds = {}
        for model_name, ev in result.evaluations.items():
            vals = result.forecasts.get(model_name, [])
            ints = result.forecast_intervals.get(model_name, []) if hasattr(result, "forecast_intervals") else []
            model_preds[model_name] = {
                "next_day_value": vals[-1] if vals else None,
                "rmse": ev.rmse,
                "mae":  ev.mae,
                "mape": ev.mape,
                "direction_accuracy": ev.direction_accuracy,
                "r2":   ev.r2,
                "confidence": ev.confidence(),
                "confidence_label": ev.confidence_label(),
                "star_rating": ev.star_rating(),
                "warning": ev.warning,
                "intervals": ints,
                "forecast_values": vals,
            }

        best_ev = result.evaluations.get(result.best_model)
        best_forecast = result.best_forecast
        best_intervals = getattr(result, "best_intervals", [])

        return {
            "symbol":             symbol,
            "current_price":      round(current_price, 4) if current_price else None,
            "predictions":        model_preds,
            "best_model":         result.best_model,
            "best_prediction":    round(best_forecast[-1], 6) if best_forecast else None,
            "confidence":         best_ev.confidence() if best_ev else None,
            "confidence_label":   best_ev.confidence_label() if best_ev else "Moderate Confidence",
            "forecast_horizon_days": horizon,
            "forecast_dates":     forecast_dates,
            "forecast_values":    best_forecast,
            "forecast_intervals": best_intervals,
            "data_points_used":   result.n_train + result.n_test,
            "n_features":         result.n_features,
            "trained_at":         datetime.now(timezone.utc).isoformat(),
            "warning":            best_ev.warning if best_ev else None,
            "technical_score":    result.technical_score,
            "technical_confidence": result.technical_confidence,
            "technical_adjustment": result.technical_adjustment,
        }

    def get_model_comparison(self, symbol: str) -> dict:
        """
        Model comparison response builder — used by the /compare endpoint.
        """
        horizon = 30
        result = self._get_or_train(symbol, horizon)

        comparison = []
        for model_name, ev in result.evaluations.items():
            comparison.append({
                "model":              model_name,
                "rmse":               ev.rmse,
                "mae":                ev.mae,
                "mape":               ev.mape,
                "direction_accuracy": ev.direction_accuracy,
                "r2":                 ev.r2,
                "confidence":         ev.confidence(),
                "star_rating":        ev.star_rating(),
                "n_test":             ev.n_test,
                "warning":            ev.warning,
            })

        # Sort by Directional Accuracy descending
        comparison.sort(key=lambda x: x["direction_accuracy"], reverse=True)

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
        Full stock data assembly: DB → preprocessing.
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
        return df_processed

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
        # Use trading calendar utility to skip weekends and holidays
        from app.utils.trading_calendar import add_trading_days
        current_date = pd.Timestamp(last_date)
        while len(dates) < horizon:
            # Add one trading day
            next_date = add_trading_days(current_date.date(), 1)
            dates.append(next_date.strftime("%Y-%m-%d"))
            current_date = pd.Timestamp(next_date)
        return dates

