# Makefile for Async News Scraper

# Variables
PYTHON = python
UV = uv

# Default target
.PHONY: help
help:
	@echo "Async News Scraper - Development Commands"
	@echo "========================================="
	@echo "setup     - Set up the development environment"
	@echo "install   - Install dependencies"
	@echo "dev       - Install in development mode"
	@echo "clean     - Clean up generated files"
	@echo "test      - Run tests"
	@echo "run       - Run the news collector with a test topic"

# Set up development environment
.PHONY: setup
setup:
	$(UV) venv
	$(UV) pip install -r requirements.txt
	$(UV) pip install -e .

# Install dependencies
.PHONY: install
install:
	$(UV) pip install -r requirements.txt

# Install in development mode
.PHONY: dev
dev:
	$(UV) pip install -e .

# Clean up generated files
.PHONY: clean
clean:
	rm -rf .venv/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

# Run tests
.PHONY: test
test:
	$(PYTHON) -m pytest

# Run with test topic
.PHONY: run
run:
	$(PYTHON) src/core/main.py "artificial intelligence"