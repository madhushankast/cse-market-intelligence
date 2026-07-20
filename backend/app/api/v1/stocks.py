"""
stocks.py — Stock price API routes
"""
from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.database.connection import SessionLocal
from app.repositories.stock_repository import StockPriceRepository
from app.services.ingestion_service import IngestionService
from app.services.bulk_ingestion_service import BulkIngestionService

router = APIRouter()

_ingestion_svc = IngestionService()
_bulk_svc      = BulkIngestionService()


# ── Read routes ─────────────────────────────────────────────────────────────────

@router.get("/stocks/{symbol}")
def get_stock(symbol: str):
    """Return all stored OHLCV rows for a symbol."""
    db = SessionLocal()
    try:
        repo    = StockPriceRepository(db)
        records = repo.get_by_symbol(symbol.upper())
        data = [{
            "symbol": r.symbol,
            "date":   str(r.date),
            "open":   r.open,
            "high":   r.high,
            "low":    r.low,
            "close":  r.close,
            "volume": r.volume,
        } for r in records]
        return {"symbol": symbol.upper(), "count": len(data), "data": data}
    finally:
        db.close()


@router.get("/stocks/{symbol}/status")
def get_stock_status(symbol: str):
    """Return data-freshness info for a symbol."""
    status = _bulk_svc.data_status()
    sym = symbol.upper()
    if sym not in status:
        raise HTTPException(status_code=404, detail=f"Symbol '{sym}' is not tracked.")
    return status[sym]


# ── Ingestion routes ────────────────────────────────────────────────────────────

@router.post("/stocks/{symbol}/ingest")
def ingest_stock(symbol: str):
    """
    Download 2 years of OHLCV history for a single symbol via Yahoo Finance
    (falls back to synthetic GBM data if the ticker is unavailable).
    """
    try:
        result = _bulk_svc.ingest_symbol(symbol.upper())
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(exc)}")


@router.post("/stocks/ingest/all")
def ingest_all_stocks(background_tasks: BackgroundTasks):
    """
    Trigger a full 2-year history download for ALL tracked symbols.
    Runs in the background so the response is immediate.
    Symbols: COMB, JKH, DIST, SAMP, HNB
    """
    background_tasks.add_task(_bulk_svc.ingest_all)
    return {
        "message": "Full ingestion started in background for all symbols.",
        "symbols": ["COMB", "JKH", "DIST", "SAMP", "HNB"],
    }


@router.post("/stocks/refresh")
def refresh_stock_data(background_tasks: BackgroundTasks):
    """
    Incremental refresh — downloads only data newer than what is already stored.
    Safe to call daily. Runs in the background.
    """
    background_tasks.add_task(_bulk_svc.refresh_incremental)
    return {
        "message": "Incremental refresh started in background.",
        "note": "Call GET /stocks/data-status to check progress.",
    }


@router.get("/stocks/data-status")
def get_data_status():
    """
    Return data-freshness status for all tracked symbols.
    Shows CSV last date, DB last date, row counts, and staleness flag.
    """
    return _bulk_svc.data_status()
