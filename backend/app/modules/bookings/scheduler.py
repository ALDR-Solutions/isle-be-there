"""APScheduler configuration with SQLAlchemy job store for booking automation."""

from apscheduler.events import EVENT_JOB_ERROR
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from app.infrastructure.database.engine import get_engine
from app.infrastructure.database.session import get_db
from app.modules.bookings.service import update_expired_bookings


# SQLAlchemy job store - uses its own tables in the same DB
# APScheduler will auto-create the tables via `start()`
jobstores = {
    "default": SQLAlchemyJobStore(
        engine=get_engine(),
        tableschema="public",
    )
}

# Scheduler instance with job store configured
scheduler = BackgroundScheduler(
    jobstores=jobstores,
    job_defaults={
        "coalesce": True,  # Combine missed executions into one
        "max_instances": 1,  # Only one instance of each job at a time
        "misfire_grace_time": 60 * 15,  # 15 minutes grace time for missed runs
    },
)


def _run_update_expired_bookings() -> None:
    """Wrapper to run update_expired_bookings with a db session."""
    from datetime import datetime
    print(f"[{datetime.utcnow().isoformat()}] Running update_expired_bookings job...")
    for db in get_db():
        try:
            result = update_expired_bookings(db)
            print(f"[{datetime.utcnow().isoformat()}] Job completed: {result}")
        finally:
            db.close()


def init_scheduler() -> None:
    """Start the scheduler if not already running, and register jobs."""
    if not scheduler.running:
        scheduler.start()

    # Register frequent job to update expired bookings (every minute for testing)
    # Production should use: trigger="cron", minute=0
    if not scheduler.get_job("update_expired_bookings"):
        scheduler.add_job(
            _run_update_expired_bookings,
            trigger="cron",
            minute="*",  # Every minute (change to 0 for hourly in production)
            id="update_expired_bookings",
            name="Update expired booking statuses",
            replace_existing=True,
        )