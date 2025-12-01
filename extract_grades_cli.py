#!/usr/bin/env python3
"""
Fixed CLI script for grade extraction - based on working minimal version
Usage: python extract_grades_cli_fixed.py <drive> <className>
"""

import sys
import os
import json
import pandas as pd
import subprocess
import platform
from extract_grades_simple import extract_grades, create_first_pages_pdf
from config_reader import get_rosters_path

def _names_match_fuzzy(name1, name2, threshold=0.8):
    """Check if two names match with fuzzy logic"""
    name1_clean = name1.lower().strip()
    name2_clean = name2.lower().strip()
    
    # If exact match, return True
    if name1_clean == name2_clean:
        return True
    
    # Split into words
    words1 = name1_clean.split()
    words2 = name2_clean.split()
    
    # If one name is contained in the other, that's a match
    if name1_clean in name2_clean or name2_clean in name1_clean:
        return True
    
    # Check if first and last names match (ignoring middle names)
    if len(words1) >= 2 and len(words2) >= 2:
        if words1[0] == words2[0] and words1[-1] == words2[-1]:
            return True
    
    # Check if most words match
    if len(words1) > 0 and len(words2) > 0:
        matches = 0
        for word1 in words1:
            for word2 in words2:
                if word1 == word2 or (len(word1) > 3 and len(word2) > 3 and 
                                    (word1 in word2 or word2 in word1)):
                    matches += 1
                    break
        
        # If threshold% of words match, consider it a match
        similarity = matches / max(len(words1), len(words2))
        return similarity >= threshold
    
    return False

