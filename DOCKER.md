# Docker Setup for News Collector

This document provides detailed instructions for using Docker with the News Collector project.

## Prerequisites

- Docker Engine 20.10+ or Docker Desktop
- Docker Compose v2+ (included with Docker Desktop)

## Building the Docker Image

### Option 1: Using Docker CLI

```bash
# Build the image
docker build -t news-collector .

# Run a one-time collection
docker run --rm -v $(pwd)/data:/app/data news-collector "artificial intelligence" --format json --full-count 3

# Run with image downloading
docker run --rm -v $(pwd)/data:/app/data news-collector "technology" --images download --full-articles --full-count 5
```

### Option 2: Using Docker Compose

```bash
# Build the image
docker-compose build

# Run a one-time collection
docker-compose run --rm news-collector "artificial intelligence" --format json --full-count 3

# Run with custom command (edit docker-compose.yml to set command)
docker-compose up
```

## Running the Container

### Basic Usage

```bash
# Run with default settings (will show help)
docker run --rm news-collector

# Run a simple collection
docker run --rm -v $(pwd)/data:/app/data news-collector "technology"

# Run with specific format
docker run --rm -v $(pwd)/data:/app/data news-collector "AI" --format csv

# Run with full article scraping
docker run --rm -v $(pwd)/data:/app/data news-collector "machine learning" --full-count 5

# Run with image downloading
docker run --rm -v $(pwd)/data:/app/data news-collector "data science" --images download --full-articles --full-count 3
```

### Volume Mounting

The container uses `/app/data` as the output directory. To persist data between runs, mount a local directory:

```bash
# On Linux/macOS
docker run --rm -v $(pwd)/data:/app/data news-collector "technology"

# On Windows (PowerShell)
docker run --rm -v ${PWD}/data:/app/data news-collector "technology"

# On Windows (Command Prompt)
docker run --rm -v %cd%/data:/app/data news-collector "technology"
```

### Configuration

You can mount a custom configuration file:

```bash
docker run --rm -v $(pwd)/data:/app/data -v $(pwd)/config/settings.cfg:/app/config/settings.cfg news-collector "technology"
```

## Docker Compose Usage

Edit the `docker-compose.yml` file to customize the command:

```yaml
version: '3.8'

services:
  news-collector:
    build: .
    container_name: news-collector
    environment:
      - PYTHONIOENCODING=utf-8
      - LANG=C.UTF-8
      - LC_ALL=C.UTF-8
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    # For running scheduled tasks:
    # command: ["--schedule", "--daily", "--hour", "9", "--minute", "0"]
    # For running a single collection:
    command: ["technology", "--format", "json", "--full-count", "3"]
```

Then run:

```bash
# Run with the configured command
docker-compose up

# Run a one-time collection with custom arguments
docker-compose run --rm news-collector "AI" --format csv --full-count 5
```

## Environment Variables

The Docker image supports the following environment variables:

- `PYTHONIOENCODING`: Set to `utf-8` for proper Unicode handling
- `LANG` and `LC_ALL`: Set to `C.UTF-8` for UTF-8 locale support

## Data Persistence

The container creates the following directories in `/app/data`:
- `logs/`: Application logs
- `images/`: Downloaded images
- `articles/`: Full article text files

Mount these directories to persist data between container runs.

## Troubleshooting

### Common Issues

1. **Permission errors with volume mounts**:
   ```bash
   # On Linux, you might need to adjust permissions
   sudo chown -R $(id -u):$(id -g) data/
   ```

2. **Chrome not starting in container**:
   The Dockerfile includes all necessary dependencies for Chrome. If you encounter issues, ensure you're using the latest image.

3. **Memory issues**:
   For large collections, you might need to increase Docker's memory allocation:
   ```bash
   docker run --rm -m 2g -v $(pwd)/data:/app/data news-collector "technology"
   ```

### Debugging

To debug issues, run the container interactively:

```bash
# Run bash in the container
docker run --rm -it -v $(pwd)/data:/app/data news-collector bash

# Inside the container, you can run commands manually
python src/core/main.py "technology"
```

## Building with Custom Python Version

To build with a specific Python version, modify the Dockerfile:

```dockerfile
# Change this line to use a different Python version
FROM python:3.13-slim
```

## Security Considerations

- The container runs as a non-root user when possible
- Chrome runs in headless mode for security
- No sensitive data is stored in the image by default
- Volumes should be properly secured in production environments

## Production Deployment

For production use, consider:

1. Using a container orchestration platform (Kubernetes, Docker Swarm)
2. Setting up proper logging and monitoring
3. Configuring resource limits
4. Using secrets management for sensitive configuration
5. Implementing backup strategies for persisted data