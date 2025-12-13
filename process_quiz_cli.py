#!/usr/bin/env python3
"""
CLI script for quiz processing - called by the Node.js backend
Usage: python process_quiz_cli.py <drive> <className>
"""

import sys
import os
import json
from config_reader import get_downloads_path

# Rich imports for beautiful terminal output
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from rich.style import Style
from rich.theme import Theme

# Custom theme for consistent styling
custom_theme = Theme({
    "info": "cyan",
    "success": "bold green",
    "warning": "bold yellow", 
    "error": "bold red",
    "header": "bold magenta",
    "highlight": "bold white on blue",
})

console = Console(theme=custom_theme)

def main():
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print(json.dumps({
            "success": False,
            "error": "Usage: python process_quiz_cli.py <drive> <className> [zipPath]"
        }))
        sys.exit(1)
    
    drive = sys.argv[1]
    class_name = sys.argv[2]
    specific_zip = sys.argv[3] if len(sys.argv) == 4 else None
    
    try:
        logs = []
        
        logs.append("")
        logs.append("=" * 60)
        logs.append(f"QUIZ PROCESSING STARTED")
        logs.append(f"Class: {class_name}")
        logs.append("=" * 60)
        logs.append("")
        
        # Check for multiple ZIPs FIRST before any console output
        # This ensures clean JSON response for ZIP selection
        if not specific_zip:
            import glob
            downloads_path = get_downloads_path()
            zip_files = glob.glob(os.path.join(downloads_path, "*.zip"))
            
            if not zip_files:
                # No ZIP files - return JSON error
                response = {
                    "success": False,
                    "error": "No ZIP files found in Downloads folder",
                    "logs": logs + ["No quiz files found in Downloads folder"]
                }
                print(json.dumps(response))
                return
            
            # If multiple ZIP files, return for user selection (clean JSON only, no Rich output)
            if len(zip_files) > 1:
                # Don't add ZIP file list to logs - just return JSON for modal
                # Return list of ZIP files for frontend to handle
                response = {
                    "success": False,
                    "error": "Multiple ZIP files found",
                    "message": "Please select which ZIP file to process",
                    "zip_files": [{"index": i+1, "filename": os.path.basename(zip_file), "path": zip_file} for i, zip_file in enumerate(zip_files)],
                    "logs": logs  # Only include logs up to this point (no file list)
                }
                # Output ONLY JSON to stdout (no Rich formatting that would corrupt JSON parsing)
                print(json.dumps(response, ensure_ascii=False))
                return
            
            # Only one ZIP file - continue with processing
            selected_zip = zip_files[0]
        else:
            selected_zip = specific_zip
        
        # Now we can use Rich console output since we're not returning early with JSON
        console.print()
        console.print(Panel.fit(
            f"[bold white]QUIZ PROCESSING[/bold white]\n[cyan]{class_name}[/cyan]",
            border_style="bright_blue",
            box=box.DOUBLE
        ))
        console.print()
        
        # Validate ZIP file exists
        if not os.path.exists(selected_zip):
            console.print("[error]✗ ZIP file not found[/error]")
            response = {
                "success": False,
                "error": f"Specified ZIP file not found: {selected_zip}",
                "logs": logs + [f"Specified ZIP file not found: {selected_zip}"]
            }
            print(json.dumps(response))
            return
        
        console.print(f"[success]✓[/success] Using: [cyan]{os.path.basename(selected_zip)}[/cyan]")
        logs.append("")
        logs.append(f"Using ZIP file: {os.path.basename(selected_zip)}")
        
        # Import and run the actual grading processor
        from grading_processor import run_grading_process, format_error_message
        
        # Run the real processing with progress indicator
        console.print()
        console.print(Panel(
            "[bold]Processing Quiz Submissions[/bold]",
            border_style="cyan",
            box=box.ROUNDED
        ))
        
        logs.append("")
        logs.append("-" * 40)
        logs.append("STARTING QUIZ PROCESSING")
        logs.append("-" * 40)
        
        def log_callback(message):
            logs.append(message)
            # Also print to console with styling
            if message:
                if "error" in message.lower() or "❌" in message:
                    console.print(f"[error]{message}[/error]")
                elif "✅" in message or "success" in message.lower() or "completed" in message.lower():
                    console.print(f"[success]{message}[/success]")
                elif "⚠" in message or "warning" in message.lower():
                    console.print(f"[warning]{message}[/warning]")
                elif message.startswith("-") or message.startswith("="):
                    console.print(f"[dim]{message}[/dim]")
                else:
                    console.print(message)
        
        result = None
        try:
            result = run_grading_process(drive, class_name, selected_zip, log_callback)
            logs.append("")
            logs.append("Processing completed successfully!")
        except Exception as e:
            logs.append("")
            logs.append(format_error_message(e))
            raise
        
        # Note: PDF is opened automatically by grading_processor.py
        
        logs.append("")
        logs.append("=" * 60)
        logs.append("QUIZ PROCESSING COMPLETED")
        logs.append("=" * 60)
        
        # Display success panel
        console.print()
        console.print(Panel.fit(
            "[bold green]✓ QUIZ PROCESSING COMPLETE[/bold green]\n"
            "[white]PDF has been created and opened for grading[/white]",
            border_style="green",
            box=box.DOUBLE
        ))
        console.print()
        
        # Return JSON for the backend (but don't print it)
        response = {
            "success": True,
            "message": "Quiz processing completed",
            "logs": logs
        }
        
        # Only print JSON to stderr so it doesn't interfere with clean output
        print(json.dumps(response), file=sys.stderr)
        
    except Exception as e:
        # Check for specific error types and show friendly messages
        error_msg = str(e)
        if "does not contain student assignments" in error_msg:
            friendly_error = "Zip file does not contain student assignments"
        elif "can't be opened" in error_msg or "This file can't be opened" in error_msg:
            friendly_error = "This file can't be opened"
        elif "wrong file" in error_msg.lower() or "wrong class" in error_msg.lower() or "Oops" in error_msg:
            friendly_error = "Zip file does not contain student assignments"
        else:
            friendly_error = error_msg
        logs.append("")
        logs.append(friendly_error)
        
        # Display error panel
        console.print()
        console.print(Panel.fit(
            f"[bold red]✗ ERROR[/bold red]\n[white]{friendly_error}[/white]",
            border_style="red",
            box=box.DOUBLE
        ))
        console.print()
        
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
