#!/usr/bin/env python3
"""
User Logger Module - Separates user-facing and developer logs

This module provides two functions:
- user_log(message): Logs messages that should be shown to the user
- dev_log(message): Logs messages for developers only (hidden from users)

All logs are prefixed with [USER] or [DEV] so server.js can separate them.
"""

import sys
from typing import Optional


def user_log(message: str) -> None:
    """
    Log a user-facing message.
    
    This message will be displayed to the user in the LogTerminal component.
    Use this for:
    - Progress updates (✅, 🔬, 📦, etc.)
    - Success messages
    - Error messages that need user action
    - Warnings that need review
    - Status updates
    
    Args:
        message: The message to display to the user
    """
    if message:
        # Prefix with [USER] so server.js can identify it
        print(f"[USER]{message}", file=sys.stdout, flush=True)


def dev_log(message: str) -> None:
    """
    Log a developer-only message.
    
    This message will NOT be displayed to the user (only in expanded/debug mode).
    Use this for:
    - Technical details (file paths, internal state)
    - Debug information
    - Step-by-step processing details
    - API/network calls
    - Module loading messages
    
    Args:
        message: The message for developers only
    """
    if message:
        # Prefix with [DEV] so server.js can identify it
        print(f"[DEV]{message}", file=sys.stdout, flush=True)

