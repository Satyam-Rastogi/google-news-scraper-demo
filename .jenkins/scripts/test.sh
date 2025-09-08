#!/bin/bash
# Jenkins test script for Google News Scraper API

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🧪 Running tests for Google News Scraper API${NC}"

# Setup Python environment
echo -e "${YELLOW}📦 Setting up Python environment...${NC}"
python -m venv venv
source venv/bin/activate
pip install uv
uv sync --extra redis

# Run linting
echo -e "${YELLOW}🔍 Running linting...${NC}"
uv run ruff check src/ || {
    echo -e "${RED}❌ Linting failed!${NC}"
    exit 1
}

# Run format check
echo -e "${YELLOW}🎨 Checking code format...${NC}"
uv run ruff format --check src/ || {
    echo -e "${RED}❌ Format check failed!${NC}"
    exit 1
}

# Run security scan
echo -e "${YELLOW}🔒 Running security scan...${NC}"
uv run bandit -r src/ -f json -o security-report.json || true

# Run unit tests
echo -e "${YELLOW}🧪 Running unit tests...${NC}"
uv run pytest tests/ -v --cov=src --cov-report=xml --cov-report=html || {
    echo -e "${RED}❌ Unit tests failed!${NC}"
    exit 1
}

# Run integration tests (if they exist)
if [ -d "tests/integration" ]; then
    echo -e "${YELLOW}🔗 Running integration tests...${NC}"
    uv run pytest tests/integration/ -v || {
        echo -e "${RED}❌ Integration tests failed!${NC}"
        exit 1
    }
fi

echo -e "${GREEN}✅ All tests passed!${NC}"
