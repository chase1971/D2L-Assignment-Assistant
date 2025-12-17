#!/usr/bin/env python3
"""
Class Manager CLI - Manage class configurations stored in classes.json

Operations:
- list: List all classes
- add: Add a new class
- edit: Edit an existing class
- delete: Delete a class (skips protected classes)
- deleteAll: Delete all non-protected classes

Usage:
    python class_manager_cli.py list
    python class_manager_cli.py add <value> <label> <rosterFolderPath>
    python class_manager_cli.py edit <id> <value> <label> <rosterFolderPath>
    python class_manager_cli.py delete <id>
    python class_manager_cli.py deleteAll
"""

import json
import os
import sys
import uuid
from pathlib import Path

# Path to classes.json
CLASSES_FILE = Path(__file__).parent / "classes.json"

def load_classes():
    """Load classes from JSON file, ensuring protected class always exists"""
    PROTECTED_CLASS = {
        "id": "protected-fm4202",
        "value": "TTH 11-1220 FM 4202",
        "label": "FM 4202 (TTH 11:00-12:20)",
        "rosterFolderPath": "C:\\Users\\chase\\My Drive\\Rosters etc\\TTH 11-1220 FM 4202",
        "isProtected": True
    }
    
    if not CLASSES_FILE.exists():
        # Create default file with protected FM 4202 class
        default_data = {"classes": [PROTECTED_CLASS]}
        save_classes(default_data)
        return default_data
    
    try:
        with open(CLASSES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Ensure protected class exists
        protected_exists = any(cls.get("id") == "protected-fm4202" for cls in data.get("classes", []))
        if not protected_exists:
            data["classes"].insert(0, PROTECTED_CLASS)
            save_classes(data)
        
        return data
    except Exception as e:
        # If file is corrupted, reset with protected class
        default_data = {"classes": [PROTECTED_CLASS]}
        save_classes(default_data)
        return default_data

def save_classes(data):
    """Save classes to JSON file"""
    try:
        with open(CLASSES_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(json.dumps({"success": False, "error": f"Failed to save classes: {str(e)}"}))
        sys.exit(1)

def validate_folder_path(path):
    """Validate that folder path exists"""
    if not path:
        return True  # Allow empty paths for protected classes
    
    # Normalize path separators
    normalized_path = path.replace('/', os.sep).replace('\\', os.sep)
    
    if not os.path.exists(normalized_path):
        return False
    
    if not os.path.isdir(normalized_path):
        return False
    
    return True

def list_classes():
    """List all classes"""
    data = load_classes()
    print(json.dumps({"success": True, "classes": data["classes"]}))

def add_class(value, label, roster_folder_path):
    """Add a new class"""
    # Validate folder path
    if roster_folder_path and not validate_folder_path(roster_folder_path):
        print(json.dumps({"success": False, "error": f"Folder path does not exist: {roster_folder_path}"}))
        sys.exit(1)
    
    data = load_classes()
    
    # Check for duplicate value
    for cls in data["classes"]:
        if cls["value"] == value:
            print(json.dumps({"success": False, "error": f"Class with value '{value}' already exists"}))
            sys.exit(1)
    
    # Generate unique ID
    new_id = str(uuid.uuid4())
    
    # Add new class
    new_class = {
        "id": new_id,
        "value": value,
        "label": label,
        "rosterFolderPath": roster_folder_path,
        "isProtected": False
    }
    
    data["classes"].append(new_class)
    save_classes(data)
    
    print(json.dumps({"success": True, "class": new_class}))

def edit_class(class_id, value, label, roster_folder_path):
    """Edit an existing class"""
    # Validate folder path
    if roster_folder_path and not validate_folder_path(roster_folder_path):
        print(json.dumps({"success": False, "error": f"Folder path does not exist: {roster_folder_path}"}))
        sys.exit(1)
    
    data = load_classes()
    
    # Find class by ID
    class_found = False
    for cls in data["classes"]:
        if cls["id"] == class_id:
            class_found = True
            # Check for duplicate value (excluding current class)
            for other_cls in data["classes"]:
                if other_cls["id"] != class_id and other_cls["value"] == value:
                    print(json.dumps({"success": False, "error": f"Class with value '{value}' already exists"}))
                    sys.exit(1)
            
            # Update class
            cls["value"] = value
            cls["label"] = label
            cls["rosterFolderPath"] = roster_folder_path
            break
    
    if not class_found:
        print(json.dumps({"success": False, "error": f"Class with ID '{class_id}' not found"}))
        sys.exit(1)
    
    save_classes(data)
    print(json.dumps({"success": True}))

def delete_class(class_id):
    """Delete a class (skip if protected)"""
    data = load_classes()
    
    # Find and check if class is protected
    class_to_delete = None
    for cls in data["classes"]:
        if cls["id"] == class_id:
            class_to_delete = cls
            break
    
    if not class_to_delete:
        print(json.dumps({"success": False, "error": f"Class with ID '{class_id}' not found"}))
        sys.exit(1)
    
    if class_to_delete.get("isProtected", False):
        print(json.dumps({"success": False, "error": "Cannot delete protected class"}))
        sys.exit(1)
    
    # Remove class
    data["classes"] = [cls for cls in data["classes"] if cls["id"] != class_id]
    save_classes(data)
    
    print(json.dumps({"success": True}))

def delete_all_classes():
    """Delete all non-protected classes"""
    data = load_classes()
    
    # Keep only protected classes
    protected_classes = [cls for cls in data["classes"] if cls.get("isProtected", False)]
    
    data["classes"] = protected_classes
    save_classes(data)
    
    print(json.dumps({"success": True, "deletedCount": len(data["classes"]) - len(protected_classes)}))

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "No operation specified"}))
        sys.exit(1)
    
    operation = sys.argv[1]
    
    try:
        if operation == "list":
            list_classes()
        
        elif operation == "add":
            if len(sys.argv) != 5:
                print(json.dumps({"success": False, "error": "Usage: add <value> <label> <rosterFolderPath>"}))
                sys.exit(1)
            add_class(sys.argv[2], sys.argv[3], sys.argv[4])
        
        elif operation == "edit":
            if len(sys.argv) != 6:
                print(json.dumps({"success": False, "error": "Usage: edit <id> <value> <label> <rosterFolderPath>"}))
                sys.exit(1)
            edit_class(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
        
        elif operation == "delete":
            if len(sys.argv) != 3:
                print(json.dumps({"success": False, "error": "Usage: delete <id>"}))
                sys.exit(1)
            delete_class(sys.argv[2])
        
        elif operation == "deleteAll":
            delete_all_classes()
        
        else:
            print(json.dumps({"success": False, "error": f"Unknown operation: {operation}"}))
            sys.exit(1)
    
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()

