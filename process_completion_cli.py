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
        
        # If specific ZIP file provided, use it directly
        if specific_zip:
            if not os.path.exists(specific_zip):
                response = {
                    "success": False,
                    "error": f"Specified ZIP file not found: {specific_zip}",
                    "logs": logs + [f"Specified ZIP file not found: {specific_zip}"]
                }
                print(json.dumps(response))
                return
            
            selected_zip = specific_zip
            logs.append("")
            logs.append(f"Using specified ZIP file: {os.path.basename(selected_zip)}")
        else:
            logs.append(f"Looking for ZIP files in Downloads folder...")
            
            # Get configured Downloads path
            downloads_path = get_downloads_path()
            
            # Look for ANY ZIP files
            import glob
            zip_files = glob.glob(os.path.join(downloads_path, "*.zip"))
            
            if not zip_files:
                response = {
                    "success": False,
                    "error": "No ZIP files found in Downloads folder",
                    "logs": logs + ["No ZIP files found in Downloads folder"]
                }
                print(json.dumps(response))
                return
            
            # If multiple ZIP files, return list for user selection
            if len(zip_files) > 1:
                logs.append("")
                logs.append(f"Found {len(zip_files)} ZIP files:")
                logs.append("")
                for i, zip_file in enumerate(zip_files):
                    logs.append(f"  {i+1}. {os.path.basename(zip_file)}")
                logs.append("")
                logs.append("Multiple ZIP files found - user selection required")
                
                # Return list of ZIP files for frontend to handle
                response = {
                    "success": False,
                    "error": "Multiple ZIP files found",
                    "message": "Please select which ZIP file to process",
                    "zip_files": [{"index": i+1, "filename": os.path.basename(zip_file), "path": zip_file} for i, zip_file in enumerate(zip_files)],
                    "logs": logs
                }
                # Output JSON to stdout for backend to parse
                print(json.dumps(response, ensure_ascii=False))
                return
            
            # If only one ZIP file, use it automatically
            selected_zip = zip_files[0]
            logs.append("")
            logs.append(f"Found 1 ZIP file: {os.path.basename(selected_zip)}")
            logs.append("")
            logs.append(f"Selected ZIP file: {os.path.basename(selected_zip)}")
        
        # Import and run the completion processor
        from grading_processor import run_completion_process
        
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
            logs.append(f"Processing failed: {str(e)}")
            raise
        
        # Open the processed PDF and Import File automatically (only if processing was successful)
        if result and hasattr(result, 'combined_pdf_path') and result.combined_pdf_path:
            if os.path.exists(result.combined_pdf_path):
                try:
                    import subprocess
                    import platform
                    
                    # Open PDF with default system application
                    if platform.system() == "Windows":
                        os.startfile(result.combined_pdf_path)
                    elif platform.system() == "Darwin":  # macOS
                        subprocess.run(["open", result.combined_pdf_path])
                    else:  # Linux
                        subprocess.run(["xdg-open", result.combined_pdf_path])
                    
                    logs.append("")
                    logs.append(f"Opened PDF file: {os.path.basename(result.combined_pdf_path)}")
                except Exception as e:
                    logs.append("")
                    logs.append(f"Could not open PDF: {str(e)}")
        
        # Open the Import File automatically (only if processing was successful)
        if result and hasattr(result, 'import_file_path') and result.import_file_path:
            if os.path.exists(result.import_file_path):
                try:
                    import subprocess
                    import platform
                    
                    # Open Import File with default system application
                    if platform.system() == "Windows":
                        os.startfile(result.import_file_path)
                    elif platform.system() == "Darwin":  # macOS
                        subprocess.run(["open", result.import_file_path])
                    else:  # Linux
                        subprocess.run(["xdg-open", result.import_file_path])
                except Exception as e:
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
            "logs": logs
        }
        
        # Only print JSON to stderr so it doesn't interfere with clean output
        print(json.dumps(response), file=sys.stderr)
        
    except Exception as e:
        # Check if it's a wrong class/file error - show friendly message
        error_msg = str(e)
        if "wrong file" in error_msg.lower() or "wrong class" in error_msg.lower() or "Oops" in error_msg:
            friendly_error = "Oops. You've chosen the wrong file or class. Try again."
            logs.append("")
            logs.append(friendly_error)
        else:
            friendly_error = error_msg
            logs.append("")
            logs.append(f"Error: {error_msg}")
        
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

