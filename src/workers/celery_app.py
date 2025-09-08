"""
Celery application configuration and setup
"""
import os
from celery import Celery
from ..common.config import config
from ..common.logger import get_logger

logger = get_logger(__name__)

# Create Celery instance
celery_app = Celery(
    "news_scraper",
    broker=f"redis://{config.redis_host}:{config.redis_port}/{config.redis_db}",
    backend=f"redis://{config.redis_host}:{config.redis_port}/{config.redis_db}",
    include=[
        "src.workers.tasks.news_tasks",
        "src.workers.tasks.cleanup_tasks",
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    result_expires=3600,  # 1 hour
    task_routes={
        "src.workers.tasks.news_tasks.*": {"queue": "news_scraping"},
        "src.workers.tasks.cleanup_tasks.*": {"queue": "cleanup"},
    },
    task_default_queue="default",
    task_default_exchange="default",
    task_default_exchange_type="direct",
    task_default_routing_key="default",
)

# Optional: Add Redis password if configured
if config.redis_password:
    celery_app.conf.broker_url = f"redis://:{config.redis_password}@{config.redis_host}:{config.redis_port}/{config.redis_db}"
    celery_app.conf.result_backend = f"redis://:{config.redis_password}@{config.redis_host}:{config.redis_port}/{config.redis_db}"

logger.info("Celery application configured successfully")
