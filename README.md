# Async News Scraper

An asynchronous news article collection system that scrapes Google News for specified topics, extracts full article content, and saves results in JSON or CSV format.

## Features

- **Asynchronous Scraping**: Collect news articles efficiently using async operations
- **Topic-based Search**: Collect news articles on any subject
- **Multiple Output Formats**: Save results in JSON or CSV
- **Full Article Scraping**: Extract complete article text for top results
- **Enhanced URL Decoding**: Improved Google News URL resolution
- **Image Downloading**: Download article images and save locally
- **Scheduled Execution**: Set up automated collection
- **Configurable Parameters**: Customize behavior through configuration files
- **Robust Error Handling**: Retry mechanisms and circuit breaker patterns
- **Comprehensive Logging**: Detailed logs for debugging and monitoring

## Installation

1. **Prerequisites**:
   - Python 3.7+
   - [uv](https://github.com/astral-sh/uv) - An extremely fast Python package installer and resolver

2. **Setup**:
   ```bash
   # Clone the repository
   git clone https://github.com/Satyam-Rastogi/async_news_scraper.git
   cd async_news_scraper
   
   # Create and activate virtual environment using uv
   uv venv
   # On Windows
   source .venv/Scripts/activate
   # On macOS/Linux
   source .venv/bin/activate
   
   # Install dependencies using uv
   uv pip install -r requirements.txt
   ```

## Usage

### Manual Collection

Collect news articles on-demand from the command line:

```bash
# Basic usage with default settings
python src/core/main.py "artificial intelligence"

# Specify output format
python src/core/main.py "machine learning" --format csv

# Control full article scraping
python src/core/main.py "data science" --full-count 5
python src/core/main.py "technology" --no-full-articles

# Collect multiple topics in one run
python src/core/main.py "climate change" "renewable energy" --format json --full-count 3

# Combine multiple options
python src/core/main.py "financial markets" --format csv --full-count 2

# Comma-separated topics in a single argument
python src/core/main.py "AI,ML,Data Science" --format csv
```

### Scheduled Collection

Set up automated news collection using Windows Task Scheduler:

```bash
# Generate scheduled task scripts
python scripts/generate_scheduled_task.py "AI_News_Collection" "artificial intelligence" --format json --full-count 3

# Register with Windows Task Scheduler (using the .vbs file for completely hidden execution)
schtasks /create /tn "AI News Collector" /tr "C:\path\to\AI_News_Collection.vbs" /sc daily /st 09:00

# Verify the task
schtasks /query /tn "AI News Collector"
```

For one-time scheduled execution:
```bash
# Schedule a one-time collection at a specific time
python src/core/main.py "machine learning" --schedule --daily --hour 0 --minute 20 --format csv --full-count 3

# Schedule periodic execution (every N minutes)
python src/core/main.py "technology" --schedule --interval 60 --format json --full-count 2
```

### Command Line Options

#### Topic Arguments
```bash
python src/core/main.py "REQUIRED_TOPIC_NAME" ["ADDITIONAL_TOPICS"...]
```

#### Format Options
```bash
# JSON format (default)
python src/core/main.py "topic" --format json

# CSV format
python src/core/main.py "topic" --format csv
```

#### Full Article Scraping Options
```bash
# Enable full article scraping (default)
python src/core/main.py "topic" --full-articles

# Disable full article scraping
python src/core/main.py "topic" --no-full-articles

# Specify number of articles to scrape fully (default: 3)
python src/core/main.py "topic" --full-count 5
```

#### Scheduling Options
```bash
# Run as a scheduled task instead of one-time collection
python src/core/main.py "topic" --schedule

# Schedule for daily execution at specific time
python src/core/main.py "topic" --schedule --daily --hour 9 --minute 0

# Schedule for periodic execution (every N minutes)
python src/core/main.py "topic" --schedule --interval 60
```

### Complete Examples

```bash
# Collect technology news in CSV format with 5 full articles
python src/core/main.py "technology" --format csv --full-count 5

# Collect AI news without full article scraping
python src/core/main.py "artificial intelligence" --no-full-articles

# Collect finance news in JSON format with default settings
python src/core/main.py "finance"

# Collect multiple topics with full article scraping
python src/core/main.py "renewable energy" "climate change" --format json --full-count 2

# Schedule a daily collection task
python src/core/main.py "machine learning" --schedule --daily --hour 9 --minute 0 --format csv --full-count 3

# Schedule a periodic collection task (every 30 minutes)
python src/core/main.py "data science" --schedule --interval 30 --format json --full-count 1

# Complex example with multiple topics, CSV format, and custom scraping settings
python src/core/main.py "blockchain,cryptocurrency,bitcoin" --format csv --full-count 4 --full-articles
```

## Configuration

The `config/settings.cfg` file controls application-level settings:

```ini
# Output settings
OUTPUT_FORMAT=json           # Default output format (json or csv)
OUTPUT_DIR=data              # Directory for saving results
LOG_LEVEL=INFO               # Logging verbosity (DEBUG, INFO, WARNING, ERROR, CRITICAL)

# Scheduler settings
SCHEDULER_INTERVAL_MINUTES=60 # Interval for periodic tasks (1-1440 minutes)
SCHEDULER_DAILY_HOUR=9        # Hour for daily run (0-23)
SCHEDULER_DAILY_MINUTE=0      # Minute for daily run (0-59)

# Full article scraping settings
SCRAPE_FULL_ARTICLES=true    # Whether to scrape full articles
FULL_ARTICLES_COUNT=3        # Number of top articles to scrape fully (1-50)
SCRAPE_IMAGES=true           # Whether to download images

# Retry mechanism settings
MAX_RETRIES=3                # Maximum retry attempts (0-10)
BASE_DELAY=1.0               # Initial retry delay (seconds)
MAX_DELAY=60.0               # Maximum retry delay (seconds)
FAILURE_THRESHOLD=5          # Failures before circuit breaker opens (1-20)
RECOVERY_TIMEOUT=60          # Recovery time after circuit breaker opens (10-3600 seconds)

# Topics for scheduled collection
TOPICS=[
    "artificial intelligence",
    "machine learning",
    "data science"
]
```

## Output Formats

### JSON Format
Contains complete article data including nested full content when available:

```json
[
  {
    "title": "Article Title",
    "link": "https://news.google.com/article-link",
    "snippet": "Article summary text...",
    "published_time": "2025-01-01T12:00:00Z",
    "full_content": {
      "text": "Full article text...",
      "authors": ["Author Name"],
      "publish_date": "2025-01-01",
      "summary": "Article summary",
      "keywords": ["keyword1", "keyword2"],
      "top_image": "path/to/image.jpg",
      "local_images": ["path/to/image1.jpg", "path/to/image2.jpg"],
      "local_article_file": "path/to/article.txt",
      "downloaded_at": "2025-01-01T12:00:00Z"
    }
  }
]
```

### CSV Format
Flattened format with separate columns for basic and full article data:

```csv
title,link,snippet,published_time,full_text,authors,publish_date,summary,keywords,top_image
"Article Title","https://link","Summary...","2025-01-01T12:00:00Z","Full text...","Author Name","2025-01-01","Summary","keyword1,keyword2","path/to/image.jpg"
```

## Scheduled Task Generation

The system uses templates to generate execution scripts for scheduled tasks:

### Template Files
- `templates/template_scheduled_task.bat`: Windows batch script template
- `templates/template_scheduled_task.ps1`: PowerShell script template
- `templates/template_scheduled_task.vbs`: VBScript template (runs completely hidden)

### Script Generation Utility
```bash
# Basic usage
python scripts/generate_scheduled_task.py "TaskName" "Search Topic"

# With custom options
python scripts/generate_scheduled_task.py "Finance_News" "financial markets" --format csv --full-count 2

# Without full article scraping
python scripts/generate_scheduled_task.py "Tech_News" "technology" --no-full-articles

# With custom project path
python scripts/generate_scheduled_task.py "AI_News" "artificial intelligence" --project-path "C:\\MyProjects\\news_scraper"
```

### Generated Files
The utility creates three files:
- `TaskName_task.bat` - Batch script that activates the virtual environment and runs the collection
- `TaskName_task.ps1` - PowerShell script for hidden execution
- `TaskName.vbs` - VBScript that runs the PowerShell script completely hidden

### Creating Scheduled Tasks with Windows Task Scheduler
```bash
# 1. Generate execution scripts
python scripts/generate_scheduled_task.py "AI_News_Collection" "artificial intelligence" --format json --full-count 3

# 2. Register with Windows Task Scheduler (using the .vbs file for completely hidden execution)
schtasks /create /tn "AI News Collector" /tr "C:\path\to\AI_News_Collection.vbs" /sc daily /st 09:00

# 3. Verify the task
schtasks /query /tn "AI News Collector"
```

## Troubleshooting

### Common Issues

1. **No articles found**: 
   - Check if the topic is too specific or misspelled
   - Verify internet connection
   - Try a more general topic

2. **Full article scraping fails**:
   - Many websites block automated scraping (403 Forbidden errors)
   - This is normal and expected for some sources
   - The system will still save basic article metadata

3. **Scheduled tasks not executing**:
   - Verify the .vbs file path in the task configuration
   - Check Windows Task Scheduler logs
   - Ensure the Python virtual environment is accessible

4. **Permission errors**:
   - Run Command Prompt as Administrator for schtasks commands
   - Ensure the application directory has proper write permissions

### Log Files

Check `data/logs/app.log` for detailed execution information:
- Successful article collections
- Errors and warnings
- Performance metrics
- Debug information when LOG_LEVEL is set to DEBUG

### Configuration Issues

1. **Invalid configuration values**:
   - Ensure numeric values are actually numbers
   - Verify boolean values are true/false, 1/0, yes/no, or on/off
   - Check that array values are properly formatted

2. **File path issues**:
   - Use forward slashes or escaped backslashes in paths
   - Ensure directories exist and are writable

## Development

### Setting up Development Environment

```bash
# Using the provided setup scripts
# On Windows
setup.bat

# On macOS/Linux
chmod +x setup.sh
./setup.sh
```

### Using Makefile (Unix-like systems)
```bash
# Set up development environment
make setup

# Install dependencies
make install

# Install in development mode
make dev

# Run tests
make test

# Run with test topic
make run
```

## Contributing

1. Fork the repository
2. Create a feature branch (e.g., `v2`, `feature/new-feature`, etc.)
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.