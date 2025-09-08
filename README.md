# Google News Scraper API

A FastAPI-based Google News scraper service with both API and CLI interfaces.

## Project Structure

```
google-news-scraper-demo/
├── src/
│   ├── api/                    # FastAPI application layer
│   │   ├── main.py            # FastAPI app configuration
│   │   └── routes/            # API route handlers
│   │       ├── news.py        # News search endpoints
│   │       └── health.py      # Health check endpoints
│   ├── cli/                   # Command Line Interface
│   │   └── news_cli.py        # CLI for news scraping
│   ├── common/                # Shared utilities
│   │   ├── config.py          # Application configuration
│   │   ├── exceptions.py      # Custom exceptions
│   │   └── logger.py          # Logging configuration
│   ├── core/                  # Core business logic
│   │   ├── scraper.py         # Google News scraper
│   │   └── parser.py          # HTML parser for articles
│   ├── models/                # Data models
│   │   └── schemas.py         # Pydantic models
│   └── services/              # Business logic services
│       └── news_service.py    # News processing service
├── data/                      # Output directory for scraped data
├── main.py                    # Main entry point
├── app.py                     # Alternative entry point
├── pyproject.toml             # Project dependencies
└── README.md
```

## Architecture

This project follows a clean architecture pattern:

- **API Layer** (`src/api/`): FastAPI routes and API-specific code
- **Services Layer** (`src/services/`): Business logic and orchestration
- **Core Layer** (`src/core/`): Core functionality (scraping, parsing)
- **Models Layer** (`src/models/`): Data models and schemas
- **Common Layer** (`src/common/`): Shared utilities and configuration
- **CLI Layer** (`src/cli/`): Command-line interface

## Installation

1. Install dependencies:
```bash
uv sync
```

2. Create environment file (optional):
```bash
cp .env.example .env
```

## Usage

### API Server Mode

Start the FastAPI server:
```bash
python main.py --server
```

The API will be available at:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### CLI Mode

Run the scraper from command line:
```bash
# Basic usage
python main.py --cli "E20 Fuel"

# With options
python main.py --cli "artificial intelligence" --format csv --max-results 20
```

### API Endpoints

#### Search News
- **POST** `/news/search` - Search for news articles
- **GET** `/news/search?query=...` - Search for news articles (GET)

#### Health Checks
- **GET** `/health/` - Health status
- **GET** `/health/ready` - Readiness check
- **GET** `/health/live` - Liveness check

## Configuration

Configuration can be set via environment variables:

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `DEBUG`: Debug mode (default: false)
- `DEFAULT_MAX_RESULTS`: Default max results (default: 50)
- `MAX_RESULTS_LIMIT`: Maximum results limit (default: 100)
- `REQUEST_TIMEOUT`: Request timeout in seconds (default: 30)
- `REQUEST_DELAY`: Delay between requests in seconds (default: 1.0)
- `DEFAULT_OUTPUT_FORMAT`: Default output format (default: json)
- `OUTPUT_DIRECTORY`: Output directory (default: data)
- `LOG_LEVEL`: Log level (default: INFO)

## Development

The project uses:
- **FastAPI** for the API framework
- **Pydantic** for data validation
- **BeautifulSoup** for HTML parsing
- **Requests** for HTTP requests
- **Uvicorn** as the ASGI server

## Features

- ✅ FastAPI-based REST API
- ✅ Command-line interface
- ✅ Rate limiting and error handling
- ✅ Multiple output formats (JSON, CSV)
- ✅ Health check endpoints
- ✅ Comprehensive logging
- ✅ Environment-based configuration
- ✅ Clean architecture separation