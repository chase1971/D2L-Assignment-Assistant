#!/usr/bin/env python3
"""
CLI script for student statistics operations - called by the Node.js backend
Usage: python statistics_cli.py <operation> <className> [additional args...]

Operations:
  - load <className>: Load all statistics for a class
  - save <className> <json_data>: Save statistics for a class
  - update-notes <className> <studentName> <notes>: Update student notes
  - update-count <className> <studentName> <count>: Update failed submission count
"""

import sys
import os
import json

# Add python-modules to path for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_MODULES_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'python-modules')
sys.path.insert(0, PYTHON_MODULES_DIR)

from student_statistics import (
    load_statistics,
    save_statistics,
    update_student_notes,
    update_failed_submission_count,
    get_all_student_statistics
)


def main():
    if len(sys.argv) < 3:
        print(json.dumps({
            "success": False,
            "error": "Usage: python statistics_cli.py <operation> <className> [args...]"
        }))
        sys.exit(1)
    
    operation = sys.argv[1]
    class_name = sys.argv[2]
    
    try:
        if operation == "load":
            # Load statistics for a class
            stats = load_statistics(class_name)
            students_list = get_all_student_statistics(class_name)
            
            response = {
                "success": True,
                "statistics": stats,
                "students": students_list
            }
            print(json.dumps(response, ensure_ascii=False))
        
        elif operation == "save":
            # Save statistics for a class
            if len(sys.argv) < 4:
                raise ValueError("Missing statistics JSON data")
            
            stats_json = sys.argv[3]
            stats = json.loads(stats_json)
            
            success = save_statistics(class_name, stats)
            
            response = {
                "success": success,
                "message": "Statistics saved successfully" if success else "Failed to save statistics"
            }
            print(json.dumps(response))
        
        elif operation == "update-notes":
            # Update notes for a student
            if len(sys.argv) < 5:
                raise ValueError("Missing student name or notes")
            
            student_name = sys.argv[3]
            notes = sys.argv[4]
            
            success = update_student_notes(class_name, student_name, notes)
            
            response = {
                "success": success,
                "message": "Notes updated successfully" if success else "Failed to update notes"
            }
            print(json.dumps(response))
        
        elif operation == "update-count":
            # Update failed submission count for a student
            if len(sys.argv) < 5:
                raise ValueError("Missing student name or count")
            
            student_name = sys.argv[3]
            count = int(sys.argv[4])
            
            success = update_failed_submission_count(class_name, student_name, count)
            
            response = {
                "success": success,
                "message": "Count updated successfully" if success else "Failed to update count"
            }
            print(json.dumps(response))
        
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    except Exception as e:
        response = {
            "success": False,
            "error": str(e)
        }
        print(json.dumps(response))
        sys.exit(1)


if __name__ == "__main__":
    main()
