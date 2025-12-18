"""
FILE LOGGER
Optional file logging for distribution and debugging.

Logs are written to disk only when LOG_TO_FILE environment variable is set to 'true'.
This allows users to share log files for troubleshooting without cluttering
the default workflow.
"""

import os
from datetime import datetime
from pathlib import Path

# Opt-in flag - set LOG_TO_FILE=true to enable file logging
LOG_TO_FILE = os.getenv('LOG_TO_FILE', 'false').lower() == 'true'

# Log directory - can be customized via LOG_DIR environment variable
LOG_DIR = os.getenv('LOG_DIR', 'logs')


def init_log_file():
    """Create logs directory if needed"""
    if LOG_TO_FILE and not os.path.exists(LOG_DIR):
        try:
            os.makedirs(LOG_DIR, exist_ok=True)
        except Exception:
            # Silently fail if we can't create directory
            pass


def write_log(level: str, code: str, message: str):
    """
    Write log entry to file if enabled.
    
    Args:
        level: SUCCESS, ERROR, WARNING, INFO, or DEBUG
        code: Error code (e.g., "E1001") or None
        message: The full message text
    """
    if not LOG_TO_FILE:
        return
    
    try:
        init_log_file()
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_file = os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y-%m-%d')}.log")
        
        # Format: timestamp [level] [code] message
        log_entry = f"{timestamp} [{level}]"
        if code:
            log_entry += f" [{code}]"
        log_entry += f" {message}\n"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception:
        # Silently fail if file logging encounters errors
        # Don't break the main application if logging fails
        pass








