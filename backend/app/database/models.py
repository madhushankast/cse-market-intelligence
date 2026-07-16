from sqlalchemy import Column, Integer, String, Float, DateTime
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
