#!/usr/bin/env python3
"""
News MCP Server - Main entry point for the News MCP Server with SSE transport
"""

import sys
import os
import argparse
import logging
import logging.config
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from common.config.mcp_config import LOGGING_CONFIG, MCP_HOST, NEWS_MCP_PORT
from core.mcp_server import main as mcp_main

# Configure logging
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('news_mcp_main')

def main():
    """Main function to start the News MCP Server"""
    parser = argparse.ArgumentParser(
        description="News MCP Server - Provides news scraping services via MCP protocol",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py
  python main.py --port 3007
  python main.py --host 0.0.0.0 --port 3006
        """
    )
    
    parser.add_argument("--port", type=int, default=NEWS_MCP_PORT, 
                        help=f"Port for server (default: {NEWS_MCP_PORT})")
    parser.add_argument("--host", type=str, default=MCP_HOST, 
                        help=f"Host for server (default: {MCP_HOST})")
    
    args = parser.parse_args()
    
    logger.info("Starting News MCP Server...")
    logger.info(f"Server will be available at: http://{args.host}:{args.port}/sse")
    
    # Start the MCP server
    mcp_main()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("News MCP Server interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)