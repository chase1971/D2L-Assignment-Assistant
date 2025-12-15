"""
LOGGING CONTROLLER
Provides log() and format_msg() functions used throughout the app.

All messages are output with [LOG:LEVEL] prefix for frontend parsing.
"""

import sys
from typing import Optional
from .catalog import MESSAGES

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
        The formatted message string
    
    Example:
        msg = format_msg("ERR_FILE_NOT_FOUND", file="Import File.csv")
        raise Exception(msg)
    """
    if message_id not in MESSAGES:
        return f"[UNKNOWN MESSAGE: {message_id}]"
    template, level = MESSAGES[message_id]
    try:
        return template.format(**kwargs) if kwargs else template
    except KeyError as e:
        return f"[MESSAGE FORMAT ERROR: {message_id} missing {e}]"


def log(message_id: str, **kwargs) -> str:
    """
    Format and print a message to stdout.
    
    The message is printed with [LOG:LEVEL] prefix so server.js can parse it
    and the frontend can style it appropriately.
    
    Args:
        message_id: Key from MESSAGES catalog
        **kwargs: Variables to substitute in template
    
    Returns:
        The formatted message string (without prefix)
    
    Example:
        log("QUIZ_SUCCESS")
        log("ERR_FILE_NOT_FOUND", file="Import File.csv")
        log("QUIZ_EXTRACTED", count=26)
    """
    msg = format_msg(message_id, **kwargs)
    
    if message_id in MESSAGES:
        level = MESSAGES[message_id][1]
    else:
        level = "ERROR"
    
    print(f"[LOG:{level}] {msg}", flush=True)
    return msg


def log_raw(message: str, level: str = "INFO") -> str:
    """
    Log a raw message (not from catalog).
    
    Use sparingly - prefer adding messages to catalog.py for consistency.
    Useful for dynamic content like student names in a list.
    
    Args:
        message: The message text to print
        level: SUCCESS, ERROR, WARNING, or INFO
    
    Returns:
        The message string
    """
    print(f"[LOG:{level}] {message}", flush=True)
    return message

