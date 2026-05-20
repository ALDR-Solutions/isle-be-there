"""APScheduler configuration with SQLAlchemy job store for booking automation."""

from apscheduler.events import EVENT_JOB_ERROR
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler

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


def _job_error_listener(event):
    """Log job errors for monitoring."""
    from datetime import datetime

    if event.exception:
        print(
            f"[{datetime.utcnow().isoformat()}] JOB ERROR - "
            f"Job '{event.job_id}' failed with: {event.exception}"
        )
    else:
        print(
            f"[{datetime.utcnow().isoformat()}] JOB {event.job_id} executed successfully"
        )


# Register error listener
scheduler.add_listener(_job_error_listener, EVENT_JOB_ERROR)


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

    # Register job to update expired bookings every 5 minutes
    # replace_existing=True ensures trigger changes are applied on reload
    scheduler.add_job(
        _run_update_expired_bookings,
        trigger="cron",
        minute="*/5",  # Every 5 minutes
        id="update_expired_bookings",
        name="Update expired booking statuses",
        replace_existing=True,
    )