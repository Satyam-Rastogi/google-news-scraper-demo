# scheduler.py
import schedule
import time
import logging
from datetime import datetime
from typing import Callable

class NewsScheduler:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
    
    def schedule_task(self, task_function: Callable, interval_minutes: int = 60) -> None:
        """
        Schedule a task to run at specified intervals
        
        Args:
            task_function: Function to execute
            interval_minutes: Interval in minutes (default: 60)
        """
        # Schedule the task
        schedule.every(interval_minutes).minutes.do(task_function)
        
        self.logger.info(f"Task scheduled to run every {interval_minutes} minutes")
        self.logger.info("Starting scheduler... Press Ctrl+C to stop")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Scheduler stopped by user")
        except Exception as e:
            self.logger.error(f"Error in scheduler: {e}")
    
    def schedule_daily_task(self, task_function: Callable, hour: int = 9, minute: int = 0) -> None:
        """
        Schedule a task to run daily at a specific time
        
        Args:
            task_function: Function to execute
            hour: Hour of the day (0-23)
            minute: Minute of the hour (0-59)
        """
        schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(task_function)
        
        self.logger.info(f"Task scheduled to run daily at {hour:02d}:{minute:02d}")
        self.logger.info("Starting scheduler... Press Ctrl+C to stop")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Scheduler stopped by user")
        except Exception as e:
            self.logger.error(f"Error in scheduler: {e}")

