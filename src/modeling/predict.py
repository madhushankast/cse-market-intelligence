"""
Inference Pipeline & Forecast Cone Generator (OHLCV + ASPI Market Benchmark)
----------------------------------------------------------------------------
Produces multi-quantile 30-day price forecast trajectories (P10, P50, P90)
from trained LightGBM models, and bundles TreeSHAP attributions and domain
indicator heuristic validation cards into a unified investor-ready payload.
"""

from __future__ import annotations

import datetime
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
import lightgbm as lgb

from src.ingestion.data_loader import StockDataLoader
from src.features.technical_features import TechnicalFeaturePipeline
from src.modeling.train_lightgbm import QuantileLightGBMTrainer, MultiQuantileLGBMTrainer
from src.explainability.shap_service import ShapExplanationService
from src.explainability.heuristics_engine import IndicatorHeuristicsEngine

logger = logging.getLogger(__name__)

# Strictly Technical & ASPI Market Relative Features
FEATURE_COLUMNS = [
    "return_1d", "return_5d", "return_10d", "return_20d", "return_30d",
    "rsi_14", "macd", "macd_signal", "macd_hist",
    "ema_ratio_12_26", "sma_ratio_20_50",
    "parkinson_vol", "parkinson_vol_10d", "parkinson_vol_20d", "high_low_spread",
    "volume_surge_ratio", "log_volume",
    "aspi_return_5d", "aspi_return_10d", "aspi_return_30d",
    "relative_strength_30d", "rolling_corr_aspi_30d",
]


class ForecastPipeline:
    """
    Translates trained multi-quantile models into an operational 30-day forecast cone.
    """

    def __init__(
        self,
        models: Dict[float, lgb.LGBMRegressor],
        feature_names: List[str],
        horizon_days: int = 30,
    ):
        self.models = models
        self.feature_names = feature_names
        self.horizon_days = horizon_days

    def predict_from_features(
        self,
        latest_features: pd.DataFrame,
        current_price: float,
        last_date: Optional[pd.Timestamp] = None,
    ) -> Dict[str, Any]:
        """
        Generate 30-day quantile forecast cone from the latest technical feature row.
        
        Mathematical transformation:
          P_{t+h, q} = P_t * exp( r_q * (h / horizon) )
        """
        if latest_features.empty:
            raise ValueError("Empty feature DataFrame provided for prediction.")

        infer_df = latest_features.copy()
        for col in self.feature_names:
            if col not in infer_df.columns:
                infer_df[col] = 0.0

        X_infer = infer_df[self.feature_names].tail(1)

        # Predict cumulative 30-day log return for each quantile
        predicted_returns: Dict[float, float] = {}
        for q, model in self.models.items():
            pred = float(model.predict(X_infer)[0])
            predicted_returns[q] = pred

        # Enforce monotonicity: P10 <= P50 <= P90
        p50_ret = predicted_returns.get(0.5, 0.0)
        p10_ret = min(predicted_returns.get(0.1, -0.05), p50_ret)
        p90_ret = max(predicted_returns.get(0.9, 0.05), p50_ret)

        start_date = pd.to_datetime(last_date) if last_date is not None else pd.Timestamp.now()

        # Build trading-day trajectory dates (weekdays)
        future_dates: List[pd.Timestamp] = []
        curr = start_date
        while len(future_dates) < self.horizon_days:
            curr += pd.Timedelta(days=1)
            if curr.weekday() < 5:  # Mon-Fri
                future_dates.append(curr)

        # Generate trajectory points across the 30-day horizon
        trajectory = []
        for step_idx, f_date in enumerate(future_dates):
            h = step_idx + 1
            fraction = h / self.horizon_days

            price_p10 = current_price * np.exp(p10_ret * fraction)
            price_p50 = current_price * np.exp(p50_ret * fraction)
            price_p90 = current_price * np.exp(p90_ret * fraction)

            trajectory.append({
                "step": h,
                "date": str(f_date.date()),
                "price_p10": round(float(price_p10), 2),
                "price_p50": round(float(price_p50), 2),
                "price_p90": round(float(price_p90), 2),
            })

        target_p10_price = round(float(current_price * np.exp(p10_ret)), 2)
        target_p50_price = round(float(current_price * np.exp(p50_ret)), 2)
        target_p90_price = round(float(current_price * np.exp(p90_ret)), 2)

        return {
            "current_price": round(float(current_price), 2),
            "as_of_date": str(start_date.date()),
            "horizon_days": self.horizon_days,
            "target_returns": {
                "p10_log_return": round(p10_ret, 4),
                "p50_log_return": round(p50_ret, 4),
                "p90_log_return": round(p90_ret, 4),
                "expected_pct_change": round((np.exp(p50_ret) - 1.0) * 100, 2),
            },
            "target_prices": {
                "price_p10": target_p10_price,
                "price_p50": target_p50_price,
                "price_p90": target_p90_price,
            },
            "cone_trajectory": trajectory,
        }


