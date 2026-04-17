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
from grading_helpers import (
    list_class_processing_folders_with_pdfs,
    resolve_workspace_folder_from_assignment_hint,
)

# Container folder for all archived assignment folders (inside class folder)
ARCHIVED_FOLDERS_NAME = "Archived Folders"
UNZIPPED_FOLDER_NAMES = ["unzipped folders", "u"]


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


def _processing_basename_for_archived_link(folder_name: str) -> str:
    """Stem used with archived folders (legacy grade processing or short names)."""
    m = re.match(r'^grade processing (.+)$', folder_name, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return folder_name.strip()


def archived_name_for_processing_folder(folder_name: str) -> str:
    return f"archived {_processing_basename_for_archived_link(folder_name)}"


def list_processing_folders(class_folder_path: str) -> list[dict[str, str]]:
    """
    List active assignment workspaces (folders with PDFs) and archived folders.
    Includes legacy 'grade processing …' names and short names like 'Quiz 4'.
    
    Returns:
        List of dicts with keys: name, path, size, modified
    """
    if not os.path.exists(class_folder_path):
        return []
    
    folders = []
    processing_pattern = re.compile(r'^grade processing (.+)$', re.IGNORECASE)
    archived_pattern = re.compile(r'^archived (.+)$', re.IGNORECASE)

    def add_folder_if_match(folder_path: str, folder_name: str) -> None:
        if not os.path.isdir(folder_path):
            return
        processing_match = processing_pattern.match(folder_name)
        archived_match = archived_pattern.match(folder_name)
        has_pdfs = os.path.isdir(os.path.join(folder_path, 'PDFs'))
        is_active = processing_match or (has_pdfs and not archived_match)
        if is_active or archived_match:
            size = get_folder_size(folder_path)
            modified = os.path.getmtime(folder_path)
            folders.append({
                'name': folder_name,
                'path': folder_path,
                'size': format_size(size),
                'modified': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(modified))
            })

    for folder_name in os.listdir(class_folder_path):
        folder_path = os.path.join(class_folder_path, folder_name)
        add_folder_if_match(folder_path, folder_name)

    archived_container = os.path.join(class_folder_path, ARCHIVED_FOLDERS_NAME)
    if os.path.isdir(archived_container):
        for folder_name in os.listdir(archived_container):
            folder_path = os.path.join(archived_container, folder_name)
            add_folder_if_match(folder_path, folder_name)
    
    # Sort by modification time (newest first)
    folders.sort(key=lambda x: x['modified'], reverse=True)
    
    return folders


