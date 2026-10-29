"""
Splits SQL seeds into bite-sized files (< 300 KB each) so they can be run in Supabase SQL Editor.
"""
from pathlib import Path
import pandas as pd

def generate_chunks():
    data_dir = Path("data")
    aspi = pd.read_parquet(data_dir / "processed" / "ASPI.parquet")
    stocks = pd.read_csv(data_dir / "all_stock_prices.csv")
    
    # 1. ASPI seed (~60 KB)
    aspi_file = data_dir / "seed_1_aspi.sql"
    with open(aspi_file, "w", encoding="utf-8") as f:
        f.write("-- ASPI Index Data (1,053 rows)\n")
        f.write("INSERT INTO aspi_index (date, close) VALUES\n")
        lines = []
        for _, r in aspi.iterrows():
            d = pd.to_datetime(r["date"]).strftime("%Y-%m-%d")
            c = round(float(r["close"]), 2)
            lines.append(f"('{d}', {c})")
        f.write(",\n".join(lines))
        f.write("\nON CONFLICT (date) DO UPDATE SET close = EXCLUDED.close;\n")
    print(f"Generated {aspi_file} ({aspi_file.stat().st_size:,} bytes)")

    # 2. Stocks split into 5 parts of ~5,000 rows each (~280 KB each)
    batch_size = 5000
    for part_idx, start in enumerate(range(0, len(stocks), batch_size), 2):
        chunk = stocks.iloc[start : start + batch_size]
        part_file = data_dir / f"seed_{part_idx}_stocks.sql"
        with open(part_file, "w", encoding="utf-8") as f:
            f.write(f"-- Stocks Data Part {part_idx - 1} (Rows {start + 1} to {start + len(chunk)})\n")
            for sub_start in range(0, len(chunk), 500):
                sub_chunk = chunk.iloc[sub_start : sub_start + 500]
                f.write("INSERT INTO stock_prices (symbol, date, open, high, low, close, volume) VALUES\n")
                sub_lines = []
                for _, r in sub_chunk.iterrows():
                    sym = str(r["symbol"])
                    d = str(r["date"])
                    o = round(float(r["open"]), 2)
                    h = round(float(r["high"]), 2)
                    l = round(float(r["low"]), 2)
                    c = round(float(r["close"]), 2)
                    v = int(r["volume"]) if pd.notnull(r["volume"]) else 0
                    sub_lines.append(f"('{sym}', '{d}', {o}, {h}, {l}, {c}, {v})")
                f.write(",\n".join(sub_lines))
                f.write("\nON CONFLICT (symbol, date) DO UPDATE SET open=EXCLUDED.open, high=EXCLUDED.high, low=EXCLUDED.low, close=EXCLUDED.close, volume=EXCLUDED.volume;\n\n")
        print(f"Generated {part_file} ({part_file.stat().st_size:,} bytes)")

if __name__ == "__main__":
    generate_chunks()
