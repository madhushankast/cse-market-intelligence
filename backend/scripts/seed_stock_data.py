"""
One-shot script to download 2 years of stock data for all CSE symbols.
Run from: backend/ directory
Usage: python scripts/seed_stock_data.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

from app.data_sources.cse.yfinance_client import YFinanceCSEClient, YAHOO_TICKER_MAP

client = YFinanceCSEClient()
symbols = list(YAHOO_TICKER_MAP.keys())

print(f"\n{'='*55}")
print(f"  CSE Stock Data Seeder — {len(symbols)} symbols")
print(f"{'='*55}")

for sym in symbols:
    print(f"\n>> {sym} ...")
    df = client.get_historical_data(sym, period_years=2)
    if df.empty:
        print(f"  [FAIL] No data returned for {sym}")
        continue
    path = client.save_to_csv(df, sym)
    print(f"  [OK] {len(df)} rows  |  {df['date'].min()} -> {df['date'].max()}")
    print(f"    Saved: {path}")

print(f"\n{'='*55}")
print("Done. Now restart the backend server to auto-ingest into DB.")
print(f"{'='*55}\n")
