"""
Historical Database Backfill Script
-----------------------------------
Migrates clean partitioned Parquet records into the primary database tables:
  1. stock_prices: All 26 equities historical OHLCV data.
  2. aspi_index: ASPI official benchmark historical close series.

Supports both PostgreSQL and SQLite dialect upserts with chunked batch processing.
"""

from __future__ import annotations

import argparse
import datetime
import logging
from pathlib import Path
import sys
import time
from typing import Dict, List, Tuple

# Safe terminal encoding on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from src.database.session import Base, engine, SessionLocal
from src.database.models import StockPrice, ASPIIndex, PipelineRun

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("backfill")


def upsert_records(session, model_class, records: List[Dict], conflict_keys: List[str]):
    """
    Executes dialect-agnostic idempotent upsert for PostgreSQL and SQLite.
    """
    if not records:
        return

    dialect_name = engine.dialect.name
    chunk_size = 100 if dialect_name == "sqlite" else 1000

    for i in range(0, len(records), chunk_size):
        chunk = records[i : i + chunk_size]

        if dialect_name == "postgresql":
            stmt = pg_insert(model_class).values(chunk)
            update_cols = {
                col: getattr(stmt.excluded, col)
                for col in chunk[0].keys()
                if col not in conflict_keys and col != "created_at"
            }
            if update_cols:
                stmt = stmt.on_conflict_do_update(
                    index_elements=conflict_keys,
                    set_=update_cols,
                )
            else:
                stmt = stmt.on_conflict_do_nothing(index_elements=conflict_keys)
            session.execute(stmt)

        elif dialect_name == "sqlite":
            stmt = sqlite_insert(model_class).values(chunk)
            update_cols = {
                col: getattr(stmt.excluded, col)
                for col in chunk[0].keys()
                if col not in conflict_keys and col != "created_at"
            }
            if update_cols:
                stmt = stmt.on_conflict_do_update(
                    index_elements=conflict_keys,
                    set_=update_cols,
                )
            else:
                stmt = stmt.on_conflict_do_nothing(index_elements=conflict_keys)
            session.execute(stmt)

        else:
            # Fallback standard merge
            for item in chunk:
                obj = model_class(**item)
                session.merge(obj)

    session.commit()


def backfill_aspi_index(processed_dir: Path, session) -> Tuple[int, str, str]:
    """Ingests official ASPI historical daily closing values."""
    aspi_path = processed_dir / "ASPI.parquet"
    if not aspi_path.exists():
        logger.warning("ASPI parquet not found at %s", aspi_path)
        return 0, "", ""

    df = pd.read_parquet(aspi_path)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df = df.sort_values("date").drop_duplicates(subset=["date"]).reset_index(drop=True)

    records = []
    for _, row in df.iterrows():
        records.append({
            "date": row["date"],
            "close": round(float(row["close"]), 2),
            "high": round(float(row["high"]), 2) if "high" in row and pd.notnull(row["high"]) else None,
            "low": round(float(row["low"]), 2) if "low" in row and pd.notnull(row["low"]) else None,
            "change": round(float(row["change"]), 2) if "change" in row and pd.notnull(row["change"]) else None,
            "percentage": round(float(row["percentage"]), 2) if "percentage" in row and pd.notnull(row["percentage"]) else None,
        })

    upsert_records(session, ASPIIndex, records, conflict_keys=["date"])
    d_min = str(df["date"].min())
    d_max = str(df["date"].max())
    return len(records), d_min, d_max


def backfill_equity(parquet_file: Path, session) -> Tuple[str, int, str, str]:
    """Ingests standardized historical OHLCV data for an individual equity."""
    symbol = parquet_file.stem
    df = pd.read_parquet(parquet_file)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df = df.sort_values("date").drop_duplicates(subset=["date"]).reset_index(drop=True)

    records = []
    for _, row in df.iterrows():
        records.append({
            "symbol": symbol,
            "date": row["date"],
            "open": round(float(row["open"]), 2) if "open" in row and pd.notnull(row["open"]) else round(float(row["close"]), 2),
            "high": round(float(row["high"]), 2) if "high" in row and pd.notnull(row["high"]) else round(float(row["close"]), 2),
            "low": round(float(row["low"]), 2) if "low" in row and pd.notnull(row["low"]) else round(float(row["close"]), 2),
            "close": round(float(row["close"]), 2),
            "volume": int(row["volume"]) if "volume" in row and pd.notnull(row["volume"]) else 0,
        })

    upsert_records(session, StockPrice, records, conflict_keys=["symbol", "date"])
    d_min = str(df["date"].min())
    d_max = str(df["date"].max())
    return symbol, len(records), d_min, d_max


def run_database_backfill(processed_dir: Path = Path("data/processed")):
    """Master backfill orchestrator."""
    start_time = time.time()
    print("=" * 85)
    print("      COLOMBO STOCK EXCHANGE: DATABASE MIGRATION & HISTORICAL BACKFILL")
    print(f"      Target Engine: {engine.url}")
    print("=" * 85)

    # 1. Initialize schema
    print("\n[1/3] Creating Database Tables if Not Exists...")
    Base.metadata.create_all(bind=engine)
    print("    [+] Tables verified: stock_prices, aspi_index, forecast_predictions, pipeline_runs")

    session = SessionLocal()
    total_records = 0
    summary = []

    try:
        # 2. Backfill ASPI Index
        print("\n[2/3] Backfilling ASPI Market Benchmark Index...")
        aspi_count, aspi_start, aspi_end = backfill_aspi_index(processed_dir, session)
        print(f"    [+] ASPI Index: {aspi_count:,} sessions ({aspi_start} to {aspi_end})")
        total_records += aspi_count

        # 3. Backfill all 26 Equities
        print("\n[3/3] Backfilling 26 CSE Equities into stock_prices...")
        stock_files = sorted(processed_dir.glob("*.parquet"))
        equity_files = [f for f in stock_files if f.stem != "ASPI"]

        for idx, pf in enumerate(equity_files, 1):
            sym, count, d_min, d_max = backfill_equity(pf, session)
            total_records += count
            summary.append({
                "Symbol": sym,
                "Records": count,
                "Start Date": d_min,
                "End Date": d_max,
            })
            print(f"    [{idx:02d}/{len(equity_files):02d}] [+] {sym:15s}: {count:,} rows ({d_min} to {d_max})")

        # 4. Record Pipeline Audit Run
        elapsed = time.time() - start_time
        audit = PipelineRun(
            run_date=datetime.date.today(),
            job_name="HISTORICAL_BACKFILL",
            status="SUCCESS",
            records_ingested=total_records,
            models_retrained=0,
            duration_seconds=round(elapsed, 2),
            message=f"Migrated {len(equity_files)} equities + ASPI into database successfully.",
        )
        session.add(audit)
        session.commit()

        print("\n" + "=" * 85)
        print(f"🎉 DATABASE BACKFILL COMPLETE in {elapsed:.1f}s")
        print(f"   Total Records Upserted: {total_records:,} across {len(equity_files)} Equities + ASPI Index")
        print("=" * 85 + "\n")

    except Exception as exc:
        session.rollback()
        logger.error("Database backfill failed: %s", exc, exc_info=True)
        raise
    finally:
        session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backfill historical Parquet records into database.")
    parser.add_argument("--data-dir", type=str, default="data/processed", help="Path to processed parquet directory")
    args = parser.parse_args()
    run_database_backfill(processed_dir=Path(args.data_dir))
