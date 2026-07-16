import logging
from app.data_sources.cse.service import CSEService
from app.database.connection import SessionLocal
from app.database.models import StockPrice
from app.repositories.stock_repository import StockPriceRepository

logger = logging.getLogger(__name__)


class IngestionService:

    def __init__(self):
        self.cse_service = CSEService()

    def ingest_stock(self, symbol: str) -> int:
        formatted_symbol = symbol if "." in symbol else f"{symbol}.N0000"

        # Fetch data via CSEService (which uses the REST client, falling back to CSV if offline)
        df = self.cse_service.get_stock_prices(symbol, period="5")
        if df.empty:
            logger.warning(f"No records returned for {symbol} ingestion.")
            return 0

        db = SessionLocal()
        repo = StockPriceRepository(db)
        records_added = 0
        try:
            for _, row in df.iterrows():
                # Check for existing records to ensure idempotency and prevent duplicates
                exists = repo.check_exists(row["symbol"], row["date"])

                if not exists:
                    db_record = StockPrice(
                        symbol=row["symbol"],
                        date=row["date"],
                        open=float(row["open"]),
                        high=float(row["high"]),
                        low=float(row["low"]),
                        close=float(row["close"]),
                        volume=int(row["volume"])
                    )
                    repo.add(db_record)
                    records_added += 1
            db.commit()
            logger.info(f"Ingested {records_added} new records for {formatted_symbol}.")
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to ingest stock {symbol}: {e}")
            raise e
        finally:
            db.close()

        return records_added
