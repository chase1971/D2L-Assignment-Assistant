#!/usr/bin/env python3
"""
CLI script for splitting combined PDF back into individual student PDFs and rezipping
Usage: python split_pdf_cli.py <drive> <className>
"""

import sys
import os
import json
import zipfile
import shutil
import re
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box
from grading_processor import run_reverse_process, format_error_message
from config_reader import get_downloads_path, get_rosters_path
from user_messages import log

# Initialize Rich console for clean output
console = Console()

class LogFormatter:
    """Handles formatting and grouping of log messages for clean output"""
    
    def __init__(self):
        self.suppress_verbose = True  # Suppress detailed technical logs
        self.student_processing = []  # Buffer for student processing messages
        self.file_additions = []  # Buffer for file additions
        self.current_section = None
    
    def should_suppress(self, message):
        """Check if message should be suppressed (verbose technical details)"""
        message_lower = message.lower()
        suppress_patterns = [
            'page', 'extracted text', 'found name from watermark',
            'combined pdf has', 'extracting student names',
            'first 10 names found', '... and', 'drive:', 'class:',
            'processing folder:', '----', 'loaded import file',
            'found combined pdf', 'found folder:', 'replacing:'
        ]
        return any(pattern in message_lower for pattern in suppress_patterns)
    
    def format_message(self, message):
        """Format a single message for Rich output"""
        cleaned = message
        plain_text = message
        
        # Map emojis to clean text
        emoji_map = {
            '🔄': '',
            '📄': '',
            '📦': '',
            '✅': '',
            '❌': '',
            '⚠️': '',
            '📝': '',
            '📋': '',
        }
        
        for emoji, replacement in emoji_map.items():
            cleaned = cleaned.replace(emoji, replacement)
            plain_text = plain_text.replace(emoji, replacement)
        
        message_lower = cleaned.lower().strip()
        
        # Suppress verbose technical details
        if self.should_suppress(cleaned) and self.suppress_verbose:
            return None, plain_text  # Return None to suppress display
        
        # Format based on content
        if 'successfully' in message_lower or 'completed' in message_lower:
            return f"[bold green]✓[/bold green] {cleaned.strip()}", plain_text
        elif 'error' in message_lower or 'failed' in message_lower:
            return f"[bold red]✗[/bold red] {cleaned.strip()}", plain_text
        elif 'warning' in message_lower or 'could not' in message_lower:
            return f"[bold yellow]⚠[/bold yellow] {cleaned.strip()}", plain_text
        elif 'found original zip' in message_lower or 'creating new zip' in message_lower:
            # Show ZIP operations
            return f"[dim]{cleaned.strip()}[/dim]", plain_text
        elif cleaned.strip().startswith('Processing '):
            # Clean up processing messages - show student name only
            name_part = cleaned.replace('Processing', '').strip()
            if ':' in name_part:
                name_only = name_part.split(':')[0].strip()
                pages_part = name_part.split(':', 1)[1].strip() if ':' in name_part else ''
                return f"  [cyan]{name_only.title()}[/cyan]", plain_text
            return f"[cyan]Processing[/cyan] {name_part}", plain_text
        elif 'pages →' in cleaned or '→' in cleaned:
            # Student completion - format nicely
            parts = cleaned.split('→')
            if len(parts) == 2:
                name_part = parts[0].strip()
                file_part = parts[1].strip()
                # Clean up name
                if ':' in name_part:
                    name_only = name_part.split(':')[0].strip()
                else:
                    name_only = name_part.replace('Processing', '').strip()
                return f"     → {name_only.title()} → {file_part}", plain_text
        elif 'added:' in message_lower:
            # File addition - suppress (handled by table)
            return None, plain_text
        elif cleaned.strip().startswith('=') or (cleaned.strip().startswith('-') and len(cleaned.strip()) > 10):
            return None, plain_text  # Suppress separator lines
        elif cleaned.startswith('   ') or cleaned.startswith('      '):
            return None, plain_text  # Suppress indented details
        else:
            # Only show important non-suppressed messages
            if any(keyword in message_lower for keyword in ['rezipping', 'found original', 'creating new zip']):
                return f"[dim]{cleaned.strip()}[/dim]", plain_text
            return None, plain_text  # Default to suppressing
    
    def format_file_table(self):
        """Format buffered file additions as a clean table"""
        if not self.file_additions:
            return None
        
        table = Table.grid(padding=(0, 2))
        table.add_column(style="dim", width=3)
        table.add_column(style="default")
        
        for i, file_path in enumerate(self.file_additions, 1):
            table.add_row(f"{i}.", file_path)
        
        self.file_additions = []  # Clear buffer
        return table

