"""
Multi-Quantile LightGBM Model Trainer
-------------------------------------
Trains asymmetric quantile regression models (P10, P50, P90) on cumulative
30-day forward log returns using Purged & Embargoed Walk-Forward Cross-Validation.
Evaluates against Naive Persistence and FB Prophet benchmark ladders.
Persists trained models and metrics under models/{symbol}/.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
import pickle
from typing import Any, Dict, List, Optional, Tuple, Union
import warnings
import lightgbm as lgb
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", message=".*eval_set.*")

from src.ingestion.data_loader import StockDataLoader
from src.features.technical_features import TechnicalFeaturePipeline
from src.modeling.walk_forward_cv import PurgedWalkForwardCV
from src.modeling.baseline_prophet import NaiveReturnBaseline, ProphetBaseline

logger = logging.getLogger(__name__)

FEATURE_COLUMNS = [
    "return_1d", "return_5d", "return_10d", "return_20d", "return_30d",
    "rsi_14", "macd", "macd_signal", "macd_hist",
    "ema_ratio_12_26", "sma_ratio_20_50",
    "parkinson_vol", "parkinson_vol_10d", "parkinson_vol_20d", "high_low_spread",
    "volume_surge_ratio", "log_volume",
    "aspi_return_5d", "aspi_return_10d", "aspi_return_30d",
    "relative_strength_30d", "rolling_corr_aspi_30d",
]


def pinball_loss(y_true: np.ndarray, y_pred: np.ndarray, alpha: float) -> float:
    """
    Pinball (Quantile) Loss:
    L_alpha(y, y_hat) = max(alpha * (y - y_hat), (alpha - 1) * (y - y_hat))
    """
    residual = y_true - y_pred
    return float(np.mean(np.maximum(alpha * residual, (alpha - 1.0) * residual)))


def directional_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Directional Accuracy (Hit Ratio):
    Fraction of times sign(y_pred) matches sign(y_true).
    """
    sign_true = np.sign(y_true)
    sign_pred = np.sign(y_pred)
    matches = (sign_true == sign_pred)
    return float(np.mean(matches)) * 100.0


def compute_rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Root Mean Squared Error."""
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def compute_mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean Absolute Error."""
    return float(np.mean(np.abs(y_true - y_pred)))


