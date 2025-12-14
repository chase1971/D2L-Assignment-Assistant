# Standard library
import os
import platform
import re
import shutil
import subprocess
import zipfile
from glob import glob
from typing import Optional, Tuple, Dict, Any, Callable, List, Set

# Third-party
import pandas as pd
from rich.console import Console

# Local
from backup_utils import backup_existing_folder
from config_reader import get_downloads_path, get_rosters_path
from import_file_handler import load_import_file, update_import_file
from pdf_operations import create_combined_pdf, split_combined_pdf
from submission_processor import process_submissions
from file_utils import open_file_with_default_app


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def make_error_response(error_msg: str, logs: Optional[list] = None) -> Dict[str, Any]:
    """
    Create a standardized error response dict.

    Args:
        error_msg: The error message to include
        logs: Optional existing logs to append the error to

    Returns:
        Dict with success=False, error message, and logs
    """
    return {
        "success": False,
        "error": error_msg,
        "logs": (logs or []) + [error_msg]
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


def find_zip_file(
    downloads_path: str, 
    specific_zip: Optional[str] = None,
    logs: Optional[list] = None
) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """
    Find ZIP file in Downloads folder or use specific ZIP if provided.
    
    Args:
        downloads_path: Path to Downloads folder
        specific_zip: Optional specific ZIP file path to use
        logs: Optional list to append log messages to
    
    Returns:
        Tuple of (zip_path, error_response_dict):
        - If single ZIP found or specific_zip provided: (zip_path, None)
        - If no ZIPs found: (None, error_response_dict)
        - If multiple ZIPs found: (None, error_response_dict with zip_files list)
    """
    if specific_zip:
        if os.path.exists(specific_zip):
            return specific_zip, None
        else:
            return None, make_error_response(f"Specified ZIP file not found: {specific_zip}", logs)

    # Look for ZIP files in Downloads
    zip_files = glob(os.path.join(downloads_path, "*.zip"))

    if not zip_files:
        return None, make_error_response("No ZIP files found in Downloads folder", logs)
    
    # If multiple ZIP files, return for user selection
    if len(zip_files) > 1:
        error_response = {
            "success": False,
            "error": "Multiple ZIP files found",
            "message": "Please select which ZIP file to process",
            "zip_files": [
                {"index": i+1, "filename": os.path.basename(zip_file), "path": zip_file} 
                for i, zip_file in enumerate(zip_files)
            ],
            "logs": logs or []  # Only include logs up to this point (no file list)
        }
        return None, error_response
    
    # Only one ZIP file found
    return zip_files[0], None


def format_error_message(e: Exception) -> str:
    """
    Convert an exception into a user-friendly error message.
    Uses consistent wording for common error types.
    """
    error_str = str(e).lower()
    
    # Check for common error patterns and return consistent messages
    if "being used by another process" in error_str or "locked" in error_str:
        return "❌ The file is being used by another process"
    
    if "permission denied" in error_str or "errno 13" in error_str or "access denied" in error_str:
        return "❌ Cannot access file - permission denied"
    
    if "could not read" in error_str or "unable to read" in error_str or "cannot read" in error_str:
        return "❌ Unable to read file"
    
    if "not found" in error_str or "no such file" in error_str or "does not exist" in error_str:
        return f"❌ File not found"
    
    if "corrupted" in error_str or "invalid" in error_str or "bad" in error_str:
        return "❌ File is corrupted or invalid"
    
    # For other errors, return the original message with emoji prefix
    return f"❌ {str(e)}"


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


class ProcessingResult:
    """Container for processing results"""
    def __init__(self):
        self.submitted = []
        self.unreadable = []
        self.no_submission = []
        self.combined_pdf_path = None
        self.import_file_path = None
        self.assignment_name = None
        self.total_students = 0


def find_latest_zip(download_folder: str, log_callback: Optional[Callable[[str], None]] = None) -> Tuple[Optional[str], Optional[str]]:
    """Find the latest ZIP file in downloads"""
    if log_callback:
        log_callback("Looking for quiz files in Downloads...")
    
    zip_files = glob(os.path.join(download_folder, "*.zip"))
    
    if not zip_files:
        if log_callback:
            log_callback("No quiz files found in Downloads")
        return None, None
    
    # Sort by modification time (newest first)
    zip_files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    chosen_zip = zip_files[0]
    
    # Extract assignment name from ZIP filename
    assignment_name = extract_assignment_name_from_zip(chosen_zip)
    
    if log_callback:
        log_callback("")
        log_callback(f"Found quiz file: {os.path.basename(chosen_zip)}")
        log_callback(f"Assignment: {assignment_name}")
        log_callback("")
    
    return chosen_zip, assignment_name


def validate_zip_structure(zip_path: str) -> bool:
    """
    Validate that ZIP file contains student assignment folders with correct structure.
    
    Expected structure: Folders named like "ID-ID - Name - Date"
    Example: "575706-1910166 - Jaime Alberto Gonzalez Franco - Oct 21, 2025 1050 PM"
    
    Returns:
        True if ZIP has valid student folder structure, False otherwise
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Get all top-level entries (files and folders)
            entries = zf.namelist()
            
            # Find top-level folders (entries that end with / and have no / before the last one)
            top_level_folders = []
            for entry in entries:
                # Remove leading/trailing slashes and normalize
                normalized = entry.replace('\\', '/').strip('/')
                # Check if it's a top-level folder (has / only at the end, or no / at all)
                parts = normalized.split('/')
                if len(parts) == 1 and entry.endswith('/'):
                    # Top-level folder
                    folder_name = parts[0]
                    if folder_name and folder_name not in ['PDFs', 'index.html']:
                        top_level_folders.append(folder_name)
                elif len(parts) > 1:
                    # Check if first part is a folder we haven't seen
                    folder_name = parts[0]
                    if folder_name and folder_name not in top_level_folders and folder_name not in ['PDFs']:
                        top_level_folders.append(folder_name)
            
            if not top_level_folders:
                return False
            
            # Validate folder names match expected pattern: "ID-ID - Name - Date"
            # Pattern: digits-digits - (name with spaces) - (date)
            pattern = r'^\d+-\d+\s+-\s+.+\s+-\s+.+'
            valid_folders = 0
            
            for folder_name in top_level_folders:
                # Remove trailing slash if present
                clean_name = folder_name.rstrip('/')
                if re.match(pattern, clean_name):
                    valid_folders += 1
            
            # Require at least one valid student folder
            return valid_folders > 0
            
    except Exception:
        return False


def extract_zip_file(zip_path: str, extraction_folder: str, log_callback: Optional[Callable[[str], None]] = None) -> int:
    """Extract ZIP file to the grade processing folder"""
    if log_callback:
        log_callback(f"Validating ZIP file structure...")
    
    # Validate ZIP structure BEFORE extraction
    if not validate_zip_structure(zip_path):
        raise Exception("Zip file does not contain student assignments")
    
    if log_callback:
        log_callback(f"✅ ZIP structure validated")
        log_callback(f"Extracting to: {extraction_folder}")
    
    # Create the extraction folder if it doesn't exist (DON'T delete existing)
    os.makedirs(extraction_folder, exist_ok=True)
    
    index_file_path = None
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Check if index.html exists in the ZIP
            if 'index.html' in zf.namelist():
                # Extract index.html to a temporary location to preserve it
                index_file_path = os.path.join(extraction_folder, 'index.html.original')
                with zf.open('index.html') as index_file:
                    with open(index_file_path, 'wb') as f:
                        f.write(index_file.read())
                if log_callback:
                    log_callback("   Preserved original index.html")
            
            # Extract all files
            zf.extractall(extraction_folder)
    except zipfile.BadZipFile:
        raise Exception("This file can't be opened")
    except zipfile.LargeZipFile:
        raise Exception("This file can't be opened")
    except Exception as e:
        if "BadZipFile" in str(type(e)) or "can't be opened" in str(e).lower():
            raise Exception("This file can't be opened")
        raise
    
    # Count extracted folders (exclude PDFs folder if it exists)
    folder_count = len([d for d in os.listdir(extraction_folder) 
                       if os.path.isdir(os.path.join(extraction_folder, d)) 
                       and d != "PDFs"])
    
    if log_callback:
        log_callback("")
        log_callback(f"✅ Extracted {folder_count} student folders")
        if index_file_path:
            log_callback(f"   Preserved index.html from original ZIP")
        log_callback("")
    
    return folder_count


# ============================================================================
# ORCHESTRATION FUNCTIONS
# ============================================================================


def create_combined_pdf_only(drive_letter, class_folder_name, zip_path, log_callback=None):
    """Create combined PDF without updating grades - just extract and combine"""
    result = ProcessingResult()
    
    try:
        # Extract assignment name from ZIP filename FIRST
        assignment_name = extract_assignment_name_from_zip(zip_path)
        result.assignment_name = assignment_name

        # Get configured rosters path
        rosters_path = get_rosters_path()
        class_folder_path = os.path.join(rosters_path, class_folder_name)
        processing_folder = os.path.join(class_folder_path, f"grade processing {assignment_name}")
        unzipped_folder = os.path.join(processing_folder, "unzipped folders")
        pdf_output_folder = os.path.join(processing_folder, "PDFs")
        unreadable_folder = os.path.join(processing_folder, "unreadable")
        
        if log_callback:
            log_callback(f"Drive: {drive_letter}:")
            log_callback(f"Class: {class_folder_name}")
            log_callback(f"Processing folder: {processing_folder}")
            log_callback("-" * 60)
        
        # Backup existing processing folder if it exists
        backup_existing_folder(processing_folder, log_callback)
        
        if log_callback:
            log_callback(f"Assignment: {assignment_name}")
        
        # Step 1: Extract ZIP to unzipped folders
        extract_zip_file(zip_path, unzipped_folder, log_callback)
        
        # Step 2: Load Import File (skip validation for process quizzes)
        import_df, import_file_path = load_import_file(class_folder_path, log_callback, skip_validation=True)
        if import_df is None:
            raise Exception("Could not load Import File.csv")
        
        result.import_file_path = import_file_path
        result.total_students = len(import_df)
        
        # Step 3: Process submissions (extract PDFs)
        submitted, unreadable, no_submission, pdf_paths, name_map, student_errors, page_counts = process_submissions(
            unzipped_folder, import_df, pdf_output_folder, unreadable_folder, log_callback, is_completion_process=False
        )
        
        # Step 4: Create combined PDF (named after assignment, versioned if exists)
        class_code = extract_class_code(class_folder_name)
        combined_pdf_path = get_versioned_pdf_path(pdf_output_folder, assignment_name, class_code)
        create_combined_pdf(pdf_paths, name_map, combined_pdf_path, log_callback)
        result.combined_pdf_path = combined_pdf_path
        
        if log_callback:
            log_callback(f"   PDF saved as: {os.path.basename(combined_pdf_path)}")
        
        # Store results (but don't update grades)
        result.submitted = [name_map[pdf] for pdf in pdf_paths]
        result.unreadable = [import_df[import_df["Username"] == u]["First Name"].iloc[0].title() + " " + 
                            import_df[import_df["Username"] == u]["Last Name"].iloc[0].title() 
                            for u in unreadable]
        result.no_submission = [import_df[import_df["Username"] == u]["First Name"].iloc[0].title() + " " + 
                               import_df[import_df["Username"] == u]["Last Name"].iloc[0].title() 
                               for u in no_submission]
        
        if log_callback:
            log_callback("")
            log_callback("✅ Combined PDF created!")
            log_callback("")
        
        return result
    
    except Exception as e:
        if log_callback:
            log_callback("")
            log_callback(format_error_message(e))
        raise


def _setup_processing_environment(
    drive_letter: str,
    class_folder_name: str,
    assignment_name: str,
    log_callback: Optional[Callable] = None
) -> Tuple[str, str, str, str, str]:
    """
    Set up processing environment: get paths, backup existing folder.
    
    Args:
        drive_letter: Drive letter (unused but kept for consistency)
        class_folder_name: Name of class folder
        assignment_name: Name of the assignment being processed
        log_callback: Optional callback for logging
    
    Returns:
        Tuple of (class_folder_path, processing_folder, unzipped_folder, pdf_output_folder, unreadable_folder)
    """
    rosters_path = get_rosters_path()
    class_folder_path = os.path.join(rosters_path, class_folder_name)
    processing_folder = os.path.join(class_folder_path, f"grade processing {assignment_name}")
    unzipped_folder = os.path.join(processing_folder, "unzipped folders")
    pdf_output_folder = os.path.join(processing_folder, "PDFs")
    unreadable_folder = os.path.join(processing_folder, "unreadable")
    
    if log_callback:
        log_callback(f"Drive: {drive_letter}:")
        log_callback(f"Class: {class_folder_name}")
        log_callback(f"Processing folder: {processing_folder}")
        log_callback("-" * 60)
    
    # Backup existing processing folder if it exists
    backup_existing_folder(processing_folder, log_callback)
    
    return class_folder_path, processing_folder, unzipped_folder, pdf_output_folder, unreadable_folder


def _extract_and_process_submissions(
    zip_path: str,
    unzipped_folder: str,
    import_df: pd.DataFrame,
    pdf_output_folder: str,
    unreadable_folder: str,
    log_callback: Optional[Callable] = None,
    is_completion_process: bool = False
) -> Tuple[Set[str], Set[str], Set[str], List[str], Dict[str, str], List[str], Dict[str, int]]:
    """
    Extract ZIP and process student submissions.
    
    Args:
        zip_path: Path to ZIP file
        unzipped_folder: Folder to extract student folders to
        import_df: DataFrame with roster data
        pdf_output_folder: Folder to save individual PDFs
        unreadable_folder: Folder for unreadable PDFs
        log_callback: Optional callback for logging
        is_completion_process: Whether this is completion processing
    
    Returns:
        Tuple from process_submissions: (submitted, unreadable, no_submission, pdf_paths, name_map, student_errors, page_counts)
    """
    # Extract ZIP to unzipped folders subfolder
    extract_zip_file(zip_path, unzipped_folder, log_callback)
    
    # Process submissions from unzipped folders
    return process_submissions(
        unzipped_folder, import_df, pdf_output_folder, unreadable_folder,
        log_callback, is_completion_process=is_completion_process
    )


def _create_and_save_combined_pdf(
    pdf_paths: List[str],
    name_map: Dict[str, str],
    assignment_name: str,
    pdf_output_folder: str,
    class_folder_name: str = "",
    log_callback: Optional[Callable] = None
) -> str:
    """
    Create and save combined PDF with versioning.
    
    Args:
        pdf_paths: List of individual PDF paths
        name_map: Dict mapping PDF paths to student names
        assignment_name: Name of assignment
        pdf_output_folder: Folder to save combined PDF
        class_folder_name: Class folder name to extract class code from
        log_callback: Optional callback for logging
    
    Returns:
        Path to created combined PDF
    
    Raises:
        Exception: If no PDFs provided
    """
    if len(pdf_paths) == 0:
        raise Exception("Zip file does not contain student assignments")
    
    # Extract class code from class folder name
    class_code = extract_class_code(class_folder_name) if class_folder_name else ""
    
    combined_pdf_path = get_versioned_pdf_path(pdf_output_folder, assignment_name, class_code)
    create_combined_pdf(pdf_paths, name_map, combined_pdf_path, log_callback)
    
    if log_callback:
        log_callback(f"   PDF saved as: {os.path.basename(combined_pdf_path)}")
    
    return combined_pdf_path


def _setup_import_file_column(
    import_df: pd.DataFrame,
    import_file_path: str,
    assignment_name: str,
    log_callback: Optional[Callable] = None
) -> None:
    """
    Set up assignment column in Import File (for quiz processing).
    
    Creates or renames column E to the assignment name.
    
    Args:
        import_df: DataFrame to update
        import_file_path: Path to save CSV
        assignment_name: Name of assignment
        log_callback: Optional callback for logging
    """
    if log_callback:
        log_callback("")
        log_callback("Setting up Import File column...")
    
    try:
        # Create column name
        column_name = f"{assignment_name} Points Grade"
        
        # Check if column already exists
        if column_name not in import_df.columns:
            # Rename column E (index 4) or add new column
            from grading_constants import REQUIRED_COLUMNS_COUNT
            columns = list(import_df.columns)
            if len(columns) > REQUIRED_COLUMNS_COUNT - 1:
                old_name = columns[REQUIRED_COLUMNS_COUNT - 1]
                columns[REQUIRED_COLUMNS_COUNT - 1] = column_name
                import_df.columns = columns
                if log_callback:
                    log_callback(f"   Created column: '{column_name}'")
            else:
                import_df[column_name] = ""
                if log_callback:
                    log_callback(f"   Added column: '{column_name}'")
            
            # Initialize all cells as blank
            import_df[column_name] = ""
            
            # Save Import File
            try:
                import_df.to_csv(import_file_path, index=False)
            except PermissionError:
                friendly_msg = "You might have the import file open, please close and try again!"
                if log_callback:
                    log_callback(f"   ❌ {friendly_msg}")
                raise Exception(friendly_msg)
            except OSError as e:
                # Check if it's a permission denied error (errno 13)
                if e.errno == 13:
                    friendly_msg = "You might have the import file open, please close and try again!"
                    if log_callback:
                        log_callback(f"   ❌ {friendly_msg}")
                    raise Exception(friendly_msg)
                else:
                    raise
            if log_callback:
                log_callback(f"   Import File ready for grade extraction")
        else:
            if log_callback:
                log_callback(f"   Column already exists: '{column_name}'")
    except Exception as e:
        if log_callback:
            log_callback(f"   Could not setup Import File: {e}")


def run_reverse_process(drive_letter: str, class_folder_name: str, log_callback: Optional[Callable[[str], None]] = None, pdf_path: Optional[str] = None) -> ProcessingResult:
    """Reverse process: Split combined PDF back into individual student PDFs"""
    result = ProcessingResult()
    
    try:
        # Get configured rosters path
        rosters_path = get_rosters_path()
        class_folder_path = os.path.join(rosters_path, class_folder_name)
        
        # If PDF path is provided, determine assignment name and processing folder from it
        assignment_name = None
        processing_folder = None
        pdf_output_folder = None
        unzipped_folder = None
        combined_pdf_path = None
        
        if pdf_path and os.path.exists(pdf_path):
            combined_pdf_path = pdf_path
            # Extract assignment name from PDF filename
            # Format: "Assignment Name CLASS_CODE combined PDF.pdf"
            pdf_filename = os.path.basename(pdf_path)
            # Remove "combined PDF.pdf" suffix and class code
            match = re.match(r'(.+?)\s+(?:[A-Z]{2}\s+\d{4}\s+)?combined PDF\.pdf$', pdf_filename, re.IGNORECASE)
            if match:
                assignment_name = match.group(1).strip()

            # Find the processing folder for this assignment
            if assignment_name:
                processing_folder = os.path.join(class_folder_path, f"grade processing {assignment_name}")

            if log_callback:
                log_callback(f"Using provided PDF: {os.path.basename(combined_pdf_path)}")
        else:
            # No PDF path provided - find the most recent processing folder
            pattern = re.compile(r'^grade processing (.+)$', re.IGNORECASE)
            processing_folders = []
            
            for folder_name in os.listdir(class_folder_path):
                folder_path = os.path.join(class_folder_path, folder_name)
                if os.path.isdir(folder_path):
                    match = pattern.match(folder_name)
                    if match:
                        processing_folders.append(folder_path)
            
            if processing_folders:
                # Sort by modification time (newest first)
                processing_folders.sort(key=lambda f: os.path.getmtime(f), reverse=True)
                processing_folder = processing_folders[0]
                assignment_name = os.path.basename(processing_folder).replace("grade processing ", "")
            else:
                raise Exception("No grade processing folders found")
        
        if not processing_folder or not os.path.exists(processing_folder):
            raise Exception(f"Processing folder not found: {processing_folder if processing_folder else 'Unknown'}")
        
        unzipped_folder = os.path.join(processing_folder, "unzipped folders")
        pdf_output_folder = os.path.join(processing_folder, "PDFs")
        
        if log_callback:
            log_callback(f"Drive: {drive_letter}:")
            log_callback(f"Class: {class_folder_name}")
            log_callback(f"Processing folder: {processing_folder}")
            log_callback("-" * 60)
        
        # Find combined PDF if not already provided
        if not combined_pdf_path:
            if os.path.exists(pdf_output_folder):
                pdf_files = [f for f in os.listdir(pdf_output_folder) if f.endswith('.pdf') and 'combined PDF' in f]
                if pdf_files:
                    # Sort by modification time (newest first)
                    pdf_files.sort(key=lambda f: os.path.getmtime(os.path.join(pdf_output_folder, f)), reverse=True)
                    combined_pdf_path = os.path.join(pdf_output_folder, pdf_files[0])
        
        # Check if combined PDF exists
        if not combined_pdf_path or not os.path.exists(combined_pdf_path):
            if pdf_path:
                raise Exception(f"Specified PDF not found: {pdf_path}")
            else:
                raise Exception(f"Combined PDF not found in: {pdf_output_folder}")
        
        if log_callback:
            log_callback(f"Found combined PDF: {os.path.basename(combined_pdf_path)}")
        
        # Load Import File (skip validation for reverse process - we only need it for name mapping)
        import_df, import_file_path = load_import_file(class_folder_path, log_callback, skip_validation=True)
        if import_df is None:
            raise Exception("Could not load Import File.csv")
        
        result.import_file_path = import_file_path
        result.total_students = len(import_df)
        result.assignment_name = assignment_name  # Store for use in split_pdf_cli.py
        
        # Split the combined PDF back into individual PDFs
        # The split_combined_pdf should place files in unzipped_folder (student folders)
        students_processed = split_combined_pdf(combined_pdf_path, import_df, unzipped_folder, log_callback)
        
        result.submitted = [f"Student {i+1}" for i in range(students_processed)]
        
        if log_callback:
            log_callback("")
            log_callback("=" * 60)
            log_callback("REVERSE PROCESSING COMPLETE!")
            log_callback(f"Processed {students_processed} students")
            log_callback("=" * 60)
            log_callback("")
        
        return result
    
    except Exception as e:
        if log_callback:
            log_callback("")
            log_callback(format_error_message(e))
        raise


def run_grading_process(drive_letter: str, class_folder_name: str, zip_path: str, log_callback: Optional[Callable[[str], None]] = None) -> ProcessingResult:
    """
    Main quiz processing function.
    
    Workflow:
    1. Setup processing environment (paths, backup)
    2. Extract ZIP file to processing folder
    3. Load Import File.csv
    4. Process student submissions (extract PDFs, handle duplicates)
    5. Create combined PDF with watermarks
    6. Setup Import File column for grade entry
    7. Open combined PDF for manual grading
    
    Args:
        drive_letter: Drive letter (for display purposes)
        class_folder_name: Name of class folder
        zip_path: Path to ZIP file containing student submissions
        log_callback: Optional callback for logging messages
    
    Returns:
        ProcessingResult with submission status and file paths
    
    Raises:
        Exception: If processing fails at any step
    """
    result = ProcessingResult()

    try:
        # Extract assignment name from ZIP filename FIRST
        assignment_name = extract_assignment_name_from_zip(zip_path)
        result.assignment_name = assignment_name

        # Setup processing environment with assignment-specific folder
        class_folder_path, processing_folder, unzipped_folder, pdf_output_folder, unreadable_folder = _setup_processing_environment(
            drive_letter, class_folder_name, assignment_name, log_callback
        )

        if log_callback:
            log_callback(f"Assignment: {assignment_name}")

        # Load Import File (skip validation for process quizzes)
        import_df, import_file_path = load_import_file(class_folder_path, log_callback, skip_validation=True)
        if import_df is None:
            raise Exception("Could not load Import File.csv")
        
        result.import_file_path = import_file_path
        result.total_students = len(import_df)
        
        # Extract ZIP and process submissions
        submitted, unreadable, no_submission, pdf_paths, name_map, student_errors, page_counts = _extract_and_process_submissions(
            zip_path, unzipped_folder, import_df, pdf_output_folder, unreadable_folder, log_callback, is_completion_process=False
        )
        
        # Create combined PDF
        combined_pdf_path = _create_and_save_combined_pdf(
            pdf_paths, name_map, assignment_name, pdf_output_folder, class_folder_name, log_callback
        )
        result.combined_pdf_path = combined_pdf_path
        
        # Setup Import File column
        _setup_import_file_column(import_df, import_file_path, assignment_name, log_callback)
        
        # Open the combined PDF for grading
        try:
            if log_callback:
                log_callback("")
                log_callback("Opening combined PDF for manual grading...")
            open_file_with_default_app(combined_pdf_path)
        except Exception as e:
            if log_callback:
                log_callback(f"   Could not open PDF: {e}")
        
        # Store results
        result.submitted = [name_map[pdf] for pdf in pdf_paths]
        result.unreadable = [import_df[import_df["Username"] == u]["First Name"].iloc[0].title() + " " + 
                            import_df[import_df["Username"] == u]["Last Name"].iloc[0].title() 
                            for u in unreadable]
        result.no_submission = [import_df[import_df["Username"] == u]["First Name"].iloc[0].title() + " " + 
                               import_df[import_df["Username"] == u]["Last Name"].iloc[0].title() 
                               for u in no_submission]
        
        if log_callback:
            log_callback("")
            log_callback("=" * 60)
            log_callback("PROCESSING COMPLETE!")
            log_callback("=" * 60)
            log_callback("")
        
        return result
    
    except Exception as e:
        if log_callback:
            log_callback("")
            log_callback(format_error_message(e))
        raise


def run_completion_process(drive_letter: str, class_folder_name: str, zip_path: str, log_callback: Optional[Callable[[str], None]] = None, dont_override: bool = False) -> ProcessingResult:
    """
    Completion processing function - auto-assigns 10 points to all submissions.
    
    Similar to grading process but auto-assigns 10 points to all students who submitted
    (no OCR extraction needed). Validates import file before processing.
    
    Workflow:
    1. Validate ZIP file structure (check for expected folder patterns)
    2. Load Import File and validate structure
    3. Validate that student names in ZIP match Import File
    4. Setup processing environment (paths, backup)
    5. Extract ZIP file to processing folder
    6. Process student submissions (extract PDFs, handle duplicates)
    7. Create combined PDF with watermarks
    8. Update Import File with auto-assigned 10 points
    
    Args:
        drive_letter: Drive letter (for display purposes)
        class_folder_name: Name of class folder
        zip_path: Path to ZIP file containing student submissions
        log_callback: Optional callback for logging messages
        dont_override: If True, add new column after column E instead of overriding it.
                       If False, reset to 6 columns and use column E (existing behavior).
    
    Returns:
        ProcessingResult with submission status and file paths
    
    Raises:
        Exception: If processing fails at any step
    """
    result = ProcessingResult()
    
    try:
        # STEP 1: Validate ZIP file structure FIRST
        if log_callback:
            log_callback("")
            log_callback("=" * 40)
            log_callback("VALIDATION CHECKS")
            log_callback("=" * 40)
            log_callback("")
            log_callback("📦 Step 1: Validating ZIP file structure...")
        
        from zip_validator import validate_zip_structure
        is_valid_zip, zip_error = validate_zip_structure(zip_path)
        if not is_valid_zip:
            raise Exception(f"❌ ZIP validation failed: {zip_error}")
        
        if log_callback:
            log_callback("✅ ZIP file structure is valid")
        
        # Get class folder path early for validation
        rosters_path = get_rosters_path()
        class_folder_path = os.path.join(rosters_path, class_folder_name)
        
        # STEP 2: Validate Import File structure
        if log_callback:
            log_callback("")
            log_callback("📋 Step 2: Validating Import File structure...")
        
        from import_file_handler import validate_import_file_early
        is_valid, error_msg = validate_import_file_early(class_folder_path)
        if not is_valid:
            raise Exception(f"❌ Import File validation failed: {error_msg}")
        
        if log_callback:
            log_callback("✅ Import File structure is valid")
        
        # Load Import File for name validation
        import_df, import_file_path = load_import_file(class_folder_path, log_callback=None)  # Don't log yet
        if import_df is None:
            raise Exception("Could not load Import File.csv")
        
        # STEP 3: Validate student names in ZIP match Import File
        if log_callback:
            log_callback("")
            log_callback("👥 Step 3: Validating student names match Import File...")
        
        from zip_validator import validate_student_names_match
        names_match, name_error, mismatches = validate_student_names_match(zip_path, import_df)
        if not names_match:
            # Build detailed error message
            error_parts = [f"❌ Name validation failed: {name_error}"]
            if mismatches:
                error_parts.append("")
                error_parts.append("Folders in ZIP that don't match Import File:")
                for mismatch in mismatches[:10]:  # Show first 10
                    error_parts.append(f"  • {mismatch}")
                if len(mismatches) > 10:
                    error_parts.append(f"  ... and {len(mismatches) - 10} more")
            raise Exception("\n".join(error_parts))
        
        if log_callback:
            log_callback("✅ All student names match Import File")
            log_callback("")
            log_callback("=" * 40)
            log_callback("VALIDATION COMPLETE - Starting Processing")
            log_callback("=" * 40)
            log_callback("")
        
        # Extract assignment name from ZIP filename
        assignment_name = extract_assignment_name_from_zip(zip_path)
        result.assignment_name = assignment_name

        # Setup processing environment with assignment-specific folder
        class_folder_path, processing_folder, unzipped_folder, pdf_output_folder, unreadable_folder = _setup_processing_environment(
            drive_letter, class_folder_name, assignment_name, log_callback
        )

        if log_callback:
            log_callback(f"Assignment: {assignment_name}")
        
        result.import_file_path = import_file_path
        result.total_students = len(import_df)
        
        # Extract ZIP and process submissions
        submitted, unreadable, no_submission, pdf_paths, name_map, student_errors, page_counts = _extract_and_process_submissions(
            zip_path, unzipped_folder, import_df, pdf_output_folder, unreadable_folder, log_callback, is_completion_process=True
        )
        
        # Create combined PDF
        combined_pdf_path = _create_and_save_combined_pdf(
            pdf_paths, name_map, assignment_name, pdf_output_folder, class_folder_name, log_callback
        )
        result.combined_pdf_path = combined_pdf_path
        
        # Update Import File with auto-assigned 10 points for completions
        # No OCR needed - just assign 10 points to all submitted students
        update_import_file(
            import_df, 
            import_file_path, 
            assignment_name,
            submitted, 
            unreadable, 
            no_submission,
            grades_map=None,  # No OCR grades - auto-assign 10 points
            log_callback=log_callback,
            dont_override=dont_override
        )
        
        # Store results
        result.submitted = [name_map[pdf] for pdf in pdf_paths]
        result.unreadable = [import_df[import_df["Username"] == u]["First Name"].iloc[0].title() + " " + 
                            import_df[import_df["Username"] == u]["Last Name"].iloc[0].title() 
                            for u in unreadable]
        result.no_submission = [import_df[import_df["Username"] == u]["First Name"].iloc[0].title() + " " + 
                               import_df[import_df["Username"] == u]["Last Name"].iloc[0].title() 
                               for u in no_submission]
        
        if log_callback:
            log_callback("")
            log_callback(f"✅ Auto-assigned 10 points to {len(submitted)} submissions")
            log_callback("✅ Completion processing completed!")
            log_callback("")
            
            # Display student errors at the end in red
            if student_errors:
                log_callback("")
                log_callback("❌ STUDENT ERRORS AND WARNINGS:")
                for error in student_errors:
                    log_callback(f"❌ {error}")
            
            log_callback("")
        
        return result
    
    except Exception as e:
        if log_callback:
            log_callback("")
            log_callback(format_error_message(e))
        raise
