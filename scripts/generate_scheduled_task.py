#!/usr/bin/env python3
"""
Utility script to generate scheduled task execution scripts for news collection
"""

import sys
import os
import argparse
from typing import Dict, Any

def read_template(template_name: str) -> str:
    """Read a template file and return its content"""
    template_path = os.path.join(os.path.dirname(__file__), template_name)
    with open(template_path, 'r') as f:
        return f.read()

def generate_script(template_content: str, replacements: Dict[str, Any]) -> str:
    """Generate script content by replacing placeholders in template"""
    script_content = template_content
    for key, value in replacements.items():
        placeholder = f"{{{key}}}"
        script_content = script_content.replace(placeholder, str(value))
    return script_content

def main():
    parser = argparse.ArgumentParser(description="Generate scheduled task execution scripts")
    parser.add_argument("task_name", help="Name of the task (used for filenames)")
    parser.add_argument("topic", help="The search topic for news articles")
    parser.add_argument("--format", "-f", choices=['json', 'csv'], default='json',
                        help="Output format (default: json)")
    parser.add_argument("--full-count", "-c", type=int, default=3,
                        help="Number of top articles to scrape fully (default: 3)")
    parser.add_argument("--no-full-articles", action="store_true",
                        help="Disable full article scraping")
    parser.add_argument("--project-path", "-p", default="..\\\\news_collector_refactored",
                        help="Project directory path")
    
    args = parser.parse_args()
    
    # Prepare replacements for templates
    replacements = {
        'topic': args.topic,
        'format': args.format,
        'full_count': args.full_count,
        'project_path': args.project_path,
        'task_name': args.task_name
    }
    
    # Add extra arguments based on options
    extra_args = ""
    extra_args_powershell = ""
    if args.no_full_articles:
        extra_args = "--no-full-articles"
        extra_args_powershell = ", \"--no-full-articles\""
    else:
        extra_args = f"--full-articles --full-count {args.full_count}"
        extra_args_powershell = f", \"--full-articles\", \"--full-count\", \"{args.full_count}\""
    
    replacements['extra_args'] = extra_args
    replacements['extra_args_powershell'] = extra_args_powershell
    
    # Generate batch file
    batch_template = read_template("template_scheduled_task.bat")
    batch_content = generate_script(batch_template, replacements)
    batch_file_path = os.path.join(args.project_path, f"{args.task_name}_task.bat")
    with open(batch_file_path, 'w') as f:
        f.write(batch_content)
    
    # Generate PowerShell file
    ps1_template = read_template("template_scheduled_task.ps1")
    ps1_content = generate_script(ps1_template, replacements)
    ps1_file_path = os.path.join(args.project_path, f"{args.task_name}_task.ps1")
    with open(ps1_file_path, 'w') as f:
        f.write(ps1_content)
    
    # Generate VBScript file
    vbs_template = read_template("template_scheduled_task.vbs")
    vbs_content = generate_script(vbs_template, replacements)
    vbs_file_path = os.path.join(args.project_path, f"{args.task_name}.vbs")
    with open(vbs_file_path, 'w') as f:
        f.write(vbs_content)
    
    print(f"Successfully generated execution scripts for task '{args.task_name}':")
    print(f"  - {batch_file_path}")
    print(f"  - {ps1_file_path}")
    print(f"  - {vbs_file_path}")
    print("\nTo register with Windows Task Scheduler:")
    print(f"  schtasks /create /tn \"{args.task_name}\" /tr \"{vbs_file_path}\" /sc daily /st HH:MM")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
