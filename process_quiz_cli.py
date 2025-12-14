#!/usr/bin/env python3
"""
CLI script for quiz processing - called by the Node.js backend
Usage: python process_quiz_cli.py <drive> <className>
"""

import sys
import os
import json
from config_reader import get_downloads_path
from grading_processor import format_error_message

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
        
        # Check for ZIP files using shared function
        from grading_processor import find_zip_file
        downloads_path = get_downloads_path()
        selected_zip, error_response = find_zip_file(downloads_path, specific_zip, logs)
        
        if error_response:
            # No ZIP files or multiple ZIP files - return JSON response
            print(json.dumps(error_response, ensure_ascii=False))
            return
        
        # selected_zip is guaranteed to be set here
        
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
        
        # Display error panel
        console.print()
        console.print(Panel.fit(
            f"[bold red]✗ ERROR[/bold red]\n[white]{friendly_error}[/white]",
            border_style="red",
            box=box.DOUBLE
        ))
        console.print()
        
        # Print all logs to stdout so user can see full context
        print("=" * 60)
        print("QUIZ PROCESSING FAILED - FULL LOG")
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
