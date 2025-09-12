#!/usr/bin/env python3
"""
Test script to verify the new CLI functionality with weather and combined modes.
"""

import sys
import os

# Add the parent directory to the sys.path to allow imports from src
sys.path.append(".")

from src.core.main import main

def test_news_only():
    """Test news-only functionality (default behavior)"""
    print("Testing news-only functionality...")
    sys.argv = ["main.py", "technology", "--format", "csv", "--limit", "3"]
    try:
        main()
        print("✓ News-only functionality works correctly")
    except Exception as e:
        print(f"✗ News-only functionality failed: {e}")

def test_weather_flag():
    """Test weather flag functionality"""
    print("\nTesting weather flag functionality...")
    sys.argv = ["main.py", "--weather", "London"]
    try:
        main()
        print("✓ Weather flag functionality works correctly")
    except Exception as e:
        print(f"✗ Weather flag functionality failed: {e}")

def test_news_flag():
    """Test news flag functionality"""
    print("\nTesting news flag functionality...")
    sys.argv = ["main.py", "--news", "technology", "--format", "json", "--limit", "2"]
    try:
        main()
        print("✓ News flag functionality works correctly")
    except Exception as e:
        print(f"✗ News flag functionality failed: {e}")

def test_flag_validation():
    """Test flag validation (should fail with multiple flags)"""
    print("\nTesting flag validation...")
    sys.argv = ["main.py", "--news", "--weather", "London"]
    try:
        main()
        print("✗ Flag validation failed - should have rejected multiple flags")
    except SystemExit:
        print("✓ Flag validation works correctly - rejected multiple flags")
    except Exception as e:
        print(f"✗ Flag validation failed with unexpected error: {e}")

if __name__ == "__main__":
    print("Running CLI functionality tests...\n")
    
    # Test existing functionality
    test_news_only()
    test_news_flag()
    
    # Test new functionality
    test_weather_flag()
    test_flag_validation()
    
    print("\nCLI functionality tests completed.")