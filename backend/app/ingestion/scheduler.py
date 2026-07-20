"""
scheduler.py
────────────
APScheduler background scheduler configuration for FastAPI.
Schedules incremental CSE ingestion every weekday at 6:00 PM.
"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from app.ingestion.daily_update import run_daily_update

logger = logging.getLogger(__name__)

_scheduler = None

def start_scheduler():
    """
    Initialize and start the background scheduler.
    Schedules the daily update task for Mon-Fri at 18:00 (6:00 PM).
    """
    global _scheduler
    if _scheduler is not None:
        logger.warning("Scheduler is already running.")
        return

    _scheduler = BackgroundScheduler()
    
    # Schedule the CSE ingestion daily update job
    _scheduler.add_job(
        run_daily_update,
        "cron",
        day_of_week="mon-fri",
        hour=18,
        minute=0,
        id="daily_cse_update",
        replace_existing=True
    )
    
    _scheduler.start()
    logger.info("APScheduler started: daily_cse_update scheduled at 6:00 PM (Mon-Fri).")

def shutdown_scheduler():
    """
    Shut down the background scheduler gracefully.
    """
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown()
        _scheduler = None
        logger.info("APScheduler shut down successfully.")
