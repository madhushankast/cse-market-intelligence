from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime, timezone
from app.database.connection import Base


class JobLog(Base):
    __tablename__ = "job_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    pipeline = Column(
        String,
        index=True,
        nullable=False
    )

    started_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    finished_at = Column(
        DateTime,
        nullable=True
    )

    status = Column(
        String,
        nullable=False
    )  # "Running", "Success", "Failed"

    rows_processed = Column(
        Integer,
        default=0
    )

    error_message = Column(
        Text,
        nullable=True
    )
