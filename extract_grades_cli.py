#!/usr/bin/env python3
"""
Fixed CLI script for grade extraction - based on working minimal version
Usage: python extract_grades_cli_fixed.py <drive> <className>
"""

# Standard library
import json
import os
import sys

# Third-party
import pandas as pd
from typing import Dict, Any, List, Tuple

# Local
from config_reader import get_rosters_path
from extract_grades_simple import extract_grades, create_first_pages_pdf
from name_matching import names_match_fuzzy
from import_file_handler import validate_import_file_early, validate_required_columns
from grading_constants import REQUIRED_COLUMNS_COUNT, END_OF_LINE_COLUMN_INDEX, CONFIDENCE_HIGH, CONFIDENCE_MEDIUM
from file_utils import open_file_with_default_app
from grading_processor import format_error_message


def _validate_import_file_structure(df: pd.DataFrame) -> Tuple[pd.DataFrame, int, str]:
    """
    Validate import file structure, ensure End-of-Line Indicator exists, and find quiz column.
    
    Args:
        df: DataFrame to validate
    
    Returns:
        Tuple of (validated_df, eol_index, quiz_column_name)
    
    Raises:
        Exception: If required columns are missing
    """
    # Validate required columns
    is_valid, missing_columns = validate_required_columns(df)
    if not is_valid:
        if len(missing_columns) == 1:
            msg = f"The import file is missing the {missing_columns[0]} column."
        else:
            cols_list = ", ".join(missing_columns[:-1]) + f" and {missing_columns[-1]}"
            msg = f"The import file is missing the {cols_list} columns."
        
        raise Exception(
            f"❌ {msg}\n\n"
            "Please download a fresh import file from D2L that includes all required columns:\n"
            "OrgDefinedId, Username, First Name, Last Name, and Email."
        )
    
    # Find End-of-Line Indicator column
    eol_index = None
    for i, col in enumerate(df.columns):
        col_lower = str(col).lower()
        if 'end' in col_lower and 'line' in col_lower:
            eol_index = i
            break
    
    # If End-of-Line Indicator not found, add it
    if eol_index is None:
        df = df.iloc[:, :REQUIRED_COLUMNS_COUNT].copy()
        df['End-of-Line Indicator'] = '#'
        eol_index = END_OF_LINE_COLUMN_INDEX
    
    # Clean up - delete ALL columns to the right of End-of-Line Indicator
    if eol_index < len(df.columns) - 1:
        columns_to_keep = list(df.columns[:eol_index + 1])
        df = df[columns_to_keep].copy()
    
    # Find quiz/grade column (the one just before End-of-Line Indicator)
    grade_columns = [col for col in df.columns if 'Points Grade' in col or 'Quiz' in col]
    if grade_columns:
        quiz_column = grade_columns[-1]  # Use the last/most recent grade column
    else:
        # Use column before End-of-Line Indicator
        quiz_column = df.columns[eol_index - 1] if eol_index > 0 else df.columns[-1]
    
    return df, eol_index, quiz_column


