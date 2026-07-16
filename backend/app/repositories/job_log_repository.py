from datetime import datetime, timezone
from app.models.job_log import JobLog
from app.repositories.base import BaseRepository


class JobLogRepository(BaseRepository):

    def create_log(self, pipeline: str, started_at: datetime = None) -> JobLog:
        if started_at is None:
            started_at = datetime.now(timezone.utc)
        log = JobLog(
            pipeline=pipeline,
            started_at=started_at,
            status="Running",
            rows_processed=0
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def update_log(self, log_id: int, status: str, rows_processed: int = 0, error_message: str = None, finished_at: datetime = None) -> JobLog:
        if finished_at is None:
            finished_at = datetime.now(timezone.utc)
        log = self.db.query(JobLog).filter(JobLog.id == log_id).first()
        if log:
            log.status = status
            log.rows_processed = rows_processed
            log.error_message = error_message
            log.finished_at = finished_at
            self.db.commit()
            self.db.refresh(log)
        return log

    def get_latest_logs(self, limit: int = 20) -> list[JobLog]:
        return self.db.query(JobLog).order_by(JobLog.started_at.desc()).limit(limit).all()

    def get_last_pipeline_status(self) -> tuple:
        res = self.db.query(JobLog).order_by(JobLog.started_at.desc()).first()
        if res:
            return res.status, res.started_at
        return "N/A", None
