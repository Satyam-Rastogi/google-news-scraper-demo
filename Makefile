# Makefile for Google News Scraper API

.PHONY: help install dev build run stop logs deploy clean

# Default target
help: ## Show this help message
	@echo "Google News Scraper API - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Main Commands
install: ## Install dependencies
	uv sync --extra redis

dev: ## Run development server
	uv run python main.py --server

build: ## Build Docker image
	docker build -f deployment/docker/Dockerfile -t news-scraper-api:latest .

run: ## Run with Docker Compose (all services)
	cd deployment/docker && docker-compose up -d

stop: ## Stop all services
	cd deployment/docker && docker-compose down

logs: ## Show logs for all services
	cd deployment/docker && docker-compose logs -f

deploy: ## Deploy using deployment script
	./deployment/scripts/deploy.sh

clean: ## Clean up containers and images
	cd deployment/docker && docker-compose down --rmi all --volumes --remove-orphans
	docker system prune -f

redis: ## Run Redis container
	cd deployment/docker && docker-compose up -d redis

redis-cli: ## Connect to Redis CLI
	docker exec -it news-scraper-redis redis-cli

stop-redis: ## Stop Redis container
	cd deployment/docker && docker-compose down redis

remove-redis: ## Remove Redis container
	docker rm news-scraper-redis

redis-logs: ## Show Redis logs
	cd deployment/docker && docker-compose logs -f redis
	