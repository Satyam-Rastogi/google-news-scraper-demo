# News Collector Project Documentation

## Project Overview
The News Collector is a Python-based application designed to scrape news articles from Google News, decode URLs, resolve article content, and store the collected data in various formats. The project includes scheduled task generation capabilities and comprehensive error handling.

## Directory Structure
```
news_collector/
├── config/                 # Configuration files
├── data/                   # Data storage (CSV, JSON files)
│   ├── articles/           # Articles storage (currently empty)
│   ├── images/             # Images storage (currently empty)
│   └── logs/               # Logs storage (git-ignored)
├── gnews/                  # Google News specific functionality
├── src/                    # Main source code
└── venv/                   # Python virtual environment (git-ignored)
```

## Core Components

### 1. Main Application Files
- `main.py` - Entry point for the news collection process
- `scheduler_main.py` - Scheduled execution of news collection
- `scheduler.py` - Scheduling functionality

### 2. Scraping Components
- `article_scraper.py` - Core article scraping functionality
- `full_article_scraper.py` - Full article content scraping
- `scraper.py` - General scraping utilities
- `parser.py` - Parsing of scraped content

### 3. URL Handling
- `google_news_decoder.py` - Google News URL decoding
- `google_news_url_decoder.py` - Additional URL decoding functionality
- `decodeGoogleNewsUrl.ts` - TypeScript implementation of URL decoding
- `resolve_urls.py` - URL resolution functionality
- `url_resolver.py` - URL resolver utilities

### 4. Utilities
- `article_processor.py` - Article processing and formatting
- `utils.py` - General utility functions
- `retry_utils.py` - Retry mechanisms for failed operations
- `news_types.py` - News category definitions
- `validation.py` - Data validation functions

### 5. Scheduled Tasks
- `generate_scheduled_task.py` - Script to generate scheduled tasks
- `template_scheduled_task.bat` - Batch template for scheduled tasks
- `template_scheduled_task.ps1` - PowerShell template for scheduled tasks
- `template_scheduled_task.vbs` - VBScript template for scheduled tasks
- Various generated task files (e.g., `E20_Fuel_Task.vbs`)

### 6. Testing
- `test_full_scraping.py` - Tests for full scraping functionality
- `test_integration.py` - Integration tests
- `test_url_decoder.py` - URL decoder tests
- `test_retry_mechanisms.py` - Tests for retry functionality
- `test_scheduled_collection.py` - Tests for scheduled collection

## Key Features

1. **News Scraping**: Collects news articles from Google News based on specified topics
2. **URL Decoding**: Decodes Google News redirect URLs to get actual article URLs
3. **Content Extraction**: Extracts full article content from source websites
4. **Data Storage**: Saves collected data in CSV and JSON formats
5. **Scheduled Execution**: Supports automated execution via scheduled tasks
6. **Error Handling**: Implements retry mechanisms for failed operations
7. **Data Validation**: Validates collected data before storage

## Data Flow

1. Scheduler triggers the main collection process
2. Articles are searched and collected from Google News based on topics
3. Google News URLs are decoded to actual article URLs
4. Full article content is scraped from source websites
5. Data is processed, validated, and stored in appropriate formats
6. Results are saved in the data directory

## Configuration

The project uses configuration files in the `config/` directory to manage:
- Search topics
- Collection parameters
- Storage settings
- Retry configurations

## Data Storage

Collected data is stored in the `data/` directory in:
- CSV format for tabular data
- JSON format for structured data
- Separate directories for articles and images (currently unused)
- Log files for tracking execution (in the logs subdirectory)