def _match_grades_to_roster(
    grades_result: Dict[str, Any],
    df: pd.DataFrame,
    csv_name_map: Dict[str, int],
    quiz_column: str
) -> Tuple[int, List[str], List[str], List[Dict], List[int]]:
    """
    Match extracted grades to roster students.
    
    Args:
        grades_result: Dict mapping student names to grade info
        df: DataFrame with roster data
        csv_name_map: Dict mapping full names to DataFrame indices
        quiz_column: Name of the quiz/grade column to update
    
    Returns:
        Tuple of (updated_count, matching_errors, fuzzy_matches, skipped_students, verify_rows)
    """
    updated_count = 0
    matching_errors = []
    fuzzy_matches = []
    skipped_students = []
    verify_rows = []
    
    for student_name, grade_info in grades_result.items():
        # Extract grade and confidence
        if isinstance(grade_info, dict):
            grade = grade_info.get('grade', '').strip()
            grade_raw = grade_info.get('grade_raw', '').strip()
            confidence = grade_info.get('confidence', 0)
            
            # If processed grade is "No grade found", use raw OCR text instead
            if grade == "No grade found" and grade_raw:
                grade = grade_raw
        else:
            grade = str(grade_info).strip()
            confidence = 0

        # If no grade found, leave empty
        if not grade or grade == "No grade found":
            grade = ""

        # Try exact matching first
        name_parts = student_name.split()
        matched = False
        matched_idx = None
        is_fuzzy_match = False
        
        if len(name_parts) >= 2:
            first_name = name_parts[0].lower()
            last_name = ' '.join(name_parts[1:]).lower()
            mask = (df['First Name'].str.lower().str.contains(first_name, na=False)) & \
                   (df['Last Name'].str.lower().str.contains(last_name, na=False))

            if mask.any():
                matched = True
                matched_idx = mask.idxmax() if mask.any() else None
                is_fuzzy_match = False
        
        # If exact match failed, try fuzzy matching
        if not matched:
            student_name_lower = student_name.lower().strip()
            best_match = None
            best_match_idx = None
            best_similarity = 0
            
            # Try matching against CSV names
            for csv_name, idx in csv_name_map.items():
                # Strategy 1: Full name fuzzy match
                if names_match_fuzzy(student_name_lower, csv_name, threshold=CONFIDENCE_HIGH):
                    words1 = set(student_name_lower.split())
                    words2 = set(csv_name.split())
                    similarity = len(words1 & words2) / max(len(words1), len(words2)) if words1 or words2 else 0
                    
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = csv_name
                        best_match_idx = idx
                
                # Strategy 2: First name matches, last name matches (ignoring middle)
                if len(name_parts) >= 2:
                    csv_parts = csv_name.split()
                    if len(csv_parts) >= 2:
                        if name_parts[0].lower() == csv_parts[0].lower() and name_parts[-1].lower() == csv_parts[-1].lower():
                            similarity = 0.95  # High similarity for first+last match
                            if similarity > best_similarity:
                                best_similarity = similarity
                                best_match = csv_name
                                best_match_idx = idx
            
            if best_match and best_match_idx is not None:
                matched = True
                matched_idx = best_match_idx
                is_fuzzy_match = True
                fuzzy_matches.append(f"{student_name} → matched to {best_match} (fuzzy match - needs verification)")

        if matched and matched_idx is not None:
            # Write the OCR's grade text
            df.at[matched_idx, quiz_column] = grade

            # Mark "Verify" for low confidence OR fuzzy matches
            row_needs_verify = False
            if confidence < CONFIDENCE_HIGH:
                row_needs_verify = True
                grade_display = grade if grade else "(no grade found)"
                # Note: This will be collected as low_confidence_students in main()
                matching_errors.append(f"{student_name}: {grade_display} (low confidence – needs verification)")
            elif is_fuzzy_match:
                row_needs_verify = True
            
            if row_needs_verify:
                verify_rows.append(matched_idx)
            
            updated_count += 1
        else:
            matching_errors.append(f"❌ Could not match: {student_name} (grade: {grade if grade else 'N/A'})")
            skipped_students.append({
                "name": student_name,
                "grade": grade,
                "confidence": confidence,
                "reason": "Could not match to roster"
            })
    
    return updated_count, matching_errors, fuzzy_matches, skipped_students, verify_rows


def _update_csv_with_grades(
    df: pd.DataFrame,
    import_file_path: str,
    eol_index: int,
    verify_rows: List[int]
) -> None:
    """
    Update CSV with verify column if needed and save.
    
    Args:
        df: DataFrame to update
        import_file_path: Path to save CSV
        eol_index: Index of End-of-Line Indicator column
        verify_rows: List of row indices that need "Verify" flag
    """
    # If any rows need verification, add the Verify column AFTER End-of-Line Indicator
    if verify_rows:
        verify_col_placeholder = '_verify_temp_'
        df[verify_col_placeholder] = ''
        
        # Mark the rows that need verification
        for row_idx in verify_rows:
            df.at[row_idx, verify_col_placeholder] = 'Verify'
        
        # Rename the column to empty string
        df.rename(columns={verify_col_placeholder: ''}, inplace=True)
    
    # Save updated CSV
    df.to_csv(import_file_path, index=False)


