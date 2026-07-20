from fastapi import APIRouter
from .health import router as health_router
from .stocks import router as stocks_router
from .analytics import router as analytics_router
from .system import router as system_router
from .predictions import router as predictions_router
from .explanations import router as explanations_router
from .forecasting import router as forecasting_router
from .dashboard import router as dashboard_router

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

api_router.include_router(
    system_router,
    tags=["System"]
)

api_router.include_router(
    predictions_router,
    tags=["Predictions"]
)

api_router.include_router(
    explanations_router,
    tags=["Explainability"]
)

api_router.include_router(
    forecasting_router,
    tags=["Forecasting"]
)

api_router.include_router(
    dashboard_router,
    tags=["Dashboard"]
)