def main():
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
        grade_processing_folder = os.path.join(class_folder, "grade processing")
        combined_pdf_path = os.path.join(grade_processing_folder, "PDFs", "1combinedpdf.pdf")
        
        if not os.path.exists(combined_pdf_path):
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
                                except:
                                    pass
                except:
                    pass
        
        grades_result = extract_grades(combined_pdf_path, log_callback)
        
        if not grades_result:
            extraction_errors.append("❌ No grades were extracted from the PDF")
            grades_result = {}  # Set to empty dict to avoid errors
        
        # Collect low confidence students and errors during CSV update
        low_confidence_students = []
        extraction_errors = []
        skipped_students = []
        
        # Update CSV
        import_file_path = os.path.join(class_folder, "Import File.csv")
        if os.path.exists(import_file_path):
            df = pd.read_csv(import_file_path)
            
            # Find quiz column
            grade_columns = [col for col in df.columns if 'Points Grade' in col or 'Quiz' in col]
            if grade_columns:
                quiz_column = grade_columns[0]
            else:
                quiz_column = df.columns[-2]
            
            # Ensure column G (index 6) exists for "Verify" flag
            if len(df.columns) <= 6:
                # Add empty columns if needed to reach column G
                while len(df.columns) <= 6:
                    df[f'Column_{len(df.columns)}'] = ''
                # Set column G (index 6) to have no heading
                column_g_name = df.columns[6]
                df.rename(columns={column_g_name: ''}, inplace=True)
            
            # Update grades - collect low confidence students
            updated_count = 0
            matching_errors = []
            fuzzy_matches = []  # Track fuzzy matches that need verification
            
            # Build a map of full names from CSV for fuzzy matching
            csv_name_map = {}
            for idx, row in df.iterrows():
                first = str(row['First Name']).strip().lower()
                last = str(row['Last Name']).strip().lower()
                full_name = f"{first} {last}"
                csv_name_map[full_name] = idx
            
            for student_name, grade_info in grades_result.items():
                # Always take the processed grade (with smart corrections)
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

                # If no grade found, leave empty (don't put "?")
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
                        # Try multiple strategies for matching with middle names
                        # Strategy 1: Full name fuzzy match
                        if _names_match_fuzzy(student_name_lower, csv_name, threshold=0.7):
                            # Calculate similarity score
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
                    # Always write the OCR's grade text
                    df.at[matched_idx, quiz_column] = grade

                    # Mark "Verify" for low confidence OR fuzzy matches
                    needs_verify = False
                    if confidence < 0.7:
                        needs_verify = True
                        grade_display = grade if grade else "(no grade found)"
                        low_confidence_students.append(f"{student_name}: {grade_display} (low confidence – needs verification)")
                    elif is_fuzzy_match:
                        needs_verify = True
                    
                    if needs_verify:
                        # Write "Verify" to column G (index 6)
                        df.at[matched_idx, df.columns[6]] = "Verify"
                    
                    updated_count += 1
                else:
                    matching_errors.append(f"❌ Could not match: {student_name} (grade: {grade if grade else 'N/A'})")
                    skipped_students.append({
                        "name": student_name,
                        "grade": grade,
                        "confidence": confidence,
                        "reason": "Could not match to roster"
                    })
            
            # Add fuzzy matches to logs (they're warnings, not errors)
            if fuzzy_matches:
                extraction_errors.extend(fuzzy_matches)
            
            # Add matching errors to extraction_errors
            extraction_errors.extend(matching_errors)
            
            # Save updated CSV
            df.to_csv(import_file_path, index=False)
            
        else:
            extraction_errors.append("❌ Import file not found")
            raise Exception("Import file not found")
        
        # Open the Excel file and first pages PDF automatically
        try:
            # Open Excel file
            if os.path.exists(import_file_path):
                if platform.system() == "Windows":
                    os.startfile(import_file_path)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", import_file_path])
                else:  # Linux
                    subprocess.run(["xdg-open", import_file_path])
            
            # Also open the first pages PDF if it exists
            first_pages_pdf = os.path.join(grade_processing_folder, "PDFs", "1combinedpdf_GRADES_ONLY.pdf")
            if not os.path.exists(first_pages_pdf):
                # Try to create it if it doesn't exist
                first_pages_pdf = create_first_pages_pdf(combined_pdf_path, lambda msg: None)
            
            if first_pages_pdf and os.path.exists(first_pages_pdf):
                if platform.system() == "Windows":
                    os.startfile(first_pages_pdf)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", first_pages_pdf])
                else:  # Linux
                    subprocess.run(["xdg-open", first_pages_pdf])
        except Exception as e:
            extraction_errors.append(f"⚠️ Could not open files: {str(e)}")
        
        # Build comprehensive log output
        logs = []
        logs.append("🔬 Starting grade extraction...")
        logs.append("")
        
        # Show all extracted grades with confidence levels
        if student_grades:
            logs.append("📋 EXTRACTED GRADES:")
            for i, sg in enumerate(student_grades, 1):
                conf = sg['confidence']
                conf_indicator = "✅" if conf >= 0.7 else "⚠️" if conf >= 0.4 else "❌"
                logs.append(f"   {i:2d}. {sg['name']}: {sg['grade']} {conf_indicator} (confidence: {conf:.2f})")
        elif grades_result:
            # Fallback: show from grades_result if student_grades wasn't populated
            logs.append("📋 EXTRACTED GRADES:")
            for i, (name, grade_info) in enumerate(grades_result.items(), 1):
                if isinstance(grade_info, dict):
                    grade = grade_info.get('grade', '')
                    conf = grade_info.get('confidence', 0)
                else:
                    grade = str(grade_info)
                    conf = 0
                conf_indicator = "✅" if conf >= 0.7 else "⚠️" if conf >= 0.4 else "❌"
                logs.append(f"   {i:2d}. {name}: {grade} {conf_indicator} (confidence: {conf:.2f})")
        
        logs.append("")
        logs.append(f"📊 Processed {len(grades_result) if grades_result else 0} students")
        
        # Collect all errors and warnings for red display at the end
        all_issues = []
        
        # Show low confidence students (will be displayed in red at end)
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
                    if conf < 0.7:
                        # Check if already in low_confidence_students or skipped_students
                        already_reported = any(name in issue[1] for issue in all_issues)
                        if not already_reported:
                            grade_display = grade if grade and grade != "No grade found" else "(no grade found)"
                            all_issues.append(("WARNING", f"⚠️ {name}: {grade_display} (low confidence: {conf:.2f} – needs verification)"))
        
        logs.append("")
        logs.append("✅ Done")
        
        # Display errors and warnings in red at the end
        if all_issues:
            logs.append("")
            logs.append("=" * 60)
            logs.append("⚠️ ISSUES FOUND (Please Review):")
            logs.append("=" * 60)
            for issue_type, issue_msg in all_issues:
                # Remove any existing error/warning symbols to avoid duplicates
                clean_msg = issue_msg.replace("❌ ", "").replace("⚠️ ", "").strip()
                # Mark with red indicator - actual red coloring would need terminal support
                if issue_type == "ERROR":
                    logs.append(f"❌ {clean_msg}")
                else:
                    logs.append(f"⚠️  {clean_msg}")
        
        response = {
            "success": True,
            "message": "Grade extraction completed",
            "logs": logs
        }
        
        # Print JSON to stderr so it doesn't interfere with logs
        print(json.dumps(response), file=sys.stderr)
        
    except Exception as e:
        error_msg = str(e)
        
        # Determine friendly error message
        if "Oops" in error_msg or "wrong file" in error_msg.lower() or "wrong class" in error_msg.lower():
            # This is a wrong file/class error - use the existing friendly message
            friendly_error = error_msg
        elif "empty" in error_msg.lower() or "could not be read" in error_msg.lower() or "could not convert" in error_msg.lower():
            # This is likely because Process Quizzes wasn't run first
            friendly_error = "Something went wrong with the extraction. Make sure you've run 'Process Quizzes' or 'Process Completion' first."
        elif error_msg and error_msg.strip():
            # There's a specific error message - use it
            friendly_error = f"Something went wrong with the extraction: {error_msg}"
        else:
            # Unknown error
            friendly_error = "It ran into a problem."
        
        # Build simplified error output
        error_logs = []
        error_logs.append("🔬 Starting grade extraction...")
        error_logs.append(friendly_error)
        error_logs.append("")
        error_logs.append("✅ Done")
        
        error_response = {
            "success": False,
            "error": friendly_error,
            "logs": error_logs
        }
        # Print JSON to stderr so it doesn't interfere with logs
        print(json.dumps(error_response), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
