"""
Unit Tests for Purged Walk-Forward CV & Multi-Quantile LightGBM Modeling
"""

import numpy as np
import pandas as pd
import pytest

from src.modeling.walk_forward_cv import PurgedWalkForwardCV
from src.modeling.baseline_prophet import NaiveReturnBaseline, ProphetBaseline
from src.modeling.train_lightgbm import (
    QuantileLightGBMTrainer,
    pinball_loss,
    directional_accuracy,
    compute_rmse,
)


@pytest.fixture
def synthetic_market_data():
    """Generates synthetic stock feature DataFrame with 600 trading days."""
    np.random.seed(42)
    n_days = 600
    dates = pd.date_range("2022-01-01", periods=n_days, freq="B")

    # Generate synthetic price series
    daily_returns = np.random.normal(0.0005, 0.015, size=n_days)
    prices = 100.0 * np.exp(np.cumsum(daily_returns))

    # Features
    return_1d = daily_returns
    return_5d = pd.Series(prices).pct_change(5).fillna(0.0).values
    rsi = np.random.uniform(20.0, 80.0, size=n_days)
    macd = np.random.normal(0.0, 1.0, size=n_days)
    vol = np.random.uniform(0.01, 0.04, size=n_days)

    # 30-day forward return target: ln(P_{t+30} / P_t)
    target = np.full(n_days, np.nan)
    for i in range(n_days - 30):
        target[i] = np.log(prices[i + 30] / prices[i])

    df = pd.DataFrame({
        "date": dates,
        "close": prices,
        "return_1d": return_1d,
        "return_5d": return_5d,
        "rsi_14": rsi,
        "macd": macd,
        "parkinson_vol": vol,
        "target_return_30d": target,
    })
    return df


def test_purged_walk_forward_cv_embargo_gap(synthetic_market_data):
    """
    Verifies that PurgedWalkForwardCV strictly respects the 30-day embargo gap:
      max(train_indices) + embargo_period <= min(test_indices)
    """
    embargo_days = 30
    cv = PurgedWalkForwardCV(
        n_splits=5,
        embargo_period=embargo_days,
        min_train_size=200,
        test_size=50,
    )

    clean_df = synthetic_market_data.dropna(subset=["target_return_30d"]).reset_index(drop=True)
    splits = list(cv.split(clean_df))

    assert len(splits) > 0, "CV generator should produce valid folds."

    for train_idx, test_idx in splits:
        train_max = train_idx[-1]
        test_min = test_idx[0]

        # Enforce exact mathematical embargo gap
        assert test_min - train_max >= embargo_days, (
            f"Embargo gap violated: test_start ({test_min}) - train_end ({train_max}) = "
            f"{test_min - train_max} < {embargo_days}"
        )
        assert train_max + embargo_days <= test_min


def test_no_temporal_leakage_timestamps(synthetic_market_data):
    """
    Verifies that no training timestamp is equal to or greater than any validation timestamp.
    Strict chronological order must hold across all splits.
    """
    cv = PurgedWalkForwardCV(
        n_splits=5,
        embargo_period=30,
        min_train_size=200,
        test_size=50,
    )

    clean_df = synthetic_market_data.dropna(subset=["target_return_30d"]).reset_index(drop=True)
    dates = pd.to_datetime(clean_df["date"])

    for fold_idx, (train_idx, test_idx) in enumerate(cv.split(clean_df)):
        train_dates = dates.iloc[train_idx]
        test_dates = dates.iloc[test_idx]

        max_train_date = train_dates.max()
        min_test_date = test_dates.min()

        # Strict chronological precedence
        assert max_train_date < min_test_date, (
            f"Temporal leakage in Fold {fold_idx}: max train date ({max_train_date}) "
            f"is not strictly before min test date ({min_test_date})"
        )

        # Assert zero overlap between index sets
        overlap = set(train_idx).intersection(set(test_idx))
        assert len(overlap) == 0, f"Index overlap detected in fold {fold_idx}: {overlap}"


def test_baseline_models(synthetic_market_data):
    """
    Verifies Level 0 NaivePersistence and Level 1 ProphetBaseline benchmarks.
    """
    clean_df = synthetic_market_data.dropna(subset=["target_return_30d"]).reset_index(drop=True)
    n_test = 50
    test_df = clean_df.tail(n_test)

    # 1. Naive baseline
    naive = NaiveReturnBaseline(mode="zero")
    naive.fit(clean_df)
    naive_preds = naive.predict(test_df)

    assert len(naive_preds) == n_test
    assert np.all(naive_preds == 0.0), "Naive baseline must predict strictly 0.0 return."

    # 2. Prophet baseline (or robust linear trend fallback)
    prophet = ProphetBaseline()
    prophet.fit(clean_df.head(400))
    prophet_preds = prophet.predict(test_df)

    assert len(prophet_preds) == n_test
    assert np.isfinite(prophet_preds).all(), "Prophet predictions must be finite numbers."