formatter = LogFormatter()

def format_log_message(message):
    """Legacy wrapper - now uses LogFormatter"""
    rich_text, plain_text = formatter.format_message(message)
    return rich_text or "", plain_text

def get_zip_name_from_assignment(assignment_name):
    """Construct ZIP filename from assignment name"""
    if not assignment_name:
        return None
    
    # Add " Download" suffix and .zip extension to match D2L format
    # The assignment name should already be clean (without " Download" suffix)
    zip_name = f"{assignment_name} Download.zip"
    return zip_name

def generate_index_html(student_folders, processing_folder, original_index_path=None):
    """Generate index.html file for D2L/Brightspace, using original if available"""
    # Get actual folder names that will be in the ZIP
    folder_names = [os.path.basename(f) for f in student_folders]
    
    # Try to use the original index.html as a template
    if original_index_path and os.path.exists(original_index_path):
        try:
            with open(original_index_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Parse the original and only include entries that match folders we have
            lines = original_content.split('\n')
            new_lines = []
            in_list = False
            list_updated = False
            
            for line in lines:
                # Detect when we enter the list section
                if '<ul>' in line.lower() or '<ol>' in line.lower():
                    in_list = True
                    new_lines.append(line)
                    # Insert our updated folder list - only include folders that exist
                    sorted_folders = sorted(student_folders, key=lambda x: os.path.basename(x))
                    for folder_path in sorted_folders:
                        folder_name = os.path.basename(folder_path)
                        # Skip unreadable folder
                        if folder_name.lower() == "unreadable":
                            continue
                        folder_name_escaped = folder_name.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
                        import urllib.parse
                        folder_name_encoded = urllib.parse.quote(folder_name, safe='')
                        new_lines.append(f'  <li><a href="{folder_name_encoded}/">{folder_name_escaped}</a></li>')
                    list_updated = True
                    continue
                # Skip old list items until we hit the closing tag
                if in_list and ('</ul>' in line.lower() or '</ol>' in line.lower()):
                    in_list = False
                    new_lines.append(line)
                    continue
                # Skip lines that are old list items
                if in_list and list_updated:
                    if '<li>' in line.lower() or '<a href' in line.lower():
                        continue  # Skip old list items
                
                new_lines.append(line)
            
            if list_updated:
                return '\n'.join(new_lines)
            else:
                # Fall through to generate new one if parsing failed
                pass
        except Exception as e:
            # If we can't parse the original, fall through to generate new one
            pass
    
    # Generate new index.html if original not available or parsing failed
    # Use format that more closely matches D2L's typical structure
    html_lines = [
        '<!DOCTYPE html>',
        '<html lang="en">',
        '<head>',
        '<meta charset="UTF-8">',
        '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">',
        '<title>Submissions</title>',
        '</head>',
        '<body>',
        '<h1>Submissions</h1>',
        '<ul>'
    ]
    
    # Sort folders by name for consistent ordering
    sorted_folders = sorted(student_folders, key=lambda x: os.path.basename(x))
    
    for folder_path in sorted_folders:
        folder_name = os.path.basename(folder_path)
        # Skip unreadable folder
        if folder_name.lower() == "unreadable":
            continue
        # Escape HTML characters in folder name (including quotes)
        folder_name_escaped = folder_name.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
        # URL encode the folder name for the href
        import urllib.parse
        folder_name_encoded = urllib.parse.quote(folder_name, safe='')
        # Create link to folder - use both escaped for display and encoded for URL
        html_lines.append(f'  <li><a href="{folder_name_encoded}/">{folder_name_escaped}</a></li>')
    
    html_lines.extend([
        '</ul>',
        '</body>',
        '</html>'
    ])
    
    return '\n'.join(html_lines)

def rezip_folders(drive, class_name, assignment_name, original_zip_name):
    """Rezip the processed folders back into a ZIP file"""
    try:
        # Get configured rosters path
        rosters_path = get_rosters_path()
        class_folder_path = os.path.join(rosters_path, class_name)
        
        # Try to find processing folder - handle both new format (with class code) and old format
        from grading_processor import extract_class_code
        class_code = extract_class_code(class_name)
        
        # Try new format first (with class code)
        if class_code:
            processing_folder = os.path.join(class_folder_path, f"grade processing {class_code} {assignment_name}")
            if not os.path.exists(processing_folder):
                # Fallback to old format (without class code)
                processing_folder = os.path.join(class_folder_path, f"grade processing {assignment_name}")
        else:
            # No class code, use old format
            processing_folder = os.path.join(class_folder_path, f"grade processing {assignment_name}")
        
        unzipped_folder = os.path.join(processing_folder, "unzipped folders")
        
        if not os.path.exists(unzipped_folder):
            log("SPLIT_UNZIPPED_NOT_FOUND")
            return False
        
        # Create new ZIP file in grade processing folder
        new_zip_path = os.path.join(processing_folder, original_zip_name)
        
        log("SPLIT_CREATING_ZIP", filename=original_zip_name)
        
        # Collect all student folders from unzipped folders directory
        student_folders = []
        for item in os.listdir(unzipped_folder):
            item_path = os.path.join(unzipped_folder, item)
            if os.path.isdir(item_path) and item.lower() != "unreadable":
                student_folders.append(item_path)
        
        # Try to find original index.html
        original_index_path = os.path.join(unzipped_folder, 'index.html.original')
        temp_index = os.path.join(unzipped_folder, 'index.html')
        
        # Check if we have the original preserved
        if os.path.exists(original_index_path):
            index_html_path = original_index_path
            # Copy it to index.html for use in ZIP
            import shutil
            shutil.copy2(original_index_path, temp_index)
            log("SPLIT_USING_PRESERVED_INDEX")
        elif os.path.exists(temp_index):
            # The index.html from extraction exists - use it as-is
            index_html_path = temp_index
            # Also preserve it as .original for future use
            try:
                import shutil
                shutil.copy2(temp_index, original_index_path)
            except Exception:
                pass
            log("SPLIT_USING_EXTRACTED_INDEX")
        else:
            # No original exists - generate a new one (fallback)
            log("SPLIT_NO_ORIGINAL_INDEX")
            index_html_content = generate_index_html(student_folders, unzipped_folder, None)
            index_html_path = temp_index
            with open(index_html_path, 'w', encoding='utf-8') as f:
                f.write(index_html_content)
            log("SPLIT_GENERATED_NEW_INDEX")
        
        # Check for any other files in the unzipped folder that should be included
        other_files = []
        for item in os.listdir(unzipped_folder):
            item_path = os.path.join(unzipped_folder, item)
            # Skip folders we're already processing and the index.html we just created
            if (os.path.isfile(item_path) and 
                item != 'index.html' and 
                not item.endswith('.original') and
                item.lower() != 'index.html.original'):
                other_files.append(item_path)
        
        with zipfile.ZipFile(new_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # First, add index.html to the root of the ZIP
            zip_file_to_add = temp_index if os.path.exists(temp_index) else index_html_path
            zipf.write(zip_file_to_add, 'index.html')
            log("SPLIT_ADDED_INDEX_TO_ZIP")
            
            # Add any other root-level files that were in the original ZIP
            for other_file in other_files:
                file_name = os.path.basename(other_file)
                zipf.write(other_file, file_name)
                log("SPLIT_ADDED_ROOT_FILE", filename=file_name)
            
            # Add all student folders to the ZIP
            for folder_path in student_folders:
                folder_name = os.path.basename(folder_path)
                # Add the entire folder to the ZIP
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Calculate relative path from unzipped folder
                        arcname = os.path.relpath(file_path, unzipped_folder)
                        zipf.write(file_path, arcname)
                        # Store in formatter for clean table display (don't log individually)
                        formatter.file_additions.append(arcname)
                        # Log to catalog
                        log("SPLIT_ADDED_TO_ZIP", filename=arcname)
        
        log("SPLIT_ZIP_CREATED", filename=new_zip_path)
        return True
        
    except Exception as e:
        log("SPLIT_ERROR_CREATING_ZIP", error=str(e))
        import traceback
        log("SPLIT_ERROR_DETAILS", details=traceback.format_exc())
        return False

def main():
    if len(sys.argv) < 3 or len(sys.argv) > 5:
        error_msg = "Usage: python split_pdf_cli.py <drive> <className> [assignmentName] [pdfPath]"
        print(json.dumps({
            "success": False,
            "error": error_msg,
            "logs": [
                "📦 Starting PDF split and rezip...",
                f"❌ Error: {error_msg}",
                "",
                "✅ Done"
            ]
        }))
        sys.exit(1)
    
    drive = sys.argv[1]
    class_name = sys.argv[2]
    # Handle both cases: assignment name OR PDF path, or both
    if len(sys.argv) >= 4:
        if len(sys.argv) == 5 and sys.argv[4] and os.path.exists(sys.argv[4]) and sys.argv[4].endswith('.pdf'):
            # 5 args: drive, className, assignmentName, '', pdfPath
            # 4th arg might be empty string, 5th is PDF path
            assignment_name = sys.argv[3] if sys.argv[3] else None
            pdf_path = sys.argv[4]
        elif sys.argv[3] and os.path.exists(sys.argv[3]) and sys.argv[3].endswith('.pdf'):
            # 4 args: drive, className, pdfPath (no assignment name)
            assignment_name = None
            pdf_path = sys.argv[3]
        else:
            # 4th arg is assignment name (no PDF path provided)
            assignment_name = sys.argv[3] if sys.argv[3] else None
            pdf_path = None
    else:
        assignment_name = None
        pdf_path = None
    
    try:
        log("SPLIT_STARTING_PROCESS")
        log("EMPTY_LINE")
        
        # Collect errors during processing
        processing_errors = []
        
        # Run the reverse process
        log("SPLIT_SPLITTING_PDF")
        result = run_reverse_process(drive, class_name, pdf_path)
        
        students_count = len(result.submitted) if hasattr(result, 'submitted') else 0
        if students_count > 0:
            log("SPLIT_SUCCESS_COUNT", count=students_count)
        else:
            log("SPLIT_NO_STUDENTS")
        
        # Get assignment name from result if available, or from CLI args
        if not assignment_name and hasattr(result, 'assignment_name'):
            assignment_name = result.assignment_name
        
        # Get ZIP name from assignment name (preferred) or fallback to finding most recent
        original_zip_name = None
        if assignment_name:
            original_zip_name = get_zip_name_from_assignment(assignment_name)
        else:
            # Fallback: find most recent ZIP in Downloads (legacy behavior)
            downloads_path = get_downloads_path()
            if os.path.exists(downloads_path):
                zip_files = []
                for file in os.listdir(downloads_path):
                    if file.lower().endswith('.zip'):
                        zip_path = os.path.join(downloads_path, file)
                        zip_files.append((zip_path, file))
                
                if zip_files:
                    latest_zip = max(zip_files, key=lambda x: os.path.getmtime(x[0]))
                    original_zip_name = latest_zip[1]
        
        rezip_success = False
        if original_zip_name and assignment_name:
            log("EMPTY_LINE")
            log("SPLIT_CREATING_ZIP_FILE", filename=original_zip_name)
            
            # Note: rezip_folders will use log() directly now
            rezip_success = rezip_folders(drive, class_name, assignment_name, original_zip_name)
            
            if rezip_success:
                log("SPLIT_ZIP_CREATED", filename=original_zip_name)
            else:
                log("SPLIT_ZIP_FAILED")
                processing_errors.append("ZIP creation failed")
        else:
            log("SPLIT_NO_NAME")
            processing_errors.append("Could not determine assignment name or ZIP name")
        
        # Build simplified output
        if processing_errors:
            log("EMPTY_LINE")
            log("SPLIT_ERRORS_HEADER")
            for error in processing_errors:
                log("SPLIT_ERROR_ITEM", error=error)
        
        log("EMPTY_LINE")
        log("SPLIT_COMPLETED")
        
        # Output JSON to stdout (for backend)
        response = {
            "success": True,
            "message": "PDF splitting and rezipping completed",
            "students_processed": students_count,
            "zip_created": original_zip_name is not None and rezip_success
        }
        
        print(json.dumps(response))
        
    except Exception as e:
        # Use standardized error formatting
        friendly_error = format_error_message(e)
        
        # Log the error
        log("ERR_UNEXPECTED", error=friendly_error)
        
        error_response = {
            "success": False,
            "error": friendly_error
        }
        print(json.dumps(error_response))
        sys.exit(1)

if __name__ == "__main__":
    main()
