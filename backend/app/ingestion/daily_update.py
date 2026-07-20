"""
daily_update.py
───────────────
Ingestion routine that fetches the latest CSE market data, checks for existing
records, inserts new records, and updates the database.
Can be executed manually via CLI.
"""
import sys
import os
import logging

# Ensure root directory is on the path if run directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.connection import SessionLocal
from app.pipelines.daily_pipeline import DailyPipelineOrchestrator

logger = logging.getLogger(__name__)

def run_daily_update() -> dict:
    """
    Main daily update function. Establishes a database session,
    triggers the CSE ingestion pipeline, and commits the updates.
    """
    logger.info("Starting daily market data update...")
    print("Starting daily update...")
    
    db = SessionLocal()
    try:
        orchestrator = DailyPipelineOrchestrator(db)
        result = orchestrator.run()
        
        status = result.get("status")
        rows = result.get("rows_processed", 0)
        
        if status == "Success":
            logger.info(f"Daily update completed successfully. Processed {rows} new records.")
            print(f"Update completed successfully! Added {rows} records.")
        else:
            err = result.get("error", "Unknown error")
            logger.error(f"Daily update failed: {err}")
            print(f"Update failed: {err}")
            
        return result
    except Exception as e:
        logger.error(f"Unexpected error during daily update: {e}")
        print(f"Unexpected error: {e}")
        return {"status": "Failed", "error": str(e)}
    finally:
        db.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    run_daily_update()
