from celery import Celery
import os

# Read Redis URL from environment so Docker containers can connect to the redis service.
# Default to localhost for local development outside Docker.
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "tasks",
    broker=REDIS_URL,       # Redis hoặc RabbitMQ
    backend=REDIS_URL,
    include=["tasks.cleanup_tasks"],
)

celery_app.conf.timezone = "Asia/Ho_Chi_Minh"
celery_app.conf.beat_schedule = {
    "delete-soft-deleted-assets-every-midnight": {
        "task": "tasks.cleanup_tasks.permanent_delete_assets",
        "schedule": 24 * 60 * 60,  # mỗi 24h
        # "schedule":  60 * 2,  # mỗi 2p for test
        
        
    },
}
