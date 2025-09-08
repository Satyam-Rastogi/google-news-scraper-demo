#!/bin/bash
# Jenkins deployment script for Google News Scraper API

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="news-scraper-api"
DOCKER_IMAGE="${DOCKER_IMAGE:-news-scraper-api}"
DOCKER_TAG="${DOCKER_TAG:-latest}"
ENVIRONMENT="${ENVIRONMENT:-staging}"

echo -e "${GREEN}🚀 Starting deployment of $PROJECT_NAME${NC}"
echo -e "${YELLOW}Environment: $ENVIRONMENT${NC}"
echo -e "${YELLOW}Image: $DOCKER_IMAGE:$DOCKER_TAG${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Build Docker image
echo -e "${YELLOW}🔨 Building Docker image...${NC}"
docker build -f deployment/docker/Dockerfile -t $DOCKER_IMAGE:$DOCKER_TAG .

# Tag for registry if REGISTRY_URL is provided
if [ ! -z "$REGISTRY_URL" ]; then
    echo -e "${YELLOW}📦 Tagging image for registry...${NC}"
    docker tag $DOCKER_IMAGE:$DOCKER_TAG $REGISTRY_URL/$DOCKER_IMAGE:$DOCKER_TAG
    docker tag $DOCKER_IMAGE:$DOCKER_TAG $REGISTRY_URL/$DOCKER_IMAGE:latest
fi

# Deploy based on environment
if [ "$ENVIRONMENT" = "production" ]; then
    echo -e "${YELLOW}🏭 Deploying to production Kubernetes...${NC}"
    kubectl set image deployment/news-scraper-api news-scraper-api=$DOCKER_IMAGE:$DOCKER_TAG
    kubectl rollout status deployment/news-scraper-api
else
    echo -e "${YELLOW}🧪 Deploying to staging Docker Compose...${NC}"
    cd deployment/docker
    docker-compose down || true
    docker-compose up -d
fi

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 30

# Health check
echo -e "${YELLOW}🏥 Running health checks...${NC}"
if curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API health check passed!${NC}"
else
    echo -e "${RED}❌ API health check failed!${NC}"
    exit 1
fi

# Redis health check
if docker exec news-scraper-redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis health check passed!${NC}"
else
    echo -e "${RED}❌ Redis health check failed!${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo -e "${GREEN}🌐 API is available at: http://localhost:8000${NC}"
echo -e "${GREEN}📚 API docs at: http://localhost:8000/docs${NC}"
