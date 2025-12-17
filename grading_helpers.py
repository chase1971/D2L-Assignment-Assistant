"""
Helper functions for grading processor - extracted utilities.
These functions are pure utilities with no dependencies on main processing logic.
"""

import os
import re
from typing import Dict, Any, List, Set
import pandas as pd
from user_messages import log, format_msg


def make_error_response(message_id: str, **kwargs) -> Dict[str, Any]:
    """
    Create a standardized error response dict using the message catalog.
    
    Args:
        message_id: The message ID from the catalog
        **kwargs: Format variables for the message
    
    Returns:
        Dict with success=False and formatted error message
    """
    log(message_id, **kwargs)  # Log the error to stdout
    return {
        "success": False,
        "error": format_msg(message_id, **kwargs)
    }


def extract_assignment_name_from_zip(zip_path: str) -> str:
    """
    Extract assignment name from a ZIP filename.

    Removes the " Download..." suffix that D2L adds to exported ZIPs.

    Args:
        zip_path: Full path to the ZIP file

    Returns:
        Assignment name extracted from filename

    Example:
        "Quiz 4 (7.1-7.4) Download Oct 21 2025.zip" -> "Quiz 4 (7.1-7.4)"
    """
    base = os.path.splitext(os.path.basename(zip_path))[0]
    return base.split(" Download")[0].strip()


def get_student_display_name(import_df: pd.DataFrame, username: str) -> str:
    """
    Get formatted display name for a student from the import DataFrame.

    Args:
        import_df: DataFrame with roster data
        username: Student's username to look up

    Returns:
        Title-cased "First Last" name string
    """
    row = import_df[import_df["Username"] == username]
    if len(row) == 0:
        return username
    first = row["First Name"].iloc[0]
    last = row["Last Name"].iloc[0]
    return f"{first.title()} {last.title()}"


def get_student_names_list(
    import_df: pd.DataFrame,
    usernames: Set[str]
) -> List[str]:
    """
    Convert a set of usernames to a list of formatted display names.

    Args:
        import_df: DataFrame with roster data
        usernames: Set of usernames to convert

    Returns:
        List of title-cased "First Last" name strings
    """
    return [get_student_display_name(import_df, u) for u in usernames]


def format_error_message(e: Exception) -> str:
    """
    Convert an exception into a user-friendly error message.
    Uses consistent wording for common error types.
    Note: Does NOT add ❌ prefix - that's added by the catalog system.
    """
    error_str = str(e).lower()
    
    # Check for common error patterns and return consistent messages
    if "being used by another process" in error_str or "locked" in error_str:
        return "The file is being used by another process"
    
    if "permission denied" in error_str or "errno 13" in error_str or "access denied" in error_str:
        return "Cannot access file - permission denied"
    
    if "could not read" in error_str or "unable to read" in error_str or "cannot read" in error_str:
        return "Unable to read file"
    
    if "not found" in error_str or "no such file" in error_str or "does not exist" in error_str:
        return "File not found"
    
    if "corrupted" in error_str or "invalid" in error_str or "bad" in error_str:
        return "File is corrupted or invalid"
    
    # For other errors, return the original message (without emoji - catalog adds it)
    return str(e)


def extract_class_code(class_folder_name: str) -> str:
    """
    Extract class code (e.g., "FM 4202") from class folder name.
    
    Examples:
        "TTH 11-1220 FM 4202" -> "FM 4202"
        "MW 930-1050 CA 4105" -> "CA 4105"
    """
    # Class code is typically the last 7 characters (2 letters, space, 4 digits)
    # But handle variations - look for pattern: 2 letters, space, 4 digits at the end
    match = re.search(r'([A-Z]{2}\s+\d{4})\s*$', class_folder_name)
    if match:
        return match.group(1)
    # Fallback: try to extract last 7 characters
    if len(class_folder_name) >= 7:
        return class_folder_name[-7:].strip()
    return ""


def get_versioned_pdf_path(output_folder: str, assignment_name: str, class_code: str = "") -> str:
    """
    Generate a versioned PDF filename based on assignment name, class code, and "combined PDF".
    
    Format: "{assignment_name} {class_code} combined PDF.pdf"
    If the file already exists, appends v2, v3, etc.
    
    Examples:
        - First run: "Quiz 4 (7.1 - 7.4) FM 4202 combined PDF.pdf"
        - Second run: "Quiz 4 (7.1 - 7.4) FM 4202 combined PDF v2.pdf"
    """
    # Clean assignment name for use as filename (remove invalid chars)
    safe_name = re.sub(r'[<>:"/\\|?*]', '', assignment_name).strip()
    
    # Build filename with class code and "combined PDF"
    if class_code:
        base_filename = f"{safe_name} {class_code} combined PDF"
    else:
        base_filename = f"{safe_name} combined PDF"
    
    base_path = os.path.join(output_folder, f"{base_filename}.pdf")
    
    # If doesn't exist, use the base name
    if not os.path.exists(base_path):
        return base_path
    
    # Find next available version number
    version = 2
    while True:
        versioned_path = os.path.join(output_folder, f"{base_filename} v{version}.pdf")
        if not os.path.exists(versioned_path):
            return versioned_path
        version += 1






