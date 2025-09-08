# News MCP Server

A Model Context Protocol (MCP) server that provides news scraping services via Server-Sent Events (SSE) transport.

## Features

- **Google News Scraping**: Search and extract news articles from Google News
- **MCP Protocol Support**: Full MCP server implementation with FastMCP
- **SSE Transport**: Real-time communication via Server-Sent Events
- **News Tools**: Multiple MCP tools for different news operations
- **Export Support**: Save results in JSON or CSV format
- **Comprehensive Logging**: Structured logging with error handling

## Architecture

```
src/
├── services/           # News scraping logic
│   ├── google_news_scraper.py
│   ├── news_parser.py
│   └── news_service.py
├── core/              # MCP server
│   └── mcp_server.py
├── common/            # Utilities
│   ├── config/        # Configuration
│   └── utils/         # Logger, exceptions
├── mcp_tools/         # MCP tool definitions
└── main.py           # Entry point
```

## Installation

1. Install dependencies using uv:
   ```bash
   uv sync
   ```

## Usage

### Start the MCP Server

```bash
uv run main.py
```

The server will start on `http://127.0.0.1:3006` with SSE endpoint at `/sse`

### Available MCP Tools

1. **search_news_tool**: Search for news articles
   - Parameters: `query` (string), `max_results` (int, default: 10)
   - Returns: List of articles with title, link, and snippet

2. **get_news_titles_tool**: Get only news titles
   - Parameters: `query` (string), `max_results` (int, default: 10)
   - Returns: List of titles with basic info

## MCP Client Integration

Connect to the server using MCP clients:

```python
# Example MCP client connection
mcp_client = MCPClient("http://127.0.0.1:3006/sse")
```

## Configuration

Environment variables (optional):
- `MCP_HOST`: Server host (default: 127.0.0.1)
- `NEWS_MCP_PORT`: Server port (default: 3006)
- `DEFAULT_MAX_RESULTS`: Default max results (default: 10)
- `DEFAULT_OUTPUT_FORMAT`: Default format (default: json)

## Output

Articles are saved in the `data/` directory:
- JSON: `query_YYYYMMDD_HHMMSS.json`
- CSV: `query_YYYYMMDD_HHMMSS.csv`

Each file contains:
- Title
- Link  
- Snippet
