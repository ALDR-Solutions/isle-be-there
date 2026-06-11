"""APScheduler configuration for booking automation."""

from __future__ import annotations

import logging

from apscheduler.events import EVENT_JOB_ERROR
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler

from app.infrastructure.database.engine import get_engine
from app.infrastructure.database.session import get_db
from app.modules.bookings.service import update_expired_bookings

logger = logging.getLogger(__name__)


def build_jobstores() -> dict[str, SQLAlchemyJobStore]:
    return {
        "default": SQLAlchemyJobStore(
            engine=get_engine(),
            tableschema="public",
        )
    }


scheduler = BackgroundScheduler(
    job_defaults={
        "coalesce": True,
        "max_instances": 1,
        "misfire_grace_time": 60 * 15,
    },
)


def job_error_listener(event) -> None:
    """Log job errors for monitoring."""
    if event.exception:
        logger.error(
            "Scheduled job '%s' failed",
            event.job_id,
            exc_info=(
                type(event.exception),
                event.exception,
                getattr(event, "traceback", None),
            ),
        )
    else:
        logger.info("Scheduled job '%s' executed successfully", event.job_id)


scheduler.add_listener(job_error_listener, EVENT_JOB_ERROR)


def run_update_expired_bookings() -> None:
    """Run update_expired_bookings with a managed database session."""
    logger.info("Running update_expired_bookings job")
    for db in get_db():
        try:
            result = update_expired_bookings(db)
            logger.info("update_expired_bookings job completed: %s", result)
            return
        except Exception:
            logger.exception("update_expired_bookings job failed")
            raise
        finally:
            db.close()


def init_scheduler() -> None:
    """Start the scheduler if not already running, and register jobs."""
    if not scheduler.running:
        scheduler.configure(jobstores=build_jobstores())
        scheduler.start()

    scheduler.add_job(
        run_update_expired_bookings,
        trigger="cron",
        minute="*/5",
        id="update_expired_bookings",
        name="Update expired booking statuses",
        replace_existing=True,
    )
