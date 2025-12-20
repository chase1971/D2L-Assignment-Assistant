"""
User Messages Module
Provides centralized logging for all user-facing messages.

Usage:
    from user_messages import log, format_msg
    
    log("QUIZ_SUCCESS")
    log("ERR_FILE_NOT_FOUND", file="Import File.csv")
    
    # For exceptions or passing message elsewhere:
    raise Exception(format_msg("ERR_FILE_NOT_FOUND", file="Import File.csv"))
"""

from .logger import log, format_msg, log_raw
from .catalog import MESSAGES

__all__ = ['log', 'format_msg', 'log_raw', 'MESSAGES']

