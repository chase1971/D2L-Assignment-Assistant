"""
Student Statistics Management Module
Tracks student submission failures and other statistics across assignments
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from config_reader import get_rosters_path


STATISTICS_FILENAME = "student_statistics.json"


def _get_statistics_file_path(class_folder_path: str) -> str:
    """Get the path to the statistics JSON file for a class"""
    return os.path.join(class_folder_path, STATISTICS_FILENAME)


def _find_class_folder(class_folder_name: str) -> Optional[str]:
    """
    Find the class folder by checking multiple possible locations.
    Checks both G:\\ and C:\\ drives.
    
    Args:
        class_folder_name: Name of the class folder (e.g., 'FM 4101 TTH 8-920')
    
    Returns:
        Path to the class folder if found, None otherwise
    """
    # Try configured rosters path first
    rosters_path = get_rosters_path()
    class_folder_path = os.path.join(rosters_path, class_folder_name)
    
    if os.path.exists(class_folder_path):
        return class_folder_path
    
    # Try common locations on different drives
    possible_locations = [
        r"G:\My Drive\Rosters etc",
        r"C:\Rosters",
        r"C:\Users\Public\Rosters"
    ]
    
    for location in possible_locations:
        class_folder_path = os.path.join(location, class_folder_name)
        if os.path.exists(class_folder_path):
            return class_folder_path
    
    return None


def load_statistics(class_folder_name: str) -> Dict[str, Any]:
    """
    Load statistics for a class. Creates empty structure if doesn't exist.
    
    Returns dict with structure:
    {
        "students": {
            "Student Name": {
                "failed_submissions": 5,
                "assignments": {
                    "Quiz 1": {"submitted": false, "date": "2024-01-15"},
                    "Quiz 2": {"submitted": true, "date": "2024-01-20"}
                },
                "notes": "Optional notes about this student"
            }
        },
        "last_updated": "2024-01-20T15:30:00"
    }
    """
    class_folder_path = _find_class_folder(class_folder_name)
    if not class_folder_path:
        return {"students": {}, "last_updated": None}
    
    stats_file = _get_statistics_file_path(class_folder_path)
    
    if not os.path.exists(stats_file):
        return {"students": {}, "last_updated": None}
    
    try:
        with open(stats_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading statistics: {e}")
        return {"students": {}, "last_updated": None}


def save_statistics(class_folder_name: str, statistics: Dict[str, Any]) -> bool:
    """
    Save statistics for a class.
    
    Args:
        class_folder_name: Name of the class folder
        statistics: Statistics dict to save
    
    Returns:
        True if successful, False otherwise
    """
    class_folder_path = _find_class_folder(class_folder_name)
    if not class_folder_path:
        print(f"Could not find class folder: {class_folder_name}")
        return False
    
    stats_file = _get_statistics_file_path(class_folder_path)
    
    # Update last_updated timestamp
    statistics["last_updated"] = datetime.now().isoformat()
    
    try:
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(statistics, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving statistics: {e}")
        return False


def record_assignment_submissions(
    class_folder_name: str,
    assignment_name: str,
    students_submitted: List[str],
    students_not_submitted: List[str]
) -> bool:
    """
    Record which students did/didn't submit an assignment.
    Updates statistics automatically.
    
    Args:
        class_folder_name: Name of the class folder
        assignment_name: Name of the assignment
        students_submitted: List of student names who submitted
        students_not_submitted: List of student names who didn't submit
    
    Returns:
        True if successful, False otherwise
    """
    statistics = load_statistics(class_folder_name)
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Ensure students dict exists
    if "students" not in statistics:
        statistics["students"] = {}
    
    # Record submissions
    for student_name in students_submitted:
        if student_name not in statistics["students"]:
            statistics["students"][student_name] = {
                "failed_submissions": 0,
                "assignments": {},
                "notes": ""
            }
        
        statistics["students"][student_name]["assignments"][assignment_name] = {
            "submitted": True,
            "date": current_date
        }
    
    # Record non-submissions
    for student_name in students_not_submitted:
        if student_name not in statistics["students"]:
            statistics["students"][student_name] = {
                "failed_submissions": 0,
                "assignments": {},
                "notes": ""
            }
        
        statistics["students"][student_name]["assignments"][assignment_name] = {
            "submitted": False,
            "date": current_date
        }
        
        # Increment failed submission count
        statistics["students"][student_name]["failed_submissions"] = \
            statistics["students"][student_name].get("failed_submissions", 0) + 1
    
    return save_statistics(class_folder_name, statistics)


def update_student_notes(
    class_folder_name: str,
    student_name: str,
    notes: str
) -> bool:
    """
    Update notes for a specific student.
    
    Args:
        class_folder_name: Name of the class folder
        student_name: Name of the student
        notes: Notes text
    
    Returns:
        True if successful, False otherwise
    """
    statistics = load_statistics(class_folder_name)
    
    if "students" not in statistics:
        statistics["students"] = {}
    
    if student_name not in statistics["students"]:
        statistics["students"][student_name] = {
            "failed_submissions": 0,
            "assignments": {},
            "notes": ""
        }
    
    statistics["students"][student_name]["notes"] = notes
    
    return save_statistics(class_folder_name, statistics)


def update_failed_submission_count(
    class_folder_name: str,
    student_name: str,
    count: int
) -> bool:
    """
    Manually update the failed submission count for a student.
    
    Args:
        class_folder_name: Name of the class folder
        student_name: Name of the student
        count: New failed submission count
    
    Returns:
        True if successful, False otherwise
    """
    statistics = load_statistics(class_folder_name)
    
    if "students" not in statistics:
        statistics["students"] = {}
    
    if student_name not in statistics["students"]:
        statistics["students"][student_name] = {
            "failed_submissions": count,
            "assignments": {},
            "notes": ""
        }
    else:
        statistics["students"][student_name]["failed_submissions"] = count
    
    return save_statistics(class_folder_name, statistics)


def get_student_statistics(class_folder_name: str, student_name: str) -> Optional[Dict[str, Any]]:
    """
    Get statistics for a specific student.
    
    Returns:
        Student statistics dict or None if not found
    """
    statistics = load_statistics(class_folder_name)
    return statistics.get("students", {}).get(student_name)


def get_all_student_statistics(class_folder_name: str) -> List[Dict[str, Any]]:
    """
    Get statistics for all students in a class, formatted for display.
    
    Returns:
        List of student statistics with name included
    """
    statistics = load_statistics(class_folder_name)
    students = statistics.get("students", {})
    
    result = []
    for student_name, student_data in students.items():
        result.append({
            "name": student_name,
            "failed_submissions": student_data.get("failed_submissions", 0),
            "assignments": student_data.get("assignments", {}),
            "notes": student_data.get("notes", "")
        })
    
    # Sort by failed_submissions (highest first), then by name
    result.sort(key=lambda x: (-x["failed_submissions"], x["name"]))
    
    return result
