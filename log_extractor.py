#!/usr/bin/env python3
"""
Log Extractor - Scans all source files and extracts logging statements
Generates extracted_logs.json with file paths, line numbers, and message content
Groups logs by scenario/use case with example values
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

# Patterns to detect logging statements
PYTHON_PATTERNS = [
    # New logging system (preferred)
    (r'user_log\s*\(\s*[f]?["\'](.+?)["\']\s*\)', 'user_log'),
    (r'user_log\s*\(\s*f["\'](.+?)["\']\s*\)', 'user_log'),
    (r'dev_log\s*\(\s*[f]?["\'](.+?)["\']\s*\)', 'dev_log'),
    (r'dev_log\s*\(\s*f["\'](.+?)["\']\s*\)', 'dev_log'),
    # Legacy patterns (still supported)
    (r'log_callback\s*\(\s*[f]?["\'](.+?)["\']\s*\)', 'log_callback'),
    (r'log_callback\s*\(\s*f["\'](.+?)["\']\s*\)', 'log_callback'),
    (r'logs\.append\s*\(\s*[f]?["\'](.+?)["\']\s*\)', 'logs.append'),
    (r'logs\.append\s*\(\s*f["\'](.+?)["\']\s*\)', 'logs.append'),
    (r'print\s*\(\s*[f]?["\'](.+?)["\']\s*\)', 'print'),
    (r'console\.print\s*\(\s*[f]?["\'](.+?)["\']\s*\)', 'console.print'),
]

TYPESCRIPT_PATTERNS = [
    (r'addLog\s*\(\s*[`\'"](.+?)[`\'"]\s*\)', 'addLog'),
    (r'addLog\s*\(\s*`(.+?)`\s*\)', 'addLog'),
]

# Example values for common variable patterns
# Order matters: specific patterns first, generic last
EXAMPLE_VALUES = {
    # Format specifier patterns (MUST come first - most specific)
    # These handle Python f-string format specifiers like {var:.2f}, {var:2d}
    r"\{conf:\.2f\}": "0.92",
    r"\{conf:\d*\.?\d*[fd]\}": "0.92",
    r"\{i:\d*d\}": " 1",
    r"\{[^}]*:\d*\.?\d*[fd]\}": "0.92",  # Catch-all for numeric format specifiers
    
    # Dictionary/object access patterns (common in grade extraction)
    r"\{sg\['name'\]\}": "John Smith",
    r"\{sg\['grade'\]\}": "95",
    r"\{sg\['confidence'\]\}": "0.92",
    r"\{grade_info\.get\([^)]+\)\}": "85",
    r"\{grade_info\[['\"]grade['\"]\]\}": "85",
    r"\{grade_info\[['\"]confidence['\"]\]\}": "0.92",
    r"\{skipped\['name'\]\}": "Bob Wilson",
    r"\{skipped\['grade'\]\}": "75",
    r"\{skipped\['confidence'\]\}": "0.45",
    r"\{skipped\['reason'\]\}": "Could not match to roster",
    
    # Indicator/emoji patterns
    r"\{conf_indicator\}": "✅",
    r"\{[^}]*indicator[^}]*\}": "✅",
    
    # File/path related
    r'\{os\.path\.basename\([^)]+\)\}': 'Assignment1-Dec2024.zip',
    r'\{[^}]*basename[^}]*\}': 'Assignment1-Dec2024.zip',
    r'\{[^}]*zip_file[^}]*\}': 'Quiz3-submissions.zip',
    r'\{[^}]*zip_path[^}]*\}': 'Quiz3-submissions.zip',
    r'\{[^}]*pdf_path[^}]*\}': 'Combined_Grades.pdf',
    r'\{[^}]*pdf_name[^}]*\}': 'Combined_Grades.pdf',
    r'\{[^}]*file_path[^}]*\}': 'Import File.csv',
    r'\{[^}]*file_name[^}]*\}': 'Import File.csv',
    r'\{[^}]*import_file[^}]*\}': 'Import File.csv',
    r'\{[^}]*filename[^}]*\}': 'StudentSubmission.pdf',
    r'\{[^}]*backup_name[^}]*\}': 'Grade Processing_backup_2024-12-13',
    r'\{[^}]*folder_path[^}]*\}': 'C:/Classes/MATH101/Grade Processing',
    r'\{[^}]*folder_name[^}]*\}': 'Grade Processing',
    r'\{[^}]*class_folder[^}]*\}': 'MATH 101 - Fall 2024',
    r'\{[^}]*class_name[^}]*\}': 'MATH 101 - Fall 2024',
    r'\{[^}]*extraction_folder[^}]*\}': 'Grade Processing',
    r'\{[^}]*output_path[^}]*\}': 'C:/Classes/MATH101/Combined.pdf',
    
    # Count/number related
    r'\{[^}]*folder_count[^}]*\}': '25',
    r'\{[^}]*count[^}]*\}': '15',
    r'\{[^}]*len\([^)]+\)[^}]*\}': '12',
    r'\{[^}]*num_[^}]*\}': '8',
    r'\{[^}]*total[^}]*\}': '30',
    r'\{[^}]*i\s*\+\s*1[^}]*\}': '5',
    r'\{[^}]*index[^}]*\}': '3',
    r'\{[^}]*page[^}]*\}': '1',
    r'\{[^}]*pages[^}]*\}': '45',
    
    # Student/name related
    r'\{[^}]*student_name[^}]*\}': 'John Smith',
    r'\{[^}]*student[^}]*\}': 'John Smith: 87 (low confidence: 0.65 – needs verification)',
    r'\{[^}]*name[^}]*\}': 'Jane Doe',
    r'\{[^}]*first_name[^}]*\}': 'John',
    r'\{[^}]*last_name[^}]*\}': 'Smith',
    r'\{[^}]*username[^}]*\}': 'jsmith01',
    r'\{[^}]*student_id[^}]*\}': '12345678',
    r'\{[^}]*best_match[^}]*\}': 'Jonathan Smith',
    r'\{[^}]*full_name[^}]*\}': 'John A. Smith',
    
    # Grade related
    r'\{[^}]*grade_display[^}]*\}': '85',
    r'\{[^}]*grade[^}]*\}': '85',
    r'\{[^}]*score[^}]*\}': '92',
    r'\{[^}]*confidence[^}]*\}': '0.92',
    r'\{[^}]*points[^}]*\}': '10',
    r'\{[^}]*max_points[^}]*\}': '100',
    r'\{[^}]*conf_info[^}]*\}': ', confidence: 0.45',
    
    # Column related
    r'\{[^}]*column[^}]*\}': 'Quiz 3 Points',
    r'\{[^}]*col_name[^}]*\}': 'End-of-Line Indicator',
    r'\{[^}]*missing_columns[^}]*\}': 'Email',
    r'\{[^}]*cols_list[^}]*\}': 'Username, First Name, and Email',
    
    # Error/exception related
    r'\{str\(e\)\}': 'The file is being used by another process',
    r'\{e\}': 'Cannot access file - permission denied',
    r'\{[^}]*error[^}]*\}': 'Unable to read file',
    r'\{[^}]*exception[^}]*\}': 'File not found',
    r'\{[^}]*err[^}]*\}': 'Access denied',
    r'\{[^}]*message[^}]*\}': 'Check that all required files exist and are not open in another program',
    
    # Friendly message patterns (used for user-facing errors)
    r'\{friendly_msg\}': 'Please close the import file in Excel and try again',
    r'\{friendly_error\}': 'Could not complete the operation - check that files are closed',
    r'\{clean_msg\}': 'Student "John Smith" not found in roster',
    r'\{issue_msg\}': 'Low confidence score detected',
    r'\{[^}]*warning[^}]*\}': '   John Smith → Jonathan Smith (fuzzy match)',
    
    # Time/date related
    r'\{[^}]*time[^}]*\}': '2.5s',
    r'\{[^}]*date[^}]*\}': '2024-12-13',
    r'\{[^}]*timestamp[^}]*\}': '14:30:45',
    
    # Drive related
    r'\{[^}]*drive[^}]*\}': 'C:',
    
    # TypeScript specific patterns
    r'\{result\.error\}': 'Unable to read file',
    r'\{result\.killed[^}]*\}': '3',
    r'\{result\.classes\.length\}': '5',
    r'\{newClass\}': 'MATH 101 - Fall 2024',
    r'\{studentName\}': 'John Smith',
    r'\{zipFilename\}': 'Quiz3-submissions.zip',
    r'\{trimmed\}': 'Invalid file format - file must be CSV format',
    r'\{error[^}]*\}': 'Unable to read file',
    
    # Generic patterns (catch-all, applied last)
    r'\{[^}]+\}': '',
}

# Dynamic log examples - for logs built in loops that can't be captured statically
DYNAMIC_LOG_EXAMPLES = {
    'fuzzy_match_warning': {
        'description': 'When a student name is matched using fuzzy matching (not exact)',
        'example': '   John Smith → Jonathan Smith (fuzzy match)',
        'action': 'Extract Grades',
    },
    'low_confidence_student': {
        'description': 'When OCR confidence is below threshold for a grade',
        'example': '   ⚠️ Jane Doe: 87 (low confidence: 0.65 – needs verification)',
        'action': 'Extract Grades',
    },
    'skipped_student': {
        'description': 'When a student from PDF cannot be matched to import file roster',
        'example': '   Bob Wilson: 75, confidence: 0.45 - Could not match to roster',
        'action': 'Extract Grades',
    },
    'grade_with_confidence': {
        'description': 'Individual grade line with OCR confidence score',
        'example': '    1. John Smith: 95 ✅ (confidence: 0.92)',
        'action': 'Extract Grades',
    },
}

# UI Transformations - how raw logs appear in the actual UI (LogTerminal.tsx)
UI_TRANSFORMATIONS = {
    'Created combined PDF': {
        'pattern': r'Created combined PDF[:\s]*(\d+)\s*submissions',
        'raw_example': 'Created combined PDF: 26 submissions (sorted by last name)',
        'user_sees': '✅ Created 📄 Combined PDF — 26 submissions (click to open)',
        'has_link': True,
        'link_action': 'Opens the combined PDF in default PDF viewer',
        'action': 'Process Quizzes',
    },
    'Grade extraction complete': {
        'pattern': r'Grade extraction complete!',
        'raw_example': 'Grade extraction complete!',
        'user_sees': 'Grade extraction complete!\n📋 Open Import File (clickable link)',
        'has_link': True,
        'link_action': 'Opens Import File.csv in Excel',
        'action': 'Extract Grades',
    },
    'Completion processing completed': {
        'pattern': r'Completion processing completed!',
        'raw_example': 'Completion processing completed!',
        'user_sees': 'Completion processing completed!\n📋 Open Import File (clickable link)',
        'has_link': True,
        'link_action': 'Opens Import File.csv in Excel',
        'action': 'Process Completion',
    },
    'Extracted student name PDF': {
        'pattern': r"Extracted.*'s PDF|Split.*PDF",
        'raw_example': "Extracted John Smith's PDF",
        'user_sees': "📄 John Smith — PDF (clickable, opens individual PDF)",
        'has_link': True,
        'link_action': 'Opens the student\'s individual graded PDF',
        'action': 'Split PDF',
    },
}

# Scenario triggers - what causes each type of log
SCENARIO_TRIGGERS = {
    'Error - Missing Required Column': 'When the Import File.csv is missing one of the required columns (ID, Username, First Name, Last Name, Email)',
    'Error - Missing Email Column': 'When the Import File.csv does not have an Email column',
    'Error - Import File Not Found': 'When Import File.csv does not exist in the class folder',
    'Error - No ZIP File Found': 'When no .zip files are found in the Downloads folder',
    'Error - PDF Not Found': 'When the combined PDF file cannot be located',
    'Error - Folder Not Found': 'When the selected class folder does not exist',
    'Error - File Not Found': 'When a required file is missing',
    'Error - File Corrupted': 'When a ZIP or PDF file cannot be opened (corrupted or invalid format)',
    'Error - File Locked/In Use': 'When Excel or another program has the Import File open',
    'Error - Permission Denied': 'When the app does not have permission to read/write a file',
    'Error - Extraction Failed': 'When grade extraction from PDFs fails (OCR error or no grades found)',
    'Error - No Student Assignments': 'When the ZIP file contains no student submission folders',
    'Prompt - Multiple ZIP Files': 'When more than one ZIP file is found in Downloads - user must choose',
    'Prompt - Select Option': 'When the user needs to make a selection',
    'Prompt - User Action': 'When waiting for user input',
    'Success - Folders Extracted': 'When student submission folders are successfully extracted from ZIP',
    'Success - PDF Created': 'When student PDFs are combined into a single grading PDF',
    'Success - PDF Split': 'When the graded PDF is split back into individual student files',
    'Success - Grades Updated': 'When grades are written to the Import File.csv',
    'Success - File Saved': 'When a file is successfully saved',
    'Success - Process Completed': 'When an entire process finishes successfully',
    'Success - Data Loaded': 'When data is loaded from files',
    'Success - Data Cleared': 'When Grade Processing folder contents are deleted',
    'Warning - Adding End-of-Line Indicator': 'When the Import File is missing the End-of-Line Indicator column and it gets added',
    'Warning - Creating Backup': 'When an existing folder is renamed as a backup before new extraction',
    'Warning - Override Mode': 'When grade columns are being replaced instead of added',
    'Status - Searching': 'While looking for ZIP files in Downloads',
    'Status - Processing': 'While processing files',
    'Status - Extracting': 'While extracting files from ZIP',
    'Status - Loading': 'While loading data from files',
    'Status - Saving': 'While saving changes to files',
    'Status - Starting': 'When a process begins',
    'Status - Creating': 'When creating new files or folders',
    'Status - Renaming': 'When renaming files or folders',
    'Status - Backup': 'When creating a backup copy',
    'Status - Awaiting Input': 'When waiting for user commands',
    'Info - Confidence Score': 'Showing OCR confidence for extracted grades',
    'Info - ZIP File Selected': 'When a ZIP file is chosen for processing',
    'Info - Classes Found': 'When class folders are discovered on the drive',
}


def get_log_type(message: str) -> str:
    """Determine if log is success, error, info, or warning"""
    lower = message.lower()
    # Check for warning emoji first (most specific)
    if '⚠️' in message:
        return 'warning'
    # Check for error emoji or error keywords
    if '❌' in message or 'error' in lower or 'failed' in lower or 'not found' in lower:
        return 'error'
    # Check for success emoji or success keywords
    if '✅' in message or 'success' in lower or 'completed' in lower or 'created' in lower:
        return 'success'
    # Check for warning keywords (but no emoji)
    if 'warning' in lower:
        return 'warning'
    return 'info'


def is_debugging_log(pattern_type: str, message: str, filepath: str, code: str) -> bool:
    """
    Determine if a log is debugging/internal (not user-facing).
    
    Debugging logs are:
    - print() statements in most files (console only)
    - Module import warnings
    - Development/deployment issues
    - Internal error messages
    
    User-facing print() statements are in:
    - extract_grades_cli.py (outputs to stdout for frontend)
    - Other CLI scripts that output to terminal for user
    """
    message_lower = message.lower()
    code_lower = code.lower()
    filename = os.path.basename(filepath)
    
    # Files where print() IS user-facing (CLI scripts that output to terminal/frontend)
    USER_FACING_PRINT_FILES = [
        'extract_grades_cli.py',
        'process_quiz_cli.py', 
        'process_completion_cli.py',
        'split_pdf_cli.py',
        'cleanup_data_cli.py',
    ]
    
    # print() statements in CLI files are user-facing
    if pattern_type == 'print':
        # Check if file is a CLI script where print() goes to user
        if filename in USER_FACING_PRINT_FILES:
            # Still filter out module loading/debug prints
            if 'failed to load' in message_lower or 'module' in message_lower:
                return True
            if 'warning:' in message_lower and 'module' in message_lower:
                return True
            # User-facing print in CLI file
            return False
        
        # For other files, check if it's clearly user-facing
        if any(keyword in message_lower for keyword in [
            'extracted grades', 'confidence', 'processed', 'students',
            'please', 'select', 'choose', 'success', '📋', '📊', '🔬', '⚠️', '❌', '✅'
        ]):
            if 'failed to load' in message_lower or 'module' in message_lower:
                return True  # Module loading is debugging
            return False  # User-facing
        
        return True  # Most other print() statements are debugging
    
    # Module import/loading errors are debugging
    if 'failed to load' in message_lower and 'module' in message_lower:
        return True
    
    # Warnings about missing modules
    if 'warning:' in message_lower and ('module' in message_lower or 'import' in message_lower):
        return True
    
    # Internal development messages
    if any(phrase in message_lower for phrase in [
        'extracted_logs.json not found',
        'running extractor',
        'error reading',
    ]):
        return True
    
    # user_log is always user-facing
    if pattern_type == 'user_log':
        return False
    
    # dev_log is always debugging
    if pattern_type == 'dev_log':
        return True
    
    # log_callback, logs.append, addLog are always user-facing
    if pattern_type in ['log_callback', 'logs.append', 'addLog']:
        return False
    
    # console.print is usually user-facing (Rich library for terminal output)
    if pattern_type == 'console.print':
        return False
    
    return False


def replace_variables_with_examples(message: str) -> str:
    """Replace f-string variables with realistic example values"""
    result = message
    
    # First, handle TypeScript template literals ${...} -> convert to Python style {...}
    # This way our patterns will match both
    result = re.sub(r'\$\{([^}]+)\}', r'{\1}', result)
    
    # Apply replacements in order (specific patterns first)
    for pattern, example in EXAMPLE_VALUES.items():
        result = re.sub(pattern, example, result, flags=re.IGNORECASE)
    
    # Clean up any remaining brackets from Rich formatting
    result = re.sub(r'\[/?[a-z_]+\]', '', result)  # Remove [bold], [/bold], etc.
    
    # Clean up any remaining $ symbols that were left behind
    result = re.sub(r'\$\s*$', '', result)  # Remove trailing $
    result = re.sub(r'\$\s+', ' ', result)  # Replace $ followed by space with just space
    
    # Remove "Error:" prefix if message already has ❌ emoji
    if '❌' in result and re.match(r'^❌\s*Error:\s*', result, re.IGNORECASE):
        result = re.sub(r'^❌\s*Error:\s*', '❌ ', result, flags=re.IGNORECASE)
    
    # Ensure all error messages have ❌ emoji (if they're error type but missing emoji)
    # This is handled in get_log_type, but we can also add it here for safety
    if 'error' in result.lower() and '❌' not in result and not result.startswith('⚠️'):
        # Only add if it's clearly an error message
        if any(keyword in result.lower() for keyword in ['error', 'failed', 'not found', 'cannot', 'unable']):
            result = f"❌ {result.lstrip('Error: ').lstrip('error: ').strip()}"
    
    return result


def generate_scenario_label(log: Dict[str, Any]) -> str:
    """Generate a human-readable scenario label for a log entry."""
    message = log.get('raw_message', '')
    log_type = log.get('type', 'info')
    function = log.get('function', '')
    
    type_labels = {'error': 'Error', 'success': 'Success', 'warning': 'Warning', 'info': 'Info'}
    prefix = type_labels.get(log_type, 'Info')
    
    msg_lower = message.lower()
    
    # Error scenarios
    if log_type == 'error':
        if 'missing' in msg_lower and 'column' in msg_lower:
            return "Error - Missing Required Column"
        if 'missing' in msg_lower and 'email' in msg_lower:
            return "Error - Missing Email Column"
        if 'not found' in msg_lower:
            if 'import' in msg_lower or 'csv' in msg_lower:
                return "Error - Import File Not Found"
            if 'zip' in msg_lower:
                return "Error - No ZIP File Found"
            if 'pdf' in msg_lower:
                return "Error - PDF Not Found"
            if 'folder' in msg_lower or 'class' in msg_lower:
                return "Error - Folder Not Found"
            return "Error - File Not Found"
        if 'corrupted' in msg_lower or "can't be opened" in msg_lower:
            return "Error - File Corrupted"
        if 'locked' in msg_lower or ('open' in msg_lower and 'close' in msg_lower):
            return "Error - File Locked/In Use"
        if 'permission' in msg_lower:
            return "Error - Permission Denied"
        if 'extract' in msg_lower and 'failed' in msg_lower:
            return "Error - Extraction Failed"
        if 'student' in msg_lower and 'assignment' in msg_lower:
            return "Error - No Student Assignments"
        if 'multiple' in msg_lower and 'zip' in msg_lower:
            return "Prompt - Multiple ZIP Files"
        return f"Error - Generic"
    
    # Success scenarios
    if log_type == 'success':
        if 'extracted' in msg_lower and 'folder' in msg_lower:
            return "Success - Folders Extracted"
        if 'pdf' in msg_lower and 'created' in msg_lower:
            return "Success - PDF Created"
        if 'pdf' in msg_lower and 'split' in msg_lower:
            return "Success - PDF Split"
        if 'grade' in msg_lower:
            return "Success - Grades Updated"
        if 'saved' in msg_lower or 'updated' in msg_lower:
            return "Success - File Saved"
        if 'completed' in msg_lower:
            return "Success - Process Completed"
        if 'loaded' in msg_lower:
            return "Success - Data Loaded"
        if 'deleted' in msg_lower or 'cleared' in msg_lower:
            return "Success - Data Cleared"
        return "Success - Generic"
    
    # Warning scenarios
    if log_type == 'warning':
        if 'end' in msg_lower and 'line' in msg_lower:
            return "Warning - Adding End-of-Line Indicator"
        if 'backup' in msg_lower:
            return "Warning - Creating Backup"
        if 'override' in msg_lower:
            return "Warning - Override Mode"
        return "Warning - Generic"
    
    # Info scenarios
    if 'searching' in msg_lower or 'looking' in msg_lower:
        return "Status - Searching"
    if 'processing' in msg_lower:
        return "Status - Processing"
    if 'extracting' in msg_lower:
        return "Status - Extracting"
    if 'loading' in msg_lower:
        return "Status - Loading"
    if 'saving' in msg_lower:
        return "Status - Saving"
    if 'starting' in msg_lower:
        return "Status - Starting"
    if 'creating' in msg_lower:
        return "Status - Creating"
    if 'renaming' in msg_lower:
        return "Status - Renaming"
    if 'backup' in msg_lower:
        return "Status - Backup"
    if 'confidence' in msg_lower:
        return "Info - Confidence Score"
    if 'using' in msg_lower and 'zip' in msg_lower:
        return "Info - ZIP File Selected"
    if 'found' in msg_lower and 'class' in msg_lower:
        return "Info - Classes Found"
    if 'select' in msg_lower:
        return "Prompt - Select Option"
    if 'press' in msg_lower:
        return "Prompt - User Action"
    if 'awaiting' in msg_lower:
        return "Status - Awaiting Input"
    
    return "Info - General"


# File/function to action mapping
FILE_ACTION_MAP = {
    'process_quiz_cli.py': 'Process Quizzes',
    'process_completion_cli.py': 'Process Completion',
    'extract_grades_cli.py': 'Extract Grades',
    'split_pdf_cli.py': 'Split PDF',
    'cleanup_data_cli.py': 'Clear Data',
    'helper_cli.py': 'Helper',
}

FUNCTION_ACTION_MAP = {
    'run_grading_process': 'Process Quizzes',
    'run_completion_process': 'Process Completion',
    'create_combined_pdf_only': 'Process Quizzes',
    'run_reverse_process': 'Split PDF',
    'extract_zip_file': 'Process Quizzes',
    'load_import_file': 'Import File',
    'update_import_file': 'Import File',
    'validate_import_file_early': 'Import File Validation',
    'handleProcessQuizzes': 'Process Quizzes',
    'handleProcessCompletion': 'Process Completion',
    'handleExtractGrades': 'Extract Grades',
    'handleSplitPdf': 'Split PDF',
    'handleOpenFolder': 'Open Folder',
    'handleOpenDownloads': 'Open Downloads',
    'handleClearData': 'Clear Data',
    'handleRefresh': 'Load Classes',
    'handleZipSelection': 'Process Quizzes',
    'handleCompletionZipSelection': 'Process Completion',
    'list_classes': 'Load Classes',
    'open_folder': 'Open Folder',
}


def find_containing_function(lines: List[str], line_num: int) -> Optional[str]:
    """Find the function name that contains the given line number"""
    for i in range(line_num - 1, -1, -1):
        line = lines[i]
        match = re.match(r'\s*def\s+(\w+)\s*\(', line)
        if match:
            return match.group(1)
        match = re.match(r'\s*(?:const|function)\s+(\w+)\s*=?\s*(?:async\s*)?\(?', line)
        if match:
            return match.group(1)
        match = re.match(r'\s*(\w+)\s*=\s*async\s*\(', line)
        if match:
            return match.group(1)
    return None


def infer_action(filename: str, function_name: Optional[str], code: str) -> str:
    """Infer which UI action this log belongs to"""
    if function_name and function_name in FUNCTION_ACTION_MAP:
        return FUNCTION_ACTION_MAP[function_name]
    
    basename = os.path.basename(filename)
    if basename in FILE_ACTION_MAP:
        return FILE_ACTION_MAP[basename]
    
    code_lower = code.lower()
    if 'extract' in code_lower and 'grade' in code_lower:
        return 'Extract Grades'
    if 'split' in code_lower and 'pdf' in code_lower:
        return 'Split PDF'
    if 'completion' in code_lower:
        return 'Process Completion'
    if 'quiz' in code_lower:
        return 'Process Quizzes'
    if 'download' in code_lower:
        return 'Open Downloads'
    if 'folder' in code_lower:
        return 'Open Folder'
    if 'class' in code_lower:
        return 'Load Classes'
    if 'clear' in code_lower or 'delete' in code_lower:
        return 'Clear Data'
    
    if 'grading_processor' in filename:
        return 'Process Quizzes'
    if 'import_file' in filename:
        return 'Import File'
    if 'pdf_operations' in filename:
        return 'PDF Operations'
    if 'Option2' in filename:
        return 'Frontend'
    if 'LogTerminal' in filename:
        return 'Log Display'
    if 'server' in filename.lower():
        return 'Backend Server'
    
    return 'Other'


def extract_logs_from_python(filepath: str) -> List[Dict[str, Any]]:
    """Extract logging statements from a Python file"""
    logs = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return logs
    
    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith('#'):
            continue
        
        for pattern, pattern_type in PYTHON_PATTERNS:
            matches = re.finditer(pattern, line)
            for match in matches:
                message = match.group(1) if match.groups() else ''
                function_name = find_containing_function(lines, line_num)
                
                example_msg = replace_variables_with_examples(message)
                
                # Skip empty messages or Rich console styling patterns
                if not example_msg.strip() or example_msg.strip() in ['', '❌', '✅', '⚠️']:
                    continue
                if re.match(r'^\[/?[a-z_]+\].*\[/?[a-z_]+\]$', message):
                    continue
                
                # Determine if this is a debugging log
                is_debug = is_debugging_log(pattern_type, message, filepath, line)
                
                log_entry = {
                    'file': os.path.basename(filepath),
                    'filepath': filepath,
                    'line': line_num,
                    'code': line.strip(),
                    'raw_message': message,
                    'example_message': example_msg,
                    'pattern_type': pattern_type,
                    'function': function_name,
                    'action': infer_action(filepath, function_name, line),
                    'type': get_log_type(message),
                    'category': 'debugging' if is_debug else 'user-facing',
                }
                log_entry['scenario'] = generate_scenario_label(log_entry)
                log_entry['trigger'] = SCENARIO_TRIGGERS.get(log_entry['scenario'], '')
                logs.append(log_entry)
    
    return logs


def extract_logs_from_typescript(filepath: str) -> List[Dict[str, Any]]:
    """Extract logging statements from a TypeScript/JavaScript file"""
    logs = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return logs
    
    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith('//') or stripped.startswith('/*'):
            continue
        
        for pattern, pattern_type in TYPESCRIPT_PATTERNS:
            matches = re.finditer(pattern, line)
            for match in matches:
                message = match.group(1) if match.groups() else ''
                function_name = find_containing_function(lines, line_num)
                
                example_msg = replace_variables_with_examples(message)
                
                # Skip empty messages or Rich console styling patterns
                if not example_msg.strip() or example_msg.strip() in ['', '❌', '✅', '⚠️']:
                    continue
                if re.match(r'^\[/?[a-z_]+\].*\[/?[a-z_]+\]$', message):
                    continue
                
                # TypeScript addLog is always user-facing
                is_debug = is_debugging_log(pattern_type, message, filepath, line)
                
                log_entry = {
                    'file': os.path.basename(filepath),
                    'filepath': filepath,
                    'line': line_num,
                    'code': line.strip(),
                    'raw_message': message,
                    'example_message': example_msg,
                    'pattern_type': pattern_type,
                    'function': function_name,
                    'action': infer_action(filepath, function_name, line),
                    'type': get_log_type(message),
                    'category': 'debugging' if is_debug else 'user-facing',
                }
                log_entry['scenario'] = generate_scenario_label(log_entry)
                log_entry['trigger'] = SCENARIO_TRIGGERS.get(log_entry['scenario'], '')
                logs.append(log_entry)
    
    return logs


def scan_directory(base_path: str) -> List[Dict[str, Any]]:
    """Scan directory for all Python and TypeScript files"""
    all_logs = []
    
    python_extensions = ['.py']
    typescript_extensions = ['.tsx', '.ts', '.js']
    skip_dirs = ['node_modules', '__pycache__', 'build', 'dist', '.git', 'venv', 'dist-frontend']
    
    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            filepath = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            
            if 'test' in file.lower() and 'conftest' not in file.lower():
                continue
            if file == 'log_extractor.py':
                continue
            
            if ext in python_extensions:
                logs = extract_logs_from_python(filepath)
                all_logs.extend(logs)
            elif ext in typescript_extensions:
                logs = extract_logs_from_typescript(filepath)
                all_logs.extend(logs)
    
    return all_logs


def organize_by_action(logs: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Organize logs by UI action"""
    organized = {}
    for log in logs:
        action = log['action']
        if action not in organized:
            organized[action] = []
        organized[action].append(log)
    
    for action in organized:
        organized[action].sort(key=lambda x: (x['scenario'], x['file'], x['line']))
    
    return organized


