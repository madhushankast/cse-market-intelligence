import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.repositories.job_log_repository import JobLogRepository
from app.pipelines.cse_pipeline import CSEPipeline
from app.pipelines.cbsl_pipeline import CBSLPipeline
from app.pipelines.trends_pipeline import TrendsPipeline
from app.pipelines.integration_pipeline import IntegrationPipeline

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

            # 2. CBSL Macro Data Validation
            cbsl = CBSLPipeline()
            cbsl_rows = cbsl.run()

            # 3. Google Trends Data Validation
            trends = TrendsPipeline()
            trends_rows = trends.run()

            # 4. Integrated Merge and Feature Generation
            integration = IntegrationPipeline(self.db)
            integration_rows = integration.run()

            total_rows = cse_rows + cbsl_rows + trends_rows + integration_rows

            self.job_repo.update_log(
                log_id=job_log.id,
                status="Success",
                rows_processed=total_rows,
                error_message=None
            )

            return {
                "status": "Success",
                "job_id": job_log.id,
                "rows_processed": total_rows,
                "cse_rows": cse_rows,
                "cbsl_rows": cbsl_rows,
                "trends_rows": trends_rows,
                "integration_rows": integration_rows
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
