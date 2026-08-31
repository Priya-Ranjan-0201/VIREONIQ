"""Celery application factory for VIREONIQ background workers.

The broker and result-backend both fall back to ``REDIS_URL`` when the
dedicated ``CELERY_BROKER_URL`` / ``CELERY_RESULT_BACKEND`` env-vars are not
set, so local development works with a plain Redis without extra config.
"""

from celery import Celery

from core.config import settings

# ---------------------------------------------------------------------------
# Resolve broker / backend URLs with graceful fallbacks
# ---------------------------------------------------------------------------
_broker: str = settings.CELERY_BROKER_URL or settings.REDIS_URL or "redis://localhost:6379/0"
_backend: str = settings.CELERY_RESULT_BACKEND or settings.REDIS_URL or "redis://localhost:6379/0"

celery_app = Celery(
    "vireoniq",
    broker=_broker,
    backend=_backend,
    include=["workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    # Prevent tasks from being silently lost on worker restart
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)
