#!/usr/bin/env python3
"""
CLI script for completion processing - called by the Node.js backend
Usage: python process_completion_cli.py <drive> <className> [zipPath] [--dont-override]
Auto-assigns 10 points to all submissions (no OCR needed)
"""

import sys
import os
import json
import argparse
from config_reader import get_downloads_path
from file_utils import open_file_with_default_app
from user_messages import log

def main():
    # Parse arguments - support both positional and named arguments
    # Format: python script.py <drive> <class_name> [zip_path] [--dont-override]
    parser = argparse.ArgumentParser(description='Process completion assignments')
    parser.add_argument('drive', help='Drive letter')
    parser.add_argument('class_name', help='Class name')
    parser.add_argument('zip_path', nargs='?', default=None, help='Optional specific ZIP file path')
    parser.add_argument('--dont-override', action='store_true', help="Don't override column E, add new column instead")
    
    args = parser.parse_args()
    
    drive = args.drive
    class_name = args.class_name
    specific_zip = args.zip_path
    dont_override = args.dont_override
    
    try:
        log("EMPTY_LINE")
        log("DOUBLE_SEPARATOR_LINE")
        log("COMPLETION_HEADER_START")
        log("COMPLETION_CLASS", class_name=class_name)
        log("DOUBLE_SEPARATOR_LINE")
        log("EMPTY_LINE")
        
        # Find ZIP file using shared function
        from grading_processor import find_zip_file
        downloads_path = get_downloads_path()
        
        if specific_zip:
            log("EMPTY_LINE")
            log("COMPLETION_USING_ZIP", filename=os.path.basename(specific_zip))
        else:
            log("COMPLETION_LOOKING_FOR_ZIP")
        
        # find_zip_file will log errors directly now
        selected_zip, error_response = find_zip_file(downloads_path, specific_zip, [])
        
        if error_response:
            # No ZIP files or multiple ZIP files - return JSON response
            print(json.dumps(error_response, ensure_ascii=False))
            return
        
        # selected_zip is guaranteed to be set here
        if not specific_zip:
            log("EMPTY_LINE")
            log("COMPLETION_FOUND_ONE_ZIP", filename=os.path.basename(selected_zip))
            log("EMPTY_LINE")
            log("COMPLETION_SELECTED_ZIP", filename=os.path.basename(selected_zip))
        
        # Import and run the completion processor
        from grading_processor import run_completion_process, format_error_message
        
        # Run the processing
        log("EMPTY_LINE")
        log("SEPARATOR_LINE")
        log("COMPLETION_PROCESSING_HEADER")
        log("COMPLETION_AUTO_ASSIGN")
        if dont_override:
            log("COMPLETION_MODE_DONT_OVERRIDE")
        else:
            log("COMPLETION_MODE_OVERRIDE")
        log("SEPARATOR_LINE")
        
        result = None
        try:
            result = run_completion_process(drive, class_name, selected_zip, dont_override=dont_override)
            log("EMPTY_LINE")
            log("COMPLETION_SUCCESS")
        except Exception as e:
            log("EMPTY_LINE")
            log("ERR_UNEXPECTED", error=format_error_message(e))
            raise
        
        # Open the processed PDF and Import File automatically (only if processing was successful)
        if result and hasattr(result, 'combined_pdf_path') and result.combined_pdf_path:
            if os.path.exists(result.combined_pdf_path):
                try:
                    open_file_with_default_app(result.combined_pdf_path)
                    log("EMPTY_LINE")
                    log("COMPLETION_OPENED_PDF", filename=os.path.basename(result.combined_pdf_path))
                except Exception as e:
                    log("EMPTY_LINE")
                    log("COMPLETION_COULD_NOT_OPEN_PDF", error=str(e))
        
        # Open the Import File automatically (only if processing was successful)
        if result and hasattr(result, 'import_file_path') and result.import_file_path:
            if os.path.exists(result.import_file_path):
                try:
                    open_file_with_default_app(result.import_file_path)
                except Exception:
                    # Silently fail - not critical
                    pass
        
        log("EMPTY_LINE")
        log("DOUBLE_SEPARATOR_LINE")
        log("COMPLETION_HEADER_COMPLETE")
        log("DOUBLE_SEPARATOR_LINE")
        
        # Return JSON for the backend
        response = {
            "success": True,
            "message": "Completion processing completed",
            "combined_pdf_path": result.combined_pdf_path if result and hasattr(result, 'combined_pdf_path') else None,
            "assignment_name": result.assignment_name if result and hasattr(result, 'assignment_name') else None
        }
        
        print(json.dumps(response))
        
    except Exception as e:
        # Use standardized error formatting
        from grading_processor import format_error_message
        friendly_error = format_error_message(e)
        log("EMPTY_LINE")
        log("ERR_UNEXPECTED", error=friendly_error)
        
        log("EMPTY_LINE")
        log("DOUBLE_SEPARATOR_LINE")
        log("COMPLETION_FAILED_HEADER")
        log("DOUBLE_SEPARATOR_LINE")
        
        # Return JSON for the backend
        error_response = {
            "success": False,
            "error": friendly_error
        }
        print(json.dumps(error_response))
        sys.exit(1)

if __name__ == "__main__":
    main()

