"""Import file handling utilities for D2L Assignment Assistant."""

import os
import subprocess
import platform
import time
from typing import Optional, Tuple, Set, Dict, Any, List

import pandas as pd

from name_matching import names_match_fuzzy
from grading_constants import REQUIRED_COLUMNS_COUNT, END_OF_LINE_COLUMN_INDEX, CONFIDENCE_HIGH
from user_messages import log


def validate_required_columns(df: pd.DataFrame) -> Tuple[bool, Optional[List[str]]]:
    """
    Validate that the DataFrame has all required columns.
    
    Args:
        df: DataFrame to validate
    
    Returns:
        Tuple of (is_valid, missing_columns_list)
        - is_valid: True if all required columns exist
        - missing_columns_list: List of missing column friendly names, or None if all present
    """
    required_columns = [
        ("OrgDefinedId", ["org", "defined", "id"]),
        ("Username", ["username"]),
        ("First Name", ["first", "name"]),
        ("Last Name", ["last", "name"]),
        ("Email", ["email"]),
    ]
    
    missing_columns = []
    columns_lower = [str(col).lower() for col in df.columns]
    
    for friendly_name, patterns in required_columns:
        found = False
        for col_lower in columns_lower:
            if all(pattern in col_lower for pattern in patterns):
                found = True
                break
        
        if not found:
            missing_columns.append(friendly_name)
    
    if missing_columns:
        return False, missing_columns
    return True, None


