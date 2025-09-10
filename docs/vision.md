# News Scraper Project Vision

## User Interface & Command Structure

The user provides a query with the following syntax:
```
"<search_topic>" --format <output_format> --full-count <number>
```

**Example:**
```
"technology" --format csv --full-count 5
```

This command means:
- **Search Query**: "technology"
- **Output Format**: CSV file
- **Full Scraping**: 5 most recent articles will have complete content extracted

## Processing Workflow

### Phase 1: Google News Scraping
1. Search Google News for the specified topic
2. Extract basic article metadata
3. Generate initial data file (CSV/JSON format)
4. Example output: `..\\news_collector_refactored\\data\\E20_Fuel_20250909_144008.csv`

### Phase 2: URL Processing & Full Content Extraction
1. **URL Decoding**: Convert Google News redirect URLs to direct article URLs
2. **Content Scraping**: Extract full article content for specified number of articles
3. **Media Extraction**: Download and save article images
4. **Markdown Generation**: Convert full articles to .md format for enhanced readability

## Data Schema

### CSV Output Columns:
```
title, gnews_link, decoded_url, snippet, publisher, published_time, full_text, authors, publish_date, summary, keywords, top_image
```

### Field Descriptions:
- **title**: Article headline
- **gnews_link**: Original Google News URL
- **decoded_url**: Direct link to the actual article
- **snippet**: Brief article preview
- **publisher**: News source (e.g., Reuters, Times of India)
- **published_time**: Original publication timestamp
- **full_text**: Complete article content (for selected articles)
- **authors**: Article author(s)
- **publish_date**: Formatted publication date
- **summary**: Auto-generated article summary
- **keywords**: Extracted key terms/tags
- **top_image**: Main article image URL/local path

## Output Formats

### Primary Outputs:
1. **Structured Data**: CSV or JSON file with all metadata
2. **Full Articles**: Individual .md files for completely scraped articles
3. **Media Assets**: Downloaded images in organized folder structure

### File Organization:
```
project_folder/
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

## Key Features

- **Selective Deep Scraping**: Only specified number of articles get full content extraction
- **Multi-format Support**: Both CSV and JSON output options
- **Media Preservation**: Images downloaded and referenced locally
- **Clean Markdown**: Full articles converted to readable .md format
- **Metadata Rich**: Comprehensive article information captured
- **Timestamped Output**: All files include generation timestamps for organization
