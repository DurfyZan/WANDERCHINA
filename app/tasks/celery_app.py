from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "wanderchina",
    broker=settings.celery_broker_url,
    backend=settings.redis_url,
)
celery_app.conf.task_routes = {
    "app.tasks.generation.*": {"queue": "generation"},
    "app.tasks.annotation.*": {"queue": "annotation"},
}
celery_app.autodiscover_tasks(["app.tasks"])
