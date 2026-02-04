#!/usr/bin/env python3
"""
Fixed CLI script for grade extraction - based on working minimal version
Usage: python extract_grades_cli_fixed.py <drive> <className>
"""

import sys
import os

# Add python-modules to path for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_MODULES_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'python-modules')
sys.path.insert(0, PYTHON_MODULES_DIR)

# Standard library
import json

# Third-party
import pandas as pd
from typing import Dict, Any, List, Tuple

# Local
from config_reader import get_rosters_path
from extract_grades_simple import extract_grades, create_first_pages_pdf
from name_matching import names_match_fuzzy
from import_file_handler import validate_import_file_early, validate_required_columns, _find_import_file
from grading_constants import REQUIRED_COLUMNS_COUNT, END_OF_LINE_COLUMN_INDEX, CONFIDENCE_HIGH, CONFIDENCE_MEDIUM
from file_utils import open_file_with_default_app
from grading_helpers import format_error_message
from user_messages import log, log_raw


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
    skipped_students: List[Dict],
    roster_students: List[str] = None
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
    # Organize issues into four categories, avoiding duplicates
    no_grade_found = []  # Students with no grade found
    low_confidence = []  # Students with low confidence grades
    name_matching = []    # Fuzzy name matches
    no_submissions = []   # Students with no submissions at all
    
    # Track which students we've already added to avoid duplicates
    seen_students = set()
    
    # Helper to extract student name from various message formats
    def extract_student_name(msg):
        """Extract student name from message string"""
        # Handle formats like "Name: grade (message)" or "Name → matched to..."
        if " → " in msg:
            return msg.split(" → ")[0].strip()
        if ": " in msg:
            return msg.split(": ")[0].strip()
        return msg.strip()
    
    # Process fuzzy matches first (name matching issues) - these are separate from other issues
    fuzzy_warnings = [err for err in extraction_errors if "fuzzy match" in err]
    for warning in fuzzy_warnings:
        clean_warning = warning.replace("⚠️ ", "").replace("❌ ", "").strip()
        student_name = extract_student_name(clean_warning)
        if student_name not in seen_students:
            name_matching.append(clean_warning)
            seen_students.add(student_name)
    
    # Process all grades from grades_result - this is the primary source
    if grades_result:
        for name, grade_info in grades_result.items():
            # Skip if already in name matching (fuzzy matches take priority)
            if name in [extract_student_name(nm) for nm in name_matching]:
                continue
                
            if isinstance(grade_info, dict):
                conf = grade_info.get('confidence', 1.0)
                grade = grade_info.get('grade', '')
                grade_str = str(grade) if grade else ''
                
                # Check if no grade found
                if not grade or grade == "No grade found" or grade_str.strip() == "":
                    if name not in seen_students:
                        no_grade_found.append(name)
                        seen_students.add(name)
                # Check if low confidence (but has a grade)
                elif conf < CONFIDENCE_HIGH:
                    if name not in seen_students:
                        low_confidence.append(f"{name}: {grade}")
                        seen_students.add(name)
    
    # Process low_confidence_students list (from matching phase) - these are pre-formatted messages
    # Format: "Name: grade (low confidence – needs verification)"
    # Note: These may not have confidence values, so we'll try to get them from grades_result
    if low_confidence_students:
        for student_msg in low_confidence_students:
            clean_msg = student_msg.replace("⚠️ ", "").replace("❌ ", "").strip()
            student_name = extract_student_name(clean_msg)
            
            # Skip if already categorized or in name matching
            if student_name in seen_students or student_name in [extract_student_name(nm) for nm in name_matching]:
                continue
            
            # Check if it's a "no grade found" message
            if "(no grade found)" in clean_msg.lower():
                no_grade_found.append(student_name)
                seen_students.add(student_name)
            # Otherwise it's a low confidence message
            elif "low confidence" in clean_msg.lower():
                # Try to get confidence from grades_result if available
                conf_val = None
                if grades_result and student_name in grades_result:
                    grade_info = grades_result[student_name]
                    if isinstance(grade_info, dict):
                        conf_val = grade_info.get('confidence', None)
                
                # Extract grade from message format: "Name: grade (low confidence...)"
                if ": " in clean_msg:
                    grade_part = clean_msg.split(": ", 1)[1].split("(")[0].strip()
                    # Remove confidence from display - just show name and grade
                    low_confidence.append(f"{student_name}: {grade_part}")
                else:
                    # Remove confidence from display if present
                    import re
                    clean_display = re.sub(r'\s*\(confidence[:\s]+[\d.]+\)', '', clean_msg)
                    low_confidence.append(clean_display)
                seen_students.add(student_name)
    
    # Process skipped students (couldn't match to roster)
    if skipped_students:
        for skipped in skipped_students:
            name = skipped['name']
            # Skip if already categorized
            if name in seen_students or name in [extract_student_name(nm) for nm in name_matching]:
                continue
                
            grade_val = skipped.get('grade', '')
            conf = skipped.get('confidence', 0)
            
            if not grade_val or grade_val == "No grade found":
                no_grade_found.append(name)
            elif conf < CONFIDENCE_HIGH:
                grade_display = grade_val if grade_val else "(no grade found)"
                low_confidence.append(f"{name}: {grade_display}")
            seen_students.add(name)
    
    # Process other extraction errors (non-fuzzy)
    actual_errors = [err for err in extraction_errors if "fuzzy match" not in err]
    for error in actual_errors:
        clean_error = error.replace("⚠️ ", "").replace("❌ ", "").strip()
        student_name = extract_student_name(clean_error)
        if student_name not in seen_students and student_name not in [extract_student_name(nm) for nm in name_matching]:
            if "(no grade found)" in clean_error.lower() or "no grade" in clean_error.lower():
                no_grade_found.append(student_name)
                seen_students.add(student_name)
    
    # Find students with no submissions (in roster but not in grades_result)
    if roster_students:
        # Get all students who have grades extracted (from grades_result keys)
        students_with_grades = set(grades_result.keys() if grades_result else [])
        
        # Also include students from skipped_students (they tried to submit but couldn't match)
        for skipped in skipped_students:
            students_with_grades.add(skipped['name'])
        
        # Find roster students who are not in the extracted grades
        for roster_student in roster_students:
            # Normalize names for comparison (case-insensitive)
            roster_lower = roster_student.lower().strip()
            found = False
            
            # Check if this roster student appears in any extracted grades
            for extracted_name in students_with_grades:
                if extracted_name.lower().strip() == roster_lower:
                    found = True
                    break
            
            # Also check fuzzy matches
            if not found:
                for fuzzy_match in name_matching:
                    fuzzy_name = extract_student_name(fuzzy_match).lower().strip()
                    if fuzzy_name == roster_lower:
                        found = True
                        break
            
            # If not found in any category, they have no submission
            if not found and roster_student not in seen_students:
                no_submissions.append(roster_student)
    
    # Display issues organized by category
    has_issues = no_grade_found or low_confidence or name_matching or no_submissions
    if has_issues:
        log("GRADES_ISSUES_HEADER")
        
        # Category 1: No Grade Found
        if no_grade_found:
            log("GRADES_NO_GRADE")
            for student in sorted(set(no_grade_found)):
                log_raw(f"  {student}", "ERROR")
        
        # Category 2: Low Confidence
        if low_confidence:
            log("GRADES_LOW_CONFIDENCE")
            for item in sorted(set(low_confidence)):
                log_raw(f"  {item}", "WARNING")
        
        # Category 3: Name Matching Issues
        if name_matching:
            log("GRADES_NAME_ISSUES")
            for item in sorted(set(name_matching)):
                log_raw(f"  {item}", "WARNING")
        
        # Category 4: No Submissions
        if no_submissions:
            log("GRADES_NO_SUBMISSIONS")
            for student in sorted(set(no_submissions)):
                log_raw(f"  {student}", "ERROR")
    
    # Print completion message
    log("GRADES_SUCCESS")


