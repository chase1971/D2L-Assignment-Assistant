#!/usr/bin/env python3
"""
CLI script for clearing assignment data with selective preservation
Usage: python clear_data_cli.py <drive> <className> [assignmentName] [--save-folders-and-pdf|--save-combined-pdf] [--list]
"""

import sys
import os

# Add python-modules to path for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_MODULES_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'python-modules')
sys.path.insert(0, PYTHON_MODULES_DIR)

import json
import shutil
import time
import stat
import re
import subprocess
from glob import glob
from config_reader import get_rosters_path
from user_messages import log


def extract_class_code(class_folder_name: str) -> str:
    """
    Extract class code (e.g., "FM 4202") from class folder name.
    
    Examples:
        "TTH 11-1220 FM 4202" -> "FM 4202"
        "MW 930-1050 CA 4105" -> "CA 4105"
    """
    # Look for pattern: 2 letters, space, 4 digits at the end
    match = re.search(r'([A-Z]{2}\s+\d{4})\s*$', class_folder_name)
    if match:
        return match.group(1)
    # Fallback: try to extract last 7 characters
    if len(class_folder_name) >= 7:
        return class_folder_name[-7:].strip()
    return ""


def force_remove_readonly(func, path, exc):
    """Remove read-only files and directories"""
    if os.path.exists(path):
        os.chmod(path, stat.S_IWRITE)
        func(path)


def close_explorer_windows_for_path(folder_path: str):
    """Force close any Windows Explorer windows showing the specified path"""
    if sys.platform != 'win32':
        return
    
    try:
        # Use PowerShell to close Explorer windows showing this path
        normalized_path = os.path.normpath(folder_path).lower()
        ps_script = f'''
        $shell = New-Object -ComObject Shell.Application
        $shell.Windows() | Where-Object {{ $_.LocationURL -like "*{normalized_path.replace(chr(92), '/')}*" }} | ForEach-Object {{ $_.Quit() }}
        '''
        subprocess.run(['powershell', '-Command', ps_script], 
                      capture_output=True, 
                      timeout=5,
                      creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception:
        pass  # Silently fail if we can't close windows


def safe_remove_file(file_path: str, max_retries: int = 3) -> bool:
    """Safely remove a file with retry logic"""
    for attempt in range(max_retries):
        try:
            if os.path.exists(file_path):
                os.chmod(file_path, stat.S_IWRITE)
                os.remove(file_path)
                return True
        except Exception:
            if attempt < max_retries - 1:
                time.sleep(0.5)
                continue
            return False
    return False


def safe_remove_tree(folder_path: str, max_retries: int = 3) -> bool:
    """Safely remove a directory tree with retry logic"""
    for attempt in range(max_retries):
        try:
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path, onerror=force_remove_readonly)
                return True
        except Exception:
            if attempt < max_retries - 1:
                time.sleep(0.5)
                continue
            return False
    return False


def get_folder_size(folder_path: str) -> int:
    """Get total size of folder in bytes"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
    except Exception:
        pass
    return total_size


def format_size(size_bytes: int) -> str:
    """Format size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def list_processing_folders(class_folder_path: str) -> list[dict[str, str]]:
    """
    List all 'grade processing [Assignment]' and 'archived [Assignment]' folders in the class folder.
    
    Returns:
        List of dicts with keys: name, path, size, modified
    """
    if not os.path.exists(class_folder_path):
        return []
    
    folders = []
    processing_pattern = re.compile(r'^grade processing (.+)$', re.IGNORECASE)
    archived_pattern = re.compile(r'^archived (.+)$', re.IGNORECASE)
    
    for folder_name in os.listdir(class_folder_path):
        folder_path = os.path.join(class_folder_path, folder_name)
        if not os.path.isdir(folder_path):
            continue
        
        # Check for both patterns
        processing_match = processing_pattern.match(folder_name)
        archived_match = archived_pattern.match(folder_name)
        
        if processing_match or archived_match:
            size = get_folder_size(folder_path)
            modified = os.path.getmtime(folder_path)
            
            folders.append({
                'name': folder_name,  # Use full folder name including "grade processing" or "archived"
                'path': folder_path,
                'size': format_size(size),
                'modified': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(modified))
            })
    
    # Sort by modification time (newest first)
    folders.sort(key=lambda x: x['modified'], reverse=True)
    
    return folders


