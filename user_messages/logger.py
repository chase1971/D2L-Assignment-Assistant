"""
LOGGING CONTROLLER
Provides log() and format_msg() functions used throughout the app.

All messages are output with [LOG:LEVEL] prefix for frontend parsing.
"""

import sys
import os
from typing import Optional
from .catalog import MESSAGES
from .file_logger import write_log

# Centralized debug flag - set D2L_DEBUG=true to show debug messages
DEBUG = os.getenv('D2L_DEBUG', 'false').lower() == 'true'

# Ensure UTF-8 output for emojis on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def format_msg(message_id: str, **kwargs) -> str:
    """
    Format a message without printing.
    
    Args:
        message_id: Key from MESSAGES catalog
        **kwargs: Variables to substitute in template
    
    Returns:
        The formatted message string (without error code)
    
    Example:
        msg = format_msg("ERR_FILE_NOT_FOUND", file="Import File.csv")
        raise Exception(msg)
    """
    if message_id not in MESSAGES:
        return f"[UNKNOWN MESSAGE: {message_id}]"
    
    # Handle both 2-tuple (old) and 3-tuple (new) formats for backwards compatibility
    message_data = MESSAGES[message_id]
    if len(message_data) == 3:
        template, level, code = message_data
    else:
        template, level = message_data
        code = None
    
    try:
        return template.format(**kwargs) if kwargs else template
    except KeyError as e:
        return f"[MESSAGE FORMAT ERROR: {message_id} missing {e}]"


def log(message_id: str, **kwargs) -> str:
    """
    Format and print a message to stdout with error code.
    
    The message is printed with [LOG:LEVEL] prefix so server.js can parse it
    and the frontend can style it appropriately. Error codes are appended at the end.
    
    Args:
        message_id: Key from MESSAGES catalog
        **kwargs: Variables to substitute in template
    
    Returns:
        The formatted message string with error code (without [LOG:LEVEL] prefix)
    
    Example:
        log("QUIZ_SUCCESS")  # Prints: [LOG:SUCCESS] ✅ Quiz processing completed! [S1003]
        log("ERR_FILE_NOT_FOUND", file="Import File.csv")  # Prints: [LOG:ERROR] ❌ File not found: Import File.csv [E1013]
    """
    if message_id not in MESSAGES:
        print(f"[LOG:ERROR] [UNKNOWN MESSAGE: {message_id}] [UNKNOWN]", flush=True)
        return f"[UNKNOWN MESSAGE: {message_id}]"
    
    # Handle both 2-tuple (old) and 3-tuple (new) formats for backwards compatibility
    message_data = MESSAGES[message_id]
    if len(message_data) == 3:
        template, level, code = message_data
    else:
        template, level = message_data
        code = None
    
    # Format the message
    try:
        msg = template.format(**kwargs) if kwargs else template
    except KeyError as e:
        msg = f"[MESSAGE FORMAT ERROR: {message_id} missing {e}]"
        code = "UNKNOWN"
    
    # Append error code only for ERROR and WARNING levels (not SUCCESS or INFO)
    if code and level in ("ERROR", "WARNING"):
        full_msg = f"{msg} [{code}]"
    else:
        full_msg = msg
    
    # Write to file if enabled (opt-in via LOG_TO_FILE environment variable)
    write_log(level, code or "", full_msg)
    
    print(f"[LOG:{level}] {full_msg}", flush=True)
    return full_msg


def log_raw(message: str, level: str = "INFO") -> str:
    """
    Log a raw message (not from catalog).
    
    Use sparingly - prefer adding messages to catalog.py for consistency.
    Useful for dynamic content like student names in a list.
    
    Debug messages (containing "🔍 DEBUG:" or level="DEBUG") are filtered
    unless D2L_DEBUG environment variable is set to 'true'.
    
    Args:
        message: The message text to print
        level: SUCCESS, ERROR, WARNING, INFO, or DEBUG
    
    Returns:
        The message string
    """
    # Skip debug messages unless DEBUG flag is set
    if (level == "DEBUG" or "🔍 DEBUG:" in message) and not DEBUG:
        return message
    
    # Write to file if enabled (opt-in via LOG_TO_FILE environment variable)
    write_log(level, "", message)  # No error code for raw messages
    
    print(f"[LOG:{level}] {message}", flush=True)
    return message

