import os
import sys
import glob
import pandas as pd
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.connection import engine, Base

def ingest_all_csvs():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cse_dir = os.path.join(base_dir, "data", "raw", "cse")

    Base.metadata.create_all(bind=engine)

    csv_files = glob.glob(os.path.join(cse_dir, "*.csv"))
    print(f"Found {len(csv_files)} stock CSV files in {cse_dir}")

    all_dfs = []
    for file_path in csv_files:
        try:
            df = pd.read_csv(file_path)
            if not df.empty and "symbol" in df.columns and "date" in df.columns:
                all_dfs.append(df[["symbol", "date", "open", "high", "low", "close", "volume"]])
        except Exception:
            continue

    if not all_dfs:
        print("No stock CSV files found to ingest.")
        return

    merged_df = pd.concat(all_dfs, ignore_index=True)
    merged_df = merged_df.drop_duplicates(subset=["symbol", "date"], keep="last")
    merged_df["created_at"] = datetime.now(timezone.utc).isoformat()

    print(f"Prepared {len(merged_df)} total unique stock records for database ingestion...")

    # High performance bulk write using pandas to_sql into SQLite
    with engine.begin() as conn:
        # Clear existing stock_prices to cleanly seed complete dataset
        conn.exec_driver_sql("DELETE FROM stock_prices;")
        merged_df.to_sql("stock_prices", con=conn, if_exists="append", index=False, chunksize=10000)

    print(f"Successfully ingested {len(merged_df)} stock price records into database!")

if __name__ == "__main__":
    ingest_all_csvs()
