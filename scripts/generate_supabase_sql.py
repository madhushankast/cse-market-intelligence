"""
Generate complete SQL migration and seed file for Supabase.
"""
from pathlib import Path
import pandas as pd

def generate_supabase_sql():
    data_dir = Path("data")
    aspi_path = data_dir / "processed" / "ASPI.parquet"
    stocks_path = data_dir / "all_stock_prices.csv"
    
    aspi = pd.read_parquet(aspi_path)
    stocks = pd.read_csv(stocks_path)
    
    out_file = data_dir / "supabase_complete_migration.sql"
    
    with open(out_file, "w", encoding="utf-8") as f:
        # 1. DDL
        f.write("-- 1. Schema DDL\n")
        f.write("""CREATE TABLE IF NOT EXISTS stock_prices (
    symbol VARCHAR(32) NOT NULL,
    date DATE NOT NULL,
    open NUMERIC(12, 2) NOT NULL,
    high NUMERIC(12, 2) NOT NULL,
    low NUMERIC(12, 2) NOT NULL,
    close NUMERIC(12, 2) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_stock_prices PRIMARY KEY (symbol, date),
    CONSTRAINT uq_stock_price_symbol_date UNIQUE (symbol, date)
);

CREATE TABLE IF NOT EXISTS aspi_index (
    date DATE PRIMARY KEY,
    close NUMERIC(12, 2) NOT NULL,
    high NUMERIC(12, 2),
    low NUMERIC(12, 2),
    change NUMERIC(12, 2),
    percentage NUMERIC(6, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS forecast_predictions (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(32) NOT NULL,
    as_of_date DATE NOT NULL,
    current_price NUMERIC(12, 2) NOT NULL,
    price_p10 NUMERIC(12, 2) NOT NULL,
    price_p50 NUMERIC(12, 2) NOT NULL,
    price_p90 NUMERIC(12, 2) NOT NULL,
    expected_pct_change NUMERIC(6, 2) NOT NULL,
    target_returns JSONB NOT NULL DEFAULT '{}'::jsonb,
    cone_trajectory JSONB NOT NULL DEFAULT '[]'::jsonb,
    shap_drivers JSONB NOT NULL DEFAULT '[]'::jsonb,
    heuristic_signals JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_symbol_date_forecast UNIQUE (symbol, as_of_date)
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    id SERIAL PRIMARY KEY,
    run_date DATE NOT NULL,
    job_name VARCHAR(64) NOT NULL,
    status VARCHAR(20) NOT NULL,
    records_ingested INT DEFAULT 0,
    models_retrained INT DEFAULT 0,
    duration_seconds NUMERIC(8, 2),
    message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
\n""")
        
        # 2. ASPI seed
        f.write("-- 2. ASPI Benchmark Index Seed (1,053 rows)\n")
        f.write("INSERT INTO aspi_index (date, close) VALUES\n")
        aspi_lines = []
        for _, r in aspi.iterrows():
            d = pd.to_datetime(r["date"]).strftime("%Y-%m-%d")
            c = round(float(r["close"]), 2)
            aspi_lines.append(f"('{d}', {c})")
        f.write(",\n".join(aspi_lines))
        f.write("\nON CONFLICT (date) DO UPDATE SET close = EXCLUDED.close;\n\n")

        # 3. Equities seed
        f.write("-- 3. Stock Prices Seed (25,494 rows chunked by 1000)\n")
        chunk_size = 1000
        for i in range(0, len(stocks), chunk_size):
            chunk = stocks.iloc[i : i + chunk_size]
            f.write("INSERT INTO stock_prices (symbol, date, open, high, low, close, volume) VALUES\n")
            stock_lines = []
            for _, r in chunk.iterrows():
                sym = str(r["symbol"])
                d = str(r["date"])
                o = round(float(r["open"]), 2)
                h = round(float(r["high"]), 2)
                l = round(float(r["low"]), 2)
                c = round(float(r["close"]), 2)
                v = int(r["volume"]) if pd.notnull(r["volume"]) else 0
                stock_lines.append(f"('{sym}', '{d}', {o}, {h}, {l}, {c}, {v})")
            f.write(",\n".join(stock_lines))
            f.write("\nON CONFLICT (symbol, date) DO UPDATE SET open=EXCLUDED.open, high=EXCLUDED.high, low=EXCLUDED.low, close=EXCLUDED.close, volume=EXCLUDED.volume;\n\n")

    print(f"Generated {out_file} ({out_file.stat().st_size:,} bytes)")

if __name__ == "__main__":
    generate_supabase_sql()
