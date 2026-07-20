import logging
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import settings
from app.database.connection import create_tables

logger = logging.getLogger(__name__)


def _auto_ingest_missing():
    """
    Background startup task: checks each tracked symbol and ingests data
    for any that are missing or empty. This runs once when the server boots.
    """
    try:
        # Import here to avoid circular deps at module load time
        from app.services.bulk_ingestion_service import BulkIngestionService
        svc = BulkIngestionService()

        status = svc.data_status()
        missing = [sym for sym, info in status.items() if info["needs_ingest"] or info["db_row_count"] == 0]

        if missing:
            logger.info(f"[Startup] Auto-ingesting missing symbols: {missing}")
            for sym in missing:
                try:
                    result = svc.ingest_symbol(sym)
                    logger.info(f"[Startup] {sym}: {result}")
                except Exception as exc:
                    logger.error(f"[Startup] Failed to ingest {sym}: {exc}")
        else:
            logger.info("[Startup] All symbols already have data. Running incremental refresh...")
            try:
                svc.refresh_incremental()
            except Exception as exc:
                logger.error(f"[Startup] Incremental refresh failed: {exc}")

    except Exception as exc:
        logger.error(f"[Startup] Auto-ingest routine failed: {exc}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──
    create_tables()
    # Kick off data ingest in a daemon thread so it doesn't block startup
    t = threading.Thread(target=_auto_ingest_missing, daemon=True, name="auto-ingest")
    t.start()
    logger.info("[Startup] Auto-ingest thread launched.")
    
    # Start APScheduler for daily weekday updates
    from app.ingestion.scheduler import start_scheduler
    try:
        start_scheduler()
    except Exception as exc:
        logger.error(f"[Startup] Failed to start scheduler: {exc}")
        
    yield
    # ── Shutdown ──
    from app.ingestion.scheduler import shutdown_scheduler
    try:
        shutdown_scheduler()
    except Exception as exc:
        logger.error(f"[Shutdown] Failed to stop scheduler: {exc}")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    api_router,
    prefix="/api/v1"
)


@app.get("/")
def root():
    return {"message": "CSE Market Intelligence API"}
