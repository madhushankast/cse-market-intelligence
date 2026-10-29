"""
CSE Market Intelligence Platform - Production API Server
--------------------------------------------------------
FastAPI backend exposing endpoints for 30-day multi-quantile stock return forecasting,
TreeSHAP explainability, and technical heuristic signals.
"""

from __future__ import annotations

from pathlib import Path
import sys
import time

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.predict import router as predict_router
from api.routes.explain import router as explain_router

SERVER_START_TIME = time.time()

app = FastAPI(
    title="Colombo Stock Exchange (CSE) Market Intelligence API",
    description=(
        "Production-grade MLOps serving engine for 30-day cumulative log return forecasting "
        "using Multi-Quantile LightGBM, TreeSHAP feature attribution, and dual-layer heuristics."
    ),
    version="2.0.0",
)

# Enable CORS for Streamlit / Vite React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers under /api/v1
app.include_router(predict_router, prefix="/api/v1", tags=["Forecasting"])
app.include_router(explain_router, prefix="/api/v1", tags=["Explainability"])


@app.get("/health", tags=["System"])
def health_check():
    """
    Liveness and readiness health probe returning system uptime and model inventory.
    """
    models_dir = Path("models")
    model_folders = []
    if models_dir.exists():
        model_folders = [d.name for d in models_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]

    processed_dir = Path("data/processed")
    stock_parquets = []
    if processed_dir.exists():
        stock_parquets = [f.stem for f in processed_dir.glob("*.parquet") if f.stem != "ASPI"]

    uptime = round(time.time() - SERVER_START_TIME, 2)

    return {
        "status": "healthy",
        "service": "cse-market-intelligence-api",
        "version": "2.0.0",
        "uptime_seconds": uptime,
        "models_count": len(model_folders),
        "available_models": sorted(model_folders),
        "available_equities_count": len(stock_parquets),
    }


@app.get("/", tags=["System"])
def root_info():
    """Root metadata and API documentation navigation."""
    return {
        "name": "Colombo Stock Exchange Market Intelligence Platform",
        "version": "2.0.0",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
        "endpoints": {
            "stocks": "GET /api/v1/stocks",
            "predict_post": "POST /api/v1/predict",
            "predict_get": "GET /api/v1/predict/{symbol}",
            "explain": "GET /api/v1/explain/{symbol}",
            "health": "GET /health",
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
