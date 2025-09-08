"""
Database configuration

This module contains database configuration settings.
Currently using file-based storage, but ready for database integration.
"""

from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    
    # Database type (sqlite, postgresql, mysql, etc.)
    db_type: str = "sqlite"
    
    # Database connection settings
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database: str = "news_scraper.db"
    
    # Connection pool settings
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    # SQLAlchemy settings
    echo: bool = False
    echo_pool: bool = False
    
    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Create database configuration from environment variables"""
        return cls(
            db_type=os.getenv("DB_TYPE", "sqlite"),
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", "0")) if os.getenv("DB_PORT") else None,
            username=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME", "news_scraper.db"),
            pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
            pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
            pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "3600")),
            echo=os.getenv("DB_ECHO", "false").lower() == "true",
            echo_pool=os.getenv("DB_ECHO_POOL", "false").lower() == "true",
        )
    
    @property
    def database_url(self) -> str:
        """Get database URL for SQLAlchemy"""
        if self.db_type == "sqlite":
            return f"sqlite:///{self.database}"
        elif self.db_type == "postgresql":
            return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.db_type == "mysql":
            return f"mysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")


# Global database configuration instance
db_config = DatabaseConfig.from_env()
