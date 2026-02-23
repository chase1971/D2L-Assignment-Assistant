#!/usr/bin/env python3
"""
CLI script for quiz processing - called by the Node.js backend
Usage: python process_quiz_cli.py <drive> <className> [zipPath]
"""

import sys
import os

# Add python-modules to path for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_MODULES_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'python-modules')
sys.path.insert(0, PYTHON_MODULES_DIR)

import json
from config_reader import get_downloads_path
from grading_processor import find_zip_file, run_grading_process
from grading_helpers import format_error_message
from user_messages import log, log_raw


def main():
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print(json.dumps({
            "success": False,
            "error": "Usage: python process_quiz_cli.py <drive> <className> [zipPath]"
        }), file=sys.stderr)
        sys.exit(1)
    
    drive = sys.argv[1]
    class_name = sys.argv[2]
    specific_zip = sys.argv[3] if len(sys.argv) == 4 else None
    
    try:
        # Check for ZIP files
        downloads_path = get_downloads_path()
        selected_zip, error_response = find_zip_file(downloads_path, specific_zip, [])
        
        if error_response:
            # Don't log anything - the error_response contains zip_files for selection modal
            # or an error message that will be displayed by the frontend
            print(json.dumps(error_response, ensure_ascii=False))
            return
        
        # Validate ZIP file exists
        if not os.path.exists(selected_zip):
            log("ERR_FILE_NOT_FOUND", file=os.path.basename(selected_zip))
            response = {
                "success": False,
                "error": f"ZIP file not found: {selected_zip}"
            }
            print(json.dumps(response))
            return
        
        log("QUIZ_USING", filename=os.path.basename(selected_zip))
        
        # Run the actual processing
        result = run_grading_process(drive, class_name, selected_zip)
        
        log("QUIZ_SUCCESS")
        
        # Return JSON for the backend
        response = {
            "success": True,
            "message": "Quiz processing completed",
            "combined_pdf_path": result.combined_pdf_path if result and hasattr(result, 'combined_pdf_path') else None,
            "assignment_name": result.assignment_name if result and hasattr(result, 'assignment_name') else None,
            "no_submission": result.no_submission if result and hasattr(result, 'no_submission') else []
        }
        print(json.dumps(response))
        
    except Exception as e:
        friendly_error = format_error_message(e)
        log("ERR_GENERIC", error=friendly_error)
        
        # Don't include error in JSON - it's already logged above
        # The server will show the log message to the user
        error_response = {
            "success": False
        }
        print(json.dumps(error_response))
        sys.exit(1)


if __name__ == "__main__":
    main()
