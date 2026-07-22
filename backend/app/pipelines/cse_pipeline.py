import logging
from sqlalchemy.orm import Session
from app.data_sources.cse.service import CSEService
from app.utils.trading_calendar import is_trading_day
from app.repositories.stock_repository import StockPriceRepository
from app.validation.validator import DataValidator
from app.database.models import StockPrice

logger = logging.getLogger(__name__)


class CSEPipeline:

    def __init__(self, db: Session):
        self.db = db
        self.cse_service = CSEService()
        self.repo = StockPriceRepository(db)

    def run(self, symbols: list[str] = None) -> int:
        if not symbols:
            # Import the full set of tracked symbols from the yfinance client configuration
            from app.data_sources.cse.yfinance_client import YAHOO_TICKER_MAP
            symbols = list(YAHOO_TICKER_MAP.keys())

        total_inserted = 0
        for symbol in symbols:
            logger.info(f"CSE Pipeline: Processing symbol {symbol}")
            try:
                df = self.cse_service.get_stock_prices(symbol, period="5")
                if df.empty:
                    logger.warning(f"No stock data fetched for {symbol}")
                    continue

                # Run quality validation check
                report = DataValidator.validate_stock_data(df)
                if not report["is_valid"]:
                    logger.error(f"Validation failed for stock {symbol}: {report['errors']}")
                    # If validation fails, we log and skip this symbol to prevent corrupting the DB
                    continue

                for _, row in df.iterrows():
                    # Format symbol name consistently
                    sym = row["symbol"]
                    dt = row["date"]
                    # Skip non‑trading days
                    from datetime import datetime
                    dt_obj = datetime.strptime(dt, "%Y-%m-%d").date() if isinstance(dt, str) else dt
                    if not is_trading_day(dt_obj):
                        continue
                    if not self.repo.check_exists(sym, dt):
                        record = StockPrice(
                            symbol=sym,
                            date=dt,
                            open=float(row["open"]),
                            high=float(row["high"]),
                            low=float(row["low"]),
                            close=float(row["close"]),
                            volume=int(row["volume"])
                        )
                        self.repo.add(record)
                        total_inserted += 1
            except Exception as e:
                logger.error(f"Failed to process stock {symbol} in pipeline: {e}")

        self.db.commit()
        return total_inserted
