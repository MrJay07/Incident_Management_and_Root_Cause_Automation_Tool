from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import text

from app.config import settings
from app.database import SessionLocal

scheduler = BackgroundScheduler(timezone="UTC")


def monitor_healthcheck() -> None:
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
    finally:
        db.close()


def start_scheduler() -> None:
    if scheduler.running:
        return
    scheduler.add_job(monitor_healthcheck, CronTrigger.from_crontab(settings.monitoring_cron), id="db_health_monitor", replace_existing=True)
    scheduler.start()


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
