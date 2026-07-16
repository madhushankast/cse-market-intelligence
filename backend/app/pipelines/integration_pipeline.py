import logging
import pandas as pd
from sqlalchemy.orm import Session
from app.repositories.stock_repository import StockPriceRepository
from app.data_sources.cbsl.service import CBSLService
from app.data_sources.trends.service import TrendsService
from app.integration.merger import DataMerger
from app.preprocessing.pipeline import ProcessingPipeline
from app.database.models import StockPrice

logger = logging.getLogger(__name__)


class IntegrationPipeline:

    def __init__(self, db: Session):
        self.db = db
        self.stock_repo = StockPriceRepository(db)
        self.cbsl_service = CBSLService()
        self.trends_service = TrendsService()
        self.merger = DataMerger()
        self.processing_pipeline = ProcessingPipeline()

    def run(self) -> int:
        logger.info("Integration Pipeline: Running merge and feature engineering...")

        # Find distinct symbols in DB
        res = self.db.query(StockPrice.symbol).distinct().all()
        symbols = [r[0] for r in res]

        if not symbols:
            logger.warning("No stocks found in DB to integrate.")
            return 0

        # Load macro and trends once
        df_macro = self.cbsl_service.get_macro_indicators()
        df_trends = self.trends_service.get_search_trends("CSE")

        total_rows_integrated = 0

        for symbol in symbols:
            records = self.stock_repo.get_by_symbol(symbol)
            if not records:
                continue

            data = [{
                "symbol": r.symbol,
                "date": r.date,
                "open": r.open,
                "high": r.high,
                "low": r.low,
                "close": r.close,
                "volume": r.volume
            } for r in records]
            df_stock = pd.DataFrame(data)

            # Preprocessing & Indicator calculation
            df_processed = self.processing_pipeline.process(df_stock)

            # Integration (Merge)
            df_merged = self.merger.merge(df_processed, df_macro, df_trends)
            total_rows_integrated += len(df_merged)

            logger.info(f"Successfully integrated {symbol}: {len(df_merged)} rows.")

        return total_rows_integrated
