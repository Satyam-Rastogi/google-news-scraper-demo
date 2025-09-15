# Docker Usage Guide

This guide explains how to use the Docker configurations provided in this project.

## Overview

The `docker-compose.yml` file provides multiple service configurations for different use cases:

1. `news-collector` - Basic news collection
2. `news-collector-scheduled` - Scheduled daily news collection
3. `weather-collector` - Weather data collection
4. `combined-collector` - Both news and weather collection
5. `news-collector-dev` - Development environment

## Prerequisites

- Docker installed on your system
- Docker Compose installed on your system

## Quick Start

To run a basic news collection:

```bash
docker-compose up news-collector
```

## Service Configurations

### 1. Basic News Collection (`news-collector`)

Collects general news by default. You can specify custom queries:

```bash
# Run with default configuration (general news)
docker-compose up news-collector

# Run with custom query
docker-compose run news-collector "artificial intelligence" --format json --full-count 5

# Run with multiple queries
docker-compose run news-collector "AI,ML,Data Science" --format csv
```

### 2. Scheduled News Collection (`news-collector-scheduled`)

Runs news collection on a daily schedule (default: 9:00 AM):

```bash
# Start the scheduled service
docker-compose up news-collector-scheduled

# To customize the schedule, modify the command in docker-compose.yml or run:
docker-compose run news-collector-scheduled --schedule --daily --hour 14 --minute 30
```

### 3. Weather Collection (`weather-collector`)

Collects weather data for a specified location:

```bash
# Run with default location (New York)
docker-compose up weather-collector

# Run with custom location
docker-compose run weather-collector --weather "London"
```

### 4. Combined Collection (`combined-collector`)

Collects both news and weather data:

```bash
# Run combined collection
docker-compose up combined-collector

# For interactive mode
docker-compose run combined-collector --nw
```

### 5. Development Environment (`news-collector-dev`)

Development service with live code mounting for easier development:

```bash
# Start development service
docker-compose up news-collector-dev

# Run with custom parameters
docker-compose run news-collector-dev "technology" --format json
```

## Customization

### Environment Variables

All services support these environment variables:
- `PYTHONIOENCODING=utf-8`
- `LANG=C.UTF-8`
- `LC_ALL=C.UTF-8`

### Volume Mounting

All services mount these directories:
- `./data:/app/data` - For output files
- `./config:/app/config` - For configuration files

The development service additionally mounts:
- `./src:/app/src` - For live code changes
- `./utils:/app/utils` - For utility scripts

## Advanced Usage

### Health Checks

The scheduled service includes commented-out health check configuration that you can enable:

```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import os; exit(0 if os.path.exists('/app/data') else 1)"]
  interval: 1h
  timeout: 30s
  retries: 3
```

### Resource Limits

You can add resource limits to any service:

```yaml
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 512M
```

## Troubleshooting

### Common Issues

1. **Permission errors with mounted volumes**:
   Ensure the `data` and `config` directories exist and have appropriate permissions.

2. **Chrome/WebDriver issues**:
   The container includes Chrome and chromedriver, but if you encounter issues, you may need to rebuild the container.

### Logs

View logs for any service:

```bash
docker-compose logs news-collector
```

View and follow logs:

```bash
docker-compose logs -f news-collector
```

## Building Images

To rebuild the Docker image:

```bash
docker-compose build
```

To rebuild a specific service:

```bash
docker-compose build news-collector
```