from celery import Celery
from app.core.config import get_settings
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

celery_app = Celery(
    "wanderchina",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.data_generation_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,
    task_soft_time_limit=540,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    task_routes={
        "app.tasks.data_generation_tasks.*": {"queue": "data_generation"},
        "app.tasks.annotation_tasks.*": {"queue": "annotation"},
        "app.tasks.evaluation_tasks.*": {"queue": "evaluation"},
    },
)
