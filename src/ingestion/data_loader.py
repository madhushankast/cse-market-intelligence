"""
Stock Data Loader & Parquet Manager
-----------------------------------
Standardizes historical Colombo Stock Exchange equities data (OHLCV)
from raw CSV archives into clean, partitioned Parquet files under data/processed/.
"""

from __future__ import annotations

import logging
from pathlib import Path
import re
from typing import Dict, List, Optional, Union
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class StockDataLoader:
    """
    Production-grade historical stock data loader and parquet cache manager.
    
    Standardized Output Schema:
      - date: datetime64[ns]
      - symbol: string (e.g. 'JKH.N0000')
      - open: float64
      - high: float64
      - low: float64
      - close: float64
      - volume: int64
    """

    DEFAULT_RAW_DIR = "data/raw"
    DEFAULT_PROCESSED_DIR = "data/processed"

    def __init__(
        self,
        raw_dir: Union[str, Path] = DEFAULT_RAW_DIR,
        processed_dir: Union[str, Path] = DEFAULT_PROCESSED_DIR,
    ):
        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def normalize_symbol(symbol: str) -> str:
        """Standardizes ticker symbol to CSE dot notation (e.g. 'JKH' or 'JKH_N0000' -> 'JKH.N0000')."""
        s = symbol.strip().upper()
        if "_" in s and not "." in s:
            s = s.replace("_", ".")
        if "." not in s and s != "ASPI":
            return f"{s}.N0000"
        return s

    @staticmethod
    def extract_base_code(symbol: str) -> str:
        """Extracts the base equity code (e.g. 'JKH.N0000' -> 'JKH')."""
        s = symbol.strip().upper().replace("_", ".")
        return s.split(".")[0]

    def _parse_dates(self, date_series: pd.Series) -> pd.Series:
        """
        Parses dates handling both 'YYYY-MM-DD' and CSE yearly format '04-JAN-24'.
        """
        if pd.api.types.is_datetime64_any_dtype(date_series):
            return date_series

        # Try fast ISO format first
        parsed = pd.to_datetime(date_series, format="%Y-%m-%d", errors="coerce")
        if parsed.isnull().all() and len(date_series) > 0:
            # Fallback to CSE yearly format '%d-%b-%y' or '%d-%b-%Y'
            parsed = pd.to_datetime(date_series, format="%d-%b-%y", errors="coerce")
            if parsed.isnull().all():
                parsed = pd.to_datetime(date_series, errors="coerce")

        return parsed

    def _sanitize_numeric_column(self, series: pd.Series, to_int: bool = False) -> pd.Series:
        """
        Cleans string representations of numbers (removing commas, currency symbols, quotes).
        """
        if pd.api.types.is_numeric_dtype(series):
            clean = series.fillna(0)
            return clean.astype(int) if to_int else clean.astype(float)

        cleaned = (
            series.astype(str)
            .str.replace(",", "", regex=False)
            .str.replace('"', "", regex=False)
            .str.replace("'", "", regex=False)
            .str.replace("Rs.", "", regex=False)
            .str.strip()
        )
        numeric = pd.to_numeric(cleaned, errors="coerce").fillna(0.0)
        return numeric.round().astype(int) if to_int else numeric.astype(float)

    def standardize_raw_df(self, df: pd.DataFrame, target_symbol: str) -> pd.DataFrame:
        """
        Standardizes raw DataFrame into clean OHLCV schema:
        ['date', 'symbol', 'open', 'high', 'low', 'close', 'volume']
        """
        if df.empty:
            return pd.DataFrame(columns=["date", "symbol", "open", "high", "low", "close", "volume"])

        df = df.copy()
        norm_sym = self.normalize_symbol(target_symbol)

        # Normalize column names: lower-case, stripped, alphanumeric
        col_map = {}
        for c in df.columns:
            clean_c = re.sub(r"[^\w\s]", "", str(c)).strip().lower().replace(" ", "_")
            col_map[c] = clean_c
        df = df.rename(columns=col_map)

        # Canonical header mapping
        rename_dict = {
            "trading_date": "date",
            "price_high_rs": "high",
            "price_low_rs": "low",
            "close_price_rs": "close",
            "open_price_rs": "open",
            "share_volume_no": "volume",
            "trade_volume_no": "trade_count",
            "company_id": "symbol",
        }
        df = df.rename(columns=rename_dict)

        # Ensure symbol column exists
        if "symbol" not in df.columns:
            df["symbol"] = norm_sym
        else:
            df["symbol"] = df["symbol"].apply(lambda s: self.normalize_symbol(str(s)))
            # If loaded from multi-symbol dump, filter to target symbol
            base_code = self.extract_base_code(target_symbol)
            df = df[df["symbol"].str.startswith(base_code)]

        if df.empty:
            return pd.DataFrame(columns=["date", "symbol", "open", "high", "low", "close", "volume"])

        # Parse dates
        df["date"] = self._parse_dates(df["date"])
        df = df.dropna(subset=["date"])

        # Sanitize numeric columns
        for col in ["open", "high", "low", "close"]:
            if col in df.columns:
                df[col] = self._sanitize_numeric_column(df[col], to_int=False)

        if "volume" in df.columns:
            df["volume"] = self._sanitize_numeric_column(df["volume"], to_int=True)
        else:
            df["volume"] = 0

        # Fill open price if missing using previous close or current close
        if "open" not in df.columns or df["open"].isnull().all():
            df["open"] = df["close"]

        # Ensure high >= low and bounds validity
        df["high"] = np.maximum(df["high"], np.maximum(df["open"], df["close"]))
        df["low"] = np.minimum(df["low"], np.minimum(df["open"], df["close"]))

        # Filter out zero or negative invalid closing prices
        df = df[df["close"] > 0]

        # Select canonical columns, drop duplicates, sort chronologically
        canonical_cols = ["date", "symbol", "open", "high", "low", "close", "volume"]
        df = df[canonical_cols]
        df = df.sort_values("date").drop_duplicates(subset=["date", "symbol"]).reset_index(drop=True)

        return df

    def extract_from_yearly_archives(self, symbol: str) -> pd.DataFrame:
        """
        Searches data/raw/yearly/ files (2021.csv - 2025.csv) for historical trades of the given symbol.
        """
        base_code = self.extract_base_code(symbol)
        yearly_dir = self.raw_dir / "yearly"
        if not yearly_dir.exists():
            return pd.DataFrame()

        matched_dfs = []
        for yf in sorted(yearly_dir.glob("*.csv")):
            try:
                # Read header to find company id column
                preview = pd.read_csv(yf, nrows=5)
                comp_cols = [c for c in preview.columns if "COMPANY" in c.upper() or "SYMBOL" in c.upper()]
                if not comp_cols:
                    continue
                comp_col = comp_cols[0]

                # Load full yearly file and filter to target stock
                chunk_df = pd.read_csv(yf)
                stock_chunk = chunk_df[chunk_df[comp_col].astype(str).str.strip().str.upper() == base_code]
                if not stock_chunk.empty:
                    matched_dfs.append(stock_chunk)
            except Exception as exc:
                logger.warning("Error scanning yearly file %s: %s", yf.name, exc)

        if not matched_dfs:
            return pd.DataFrame()

        combined = pd.concat(matched_dfs, ignore_index=True)
        return self.standardize_raw_df(combined, target_symbol=symbol)

    def load_stock_data(self, symbol: str, use_parquet_cache: bool = True) -> pd.DataFrame:
        """
        Loads cleaned historical stock OHLCV data for a ticker.
        Priority:
          1. data/processed/{symbol}.parquet (if cache exists)
          2. data/raw/cse/{code}.csv
          3. data/raw/yearly/*.csv (as fallback archive scan)
        """
        norm_sym = self.normalize_symbol(symbol)
        clean_name = norm_sym.replace(".", "_")
        parquet_path = self.processed_dir / f"{clean_name}.parquet"
        if not parquet_path.exists():
            parquet_path = self.processed_dir / f"{symbol}.parquet"

        if use_parquet_cache and parquet_path.exists():
            logger.info("Loading cached Parquet dataset for %s from %s", norm_sym, parquet_path)
            df = pd.read_parquet(parquet_path)
            df["date"] = pd.to_datetime(df["date"])
            return df.sort_values("date").reset_index(drop=True)

        # Load from individual raw CSV
        base_code = self.extract_base_code(symbol)
        candidates = [
            self.raw_dir / "cse" / f"{base_code}.csv",
            self.raw_dir / "cse" / f"{norm_sym}.csv",
            self.raw_dir / f"{base_code}.csv",
        ]

        raw_df = pd.DataFrame()
        for p in candidates:
            if p.exists():
                logger.info("Loading raw CSV for %s from %s", norm_sym, p)
                raw_df = pd.read_csv(p)
                break

        if not raw_df.empty:
            std_df = self.standardize_raw_df(raw_df, target_symbol=norm_sym)
        else:
            logger.info("No raw individual CSV found for %s. Scanning yearly archives...", norm_sym)
            std_df = self.extract_from_yearly_archives(norm_sym)

        if not std_df.empty:
            # Persist clean dataset to Parquet
            self.save_to_parquet(std_df, symbol=norm_sym)
            return std_df

        logger.warning("No data found anywhere for symbol %s", symbol)
        return pd.DataFrame(columns=["date", "symbol", "open", "high", "low", "close", "volume"])

    # Method alias
    load_stock = load_stock_data

    def save_to_parquet(self, df: pd.DataFrame, symbol: str) -> Path:
        """
        Saves standardized OHLCV DataFrame to data/processed/{symbol}.parquet.
        """
        norm_sym = self.normalize_symbol(symbol)
        clean_name = norm_sym.replace(".", "_")
        output_path = self.processed_dir / f"{clean_name}.parquet"
        df.to_parquet(output_path, index=False)
        logger.info("Saved standardized Parquet file: %s (%d records)", output_path, len(df))
        return output_path

    # Backwards-compatible aliases
    load_stock_csv = load_stock_data


# Alias for backwards compatibility
CSEDataLoader = StockDataLoader
