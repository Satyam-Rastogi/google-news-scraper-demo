# config.py
import os
import configparser
from typing import List
from src.utils.validation import validate_config_values, validate_string, validate_integer_range, validate_boolean

class Config:
    SEARCH_URL: str = "https://news.google.com/search"
    OUTPUT_FORMAT: str = "json"  # Can be "json" or "csv"
    OUTPUT_DIR: str = "data"
    LOG_LEVEL: str = "INFO"
    
    # Scheduler settings
    SCHEDULER_INTERVAL_MINUTES: int = 60
    SCHEDULER_DAILY_HOUR: int = 9
    SCHEDULER_DAILY_MINUTE: int = 0
    
    # Full article scraping settings
    SCRAPE_FULL_ARTICLES: bool = False  # Whether to scrape full articles
    FULL_ARTICLES_COUNT: int = 3  # Number of top articles to scrape fully
    SCRAPE_IMAGES: bool = True  # Whether to download images
    
    # Retry mechanism settings
    MAX_RETRIES: int = 3  # Maximum number of retry attempts
    BASE_DELAY: float = 1.0  # Initial delay between retries in seconds
    MAX_DELAY: float = 60.0  # Maximum delay between retries in seconds
    FAILURE_THRESHOLD: int = 5  # Number of failures before circuit breaker opens
    RECOVERY_TIMEOUT: int = 60  # Seconds to wait before trying again after circuit breaker opens
    
    # Topics for scheduled collection
    TOPICS: List[str] = [
        "artificial intelligence",
        "machine learning",
        "data science"
    ]
    
    @classmethod
    def load_from_file(cls, config_file: str = "config/settings.cfg") -> None:
        """Load configuration from a file"""
        if os.path.exists(config_file):
            config_values = {}
            lines = []
            with open(config_file, 'r') as f:
                lines = [line.strip() for line in f.readlines() if line.strip() and not line.strip().startswith('#')]
            
            i = 0
            while i < len(lines):
                line = lines[i]
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Handle multi-line arrays
                    if value == '[':
                        # Read array values until we find the closing bracket
                        array_values = []
                        i += 1
                        while i < len(lines) and lines[i] != ']':
                            array_line = lines[i].strip().rstrip(',')
                            if array_line:
                                # Remove quotes and whitespace
                                cleaned_value = array_line.strip('"\'')
                                if cleaned_value:
                                    array_values.append(cleaned_value)
                            i += 1
                        config_values[key] = array_values
                    # Handle boolean values
                    elif key == "SCRAPE_FULL_ARTICLES":
                        config_values[key] = value.lower() in ('true', '1', 'yes', 'on')
                    elif key == "SCRAPE_IMAGES":
                        config_values[key] = value.lower() in ('true', '1', 'yes', 'on')
                    # Handle integer values
                    elif key in ("FULL_ARTICLES_COUNT", "SCHEDULER_INTERVAL_MINUTES", 
                                "SCHEDULER_DAILY_HOUR", "SCHEDULER_DAILY_MINUTE"):
                        config_values[key] = int(value)
                    # Handle string values
                    else:
                        config_values[key] = value.strip('"\'')
                i += 1
            
            # Validate configuration values
            try:
                validated_config = validate_config_values(config_values)
                
                # Update class attributes with validated values
                for key, value in validated_config.items():
                    setattr(cls, key, value)
                    
            except ValueError as e:
                raise ValueError(f"Invalid configuration in {config_file}: {str(e)}")

