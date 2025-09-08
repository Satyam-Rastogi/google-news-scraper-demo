#!/usr/bin/env python3
"""
Google News Scraper - Main Entry Point
Choose between API server or CLI mode
"""

import sys
import argparse
from src.common.logger import setup_logging


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Google News Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run FastAPI server
  python main.py --server
  
  # Run CLI mode
  python main.py --cli "E20 Fuel"
  python main.py --cli "artificial intelligence" --format csv
        """
    )
    
    parser.add_argument("--server", action="store_true", 
                        help="Run FastAPI server")
    parser.add_argument("--cli", type=str, metavar="QUERY",
                        help="Run CLI mode with search query")
    parser.add_argument("--format", "-f", choices=['json', 'csv'], 
                        help="Output format for CLI mode (json or csv)")
    parser.add_argument("--max-results", "-m", type=int, 
                        help="Maximum number of results for CLI mode")
    
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
        
        uvicorn.run(
            "src.api.main:app",
            host=config.host,
            port=config.port,
            reload=config.debug,
            log_level=config.log_level.lower()
        )
        
    elif args.cli:
        # Run CLI mode
        import asyncio
        from src.cli.news_cli import collect_news
        
        print("🔍 Running in CLI mode...")
        asyncio.run(collect_news(args.cli, args.format, args.max_results))
        
    else:
        parser.print_help()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\Operation interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
