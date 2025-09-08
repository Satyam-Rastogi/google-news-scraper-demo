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
│   ├── services/              # Business logic services
│   │   └── news_service.py    # News processing service
│   └── database/              # Database layer (future)
│       ├── models/            # Database models
│       ├── migrations/        # Database migrations
│       ├── repositories/      # Repository pattern
│       └── connections/       # Connection management
├── artifacts/                 # Output artifacts directory
│   ├── data/                 # Data outputs
│   │   ├── raw/             # Raw scraped data
│   │   ├── processed/       # Processed data
│   │   └── scraped/         # Direct scraped outputs
│   ├── reports/             # Generated reports
│   └── exports/             # Exported data in various formats
├── logs/                     # Application logs
│   ├── api/                 # API server logs
│   ├── scraper/             # Scraper operation logs
│   └── errors/              # Error logs
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
- **Database Layer** (`src/database/`): Database models, repositories, and connections (future)
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

#### Versioned Endpoints (Recommended)
- **POST** `/api/v1/news/search` - Search for news articles
- **GET** `/api/v1/news/search?query=...` - Search for news articles (GET)
- **GET** `/api/v1/health/` - Health status
- **GET** `/api/v1/health/ready` - Readiness check
- **GET** `/api/v1/health/live` - Liveness check
- **GET** `/api/v1/artifacts/scraped` - List scraped articles
- **GET** `/api/v1/artifacts/stats` - Get artifacts statistics
- **DELETE** `/api/v1/artifacts/cleanup` - Clean up old articles

#### Legacy Endpoints (Backward Compatibility)
- **GET** `/health/` - Health status (legacy)
- **GET** `/health/ready` - Readiness check (legacy)
- **GET** `/health/live` - Liveness check (legacy)

#### Utility Endpoints
- **GET** `/` - API information
- **GET** `/version` - Version information

## Configuration

Configuration can be set via environment variables:

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `DEBUG`: Debug mode (default: false)
- `API_PREFIX`: API prefix for versioning (default: /api/v1)
- `ENABLE_VERSIONING`: Enable API versioning (default: true)
- `SUPPORTED_VERSIONS`: Comma-separated supported versions (default: v1)
- `DEFAULT_MAX_RESULTS`: Default max results (default: 50)
- `MAX_RESULTS_LIMIT`: Maximum results limit (default: 100)
- `REQUEST_TIMEOUT`: Request timeout in seconds (default: 30)
- `REQUEST_DELAY`: Delay between requests in seconds (default: 1.0)
- `DEFAULT_OUTPUT_FORMAT`: Default output format (default: json)
- `OUTPUT_DIRECTORY`: Output directory (default: artifacts/data/scraped)
- `LOGS_DIRECTORY`: Logs directory (default: logs)
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