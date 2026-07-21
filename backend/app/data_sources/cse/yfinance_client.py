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
  MADU  →  MADU.CM   (Madulsima Plantations)

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
    "LOLC": "LOLC.CM",
    "AAIC": "AAIC.CM",
    "CARG": "CARG.CM",
    "AHUN": "AHUN.CM",
    "HAYL": "HAYL.CM",
    "HEMA": "HEMA.CM",
    "ACL":  "ACL.CM",
    "TKYO": "TKYO.CM",
    "LIOC": "LIOC.CM",
    "LWL":  "LWL.CM",
    "EXPO": "EXPO.CM",
    "UML":  "UML.CM",
    "ODEL": "ODEL.CM",
    "RICH": "RICH.CM",
    "OSEA": "OSEA.CM",
    "KGAL": "KGAL.CM",
    "MADU": "MADU.CM",
    "SEYB": "SEYB.CM",
    "NDB":  "NDB.CM",
    "SLTL": "SLTL.CM",
    "DIAL": "DIAL.CM",
}

# ── Realistic base price seeds per symbol (LKR) ────────────────────────────────
BASE_PRICES = {
    "COMB": 95.0,
    "JKH":  185.0,
    "DIST": 18.5,
    "SAMP": 72.0,
    "HNB":  165.0,
    "LOLC": 420.0,
    "AAIC": 24.5,
    "CARG": 340.0,
    "AHUN": 68.0,
    "HAYL": 105.0,
    "HEMA": 82.0,
    "ACL":  85.0,
    "TKYO": 54.0,
    "LIOC": 125.0,
    "LWL":  52.0,
    "EXPO": 145.0,
    "UML":  62.0,
    "ODEL": 15.0,
    "RICH": 22.0,
    "OSEA": 17.5,
    "KGAL": 46.0,
    "MADU": 14.2,
    "SEYB": 48.0,
    "NDB":  64.0,
    "SLTL": 92.0,
    "DIAL": 11.5,
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
        sym_clean = symbol.upper()

        # Try CSEService first to get real CSE API data
        try:
            from app.data_sources.cse.service import CSEService
            cse_svc = CSEService()
            logger.info(f"[YFinance/CSE] Attempting to fetch {sym_clean} from CSEService")
            df = cse_svc.get_stock_prices(sym_clean, period="5")
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
            logger.error(f"[YFinance/CSE] CSEService fetch failed for {sym_clean}: {e}. Trying Yahoo Finance.")

        try:
            import yfinance as yf
        except ImportError:
            logger.error("yfinance is not installed. Generating synthetic data.")
            return self._generate_synthetic(sym_clean, start, end)

        ticker_sym = YAHOO_TICKER_MAP.get(sym_clean, f"{sym_clean}.CM")

        if start is None:
            start = (date.today() - timedelta(days=period_years * 365)).isoformat()
        if end is None:
            end = date.today().isoformat()

        logger.info(f"[YFinance] Downloading {ticker_sym} from {start} to {end}")

        try:
            ticker = yf.Ticker(ticker_sym)
            df = ticker.history(start=start, end=end, auto_adjust=True)

            if df.empty:
                logger.warning(f"[YFinance] No data returned for {ticker_sym}. Generating synthetic fallback.")
                return self._generate_synthetic(sym_clean, start, end)

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

            df["date"] = pd.to_datetime(df["date"]).dt.date.astype(str)
            df["symbol"] = sym_clean
            df = df[["symbol", "date", "open", "high", "low", "close", "volume"]]
            df = df.dropna(subset=["close"])
            df = df.sort_values("date").reset_index(drop=True)

            if df.empty:
                return self._generate_synthetic(sym_clean, start, end)

            return df

        except Exception as exc:
            logger.error(f"[YFinance] Download failed for {ticker_sym}: {exc}. Generating synthetic fallback.")
            return self._generate_synthetic(sym_clean, start, end)

    # ── Synthetic fallback ──────────────────────────────────────────────────────

    def _generate_synthetic(
        self, symbol: str, start: str = None, end: str = None
    ) -> pd.DataFrame:
        """
        Produce realistic-looking OHLCV data using geometric Brownian motion.
        Used when the Yahoo Finance / CSE API is unavailable.
        """
        sym_clean = symbol.upper()
        if start is None:
            start = (date.today() - timedelta(days=2 * 365)).isoformat()
        if end is None:
            end = date.today().isoformat()

        logger.info(f"[Synthetic] Generating data for {sym_clean} ({start} → {end})")

        rng = np.random.default_rng(seed=sum(ord(c) for c in sym_clean))

        # Generate trading dates (excluding weekends)
        dates = pd.date_range(start=start, end=end, freq="B")
        n_days = len(dates)

        if n_days == 0:
            return pd.DataFrame()

        base_price = BASE_PRICES.get(sym_clean, 50.0)

        # GBM parameters
        mu = 0.0003
        sigma = 0.018

        daily_returns = rng.normal(loc=mu, scale=sigma, size=n_days)
        price_path = base_price * np.exp(np.cumsum(daily_returns))

        records = []
        for dt, close_p in zip(dates, price_path):
            intra_vol = rng.uniform(0.005, 0.025)
            high_p = close_p * (1.0 + intra_vol * 0.7)
            low_p = close_p * (1.0 - intra_vol * 0.7)
            open_p = rng.uniform(low_p, high_p)
            volume = int(rng.uniform(10_000, 500_000))

            records.append({
                "symbol": sym_clean,
                "date": dt.strftime("%Y-%m-%d"),
                "open": round(float(open_p), 2),
                "high": round(float(high_p), 2),
                "low": round(float(low_p), 2),
                "close": round(float(close_p), 2),
                "volume": volume,
            })

        df = pd.DataFrame(records)
        return df.sort_values("date").reset_index(drop=True)

    def save_to_csv(self, df: pd.DataFrame, symbol: str) -> str:
        """Save historical DataFrame to data/raw/cse/<SYMBOL>.csv"""
        os.makedirs(CSV_DIR, exist_ok=True)
        path = os.path.join(CSV_DIR, f"{symbol.upper()}.csv")
        df.to_csv(path, index=False)
        logger.info(f"[YFinance] Saved {len(df)} rows to {path}")
        return path
