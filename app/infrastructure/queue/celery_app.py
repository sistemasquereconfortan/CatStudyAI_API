from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "catstudyai_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Configuración adicional de Celery
celery_app.conf.update(
    task_track_started=True,
    timezone="UTC",
    broker_connection_retry_on_startup=True,
)

# Auto-descubrimiento de tareas dentro de app.workers
celery_app.autodiscover_tasks(["app.workers"])
