"""
Ingest existing CSV files into the database.
Run from: backend/ directory
Usage: python scripts/ingest_csv_to_db.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Suppress yfinance noise on Windows console
import logging
logging.disable(logging.WARNING)

from app.database.connection import SessionLocal, create_tables
from app.database.models import StockPrice
from app.repositories.stock_repository import StockPriceRepository
from app.data_sources.cse.yfinance_client import YFinanceCSEClient, CSV_DIR, YAHOO_TICKER_MAP
import pandas as pd

logging.disable(logging.NOTSET)

# Ensure tables exist
create_tables()

client = YFinanceCSEClient()
symbols = list(YAHOO_TICKER_MAP.keys())

print(f"\n{'='*55}")
print(f"  CSE CSV -> DB Ingestion ({len(symbols)} symbols)")
print(f"{'='*55}")

total_added = 0

for sym in symbols:
    csv_path = os.path.join(CSV_DIR, f"{sym}.csv")
    if not os.path.exists(csv_path):
        print(f"  [{sym}] SKIP - no CSV found")
        continue

    df = pd.read_csv(csv_path)
    if df.empty:
        print(f"  [{sym}] SKIP - CSV is empty")
        continue

    df["symbol"] = sym

    db = SessionLocal()
    repo = StockPriceRepository(db)
    added = 0
    try:
        for _, row in df.iterrows():
            if not repo.check_exists(sym, str(row["date"])):
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
        total_added += added
        last_date = df["date"].max()
        print(f"  [{sym}] OK - {len(df)} rows in CSV, {added} new in DB  (last: {last_date})")
    except Exception as e:
        db.rollback()
        print(f"  [{sym}] ERROR - {e}")
    finally:
        db.close()

print(f"\n{'='*55}")
print(f"  Total new DB records: {total_added}")
print(f"{'='*55}\n")
