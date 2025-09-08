# Logs Directory

This directory contains all application logs.

## Directory Structure

```
logs/
├── api/                    # API server logs
├── scraper/                # Scraper operation logs
└── errors/                 # Error logs
```

## Log Files

- **api/**: FastAPI server logs, request logs
- **scraper/**: News scraping operation logs
- **errors/**: Error logs and exception traces

## Log Rotation

Logs are automatically rotated to prevent disk space issues.
