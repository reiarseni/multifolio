from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "multifolio",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_default_queue="default",
    worker_prefetch_multiplier=1,
)

celery_app.autodiscover_tasks(["app.worker.tasks"])
