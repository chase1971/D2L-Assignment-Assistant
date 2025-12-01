#!/usr/bin/env python3
"""
CLI script for cleaning up quiz data - called by the Node.js backend
Usage: python cleanup_data_cli.py <drive> <className>
"""

import sys
import os
import json
import shutil
import time
import stat
from glob import glob
from config_reader import get_downloads_path, get_rosters_path

def force_remove_readonly(func, path, exc):
    """Remove read-only files and directories"""
    if os.path.exists(path):
        os.chmod(path, stat.S_IWRITE)
        func(path)

def safe_remove_file(file_path, max_retries=3):
    """Safely remove a file with retry logic"""
    for attempt in range(max_retries):
        try:
            if os.path.exists(file_path):
                # Try to make file writable first
                os.chmod(file_path, stat.S_IWRITE)
                os.remove(file_path)
                return True
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(0.5)  # Wait before retry
                continue
            return False
    return False

def safe_remove_tree(folder_path, max_retries=3):
    """Safely remove a directory tree with retry logic"""
    for attempt in range(max_retries):
        try:
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path, onerror=force_remove_readonly)
                return True
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(0.5)  # Wait before retry
                continue
            return False
    return False

def main():
    if len(sys.argv) != 3:
        print(json.dumps({
            "success": False,
            "error": "Usage: python cleanup_data_cli.py <drive> <className>"
        }))
        sys.exit(1)
    
    drive = sys.argv[1]
    class_name = sys.argv[2]
    
    try:
        logs = []
        logs.append(f"🗑️ Starting cleanup for {class_name} on {drive}: drive")
        
        # Get configured paths
        downloads_path = get_downloads_path()
        rosters_path = get_rosters_path()
        
        # Look for class folder in Rosters etc
        class_folders = []
        if os.path.exists(rosters_path):
            for folder in os.listdir(rosters_path):
                if class_name in folder:
                    class_folders.append(os.path.join(rosters_path, folder))
        
        # Clean up Canvas ZIP files in Downloads
        zip_files = glob(os.path.join(downloads_path, "*Canvas*.zip"))
        zip_files.extend(glob(os.path.join(downloads_path, "*canvas*.zip")))
        
        deleted_zips = 0
        for zip_file in zip_files:
            if safe_remove_file(zip_file):
                logs.append(f"🗑️ Deleted ZIP: {os.path.basename(zip_file)}")
                deleted_zips += 1
            else:
                logs.append(f"⚠️ Could not delete {os.path.basename(zip_file)}: Access denied or file in use")
        
        # Clean up grade processing folders
        deleted_folders = 0
        for class_folder in class_folders:
            grade_processing_folder = os.path.join(class_folder, "Grade Processing")
            if os.path.exists(grade_processing_folder):
                if safe_remove_tree(grade_processing_folder):
                    logs.append(f"🗑️ Deleted folder: Grade Processing")
                    deleted_folders += 1
                else:
                    logs.append(f"⚠️ Could not delete Grade Processing folder: Access denied or files in use")
        
        if deleted_zips == 0 and deleted_folders == 0:
            logs.append("ℹ️ No files or folders found to clean up")
        
        logs.append(f"✅ Cleanup completed - {deleted_zips} ZIP files and {deleted_folders} folders removed")
        
        # Output human-readable logs instead of JSON
        for log in logs:
            print(log)
        
        # Output final status
        print(f"SUCCESS: Cleanup completed - {deleted_zips} ZIP files and {deleted_folders} folders removed")
        
    except Exception as e:
        print(f"🗑️ Starting cleanup for {class_name} on {drive}: drive")
        print(f"❌ Error: {str(e)}")
        print(f"ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
