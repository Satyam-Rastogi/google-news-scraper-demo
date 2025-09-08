#!/usr/bin/env python3
"""
News MCP Server - Provides news scraping services via MCP protocol with SSE transport
"""

import os
import sys
import logging
import logging.config
from typing import Optional
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from mcp.server.fastmcp import FastMCP
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route
import uvicorn

# Import configurations and tools
from common.config.mcp_config import (
    LOGGING_CONFIG,
    MCP_HOST,
    NEWS_MCP_PORT
)
from mcp_tools.news_tools import (
    search_news,
    get_news_titles,
    save_news,
    NewsSearchRequest,
    NewsSearchResponse,
    NewsTitlesRequest,
    NewsTitlesResponse,
    SaveNewsRequest,
    SaveNewsResponse
)

# Configure logging
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('news_mcp_server')

# Create MCP server
mcp = FastMCP("NewsTools")

# -------------------------------------------------------------------------
# Register MCP Tools
# -------------------------------------------------------------------------

@mcp.tool()
async def search_news_tool(request: NewsSearchRequest) -> NewsSearchResponse:
    """
    Search for news articles based on a query
    
    This tool searches Google News for articles matching the provided query
    and returns a list of articles with their titles, links, and snippets.
    
    Args:
        request: Contains the search query and maximum number of results
        
    Returns:
        List of news articles with title, link, and snippet
    """
    return search_news(request)

@mcp.tool()
async def get_news_titles_tool(request: NewsTitlesRequest) -> NewsTitlesResponse:
    """
    Get only news titles for a query
    
    This tool searches Google News and returns only the titles, links, and snippets
    of articles matching the provided query. Useful when you only need headlines.
    
    Args:
        request: Contains the search query and maximum number of results
        
    Returns:
        List of news titles with title, link, and snippet
    """
    return get_news_titles(request)

@mcp.tool()
async def save_news_tool(request: SaveNewsRequest) -> SaveNewsResponse:
    """
    Save news articles to a file
    
    This tool saves a list of news articles to a file in either JSON or CSV format.
    The filename is generated based on the search query and current timestamp.
    
    Args:
        request: Contains articles to save, query for naming, and format type
        
    Returns:
        Success status and file path where articles were saved
    """
    return save_news(request)

# -------------------------------------------------------------------------
# SSE Server Setup
# -------------------------------------------------------------------------

def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette app with SSE transport for the MCP server."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request):
        try:
            async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,
            ) as (read_stream, write_stream):
                await mcp_server.run(
                    read_stream,
                    write_stream,
                    mcp_server.create_initialization_options(),
                )
        except Exception as e:
            logger.error(f"Error in SSE handler: {e}")
            raise

    # Create the messages app
    messages_app = sse.handle_post_message if hasattr(sse, 'handle_post_message') else None
    
    routes = [Route("/sse", endpoint=handle_sse)]
    if messages_app:
        routes.append(Mount("/messages/", app=messages_app))

    return Starlette(
        debug=debug,
        routes=routes,
    )

def main():
    """Main function to start the MCP server"""
    import argparse

    # Get MCP server instance from FastMCP
    mcp_server = mcp._mcp_server

    parser = argparse.ArgumentParser(description="News MCP Server")
    parser.add_argument("--port", type=int, default=NEWS_MCP_PORT, help="Port for server")
    parser.add_argument("--host", type=str, default=MCP_HOST, help="Host for server")
    
    args = parser.parse_args()
    
    logger.info(f"Starting News MCP Server on {args.host}:{args.port}")
    
    # Create Starlette app with SSE transport
    starlette_app = create_starlette_app(mcp_server, debug=True)
    
    # Run the server with uvicorn
    uvicorn.run(
        starlette_app,
        host=args.host,
        port=args.port,
    )

if __name__ == "__main__":
    main()
