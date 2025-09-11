# One-time News Collection Task for {topic}
# This script runs the news collector once without scheduling

# Change to the project directory
Set-Location -Path "{project_path}"

# Activate the virtual environment and run the script
Start-Process -FilePath ".\venv\Scripts\python.exe" -ArgumentList "src/main.py", "{topic}", "--format", "{format}" {extra_args_powershell} -WindowStyle Hidden -Wait