#!/usr/bin/env python3
"""
ZIP file validation utilities for D2L Assignment Processing
Validates ZIP structure and student name matching
"""

import os
import zipfile
import re
from typing import Tuple, List
import pandas as pd


def validate_zip_structure(zip_path: str) -> Tuple[bool, str]:
    """
    Validate that ZIP file has the correct folder structure.
    Expected format: Student folders named like "ID-ID - Name - Date"
    
    Args:
        zip_path: Path to ZIP file
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        if not os.path.exists(zip_path):
            return False, f"ZIP file not found: {zip_path}"
        
        if not zipfile.is_zipfile(zip_path):
            return False, "File is not a valid ZIP archive"
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            all_files = zip_ref.namelist()
            
            if not all_files:
                return False, "ZIP file is empty"
            
            # Look for student submission folders
            # Pattern: "ID-ID - Name - Date" or just folders with files in them
            student_folders = set()
            pattern = re.compile(r'^([^/]+)/.*')  # Match "folder/anything"
            
            for file_path in all_files:
                match = pattern.match(file_path)
                if match:
                    folder_name = match.group(1)
                    student_folders.add(folder_name)
            
            if not student_folders:
                return False, "ZIP file doesn't contain any student submission folders"
            
            # Check if folders match the expected D2L pattern
            # Pattern: "ID-ID - Name - Date" or "Name - Date"
            d2l_pattern = re.compile(r'^(\d+-\d+\s+-\s+)?[\w\s]+\s+-\s+\w+\s+\d+')
            valid_folders = [f for f in student_folders if d2l_pattern.match(f)]
            
            if not valid_folders:
                return False, (
                    "ZIP file doesn't appear to be a D2L submission export. "
                    "Expected folder names like: '12345-67890 - John Doe - Jan 1, 2024'"
                )
            
            return True, ""
            
    except zipfile.BadZipFile:
        return False, "File is corrupted or not a valid ZIP file"
    except Exception as e:
        return False, f"Error reading ZIP file: {str(e)}"


def validate_student_names_match(zip_path: str, import_df: pd.DataFrame) -> Tuple[bool, str, List[str]]:
    """
    Validate that student names in ZIP match names in Import File.
    
    Args:
        zip_path: Path to ZIP file
        import_df: Import File DataFrame with student data
    
    Returns:
        Tuple of (names_match, error_message, list_of_mismatches)
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            all_files = zip_ref.namelist()
            
            # Extract student folder names
            student_folders = set()
            pattern = re.compile(r'^([^/]+)/.*')
            
            for file_path in all_files:
                match = pattern.match(file_path)
                if match:
                    folder_name = match.group(1)
                    student_folders.add(folder_name)
            
            # Extract student names from folder names
            # Pattern: "ID-ID - First Last - Date"
            zip_names = set()
            name_pattern = re.compile(r'^\d+-\d+\s+-\s+([\w\s]+)\s+-\s+\w+\s+\d+')
            
            for folder in student_folders:
                match = name_pattern.match(folder)
                if match:
                    full_name = match.group(1).strip()
                    # Normalize: convert to "First Last" format
                    zip_names.add(full_name.lower())
            
            # Get names from Import File
            import_names = set()
            for _, row in import_df.iterrows():
                first = str(row.get('First Name', '')).strip()
                last = str(row.get('Last Name', '')).strip()
                if first and last:
                    full_name = f"{first} {last}".lower()
                    import_names.add(full_name)
            
            # Find names in ZIP but not in Import File
            mismatches = []
            for zip_name in zip_names:
                if zip_name not in import_names:
                    mismatches.append(zip_name)
            
            if mismatches:
                return False, (
                    f"Found {len(mismatches)} student(s) in ZIP that don't match Import File. "
                    "This might mean you selected the wrong class or wrong Import File."
                ), mismatches
            
            return True, "", []
            
    except Exception as e:
        return False, f"Error validating student names: {str(e)}", []
