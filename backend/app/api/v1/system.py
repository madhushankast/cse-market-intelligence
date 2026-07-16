from fastapi import APIRouter, BackgroundTasks
from app.database.connection import SessionLocal
from app.repositories.stock_repository import StockPriceRepository
from app.repositories.job_log_repository import JobLogRepository
from app.pipelines.daily_pipeline import DailyPipelineOrchestrator

router = APIRouter()


def run_daily_pipeline_task():
    db = SessionLocal()
    try:
        orchestrator = DailyPipelineOrchestrator(db)
        orchestrator.run()
    finally:
        db.close()


@router.get("/system/status")
def get_system_status():
    db = SessionLocal()
    try:
        stock_repo = StockPriceRepository(db)
        job_repo = JobLogRepository(db)

        last_pipeline_status, last_pipeline_time = job_repo.get_last_pipeline_status()

        total_records = stock_repo.get_total_count()
        unique_stocks = stock_repo.get_unique_symbols_count()
        last_update = stock_repo.get_last_updated_date()

        pipeline_health = "healthy"
        if last_pipeline_status == "Failed":
            pipeline_health = "unhealthy"

        return {
            "last_update": last_update,
            "stocks": unique_stocks,
            "records": total_records,
            "pipeline": pipeline_health,
            "last_pipeline": last_pipeline_status,
            "last_pipeline_time": last_pipeline_time.strftime("%Y-%m-%d %H:%M:%S") if last_pipeline_time else "N/A"
        }
    finally:
        db.close()


@router.get("/system/pipelines/logs")
def get_pipeline_logs(limit: int = 15):
    db = SessionLocal()
    try:
        job_repo = JobLogRepository(db)
        logs = job_repo.get_latest_logs(limit=limit)
        return [{
            "id": l.id,
            "pipeline": l.pipeline,
            "started_at": l.started_at.strftime("%Y-%m-%d %H:%M:%S") if l.started_at else None,
            "finished_at": l.finished_at.strftime("%Y-%m-%d %H:%M:%S") if l.finished_at else None,
            "status": l.status,
            "rows_processed": l.rows_processed,
            "error_message": l.error_message
        } for l in logs]
    finally:
        db.close()


@router.post("/system/pipelines/run")
def trigger_pipeline(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_daily_pipeline_task)
    return {"message": "Daily pipeline execution started in the background."}