def _format_extraction_results(
    grades_result: Dict[str, Any],
    student_grades: List[Dict],
    extraction_errors: List[str],
    low_confidence_students: List[str],
    skipped_students: List[Dict]
) -> None:
    """
    Format and print extraction results to stdout.
    
    Args:
        grades_result: Dict mapping student names to grade info
        student_grades: List of student grade dicts with confidence
        extraction_errors: List of error messages
        low_confidence_students: List of low confidence student messages
        skipped_students: List of skipped student dicts
    """
    # Print logs directly to stdout so they show in the frontend
    print("🔬 Starting grade extraction...")
    print("")
    
    # Show all extracted grades with confidence levels
    if student_grades:
        print("📋 EXTRACTED GRADES:")
        for i, sg in enumerate(student_grades, 1):
            conf = sg['confidence']
            conf_indicator = "✅" if conf >= CONFIDENCE_HIGH else "⚠️" if conf >= CONFIDENCE_MEDIUM else "❌"
            print(f"   {i:2d}. {sg['name']}: {sg['grade']} {conf_indicator} (confidence: {conf:.2f})")
    elif grades_result:
        # Fallback: show from grades_result if student_grades wasn't populated
        print("📋 EXTRACTED GRADES:")
        for i, (name, grade_info) in enumerate(grades_result.items(), 1):
            if isinstance(grade_info, dict):
                grade = grade_info.get('grade', '')
                conf = grade_info.get('confidence', 0)
            else:
                grade = str(grade_info)
                conf = 0
            conf_indicator = "✅" if conf >= CONFIDENCE_HIGH else "⚠️" if conf >= CONFIDENCE_MEDIUM else "❌"
            print(f"   {i:2d}. {name}: {grade} {conf_indicator} (confidence: {conf:.2f})")
    
    print("")
    print(f"📊 Processed {len(grades_result) if grades_result else 0} students")
    
    # Collect all errors and warnings for display at the end
    all_issues = []
    
    # Show low confidence students
    if low_confidence_students:
        for student in low_confidence_students:
            all_issues.append(("WARNING", f"⚠️ {student}"))
    
    # Show fuzzy matches (these are warnings but still successful matches)
    fuzzy_warnings = [err for err in extraction_errors if "fuzzy match" in err]
    if fuzzy_warnings:
        for warning in fuzzy_warnings:
            all_issues.append(("WARNING", f"⚠️ {warning}"))
    
    # Show actual errors (unmatched students)
    actual_errors = [err for err in extraction_errors if "fuzzy match" not in err]
    if actual_errors:
        for error in actual_errors:
            all_issues.append(("ERROR", error))
    
    # Add skipped students (couldn't match to roster)
    if skipped_students:
        for skipped in skipped_students:
            grade_display = skipped['grade'] if skipped['grade'] and skipped['grade'] != "No grade found" else "(no grade found)"
            conf_info = f", confidence: {skipped['confidence']:.2f}" if skipped['confidence'] > 0 else ""
            all_issues.append(("ERROR", f"{skipped['name']}: {grade_display}{conf_info} - {skipped['reason']}"))
    
    # Check for low confidence in extracted grades (only if not already reported)
    if grades_result:
        for name, grade_info in grades_result.items():
            if isinstance(grade_info, dict):
                conf = grade_info.get('confidence', 1.0)
                grade = grade_info.get('grade', '')
                if conf < CONFIDENCE_HIGH:
                    # Check if already in low_confidence_students or skipped_students
                    already_reported = any(name in issue[1] for issue in all_issues)
                    if not already_reported:
                        grade_display = grade if grade and grade != "No grade found" else "(no grade found)"
                        all_issues.append(("WARNING", f"⚠️ {name}: {grade_display} (low confidence: {conf:.2f} – needs verification)"))
    
    print("")
    print("✅ Grade extraction complete!")
    
    # Display errors and warnings at the end
    if all_issues:
        print("")
        print("⚠️ ISSUES FOUND (Please Review):")
        for issue_type, issue_msg in all_issues:
            # Remove any existing error/warning symbols to avoid duplicates
            clean_msg = issue_msg.replace("❌ ", "").replace("⚠️ ", "").strip()
            if issue_type == "ERROR":
                print(f"   ❌ {clean_msg}")
            else:
                print(f"   ⚠️ {clean_msg}")


