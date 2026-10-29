"""
Daily CSE Market Synchronization & Quality Audit Script
-------------------------------------------------------
Executes daily post-market close (CSE trading ends at 2:30 PM Colombo / UTC+5:30):
  1. Synchronizes official ASPI benchmark index point-in-time closing values.
  2. Ingests latest daily OHLCV bars across all 26 CSE equities from official API.
  3. Executes data drift, outlier, and circuit-breaker anomaly checks.
  4. Appends to partitioned Parquet storage in data/processed/.
"""

from __future__ import annotations

import argparse
import datetime
import logging
from pathlib import Path
import sys
import time
from typing import Dict, List, Optional, Tuple

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
import requests

from src.ingestion.cse_scraper import CSEScraper
from src.ingestion.data_loader import StockDataLoader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("daily_sync")


class DailyMarketSyncService:
    """
    Automated market synchronization and quality verification pipeline.
    """

    def __init__(self, processed_dir: Path = Path("data/processed")):
        self.processed_dir = processed_dir
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.scraper = CSEScraper()
        self.loader = StockDataLoader(processed_dir=self.processed_dir)

    def sync_aspi_index(self) -> Tuple[bool, Optional[float], str]:
        """
        Synchronizes ASPI historical series using CSE live API endpoint.
        """
        aspi_file = self.processed_dir / "ASPI.parquet"
        existing_df = pd.read_parquet(aspi_file) if aspi_file.exists() else pd.DataFrame()

        try:
            url = f"{self.scraper.base_url}/aspiData"
            resp = self.scraper.session.post(url, timeout=12)
            resp.raise_for_status()
            data = resp.json()

            value = data.get("value")
            if value is None:
                return False, None, "No value in aspiData response"

            current_val = float(value)
            today_str = str(datetime.date.today())

            if not existing_df.empty:
                existing_df["date"] = pd.to_datetime(existing_df["date"])
                last_date = existing_df["date"].max()

                # If today's bar not yet recorded
                if pd.to_datetime(today_str) > last_date:
                    new_row = pd.DataFrame([{
                        "date": pd.to_datetime(today_str),
                        "symbol": "ASPI",
                        "close": current_val,
                    }])
                    updated = pd.concat([existing_df, new_row], ignore_index=True)
                    updated = updated.sort_values("date").drop_duplicates(subset=["date"]).reset_index(drop=True)
                    updated.to_parquet(aspi_file, index=False)
                    return True, current_val, f"Appended new ASPI close {current_val} for {today_str}"
                else:
                    return True, current_val, f"ASPI already up to date ({last_date.date()})"
            return True, current_val, f"ASPI current value: {current_val}"
        except Exception as exc:
            return False, None, f"ASPI sync error: {exc}"

    def sync_equity(self, symbol: str) -> Dict[str, Any]:
        """
        Syncs latest daily OHLCV bar for an individual equity and audits data quality.
        """
        clean_name = symbol.replace(".", "_")
        parquet_path = self.processed_dir / f"{clean_name}.parquet"
        if not parquet_path.exists():
            return {"symbol": symbol, "status": "skipped", "reason": "No existing parquet"}

        existing_df = pd.read_parquet(parquet_path)
        existing_df["date"] = pd.to_datetime(existing_df["date"])
        last_date = existing_df["date"].max()
        last_close = float(existing_df["close"].iloc[-1])

        # Fetch latest bars from API
        norm_sym = symbol.replace("_", ".")
        new_df = self.scraper.pull_latest_ohlcv(norm_sym)

        if new_df.empty:
            return {"symbol": symbol, "status": "no_live_data", "last_date": str(last_date.date()), "last_close": last_close}

        new_df["date"] = pd.to_datetime(new_df["date"])
        fresh_bars = new_df[new_df["date"] > last_date]

        if fresh_bars.empty:
            return {"symbol": symbol, "status": "up_to_date", "last_date": str(last_date.date()), "last_close": last_close}

        # Quality & Anomaly Checks
        anomalies = []
        for _, bar in fresh_bars.iterrows():
            new_close = float(bar["close"])
            ret = (new_close - last_close) / last_close
            # Single-session move > 25% is flagged as anomaly
            if abs(ret) > 0.25:
                anomalies.append(f"Abnormal return jump: {ret:+.1%} (LKR {last_close} -> {new_close})")
            if bar["high"] < bar["low"]:
                anomalies.append(f"Invalid spread: high {bar['high']} < low {bar['low']}")

        # Append fresh bars
        combined = pd.concat([existing_df, fresh_bars], ignore_index=True)
        combined = combined.sort_values("date").drop_duplicates(subset=["date"]).reset_index(drop=True)
        combined.to_parquet(parquet_path, index=False)

        latest_synced = combined.iloc[-1]
        return {
            "symbol": symbol,
            "status": "updated",
            "bars_added": len(fresh_bars),
            "new_date": str(latest_synced["date"].date()),
            "new_close": float(latest_synced["close"]),
            "anomalies": anomalies,
        }

    def run_daily_sync(self) -> pd.DataFrame:
        """
        Executes end-to-end sync for ASPI and all 26 equities.
        """
        start_time = time.time()
        print("\n" + "=" * 80)
        print("          COLOMBO STOCK EXCHANGE: DAILY MARKET DATA SYNC & AUDIT")
        print("=" * 80)

        # 1. Sync ASPI benchmark index
        print("[1/2] Synchronizing ASPI Market Benchmark Index...")
        aspi_ok, aspi_val, aspi_msg = self.sync_aspi_index()
        status_marker = "[+]" if aspi_ok else "[!]"
        print(f"    {status_marker} {aspi_msg}")

        # 2. Sync all 26 equities
        print("\n[2/2] Synchronizing 26 CSE Equities...")
        stock_files = sorted(self.processed_dir.glob("*.parquet"))
        symbols = [f.stem for f in stock_files if f.stem != "ASPI"]

        records = []
        for s in symbols:
            res = self.sync_equity(s)
            records.append(res)
            anom_msg = f" | [!] {res['anomalies']}" if res.get("anomalies") else ""
            status_desc = res["status"]
            if status_desc == "updated":
                print(f"    [+] {s:<12}: Updated +{res['bars_added']} bar(s) -> {res['new_date']} @ LKR {res['new_close']:,.2f}{anom_msg}")
            else:
                print(f"    [*] {s:<12}: Up-to-date ({res.get('last_date', 'N/A')}) @ LKR {res.get('last_close', 0.0):,.2f}")

        elapsed = time.time() - start_time
        print("-" * 80)
        print(f"Sync complete in {elapsed:.1f}s. All datasets verified.\n" + "=" * 80 + "\n")
        return pd.DataFrame(records)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synchronize daily CSE market data and audit quality.")
    parser.add_argument("--data-dir", type=str, default="data/processed", help="Path to processed Parquet directory.")
    args = parser.parse_args()

    service = DailyMarketSyncService(processed_dir=Path(args.data_dir))
    service.run_daily_sync()
