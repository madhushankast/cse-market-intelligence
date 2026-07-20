"""
yfinance_client.py
─────────────────
Yahoo Finance client for CSE-listed stocks.

CSE stocks are listed on Yahoo Finance with the suffix '.CM':
  COMB  →  COMB.CM   (Commercial Bank of Ceylon)
  JKH   →  JKH.CM    (John Keells Holdings)
  DIST  →  DIST.CM   (Distilleries Company)
  SAMP  →  SAMP.CM   (Sampath Bank)
  HNB   →  HNB.CM    (Hatton National Bank)

Falls back to generating realistic synthetic data if the ticker is
unavailable on Yahoo Finance (e.g. insufficient history, delisted, etc.)
"""

import logging
import os
import pandas as pd
import numpy as np
from datetime import date, timedelta

logger = logging.getLogger(__name__)

# ── Mapping of internal symbol → Yahoo Finance ticker ──────────────────────────
YAHOO_TICKER_MAP = {
    "COMB": "COMB.CM",
    "JKH":  "JKH.CM",
    "DIST": "DIST.CM",
    "SAMP": "SAMP.CM",
    "HNB":  "HNB.CM",
}

# ── Realistic base price seeds per symbol (LKR) ────────────────────────────────
BASE_PRICES = {
    "COMB": 95.0,
    "JKH":  185.0,
    "DIST": 18.5,
    "SAMP": 72.0,
    "HNB":  165.0,
}

CSV_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "data", "raw", "cse"
)


