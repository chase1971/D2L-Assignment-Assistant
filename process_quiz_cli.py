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
        
        # Display header panel
        console.print()
        console.print(Panel.fit(
            f"[bold white]QUIZ PROCESSING[/bold white]\n[cyan]{class_name}[/cyan]",
            border_style="bright_blue",
            box=box.DOUBLE
        ))
        console.print()
        
        logs.append("")
        logs.append("=" * 60)
        logs.append(f"QUIZ PROCESSING STARTED")
        logs.append(f"Class: {class_name}")
        logs.append("=" * 60)
        logs.append("")
        # If specific ZIP file provided, use it directly
        if specific_zip:
            if not os.path.exists(specific_zip):
                console.print("[error]✗ ZIP file not found[/error]")
                response = {
                    "success": False,
                    "error": f"Specified ZIP file not found: {specific_zip}",
                    "logs": logs + [f"Specified ZIP file not found: {specific_zip}"]
                }
                print(json.dumps(response))
                return
            
            selected_zip = specific_zip
            console.print(f"[success]✓[/success] Using: [cyan]{os.path.basename(selected_zip)}[/cyan]")
            logs.append("")
            logs.append(f"Using specified ZIP file: {os.path.basename(selected_zip)}")
        else:
            console.print("[info]🔍 Searching Downloads folder...[/info]")
            logs.append(f"Looking for quiz files in Downloads folder...")
            
            # Get configured Downloads path
            downloads_path = get_downloads_path()
            
            # Look for ANY ZIP files
            import glob
            zip_files = glob.glob(os.path.join(downloads_path, "*.zip"))
            
            if not zip_files:
                console.print("[error]✗ No ZIP files found[/error]")
                response = {
                    "success": False,
                    "error": "No ZIP files found in Downloads folder",
                    "logs": logs + ["No quiz files found in Downloads folder"]
                }
                print(json.dumps(response))
                return
            
            # If multiple ZIP files, display table and return for user selection
            if len(zip_files) > 1:
                console.print(f"[warning]⚠ Found {len(zip_files)} ZIP files[/warning]")
                console.print()
                
                # Create a nice table of files
                table = Table(
                    title="Available ZIP Files",
                    box=box.ROUNDED,
                    header_style="bold cyan",
                    border_style="bright_blue"
                )
                table.add_column("#", style="dim", width=4)
                table.add_column("Filename", style="white")
                
                logs.append("")
                logs.append(f"Found {len(zip_files)} quiz files:")
                logs.append("")
                for i, zip_file in enumerate(zip_files):
                    table.add_row(str(i+1), os.path.basename(zip_file))
                    logs.append(f"  {i+1}. {os.path.basename(zip_file)}")
                
                console.print(table)
                console.print()
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
            console.print(f"[success]✓[/success] Found: [cyan]{os.path.basename(selected_zip)}[/cyan]")
            logs.append("")
            logs.append(f"Found 1 quiz file: {os.path.basename(selected_zip)}")
            logs.append("")
            logs.append(f"Selected quiz file: {os.path.basename(selected_zip)}")
        
        # Import and run the actual grading processor
        from grading_processor import run_grading_process
        
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
            logs.append(f"Processing failed: {str(e)}")
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
