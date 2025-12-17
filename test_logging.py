#!/usr/bin/env python3
"""
Test script for logging enhancements.

Run this to verify:
1. Error codes appear on ERROR/WARNING but not SUCCESS/INFO
2. DEBUG flag filters debug messages
3. File logging works when enabled
4. Developer error logging works
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from user_messages import log, log_raw

def test_error_codes():
    """Test that error codes appear only on ERROR/WARNING messages"""
    print("\n" + "="*60)
    print("TEST 1: Error Codes")
    print("="*60)
    print("SUCCESS message (should NOT have code):")
    log("QUIZ_SUCCESS")
    
    print("\nINFO message (should NOT have code):")
    log("QUIZ_SEARCHING")
    
    print("\nERROR message (should HAVE code):")
    log("ERR_FILE_NOT_FOUND", file="test.csv")
    
    print("\nWARNING message (should HAVE code):")
    log("GRADES_ISSUES_HEADER")


def test_debug_flag():
    """Test that DEBUG flag controls debug message visibility"""
    print("\n" + "="*60)
    print("TEST 2: DEBUG Flag")
    print("="*60)
    
    debug_enabled = os.getenv('D2L_DEBUG', 'false').lower() == 'true'
    print(f"D2L_DEBUG is: {os.getenv('D2L_DEBUG', 'false')} (enabled: {debug_enabled})")
    
    print("\nDebug message (should be hidden unless D2L_DEBUG=true):")
    log_raw("🔍 DEBUG: This is a debug message", "DEBUG")
    
    print("\nRegular message (should always show):")
    log_raw("This is a regular message", "INFO")


def test_file_logging():
    """Test that file logging works when enabled"""
    print("\n" + "="*60)
    print("TEST 3: File Logging")
    print("="*60)
    
    log_to_file = os.getenv('LOG_TO_FILE', 'false').lower() == 'true'
    log_dir = os.getenv('LOG_DIR', 'logs')
    
    print(f"LOG_TO_FILE is: {os.getenv('LOG_TO_FILE', 'false')} (enabled: {log_to_file})")
    print(f"LOG_DIR is: {log_dir}")
    
    if log_to_file:
        log_file = os.path.join(log_dir, f"{__import__('datetime').datetime.now().strftime('%Y-%m-%d')}.log")
        print(f"\nLogs should be written to: {log_file}")
        if os.path.exists(log_file):
            print(f"✅ Log file exists!")
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"   File has {len(lines)} lines")
                if lines:
                    print(f"   Last line: {lines[-1].strip()}")
        else:
            print(f"⚠️  Log file doesn't exist yet (will be created on first log)")
    else:
        print("\n⚠️  File logging is disabled. Set LOG_TO_FILE=true to test.")
    
    print("\nSending test messages (will be logged to file if enabled):")
    log("QUIZ_SUCCESS")
    log("ERR_FILE_NOT_FOUND", file="test.csv")


def test_dev_logging():
    """Test that developer error logging works"""
    print("\n" + "="*60)
    print("TEST 4: Developer Error Logging")
    print("="*60)
    print("Simulating silent error scenarios...")
    
    print("\n1. Testing DEV_ERROR_OPEN_PDF:")
    try:
        # This will fail - file doesn't exist
        with open("nonexistent_file.pdf", "r") as f:
            pass
    except Exception as e:
        log("DEV_ERROR_OPEN_PDF", error=str(e))
    
    print("\n2. Testing DEV_ERROR_PARSE_INDEX:")
    try:
        # This will fail - invalid JSON
        import json
        json.loads("invalid json {")
    except Exception as e:
        log("DEV_ERROR_PARSE_INDEX", error=str(e))
    
    print("\n✅ Developer errors logged (check logs/ directory if LOG_TO_FILE=true)")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("LOGGING SYSTEM TEST SUITE")
    print("="*60)
    print("\nTo test file logging, run:")
    print("  set LOG_TO_FILE=true")
    print("  python test_logging.py")
    print("\nTo test debug messages, run:")
    print("  set D2L_DEBUG=true")
    print("  python test_logging.py")
    
    test_error_codes()
    test_debug_flag()
    test_file_logging()
    test_dev_logging()
    
    print("\n" + "="*60)
    print("TESTING COMPLETE")
    print("="*60)
    print("\nCheck the frontend to verify:")
    print("  - ERROR/WARNING messages have codes")
    print("  - SUCCESS/INFO messages don't have codes")
    print("  - [LOG:LEVEL] prefix is stripped (not visible to user)")


if __name__ == "__main__":
    main()






