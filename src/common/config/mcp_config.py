#!/usr/bin/env python3
"""
Configuration settings for News Scraping MCP tools
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent.parent.parent

# News Scraping settings
DEFAULT_MAX_RESULTS = int(os.getenv("DEFAULT_MAX_RESULTS", "10"))
DEFAULT_OUTPUT_FORMAT = os.getenv("DEFAULT_OUTPUT_FORMAT", "json")
OUTPUT_DIR = BASE_DIR / "data"

# MCP Server settings
MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1")
NEWS_MCP_PORT = int(os.getenv("NEWS_MCP_PORT", "3006"))
NEWS_MCP_URL = f"http://{MCP_HOST}:{NEWS_MCP_PORT}/sse"


