"""
Worker management utilities for Celery
"""
import subprocess
import sys
from typing import List, Optional
from src.common.logger import get_logger

logger = get_logger(__name__)


class WorkerManager:
    """Manages Celery workers and tasks"""
    
    def __init__(self):
        self.worker_processes = []
    
    def start_worker(
        self,
        queue: str = "default",
        concurrency: int = 4,
        hostname: Optional[str] = None,
        loglevel: str = "info",
        foreground: bool = False
    ) -> subprocess.Popen:
        """
        Start a Celery worker
        
        Args:
            queue: Queue name to process
            concurrency: Number of concurrent workers
            hostname: Worker hostname
            loglevel: Log level
        
        Returns:
            subprocess.Popen: Worker process
        """
        cmd = [
            "celery",
            "-A", "src.workers.celery_app:celery_app",
            "worker",
            "--loglevel", loglevel,
            "--concurrency", str(concurrency),
            "--queues", queue,
        ]
        
        if hostname:
            cmd.extend(["--hostname", hostname])
        
        logger.info(f"Starting Celery worker: {' '.join(cmd)}")
        
        try:
            if foreground:
                # Run in foreground - logs will be visible in terminal
                process = subprocess.Popen(
                    cmd,
                    text=True
                )
                # Don't add to worker_processes list when running in foreground
                logger.info(f"Worker started in foreground with PID: {process.pid}")
                return process
            else:
                # Run in background - capture output
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                self.worker_processes.append(process)
                logger.info(f"Worker started with PID: {process.pid}")
                return process
            
        except Exception as e:
            logger.error(f"Failed to start worker: {e}")
            raise
    
    def start_news_worker(self, concurrency: int = 2) -> subprocess.Popen:
        """Start a worker for news scraping tasks"""
        return self.start_worker(
            queue="news_scraping",
            concurrency=concurrency,
            hostname="news-worker@%h"
        )
    
    def start_cleanup_worker(self, concurrency: int = 1) -> subprocess.Popen:
        """Start a worker for cleanup tasks"""
        return self.start_worker(
            queue="cleanup",
            concurrency=concurrency,
            hostname="cleanup-worker@%h"
        )
    
    def start_beat_scheduler(self) -> subprocess.Popen:
        """Start Celery Beat scheduler for periodic tasks"""
        cmd = [
            "celery",
            "-A", "src.workers.celery_app:celery_app",
            "beat",
            "--loglevel", "info",
        ]
        
        logger.info(f"Starting Celery Beat: {' '.join(cmd)}")
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.worker_processes.append(process)
            logger.info(f"Beat scheduler started with PID: {process.pid}")
            return process
            
        except Exception as e:
            logger.error(f"Failed to start beat scheduler: {e}")
            raise
    
    def start_flower_monitor(self, port: int = 5555) -> subprocess.Popen:
        """Start Flower monitoring tool"""
        cmd = [
            "celery",
            "-A", "src.workers.celery_app:celery_app",
            "flower",
            "--port", str(port),
        ]
        
        logger.info(f"Starting Flower monitor: {' '.join(cmd)}")
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.worker_processes.append(process)
            logger.info(f"Flower monitor started with PID: {process.pid} on port {port}")
            return process
            
        except Exception as e:
            logger.error(f"Failed to start Flower monitor: {e}")
            raise
    
    def stop_all_workers(self):
        """Stop all running workers"""
        logger.info("Stopping all workers...")
        
        for process in self.worker_processes:
            try:
                process.terminate()
                process.wait(timeout=10)
                logger.info(f"Worker {process.pid} stopped")
            except subprocess.TimeoutExpired:
                process.kill()
                logger.warning(f"Worker {process.pid} force killed")
            except Exception as e:
                logger.error(f"Error stopping worker {process.pid}: {e}")
        
        self.worker_processes.clear()
        logger.info("All workers stopped")
    
    def get_worker_status(self) -> List[dict]:
        """Get status of all workers"""
        status = []
        
        for process in self.worker_processes:
            status.append({
                "pid": process.pid,
                "running": process.poll() is None,
                "returncode": process.returncode,
            })
        
        return status


def main():
    """Main function for worker management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Celery Worker Manager")
    parser.add_argument("command", choices=["start", "stop", "status"], help="Command to run")
    parser.add_argument("--queue", default="default", help="Queue name")
    parser.add_argument("--concurrency", type=int, default=4, help="Worker concurrency")
    parser.add_argument("--port", type=int, default=5555, help="Flower port")
    
    args = parser.parse_args()
    
    manager = WorkerManager()
    
    try:
        if args.command == "start":
            if args.queue == "news_scraping":
                manager.start_news_worker(args.concurrency)
            elif args.queue == "cleanup":
                manager.start_cleanup_worker(args.concurrency)
            elif args.queue == "beat":
                manager.start_beat_scheduler()
            elif args.queue == "flower":
                manager.start_flower_monitor(args.port)
            else:
                manager.start_worker(args.queue, args.concurrency)
            
            # Keep running
            try:
                while True:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Shutting down...")
                manager.stop_all_workers()
        
        elif args.command == "stop":
            manager.stop_all_workers()
        
        elif args.command == "status":
            status = manager.get_worker_status()
            for worker in status:
                print(f"Worker PID {worker['pid']}: {'Running' if worker['running'] else 'Stopped'}")
    
    except Exception as e:
        logger.error(f"Worker management error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
