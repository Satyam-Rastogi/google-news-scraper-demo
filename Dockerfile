# Dockerfile for News Collector
# Uses Python 3.13 with latest stable library releases

FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# Set working directory
WORKDIR /app

# Install system dependencies needed for Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    zlib1g-dev \
    wget \
    curl \
    unzip \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome for Selenium
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements.txt .
COPY gnews/requirements.txt gnews/requirements.txt

# Install Python dependencies with latest stable versions
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    # Install gnews dependencies
    && pip install --no-cache-dir -r gnews/requirements.txt \
    # Install the package in development mode
    && pip install --no-cache-dir -e .

# Create directories for data output
RUN mkdir -p data/logs data/images data/articles

# Copy project files
COPY . .

# Expose port for any web interface (if needed in the future)
EXPOSE 8000

# Set the entry point
ENTRYPOINT ["python", "src/core/main.py"]