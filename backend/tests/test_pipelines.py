import sys
import os

# Add backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.connection import SessionLocal, create_tables
from app.pipelines.daily_pipeline import DailyPipelineOrchestrator
from app.repositories.job_log_repository import JobLogRepository


def test_pipeline():
    print("Initializing tables...")
    create_tables()

    db = SessionLocal()
    try:
        orchestrator = DailyPipelineOrchestrator(db)
        print("Running daily pipeline for symbol DIAL...")
        result = orchestrator.run(symbols=["DIAL"])
        print("Pipeline result:", result)

        # Verify log entry creation
        job_repo = JobLogRepository(db)
        logs = job_repo.get_latest_logs(limit=3)
        print("\nLogged jobs:")
        for log in logs:
            print(
                f"- Job ID: #{log.id}, Pipeline: {log.pipeline}, Status: {log.status}, Rows: {log.rows_processed}, Error: {log.error_message}"
            )

        assert len(logs) > 0, "No logs were created!"
        print("\nVerification successful!")
    finally:
        db.close()


if __name__ == "__main__":
    test_pipeline()
