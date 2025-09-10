# News Collector Technical Specification

## 1. Command-Line Interface Design

### 1.1 Command Syntax
```
news_collector "<search_topic>" --format <output_format> --full-count <number>
```

### 1.2 Parameters
- `search_topic` (required): String query for news search
- `--format` (optional, default: csv): Output format (csv|json)
- `--full-count` (optional, default: 0): Number of articles to fully scrape

### 1.3 Implementation Details
- Use `argparse` for argument parsing
- Validate parameter combinations
- Provide helpful error messages for invalid inputs

## 2. Data Schema Specification

### 2.1 CSV/JSON Fields
| Field | Type | Description | Source |
|-------|------|-------------|--------|
| title | string | Article headline | Google News |
| gnews_link | string (URL) | Original Google News URL | Google News |
| decoded_url | string (URL) | Direct link to the actual article | URL Decoder |
| snippet | string | Brief article preview | Google News |
| publisher | string | News source | Google News |
| published_time | datetime | Original publication timestamp | Google News |
| full_text | string | Complete article content | Article Scraper |
| authors | array of strings | Article author(s) | Article Scraper |
| publish_date | date | Formatted publication date | Article Scraper |
| summary | string | Auto-generated article summary | Article Scraper |
| keywords | array of strings | Extracted key terms/tags | Article Scraper |
| top_image | string (URL/path) | Main article image | Article Scraper |

## 3. Module Architecture

### 3.1 Core Modules

#### cli.py
- Argument parsing
- Parameter validation
- Command routing

#### article_scraper.py
- Google News search
- Initial metadata extraction
- Basic article information gathering

#### google_news_decoder.py
- URL decoding from Google News format
- Redirect resolution
- Direct URL extraction

#### full_article_scraper.py
- Full content extraction
- Author extraction
- Publish date parsing
- Summary generation
- Keyword extraction
- Image URL identification

#### media_handler.py
- Image downloading
- Local storage management
- Path reference generation

#### markdown_generator.py
- Article to markdown conversion
- Formatting standardization
- File generation

#### article_processor.py
- Data aggregation
- Output formatting
- File generation (CSV/JSON)

### 3.2 Utility Modules

#### utils.py
- Timestamp generation
- File naming
- Path management
- Data formatting helpers

#### retry_utils.py
- Retry mechanisms
- Error handling
- Backoff strategies

#### validation.py
- Data validation
- Schema compliance checking

## 4. Data Flow

### 4.1 Phase 1: Initial Scraping
1. CLI receives command and parameters
2. article_scraper.py searches Google News
3. Raw data is collected and parsed
4. Initial CSV/JSON is generated with basic metadata

### 4.2 Phase 2: URL Decoding
1. google_news_decoder.py processes gnews_link
2. decoded_url is generated for each article
3. Updated data is saved

### 4.3 Phase 3: Selective Full Scraping
1. full_article_scraper.py processes specified number of articles
2. full_text, authors, publish_date, summary, keywords, top_image are extracted
3. Data is updated

### 4.4 Phase 4: Media Handling
1. media_handler.py downloads top_image for fully scraped articles
2. Images are stored in images/ directory
3. Image paths are updated in data

### 4.5 Phase 5: Markdown Generation
1. markdown_generator.py creates .md files for fully scraped articles
2. Files are stored in articles/ directory

### 4.6 Phase 6: Final Output
1. article_processor.py generates final CSV/JSON with all data
2. Files are organized in proper directory structure

## 5. File Organization

### 5.1 Directory Structure
```
project_folder/
├── src/
│   ├── cli.py
│   ├── main.py
│   ├── article_scraper.py
│   ├── google_news_decoder.py
│   ├── full_article_scraper.py
│   ├── media_handler.py
│   ├── markdown_generator.py
│   ├── article_processor.py
│   ├── utils.py
│   ├── retry_utils.py
│   ├── validation.py
│   └── ...
├── data/
│   ├── {topic}_{timestamp}.csv
│   └── {topic}_{timestamp}.json
├── articles/
│   ├── article_1.md
│   ├── article_2.md
│   └── ...
└── images/
    ├── article_1_image.jpg
    ├── article_2_image.png
    └── ...
```

## 6. Error Handling and Logging

### 6.1 Error Categories
1. Network errors (timeouts, DNS failures)
2. Parsing errors (HTML structure changes)
3. Data validation errors
4. File I/O errors
5. Media download errors

### 6.2 Logging Strategy
- INFO level: Major workflow steps
- WARNING level: Recoverable issues
- ERROR level: Unrecoverable issues
- DEBUG level: Detailed debugging information

### 6.3 Retry Mechanisms
- Exponential backoff for network requests
- Max retry attempts: 3
- Specific handling for rate limiting

## 7. Performance Considerations

### 7.1 Rate Limiting
- Delay between requests: 1-2 seconds
- User agent rotation
- Session management

### 7.2 Memory Management
- Stream processing for large datasets
- Temporary file cleanup
- Efficient data structures

### 7.3 Parallelization Opportunities
- Concurrent image downloads
- Parallel URL decoding
- Batch processing where appropriate

## 8. Testing Strategy

### 8.1 Unit Tests
- Individual function testing
- Mock external dependencies
- Edge case handling

### 8.2 Integration Tests
- End-to-end workflow testing
- File generation verification
- Data integrity checks

### 8.3 Test Data Management
- Sample articles for testing
- Mock HTTP responses
- Expected output templates

## 9. Dependencies

### 9.1 Python Packages
- requests: HTTP requests
- beautifulsoup4: HTML parsing
- newspaper3k: Article extraction
- Pillow: Image processing
- sumy: Text summarization
- argparse: CLI argument parsing
- feedparser: RSS feed parsing (if needed)

### 9.2 System Requirements
- Python 3.7+
- Internet connection
- Adequate disk space for media files

## 10. Security Considerations

### 10.1 Data Handling
- No sensitive data storage
- Temporary file cleanup
- Secure file permissions

### 10.2 External Requests
- HTTPS validation
- User agent spoofing
- Request timeout settings

## 11. Extensibility Points

### 11.1 Plugin Architecture
- Configurable scrapers
- Pluggable summarization engines
- Custom output formatters

### 11.2 Configuration Management
- External configuration files
- Environment variable support
- Command-line overrides