def main():
    """Main extraction function"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("=" * 60)
    print("LOG EXTRACTOR")
    print("Scanning source files for logging statements...")
    print("=" * 60)
    print()
    
    all_logs = scan_directory(script_dir)
    
    # Separate user-facing and debugging logs
    user_facing_logs = [log for log in all_logs if log.get('category', 'user-facing') == 'user-facing']
    debugging_logs = [log for log in all_logs if log.get('category') == 'debugging']
    
    print(f"Found {len(all_logs)} logging statements")
    print(f"  - User-facing: {len(user_facing_logs)}")
    print(f"  - Debugging: {len(debugging_logs)}")
    print()
    
    # Organize separately
    user_organized = organize_by_action(user_facing_logs)
    debug_organized = organize_by_action(debugging_logs)
    
    print("User-facing logs by action:")
    for action, logs in sorted(user_organized.items()):
        print(f"  {action}: {len(logs)} logs")
    print()
    
    if debug_organized:
        print("Debugging logs by action:")
        for action, logs in sorted(debug_organized.items()):
            print(f"  {action}: {len(logs)} logs")
        print()
    
    output_path = os.path.join(script_dir, 'extracted_logs.json')
    output_data = {
        'total_logs': len(all_logs),
        'user_facing_logs': len(user_facing_logs),
        'debugging_logs': len(debugging_logs),
        'actions': sorted(list(user_organized.keys())),
        'debugging_actions': sorted(list(debug_organized.keys())),
        'logs': all_logs,
        'logs_by_action': user_organized,
        'debugging_logs_by_action': debug_organized,
        'dynamic_log_examples': DYNAMIC_LOG_EXAMPLES,
        'ui_transformations': UI_TRANSFORMATIONS,
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"Saved to: {output_path}")
    
    return output_data


if __name__ == "__main__":
    main()
