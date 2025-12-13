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
from grading_processor import run_reverse_process
from config_reader import get_downloads_path, get_rosters_path

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

def rezip_folders(drive, class_name, original_zip_name, log_callback):
    """Rezip the processed folders back into a ZIP file"""
    try:
        # Get configured rosters path
        rosters_path = get_rosters_path()
        class_folder_path = os.path.join(rosters_path, class_name)
        
        processing_folder = os.path.join(class_folder_path, "grade processing")
        
        if not os.path.exists(processing_folder):
            log_callback("❌ Grade processing folder not found")
            return False
        
        # Create new ZIP file in grade processing folder
        new_zip_path = os.path.join(processing_folder, original_zip_name)
        
        log_callback(f"📦 Creating new ZIP: {original_zip_name}")
        
        # Collect all student folders (exclude PDFs and unreadable folders)
        student_folders = []
        for item in os.listdir(processing_folder):
            item_path = os.path.join(processing_folder, item)
            if (os.path.isdir(item_path) and 
                item != "PDFs" and 
                item.lower() != "unreadable"):
                student_folders.append(item_path)
        
        # Try to find original index.html - use it EXACTLY as-is if it exists
        original_index_path = os.path.join(processing_folder, 'index.html.original')
        temp_index = os.path.join(processing_folder, 'index.html')
        
        # Check if we have the original preserved
        if os.path.exists(original_index_path):
            index_html_path = original_index_path
            # Copy it to index.html for use in ZIP
            import shutil
            shutil.copy2(original_index_path, temp_index)
            log_callback("   Using preserved original index.html (exact copy)")
        elif os.path.exists(temp_index):
            # The index.html from extraction exists - use it as-is
            index_html_path = temp_index
            # Also preserve it as .original for future use
            try:
                import shutil
                shutil.copy2(temp_index, original_index_path)
            except Exception:
                pass
            log_callback("   Using original index.html from extraction (exact copy)")
        else:
            # No original exists - generate a new one (fallback)
            log_callback("   Warning: No original index.html found, generating new one")
            index_html_content = generate_index_html(student_folders, processing_folder, None)
            index_html_path = temp_index
            with open(index_html_path, 'w', encoding='utf-8') as f:
                f.write(index_html_content)
            log_callback("   Generated new index.html (fallback - may not work with D2L)")
        
        # Check for any other files in the processing folder that should be included
        other_files = []
        for item in os.listdir(processing_folder):
            item_path = os.path.join(processing_folder, item)
            # Skip folders we're already processing, PDFs folder, and the index.html we just created
            if (os.path.isfile(item_path) and 
                item != 'index.html' and 
                not item.endswith('.original') and
                item.lower() != 'index.html.original'):
                other_files.append(item_path)
        
        with zipfile.ZipFile(new_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # First, add index.html to the root of the ZIP (use the actual file path)
            zip_file_to_add = temp_index if os.path.exists(temp_index) else index_html_path
            # Add index.html - use same compression as other files (DEFLATED works fine)
            zipf.write(zip_file_to_add, 'index.html')
            log_callback("   Added index.html to ZIP root")
            
            # Add any other root-level files that were in the original ZIP
            for other_file in other_files:
                file_name = os.path.basename(other_file)
                zipf.write(other_file, file_name)
                log_callback(f"   Added root file: {file_name}")
            
            # Add all student folders to the ZIP
            for folder_path in student_folders:
                folder_name = os.path.basename(folder_path)
                # Add the entire folder to the ZIP
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Calculate relative path from processing folder
                        arcname = os.path.relpath(file_path, processing_folder)
                        zipf.write(file_path, arcname)
                        # Store in formatter for clean table display (don't log individually)
                        formatter.file_additions.append(arcname)
                        # Still add to JSON logs
                        log_callback(f"Added: {arcname}")
        
        log_callback(f"✅ Created ZIP file: {new_zip_path}")
        return True
        
    except Exception as e:
        log_callback(f"❌ Error creating ZIP: {str(e)}")
        import traceback
        log_callback(f"   Details: {traceback.format_exc()}")
        return False

def main():
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        error_msg = "Usage: python split_pdf_cli.py <drive> <className> [assignmentName]"
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
    assignment_name = sys.argv[3] if len(sys.argv) == 4 else None
    
    try:
        # Simplified logs - only important information
        logs = []
        logs.append("📦 Starting PDF split and rezip...")
        
        # Collect errors during processing
        processing_errors = []
        
        def log_callback(message):
            # Suppress all verbose logging - only collect errors
            message_lower = message.lower()
            
            # Only collect errors and warnings
            if (
                'error' in message_lower or 
                '❌' in message or 
                'failed' in message_lower or
                'could not find folder for' in message_lower
            ):
                processing_errors.append(message)
            # Suppress everything else
        
        # Run the reverse process (suppresses verbose logging)
        result = run_reverse_process(drive, class_name, log_callback)
        
        students_count = len(result.submitted) if hasattr(result, 'submitted') else 0
        logs.append(f"✅ Successfully split PDF for {students_count} students")
        
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
        if original_zip_name:
            rezip_success = rezip_folders(drive, class_name, original_zip_name, lambda msg: None)  # Suppress rezip logs
            
            if rezip_success:
                logs.append(f"✅ Created ZIP file: {original_zip_name}")
            else:
                processing_errors.append("⚠️ ZIP creation failed, but PDFs were split")
        else:
            processing_errors.append("⚠️ Could not determine ZIP name, skipping rezip")
        
        # Build simplified output
        if processing_errors:
            logs.append("")
            logs.append("❌ Errors:")
            for error in processing_errors:
                logs.append(f"   {error}")
        
        logs.append("")
        logs.append("✅ completed!")
        
        # Output JSON to stdout (for backend)
        response = {
            "success": True,
            "message": "PDF splitting and rezipping completed",
            "logs": logs,
            "students_processed": students_count,
            "zip_created": original_zip_name is not None and rezip_success
        }
        
        print(json.dumps(response))
        
    except Exception as e:
        error_msg = str(e)
        
        # Determine friendly error message
        if "combined pdf not found" in error_msg.lower() or "could not find" in error_msg.lower() and "pdf" in error_msg.lower():
            friendly_error = "Could not process. There's no PDF to split."
        elif error_msg and error_msg.strip() and not error_msg.lower().startswith("usage"):
            # There's a specific error message - use it
            friendly_error = error_msg
        else:
            # Unknown error
            friendly_error = "Something ran into a problem with the split and zip."
        
        # Build simplified error output
        error_logs = []
        error_logs.append("❌ Split PDF failed")
        
        error_response = {
            "success": False,
            "error": "Split PDF failed",
            "logs": error_logs
        }
        print(json.dumps(error_response))
        sys.exit(1)

if __name__ == "__main__":
    main()
