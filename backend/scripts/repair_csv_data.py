"""
Fix COMB (and any other) CSV data by overwriting with clean synthetic data.
Needed when old stub CSV was appended to new synthetic data, creating discontinuities.
Run from: backend/ directory
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
logging.disable(logging.WARNING)

import pandas as pd
from app.data_sources.cse.yfinance_client import YFinanceCSEClient, CSV_DIR, YAHOO_TICKER_MAP
from app.database.connection import SessionLocal, create_tables
from app.database.models import StockPrice
from app.repositories.stock_repository import StockPriceRepository

logging.disable(logging.NOTSET)

create_tables()
client = YFinanceCSEClient()

# Check each CSV for price discontinuities (large jumps between consecutive closes)
DISCONTINUITY_THRESHOLD = 0.30   # 30% single-day price jump = bad data

def check_has_discontinuity(df):
    df = df.sort_values("date")
    returns = df["close"].pct_change().abs()
    return (returns > DISCONTINUITY_THRESHOLD).any()

symbols = list(YAHOO_TICKER_MAP.keys())

print(f"\n{'='*58}")
print(f"  COMB/CSE CSV Data Repair Tool")
print(f"{'='*58}")

for sym in symbols:
    csv_path = os.path.join(CSV_DIR, f"{sym}.csv")
    if not os.path.exists(csv_path):
        print(f"  [{sym}] SKIP - no CSV")
        continue

    df = pd.read_csv(csv_path)
    if check_has_discontinuity(df):
        print(f"  [{sym}] DISCONTINUITY DETECTED - regenerating clean data...")
        # Generate fresh synthetic data (overwrite)
        fresh = client._generate_synthetic(sym, "2024-07-16", "2026-07-16")
        fresh[["date","open","high","low","close","volume"]].sort_values("date").to_csv(csv_path, index=False)
        print(f"    Overwritten CSV: {len(fresh)} rows  |  {fresh['date'].min()} -> {fresh['date'].max()}")

        # Clear old DB rows for this symbol and re-ingest
        db = SessionLocal()
        try:
            db.query(StockPrice).filter(StockPrice.symbol == sym).delete()
            db.commit()
            print(f"    Cleared old DB rows for {sym}")
        except Exception as e:
            db.rollback()
            print(f"    ERROR clearing DB: {e}")
        finally:
            db.close()

        # Re-ingest from fresh CSV
        db = SessionLocal()
        repo = StockPriceRepository(db)
        added = 0
        try:
            for _, row in fresh.iterrows():
                db.add(StockPrice(
                    symbol=sym,
                    date=str(row["date"]),
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=int(row["volume"]),
                ))
                added += 1
            db.commit()
            print(f"    Re-ingested {added} rows into DB")
        except Exception as e:
            db.rollback()
            print(f"    ERROR re-ingesting: {e}")
        finally:
            db.close()
    else:
        print(f"  [{sym}] OK - no discontinuity  (rows: {len(df)}  |  last: {df['date'].max()})")

print(f"\n{'='*58}")
print("Done. Data is now consistent.")
print(f"{'='*58}\n")
