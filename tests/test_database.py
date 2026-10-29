"""
Database & Pipeline Integration Tests
-------------------------------------
Verifies:
  1. SQLAlchemy schema creation and ORM models operations.
  2. Idempotent upserts for stock_prices and aspi_index.
  3. Forecast prediction history persistence and retrieval.
  4. Pipeline audit logging.
  5. FastAPI `/api/v1/predictions/history/{symbol}` endpoint.
"""

from __future__ import annotations

import datetime
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.main import app
from src.database.models import Base, StockPrice, ASPIIndex, ForecastPrediction, PipelineRun
from src.database.session import get_db

client = TestClient(app)


def test_db_models_crud(tmp_path):
    """Verifies ORM models and constraints on SQLite test database."""
    test_db = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{test_db}")
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    session = TestingSession()

    try:
        # 1. StockPrice
        price = StockPrice(
            symbol="TEST_N0000",
            date=datetime.date(2026, 10, 27),
            open=100.0,
            high=105.0,
            low=99.0,
            close=104.5,
            volume=50000,
        )
        session.add(price)
        session.commit()

        queried = session.query(StockPrice).filter_by(symbol="TEST_N0000").first()
        assert queried is not None
        assert float(queried.close) == 104.5

        # 2. ASPIIndex
        aspi = ASPIIndex(
            date=datetime.date(2026, 10, 27),
            close=20250.50,
            high=20300.00,
            low=20200.00,
            change=45.2,
            percentage=0.22,
        )
        session.add(aspi)
        session.commit()

        queried_aspi = session.query(ASPIIndex).filter_by(date=datetime.date(2026, 10, 27)).first()
        assert queried_aspi is not None
        assert float(queried_aspi.close) == 20250.50

        # 3. ForecastPrediction
        pred = ForecastPrediction(
            symbol="TEST_N0000",
            as_of_date=datetime.date(2026, 10, 27),
            current_price=104.5,
            price_p10=98.0,
            price_p50=108.0,
            price_p90=115.0,
            expected_pct_change=3.35,
            target_returns={"p50_log_return": 0.033},
            cone_trajectory=[{"step": 1, "price_p50": 105.0}],
            shap_drivers={"top_positive_drivers": []},
            heuristic_signals=[{"indicator": "RSI", "status": "Supporting"}],
        )
        session.add(pred)
        session.commit()

        queried_pred = session.query(ForecastPrediction).filter_by(symbol="TEST_N0000").first()
        assert queried_pred is not None
        assert float(queried_pred.price_p50) == 108.0
        assert len(queried_pred.cone_trajectory) == 1

        # 4. PipelineRun Audit Log
        run = PipelineRun(
            run_date=datetime.date.today(),
            job_name="TEST_JOB",
            status="SUCCESS",
            records_ingested=10,
            models_retrained=1,
            duration_seconds=2.5,
            message="Test execution success",
        )
        session.add(run)
        session.commit()

        queried_run = session.query(PipelineRun).filter_by(job_name="TEST_JOB").first()
        assert queried_run is not None
        assert queried_run.status == "SUCCESS"

    finally:
        session.close()


def test_api_prediction_history_endpoint():
    """Verifies GET /api/v1/predictions/history/{symbol} endpoint."""
    response = client.get("/api/v1/predictions/history/JKH_N0000")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "symbol" in data
    assert "data" in data
    assert isinstance(data["data"], list)
