"""
CSE Direct API Scraper & Live Synchronization Client
-----------------------------------------------------
Session-based HTTP client interacting directly with official Colombo Stock Exchange
endpoints (https://www.cse.lk/api) to pull daily OHLCV bars and official ASPI index values.
"""

from __future__ import annotations

import datetime
import logging
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class CSEScraper:
    """
    Client for querying Colombo Stock Exchange REST API endpoints and
    synchronizing daily historical OHLCV data into local Parquet storage.
    """

    DEFAULT_BASE_URL = "https://www.cse.lk/api"
    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://www.cse.lk",
        "Referer": "https://www.cse.lk/",
    }

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: int = 15,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
    ):
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)

        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST", "GET"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    @staticmethod
    def normalize_symbol(symbol: str) -> str:
        """Standardizes ticker symbol to CSE dot notation (e.g. 'JKH' -> 'JKH.N0000')."""
        symbol = symbol.strip().upper()
        if "." not in symbol and symbol != "ASPI":
            return f"{symbol}.N0000"
        return symbol

    def get_stock_id(self, symbol: str) -> Optional[int]:
        """
        Query companyInfoSummery to retrieve internal integer stock ID.
        """
        formatted = self.normalize_symbol(symbol)
        url = f"{self.base_url}/companyInfoSummery"
        payload = {"symbol": formatted}

        try:
            resp = self.session.post(url, data=payload, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            stock_id = data.get("reqSymbolInfo", {}).get("id")
            if stock_id is not None:
                return int(stock_id)
            logger.warning("No stock ID found in CSE response for %s", formatted)
            return None
        except Exception as exc:
            logger.error("Failed to fetch stock ID for %s: %s", formatted, exc)
            return None

    def fetch_chart_data(self, stock_id: int, period: str = "5") -> List[Dict[str, Any]]:
        """
        Fetch OHLCV chart records for given internal stock ID.
        """
        url = f"{self.base_url}/companyChartDataByStock"
        payload = {"stockId": str(stock_id), "period": str(period)}

        try:
            resp = self.session.post(url, data=payload, timeout=self.timeout)
            resp.raise_for_status()
            payload_data = resp.json()
            return payload_data.get("chartData", [])
        except Exception as exc:
            logger.error("Failed fetching chart data for stockId %s: %s", stock_id, exc)
            return []

    def parse_chart_data(self, symbol: str, raw_records: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Converts raw CSE JSON chart points into standardized OHLCV DataFrame.
        """
        canonical_cols = ["date", "symbol", "open", "high", "low", "close", "volume"]
        if not raw_records:
            return pd.DataFrame(columns=canonical_cols)

        norm_sym = self.normalize_symbol(symbol)
        rows = []
        for idx, pt in enumerate(raw_records):
            t_ms = pt.get("t")
            if not t_ms:
                continue
            dt = datetime.datetime.fromtimestamp(t_ms / 1000.0, tz=datetime.timezone.utc).date()
            close_val = float(pt.get("p", 0.0))
            high_val = float(pt.get("h", close_val)) if pt.get("h") is not None else close_val
            low_val = float(pt.get("l", close_val)) if pt.get("l") is not None else close_val
            volume_val = int(pt.get("q", 0))

            if pt.get("o") is not None:
                open_val = float(pt.get("o"))
            elif idx > 0 and rows:
                open_val = rows[-1]["close"]
            else:
                open_val = close_val

            rows.append({
                "date": pd.to_datetime(dt),
                "symbol": norm_sym,
                "open": float(open_val),
                "high": float(max(high_val, open_val, close_val)),
                "low": float(min(low_val, open_val, close_val)),
                "close": float(close_val),
                "volume": int(volume_val),
            })

        df = pd.DataFrame(rows)
        if not df.empty:
            df = df[df["close"] > 0]
            df = df.sort_values("date").drop_duplicates(subset=["date", "symbol"]).reset_index(drop=True)
        return df

    def pull_latest_ohlcv(self, symbol: str, period: str = "3") -> pd.DataFrame:
        """
        Orchestrates symbol resolution, API querying, and OHLCV parsing.
        """
        stock_id = self.get_stock_id(symbol)
        if stock_id is None:
            logger.warning("Could not resolve stockId for symbol %s via CSE API", symbol)
            return pd.DataFrame(columns=["date", "symbol", "open", "high", "low", "close", "volume"])

        raw_points = self.fetch_chart_data(stock_id, period=period)
        return self.parse_chart_data(symbol, raw_points)

    def fetch_aspi_daily(self) -> Optional[Dict[str, Any]]:
        """
        Query official CSE endpoint POST https://www.cse.lk/api/aspiData
        to retrieve the latest live ASPI index points.
        """
        url = f"{self.base_url}/aspiData"
        try:
            resp = self.session.post(url, data={"period": "1"}, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()

            value = data.get("value")
            t_ms = data.get("timestamp")
            if value is not None and t_ms is not None:
                dt = datetime.datetime.fromtimestamp(t_ms / 1000.0, tz=datetime.timezone.utc).date()
                return {
                    "date": pd.to_datetime(dt),
                    "symbol": "ASPI",
                    "close": float(value),
                    "high": float(data.get("highValue", value)),
                    "low": float(data.get("lowValue", value)),
                    "change": float(data.get("change", 0.0)),
                    "percentage": float(data.get("percentage", 0.0)),
                }
            return None
        except Exception as exc:
            logger.error("Failed fetching live ASPI data from CSE: %s", exc)
            return None

    def sync_to_parquet(
        self,
        symbol: str,
        processed_dir: Union[str, Path] = "data/processed",
        period: str = "3",
    ) -> pd.DataFrame:
        """
        Fetches latest daily OHLCV from CSE and merges into local Parquet cache:
        data/processed/{symbol}.parquet.
        """
        norm_sym = self.normalize_symbol(symbol)
        clean_name = norm_sym.replace(".", "_")
        p_dir = Path(processed_dir)
        p_dir.mkdir(parents=True, exist_ok=True)
        parquet_path = p_dir / f"{clean_name}.parquet"

        new_df = self.pull_latest_ohlcv(norm_sym, period=period)

        if parquet_path.exists():
            existing_df = pd.read_parquet(parquet_path)
            existing_df["date"] = pd.to_datetime(existing_df["date"])
            if not new_df.empty:
                combined = pd.concat([existing_df, new_df], ignore_index=True)
                combined = combined.sort_values("date").drop_duplicates(subset=["date", "symbol"], keep="last").reset_index(drop=True)
            else:
                combined = existing_df
        else:
            combined = new_df

        if not combined.empty:
            combined.to_parquet(parquet_path, index=False)
            logger.info("Synchronized %s to %s (%d records)", norm_sym, parquet_path, len(combined))

        return combined