def clear_all_archived_data(class_folder_path: str) -> int:
    """
    Clear all 'archived [Assignment]' folders in the class folder.
    
    Returns:
        deleted_count
    """
    if not os.path.exists(class_folder_path):
        log("ERR_NO_FOLDER")
        return 0
    
    deleted_count = 0
    pattern = re.compile(r'^archived (.+)$', re.IGNORECASE)
    
    for folder_name in os.listdir(class_folder_path):
        folder_path = os.path.join(class_folder_path, folder_name)
        if not os.path.isdir(folder_path):
            continue
        
        match = pattern.match(folder_name)
        if match:
            # Force close any explorer windows showing this folder
            close_explorer_windows_for_path(folder_path)
            time.sleep(0.5)  # Give Windows time to close the window
            
            if safe_remove_tree(folder_path):
                deleted_count += 1
                log("CLEAR_DELETED", folder_name=folder_name)
            else:
                log("ERR_CLEAR_FAILED_DELETE")
    
    return deleted_count


def clear_assignment_data(folder_path: str, save_mode: str = 'delete_all') -> bool:
    """
    Clear data with optional selective preservation.
    
    Args:
        folder_path: Path to 'grade processing [Assignment]' folder
        save_mode: One of 'delete_all', 'save_folders_and_pdf', 'save_combined_pdf'
    
    Returns:
        success status
    """
    if not os.path.exists(folder_path):
        log("ERR_NO_FOLDER")
        return False
    
    folder_name = os.path.basename(folder_path)
    parent_folder = os.path.dirname(folder_path)
    
    # Delete ZIP files created from split/rezip in ALL modes
    for file in os.listdir(folder_path):
        if file.endswith('.zip') and 'Download' in file:
            zip_path = os.path.join(folder_path, file)
            safe_remove_file(zip_path)
    
    if save_mode == 'save_combined_pdf':
        # Save only combined PDF: Extract it to root, delete everything else, then archive
        pdfs_folder = os.path.join(folder_path, "PDFs")
        combined_pdf_source = None
        
        # Find combined PDF in PDFs folder (case-insensitive)
        if os.path.exists(pdfs_folder):
            for file in os.listdir(pdfs_folder):
                if file.endswith('.pdf') and 'combined pdf' in file.lower():
                    combined_pdf_source = os.path.join(pdfs_folder, file)
                    break
        
        if combined_pdf_source:
            # Move combined PDF to root of processing folder
            combined_pdf_dest = os.path.join(folder_path, os.path.basename(combined_pdf_source))
            try:
                shutil.copy2(combined_pdf_source, combined_pdf_dest)
            except Exception:
                pass
        
        # Delete PDFs folder
        if os.path.exists(pdfs_folder):
            safe_remove_tree(pdfs_folder)
        
        # Delete unreadable folder
        unreadable_folder = os.path.join(folder_path, "unreadable")
        if os.path.exists(unreadable_folder):
            safe_remove_tree(unreadable_folder)
        
        # Delete unzipped folders
        unzipped_folder = os.path.join(folder_path, "unzipped folders")
        if os.path.exists(unzipped_folder):
            safe_remove_tree(unzipped_folder)
        
        # Rename folder to 'archived [Assignment]'
        match = re.match(r'^grade processing (.+)$', folder_name, re.IGNORECASE)
        if match:
            assignment_name = match.group(1)
            new_folder_name = f"archived {assignment_name}"
            new_folder_path = os.path.join(parent_folder, new_folder_name)
            
            # If archived folder already exists, remove it first
            if os.path.exists(new_folder_path):
                safe_remove_tree(new_folder_path)
            
            try:
                os.rename(folder_path, new_folder_path)
                log("CLEAR_ARCHIVED_TO", folder_name=new_folder_name)
                return True
            except Exception as e:
                log("ERR_CLEAR_FAILED_RENAME", error=str(e))
                return False
        
        return True
        
    elif save_mode == 'save_folders_and_pdf':
        # Save folders and PDF: Keep unzipped folders, extract combined PDF to root, delete PDFs folder
        pdfs_folder = os.path.join(folder_path, "PDFs")
        combined_pdf_source = None
        
        # Find combined PDF in PDFs folder (case-insensitive)
        if os.path.exists(pdfs_folder):
            for file in os.listdir(pdfs_folder):
                if file.endswith('.pdf') and 'combined pdf' in file.lower():
                    combined_pdf_source = os.path.join(pdfs_folder, file)
                    break
        
        if combined_pdf_source:
            # Move combined PDF to root of processing folder
            combined_pdf_dest = os.path.join(folder_path, os.path.basename(combined_pdf_source))
            try:
                shutil.copy2(combined_pdf_source, combined_pdf_dest)
            except Exception:
                pass
        
        # Delete PDFs folder (all individual PDFs)
        if os.path.exists(pdfs_folder):
            safe_remove_tree(pdfs_folder)
        
        # Delete unreadable folder
        unreadable_folder = os.path.join(folder_path, "unreadable")
        if os.path.exists(unreadable_folder):
            safe_remove_tree(unreadable_folder)
        
        # Rename folder to 'archived [Assignment]'
        match = re.match(r'^grade processing (.+)$', folder_name, re.IGNORECASE)
        if match:
            assignment_name = match.group(1)
            new_folder_name = f"archived {assignment_name}"
            new_folder_path = os.path.join(parent_folder, new_folder_name)
            
            # If archived folder already exists, remove it first
            if os.path.exists(new_folder_path):
                safe_remove_tree(new_folder_path)
            
            try:
                os.rename(folder_path, new_folder_path)
                log("CLEAR_ARCHIVED_TO", folder_name=new_folder_name)
                return True
            except Exception as e:
                log("ERR_CLEAR_FAILED_RENAME", error=str(e))
                return False
        
        log("CLEAR_SELECTIVE_COMPLETE")
        return True
    elif save_mode == 'delete_all':
        # Delete only processing folder (keep archived)
        if safe_remove_tree(folder_path):
            log("CLEAR_DELETED", folder_name=folder_name)
            return True
        else:
            log("ERR_CLEAR_FAILED_DELETE")
            return False
    elif save_mode == 'delete_all_with_archived':
        # Delete processing folder, then also delete corresponding archived folder if it exists
        if safe_remove_tree(folder_path):
            log("CLEAR_DELETED", folder_name=folder_name)
            
            # Also delete corresponding archived folder if it exists
            match = re.match(r'^grade processing (.+)$', folder_name, re.IGNORECASE)
            if match:
                assignment_name = match.group(1)
                archived_folder_name = f"archived {assignment_name}"
                archived_folder_path = os.path.join(parent_folder, archived_folder_name)
                if os.path.exists(archived_folder_path):
                    if safe_remove_tree(archived_folder_path):
                        log("CLEAR_DELETED", folder_name=archived_folder_name)
            
            return True
        else:
            log("ERR_CLEAR_FAILED_DELETE")
            return False
    else:
        # delete_everything mode - handled separately in main()
        return False