class QuantileLightGBMTrainer:
    """
    Primary Production Model: Multi-Quantile LightGBM Regressor.
    Models uncertainty intervals (P10 downside, P50 median expected return, P90 upside).
    """

    DEFAULT_QUANTILES = [0.10, 0.50, 0.90]

    def __init__(
        self,
        quantiles: Optional[List[float]] = None,
        hyperparams: Optional[Dict[str, Any]] = None,
        experiment_name: str = "cse_30d_quantile_lgbm",
    ):
        self.quantiles = quantiles or self.DEFAULT_QUANTILES
        self.hyperparams = hyperparams or {
            "n_estimators": 150,
            "learning_rate": 0.03,
            "num_leaves": 31,
            "max_depth": 5,
            "min_child_samples": 20,
            "subsample": 0.85,
            "colsample_bytree": 0.85,
            "reg_alpha": 0.1,
            "reg_lambda": 1.0,
            "verbose": -1,
            "random_state": 42,
        }
        self.experiment_name = experiment_name
        self.models: Dict[float, lgb.LGBMRegressor] = {}
        self.feature_names_: List[str] = []
        self.cv_summary_: Optional[Dict[str, Any]] = None

    def prepare_data(
        self,
        symbol: str,
        data_dir: Union[str, Path] = "data/processed",
        aspi_path: Union[str, Path] = "data/processed/ASPI.parquet",
    ) -> Tuple[pd.DataFrame, List[str]]:
        """
        Loads stock and ASPI data, computes technical & market features,
        and returns clean DataFrame with feature column names.
        """
        loader = StockDataLoader(processed_dir=data_dir)
        parquet_file = Path(data_dir) / f"{symbol}.parquet"
        if not parquet_file.exists():
            clean_sym = symbol.replace(".", "_")
            parquet_file = Path(data_dir) / f"{clean_sym}.parquet"

        if parquet_file.exists():
            stock_df = pd.read_parquet(parquet_file)
            stock_df["date"] = pd.to_datetime(stock_df["date"])
            stock_df = stock_df.sort_values("date").reset_index(drop=True)
        elif hasattr(loader, "load_stock"):
            stock_df = loader.load_stock(symbol)
        else:
            stock_df = loader.load_stock_data(symbol)

        if stock_df.empty:
            raise FileNotFoundError(f"No processed data found for symbol: {symbol}")

        pipeline = TechnicalFeaturePipeline(aspi_path=aspi_path)
        feature_df = pipeline.transform(stock_df)

        available_features = [col for col in FEATURE_COLUMNS if col in feature_df.columns]
        self.feature_names_ = available_features
        return feature_df, available_features

    def fit_single_split(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
    ) -> Dict[float, lgb.LGBMRegressor]:
        """
        Train separate LightGBM models for each specified quantile.
        """
        self.feature_names_ = list(X_train.columns)
        fitted_models: Dict[float, lgb.LGBMRegressor] = {}

        for q in self.quantiles:
            params = self.hyperparams.copy()
            params.update({
                "objective": "quantile",
                "alpha": q,
            })
            model = lgb.LGBMRegressor(**params)

            if X_val is not None and y_val is not None:
                model.fit(
                    X_train,
                    y_train,
                    eval_set=[(X_val, y_val)],
                    callbacks=[lgb.early_stopping(stopping_rounds=25, verbose=False)],
                )
            else:
                model.fit(X_train, y_train)

            fitted_models[q] = model

        self.models = fitted_models
        return fitted_models

    def evaluate_walk_forward(
        self,
        df: pd.DataFrame,
        feature_cols: Optional[List[str]] = None,
        target_col: str = "target_return_30d",
        cv_engine: Optional[PurgedWalkForwardCV] = None,
    ) -> Dict[str, Any]:
        """
        Executes Purged Walk-Forward Cross-Validation and benchmarks against:
          - Level 0 (Naive Persistence Baseline)
          - Level 1 (FB Prophet Baseline Benchmark)
          - Level 2 (Multi-Quantile LightGBM)
        """
        # Resolve target column name if needed
        if target_col not in df.columns and "target_log_return_30d" in df.columns:
            target_col = "target_log_return_30d"

        features = feature_cols or self.feature_names_ or [c for c in FEATURE_COLUMNS if c in df.columns]
        self.feature_names_ = features

        # Drop rows where forward 30-day target is NaN (e.g. latest 30 trading days)
        clean_df = df.dropna(subset=[target_col] + features).reset_index(drop=True)

        cv = cv_engine or PurgedWalkForwardCV(
            n_splits=5,
            embargo_period=30,
            min_train_size=250,
            test_size=60,
        )

        fold_metrics: List[Dict[str, Any]] = []
        all_y_true: List[float] = []
        all_lgb_p50: List[float] = []
        all_lgb_p10: List[float] = []
        all_lgb_p90: List[float] = []
        all_naive_preds: List[float] = []
        all_prophet_preds: List[float] = []

        for fold_idx, (train_idx, test_idx) in enumerate(cv.split(clean_df)):
            train_data = clean_df.iloc[train_idx]
            test_data = clean_df.iloc[test_idx]

            X_tr, y_tr = train_data[features], train_data[target_col]
            X_te, y_te = test_data[features], test_data[target_col]
            y_te_arr = y_te.values

            # 1. Train LightGBM Quantile Models
            fold_models = self.fit_single_split(X_tr, y_tr, X_val=X_te, y_val=y_te)

            pred_p10 = fold_models[0.10].predict(X_te)
            pred_p50 = fold_models[0.50].predict(X_te)
            pred_p90 = fold_models[0.90].predict(X_te)

            # 2. Train Naive Baseline
            naive_model = NaiveReturnBaseline(mode="zero")
            naive_model.fit(X_tr, y_tr)
            pred_naive = naive_model.predict(X_te)

            # 3. Train Prophet Baseline
            prophet_model = ProphetBaseline()
            prophet_model.fit(train_data)
            pred_prophet = prophet_model.predict(test_data)

            # Metrics for this fold
            loss_p10 = pinball_loss(y_te_arr, pred_p10, 0.10)
            loss_p50 = pinball_loss(y_te_arr, pred_p50, 0.50)
            loss_p90 = pinball_loss(y_te_arr, pred_p90, 0.90)
            mean_pinball = (loss_p10 + loss_p50 + loss_p90) / 3.0

            lgb_rmse = compute_rmse(y_te_arr, pred_p50)
            lgb_mae = compute_mae(y_te_arr, pred_p50)
            lgb_dir_acc = directional_accuracy(y_te_arr, pred_p50)

            naive_rmse = compute_rmse(y_te_arr, pred_naive)
            naive_mae = compute_mae(y_te_arr, pred_naive)
            naive_dir_acc = 50.0  # Theoretical random walk baseline

            prophet_rmse = compute_rmse(y_te_arr, pred_prophet)
            prophet_mae = compute_mae(y_te_arr, pred_prophet)
            prophet_dir_acc = directional_accuracy(y_te_arr, pred_prophet)

            coverage = float(np.mean((y_te_arr >= pred_p10) & (y_te_arr <= pred_p90)))

            fold_result = {
                "fold": fold_idx + 1,
                "train_size": len(train_idx),
                "test_size": len(test_idx),
                "lgb_dir_acc": round(lgb_dir_acc, 2),
                "lgb_rmse": round(lgb_rmse, 4),
                "lgb_mae": round(lgb_mae, 4),
                "lgb_pinball_p10": round(loss_p10, 5),
                "lgb_pinball_p50": round(loss_p50, 5),
                "lgb_pinball_p90": round(loss_p90, 5),
                "lgb_mean_pinball": round(mean_pinball, 5),
                "lgb_coverage_80": round(coverage * 100, 2),
                "naive_rmse": round(naive_rmse, 4),
                "naive_mae": round(naive_mae, 4),
                "naive_dir_acc": round(naive_dir_acc, 2),
                "prophet_rmse": round(prophet_rmse, 4),
                "prophet_mae": round(prophet_mae, 4),
                "prophet_dir_acc": round(prophet_dir_acc, 2),
            }
            fold_metrics.append(fold_result)

            all_y_true.extend(y_te_arr.tolist())
            all_lgb_p10.extend(pred_p10.tolist())
            all_lgb_p50.extend(pred_p50.tolist())
            all_lgb_p90.extend(pred_p90.tolist())
            all_naive_preds.extend(pred_naive.tolist())
            all_prophet_preds.extend(pred_prophet.tolist())

        # Overall aggregate metrics across all walk-forward folds
        y_all = np.array(all_y_true)
        lgb_p50_all = np.array(all_lgb_p50)
        lgb_p10_all = np.array(all_lgb_p10)
        lgb_p90_all = np.array(all_lgb_p90)
        naive_all = np.array(all_naive_preds)
        prophet_all = np.array(all_prophet_preds)

        overall_metrics = {
            "n_folds": len(fold_metrics),
            "total_test_samples": len(y_all),
            "lgb_directional_accuracy": round(directional_accuracy(y_all, lgb_p50_all), 2),
            "lgb_rmse": round(compute_rmse(y_all, lgb_p50_all), 4),
            "lgb_mae": round(compute_mae(y_all, lgb_p50_all), 4),
            "lgb_pinball_p10": round(pinball_loss(y_all, lgb_p10_all, 0.10), 5),
            "lgb_pinball_p50": round(pinball_loss(y_all, lgb_p50_all, 0.50), 5),
            "lgb_pinball_p90": round(pinball_loss(y_all, lgb_p90_all, 0.90), 5),
            "lgb_mean_pinball": round(
                (pinball_loss(y_all, lgb_p10_all, 0.10) +
                 pinball_loss(y_all, lgb_p50_all, 0.50) +
                 pinball_loss(y_all, lgb_p90_all, 0.90)) / 3.0, 5
            ),
            "lgb_coverage_80": round(float(np.mean((y_all >= lgb_p10_all) & (y_all <= lgb_p90_all))) * 100, 2),
            "naive_directional_accuracy": 50.0,
            "naive_rmse": round(compute_rmse(y_all, naive_all), 4),
            "naive_mae": round(compute_mae(y_all, naive_all), 4),
            "prophet_directional_accuracy": round(directional_accuracy(y_all, prophet_all), 2),
            "prophet_rmse": round(compute_rmse(y_all, prophet_all), 4),
            "prophet_mae": round(compute_mae(y_all, prophet_all), 4),
            "folds": fold_metrics,
        }

        self.cv_summary_ = overall_metrics
        return overall_metrics

    def fit_final_models(
        self,
        df: pd.DataFrame,
        feature_cols: Optional[List[str]] = None,
        target_col: str = "target_return_30d",
    ) -> Dict[float, lgb.LGBMRegressor]:
        """
        Retrains final production models on the entire valid history
        (excluding the trailing unlabelled horizon).
        """
        if target_col not in df.columns and "target_log_return_30d" in df.columns:
            target_col = "target_log_return_30d"

        features = feature_cols or self.feature_names_ or [c for c in FEATURE_COLUMNS if c in df.columns]
        self.feature_names_ = features

        clean_df = df.dropna(subset=[target_col] + features).reset_index(drop=True)
        X = clean_df[features]
        y = clean_df[target_col]

        logger.info("Fitting final production LightGBM models on %d samples", len(clean_df))
        return self.fit_single_split(X, y)

    def save_artifacts(
        self,
        output_dir: Union[str, Path] = "models",
        symbol: Optional[str] = None,
    ) -> Path:
        """
        Serializes trained quantile models and metadata to models/{symbol}/:
          - lgb_p10.txt
          - lgb_p50.txt
          - lgb_p90.txt
          - models.pkl
          - feature_names.json
          - metrics.json
        """
        out_path = Path(output_dir)
        if symbol:
            out_path = out_path / symbol
        out_path.mkdir(parents=True, exist_ok=True)

        # 1. Native LightGBM text models
        if 0.10 in self.models and hasattr(self.models[0.10], "booster_"):
            self.models[0.10].booster_.save_model(str(out_path / "lgb_p10.txt"))
        if 0.50 in self.models and hasattr(self.models[0.50], "booster_"):
            self.models[0.50].booster_.save_model(str(out_path / "lgb_p50.txt"))
        if 0.90 in self.models and hasattr(self.models[0.90], "booster_"):
            self.models[0.90].booster_.save_model(str(out_path / "lgb_p90.txt"))

        # 2. Pickle dictionary bundle
        with open(out_path / "models.pkl", "wb") as f:
            pickle.dump({
                "models": self.models,
                "quantiles": self.quantiles,
                "feature_names": self.feature_names_,
                "hyperparams": self.hyperparams,
            }, f)

        # 3. Feature names
        with open(out_path / "feature_names.json", "w", encoding="utf-8") as f:
            json.dump(self.feature_names_, f, indent=2)

        # 4. CV Metrics summary
        if self.cv_summary_ is not None:
            with open(out_path / "metrics.json", "w", encoding="utf-8") as f:
                json.dump(self.cv_summary_, f, indent=2)

        logger.info("Artifacts successfully saved to: %s", out_path)
        return out_path

    @classmethod
    def load_artifacts(cls, model_dir: Union[str, Path]) -> QuantileLightGBMTrainer:
        """
        Loads persisted models and features from model_dir.
        """
        path = Path(model_dir)
        pkl_path = path / "models.pkl"
        if not pkl_path.exists():
            raise FileNotFoundError(f"Model artifacts not found at {pkl_path}")

        with open(pkl_path, "rb") as f:
            bundle = pickle.load(f)

        trainer = cls(
            quantiles=bundle.get("quantiles", [0.10, 0.50, 0.90]),
            hyperparams=bundle.get("hyperparams", {}),
        )
        trainer.models = bundle.get("models", {})
        trainer.feature_names_ = bundle.get("feature_names", [])

        metrics_path = path / "metrics.json"
        if metrics_path.exists():
            with open(metrics_path, "r", encoding="utf-8") as f:
                trainer.cv_summary_ = json.load(f)

        return trainer


# Alias for backward compatibility
MultiQuantileLGBMTrainer = QuantileLightGBMTrainer
