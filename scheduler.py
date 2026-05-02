import logging, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from config import SCHEDULER_HOUR, SCHEDULER_MINUTE

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("scheduler")

def full_ingest():
    log.info("Running full ingest pipeline")
    try:
        from ingest.sync_app_registry import sync_app_registry
        sync_app_registry()
    except Exception as e:
        log.error(f"App registry sync failed: {e}")
    
    try:
        from ingest.rf_lttd_mongo import run_rf_lttd_ingest
        run_rf_lttd_ingest()
    except Exception as e:
        log.error(f"RF ingest failed: {e}")
    
    try:
        from ingest.git_hygiene_mongo import run_git_hygiene_ingest
        run_git_hygiene_ingest()
    except Exception as e:
        log.error(f"Git hygiene failed: {e}")
    
    try:
        from scoring.dpi_engine_mongo import run_dpi_scoring
        run_dpi_scoring()
    except Exception as e:
        log.error(f"DPI scoring failed: {e}")

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(full_ingest, CronTrigger(hour=SCHEDULER_HOUR, minute=SCHEDULER_MINUTE), id="dpi_ingest")
    log.info(f"Scheduler started. Next run at {SCHEDULER_HOUR:02d}:{SCHEDULER_MINUTE:02d}")
    full_ingest()  # Run once immediately
    try:
        scheduler.start()
    except KeyboardInterrupt:
        log.info("Stopped")
