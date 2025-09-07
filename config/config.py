# config.py
import os
from typing import List

class Config:
    OUTPUT_FORMAT: str = "json"  # Can be "json" or "csv"
    OUTPUT_DIR: str = "data"
    LOG_LEVEL: str = "INFO"
    
    @classmethod
    def load_from_file(cls, config_file: str = "config/settings.cfg") -> None:
        """Load configuration from a file"""
        # For this simplified version, we're not loading from a file
        # In a full implementation, this would read from config/settings.cfg
        pass