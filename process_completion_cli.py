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
        logs = []
        logs.append("")
        logs.append("=" * 60)
        logs.append(f"COMPLETION PROCESSING STARTED")
        logs.append(f"Class: {class_name}")
        logs.append("=" * 60)
        logs.append("")
        
        # Find ZIP file using shared function
        from grading_processor import find_zip_file
        downloads_path = get_downloads_path()
        
        if specific_zip:
            logs.append("")
            logs.append(f"Using specified ZIP file: {os.path.basename(specific_zip)}")
        else:
            logs.append(f"Looking for ZIP files in Downloads folder...")
        
        selected_zip, error_response = find_zip_file(downloads_path, specific_zip, logs)
        
        if error_response:
            # No ZIP files or multiple ZIP files - return JSON response
            print(json.dumps(error_response, ensure_ascii=False))
            return
        
        # selected_zip is guaranteed to be set here
        if not specific_zip:
            logs.append("")
            logs.append(f"Found 1 ZIP file: {os.path.basename(selected_zip)}")
            logs.append("")
            logs.append(f"Selected ZIP file: {os.path.basename(selected_zip)}")
        
        # Import and run the completion processor
        from grading_processor import run_completion_process, format_error_message
        
        # Run the processing
        logs.append("")
        logs.append("-" * 40)
        logs.append("STARTING COMPLETION PROCESSING")
        logs.append("(Auto-assigning 10 points to all submissions)")
        if dont_override:
            logs.append("Mode: Don't override (adding new column after column E)")
        else:
            logs.append("Mode: Override column E (existing behavior)")
        logs.append("-" * 40)
        
        def log_callback(message):
            logs.append(message)
        
        result = None
        try:
            result = run_completion_process(drive, class_name, selected_zip, log_callback, dont_override=dont_override)
            logs.append("")
            logs.append("Completion processing completed successfully!")
        except Exception as e:
            logs.append("")
            logs.append(format_error_message(e))
            raise
        
        # Open the processed PDF and Import File automatically (only if processing was successful)
        if result and hasattr(result, 'combined_pdf_path') and result.combined_pdf_path:
            if os.path.exists(result.combined_pdf_path):
                try:
                    open_file_with_default_app(result.combined_pdf_path)
                    logs.append("")
                    logs.append(f"Opened PDF file: {os.path.basename(result.combined_pdf_path)}")
                except Exception as e:
                    logs.append("")
                    logs.append(f"Could not open PDF: {str(e)}")
        
        # Open the Import File automatically (only if processing was successful)
        if result and hasattr(result, 'import_file_path') and result.import_file_path:
            if os.path.exists(result.import_file_path):
                try:
                    open_file_with_default_app(result.import_file_path)
                except Exception:
                    # Silently fail - not critical
                    pass
        
        logs.append("")
        logs.append("=" * 60)
        logs.append("COMPLETION PROCESSING COMPLETED")
        logs.append("=" * 60)
        
        # Output clean, human-readable logs
        print("\n" + "=" * 60)
        print("COMPLETION PROCESSING COMPLETED")
        print("=" * 60)
        print()
        
        for log in logs:
            print(log)
        
        print()
        print("=" * 60)
        print("PROCESSING FINISHED")
        print("=" * 60)
        
        # Return JSON for the backend (but don't print it)
        response = {
            "success": True,
            "message": "Completion processing completed",
            "logs": logs,
            "combined_pdf_path": result.combined_pdf_path if result and hasattr(result, 'combined_pdf_path') else None,
            "assignment_name": result.assignment_name if result and hasattr(result, 'assignment_name') else None
        }
        
        # Only print JSON to stderr so it doesn't interfere with clean output
        print(json.dumps(response), file=sys.stderr)
        
    except Exception as e:
        # Use standardized error formatting
        friendly_error = format_error_message(e)
        logs.append("")
        logs.append(friendly_error)
        
        # Print logs to stdout so user can see them in log terminal
        print("\n" + "=" * 60)
        print("COMPLETION PROCESSING FAILED")
        print("=" * 60)
        print()
        
        for log in logs:
            print(log)
        
        print()
        print("=" * 60)
        print("PROCESSING FAILED")
        print("=" * 60)
        
        # Return JSON for the backend
        error_response = {
            "success": False,
            "error": friendly_error,
            "logs": logs
        }
        # Only print JSON to stderr so it doesn't interfere with clean output
        print(json.dumps(error_response), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