def main():
    # Check for --list flag
    if "--list" in sys.argv:
        if len(sys.argv) < 3:
            print(json.dumps({
                "success": False,
                "error": "Usage: python clear_data_cli.py <drive> <className> --list"
            }))
            sys.exit(1)
        
        drive = sys.argv[1]
        class_name = sys.argv[2]
        
        try:
            rosters_path = get_rosters_path()
            
            # Find class folder
            class_folder = None
            if os.path.exists(rosters_path):
                for folder in os.listdir(rosters_path):
                    if class_name in folder:
                        class_folder = os.path.join(rosters_path, folder)
                        break
            
            if not class_folder:
                print(json.dumps({
                    "success": False,
                    "error": f"Class folder not found: {class_name}"
                }))
                sys.exit(1)
            
            # List processing folders
            folders = list_processing_folders(class_folder)
            
            print(json.dumps({
                "success": True,
                "folders": folders
            }))
            sys.exit(0)
            
        except Exception as e:
            print(json.dumps({
                "success": False,
                "error": str(e)
            }))
            sys.exit(1)
    
    # Check for --clear-archived flag
    if "--clear-archived" in sys.argv:
        if len(sys.argv) < 3:
            print(json.dumps({
                "success": False,
                "error": "Usage: python clear_data_cli.py <drive> <className> --clear-archived"
            }))
            sys.exit(1)
        
        drive = sys.argv[1]
        class_name = sys.argv[2]
        
        try:
            log("CLEAR_ARCHIVED", class_name=class_name)
            
            rosters_path = get_rosters_path()
            
            # Find class folder
            class_folder = None
            if os.path.exists(rosters_path):
                for folder in os.listdir(rosters_path):
                    if class_name in folder:
                        class_folder = os.path.join(rosters_path, folder)
                        break
            
            if not class_folder:
                log("ERR_NO_FOLDER")
                sys.exit(1)
            
            # Clear all archived folders
            deleted_count = clear_all_archived_data(class_folder)
            
            if deleted_count > 0:
                log("CLEAR_ARCHIVED_SUCCESS", count=deleted_count)
            else:
                log("CLEAR_NO_ARCHIVED")
            
            sys.exit(0)
            
        except Exception as e:
            error_str = str(e).lower()
            if "being used by another process" in error_str or "locked" in error_str:
                log("ERR_FILE_LOCKED")
            elif "permission denied" in error_str:
                log("ERR_PERMISSION")
            else:
                log("ERR_GENERIC", error=str(e))
            sys.exit(1)
    
    # Normal clear operation
    if len(sys.argv) < 3:
        print(json.dumps({
            "success": False,
            "error": "Usage: python clear_data_cli.py <drive> <className> [assignmentName] [--save-folders-and-pdf|--save-combined-pdf]"
        }))
        sys.exit(1)
    
    drive = sys.argv[1]
    class_name = sys.argv[2]
    assignment_name = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith('--') else None
    
    # Determine save mode
    if "--save-folders-and-pdf" in sys.argv:
        save_mode = 'save_folders_and_pdf'
    elif "--save-combined-pdf" in sys.argv:
        save_mode = 'save_combined_pdf'
    elif "--delete-everything" in sys.argv:
        save_mode = 'delete_everything'
    elif "--delete-all-with-archived" in sys.argv:
        save_mode = 'delete_all_with_archived'  # Delete processing + archived
    else:
        save_mode = 'delete_all'  # Only delete processing folder (keep archived)
    
    try:
        log("CLEAR_STARTING", class_name=class_name)
        
        rosters_path = get_rosters_path()
        
        # Find class folder
        class_folder = None
        if os.path.exists(rosters_path):
            for folder in os.listdir(rosters_path):
                if class_name in folder:
                    class_folder = os.path.join(rosters_path, folder)
                    break
        
        if not class_folder:
            log("ERR_NO_FOLDER")
            sys.exit(1)
        
        # Handle delete_everything mode separately (doesn't need assignment_name)
        if save_mode == 'delete_everything':
            # Delete ALL grade processing folders AND ALL archived folders
            log("CLEAR_MODE_EVERYTHING")
            
            deleted_count = 0
            
            # Delete all grade processing folders
            processing_pattern = re.compile(r'^grade processing (.+)$', re.IGNORECASE)
            for folder_name in os.listdir(class_folder):
                folder_path = os.path.join(class_folder, folder_name)
                if os.path.isdir(folder_path):
                    if processing_pattern.match(folder_name):
                        if safe_remove_tree(folder_path):
                            log("CLEAR_DELETED", folder_name=folder_name)
                            deleted_count += 1
            
            # Delete all archived folders
            archived_pattern = re.compile(r'^archived (.+)$', re.IGNORECASE)
            for folder_name in os.listdir(class_folder):
                folder_path = os.path.join(class_folder, folder_name)
                if os.path.isdir(folder_path):
                    if archived_pattern.match(folder_name):
                        if safe_remove_tree(folder_path):
                            log("CLEAR_DELETED", folder_name=folder_name)
                            deleted_count += 1
            
            if deleted_count > 0:
                log("CLEAR_SUCCESS")
            else:
                log("CLEAR_NO_FOLDERS")
            sys.exit(0)
        
        # Find the target processing folder
        if assignment_name:
            # Check if assignment_name already includes the prefix
            if assignment_name.lower().startswith("grade processing ") or assignment_name.lower().startswith("archived "):
                # Use the folder name directly
                processing_folder = os.path.join(class_folder, assignment_name)
            else:
                # Clean the assignment name - remove "combined PDF", class code, and other suffixes
                cleaned_assignment = assignment_name
                
                # Remove "combined PDF" suffix (case insensitive)
                cleaned_assignment = re.sub(r'\s+combined\s+pdf\s*$', '', cleaned_assignment, flags=re.IGNORECASE)
                
                # Extract class code from class name
                class_code = extract_class_code(class_name)
                
                # Remove class code from assignment name if it's in there (e.g., "Quiz 4 FM 4202" -> "Quiz 4")
                if class_code:
                    # Remove class code pattern from assignment name
                    class_code_pattern = re.escape(class_code)
                    cleaned_assignment = re.sub(r'\s*' + class_code_pattern + r'\s*', ' ', cleaned_assignment, flags=re.IGNORECASE)
                    cleaned_assignment = cleaned_assignment.strip()
                
                # Clean up any extra spaces
                cleaned_assignment = re.sub(r'\s+', ' ', cleaned_assignment).strip()
                
                # Construct folder name with class code
                if class_code:
                    processing_folder = os.path.join(class_folder, f"grade processing {class_code} {cleaned_assignment}")
                else:
                    # Fallback if class code can't be extracted
                    processing_folder = os.path.join(class_folder, f"grade processing {cleaned_assignment}")
            
            if not os.path.exists(processing_folder):
                # Try to find the folder by searching for folders that contain the assignment name
                # This helps if the assignment name format is slightly different
                pattern = re.compile(r'^grade processing (.+)$', re.IGNORECASE)
                matching_folders = []
                for folder_name in os.listdir(class_folder):
                    folder_path = os.path.join(class_folder, folder_name)
                    if os.path.isdir(folder_path):
                        match = pattern.match(folder_name)
                        if match:
                            folder_assignment = match.group(1)
                            # Check if the cleaned assignment name is in the folder name
                            if cleaned_assignment.lower() in folder_assignment.lower() or folder_assignment.lower() in cleaned_assignment.lower():
                                matching_folders.append(folder_path)
                
                if matching_folders:
                    # Use the first matching folder
                    processing_folder = matching_folders[0]
                    log("CLEAR_FOUND_MATCHING", folder_name=os.path.basename(processing_folder))
                else:
                    log("ERR_CLEAR_FOLDER_NOT_FOUND", 
                        assignment=assignment_name, 
                        path=os.path.basename(processing_folder))
                    sys.exit(1)
        else:
            log("ERR_NO_ASSIGNMENTS")
            sys.exit(1)
        
        # Handle delete_everything mode separately
        if save_mode == 'delete_everything':
            # Delete ALL grade processing folders AND ALL archived folders
            log("CLEAR_MODE_EVERYTHING")
            
            deleted_count = 0
            
            # Delete all grade processing folders
            processing_pattern = re.compile(r'^grade processing (.+)$', re.IGNORECASE)
            for folder_name in os.listdir(class_folder):
                folder_path = os.path.join(class_folder, folder_name)
                if os.path.isdir(folder_path):
                    if processing_pattern.match(folder_name):
                        if safe_remove_tree(folder_path):
                            log("CLEAR_DELETED", folder_name=folder_name)
                            deleted_count += 1
            
            # Delete all archived folders
            archived_pattern = re.compile(r'^archived (.+)$', re.IGNORECASE)
            for folder_name in os.listdir(class_folder):
                folder_path = os.path.join(class_folder, folder_name)
                if os.path.isdir(folder_path):
                    if archived_pattern.match(folder_name):
                        if safe_remove_tree(folder_path):
                            log("CLEAR_DELETED", folder_name=folder_name)
                            deleted_count += 1
            
            if deleted_count > 0:
                log("CLEAR_SUCCESS")
            else:
                log("CLEAR_NO_FOLDERS")
            sys.exit(0)
        
        # Clear the data for specific assignment
        log("CLEAR_TARGET_FOLDER", folder_name=os.path.basename(processing_folder))
        if save_mode == 'save_folders_and_pdf':
            log("CLEAR_MODE_SELECTIVE")
        elif save_mode == 'save_combined_pdf':
            # Add log message for this mode
            pass  # No specific log message for this, just proceed
        else:
            log("CLEAR_MODE_FULL")
        
        success = clear_assignment_data(processing_folder, save_mode)
        
        if success:
            log("CLEAR_SUCCESS")
        else:
            sys.exit(1)
        
    except Exception as e:
        error_str = str(e).lower()
        if "being used by another process" in error_str or "locked" in error_str:
            log("ERR_FILE_LOCKED")
        elif "permission denied" in error_str:
            log("ERR_PERMISSION")
        else:
            log("ERR_GENERIC", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
