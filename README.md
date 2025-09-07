# News Collector (Partial Implementation)

This is a simplified version of the News Collector that demonstrates the core functionality without including the full article scraping or scheduling features.

## Features Included

- Search for news articles on Google News based on a given query
- Extract basic article information (title, link, snippet)
- Save results in JSON or CSV format
- Command-line interface for easy usage

## Features Excluded

- Full article scraping (complete text, authors, publish date, etc.)
- Image downloading
- Scheduling/cron jobs
- Advanced error handling and retry mechanisms

## Installation

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

```
python src/main.py "search query" [--format json|csv]
```

Example:
```
python src/main.py "E20 Fuel"
python src/main.py "artificial intelligence" --format csv
```

## Output

The collected articles will be saved in the `data` directory in files named with the pattern:
- JSON: `query_YYYYMMDD_HHMMSS.json`
- CSV: `query_YYYYMMDD_HHMMSS.csv`

Each file will contain basic article information:
- Title
- Link
- Snippet