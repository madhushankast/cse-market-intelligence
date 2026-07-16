from fastapi import APIRouter, HTTPException
import pandas as pd
import numpy as np
from app.database.connection import SessionLocal
from app.repositories.stock_repository import StockPriceRepository
from app.preprocessing.pipeline import ProcessingPipeline
from app.data_sources.cbsl.service import CBSLService
from app.data_sources.trends.service import TrendsService
from app.integration.merger import DataMerger

router = APIRouter()
pipeline = ProcessingPipeline()
cbsl_service = CBSLService()
trends_service = TrendsService()
merger = DataMerger()


def clean_val(val):
    if val is None or pd.isna(val) or np.isinf(val):
        return None
    return float(val)


@router.get("/analytics/stocks/{symbol}")
def get_analytics(symbol: str):
    db = SessionLocal()
    try:
        repo = StockPriceRepository(db)
        records = repo.get_by_symbol(symbol)

        if not records:
            raise HTTPException(
                status_code=404,
                detail=f"No stock data found in DB for {symbol}. Run ingestion POST first."
            )

        # Convert to DataFrame
        data = [{
            "symbol": r.symbol,
            "date": r.date,
            "open": r.open,
            "high": r.high,
            "low": r.low,
            "close": r.close,
            "volume": r.volume
        } for r in records]

        df_raw = pd.DataFrame(data)

        # Run preprocessing and indicator builder pipeline
        df_processed = pipeline.process(df_raw)

        # Grab the latest daily row
        latest_row = df_processed.iloc[-1]

        return {
            "symbol": symbol,
            "features": {
                "close": clean_val(latest_row.get("close")),
                "daily_return": clean_val(latest_row.get("daily_return")),
                "rsi": clean_val(latest_row.get("rsi")),
                "sma_20": clean_val(latest_row.get("sma_20")),
                "sma_50": clean_val(latest_row.get("sma_50")),
                "macd": clean_val(latest_row.get("macd")),
                "volatility": clean_val(latest_row.get("volatility")),
                "date": latest_row.get("date").strftime("%Y-%m-%d")
            }
        }
    finally:
        db.close()


@router.get("/analytics/stocks/{symbol}/integrated")
def get_integrated_data(symbol: str):
    db = SessionLocal()
    try:
        repo = StockPriceRepository(db)
        records = repo.get_by_symbol(symbol)

        if not records:
            raise HTTPException(
                status_code=404,
                detail=f"No stock data found in DB for {symbol}. Run ingestion POST first."
            )

        # 1. Stocks DataFrame
        data = [{
            "symbol": r.symbol,
            "date": r.date,
            "close": r.close,
            "volume": r.volume
        } for r in records]
        df_stock = pd.DataFrame(data)

        # 2. Macro Indicators DataFrame
        df_macro = cbsl_service.get_macro_indicators()

        # 3. Google Trends DataFrame (defaulting to keyword "CSE")
        df_trends = trends_service.get_search_trends("CSE")

        # 4. Merge
        df_merged = merger.merge(df_stock, df_macro, df_trends)

        # 5. Format return payload
        output = []
        for _, row in df_merged.iterrows():
            output.append({
                "date": row["date"].strftime("%Y-%m-%d"),
                "symbol": row["symbol"],
                "close": clean_val(row["close"]),
                "volume": int(row["volume"]),
                "inflation": clean_val(row.get("inflation")),
                "usd_lkr": clean_val(row.get("usd_lkr")),
                "interest_rate": clean_val(row.get("interest_rate")),
                "trend_score": clean_val(row.get("trend_score"))
            })

        return {
            "symbol": symbol,
            "count": len(output),
            "data": output
        }
    finally:
        db.close()
