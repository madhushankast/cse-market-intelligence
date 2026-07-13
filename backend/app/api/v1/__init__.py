from fastapi import APIRouter
from .health import router as health_router
from .stocks import router as stocks_router
from .analytics import router as analytics_router

api_router = APIRouter()

api_router.include_router(
    health_router,
    tags=["Health"]
)

api_router.include_router(
    stocks_router,
    tags=["Stocks"]
)

api_router.include_router(
    analytics_router,
    tags=["Analytics"]
)
