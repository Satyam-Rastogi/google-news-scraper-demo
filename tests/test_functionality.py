"""
Test script to verify the updated functionality with decoded URLs and markdown generation.
"""
import sys
import os

# Add the parent directory to the sys.path to allow imports from src
sys.path.append(".")

from src.core.main import main

if __name__ == "__main__":
    # Test with a simple query
    sys.argv = ["main.py", "technology", "--format", "csv", "--full-count", "2"]
    main()
