#!/usr/bin/env python3
"""
Test script to verify retry mechanisms work correctly
"""

import sys
import os
import logging
from datetime import datetime
from typing import Optional

# Add the parent directory to the sys.path to allow imports from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

from src.utils.retry_utils import retry_with_backoff, CircuitBreaker
from config.config import Config

# Load configuration from file
Config.load_from_file()

# Set up logging
logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Test function that fails a few times then succeeds
attempt_count = 0

@retry_with_backoff(max_retries=3, base_delay=0.5)
def unreliable_function() -> str:
    """Function that fails a few times then succeeds"""
    global attempt_count
    attempt_count += 1
    
    if attempt_count < 3:
        raise ConnectionError(f"Simulated network error on attempt {attempt_count}")
    
    return f"Success on attempt {attempt_count}"

def test_retry_mechanism() -> bool:
    """Test that retry mechanism works correctly"""
    print("=== RETRY MECHANISM TEST ===")
    print(f"Test started at: {datetime.now().isoformat()}")
    print("=" * 50)
    
    global attempt_count
    attempt_count = 0
    
    try:
        result = unreliable_function()
        print(f"Function returned: {result}")
        print(f"Total attempts: {attempt_count}")
        
        if result == "Success on attempt 3" and attempt_count == 3:
            print("[PASS] Retry mechanism test PASSED")
            return True
        else:
            print("[FAIL] Retry mechanism test FAILED")
            return False
            
    except Exception as e:
        print(f"[FAIL] Retry mechanism test FAILED with exception: {e}")
        return False

def test_circuit_breaker() -> bool:
    """Test that circuit breaker works correctly"""
    print("\n=== CIRCUIT BREAKER TEST ===")
    print(f"Test started at: {datetime.now().isoformat()}")
    print("=" * 50)
    
    # Create a circuit breaker with low threshold for testing
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=2)
    
    # Function that always fails
    def always_fails():
        raise ConnectionError("Always fails")
    
    # Test that circuit breaker opens after threshold
    failure_count = 0
    for i in range(5):
        try:
            cb.call(always_fails)
        except Exception as e:
            failure_count += 1
            if i < 2:
                print(f"Attempt {i+1}: Function failed as expected: {e}")
            else:
                # After threshold, should get circuit breaker exception
                if "Circuit breaker is OPEN" in str(e):
                    print(f"Attempt {i+1}: Circuit breaker opened as expected")
                else:
                    print(f"Attempt {i+1}: Unexpected error: {e}")
    
    # Wait for recovery timeout
    print("Waiting for circuit breaker to recover...")
    import time
    time.sleep(3)
    
    # Function that succeeds
    def succeeds():
        return "Success"
    
    # Test that circuit breaker can close again
    try:
        result = cb.call(succeeds)
        if result == "Success":
            print("Circuit breaker closed and function succeeded")
            print("[PASS] Circuit breaker test PASSED")
            return True
        else:
            print("[FAIL] Circuit breaker test FAILED - unexpected result")
            return False
    except Exception as e:
        print(f"[FAIL] Circuit breaker test FAILED with exception: {e}")
        return False

def main() -> bool:
    """Main function for testing retry mechanisms"""
    print("Starting retry mechanism tests...")
    
    # Run the tests
    retry_success = test_retry_mechanism()
    circuit_breaker_success = test_circuit_breaker()
    
    print("\n" + "=" * 50)
    print("FINAL TEST RESULTS:")
    print(f"Retry mechanism: {'[PASS] PASSED' if retry_success else '[FAIL] FAILED'}")
    print(f"Circuit breaker: {'[PASS] PASSED' if circuit_breaker_success else '[FAIL] FAILED'}")
    print("=" * 50)
    
    return retry_success and circuit_breaker_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
