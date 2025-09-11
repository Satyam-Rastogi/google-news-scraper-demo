# Architecture Documentation

This document provides a detailed overview of the News Collector project architecture, explaining what each file and function does.

## Project Structure

```
news_collector/
├── config/                 # Configuration files
├── data/                   # Output directory for results
├── gnews/                  # Google News decoder library
├── scripts/                # Utility scripts
├── src/                    # Source code
│   ├── core/              # Core application logic
│   ├── scrapers/          # Web scraping modules
│   ├── utils/             # Utility functions
│   └── tests/             # Test files
├── templates/             # Scheduled task templates
├── tests/                 # Additional test files
└── venv/                  # Virtual environment
```

## Core Modules

### src/core/main.py
**Main entry point for the News Collector application**

Key Functions:
- `main()`: Entry point that parses command-line arguments and initiates collection
- `main_cli()`: Main CLI function for interactive use
- `collect_news_task()`: Task function to collect news for a specific query
- `collect_news_for_all_topics()`: Collects news for all configured topics
- `run_scheduler()`: Runs the news collection scheduler
- `display_articles_summary()`: Displays formatted article summaries
- `validate_queries()`: Validates search queries
- Helper functions for formatting and display

### src/core/scheduler.py
**Scheduler implementation for automated news collection**

Key Functions:
- `NewsScheduler.schedule_task()`: Schedules a task to run at specified intervals
- `NewsScheduler.schedule_daily_task()`: Schedules a task to run daily at a specific time

### src/core/news_types.py
**Type definitions for the application**

Key Components:
- `ArticleDict`: TypedDict for basic article data with all enhanced fields
- `FullArticleDict`: TypedDict for full article content data
- `ConfigDict`: TypedDict for configuration data

## Scraping Modules

### src/scrapers/scraper.py
**Google News search scraper**

Key Functions:
- `GoogleNewsScraper.search()`: Searches Google News for articles based on a query
- `GoogleNewsScraper._make_request()`: Makes HTTP requests with retry logic

### src/scrapers/parser.py
**HTML parser for Google News search results**

Key Functions:
- `ArticleParser.parse()`: Parses HTML content and extracts article information
  - Extracts titles, links, snippets, timestamps, publishers
  - Handles image extraction (favicons and actual article images)
  - Splits timestamps into separate date and time fields
  - Adds sequential numbering to articles

### src/scrapers/article_processor.py
**Main orchestrator for article collection and processing**

Key Functions:
- `collect_news()`: Main function that orchestrates the entire collection process
- `collect_full_articles()`: Collects full article content for top articles
- `collect_images()`: Collects images for all articles based on image mode
- `save_articles()`: Saves articles to file in specified format (JSON/CSV)
- `create_full_article_data()`: Creates standardized full article data structure

### src/scrapers/article_scraper.py
**Full article content scraper using multiple approaches**

Key Functions:
- `ArticleScraper.scrape_article()`: Primary method using newspaper3k library
- `ArticleScraper.scrape_article_with_readability()`: Fallback method using readability
- `ArticleScraper.scrape_article_simplified()`: Secondary fallback with simplified parsing
- `ArticleScraper.clean_text()`: Cleans extracted text by removing unwanted content
- Helper functions for request delays and user agent rotation

### src/scrapers/full_article_scraper.py
**High-level full article scraper with image processing**

Key Functions:
- `FullArticleScraper.scrape_full_article()`: Main function for scraping full articles
  - Decodes Google News URLs using multiple approaches
  - Scrapes article content with fallback mechanisms
  - Handles image downloading based on image mode
  - Saves article text and generates Markdown files

### src/scrapers/google_news_decoder.py
**Google News URL decoder with multiple fallback approaches**

Key Functions:
- `decode_google_news_url()`: Decodes Google News URLs using:
  - gnewsdecoder library (primary)
  - Custom URL resolver (fallback)
- Integrates with external googlenewsdecoder package

### src/scrapers/url_resolver.py
**Custom URL resolver for Google News redirects**

