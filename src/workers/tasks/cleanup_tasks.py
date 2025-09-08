"""
Celery tasks for cleanup operations
"""
from typing import Dict, Optional
from celery import Task
from src.workers.celery_app import celery_app
from src.common.utils.artifacts import artifacts_manager
from src.common.logger import get_logger

logger = get_logger(__name__)


class CallbackTask(Task):
    """Custom task class with callback support"""
    
    def on_success(self, retval, task_id, args, kwargs):
        logger.info(f"Cleanup task {task_id} succeeded: {retval}")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Cleanup task {task_id} failed: {exc}")


@celery_app.task(
    bind=True,
    base=CallbackTask,
    name="cleanup_old_headlines",
    queue="cleanup",
    max_retries=2,
    default_retry_delay=60,
)
def cleanup_old_headlines(
    self,
    days_old: int = 7
) -> Dict:
    """
    Clean up old headlines based on age
    
    Args:
        days_old: Number of days old to consider for cleanup
    
    Returns:
        Dict with cleanup results
    """
    try:
        logger.info(f"Starting cleanup of headlines older than {days_old} days")
        
        # Get cleanup stats before cleanup
        stats_before = artifacts_manager.get_stats()
        
        # Perform cleanup
        cleanup_result = artifacts_manager.cleanup_old_artifacts(
            days_old=days_old,
            artifact_type="headlines_raw"
        )
        
        # Get cleanup stats after cleanup
        stats_after = artifacts_manager.get_stats()
        
        logger.info(f"Cleanup completed: {cleanup_result.get('files_removed', 0)} files removed")
        
        return {
            "status": "success",
            "task_id": self.request.id,
            "days_old": days_old,
            "artifact_type": "headlines_raw",
            "files_removed": cleanup_result.get("files_removed", 0),
            "space_freed": cleanup_result.get("space_freed", 0),
            "stats_before": stats_before,
            "stats_after": stats_after,
            "message": f"Successfully cleaned up {cleanup_result.get('files_removed', 0)} old headlines"
        }
        
    except Exception as exc:
        logger.error(f"Cleanup task failed: {exc}")
        
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying cleanup task {self.request.id} (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60 * (self.request.retries + 1))
        
        return {
            "status": "error",
            "task_id": self.request.id,
            "days_old": days_old,
            "artifact_type": "headlines_raw",
            "error": str(exc),
            "message": f"Failed to cleanup old headlines"
        }




@celery_app.task(
    bind=True,
    base=CallbackTask,
    name="generate_headlines_report",
    queue="cleanup",
    max_retries=1,
    default_retry_delay=30,
)
def generate_headlines_report(self) -> Dict:
    """
    Generate a headlines report with statistics
    
    Returns:
        Dict with headlines report
    """
    try:
        logger.info("Generating headlines report")
        
        # Get current stats
        stats = artifacts_manager.get_stats()
        
        # List all headlines
        headlines = artifacts_manager.list_artifacts("headlines_raw")
        
        report = {
            "status": "success",
            "task_id": self.request.id,
            "generated_at": artifacts_manager._get_timestamp(),
            "current_stats": stats,
            "total_headlines_files": len(headlines),
            "headlines_stats": {
                "total_files": len(headlines),
                "total_size_mb": sum(f.stat().st_size for f in headlines if f.exists()) / (1024 * 1024),
                "latest_file": headlines[0] if headlines else None
            },
            "recommendations": []
        }
        
        # Add recommendations
        if len(headlines) > 100:
            report["recommendations"].append("Consider cleaning up old headlines (100+ files)")
        
        if report["headlines_stats"]["total_size_mb"] > 100:
            report["recommendations"].append("Consider cleaning up old headlines (100MB+ total)")
        
        logger.info("Headlines report generated successfully")
        return report
        
    except Exception as exc:
        logger.error(f"Headlines report generation failed: {exc}")
        
        return {
            "status": "error",
            "task_id": self.request.id,
            "error": str(exc),
            "message": "Failed to generate headlines report"
        }