class YFinanceCSEClient:
    """
    Downloads CSE stock price history from Yahoo Finance.
    Falls back to synthetic data generation if the ticker
    is not available on Yahoo Finance.
    """

    def get_historical_data(
        self,
        symbol: str,
        start: str = None,
        end: str = None,
        period_years: int = 2,
    ) -> pd.DataFrame:
        """
        Download OHLCV data for `symbol` from CSE API via CSEService,
        with fallback to Yahoo Finance and then to synthetic data.
        """
        # Try CSEService first to get real CSE API data
        try:
            from app.data_sources.cse.service import CSEService
            cse_svc = CSEService()
            logger.info(f"[YFinance/CSE] Attempting to fetch {symbol} from CSEService")
            df = cse_svc.get_stock_prices(symbol, period="5")
            if not df.empty:
                df['date'] = pd.to_datetime(df['date']).dt.date.astype(str)
                if start:
                    df = df[df['date'] >= start]
                if end:
                    df = df[df['date'] <= end]
                if not df.empty:
                    logger.info(f"[YFinance/CSE] Successfully fetched {len(df)} real rows from CSE API")
                    df = df[["symbol", "date", "open", "high", "low", "close", "volume"]]
                    return df.sort_values("date").reset_index(drop=True)
        except Exception as e:
            logger.error(f"[YFinance/CSE] CSEService fetch failed for {symbol}: {e}. Trying Yahoo Finance.")

        try:
            import yfinance as yf
        except ImportError:
            logger.error("yfinance is not installed. Run: pip install yfinance")
            return pd.DataFrame()

        ticker_sym = YAHOO_TICKER_MAP.get(symbol.upper(), f"{symbol}.CM")

        if start is None:
            start = (date.today() - timedelta(days=period_years * 365)).isoformat()
        if end is None:
            end = date.today().isoformat()

        logger.info(f"[YFinance] Downloading {ticker_sym} from {start} to {end}")

        try:
            ticker = yf.Ticker(ticker_sym)
            df = ticker.history(start=start, end=end, auto_adjust=True)

            if df.empty:
                if start is not None:
                    logger.info(f"[YFinance] No new incremental data for {ticker_sym}. Returning empty.")
                    return pd.DataFrame()
                logger.warning(
                    f"[YFinance] No data returned for {ticker_sym}. "
                    "Generating synthetic fallback."
                )
                return self._generate_synthetic(symbol, start, end)

            # Normalise column names
            df = df.reset_index()
            df.rename(columns={
                "Date":   "date",
                "Open":   "open",
                "High":   "high",
                "Low":    "low",
                "Close":  "close",
                "Volume": "volume",
            }, inplace=True)

            # Keep only trading days (date may already be tz-aware)
            df["date"] = pd.to_datetime(df["date"]).dt.date.astype(str)
            df["symbol"] = symbol.upper()
            df = df[["symbol", "date", "open", "high", "low", "close", "volume"]]
            df = df.dropna(subset=["close"])
            df = df.sort_values("date").reset_index(drop=True)

            logger.info(
                f"[YFinance] Fetched {len(df)} rows for {ticker_sym} "
                f"({df['date'].iloc[0]} → {df['date'].iloc[-1]})"
            )
            return df

        except Exception as exc:
            if start is not None:
                logger.error(f"[YFinance] Incremental fetch failed for {ticker_sym}: {exc}. Returning empty.")
                return pd.DataFrame()
            logger.error(
                f"[YFinance] Download failed for {ticker_sym}: {exc}. "
                "Generating synthetic fallback."
            )
            return self._generate_synthetic(symbol, start, end)

    # ── Synthetic fallback ──────────────────────────────────────────────────────

    def _generate_synthetic(
        self, symbol: str, start: str, end: str
    ) -> pd.DataFrame:
        """
        Produce realistic-looking OHLCV data using geometric Brownian motion.
        Used only when the Yahoo Finance ticker is unavailable.
        """
        logger.info(f"[Synthetic] Generating data for {symbol} ({start} → {end})")

        rng = np.random.default_rng(seed=sum(ord(c) for c in symbol))

        # Build a calendar of trading days (Mon–Fri)
        all_days = pd.date_range(start=start, end=end, freq="B")  # business days
        n = len(all_days)
        if n == 0:
            return pd.DataFrame(
                columns=["symbol", "date", "open", "high", "low", "close", "volume"]
            )

        base = BASE_PRICES.get(symbol.upper(), 100.0)

        # GBM parameters
        mu    = 0.0003   # small daily drift
        sigma = 0.012    # daily volatility (~19% annualised)

        returns = rng.normal(mu, sigma, n)
        close_prices = base * np.cumprod(1 + returns)

        # Derive OHLV from close
        daily_range_pct = rng.uniform(0.005, 0.025, n)
        high_prices  = close_prices * (1 + daily_range_pct / 2)
        low_prices   = close_prices * (1 - daily_range_pct / 2)
        open_prices  = np.roll(close_prices, 1)
        open_prices[0] = base

        volumes = rng.integers(500_000, 5_000_000, n)

        df = pd.DataFrame({
            "symbol": symbol.upper(),
            "date":   all_days.strftime("%Y-%m-%d"),
            "open":   np.round(open_prices, 2),
            "high":   np.round(high_prices, 2),
            "low":    np.round(low_prices,  2),
            "close":  np.round(close_prices, 2),
            "volume": volumes,
        })

        return df

    # ── CSV persistence helpers ─────────────────────────────────────────────────

    def save_to_csv(self, df: pd.DataFrame, symbol: str, merge: bool = False) -> str:
        """
        Save data to the raw CSE CSV file.

        Args:
            df:     DataFrame with columns date/open/high/low/close/volume.
            symbol: Stock symbol (e.g. 'COMB').
            merge:  If True, append and deduplicate (for incremental updates).
                    If False (default), overwrite with fresh data.
        """
        os.makedirs(CSV_DIR, exist_ok=True)
        path = os.path.join(CSV_DIR, f"{symbol.upper()}.csv")

        cols = ["date", "open", "high", "low", "close", "volume"]
        new_data = df[cols].copy().sort_values("date")

        if merge and os.path.exists(path):
            existing = pd.read_csv(path)
            combined = pd.concat([existing, new_data])
            combined = combined.drop_duplicates(subset=["date"]).sort_values("date")
            combined.to_csv(path, index=False)
            logger.info(f"[CSV] Merged → {len(combined)} rows at {path}")
        else:
            new_data.to_csv(path, index=False)
            logger.info(f"[CSV] Saved {len(new_data)} rows to {path}")

        return path

    def get_last_date_in_csv(self, symbol: str) -> str | None:
        """Return the most recent date in the CSV, or None if the file is missing."""
        path = os.path.join(CSV_DIR, f"{symbol.upper()}.csv")
        if not os.path.exists(path):
            return None
        df = pd.read_csv(path)
        if df.empty or "date" not in df.columns:
            return None
        return df["date"].max()
