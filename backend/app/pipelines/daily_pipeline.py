import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.repositories.job_log_repository import JobLogRepository
from app.pipelines.cse_pipeline import CSEPipeline

logger = logging.getLogger(__name__)


class DailyPipelineOrchestrator:

    def __init__(self, db: Session):
        self.db = db
        self.job_repo = JobLogRepository(db)

    def run(self, symbols: list[str] = None) -> dict:
        started_at = datetime.now(timezone.utc)
        job_log = self.job_repo.create_log("Daily Pipeline", started_at)

        try:
            # 1. CSE Stock Ingestion
            cse = CSEPipeline(self.db)
            cse_rows = cse.run(symbols)

            self.job_repo.update_log(
                log_id=job_log.id,
                status="Success",
                rows_processed=cse_rows,
                error_message=None
            )

            return {
                "status": "Success",
                "job_id": job_log.id,
                "rows_processed": cse_rows,
                "cse_rows": cse_rows,
                "cbsl_rows": 0,
                "trends_rows": 0,
                "integration_rows": 0
            }

        except Exception as e:
            logger.error(f"Error executing Daily Pipeline: {e}")
            self.db.rollback()
            self.job_repo.update_log(
                log_id=job_log.id,
                status="Failed",
                rows_processed=0,
                error_message=str(e)
            )
            return {
                "status": "Failed",
                "job_id": job_log.id,
                "error": str(e)
            }

