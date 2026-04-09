"""
Helper functions for grading processor - extracted utilities.
These functions are pure utilities with no dependencies on main processing logic.
"""

import os
import re
import zipfile
from datetime import date
from typing import Dict, Any, List, Set, Optional
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


def sanitize_processing_folder_basename(name: str) -> str:
    """Remove characters invalid in Windows folder names."""
    invalid = '<>:"/\\|?*'
    for c in invalid:
        name = name.replace(c, "")
    name = name.strip().rstrip(".")
    return name or "Assignment"


def extract_quiz_folder_label_from_text(text: str) -> Optional[str]:
    """Return short label like 'Quiz 4' from assignment or ZIP stem text."""
    if not text:
        return None
    t = text.split(" Download")[0].strip() if " Download" in text else text.strip()
    m = re.search(r"(?i)quiz\s*(\d+)", t)
    if m:
        return sanitize_processing_folder_basename(f"Quiz {m.group(1)}")
    return None


def extract_quiz_folder_label_from_zip(zip_path: str) -> str:
    """
    Short on-disk folder name for quiz exports: 'Quiz' + first number found.
    Scans ZIP file name, then ZIP entry paths, then falls back to a trimmed stem.
    """
    base = os.path.splitext(os.path.basename(zip_path))[0]
    stem = base.split(" Download")[0].strip()
    label = extract_quiz_folder_label_from_text(stem)
    if label:
        return label
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            for name in zf.namelist():
                flat = name.replace("/", " ").replace("\\", " ")
                m = re.search(r"(?i)quiz\s*(\d+)", flat)
                if m:
                    return sanitize_processing_folder_basename(f"Quiz {m.group(1)}")
    except Exception:
        pass
    safe = sanitize_processing_folder_basename(stem)
    if len(safe) > 50:
        safe = safe[:50].rstrip()
    return safe or "Quiz"


def build_completion_processing_folder_basename() -> str:
    """Folder name for a completion run: Completion YYYY-MM-DD (local date when processed)."""
    return sanitize_processing_folder_basename(f"Completion {date.today().isoformat()}")


def assignment_label_from_processing_folder_name(folder_name: str) -> str:
    """
    Map on-disk processing folder basename to an assignment label for PDFs / rezip.
    Supports legacy 'grade processing [code] [name]' and short 'Quiz 4' / 'Completion YYYY-MM-DD'.
    """
    name = re.sub(r"\s+backup\s*$", "", folder_name, flags=re.IGNORECASE).strip()
    lower = name.lower()
    if lower.startswith("grade processing "):
        rest = name[len("grade processing ") :].strip()
        rest = re.sub(r"^\d+-\d+\s+", "", rest).strip()
        rest = re.sub(r"^[A-Z]{2}\s+\d{4}\s+", "", rest).strip()
        return rest or name
    return name


def list_class_processing_folders_with_pdfs(class_folder_path: str) -> List[str]:
    """Subfolders of the class folder that contain a PDFs directory (active workspaces)."""
    if not os.path.isdir(class_folder_path):
        return []
    skip = {"archived folders"}
    out: List[str] = []
    for entry in os.listdir(class_folder_path):
        if entry.lower() in skip:
            continue
        path = os.path.join(class_folder_path, entry)
        if not os.path.isdir(path):
            continue
        if os.path.isdir(os.path.join(path, "PDFs")):
            out.append(path)
    return out


def resolve_workspace_folder_from_assignment_hint(
    class_folder: str,
    class_name: str,
    assignment_name: str,
) -> Optional[str]:
    """
    Resolve a class subfolder path from a UI/CLI hint: short names (Quiz 4, Completion YYYY-MM-DD),
    legacy 'grade processing …', or long D2L-style titles.
    """
    if not assignment_name or not str(assignment_name).strip():
        return None
    stripped = str(assignment_name).strip()
    direct = os.path.join(class_folder, stripped)
    if os.path.isdir(direct):
        return direct

    cleaned_assignment = stripped
    cleaned_assignment = re.sub(
        r"\s+combined\s+pdf\s*$", "", cleaned_assignment, flags=re.IGNORECASE
    )
    class_code = extract_class_code(class_name)
    if class_code:
        class_code_pattern = re.escape(class_code)
        cleaned_assignment = re.sub(
            r"\s*" + class_code_pattern + r"\s*", " ", cleaned_assignment, flags=re.IGNORECASE
        )
        cleaned_assignment = cleaned_assignment.strip()
    cleaned_assignment = re.sub(r"\s+", " ", cleaned_assignment).strip()

    try_paths: List[str] = []
    for name in (stripped, cleaned_assignment):
        if name:
            try_paths.append(os.path.join(class_folder, name))
    quiz_label = extract_quiz_folder_label_from_text(cleaned_assignment)
    if quiz_label:
        try_paths.append(os.path.join(class_folder, quiz_label))
    if class_code:
        try_paths.append(
            os.path.join(class_folder, f"grade processing {class_code} {cleaned_assignment}")
        )
    try_paths.append(
        os.path.join(class_folder, f"grade processing {cleaned_assignment}")
    )

    for path in try_paths:
        if path and os.path.isdir(path):
            return path

    if "completion" in cleaned_assignment.lower():
        comp_re = re.compile(r"^Completion \d{4}-\d{2}-\d{2}$", re.IGNORECASE)
        folders = list_class_processing_folders_with_pdfs(class_folder)
        comp_folders = [f for f in folders if comp_re.match(os.path.basename(f))]
        if comp_folders:
            date_m = re.search(r"(\d{4}-\d{2}-\d{2})", cleaned_assignment)
            if date_m:
                d = date_m.group(1)
                for f in comp_folders:
                    if d in os.path.basename(f):
                        return f
            comp_folders.sort(key=lambda f: os.path.getmtime(f), reverse=True)
            return comp_folders[0]

    pattern = re.compile(r"^grade processing (.+)$", re.IGNORECASE)
    matching_folders: List[str] = []
    for entry_name in os.listdir(class_folder):
        folder_path = os.path.join(class_folder, entry_name)
        if not os.path.isdir(folder_path):
            continue
        m = pattern.match(entry_name)
        if m:
            folder_assignment = m.group(1)
            if (
                cleaned_assignment.lower() in folder_assignment.lower()
                or folder_assignment.lower() in cleaned_assignment.lower()
            ):
                matching_folders.append(folder_path)

    for folder_path in list_class_processing_folders_with_pdfs(class_folder):
        bn = os.path.basename(folder_path)
        bl = bn.lower()
        cl = cleaned_assignment.lower()
        if quiz_label and bl == quiz_label.lower():
            return folder_path
        if cl and (cl in bl or bl in cl):
            if folder_path not in matching_folders:
                matching_folders.append(folder_path)

    if matching_folders:
        return matching_folders[0]

    return None


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
    
    # Check for specific errors before generic "not found"
    if "unzipped folders" in error_str.lower():
        return "No unzipped folders found"
    
    # Preserve context for "not found" errors if they contain useful information
    if "not found" in error_str or "no such file" in error_str or "does not exist" in error_str:
        # If the error message contains a path or specific details, preserve them
        original_msg = str(e)
        if ":" in original_msg or "folder" in error_str or "file" in error_str:
            # Keep the original message if it has context
            return original_msg
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






