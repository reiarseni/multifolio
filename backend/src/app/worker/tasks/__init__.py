from app.worker.celery_app import celery_app


@celery_app.task(name="health_check")
def health_check() -> dict:
    return {"status": "ok"}
