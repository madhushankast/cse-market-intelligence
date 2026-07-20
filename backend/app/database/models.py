from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime, timezone
from app.database.connection import Base
from app.models.job_log import JobLog
from app.models.prediction_explanation import PredictionExplanationLog



class StockPrice(Base):

    __tablename__ = "stock_prices"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    symbol = Column(
        String,
        index=True,
        nullable=False
    )


    date = Column(
        String,
        index=True,
        nullable=False
    )


    open = Column(
        Float,
        nullable=False
    )


    high = Column(
        Float,
        nullable=False
    )


    low = Column(
        Float,
        nullable=False
    )


    close = Column(
        Float,
        nullable=False
    )


    volume = Column(
        Integer,
        nullable=False
    )


    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )


class AlternativeData(Base):
    __tablename__ = "alternative_data"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    source = Column(
        String,
        index=True,
        nullable=False
    )
    indicator = Column(
        String,
        index=True,
        nullable=False
    )
    date = Column(
        String,
        index=True,
        nullable=False
    )
    value = Column(
        Float,
        nullable=False
    )
    frequency = Column(
        String,
        nullable=False
    )
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )


class ForecastResult(Base):
    __tablename__ = "forecast_results"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    symbol = Column(
        String,
        index=True,
        nullable=False
    )
    date = Column(
        String,
        index=True,
        nullable=False
    )
    model = Column(
        String,
        nullable=False
    )
    horizon = Column(
        Integer,
        nullable=False
    )
    expected_return = Column(
        Float,
        nullable=False
    )
    forecast_values = Column(
        Text, # Store JSON array
        nullable=False
    )
    explanation_json = Column(
        Text, # Store JSON object
        nullable=True
    )
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )
