#!/bin/bash
# Logs script for Google News Scraper API

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DOCKER_COMPOSE_FILE="deployment/docker/docker-compose.yml"

echo -e "${YELLOW}📋 Showing logs for Google News Scraper API...${NC}"

# Check if docker-compose file exists
if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
    echo -e "${RED}❌ Docker compose file not found: $DOCKER_COMPOSE_FILE${NC}"
    exit 1
fi

# Show logs
if [ "$1" = "--follow" ] || [ "$1" = "-f" ]; then
    echo -e "${GREEN}📊 Following logs (Ctrl+C to stop)...${NC}"
    docker-compose -f $DOCKER_COMPOSE_FILE logs -f
else
    docker-compose -f $DOCKER_COMPOSE_FILE logs
fi
