import asyncio

from celery import Celery
from celery.schedules import crontab
from celery.signals import worker_process_init, worker_process_shutdown

from workers.config import config
from workers.db import close_db_engine, init_db_engine
from workers.logging import get_logger

logger = get_logger(__name__)

celery_app = Celery(
    "url_classification_worker",
    broker=config.redis_url,
    backend=config.redis_url,
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
    task_soft_time_limit=config.task_soft_time_limit,
    task_time_limit=config.task_time_limit,
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
        "schedule": crontab(minute="0", hour=f"*/{config.classification_interval_hours}"),
        "args": (config.batch_size,),
        "options": {"queue": "classification"},
    },
    # "reclassify-sample-urls": {
    #     "task": "workers.tasks.classification.reclassify_sample_batch",
    #     "schedule": crontab(minute="0", hour="3"),
    #     "args": (config.batch_size, config.reclassification_sample_percent),
    #     "options": {"queue": "classification"},
    # },
}


@worker_process_init.connect
def init_worker(**kwargs) -> None:
    pid = kwargs.get("sender").pid if kwargs.get("sender") else None
    logger.info("worker_process_initializing", pid=pid)

    init_db_engine()

    logger.info("worker_process_initialized", pid=pid)


@worker_process_shutdown.connect
def shutdown_worker(**kwargs) -> None:
    pid = kwargs.get("sender").pid if kwargs.get("sender") else None
    logger.info("worker_process_shutting_down", pid=pid)

    # Close database engine and release connections
    asyncio.run(close_db_engine())

    logger.info("worker_process_shutdown_complete", pid=pid)
