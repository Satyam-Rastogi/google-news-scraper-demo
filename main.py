#!/usr/bin/env python3
"""
Google News Scraper - Main Entry Point
FastAPI server with Celery async task processing
"""

import sys
import argparse
from src.common.logger import setup_logging


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Google News Scraper API with Celery",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run FastAPI server
  python main.py --server
  
  # Run Celery worker
  python main.py --worker
  
  # Run Celery beat scheduler
  python main.py --beat
  
  # Run Flower monitoring
  python main.py --flower
        """
    )
    
    parser.add_argument("--server", action="store_true", 
                        help="Run FastAPI server")
    parser.add_argument("--worker", action="store_true",
                        help="Run Celery worker")
    parser.add_argument("--beat", action="store_true",
                        help="Run Celery beat scheduler")
    parser.add_argument("--flower", action="store_true",
                        help="Run Flower monitoring")
    parser.add_argument("--queue", type=str, default="news_scraping",
                        help="Queue name for worker (default: news_scraping)")
    parser.add_argument("--concurrency", type=int, default=2,
                        help="Worker concurrency (default: 2)")
    parser.add_argument("--port", type=int, default=5555,
                        help="Flower port (default: 5555)")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    
    if args.server:
        # Run FastAPI server
        import uvicorn
        from src.api.main import app
        from src.common.config import config
        
        print("🚀 Starting Google News Scraper API server...")
        print(f"📡 Server will be available at: http://{config.host}:{config.port}")
        print(f"📚 API documentation: http://{config.host}:{config.port}/docs")
        print("🔄 Using Celery for async task processing")
        
        uvicorn.run(
            "src.api.main:app",
            host=config.host,
            port=config.port,
            reload=config.debug,
            log_level=config.log_level.lower()
        )
        
    elif args.worker:
        # Run Celery worker
        from src.workers.worker_manager import WorkerManager
        
        print(f"🔄 Starting Celery worker for queue: {args.queue}")
        manager = WorkerManager()
        manager.start_worker(queue=args.queue, concurrency=args.concurrency)
        
    elif args.beat:
        # Run Celery beat scheduler
        from src.workers.worker_manager import WorkerManager
        
        print("⏰ Starting Celery beat scheduler...")
        manager = WorkerManager()
        manager.start_beat_scheduler()
        
    elif args.flower:
        # Run Flower monitoring
        from src.workers.worker_manager import WorkerManager
        
        print(f"🌸 Starting Flower monitoring on port {args.port}...")
        manager = WorkerManager()
        manager.start_flower_monitor(port=args.port)
        
    else:
        parser.print_help()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
