"""
PredictionExplanationLog — persists feature-level explanation data for auditing
and future time-series research.

One row per feature per explanation run. A single API call for 10 top features
writes 10 rows.

Use cases:
    - Audit trail: which features drove predictions on which dates
    - Research: track feature importance stability over time
    - Portfolio analysis: compare feature drivers across symbols
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime, timezone
from app.database.connection import Base


class PredictionExplanationLog(Base):
    __tablename__ = "prediction_explanations"

    id = Column(Integer, primary_key=True, index=True)

    # Prediction context
    symbol      = Column(String,  nullable=False, index=True)
    model       = Column(String,  nullable=False)
    prediction  = Column(Float,   nullable=True)
    confidence  = Column(Float,   nullable=True)
    baseline_value = Column(Float, nullable=True)

    # Explanation method
    explanation_method = Column(String, nullable=False)

    # Feature-level data (one row per feature)
    feature_name = Column(String, nullable=False)
    impact       = Column(Float,  nullable=False)
    abs_impact   = Column(Float,  nullable=False)
    direction    = Column(String, nullable=False)  # 'positive' | 'negative'
    feature_rank = Column(Integer, nullable=True)  # 1 = most important

    # Optional warning from the explainer
    warning = Column(Text, nullable=True)

    # Timestamp
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
