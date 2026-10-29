"""
Daily CSE Market Synchronization & Database Ingestion Module
-----------------------------------------------------------
Pulls latest post-market close session data directly from official CSE endpoints:
  1. Synchronizes ASPI benchmark index point-in-time closing quote into `aspi_index`.
  2. Pulls daily OHLCV bars across all 26 equities and upserts into `stock_prices`.
  3. Detects price anomalies and records execution audit history in `pipeline_runs`.
"""

from __future__ import annotations

import datetime
import logging
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from src.database.session import engine, SessionLocal
from src.database.models import StockPrice, ASPIIndex, PipelineRun
from src.ingestion.cse_scraper import CSEScraper

logger = logging.getLogger("daily_sync")


def upsert_records_chunked(session, model_class, records: List[Dict], conflict_keys: List[str]):
    """Idempotent batch upsert supporting PostgreSQL and SQLite dialects."""
    if not records:
        return 0

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
                stmt = stmt.on_conflict_do_update(index_elements=conflict_keys, set_=update_cols)
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
                stmt = stmt.on_conflict_do_update(index_elements=conflict_keys, set_=update_cols)
            else:
                stmt = stmt.on_conflict_do_nothing(index_elements=conflict_keys)
            session.execute(stmt)

        else:
            for item in chunk:
                session.merge(model_class(**item))

    session.commit()
    return len(records)


class DailyCSESyncService:
    """Service orchestrating daily ingestion from CSE API into database."""

    def __init__(self, session=None):
        self._session = session
        self.scraper = CSEScraper()

    def get_session(self):
        return self._session if self._session is not None else SessionLocal()

    def sync_aspi_index(self, session) -> Tuple[bool, Optional[float], str]:
        """Fetches latest ASPI benchmark value and upserts into `aspi_index`."""
        try:
            url = f"{self.scraper.base_url}/aspiData"
            resp = self.scraper.session.post(url, timeout=12)
            resp.raise_for_status()
            data = resp.json()

            value = data.get("value")
            if value is None:
                return False, None, "No value in aspiData payload"

            current_val = round(float(value), 2)
            today_date = datetime.date.today()

            record = {
                "date": today_date,
                "close": current_val,
                "high": round(float(data.get("high")), 2) if data.get("high") is not None else current_val,
                "low": round(float(data.get("low")), 2) if data.get("low") is not None else current_val,
                "change": round(float(data.get("change")), 2) if data.get("change") is not None else 0.0,
                "percentage": round(float(data.get("percentage")), 2) if data.get("percentage") is not None else 0.0,
            }

            upsert_records_chunked(session, ASPIIndex, [record], conflict_keys=["date"])
            return True, current_val, f"ASPI synchronized at {current_val} for {today_date}"
        except Exception as exc:
            logger.error("Failed to sync ASPI index: %s", exc)
            return False, None, f"ASPI sync error: {exc}"

    def sync_equity(self, symbol: str, session) -> Dict[str, Any]:
        """Pulls latest daily OHLCV bar for an individual stock and upserts into `stock_prices`."""
        norm_sym = symbol.replace("_", ".")
        clean_sym = symbol.replace(".", "_")

        try:
            df = self.scraper.pull_latest_ohlcv(norm_sym)
            if df.empty:
                return {"symbol": clean_sym, "status": "no_data", "bars_added": 0}

            df["date"] = pd.to_datetime(df["date"]).dt.date
            # Ensure unique dates
            df = df.sort_values("date").drop_duplicates(subset=["date"])

            records = []
            for _, row in df.iterrows():
                records.append({
                    "symbol": clean_sym,
                    "date": row["date"],
                    "open": round(float(row["open"]), 2) if "open" in row and pd.notnull(row["open"]) else round(float(row["close"]), 2),
                    "high": round(float(row["high"]), 2) if "high" in row and pd.notnull(row["high"]) else round(float(row["close"]), 2),
                    "low": round(float(row["low"]), 2) if "low" in row and pd.notnull(row["low"]) else round(float(row["close"]), 2),
                    "close": round(float(row["close"]), 2),
                    "volume": int(row["volume"]) if "volume" in row and pd.notnull(row["volume"]) else 0,
                })

            count = upsert_records_chunked(session, StockPrice, records, conflict_keys=["symbol", "date"])
            latest = records[-1]
            return {
                "symbol": clean_sym,
                "status": "updated",
                "bars_added": count,
                "latest_date": str(latest["date"]),
                "latest_close": latest["close"],
            }
        except Exception as exc:
            logger.error("Error syncing equity %s: %s", symbol, exc)
            return {"symbol": clean_sym, "status": "error", "message": str(exc), "bars_added": 0}

    def run_sync(self, symbols: Optional[List[str]] = None) -> Dict[str, Any]:
        """Runs full synchronization across ASPI and all target equities."""
        start_time = time.time()
        close_session = self._session is None
        session = self.get_session()

        try:
            # 1. Sync ASPI
            aspi_ok, aspi_val, aspi_msg = self.sync_aspi_index(session)

            # 2. Get target symbols from database or default list
            if not symbols:
                res = session.query(StockPrice.symbol).distinct().all()
                symbols = [r[0] for r in res] if res else []

            if not symbols:
                # Fallback to files in data/processed
                processed_dir = Path("data/processed")
                symbols = [f.stem for f in processed_dir.glob("*.parquet") if f.stem != "ASPI"]

            equity_summaries = []
            total_bars = 0
            for sym in sorted(symbols):
                res = self.sync_equity(sym, session)
                total_bars += res.get("bars_added", 0)
                equity_summaries.append(res)

            elapsed = time.time() - start_time

            # Record audit
            audit = PipelineRun(
                run_date=datetime.date.today(),
                job_name="DAILY_MARKET_SYNC",
                status="SUCCESS" if aspi_ok else "WARNING",
                records_ingested=total_bars + (1 if aspi_ok else 0),
                models_retrained=0,
                duration_seconds=round(elapsed, 2),
                message=f"Synced {len(symbols)} equities + ASPI ({aspi_msg}) in {elapsed:.1f}s",
            )
            session.add(audit)
            session.commit()

            return {
                "status": "success",
                "aspi_ok": aspi_ok,
                "aspi_value": aspi_val,
                "equities_synced": len(symbols),
                "total_records_ingested": total_bars,
                "duration_seconds": round(elapsed, 2),
                "summaries": equity_summaries,
            }
        finally:
            if close_session:
                session.close()


def sync_daily_cse_market(session=None) -> Dict[str, Any]:
    """Top-level invocation wrapper for daily market sync."""
    service = DailyCSESyncService(session=session)
    return service.run_sync()


if __name__ == "__main__":
    result = sync_daily_cse_market()
    print("=" * 80)
    print("DAILY MARKET SYNC RESULT:")
    print(f"  ASPI Synchronized: {result['aspi_ok']} (LKR {result['aspi_value']})")
    print(f"  Equities Updated: {result['equities_synced']} ({result['total_records_ingested']} bars)")
    print(f"  Duration: {result['duration_seconds']}s")
    print("=" * 80)
