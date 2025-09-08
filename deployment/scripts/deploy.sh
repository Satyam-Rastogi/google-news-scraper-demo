#!/bin/bash
# Deployment script for Google News Scraper API

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="news-scraper-api"
DOCKER_COMPOSE_FILE="deployment/docker/docker-compose.yml"

echo -e "${GREEN}🚀 Starting deployment of $PROJECT_NAME${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Check if docker-compose file exists
if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
    echo -e "${RED}❌ Docker compose file not found: $DOCKER_COMPOSE_FILE${NC}"
    exit 1
fi

# Stop existing containers
echo -e "${YELLOW}🛑 Stopping existing containers...${NC}"
docker-compose -f $DOCKER_COMPOSE_FILE down

# Remove old images (optional)
if [ "$1" = "--clean" ]; then
    echo -e "${YELLOW}🧹 Cleaning up old images...${NC}"
    docker-compose -f $DOCKER_COMPOSE_FILE down --rmi all
fi

# Build and start containers
echo -e "${YELLOW}🔨 Building and starting containers...${NC}"
docker-compose -f $DOCKER_COMPOSE_FILE up --build -d

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 10

# Check health
echo -e "${YELLOW}🏥 Checking service health...${NC}"
if curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Service is healthy!${NC}"
    echo -e "${GREEN}🌐 API is available at: http://localhost:8000${NC}"
    echo -e "${GREEN}📚 API docs at: http://localhost:8000/docs${NC}"
else
    echo -e "${RED}❌ Service health check failed!${NC}"
    echo -e "${YELLOW}📋 Checking logs...${NC}"
    docker-compose -f $DOCKER_COMPOSE_FILE logs
    exit 1
fi

# Show running containers
echo -e "${GREEN}📦 Running containers:${NC}"
docker-compose -f $DOCKER_COMPOSE_FILE ps

echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