def main() -> None:
    """
    Main entry point for grade extraction CLI.
    
    Workflow:
    1. Validates class folder and import file
    2. Finds most recent combined PDF
    3. Extracts grades using OCR
    4. Matches grades to roster students
    5. Updates Import File.csv with grades
    6. Opens Excel and first pages PDF for review
    
    Usage:
        python extract_grades_cli.py <drive> <className>
    
    Output:
        Prints extraction results to stdout, JSON error responses to stdout on failure
    """
    if len(sys.argv) != 3:
        print(json.dumps({
            "success": False,
            "error": "Usage: python extract_grades_cli_fixed.py <drive> <className>"
        }))
        sys.exit(1)
    
    drive = sys.argv[1]
    class_name = sys.argv[2]
    
    try:
        # Get configured rosters path
        rosters_path = get_rosters_path()
        class_folders = [f for f in os.listdir(rosters_path) if class_name in f]
        
        if not class_folders:
            raise Exception("Class folder not found")
        
        class_folder = os.path.join(rosters_path, class_folders[0])
        
        # Validate import file BEFORE starting extraction
        is_valid, error_msg = validate_import_file_early(class_folder)
        if not is_valid:
            response = {
                "success": False,
                "error": error_msg,
                "logs": ["🔬 Starting grade extraction...", "", error_msg]
            }
            print(json.dumps(response))
            sys.exit(1)
        
        # Find the most recent "grade processing [Assignment]" folder
        import re
        pattern = re.compile(r'^grade processing (.+)$', re.IGNORECASE)
        processing_folders = []
        
        for folder_name in os.listdir(class_folder):
            folder_path = os.path.join(class_folder, folder_name)
            if os.path.isdir(folder_path):
                match = pattern.match(folder_name)
                if match:
                    processing_folders.append(folder_path)
        
        if not processing_folders:
            raise Exception("No grade processing folders found for this class")
        
        # Sort by modification time (newest first) and use the most recent
        processing_folders.sort(key=lambda f: os.path.getmtime(f), reverse=True)
        grade_processing_folder = processing_folders[0]
        pdfs_folder = os.path.join(grade_processing_folder, "PDFs")
        
        # Find the most recent PDF in the PDFs folder (assignment-named PDFs)
        combined_pdf_path = None
        if os.path.exists(pdfs_folder):
            pdf_files = [f for f in os.listdir(pdfs_folder) if f.endswith('.pdf') and 'combined PDF' in f]
            if pdf_files:
                # Sort by modification time (newest first)
                pdf_files.sort(key=lambda f: os.path.getmtime(os.path.join(pdfs_folder, f)), reverse=True)
                combined_pdf_path = os.path.join(pdfs_folder, pdf_files[0])
        
        if not combined_pdf_path or not os.path.exists(combined_pdf_path):
            raise Exception("Combined PDF not found")
        
        # Close any open instances of Excel and PDF viewers to avoid file locking
        try:
            import subprocess
            # Kill Excel processes
            subprocess.run(["taskkill", "/F", "/IM", "EXCEL.EXE"], 
                          capture_output=True, text=True)
            
            # Kill PDF viewers (common ones)
            pdf_viewers = ["AcroRd32.exe", "Acrobat.exe", "PDFXCview.exe", "SumatraPDF.exe", "FoxitReader.exe"]
            for viewer in pdf_viewers:
                subprocess.run(["taskkill", "/F", "/IM", viewer], 
                              capture_output=True, text=True)
        except Exception:
            pass  # Silently fail - not critical
        
        # Extract grades - collect all logs
        all_logs = []
        student_grades = []  # Track all students with their grades and confidence
        
        def log_callback(message):
            # Collect all log messages
            all_logs.append(message)
            # Also track student grades as they're extracted
            if "📊 Grade:" in message:
                # Parse: "   📊 Grade: XX.X (confidence: 0.XX)"
                try:
                    parts = message.split("Grade:")
                    if len(parts) > 1:
                        grade_part = parts[1].strip()
                        # Extract name from previous log line
                        if len(all_logs) > 0 and "✅ Name:" in all_logs[-2]:
                            name_line = all_logs[-2]
                            name = name_line.split("✅ Name:")[1].strip()
                            # Extract grade and confidence
                            if "confidence:" in grade_part:
                                grade = grade_part.split("(confidence:")[0].strip()
                                conf_str = grade_part.split("confidence:")[1].strip().rstrip(")")
                                try:
                                    confidence = float(conf_str)
                                    student_grades.append({
                                        "name": name,
                                        "grade": grade,
                                        "confidence": confidence
                                    })
                                except Exception:
                                    pass
                except Exception:
                    pass
        
        grades_result = extract_grades(combined_pdf_path, log_callback)
        
        # Initialize error tracking lists BEFORE first use
        extraction_errors = []
        low_confidence_students = []
        skipped_students = []
        
        if not grades_result:
            extraction_errors.append("❌ No grades were extracted from the PDF")
            grades_result = {}  # Set to empty dict to avoid errors
        
        # Update CSV
        import_file_path = os.path.join(class_folder, "Import File.csv")
        if not os.path.exists(import_file_path):
            extraction_errors.append("❌ Import file not found")
            raise Exception("Import file not found")
        
        df = pd.read_csv(import_file_path)
        
        # Validate and prepare import file structure
        df, eol_index, quiz_column = _validate_import_file_structure(df)
        
        # Build a map of full names from CSV for fuzzy matching
        csv_name_map = {}
        for idx, row in df.iterrows():
            first = str(row['First Name']).strip().lower()
            last = str(row['Last Name']).strip().lower()
            full_name = f"{first} {last}"
            csv_name_map[full_name] = idx
        
        # Match grades to roster
        updated_count, matching_errors, fuzzy_matches, skipped_students, verify_rows = _match_grades_to_roster(
            grades_result, df, csv_name_map, quiz_column
        )
        
        # Collect low confidence students from matching errors
        low_confidence_students = [err for err in matching_errors if "low confidence" in err]
        
        # Add fuzzy matches and matching errors to extraction_errors
        if fuzzy_matches:
            extraction_errors.extend(fuzzy_matches)
        extraction_errors.extend(matching_errors)
        
        # Update CSV with verify column if needed
        _update_csv_with_grades(df, import_file_path, eol_index, verify_rows)
        
        # Open the Excel file and first pages PDF automatically
        try:
            # Open Excel file
            if os.path.exists(import_file_path):
                open_file_with_default_app(import_file_path)
            
            # Also open the first pages PDF if it exists
            first_pages_pdf = os.path.join(grade_processing_folder, "PDFs", "1combinedpdf_GRADES_ONLY.pdf")
            if not os.path.exists(first_pages_pdf):
                # Try to create it if it doesn't exist
                first_pages_pdf = create_first_pages_pdf(combined_pdf_path, lambda msg: None)
            
            if first_pages_pdf and os.path.exists(first_pages_pdf):
                open_file_with_default_app(first_pages_pdf)
        except Exception as e:
            extraction_errors.append(f"⚠️ Could not open files: {str(e)}")
        
        # Format and display results
        _format_extraction_results(
            grades_result, student_grades, extraction_errors, 
            low_confidence_students, skipped_students
        )
        
    except Exception as e:
        # Use standardized error formatting
        friendly_error = format_error_message(e)
        
        error_response = {
            "success": False,
            "error": friendly_error,
            "logs": ["🔬 Starting grade extraction...", "", friendly_error]
        }
        print(json.dumps(error_response))
        sys.exit(1)

if __name__ == "__main__":
    main()
