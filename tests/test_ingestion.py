"""
Unit Tests for Stock Data Ingestion, Scraping, and Standardization
"""

import pandas as pd
import pytest

from src.ingestion.cse_scraper import CSEScraper
from src.ingestion.data_loader import StockDataLoader


def test_symbol_normalization():
    assert CSEScraper.normalize_symbol("JKH") == "JKH.N0000"
    assert CSEScraper.normalize_symbol("COMB.N0000") == "COMB.N0000"
    assert CSEScraper.normalize_symbol("  samp.n0000  ") == "SAMP.N0000"
    assert StockDataLoader.extract_base_code("JKH.N0000") == "JKH"


def test_chart_data_parser():
    scraper = CSEScraper()
    raw_points = [
        {"t": 1672531200000, "o": 140.0, "h": 142.5, "l": 139.0, "p": 141.0, "q": 15000},
        {"t": 1672617600000, "o": 141.0, "h": 143.0, "l": 140.5, "p": 142.5, "q": 22000},
    ]
    df = scraper.parse_chart_data("JKH", raw_points)

    assert len(df) == 2
    assert "date" in df.columns
    assert "symbol" in df.columns
    assert df["symbol"].iloc[0] == "JKH.N0000"
    assert df["close"].iloc[0] == 141.0
    assert df["volume"].iloc[1] == 22000


def test_data_loader_raw_stock_load(tmp_path):
    loader = StockDataLoader(raw_dir="data/raw", processed_dir=tmp_path)
    df = loader.load_stock_data("JKH")
    assert not df.empty
    assert "date" in df.columns
    assert "open" in df.columns
    assert "high" in df.columns
    assert "low" in df.columns
    assert "close" in df.columns
    assert "volume" in df.columns
    assert (df["close"] > 0).all()
    assert (df["high"] >= df["low"]).all()

    # Test Parquet round-trip
    p_path = loader.save_to_parquet(df, symbol="JKH.N0000")
    assert p_path.exists()
    cached_df = loader.load_stock_data("JKH.N0000", use_parquet_cache=True)
    assert len(cached_df) == len(df)
