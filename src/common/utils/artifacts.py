"""
Artifacts management utilities
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Literal
from .config import config
from .logger import get_logger

logger = get_logger(__name__)

# Artifact types
ArtifactType = Literal["scraped", "processed", "raw", "reports", "exports"]
ExportFormat = Literal["json", "csv", "excel"]
ReportPeriod = Literal["daily", "weekly", "monthly"]


class ArtifactsManager:
    """Manages artifacts directory structure and file organization"""
    
    def __init__(self):
        self.base_dir = Path("artifacts")
        self.logs_dir = Path("logs")
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Ensure all required directories exist"""
        directories = [
            self.base_dir / "data" / "scraped",
            self.base_dir / "data" / "processed", 
            self.base_dir / "data" / "raw",
            self.base_dir / "reports" / "daily",
            self.base_dir / "reports" / "weekly",
            self.base_dir / "reports" / "monthly",
            self.base_dir / "exports" / "json",
            self.base_dir / "exports" / "csv",
            self.base_dir / "exports" / "excel",
            self.logs_dir / "api",
            self.logs_dir / "scraper",
            self.logs_dir / "errors"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {directory}")
    
    def get_data_path(self, artifact_type: ArtifactType) -> Path:
        """Get path for data artifacts"""
        if artifact_type in ["scraped", "processed", "raw"]:
            return self.base_dir / "data" / artifact_type
        else:
            raise ValueError(f"Invalid data artifact type: {artifact_type}")
    
    def get_export_path(self, format_type: ExportFormat) -> Path:
        """Get path for export artifacts"""
        return self.base_dir / "exports" / format_type
    
    def get_report_path(self, period: ReportPeriod) -> Path:
        """Get path for report artifacts"""
        return self.base_dir / "reports" / period
    
    def get_log_path(self, log_type: str) -> Path:
        """Get path for log files"""
        return self.logs_dir / log_type
    
    def generate_filename(self, 
                         query: str, 
                         format_type: str = "json",
                         artifact_type: ArtifactType = "scraped",
                         timestamp: Optional[datetime] = None) -> str:
        """
        Generate standardized filename for artifacts
        
        Args:
            query: Search query
            format_type: File format (json, csv, etc.)
            artifact_type: Type of artifact (scraped, processed, etc.)
            timestamp: Timestamp for filename (defaults to now)
            
        Returns:
            Generated filename
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Clean query for filename
        safe_query = query.replace(' ', '_').replace('/', '_').replace('\\', '_')
        safe_query = ''.join(c for c in safe_query if c.isalnum() or c in '_-')
        
        # Generate timestamp string
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        
        return f"{safe_query}_{timestamp_str}.{format_type}"
    
    def get_file_path(self, 
                     query: str,
                     format_type: str = "json",
                     artifact_type: ArtifactType = "scraped",
                     timestamp: Optional[datetime] = None) -> Path:
        """
        Get full file path for saving artifacts with timestamp-based organization
        
        Args:
            query: Search query
            format_type: File format
            artifact_type: Type of artifact
            timestamp: Timestamp for filename
            
        Returns:
            Full file path with timestamp folder organization
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Create timestamp-based folder structure
        date_folder = timestamp.strftime("%Y-%m-%d")
        time_folder = timestamp.strftime("%H-%M-%S")
        
        if artifact_type in ["scraped", "processed", "raw"]:
            base_path = self.get_data_path(artifact_type) / date_folder / time_folder
        elif artifact_type == "exports":
            base_path = self.get_export_path(format_type) / date_folder / time_folder
        else:
            base_path = self.base_dir / artifact_type / date_folder / time_folder
        
        filename = self.generate_filename(query, format_type, artifact_type, timestamp)
        return base_path / filename
    
    def save_artifact(self, 
                     data: any,
                     query: str,
                     format_type: str = "json",
                     artifact_type: ArtifactType = "scraped",
                     timestamp: Optional[datetime] = None) -> Path:
        """
        Save data to appropriate artifact location
        
        Args:
            data: Data to save
            query: Search query
            format_type: File format
            artifact_type: Type of artifact
            timestamp: Timestamp for filename
            
        Returns:
            Path to saved file
        """
        file_path = self.get_file_path(query, format_type, artifact_type, timestamp)
        
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save based on format
        if format_type == "json":
            import json
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        elif format_type == "csv":
            import csv
            if isinstance(data, list) and data:
                fieldnames = data[0].keys() if isinstance(data[0], dict) else None
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)
        else:
            # For other formats, save as text
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(str(data))
        
        logger.info(f"Saved artifact: {file_path}")
        return file_path
    
    def list_artifacts(self, 
                      artifact_type: ArtifactType = "scraped",
                      format_type: Optional[str] = None) -> list[Path]:
        """
        List artifacts in a specific directory (recursively for timestamp folders)
        
        Args:
            artifact_type: Type of artifacts to list
            format_type: Optional format filter
            
        Returns:
            List of artifact file paths
        """
        if artifact_type in ["scraped", "processed", "raw"]:
            base_path = self.get_data_path(artifact_type)
        elif artifact_type == "exports":
            if format_type:
                base_path = self.get_export_path(format_type)
            else:
                base_path = self.base_dir / "exports"
        else:
            base_path = self.base_dir / artifact_type
        
        if not base_path.exists():
            return []
        
        # Recursively find all files in timestamp folders
        if format_type:
            pattern = f"**/*.{format_type}"
        else:
            pattern = "**/*"
        
        files = list(base_path.glob(pattern))
        # Filter out directories
        files = [f for f in files if f.is_file()]
        
        return sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)
    
    def cleanup_old_artifacts(self, 
                             artifact_type: ArtifactType = "scraped",
                             days_to_keep: int = 30) -> int:
        """
        Clean up old artifacts
        
        Args:
            artifact_type: Type of artifacts to clean
            days_to_keep: Number of days to keep artifacts
            
        Returns:
            Number of files removed
        """
        files = self.list_artifacts(artifact_type)
        cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
        
        removed_count = 0
        for file_path in files:
            if file_path.stat().st_mtime < cutoff_time:
                try:
                    file_path.unlink()
                    removed_count += 1
                    logger.info(f"Removed old artifact: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to remove {file_path}: {e}")
        
        return removed_count


# Global artifacts manager instance
artifacts_manager = ArtifactsManager()
