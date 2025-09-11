#!/usr/bin/env python3
"""
Test script to verify the new functionality with the updated features.
"""

import sys
import os

# Add the parent directory to the sys.path to allow imports from src
sys.path.append(".")

from src.core.main import main

if __name__ == "__main__":
    # Test with a simple query and new arguments
    sys.argv = ["main.py", "technology", "--format", "csv", "--limit", "5", "--images", "url-only"]
    main()