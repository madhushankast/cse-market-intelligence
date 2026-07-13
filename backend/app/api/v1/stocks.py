from fastapi import APIRouter, HTTPException
from app.database.connection import SessionLocal
from app.database.models import StockPrice
from app.services.ingestion_service import IngestionService

router = APIRouter()
ingestion_service = IngestionService()


@router.get("/stocks/{symbol}")
def get_stock(symbol: str):
    db = SessionLocal()
    try:
        formatted_symbol = symbol if "." in symbol else f"{symbol}.N0000"
        records = db.query(StockPrice).filter(
            (StockPrice.symbol == formatted_symbol) | (StockPrice.symbol == symbol)
        ).order_by(StockPrice.date.asc()).all()

        data = [{
            "symbol": r.symbol,
            "date": r.date,
            "open": r.open,
            "high": r.high,
            "low": r.low,
            "close": r.close,
            "volume": r.volume
        } for r in records]

        return {
            "symbol": symbol,
            "data": data
        }
    finally:
        db.close()


@router.post("/stocks/{symbol}/ingest")
def ingest_stock(symbol: str):
    try:
        records_added = ingestion_service.ingest_stock(symbol)
        return {
            "symbol": symbol,
            "records_added": records_added
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