def _close_excel_for_file(file_path: str) -> bool:
    """
    Close any Excel process that might have the specified file open.
    Returns True if Excel was closed, False otherwise.
    """
    if platform.system() != "Windows":
        return False
    
    try:
        # Use PowerShell to find and close Excel processes
        # This closes ALL Excel instances - a more surgical approach would require COM automation
        result = subprocess.run(
            ["taskkill", "/F", "/IM", "EXCEL.EXE"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            log("IMPORT_CLOSED_EXCEL")
            return True
        return False
    except Exception:
        return False


def _validate_and_fix_import_file(
    df: pd.DataFrame, 
    import_file_path: str
) -> pd.DataFrame:
    """
    Validate the import file has required columns and fix structure if needed.
    
    Required structure:
    - Columns 0-4: OrgDefinedId, Username, First Name, Last Name, Email
    - Column 5: End-of-Line Indicator
    
    Returns the fixed DataFrame, or raises an exception if unfixable.
    """
    # Validate required columns using shared function
    is_valid, missing_columns = validate_required_columns(df)
    if not is_valid:
        if len(missing_columns) == 1:
            msg = f"The import file is missing the {missing_columns[0]} column."
        else:
            cols_list = ", ".join(missing_columns[:-1]) + f" and {missing_columns[-1]}"
            msg = f"The import file is missing the {cols_list} columns."
        
        raise Exception(
            f"❌ {msg}\n\n"
            "Please download a fresh import file from D2L that includes all required columns:\n"
            "OrgDefinedId, Username, First Name, Last Name, and Email."
        )
    
    # Check if End-of-Line Indicator exists
    eol_exists = False
    eol_index = None
    for i, col in enumerate(df.columns):
        col_lower = str(col).lower()
        if 'end' in col_lower and 'line' in col_lower:
            eol_exists = True
            eol_index = i
            break
    
    if not eol_exists:
        log("IMPORT_NO_EOL")
        
        # Keep only the first 5 columns, then add End-of-Line Indicator
        df = df.iloc[:, :REQUIRED_COLUMNS_COUNT].copy()
        df['End-of-Line Indicator'] = '#'
        
        # Save the fixed file
        df.to_csv(import_file_path, index=False)
    
    return df


def validate_import_file_early(
    class_folder_path: str
) -> Tuple[bool, Optional[str]]:
    """
    Validate import file exists and can be opened BEFORE processing starts.
    
    Args:
        class_folder_path: Path to the class folder
    
    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if file exists and can be opened
        - error_message: None if valid, error message string if invalid
    """
    import_file_path = os.path.join(class_folder_path, "Import File.csv")
    
    # Check if file exists
    if not os.path.exists(import_file_path):
        return False, "❌ Import file not found. Please download a fresh import file from D2L."
    
    # Try to open and read the file
    try:
        df = pd.read_csv(import_file_path, dtype=str)
    except pd.errors.EmptyDataError:
        return False, "❌ Import file is empty or corrupted. Please download a fresh import file from D2L."
    except pd.errors.ParserError:
        return False, "❌ Import file cannot be opened. The file may be corrupted. Please download a fresh import file from D2L."
    except PermissionError:
        return False, "❌ Import file is locked. Please close Excel and try again."
    except Exception as e:
        error_str = str(e).lower()
        if "being used by another process" in error_str or "locked" in error_str:
            return False, "❌ The file is being used by another process"
        elif "permission denied" in error_str:
            return False, "❌ Cannot access file - permission denied"
        else:
            return False, "❌ Unable to read file"
    
    # Check for required columns using shared function
    is_valid, missing_columns = validate_required_columns(df)
    if not is_valid:
        if len(missing_columns) == 1:
            msg = f"❌ The import file is missing the {missing_columns[0]} column."
        else:
            cols_list = ", ".join(missing_columns[:-1]) + f" and {missing_columns[-1]}"
            msg = f"❌ The import file is missing the {cols_list} columns."
        
        return False, (
            f"{msg}\n\n"
            "Please download a fresh import file from D2L that includes all required columns:\n"
            "OrgDefinedId, Username, First Name, Last Name, and Email."
        )
    
    return True, None


def validate_import_file_early(class_folder_path: str) -> Tuple[bool, str]:
    """
    Validate Import File structure early before processing.
    Checks for required columns without modifying the file.
    
    Args:
        class_folder_path: Path to the class folder
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    import_file_path = os.path.join(class_folder_path, "Import File.csv")
    
    if not os.path.exists(import_file_path):
        return False, f"Import File not found: {import_file_path}"
    
    try:
        df = pd.read_csv(import_file_path, dtype=str)
    except Exception as e:
        error_str = str(e).lower()
        if "being used by another process" in error_str or "locked" in error_str:
            return False, "Import File is being used by another process. Please close Excel and try again."
        elif "permission denied" in error_str:
            return False, "Cannot access Import File - permission denied"
        else:
            return False, f"Error reading Import File: {str(e)}"
    
    # Check for required columns (first 5 columns of Import File)
    # OrgDefinedId, Username, First Name, Last Name, Email
    required_columns = ['OrgDefinedId', 'Username', 'First Name', 'Last Name', 'Email']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        return False, f"Import File is missing required column(s): {', '.join(missing_columns)}"
    
    # For completion processing, we need at least these 5 columns
    if len(df.columns) < 5:
        return False, (
            "Import File doesn't have enough columns. "
            "Expected: OrgDefinedId, Username, First Name, Last Name, Email"
        )
    
    return True, ""


def load_import_file(
    class_folder_path: str, 
    skip_validation: bool = False
) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Load the Import File.csv from a class folder.
    
    Args:
        class_folder_path: Path to the class folder
        skip_validation: If True, skip validation (for process quizzes only)
    
    Returns:
        Tuple of (DataFrame, import_file_path) or (None, None) if not found
    """
    import_file_path = os.path.join(class_folder_path, "Import File.csv")
    
    if not os.path.exists(import_file_path):
        log("IMPORT_FILE_NOT_FOUND", path=import_file_path)
        return None, None
    
    try:
        df = pd.read_csv(import_file_path, dtype=str)
    except Exception as e:
        error_str = str(e).lower()
        if "being used by another process" in error_str or "locked" in error_str:
            log("IMPORT_FILE_IN_USE")
        elif "permission denied" in error_str:
            log("IMPORT_PERMISSION_DENIED")
        else:
            log("IMPORT_UNABLE_TO_READ")
        return None, None
    
    # Validate and fix the import file structure (skip for process quizzes)
    if not skip_validation:
        df = _validate_and_fix_import_file(df, import_file_path)
    
    log("EMPTY_LINE")
    log("IMPORT_LOADED_STUDENTS", count=len(df))
    log("EMPTY_LINE")
    
    return df, import_file_path


def update_import_file(
    import_df: pd.DataFrame, 
    import_file_path: str, 
    assignment_name: str,
    submitted: Set[str], 
    unreadable: Set[str], 
    no_submission: Set[str], 
    grades_map: Optional[Dict[str, Any]] = None, 
    dont_override: bool = False
) -> pd.DataFrame:
    """
    Update the Import File with grades.
    
    Args:
        import_df: DataFrame with student data
        import_file_path: Path to save the updated CSV
        assignment_name: Name of the assignment
        submitted: Set of usernames who submitted
        unreadable: Set of usernames with unreadable submissions
        no_submission: Set of usernames with no submission
        grades_map: Optional dict mapping student names to grades
        dont_override: If True, add new column after column E instead of overriding
    
    Returns:
        Updated DataFrame
    """
    try:
        log("EMPTY_LINE")
        log("SEPARATOR_LINE")
        log("IMPORT_UPDATE_HEADER")
        log("SEPARATOR_LINE")
        log("IMPORT_CURRENT_COLUMNS", columns=list(import_df.columns))
        log("EMPTY_LINE")
        
        # Step 1: Clean up any corrupted columns after End-of-Line Indicator
        import_df = _cleanup_columns_after_eol(import_df)
        
        # Create column name
        column_name = f"{assignment_name} Points Grade"
        
        log("IMPORT_NEW_COLUMN", name=column_name)
        
        # Handle dont_override flag
        if dont_override:
            _handle_dont_override_mode(import_df, column_name)
        else:
            import_df = _handle_override_mode(import_df, column_name)
        
        # Update grades
        log("IMPORT_UPDATING_GRADES")
        
        fuzzy_match_warnings = _update_grades(
            import_df, column_name, submitted, unreadable, 
            grades_map
        )
        
        log("IMPORT_SAVING_TO", path=import_file_path)
        
        # Save the file
        _save_import_file(import_df, import_file_path)
        
        log("EMPTY_LINE")
        if fuzzy_match_warnings:
            log("IMPORT_FUZZY_HEADER")
            for warning in fuzzy_match_warnings:
                log("IMPORT_FUZZY_ITEM", warning=warning)
            log("EMPTY_LINE")
        log("EMPTY_LINE")
        
        return import_df
    
    except Exception as e:
        error_msg = str(e)
        if "You might have the import file open" not in error_msg:
            log("IMPORT_UPDATE_ERROR", error=error_msg)
        raise


def _find_end_of_line_indicator_index(import_df: pd.DataFrame) -> int:
    """Find the index of the End-of-Line Indicator column by name."""
    for i, col in enumerate(import_df.columns):
        col_lower = str(col).lower()
        if 'end' in col_lower and 'line' in col_lower:
            return i
    # Fallback: column 5 (index 5) if we have at least 6 columns
    # Structure: [0:OrgDefinedId, 1:Username, 2:FirstName, 3:LastName, 4:Email, 5:End-of-Line]
    if len(import_df.columns) >= 6:
        return END_OF_LINE_COLUMN_INDEX
    return len(import_df.columns) - 1


def _cleanup_columns_after_eol(import_df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove all columns to the RIGHT of End-of-Line Indicator.
    These are corrupted/duplicate Verify columns that need to be cleaned up.
    """
    eol_index = _find_end_of_line_indicator_index(import_df)
    
    if eol_index < len(import_df.columns) - 1:
        # There are columns after End-of-Line Indicator - remove them
        columns_to_remove = list(import_df.columns[eol_index + 1:])
        if columns_to_remove:
            log("IMPORT_CLEANUP_COLUMNS", count=len(columns_to_remove))
        
        # Keep only columns up to and including End-of-Line Indicator
        import_df = import_df.iloc[:, :eol_index + 1].copy()
    
    return import_df


def _handle_dont_override_mode(
    import_df: pd.DataFrame, 
    column_name: str
) -> None:
    """Handle don't override mode - insert new column before End-of-Line Indicator."""
    log("IMPORT_MODE_DONT_OVERRIDE")
    
    # Ensure we have at least 5 columns (A-E)
    if len(import_df.columns) < REQUIRED_COLUMNS_COUNT:
        log("IMPORT_WARNING_FEW_COLUMNS", required=REQUIRED_COLUMNS_COUNT)
        while len(import_df.columns) < REQUIRED_COLUMNS_COUNT:
            # Use empty string for column name to avoid "Unnamed" issues
            import_df[f'_temp_col_{len(import_df.columns)}'] = ""
    
    # Check if column already exists
    if column_name in import_df.columns:
        log("IMPORT_COLUMN_EXISTS", name=column_name)
    else:
        # Find the End-of-Line Indicator by name (not just last column)
        eol_index = _find_end_of_line_indicator_index(import_df)
        eol_col_name = import_df.columns[eol_index]
        
        # Insert new grade column just before End-of-Line Indicator
        import_df.insert(eol_index, column_name, "")
        log("IMPORT_ADDED_COLUMN", name=column_name, index=eol_index, before=eol_col_name)


def _handle_override_mode(
    import_df: pd.DataFrame, 
    column_name: str
) -> pd.DataFrame:
    """Handle override mode - reset columns, keeping first 5 fixed columns and End-of-Line Indicator."""
    log("IMPORT_MODE_OVERRIDE")
    
    # Find the End-of-Line Indicator by name
    eol_index = _find_end_of_line_indicator_index(import_df)
    eol_col_name = import_df.columns[eol_index]
    
    # First 5 columns are fixed: OrgDefinedId, Username, First Name, Last Name, Email
    first_five_columns = list(import_df.columns[:REQUIRED_COLUMNS_COUNT])
    
    log("IMPORT_FIXED_COLUMNS", count=REQUIRED_COLUMNS_COUNT-1, columns=first_five_columns)
    log("IMPORT_EOL_INFO", name=eol_col_name, index=eol_index)
    log("IMPORT_TOTAL_COLUMNS", count=len(import_df.columns))
    
    # Keep first 5 columns + End-of-Line Indicator (ignore any columns after it)
    columns_to_keep = first_five_columns + [eol_col_name]
    
    if eol_index > REQUIRED_COLUMNS_COUNT:
        columns_removed = list(import_df.columns[REQUIRED_COLUMNS_COUNT:eol_index])
        log("IMPORT_REMOVING_OLD", count=len(columns_removed), columns=columns_removed)
    
    import_df = import_df[columns_to_keep].copy()
    
    # Insert the new grade column at index 5 (after Email, before End-of-Line Indicator)
    import_df.insert(END_OF_LINE_COLUMN_INDEX, column_name, "")
    
    log("IMPORT_RESULT_COLUMNS", count=len(import_df.columns))
    log("IMPORT_ADDED_AT_INDEX", name=column_name)
    
    return import_df


def _update_grades(
    import_df: pd.DataFrame,
    column_name: str,
    submitted: Set[str],
    unreadable: Set[str],
    grades_map: Optional[Dict[str, Any]]
) -> List[str]:
    """Update grades in the DataFrame. Returns list of fuzzy match warnings."""
    fuzzy_match_warnings = []
    
    for idx, row in import_df.iterrows():
        user = row["Username"]
        grade_value = None
        
        if grades_map:
            first = row["First Name"].strip().lower()
            last = row["Last Name"].strip().lower()
            full_name = f"{first} {last}"
            
            # Try exact matching first
            for student_name, grade_data in grades_map.items():
                if isinstance(grade_data, dict):
                    grade = grade_data.get('grade', '')
                else:
                    grade = grade_data
                
                student_name_lower = student_name.strip().lower()
                if student_name_lower == full_name or student_name_lower == f"{last} {first}":
                    grade_value = grade
                    break
            
            # Try fuzzy matching if exact match failed
            if grade_value is None:
                best_match, best_grade, best_similarity = None, None, 0
                
                for student_name, grade_data in grades_map.items():
                    if isinstance(grade_data, dict):
                        grade = grade_data.get('grade', '')
                    else:
                        grade = grade_data
                    
                    student_name_lower = student_name.strip().lower()
                    
                    if names_match_fuzzy(student_name_lower, full_name, threshold=CONFIDENCE_HIGH):
                        words1 = set(student_name_lower.split())
                        words2 = set(full_name.split())
                        similarity = len(words1 & words2) / max(len(words1), len(words2)) if words1 or words2 else 0
                        
                        # Boost for first+last name match
                        if len(student_name_lower.split()) >= 2 and len(full_name.split()) >= 2:
                            name_parts = student_name_lower.split()
                            csv_parts = full_name.split()
                            if name_parts[0] == csv_parts[0] and name_parts[-1] == csv_parts[-1]:
                                similarity = max(similarity, 0.95)
                        
                        if similarity > best_similarity:
                            best_similarity = similarity
                            best_match = student_name
                            best_grade = grade
                
                if best_match and best_grade:
                    grade_value = best_grade
                    fuzzy_match_warnings.append(f"   {best_match} → {full_name.title()} (fuzzy match)")
        
        # Set the grade
        if user in submitted:
            if grade_value and grade_value != "No grade found":
                import_df.at[idx, column_name] = grade_value
            else:
                import_df.at[idx, column_name] = "10"
        elif user in unreadable:
            import_df.at[idx, column_name] = "unreadable"
        else:
            import_df.at[idx, column_name] = "0"
    
    return fuzzy_match_warnings


def _save_import_file(
    import_df: pd.DataFrame, 
    import_file_path: str
) -> None:
    """Save the import file with proper error handling. Auto-closes Excel if needed."""
    # First attempt to save
    try:
        import_df.to_csv(import_file_path, index=False)
        return  # Success on first try
    except (PermissionError, OSError) as e:
        # Check if it's a permission error (file is open)
        if isinstance(e, PermissionError) or (isinstance(e, OSError) and e.errno == 13):
            # Try to close Excel and retry
            if _close_excel_for_file(import_file_path):
                # Give Excel a moment to fully close
                time.sleep(0.5)
                
                # Retry save
                try:
                    import_df.to_csv(import_file_path, index=False)
                    return  # Success after closing Excel
                except (PermissionError, OSError):
                    pass  # Fall through to error message
            
            # If we get here, closing Excel didn't help
            friendly_msg = "You might have the import file open, please close and try again!"
            log("EMPTY_LINE")
            log("IMPORT_UPDATE_ERROR", error=friendly_msg)
            raise Exception(friendly_msg)
        else:
            raise