def main() -> None:
    """
    Main entry point for grade extraction CLI.
    
    Workflow:
    1. Validates class folder and import file
    2. Finds most recent combined PDF (or uses provided pdfPath)
    3. Extracts grades using OCR
    4. Matches grades to roster students
    5. Updates Import File.csv with grades
    6. Opens Excel and first pages PDF for review
    
    Usage:
        python extract_grades_cli.py <drive> <className> [pdfPath]
    
    Output:
        Prints extraction results to stdout, JSON error responses to stdout on failure
    """
    if len(sys.argv) < 3:
        print(json.dumps({
            "success": False,
            "error": "Usage: python extract_grades_cli_fixed.py <drive> <className> [pdfPath]"
        }))
        sys.exit(1)
    
    drive = sys.argv[1]
    class_name = sys.argv[2]
    pdf_path_override = sys.argv[3] if len(sys.argv) > 3 else None
    
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
        
        # Print starting message after validation passes
        log("GRADES_STARTING")
        
        # Use provided PDF path if available, otherwise find the most recent one
        combined_pdf_path = None
        grade_processing_folder = None
        assignment_name_from_pdf = None
        
        if pdf_path_override and os.path.exists(pdf_path_override):
            # Use the provided PDF path
            combined_pdf_path = pdf_path_override
            log(f"📄 Using selected PDF: {os.path.basename(combined_pdf_path)}")
            
            # Try to find the grade processing folder from the PDF path
            # PDF should be in: .../grade processing [assignment]/PDFs/[filename].pdf
            pdf_dir = os.path.dirname(combined_pdf_path)
            if os.path.basename(pdf_dir) == "PDFs":
                grade_processing_folder = os.path.dirname(pdf_dir)
            else:
                # PDF might be directly in grade processing folder
                grade_processing_folder = pdf_dir
            
            # Extract assignment name from the grade processing folder name
            # Just extract everything after "grade processing " and before/without the class code
            folder_name = os.path.basename(grade_processing_folder)
            import re
            
            # Remove "grade processing " prefix
            if folder_name.lower().startswith('grade processing '):
                assignment_with_code = folder_name[len('grade processing '):]
                # Remove class code at the beginning if present (e.g., "H 8-920 " or "TTH 11-1220 ")
                assignment_name_from_pdf = re.sub(r'^[A-Z]+\s+\d+-\d+\s+', '', assignment_with_code, flags=re.IGNORECASE).strip()
            else:
                # Fallback: extract from PDF filename
                pdf_basename = os.path.basename(combined_pdf_path)
                assignment_name_from_pdf = pdf_basename.replace(' combined PDF.pdf', '').replace('combined PDF.pdf', '')
                # Remove class code at the end
                assignment_name_from_pdf = re.sub(r'\s+[A-Z]+\s+\d+-\d+\s*$', '', assignment_name_from_pdf, flags=re.IGNORECASE).strip()
        else:
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
            # Exclude _GRADES_ONLY PDFs since those are generated versions
            if os.path.exists(pdfs_folder):
                pdf_files = [f for f in os.listdir(pdfs_folder) 
                            if f.endswith('.pdf') 
                            and 'combined PDF' in f 
                            and '_GRADES_ONLY' not in f]
                if pdf_files:
                    # Sort by modification time (newest first)
                    pdf_files.sort(key=lambda f: os.path.getmtime(os.path.join(pdfs_folder, f)), reverse=True)
                    combined_pdf_path = os.path.join(pdfs_folder, pdf_files[0])
                    # Extract assignment name from PDF filename
                    assignment_name_from_pdf = pdf_files[0].replace('.pdf', '').replace(' combined PDF', '').strip()
            
            if not combined_pdf_path or not os.path.exists(combined_pdf_path):
                log("GRADES_PDF_NOT_FOUND")
                raise Exception("Combined PDF not found")
        
        # Load CSV BEFORE extraction so we can pass roster names for fuzzy matching
        # Check for both "Import File.csv" and "import.csv"
        import_file_path = _find_import_file(class_folder)
        if not import_file_path or not os.path.exists(import_file_path):
            log("GRADES_IMPORT_NOT_FOUND")
            raise Exception("Import file not found. Please ensure 'Import File.csv' or 'import.csv' exists in the class folder.")
        
        df = pd.read_csv(import_file_path)
        
        # Validate and prepare import file structure
        df, eol_index, quiz_column = _validate_import_file_structure(df)
        
        # Build roster names list for fuzzy matching during extraction
        roster_names = []
        csv_name_map = {}
        for idx, row in df.iterrows():
            first = str(row['First Name']).strip()
            last = str(row['Last Name']).strip()
            full_name = f"{first} {last}"
            full_name_lower = f"{first.lower()} {last.lower()}"
            roster_names.append(full_name)  # Keep original case for display
            csv_name_map[full_name_lower] = idx
        
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
            # Route messages to our logging system
            # Debug filtering is now handled centrally in logger.py via D2L_DEBUG flag
            if message:
                log_raw(message)
            
            # Collect all log messages for tracking
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
        
        # Create debug images folder for troubleshooting
        debug_images_folder = os.path.join(grade_processing_folder, "debug_grade_crops")
        if not os.path.exists(debug_images_folder):
            os.makedirs(debug_images_folder)
        
        # Pass roster names to extract_grades for fuzzy matching during extraction
        grades_result = extract_grades(combined_pdf_path, log_callback, debug_images_folder, roster_names=roster_names)
        
        # Initialize error tracking lists BEFORE first use
        extraction_errors = []
        low_confidence_students = []
        skipped_students = []
        
        if not grades_result:
            log("GRADES_NO_RESULTS")
            grades_result = {}  # Set to empty dict to avoid errors
        
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
                log(f"📂 Opening import file...")
                open_file_with_default_app(import_file_path)
            
            # Also open the first pages PDF if it exists
            first_pages_pdf = os.path.join(grade_processing_folder, "PDFs", "1combinedpdf_GRADES_ONLY.pdf")
            if not os.path.exists(first_pages_pdf):
                # Try to create it if it doesn't exist
                log(f"📄 Creating first pages PDF...")
                first_pages_pdf = create_first_pages_pdf(combined_pdf_path, lambda msg: None)
            
            if first_pages_pdf and os.path.exists(first_pages_pdf):
                log(f"📄 Opening grades PDF...")
                open_file_with_default_app(first_pages_pdf)
                
                # Try to arrange windows side-by-side (Windows only)
                try:
                    from file_utils import arrange_windows_side_by_side
                    # Wait briefly and arrange - look for CSV/Excel and PDF windows
                    csv_filename = os.path.basename(import_file_path)
                    pdf_filename = os.path.basename(first_pages_pdf)
                    log(f"🖥️ Arranging windows side-by-side...")
                    if arrange_windows_side_by_side([csv_filename, pdf_filename], delay=1.5):
                        log(f"✓ Windows arranged")
                    else:
                        log(f"⚠️ Could not arrange windows (they may still be open)")
                except Exception as e:
                    log(f"⚠️ Window arrangement unavailable: {e}")
                    pass  # Silent fail - not critical
        except Exception as e:
            log("DEV_ERROR_OPEN_EXTRACTED_FILES", error=str(e))
            extraction_errors.append(f"⚠️ Could not open files: {str(e)}")
        
        # Format and display results
        _format_extraction_results(
            grades_result, student_grades, extraction_errors, 
            low_confidence_students, skipped_students, roster_names
        )
        
        # Prepare confidence scores data for frontend
        confidence_scores = []
        if grades_result:
            for name, grade_info in grades_result.items():
                if isinstance(grade_info, dict):
                    confidence_scores.append({
                        "name": name,
                        "grade": grade_info.get('grade', 'No grade found'),
                        "confidence": grade_info.get('confidence', 0.0)
                    })
        
        # Output JSON response with confidence scores (on new line for server parsing)
        success_response = {
            "success": True,
            "confidenceScores": confidence_scores,
            "assignmentName": assignment_name_from_pdf,
            "pdfPath": combined_pdf_path
        }
        print("\n" + json.dumps(success_response), flush=True)
        
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
