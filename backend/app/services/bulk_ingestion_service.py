"""
bulk_ingestion_service.py
─────────────────────────
Orchestrates downloading and persisting stock data for all tracked symbols.

Key capabilities:
  • ingest_all()           – download all symbols (2yr history)
  • refresh_incremental()  – append only missing recent data (next-day updates)
  • ingest_symbol()        – download one symbol (used by API route)
  • data_status()          – return last-date + row counts for each symbol
"""

import logging
from datetime import date, timedelta
from typing import Optional

import pandas as pd

from app.data_sources.cse.yfinance_client import YFinanceCSEClient, YAHOO_TICKER_MAP
from app.database.connection import SessionLocal
from app.database.models import StockPrice
from app.repositories.stock_repository import StockPriceRepository

logger = logging.getLogger(__name__)

# All symbols the platform tracks
ALL_SYMBOLS = list(YAHOO_TICKER_MAP.keys())


class BulkIngestionService:
    """
    Downloads historical and incremental stock data for all CSE symbols
    using Yahoo Finance as the primary source with synthetic GBM fallback.
    """

    def __init__(self):
        self.yf_client = YFinanceCSEClient()

    # ── Public API ──────────────────────────────────────────────────────────────

    def ingest_all(self, period_years: int = 2) -> dict:
        """
        Download full history for every symbol and persist to CSV + DB.
        Returns a summary dict keyed by symbol.
        """
        results = {}
        for sym in ALL_SYMBOLS:
            try:
                df = self.yf_client.get_historical_data(sym, period_years=period_years)
                if df.empty:
                    results[sym] = {"status": "no_data", "rows": 0}
                    continue

                # Persist CSV
                self.yf_client.save_to_csv(df, sym)

                # Persist DB
                added = self._persist_to_db(sym, df)
                results[sym] = {
                    "status": "ok",
                    "rows_fetched": len(df),
                    "rows_added_to_db": added,
                    "date_range": f"{df['date'].min()} → {df['date'].max()}",
                }
                logger.info(f"[Bulk] {sym}: {len(df)} rows fetched, {added} new in DB")

            except Exception as exc:
                logger.error(f"[Bulk] Failed for {sym}: {exc}")
                results[sym] = {"status": "error", "error": str(exc)}

        return results

    def refresh_incremental(self) -> dict:
        """
        For each symbol, fetch only the data that is newer than what is
        already stored. Designed to be called daily (e.g. via /refresh endpoint
        or a scheduler).
        """
        results = {}
        today = date.today().isoformat()

        for sym in ALL_SYMBOLS:
            try:
                last_date = self.yf_client.get_last_date_in_csv(sym)

                if last_date is None:
                    # No CSV at all — full download
                    logger.info(f"[Refresh] {sym}: no CSV found, running full ingest.")
                    df = self.yf_client.get_historical_data(sym, period_years=2)
                else:
                    # Download from day after last recorded date
                    start = (
                        pd.Timestamp(last_date) + timedelta(days=1)
                    ).strftime("%Y-%m-%d")

                    if start >= today:
                        logger.info(f"[Refresh] {sym}: already up-to-date ({last_date}).")
                        results[sym] = {"status": "up_to_date", "last_date": last_date}
                        continue

                    logger.info(f"[Refresh] {sym}: fetching {start} → {today}")
                    df = self.yf_client.get_historical_data(sym, start=start, end=today)

                if df.empty:
                    results[sym] = {"status": "no_new_data", "last_date": last_date}
                    continue

                self.yf_client.save_to_csv(df, sym)
                added = self._persist_to_db(sym, df)

                new_last = self.yf_client.get_last_date_in_csv(sym)
                results[sym] = {
                    "status": "updated",
                    "rows_added": added,
                    "last_date": new_last,
                }

            except Exception as exc:
                logger.error(f"[Refresh] Failed for {sym}: {exc}")
                results[sym] = {"status": "error", "error": str(exc)}

        return results

    def ingest_symbol(self, symbol: str, period_years: int = 2) -> dict:
        """
        Ingest (or re-ingest) a single symbol. Called by the existing
        POST /stocks/{symbol}/ingest route.
        """
        sym = symbol.upper()
        df = self.yf_client.get_historical_data(sym, period_years=period_years)

        if df.empty:
            return {"status": "no_data", "rows": 0}

        self.yf_client.save_to_csv(df, sym)
        added = self._persist_to_db(sym, df)

        return {
            "status": "ok",
            "symbol": sym,
            "rows_fetched": len(df),
            "rows_added_to_db": added,
            "date_range": f"{df['date'].min()} → {df['date'].max()}",
        }

    def data_status(self) -> dict:
        """
        Return data-freshness status for all tracked symbols.
        Useful for the /system/data-status endpoint.
        """
        db = SessionLocal()
        repo = StockPriceRepository(db)
        status = {}
        try:
            for sym in ALL_SYMBOLS:
                last_csv = self.yf_client.get_last_date_in_csv(sym)
                try:
                    records = repo.get_by_symbol(sym)
                    db_count = len(records)
                    db_last  = max((r.date for r in records), default=None)
                    db_last_str = str(db_last) if db_last else None
                except Exception:
                    db_count = 0
                    db_last_str = None

                today = date.today().isoformat()
                stale = (
                    last_csv is not None and last_csv < (
                        pd.Timestamp(today) - timedelta(days=3)
                    ).strftime("%Y-%m-%d")
                )

                status[sym] = {
                    "csv_last_date": last_csv,
                    "db_last_date":  db_last_str,
                    "db_row_count":  db_count,
                    "is_stale":      stale,
                    "needs_ingest":  last_csv is None,
                }
        finally:
            db.close()

        return status

    # ── Internal helpers ────────────────────────────────────────────────────────

    def _persist_to_db(self, symbol: str, df: pd.DataFrame) -> int:
        """
        Upsert rows from `df` into the StockPrice table.
        Returns the number of new rows added.
        """
        db = SessionLocal()
        repo = StockPriceRepository(db)
        added = 0
        try:
            for _, row in df.iterrows():
                sym_col = row.get("symbol", symbol)
                if not repo.check_exists(str(sym_col), str(row["date"])):
                    db.add(StockPrice(
                        symbol=str(sym_col),
                        date=str(row["date"]),
                        open=float(row["open"]),
                        high=float(row["high"]),
                        low=float(row["low"]),
                        close=float(row["close"]),
                        volume=int(row["volume"]),
                    ))
                    added += 1
            db.commit()
        except Exception as exc:
            db.rollback()
            logger.error(f"[DB] Failed persisting {symbol}: {exc}")
            raise
        finally:
            db.close()
        return added
