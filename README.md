# News Collector

A comprehensive news article collection system that scrapes Google News for specified topics, extracts full article content, resolves Google News redirect URLs, downloads images, and saves results in JSON or CSV format.

## Features

- **Topic-based Search**: Collect news articles on any subject
- **Multiple Output Formats**: Save results in JSON or CSV
- **Full Article Scraping**: Extract complete article text for top results
- **Enhanced URL Decoding**: Improved Google News URL resolution with fallbacks
- **Flexible Image Downloading**: Multiple options for image handling
- **Scheduled Execution**: Set up automated collection
- **Configurable Parameters**: Customize behavior through configuration files
- **Robust Error Handling**: Retry mechanisms and circuit breaker patterns
- **Comprehensive Logging**: Detailed logs for debugging and monitoring
- **Markdown Generation**: Convert articles to Markdown format
- **Enhanced Data Structure**: Richer data with additional fields (serial_number, date/time, etc.)

## Installation

1. **Prerequisites**:
   - Python 3.7+
   - [uv](https://github.com/astral-sh/uv) - An extremely fast Python package installer and resolver (recommended)
   - Google Chrome browser (for Selenium-based URL resolution)

2. **Setup**:
   ```bash
   # Clone the repository
   git clone https://github.com/your-username/news_collector.git
   cd news_collector
   
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

# Fetch from Google News homepage when no topic is specified
python src/core/main.py
```

### Image Scraping Options

The scraper offers flexible image handling with three modes:

```bash
# URL-only mode: Extract and include only image URLs (no downloads)
python src/core/main.py "technology" --images url-only

# Download mode: Download images locally and include file paths
python src/core/main.py "technology" --images download

# Both mode: Include both image URLs and download images locally
python src/core/main.py "technology" --images both

# Image scraping is DISABLED by default - only processes when --images flag is explicitly used
```

**Important Note About Image URLs**: 
Google News search results pages only provide favicons (small website icons) for performance reasons. Actual article images are only available when scraping full articles. The image modes work as follows:

- **url-only**: Extracts favicon URLs for search results OR actual article images when scraping full articles
- **download**: Downloads favicon images for search results OR actual article images when scraping full articles  
- **both**: Provides both favicon URLs and downloads favicon images for search results OR actual article images when scraping full articles

To get actual article images, combine image scraping with full article scraping:

```bash
# Get actual article images by scraping full articles
python src/core/main.py "technology" --images download --full-articles --full-count 5
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

#### Article Limit Options
```bash
# Limit the number of articles collected (default: 20)
python src/core/main.py "topic" --limit 50

# Fetch from Google News homepage when no topic is specified
python src/core/main.py
```

#### Image Scraping Options
```bash
# Image scraping mode: url-only, download, or both (default: disabled)
python src/core/main.py "topic" --images url-only
python src/core/main.py "topic" --images download
python src/core/main.py "topic" --images both
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

# Get favicon URLs for search results (no full article scraping)
python src/core/main.py "technology" --images url-only --limit 10

# Download favicon images for search results (no full article scraping)
python src/core/main.py "technology" --images download --limit 10

# Get actual article images by combining with full article scraping
python src/core/main.py "technology" --images download --full-articles --full-count 5
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

# Image scraping settings (DISABLED by default - only when --images flag used)
SCRAPE_IMAGES=false          # Whether to process images
IMAGE_SCRAPE_MODE=url-only   # Image scraping mode: "url-only", "download", or "both"

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
    "serial_number": 1,
    "title": "Article Title",
    "link": "https://news.google.com/article-link",
    "snippet": "Article summary text...",
    "published_time": "2025-01-01T12:00:00Z",
    "date": "2025-01-01",
    "time": "12:00:00",
    "image_url": "https://example.com/favicon.jpg",  // Favicon for search results, actual image for full articles
    "image_path": "/path/to/local/image.jpg",        // When images are downloaded
    "full_content": {
      "text": "Full article text...",
      "authors": ["Author Name"],
      "publish_date": "2025-01-01",
      "summary": "Article summary",
      "keywords": ["keyword1", "keyword2"],
      "top_image": "https://example.com/actual-article-image.jpg",  // Actual article image from full content
      "local_images": ["/path/to/image1.jpg", "/path/to/image2.jpg"],
      "local_article_file": "/path/to/article.txt",
      "markdown_file": "/path/to/article.md",
      "downloaded_at": "2025-01-01T12:00:00Z",
      "gnews_link": "https://news.google.com/read/...",
      "decoded_url": "https://original-article-url.com"
    }
  }
]
```

### CSV Format
Flattened format with separate columns for basic and full article data:

```csv
serial_number,title,link,snippet,published_time,date,time,image_url,image_path,full_text,authors,publish_date,summary,keywords,top_image,local_article_file,markdown_file,gnews_link,decoded_url
1,"Article Title","https://link","Summary...","2025-01-01T12:00:00Z","2025-01-01","12:00:00","https://example.com/favicon.jpg","/path/to/local/image.jpg","Full text...","Author Name","2025-01-01","Summary","keyword1,keyword2","https://example.com/actual-article-image.jpg","/path/to/article.txt","/path/to/article.md","https://news.google.com/read/...","https://original-article-url.com"
```

**Important Notes About Image Data**:
1. For search results (without full article scraping): `image_url` contains favicons
2. For full articles (with `--full-articles`): `image_url` contains actual article images
3. The `top_image` field in full content always contains actual article images
4. Use `--images download --full-articles --full-count N` to get actual article images

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
python scripts/generate_scheduled_task.py "AI_News" "artificial intelligence" --project-path "C:\MyProjects\news_scraper"
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

## Limitations

### 1. Google News Homepage Fetching Limitation
**Issue**: Google News homepage loads content dynamically with JavaScript. Static HTTP requests cannot retrieve the article data needed for parsing.

**Impact**: When running the collector without a query (to fetch from the homepage), no articles will be parsed.

**Workaround**: Provide a general query like "latest news" or "top stories" instead of relying on homepage scraping.

**Technical Explanation**: This is a well-known limitation when scraping modern web applications that heavily rely on client-side rendering.

### 2. Full Article Scraping Success Rate
**Issue**: Many websites implement anti-scraping measures like CAPTCHAs, IP blocking, or rate limiting.

**Impact**: Full article scraping may fail for some articles with HTTP 403 or 429 errors.

**Mitigation**: The system uses multiple fallback approaches:
- Newspaper3k library as primary method
- Readability library as fallback
- Simplified HTML parsing as secondary fallback
- Retry mechanisms with exponential backoff
- Circuit breaker pattern to prevent cascading failures
- User agent rotation to avoid detection

### 3. Image Quality and Availability
**Issue**: Google News search results only provide favicons (small website icons) for performance reasons.

**Impact**: When collecting search results without full article scraping, image quality is limited.

**Solution**: To get actual article images, use `--images [mode] --full-articles --full-count N`

### 4. Rate Limiting and IP Blocking
**Issue**: Google and other websites may implement rate limiting or IP blocking for automated requests.

**Impact**: Requests may fail with HTTP 429 (Too Many Requests) errors.

**Mitigation**: The system implements:
- Request delays between calls
- Exponential backoff with jitter for retries
- Circuit breaker pattern to pause requests after repeated failures
- Rate limiting detection and longer delays for such errors

### 5. Content Restrictions
**Issue**: Some articles require human verification (CAPTCHA) or are behind paywalls.

**Impact**: These articles cannot be scraped automatically.

**Mitigation**: The system filters out content that appears to require human verification.

## Alternatives to Overcome Limitations

### 1. For Homepage Fetching Limitation
- **Browser Automation**: Implement Selenium or similar browser automation tools for full homepage support
- **RSS Feeds**: Use official Google News RSS feeds for general news
- **Alternative Sources**: Use other news APIs or sources that provide structured data

### 2. For Full Article Scraping Success Rate
- **Browser Automation**: Use Selenium to scrape articles (slower but more reliable)
- **Proxy Rotation**: Implement proxy rotation to avoid IP-based blocking
- **Commercial Services**: Use paid article extraction services (e.g., Diffbot, Mercury)
- **Headless Browsers**: Use headless browsers with proper browser fingerprinting

### 3. For Rate Limiting Issues
- **Proxy Rotation**: Implement proxy rotation to distribute requests across multiple IPs
- **Request Scheduling**: Implement longer delays between requests
- **API Keys**: Use official APIs where available with proper authentication
- **Distributed Scraping**: Run multiple instances from different locations

### 4. For Content Restrictions
- **Subscription Services**: Use subscription-based news services with APIs
- **Manual Collection**: Implement manual collection workflows for important articles
- **Hybrid Approach**: Combine automated scraping with manual curation

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

### Image Scraping Notes

**Why am I only getting favicons?**
- Google News search results pages intentionally only provide favicons for performance
- Actual article images are only available when scraping full articles
- To get actual article images, use `--images [mode] --full-articles --full-count N`

**How to get actual article images:**
```bash
# This gets actual article images
python src/core/main.py "technology" --images download --full-articles --full-count 5

# This only gets favicons
python src/core/main.py "technology" --images download
```

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

## Architecture

For detailed information about the project's architecture, including what each file and function does, see [ARCHITECTURE.md](ARCHITECTURE.md).

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