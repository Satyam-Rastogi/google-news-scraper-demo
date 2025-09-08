#!/bin/bash
# Stop script for Google News Scraper API

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DOCKER_COMPOSE_FILE="deployment/docker/docker-compose.yml"

echo -e "${YELLOW}🛑 Stopping Google News Scraper API...${NC}"

# Check if docker-compose file exists
if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
    echo -e "${RED}❌ Docker compose file not found: $DOCKER_COMPOSE_FILE${NC}"
    exit 1
fi

# Stop containers
docker-compose -f $DOCKER_COMPOSE_FILE down

echo -e "${GREEN}✅ Service stopped successfully!${NC}"
