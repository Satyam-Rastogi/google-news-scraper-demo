#!/usr/bin/env python3
"""
Test script to verify the homepage functionality.
"""

import sys
import os

# Add the parent directory to the sys.path to allow imports from src
sys.path.append(".")

from src.core.main import main

if __name__ == "__main__":
    # Test with no query (should fetch from homepage)
    sys.argv = ["main.py", "--format", "json", "--limit", "5"]
    main()