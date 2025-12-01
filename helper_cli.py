#!/usr/bin/env python3
"""
Helper CLI for getting available classes and ZIP files.

Commands:
    python helper_cli.py list-classes <drive_letter>
    python helper_cli.py find-zips
    python helper_cli.py extract-assignment-name <zip_filename>
    python helper_cli.py open-folder <drive_letter> <class_name>

Output: JSON with results
"""

import sys
import json
import os
from glob import glob
from config_reader import get_downloads_path, get_rosters_path

def list_classes(drive_letter):
    """List available class folders"""
    drive_letter = drive_letter.upper()
    
    # Get configured rosters path
    rosters_path = get_rosters_path()
    
    if not rosters_path or not os.path.exists(rosters_path):
        return {
            "success": False,
            "error": f"Rosters folder not found at {rosters_path}",
            "rosters_path": rosters_path
        }
    
    # Get all folders
    try:
        folders = [f for f in os.listdir(rosters_path) 
                  if os.path.isdir(os.path.join(rosters_path, f))]
        
        # Extract class codes (last 7 characters, e.g., "FM 4103")
        classes = []
        for folder in folders:
            if len(folder) >= 7:
                class_code = folder[-7:].strip()
                # Validate format (2 letters, space, 4 digits)
                parts = class_code.split()
                if len(parts) == 2 and parts[0].isalpha() and parts[1].isdigit():
                    classes.append({
                        "code": class_code,
                        "folder_name": folder
                    })
        
        return {
            "success": True,
            "drive": drive_letter,
            "rosters_path": rosters_path,
            "classes": sorted(classes, key=lambda x: x['code'])
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def find_zips():
    """Find ZIP files in Downloads"""
    downloads_path = get_downloads_path()
    
    if not os.path.exists(downloads_path):
        return {
            "success": False,
            "error": f"Downloads folder not found: {downloads_path}"
        }
    
    try:
        zip_files = glob(os.path.join(downloads_path, "*.zip"))
        
        # Sort by modification time (newest first)
        zip_files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
        
        zips = []
        for zip_path in zip_files:
            basename = os.path.basename(zip_path)
            # Extract assignment name (everything before " Download")
            assignment_name = os.path.splitext(basename)[0].split(" Download")[0].strip()
            
            zips.append({
                "path": zip_path,
                "filename": basename,
                "assignment_name": assignment_name,
                "modified": os.path.getmtime(zip_path)
            })
        
        return {
            "success": True,
            "downloads_path": downloads_path,
            "zips": zips
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def extract_assignment_name(zip_filename):
    """Extract assignment name from ZIP filename"""
    try:
        basename = os.path.basename(zip_filename)
        assignment_name = os.path.splitext(basename)[0].split(" Download")[0].strip()
        
        return {
            "success": True,
            "filename": basename,
            "assignment_name": assignment_name
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def open_folder(drive_letter, class_name):
    """Open the grade processing folder for a class"""
    import subprocess
    import platform
    
    try:
        # Get configured rosters path
        rosters_path = get_rosters_path()
        class_folder = os.path.join(rosters_path, class_name)
        processing_folder = os.path.join(class_folder, "grade processing")
        
        # Determine which folder to open
        if os.path.exists(processing_folder):
            folder_to_open = processing_folder
        elif os.path.exists(class_folder):
            folder_to_open = class_folder
        else:
            return {
                "success": False,
                "error": f"Folder not found: {class_folder}"
            }
        
        # Open the folder
        if platform.system() == "Windows":
            os.startfile(folder_to_open)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", folder_to_open])
        else:  # Linux
            subprocess.run(["xdg-open", folder_to_open])
        
        return {
            "success": True,
            "message": f"Opened folder: {folder_to_open}",
            "folder": folder_to_open
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "success": False,
            "error": "No command specified",
            "usage": "python helper_cli.py <command> [args]",
            "commands": [
                "list-classes <drive_letter>",
                "find-zips",
                "extract-assignment-name <zip_filename>",
                "open-folder <drive_letter> <class_name>"
            ]
        }))
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list-classes":
        if len(sys.argv) != 3:
            result = {
                "success": False,
                "error": "Missing drive letter",
                "usage": "python helper_cli.py list-classes <drive_letter>"
            }
        else:
            result = list_classes(sys.argv[2])
    
    elif command == "find-zips":
        result = find_zips()
    
    elif command == "extract-assignment-name":
        if len(sys.argv) != 3:
            result = {
                "success": False,
                "error": "Missing ZIP filename",
                "usage": "python helper_cli.py extract-assignment-name <zip_filename>"
            }
        else:
            result = extract_assignment_name(sys.argv[2])
    
    elif command == "open-folder":
        if len(sys.argv) != 4:
            result = {
                "success": False,
                "error": "Missing arguments",
                "usage": "python helper_cli.py open-folder <drive_letter> <class_name>"
            }
        else:
            result = open_folder(sys.argv[2], sys.argv[3])
    
    else:
        result = {
            "success": False,
            "error": f"Unknown command: {command}",
            "available_commands": ["list-classes", "find-zips", "extract-assignment-name", "open-folder"]
        }
    
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)

if __name__ == "__main__":
    main()