Key Functions:
- `resolve_google_news_url()`: Resolves Google News redirect URLs using requests
- Helper functions for parameter extraction and URL construction

## Utility Modules

### src/utils/utils.py
**Common utility functions used across the application**

Key Functions:
- `setup_logging()`: Configures logging to both file and console
- `resolve_google_news_url_with_selenium()`: Resolves URLs using Selenium (fallback)
- `download_image()`: Downloads images and saves them locally
- `save_article_text()`: Saves full article text to a file
- `_download_image_with_retry()`: Internal function with retry logic
- `_resolve_url_with_selenium()`: Internal Selenium resolution function

### src/utils/validation.py
**Input validation functions**

Key Functions:
- `validate_string()`: Validates string inputs
- `validate_integer_range()`: Validates integers within a range
- `validate_boolean()`: Validates boolean values
- `validate_path()`: Validates file paths
- `validate_url()`: Validates URLs
- `validate_config_values()`: Validates configuration values
- `sanitize_filename()`: Sanitizes filenames
- `validate_search_query()`: Validates search queries

### src/utils/retry_utils.py
**Retry mechanisms and circuit breaker patterns**

Key Components:
- `CircuitBreaker`: Circuit breaker implementation to prevent cascading failures
- `retry_with_backoff()`: Decorator for retry logic with exponential backoff
- Pre-configured retry policies:
  - `retry_default`: Default retry settings
  - `retry_for_network`: Network-specific retry settings
  - `retry_for_parsing`: Parsing-specific retry settings
  - `retry_for_file_operations`: File operation retry settings
  - `retry_for_validation`: Validation retry settings

### src/utils/markdown_generator.py
**Markdown file generation for articles**

Key Functions:
- `generate_markdown()`: Generates Markdown files for full articles
  - Includes metadata, images, and content
  - Creates proper file paths and formatting

## Configuration

### config/config.py
**Configuration management**

Key Functions:
- `Config.load_from_file()`: Loads configuration from settings.cfg
- Defines all configuration parameters as class attributes
- Handles parsing of different data types (strings, integers, booleans, arrays)

### config/settings.cfg
**Main configuration file**
Contains settings for:
- Output format and directory
- Scheduler settings
- Article collection limits
- Full article scraping settings
- Image scraping settings
- Retry mechanism settings
- Scheduled collection topics

## Scripts

### scripts/generate_scheduled_task.py
**Utility script for generating scheduled task execution scripts**

Key Functions:
- `read_template()`: Reads template files
- `generate_script()`: Generates script content by replacing placeholders
- `main()`: Main function that generates batch, PowerShell, and VBScript files

### templates/template_scheduled_task.*
**Template files for scheduled tasks**
- `.bat`: Windows batch script template
- `.ps1`: PowerShell script template
- `.vbs`: VBScript template for hidden execution

## Data Flow

1. **User Input**: Command-line arguments or configuration files
2. **Search**: GoogleNewsScraper searches Google News for specified topics
3. **Parse**: ArticleParser extracts article data from HTML
4. **Process**: ArticleProcessor orchestrates full article scraping and image downloading
5. **Full Scrape**: ArticleScraper extracts complete article content with fallbacks
6. **URL Decode**: GoogleNewsDecoder resolves redirect URLs
7. **Save**: Articles saved in JSON/CSV format with enhanced data structure
8. **Schedule**: Scheduler manages automated collection tasks

## Error Handling

The application implements multiple layers of error handling:
- **Retry Mechanisms**: Exponential backoff with jitter for network operations
- **Circuit Breakers**: Prevents cascading failures
- **Validation**: Input validation at multiple levels
- **Fallbacks**: Multiple approaches for critical operations (scraping, URL decoding)
- **Logging**: Comprehensive logging for debugging and monitoring

## Key Design Patterns

- **Strategy Pattern**: Multiple scraping approaches (newspaper3k, readability, simplified)
- **Decorator Pattern**: Retry mechanisms with backoff
- **Factory Pattern**: Different image handling modes
- **Circuit Breaker Pattern**: Failure prevention
- **Singleton Pattern**: Configuration management