class ModelRegistryService:
    """
    Singleton-style orchestrator to load historical OHLCV data, compute technical features,
    retrieve trained multi-quantile models from disk, compute TreeSHAP attributions,
    and generate unified explainable forecast payloads.
    """

    _cache: Dict[str, Any] = {}

    def __init__(
        self,
        raw_dir: str = "data/raw",
        processed_dir: str = "data/processed",
        models_dir: str = "models",
    ):
        self.loader = StockDataLoader(raw_dir=raw_dir, processed_dir=processed_dir)
        self.feature_engine = TechnicalFeaturePipeline(target_horizon=30)
        self.models_dir = Path(models_dir)
        self.heuristics_engine = IndicatorHeuristicsEngine()

    def get_processed_data(self, symbol: str) -> pd.DataFrame:
        """
        Loads raw historical stock data and engineers technical OHLCV features.
        """
        cache_key = f"data_{symbol}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        stock_df = self.loader.load_stock_data(symbol, use_parquet_cache=True)
        if stock_df.empty:
            raise FileNotFoundError(f"No historical price data found for symbol '{symbol}'.")

        feat_df = self.feature_engine.transform(stock_df)
        self._cache[cache_key] = feat_df
        return feat_df

    def get_or_train_models(
        self,
        symbol: str,
    ) -> Tuple[Dict[float, lgb.LGBMRegressor], List[str], pd.DataFrame]:
        """
        Retrieves serialized models from models/{symbol}/ or trains on the fly.
        """
        cache_key = f"models_{symbol}"
        df = self.get_processed_data(symbol)
        available_features = [col for col in FEATURE_COLUMNS if col in df.columns]

        if cache_key in self._cache:
            models, feat_names = self._cache[cache_key]
            return models, feat_names, df

        # Check for serialized models on disk
        clean_name = symbol.replace(".", "_")
        symbol_dir = self.models_dir / clean_name
        if not symbol_dir.exists():
            symbol_dir = self.models_dir / symbol

        if symbol_dir.exists() and (symbol_dir / "models.pkl").exists():
            logger.info("Loading persisted LightGBM quantile models for %s from %s", symbol, symbol_dir)
            trainer = QuantileLightGBMTrainer.load_artifacts(symbol_dir)
            self._cache[cache_key] = (trainer.models, trainer.feature_names_)
            return trainer.models, trainer.feature_names_, df

        # Otherwise train final models on the fly
        logger.info("Training on-the-fly Multi-Quantile LightGBM models for %s...", symbol)
        trainer = QuantileLightGBMTrainer(quantiles=[0.10, 0.50, 0.90])
        target_col = "target_return_30d" if "target_return_30d" in df.columns else "target_log_return_30d"
        models = trainer.fit_final_models(df, available_features, target_col=target_col)
        self._cache[cache_key] = (models, available_features)
        return models, available_features, df

    def predict(
        self,
        symbol: str,
        horizon_days: int = 30,
        explain: bool = True,
    ) -> Dict[str, Any]:
        """
        End-to-end prediction execution:
          1. 30-day quantile forecast cone (P10, P50, P90)
          2. Mathematical feature attributions via TreeSHAP
          3. Institutional indicator heuristic validation cards
        """
        models, feature_names, df = self.get_or_train_models(symbol)
        pipeline = ForecastPipeline(models, feature_names, horizon_days=horizon_days)

        latest_row = df.tail(1)
        current_price = float(latest_row["close"].iloc[0])
        last_date = pd.to_datetime(latest_row["date"].iloc[0])

        result = pipeline.predict_from_features(latest_row, current_price, last_date)
        result["symbol"] = symbol

        if explain:
            # 1. TreeSHAP Feature Attributions
            p50_model = models.get(0.50)
            if p50_model is not None:
                shap_svc = ShapExplanationService(p50_model, feature_names, symbol=symbol)
                shap_out = shap_svc.explain_instance(latest_row, top_k=5)
                result["shap_explanation"] = {
                    "base_value": shap_out["base_value"],
                    "predicted_return": shap_out["predicted_return"],
                    "top_positive_drivers": shap_out["top_positive_drivers"],
                    "top_negative_drivers": shap_out["top_negative_drivers"],
                }

            # 2. Domain Indicator Heuristics Validation
            p50_return = result["target_returns"]["p50_log_return"]
            heuristic_cards = self.heuristics_engine.evaluate_alignment(latest_row, p50_return)
            result["indicator_heuristics"] = heuristic_cards

        # Include recent historical series for charting (last 90 sessions)
        hist_df = df.tail(90)
        result["historical_series"] = [
            {
                "date": str(pd.to_datetime(r["date"]).date()),
                "open": round(float(r["open"]), 2) if "open" in r and pd.notnull(r["open"]) else round(float(r["close"]), 2),
                "high": round(float(r["high"]), 2) if "high" in r and pd.notnull(r["high"]) else round(float(r["close"]), 2),
                "low": round(float(r["low"]), 2) if "low" in r and pd.notnull(r["low"]) else round(float(r["close"]), 2),
                "close": round(float(r["close"]), 2),
                "volume": int(r["volume"]) if "volume" in r and pd.notnull(r["volume"]) else 0,
            }
            for _, r in hist_df.iterrows()
        ]

        return result


# Aliases for backward compatibility
PredictService = ModelRegistryService
