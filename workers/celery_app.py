from celery import Celery
from celery.schedules import crontab
from celery.signals import worker_process_init, worker_process_shutdown

from workers.config import settings
from workers.logging import get_logger

logger = get_logger(__name__)

celery_app = Celery(
    "url_classification_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["workers.tasks.classification"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # task execution
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    # time limits
    task_soft_time_limit=settings.TASK_SOFT_TIME_LIMIT,
    task_time_limit=settings.TASK_TIME_LIMIT,
    # task routing
    task_routes={
        "workers.tasks.classification.*": {"queue": "classification"},
    },
    # Result backend settings
    result_expires=3600,
    result_extended=True,
    # Worker settings
    worker_max_tasks_per_child=100,
    worker_disable_rate_limits=False,
    # Logging
    worker_redirect_stdouts=True,
    worker_redirect_stdouts_level="INFO",
)

# configure periodic tasks (celery beat schedule)
celery_app.conf.beat_schedule = {
    "classify-pending-urls": {
        "task": "workers.tasks.classification.classify_pending_batch",
        "schedule": crontab(minute=f"*/{settings.CLASSIFICATION_INTERVAL_MINUTES}"),
        "args": (settings.BATCH_SIZE,),
        "options": {"queue": "classification"},
    },
    "reclassify-sample-urls": {
        "task": "workers.tasks.classification.reclassify_sample_batch",
        "schedule": crontab(hour="3", minute="0"),
        "args": (settings.BATCH_SIZE, settings.RECLASSIFICATION_SAMPLE_PERCENT),
        "options": {"queue": "classification"},
    },
}


@worker_process_init.connect
def init_worker(**kwargs) -> None:
    logger.info(
        "worker_process_initialized",
        pid=kwargs.get("sender").pid if kwargs.get("sender") else None,
    )


@worker_process_shutdown.connect
def shutdown_worker(**kwargs) -> None:
    import asyncio

    from workers.db import close_db_connections

    logger.info(
        "worker_process_shutting_down",
        pid=kwargs.get("sender").pid if kwargs.get("sender") else None,
    )

    # close db connections
    try:
        asyncio.run(close_db_connections())
        logger.info("database_connections_closed")
    except Exception as e:
        logger.error("error_closing_database_connections", error=str(e))
