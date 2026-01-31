import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

celery_app = Celery(
    "eiregate",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0")
)

# Only load tasks if they exist
try:
    celery_app.autodiscover_tasks(["app"])
except Exception:
    pass  # Tasks module not yet implemented