def clear_all_archived_data(class_folder_path: str) -> int:
    """
    Clear all 'archived [Assignment]' folders in the class folder (root and inside Archived Folders).
    
    Returns:
        deleted_count
    """
    if not os.path.exists(class_folder_path):
        log("ERR_NO_FOLDER")
        return 0
    
    deleted_count = 0
    pattern = re.compile(r'^archived (.+)$', re.IGNORECASE)

    def delete_archived_in_dir(dir_path: str) -> None:
        nonlocal deleted_count
        if not os.path.exists(dir_path):
            return
        for folder_name in os.listdir(dir_path):
            folder_path = os.path.join(dir_path, folder_name)
            if not os.path.isdir(folder_path):
                continue
            if pattern.match(folder_name):
                close_explorer_windows_for_path(folder_path)
                time.sleep(0.5)
                if safe_remove_tree(folder_path):
                    deleted_count += 1
                    log("CLEAR_DELETED", folder_name=folder_name)
                else:
                    log("ERR_CLEAR_FAILED_DELETE")

    delete_archived_in_dir(class_folder_path)
    delete_archived_in_dir(os.path.join(class_folder_path, ARCHIVED_FOLDERS_NAME))
    
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
        for unzipped_folder_name in UNZIPPED_FOLDER_NAMES:
            unzipped_folder = os.path.join(folder_path, unzipped_folder_name)
            if os.path.exists(unzipped_folder):
                safe_remove_tree(unzipped_folder)
        
        # Move folder to 'Archived Folders/archived [Assignment]'
        new_folder_name = archived_name_for_processing_folder(folder_name)
        archived_root = os.path.join(parent_folder, ARCHIVED_FOLDERS_NAME)
        os.makedirs(archived_root, exist_ok=True)
        new_folder_path = os.path.join(archived_root, new_folder_name)

        if os.path.exists(new_folder_path):
            safe_remove_tree(new_folder_path)

        try:
            os.rename(folder_path, new_folder_path)
            log("CLEAR_ARCHIVED_TO", folder_name=new_folder_name)
            return True
        except Exception as e:
            log("ERR_CLEAR_FAILED_RENAME", error=str(e))
            return False
        
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
        
        # Move folder to 'Archived Folders/archived [Assignment]'
        new_folder_name = archived_name_for_processing_folder(folder_name)
        archived_root = os.path.join(parent_folder, ARCHIVED_FOLDERS_NAME)
        os.makedirs(archived_root, exist_ok=True)
        new_folder_path = os.path.join(archived_root, new_folder_name)

        if os.path.exists(new_folder_path):
            safe_remove_tree(new_folder_path)

        try:
            os.rename(folder_path, new_folder_path)
            log("CLEAR_ARCHIVED_TO", folder_name=new_folder_name)
            return True
        except Exception as e:
            log("ERR_CLEAR_FAILED_RENAME", error=str(e))
            return False
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
            
            # Also delete corresponding archived folder (check root and Archived Folders)
            if not re.match(r'^archived ', folder_name, re.IGNORECASE):
                archived_folder_name = archived_name_for_processing_folder(folder_name)
                for archived_path in (
                    os.path.join(parent_folder, archived_folder_name),
                    os.path.join(parent_folder, ARCHIVED_FOLDERS_NAME, archived_folder_name),
                ):
                    if os.path.exists(archived_path):
                        if safe_remove_tree(archived_path):
                            log("CLEAR_DELETED", folder_name=archived_folder_name)
                        break
            
            return True
        else:
            log("ERR_CLEAR_FAILED_DELETE")
            return False
    elif save_mode == 'delete_everything':
        # Delete the entire folder completely (for selected folders)
        # Removes both processing and archived; if selected folder is archived, also remove processing
        if safe_remove_tree(folder_path):
            log("CLEAR_DELETED", folder_name=folder_name)
            
            # If this was a processing folder, delete corresponding archived (root or Archived Folders)
            if not re.match(r'^archived ', folder_name, re.IGNORECASE):
                archived_folder_name = archived_name_for_processing_folder(folder_name)
                for archived_path in (
                    os.path.join(parent_folder, archived_folder_name),
                    os.path.join(parent_folder, ARCHIVED_FOLDERS_NAME, archived_folder_name),
                ):
                    if os.path.exists(archived_path):
                        if safe_remove_tree(archived_path):
                            log("CLEAR_DELETED", folder_name=archived_folder_name)
                        break
            
            # If this was an archived folder, delete corresponding processing (always in class root)
            match = re.match(r'^archived (.+)$', folder_name, re.IGNORECASE)
            if match:
                assignment_key = match.group(1).strip()
                class_root = os.path.dirname(parent_folder) if os.path.basename(parent_folder) == ARCHIVED_FOLDERS_NAME else parent_folder
                for processing_folder_path in (
                    os.path.join(class_root, assignment_key),
                    os.path.join(class_root, f"grade processing {assignment_key}"),
                ):
                    if os.path.exists(processing_folder_path):
                        if safe_remove_tree(processing_folder_path):
                            log("CLEAR_DELETED", folder_name=os.path.basename(processing_folder_path))
                        break
            
            return True
        else:
            log("ERR_CLEAR_FAILED_DELETE")
            return False
    else:
        log("ERR_UNKNOWN_MODE", mode=save_mode)
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
        
        # Find the target processing folder
        if assignment_name:
            processing_folder = resolve_workspace_folder_from_assignment_hint(
                class_folder, class_name, assignment_name
            )
            if not processing_folder:
                log(
                    "ERR_CLEAR_FOLDER_NOT_FOUND",
                    assignment=assignment_name,
                    path=assignment_name,
                )
                sys.exit(1)
        else:
            log("ERR_NO_ASSIGNMENTS")
            sys.exit(1)
        
        # Clear the data for specific assignment
        log("CLEAR_TARGET_FOLDER", folder_name=os.path.basename(processing_folder))
        if save_mode == 'save_folders_and_pdf':
            log("CLEAR_MODE_SELECTIVE")
        elif save_mode == 'save_combined_pdf':
            # Add log message for this mode
            pass  # No specific log message for this, just proceed
        elif save_mode == 'delete_everything':
            # Delete everything in THIS specific folder
            log("CLEAR_MODE_FULL")
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
