@echo off
REM One-time News Collection Task for {topic}
REM This script runs the news collector once without scheduling

REM Change to the project directory
cd /d "{project_path}"

REM Activate the virtual environment
call venv\Scripts\activate

REM Run the one-time collection script
python src/main.py "{topic}" --format {format} {extra_args}

REM Deactivate the virtual environment
deactivate