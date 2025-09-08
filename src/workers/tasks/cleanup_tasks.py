"""
Celery tasks for cleanup operations
"""
from typing import Dict, Optional
from celery import Task
from ..celery_app import celery_app
from ...common.utils.artifacts import artifacts_manager
from ...common.logger import get_logger

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
    name="cleanup_old_artifacts",
    queue="cleanup",
    max_retries=2,
    default_retry_delay=60,
)
def cleanup_old_artifacts(
    self,
    days_old: int = 7,
    artifact_type: Optional[str] = None
) -> Dict:
    """
    Clean up old artifacts based on age
    
    Args:
        days_old: Number of days old to consider for cleanup
        artifact_type: Specific artifact type to clean (optional)
    
    Returns:
        Dict with cleanup results
    """
    try:
        logger.info(f"Starting cleanup of artifacts older than {days_old} days")
        
        # Get cleanup stats before cleanup
        stats_before = artifacts_manager.get_stats()
        
        # Perform cleanup
        cleanup_result = artifacts_manager.cleanup_old_artifacts(
            days_old=days_old,
            artifact_type=artifact_type
        )
        
        # Get cleanup stats after cleanup
        stats_after = artifacts_manager.get_stats()
        
        logger.info(f"Cleanup completed: {cleanup_result.get('files_removed', 0)} files removed")
        
        return {
            "status": "success",
            "task_id": self.request.id,
            "days_old": days_old,
            "artifact_type": artifact_type,
            "files_removed": cleanup_result.get("files_removed", 0),
            "space_freed": cleanup_result.get("space_freed", 0),
            "stats_before": stats_before,
            "stats_after": stats_after,
            "message": f"Successfully cleaned up {cleanup_result.get('files_removed', 0)} old files"
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
            "artifact_type": artifact_type,
            "error": str(exc),
            "message": f"Failed to cleanup old artifacts"
        }


@celery_app.task(
    bind=True,
    base=CallbackTask,
    name="cleanup_by_size",
    queue="cleanup",
    max_retries=2,
    default_retry_delay=60,
)
def cleanup_by_size(
    self,
    max_size_mb: int = 1000,
    artifact_type: Optional[str] = None
) -> Dict:
    """
    Clean up artifacts to keep total size under limit
    
    Args:
        max_size_mb: Maximum total size in MB
        artifact_type: Specific artifact type to clean (optional)
    
    Returns:
        Dict with cleanup results
    """
    try:
        logger.info(f"Starting size-based cleanup with max size: {max_size_mb}MB")
        
        # Get cleanup stats before cleanup
        stats_before = artifacts_manager.get_stats()
        
        # Perform cleanup
        cleanup_result = artifacts_manager.cleanup_by_size(
            max_size_mb=max_size_mb,
            artifact_type=artifact_type
        )
        
        # Get cleanup stats after cleanup
        stats_after = artifacts_manager.get_stats()
        
        logger.info(f"Size-based cleanup completed: {cleanup_result.get('files_removed', 0)} files removed")
        
        return {
            "status": "success",
            "task_id": self.request.id,
            "max_size_mb": max_size_mb,
            "artifact_type": artifact_type,
            "files_removed": cleanup_result.get("files_removed", 0),
            "space_freed": cleanup_result.get("space_freed", 0),
            "stats_before": stats_before,
            "stats_after": stats_after,
            "message": f"Successfully cleaned up {cleanup_result.get('files_removed', 0)} files to reduce size"
        }
        
    except Exception as exc:
        logger.error(f"Size-based cleanup task failed: {exc}")
        
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying size cleanup task {self.request.id} (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60 * (self.request.retries + 1))
        
        return {
            "status": "error",
            "task_id": self.request.id,
            "max_size_mb": max_size_mb,
            "artifact_type": artifact_type,
            "error": str(exc),
            "message": f"Failed to cleanup artifacts by size"
        }


@celery_app.task(
    bind=True,
    base=CallbackTask,
    name="generate_cleanup_report",
    queue="cleanup",
    max_retries=1,
    default_retry_delay=30,
)
def generate_cleanup_report(self) -> Dict:
    """
    Generate a cleanup report with statistics
    
    Returns:
        Dict with cleanup report
    """
    try:
        logger.info("Generating cleanup report")
        
        # Get current stats
        stats = artifacts_manager.get_stats()
        
        # List all artifacts
        artifacts = artifacts_manager.list_artifacts()
        
        # Calculate potential cleanup
        old_artifacts = artifacts_manager.get_old_artifacts(days_old=7)
        large_artifacts = artifacts_manager.get_large_artifacts(max_size_mb=100)
        
        report = {
            "status": "success",
            "task_id": self.request.id,
            "generated_at": artifacts_manager._get_timestamp(),
            "current_stats": stats,
            "total_artifacts": len(artifacts),
            "old_artifacts_count": len(old_artifacts),
            "large_artifacts_count": len(large_artifacts),
            "potential_cleanup": {
                "old_files": len(old_artifacts),
                "large_files": len(large_artifacts),
                "total_size_mb": stats.get("total_size_mb", 0),
            },
            "recommendations": []
        }
        
        # Add recommendations
        if len(old_artifacts) > 10:
            report["recommendations"].append("Consider cleaning up old artifacts (7+ days)")
        
        if stats.get("total_size_mb", 0) > 500:
            report["recommendations"].append("Consider size-based cleanup (500MB+ total)")
        
        if len(large_artifacts) > 5:
            report["recommendations"].append("Consider cleaning up large individual files")
        
        logger.info("Cleanup report generated successfully")
        return report
        
    except Exception as exc:
        logger.error(f"Cleanup report generation failed: {exc}")
        
        return {
            "status": "error",
            "task_id": self.request.id,
            "error": str(exc),
            "message": "Failed to generate cleanup report"
        }
