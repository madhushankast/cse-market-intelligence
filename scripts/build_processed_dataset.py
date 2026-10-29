"""
Batch Raw Stock Data to Parquet Processing Pipeline
---------------------------------------------------
Standardizes all 26 individual stock CSV files in data/raw/cse/ using StockDataLoader,
ensuring clean chronological OHLCV schemas and persisting them to data/processed/{symbol}.parquet.
"""

from __future__ import annotations

import logging
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Safe terminal encoding on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import pandas as pd
from src.ingestion.data_loader import StockDataLoader

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def batch_process_stock_data(
    raw_dir: str = "data/raw",
    processed_dir: str = "data/processed",
) -> List[dict]:
    loader = StockDataLoader(raw_dir=raw_dir, processed_dir=processed_dir)
    cse_raw_dir = Path(raw_dir) / "cse"
    stock_files = sorted(cse_raw_dir.glob("*.csv"))

    if not stock_files:
        logger.error("No raw stock CSV files detected in %s", cse_raw_dir)
        return []

    print("=" * 80)
    print(f"📦 BATCH PROCESSING: Converting {len(stock_files)} Equities to Parquet")
    print(f"   Source: {cse_raw_dir.resolve()}")
    print(f"   Target: {Path(processed_dir).resolve()}")
    print("=" * 80)

    summary_records = []

    for idx, file_path in enumerate(stock_files, 1):
        base_code = file_path.stem.upper()
        symbol = loader.normalize_symbol(base_code)

        try:
            df = loader.load_stock_data(symbol, use_parquet_cache=False)
            if df.empty:
                print(f"[{idx:02d}/{len(stock_files):02d}] ⚠️ {symbol}: No records found.")
                continue

            # Persist to data/processed/{symbol}.parquet
            out_path = loader.save_to_parquet(df, symbol=symbol)

            summary_records.append({
                "symbol": symbol,
                "code": base_code,
                "records": len(df),
                "date_min": str(df["date"].min().date()),
                "date_max": str(df["date"].max().date()),
                "latest_close": round(float(df["close"].iloc[-1]), 2),
                "file_path": out_path.name,
            })
            print(f"[{idx:02d}/{len(stock_files):02d}] ✅ {symbol:10s}: {len(df):,} rows | {df['date'].min().date()} to {df['date'].max().date()} | Last: LKR {df['close'].iloc[-1]:.2f}")

        except Exception as exc:
            logger.error("Failed processing %s: %s", symbol, exc)

    return summary_records


def main():
    summary = batch_process_stock_data()
    if summary:
        sum_df = pd.DataFrame(summary)
        total_rows = sum_df["records"].sum()
        print("\n" + "=" * 80)
        print(f"🎉 BATCH CONVERSION COMPLETE: {len(summary)} Stocks Standardized (~{total_rows:,} Total Rows)")
        print("=" * 80)


if __name__ == "__main__":
    main()
