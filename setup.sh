#!/bin/bash
# Setup script for Async News Scraper using uv

echo "Setting up Async News Scraper development environment..."

# Check if uv is installed
if ! command -v uv &> /dev/null
then
    echo "Error: uv is not installed. Please install uv from https://github.com/astral-sh/uv"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
uv venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
uv pip install -r requirements.txt

# Install in development mode
echo "Installing in development mode..."
uv pip install -e .

echo ""
echo "Setup complete!"
echo ""
echo "To activate the environment in the future, run:"
echo "  source .venv/bin/activate"
echo ""
echo "To run the news collector, use:"
echo "  python src/core/main.py \"your topic\""