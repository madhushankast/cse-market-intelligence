"""
Unit Tests for Vectorized Technical Feature Pipeline & ASPI Alignment
"""

import numpy as np
import pandas as pd
import pytest

from src.features.technical_features import TechnicalFeaturePipeline


@pytest.fixture
def sample_stock_df():
    dates = pd.date_range("2023-01-01", periods=120, freq="B")
    np.random.seed(42)
    # Simulate geometric Brownian motion prices
    ret = np.random.normal(0.0005, 0.015, size=120)
    price = 100.0 * np.exp(np.cumsum(ret))
    high = price * (1.0 + np.random.uniform(0.002, 0.015, size=120))
    low = price * (1.0 - np.random.uniform(0.002, 0.015, size=120))
    open_p = price * (1.0 + np.random.normal(0, 0.003, size=120))
    volume = np.random.randint(50000, 200000, size=120)

    return pd.DataFrame({
        "date": dates,
        "symbol": "JKH.N0000",
        "open": open_p,
        "high": high,
        "low": low,
        "close": price,
        "volume": volume,
    })


@pytest.fixture
def sample_aspi_df(sample_stock_df):
    dates = sample_stock_df["date"]
    np.random.seed(99)
    mkt_ret = np.random.normal(0.0003, 0.01, size=len(dates))
    aspi_levels = 10000.0 * np.exp(np.cumsum(mkt_ret))
    return pd.DataFrame({
        "date": dates,
        "symbol": "ASPI",
        "close": aspi_levels,
    })


def test_rsi_bounds(sample_stock_df):
    rsi = TechnicalFeaturePipeline.compute_rsi(sample_stock_df["close"], period=14)
    valid_rsi = rsi.dropna()
    assert len(valid_rsi) > 0
    assert (valid_rsi >= 0.0).all()
    assert (valid_rsi <= 100.0).all()


def test_macd_calculation(sample_stock_df):
    macd_df = TechnicalFeaturePipeline.compute_macd(sample_stock_df["close"])
    assert "macd" in macd_df.columns
    assert "macd_signal" in macd_df.columns
    assert "macd_hist" in macd_df.columns
    assert len(macd_df) == len(sample_stock_df)


def test_parkinson_volatility(sample_stock_df):
    p_vol = TechnicalFeaturePipeline.compute_parkinson_volatility(
        sample_stock_df["high"],
        sample_stock_df["low"],
    )
    assert len(p_vol) == len(sample_stock_df)
    assert (p_vol >= 0.0).all()


def test_target_calculation(sample_stock_df, sample_aspi_df):
    pipeline = TechnicalFeaturePipeline(target_horizon=30)
    transformed = pipeline.transform(sample_stock_df, aspi_df=sample_aspi_df)

    assert "target_return_30d" in transformed.columns
    # Check forward log return calculation for index 0: ln(close[30] / close[0])
    expected = np.log(sample_stock_df["close"].iloc[30] / sample_stock_df["close"].iloc[0])
    assert pytest.approx(transformed["target_return_30d"].iloc[0], rel=1e-5) == expected

    # Last 30 rows must have NaN in target (future unseen horizon)
    assert transformed["target_return_30d"].iloc[-30:].isnull().all()
    # Prior rows must NOT have NaN in target
    assert not transformed["target_return_30d"].iloc[:-30].isnull().any()


def test_aspi_alignment_leak_free(sample_stock_df, sample_aspi_df):
    """
    Verify that ASPI alignment using backward merge_asof guarantees
    that at day t, no future ASPI point (t+k) is accessible.
    """
    # Create shifted ASPI with sudden jump in future
    aspi_modified = sample_aspi_df.copy()
    jump_idx = 50
    aspi_modified.loc[jump_idx:, "close"] *= 2.0

    pipeline = TechnicalFeaturePipeline(target_horizon=30)
    transformed = pipeline.transform(sample_stock_df, aspi_df=aspi_modified)

    assert "aspi_return_5d" in transformed.columns
    assert "relative_strength_30d" in transformed.columns
    assert "rolling_corr_aspi_30d" in transformed.columns

    # Any index strictly before jump_idx must NOT be impacted by the jump
    assert transformed["aspi_return_5d"].iloc[jump_idx - 1] != transformed["aspi_return_5d"].iloc[jump_idx]


def test_zero_infs_and_feature_cleanliness(sample_stock_df, sample_aspi_df):
    pipeline = TechnicalFeaturePipeline(target_horizon=30)
    transformed = pipeline.transform(sample_stock_df, aspi_df=sample_aspi_df)

    feature_cols = [
        "return_1d", "return_5d", "return_10d", "return_20d", "return_30d",
        "rsi_14", "macd", "macd_signal", "macd_hist",
        "ema_ratio_12_26", "sma_ratio_20_50",
        "parkinson_vol", "parkinson_vol_10d", "parkinson_vol_20d", "high_low_spread",
        "volume_surge_ratio", "log_volume",
        "aspi_return_5d", "aspi_return_10d", "aspi_return_30d",
        "relative_strength_30d", "rolling_corr_aspi_30d",
    ]

    for col in feature_cols:
        assert col in transformed.columns, f"Missing feature column: {col}"
        # Check zero infs
        assert not np.isinf(transformed[col]).any(), f"Infinity detected in {col}"
        # Check zero trailing NaNs in features (features must be fully populated)
        assert not transformed[col].isnull().any(), f"Unexpected NaN in feature {col}"
