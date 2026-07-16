from fastapi import APIRouter, HTTPException
from app.database.connection import SessionLocal
from app.repositories.stock_repository import StockPriceRepository
from app.services.ingestion_service import IngestionService

router = APIRouter()
ingestion_service = IngestionService()


@router.get("/stocks/{symbol}")
def get_stock(symbol: str):
    db = SessionLocal()
    try:
        repo = StockPriceRepository(db)
        records = repo.get_by_symbol(symbol)

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
