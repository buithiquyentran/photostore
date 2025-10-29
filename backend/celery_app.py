from celery import Celery

celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",       # Redis hoặc RabbitMQ
    backend="redis://localhost:6379/0",
    include=["tasks.cleanup_tasks"], 
)

celery_app.conf.timezone = "Asia/Ho_Chi_Minh"
celery_app.conf.beat_schedule = {
    "delete-soft-deleted-assets-every-midnight": {
        "task": "tasks.cleanup_tasks.permanent_delete_assets",
        "schedule": 24 * 60 * 60,  # mỗi 24h
        
    },
}
