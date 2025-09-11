@echo off
REM Setup script for Async News Scraper using uv

echo Setting up Async News Scraper development environment...

REM Check if uv is installed
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: uv is not installed. Please install uv from https://github.com/astral-sh/uv
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
uv venv

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
uv pip install -r requirements.txt

REM Install in development mode
echo Installing in development mode...
uv pip install -e .

echo.
echo Setup complete!
echo.
echo To activate the environment in the future, run:
echo   call .venv\Scripts\activate.bat
echo.
echo To run the news collector, use:
echo   python src/core/main.py "your topic"