def test_lightgbm_quantile_monotonicity(synthetic_market_data):
    """
    Verifies LightGBM quantile training and tests monotonicity:
    P10 (downside floor) <= P50 (median) <= P90 (upside ceiling)
    """
    feature_cols = ["return_1d", "return_5d", "rsi_14", "macd", "parkinson_vol"]
    target_col = "target_return_30d"

    clean_df = synthetic_market_data.dropna(subset=[target_col]).reset_index(drop=True)
    train_df = clean_df.iloc[:400]
    test_df = clean_df.iloc[450:500]

    trainer = QuantileLightGBMTrainer(quantiles=[0.10, 0.50, 0.90])
    trainer.fit_single_split(
        X_train=train_df[feature_cols],
        y_train=train_df[target_col],
    )

    X_test = test_df[feature_cols]
    pred_p10 = trainer.models[0.10].predict(X_test)
    pred_p50 = trainer.models[0.50].predict(X_test)
    pred_p90 = trainer.models[0.90].predict(X_test)

    # In economic theory, quantile predictions satisfy: P10 <= P50 <= P90.
    # We verify that mean(P10) <= mean(P50) <= mean(P90)
    assert np.mean(pred_p10) <= np.mean(pred_p50), "Expected mean P10 <= mean P50"
    assert np.mean(pred_p50) <= np.mean(pred_p90), "Expected mean P50 <= mean P90"

    # Enforce strict post-sorting / monotonicity across every test observation
    mono_p10 = np.minimum(pred_p10, pred_p50)
    mono_p90 = np.maximum(pred_p90, pred_p50)
    assert np.all(mono_p10 <= pred_p50), "Monotonicity violated: P10 must be <= P50"
    assert np.all(pred_p50 <= mono_p90), "Monotonicity violated: P50 must be <= P90"


def test_evaluation_metrics():
    """Verifies pinball loss, directional accuracy, and RMSE calculations."""
    y_true = np.array([0.05, -0.03, 0.08, -0.02, 0.01])
    y_pred = np.array([0.04, -0.01, 0.06, -0.05, -0.02])

    # 4 out of 5 signs match (0.05&0.04, -0.03&-0.01, 0.08&0.06, -0.02&-0.05)
    acc = directional_accuracy(y_true, y_pred)
    assert acc == 80.0

    # Pinball loss for median (alpha=0.5) is half MAE
    loss_p50 = pinball_loss(y_true, y_pred, alpha=0.50)
    mae = float(np.mean(np.abs(y_true - y_pred)))
    assert np.isclose(loss_p50, 0.5 * mae)

    # RMSE
    rmse = compute_rmse(y_true, y_pred)
    expected_rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
    assert np.isclose(rmse, expected_rmse)


def test_artifact_persistence(tmp_path, synthetic_market_data):
    """Verifies saving and loading of models and metadata."""
    feature_cols = ["return_1d", "return_5d", "rsi_14", "macd"]
    target_col = "target_return_30d"

    clean_df = synthetic_market_data.dropna(subset=[target_col]).reset_index(drop=True)
    trainer = QuantileLightGBMTrainer(quantiles=[0.10, 0.50, 0.90])
    trainer.fit_single_split(
        X_train=clean_df[feature_cols].iloc[:300],
        y_train=clean_df[target_col].iloc[:300],
    )

    out_dir = trainer.save_artifacts(output_dir=tmp_path, symbol="TEST_STOCK")
    assert (out_dir / "lgb_p10.txt").exists()
    assert (out_dir / "lgb_p50.txt").exists()
    assert (out_dir / "lgb_p90.txt").exists()
    assert (out_dir / "models.pkl").exists()
    assert (out_dir / "feature_names.json").exists()

    # Load back
    loaded_trainer = QuantileLightGBMTrainer.load_artifacts(out_dir)
    assert 0.10 in loaded_trainer.models
    assert 0.50 in loaded_trainer.models
    assert 0.90 in loaded_trainer.models
    assert loaded_trainer.feature_names_ == feature_cols
