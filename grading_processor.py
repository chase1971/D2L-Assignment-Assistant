# Standard library
import os
import platform
import shutil
import subprocess
import zipfile
from glob import glob

# Third-party
import pandas as pd
from rich.console import Console

# Local
from backup_utils import backup_existing_folder
from config_reader import get_downloads_path, get_rosters_path
from import_file_handler import load_import_file, update_import_file
from pdf_operations import create_combined_pdf, split_combined_pdf
from submission_processor import process_submissions

# Try to import the simplified extract_grades module
try:
    import extract_grades_simple as extract_grades_module
    EXTRACT_GRADES_MODULE = extract_grades_module
    GRADE_EXTRACTION_ENABLED = True
except Exception as e:
    print(f"WARNING: Failed to load extract_grades_simple module: {e}")
    EXTRACT_GRADES_MODULE = None
    GRADE_EXTRACTION_ENABLED = False


def format_error_message(e: Exception) -> str:
    """
    Convert an exception into a user-friendly error message.
    Uses consistent wording for common error types.
    """
    error_str = str(e).lower()
    
    # Check for common error patterns and return consistent messages
    if "being used by another process" in error_str or "locked" in error_str:
        return "❌ The file is being used by another process"
    
    if "permission denied" in error_str or "errno 13" in error_str or "access denied" in error_str:
        return "❌ Cannot access file - permission denied"
    
    if "could not read" in error_str or "unable to read" in error_str or "cannot read" in error_str:
        return "❌ Unable to read file"
    
    if "not found" in error_str or "no such file" in error_str or "does not exist" in error_str:
        return f"❌ File not found"
    
    if "corrupted" in error_str or "invalid" in error_str or "bad" in error_str:
        return "❌ File is corrupted or invalid"
    
    # For other errors, return the original message with emoji prefix
    return f"❌ {str(e)}"


def get_versioned_pdf_path(output_folder: str, assignment_name: str) -> str:
    """
    Generate a versioned PDF filename based on assignment name.
    
    If the file already exists, appends v2, v3, etc.
    Examples:
        - First run: "Quiz 1.pdf"
        - Second run: "Quiz 1 v2.pdf"
        - Third run: "Quiz 1 v3.pdf"
    """
    import re
    
    # Clean assignment name for use as filename (remove invalid chars)
    safe_name = re.sub(r'[<>:"/\\|?*]', '', assignment_name).strip()
    
    base_path = os.path.join(output_folder, f"{safe_name}.pdf")
    
    # If doesn't exist, use the base name
    if not os.path.exists(base_path):
        return base_path
    
    # Find next available version number
    version = 2
    while True:
        versioned_path = os.path.join(output_folder, f"{safe_name} v{version}.pdf")
        if not os.path.exists(versioned_path):
            return versioned_path
        version += 1


class ProcessingResult:
    """Container for processing results"""
    def __init__(self):
        self.submitted = []
        self.unreadable = []
        self.no_submission = []
        self.combined_pdf_path = None
        self.import_file_path = None
        self.assignment_name = None
        self.total_students = 0


def find_latest_zip(download_folder, log_callback=None):
    """Find the latest ZIP file in downloads"""
    if log_callback:
        log_callback("Looking for quiz files in Downloads...")
    
    zip_files = glob(os.path.join(download_folder, "*.zip"))
    
    if not zip_files:
        if log_callback:
            log_callback("No quiz files found in Downloads")
        return None, None
    
    # Sort by modification time (newest first)
    zip_files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    chosen_zip = zip_files[0]
    
    # Extract assignment name from ZIP filename
    base = os.path.splitext(os.path.basename(chosen_zip))[0]
    # Get everything before " Download"
    assignment_name = base.split(" Download")[0].strip()
    
    if log_callback:
        log_callback("")
        log_callback(f"Found quiz file: {os.path.basename(chosen_zip)}")
        log_callback(f"Assignment: {assignment_name}")
        log_callback("")
    
    return chosen_zip, assignment_name


def extract_zip_file(zip_path, extraction_folder, log_callback=None):
    """Extract ZIP file to the grade processing folder"""
    if log_callback:
        log_callback(f"Extracting to: {extraction_folder}")
    
    # Create the extraction folder if it doesn't exist (DON'T delete existing)
    os.makedirs(extraction_folder, exist_ok=True)
    
    index_file_path = None
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Check if index.html exists in the ZIP
            if 'index.html' in zf.namelist():
                # Extract index.html to a temporary location to preserve it
                index_file_path = os.path.join(extraction_folder, 'index.html.original')
                with zf.open('index.html') as index_file:
                    with open(index_file_path, 'wb') as f:
                        f.write(index_file.read())
                if log_callback:
                    log_callback("   Preserved original index.html")
            
            # Extract all files
            zf.extractall(extraction_folder)
    except zipfile.BadZipFile:
        raise Exception("This file can't be opened")
    except zipfile.LargeZipFile:
        raise Exception("This file can't be opened")
    except Exception as e:
        if "BadZipFile" in str(type(e)) or "can't be opened" in str(e).lower():
            raise Exception("This file can't be opened")
        raise
    
    # Count extracted folders (exclude PDFs folder if it exists)
    folder_count = len([d for d in os.listdir(extraction_folder) 
                       if os.path.isdir(os.path.join(extraction_folder, d)) 
                       and d != "PDFs"])
    
    # Check if ZIP contains student assignments
    if folder_count == 0:
        raise Exception("Zip file does not contain student assignments")
    
    if log_callback:
        log_callback("")
        log_callback(f"✅ Extracted {folder_count} student folders")
        if index_file_path:
            log_callback(f"   Preserved index.html from original ZIP")
        log_callback("")
    
    return folder_count


# ============================================================================
# ORCHESTRATION FUNCTIONS
# ============================================================================


def create_combined_pdf_only(drive_letter, class_folder_name, zip_path, log_callback=None):
    """Create combined PDF without updating grades - just extract and combine"""
    result = ProcessingResult()
    
    try:
        # Get configured rosters path
        rosters_path = get_rosters_path()
        class_folder_path = os.path.join(rosters_path, class_folder_name)
        processing_folder = os.path.join(class_folder_path, "grade processing")
        pdf_output_folder = os.path.join(processing_folder, "PDFs")
        
        if log_callback:
            log_callback(f"Drive: {drive_letter}:")
            log_callback(f"Class: {class_folder_name}")
            log_callback(f"Processing folder: {processing_folder}")
            log_callback("-" * 60)
        
        # Backup existing processing folder if it exists
        backup_existing_folder(processing_folder, log_callback)
        
        # Extract assignment name from ZIP filename
        base = os.path.splitext(os.path.basename(zip_path))[0]
        assignment_name = base.split(" Download")[0].strip()
        result.assignment_name = assignment_name
        
        if log_callback:
            log_callback(f"Assignment: {assignment_name}")
        
        # Step 1: Extract ZIP
        extract_zip_file(zip_path, processing_folder, log_callback)
        
        # Step 2: Load Import File (skip validation for process quizzes)
        import_df, import_file_path = load_import_file(class_folder_path, log_callback, skip_validation=True)
        if import_df is None:
            raise Exception("Could not load Import File.csv")
        
        result.import_file_path = import_file_path
        result.total_students = len(import_df)
        
        # Step 3: Process submissions (extract PDFs)
        submitted, unreadable, no_submission, pdf_paths, name_map, student_errors, page_counts = process_submissions(
            processing_folder, import_df, pdf_output_folder, log_callback, is_completion_process=False
        )
        
        # Step 4: Create combined PDF (named after assignment, versioned if exists)
        combined_pdf_path = get_versioned_pdf_path(pdf_output_folder, assignment_name)
        create_combined_pdf(pdf_paths, name_map, combined_pdf_path, log_callback)
        result.combined_pdf_path = combined_pdf_path
        
        if log_callback:
            log_callback(f"   PDF saved as: {os.path.basename(combined_pdf_path)}")
        
        # Store results (but don't update grades)
        result.submitted = [name_map[pdf] for pdf in pdf_paths]
        result.unreadable = [import_df[import_df["Username"] == u]["First Name"].iloc[0].title() + " " + 
                            import_df[import_df["Username"] == u]["Last Name"].iloc[0].title() 
                            for u in unreadable]
        result.no_submission = [import_df[import_df["Username"] == u]["First Name"].iloc[0].title() + " " + 
                               import_df[import_df["Username"] == u]["Last Name"].iloc[0].title() 
                               for u in no_submission]
        
        if log_callback:
            log_callback("")
            log_callback("✅ Combined PDF created!")
            log_callback("")
        
        return result
    
    except Exception as e:
        if log_callback:
            log_callback("")
            log_callback(format_error_message(e))
        raise


def run_reverse_process(drive_letter, class_folder_name, log_callback=None):
    """Reverse process: Split combined PDF back into individual student PDFs"""
    result = ProcessingResult()
    
    try:
        # Get configured rosters path
        rosters_path = get_rosters_path()
        class_folder_path = os.path.join(rosters_path, class_folder_name)
        processing_folder = os.path.join(class_folder_path, "grade processing")
        pdf_output_folder = os.path.join(processing_folder, "PDFs")
        
        # Find the most recent PDF in the folder (assignment-named PDFs)
        combined_pdf_path = None
        if os.path.exists(pdf_output_folder):
            pdf_files = [f for f in os.listdir(pdf_output_folder) if f.endswith('.pdf')]
            if pdf_files:
                # Sort by modification time (newest first)
                pdf_files.sort(key=lambda f: os.path.getmtime(os.path.join(pdf_output_folder, f)), reverse=True)
                combined_pdf_path = os.path.join(pdf_output_folder, pdf_files[0])
        
        if log_callback:
            log_callback(f"Drive: {drive_letter}:")
            log_callback(f"Class: {class_folder_name}")
            log_callback(f"Processing folder: {processing_folder}")
            log_callback("-" * 60)
        
        # Check if combined PDF exists
        if not combined_pdf_path or not os.path.exists(combined_pdf_path):
            raise Exception(f"Combined PDF not found in: {pdf_output_folder}")
        
        if log_callback:
            log_callback(f"Found combined PDF: {os.path.basename(combined_pdf_path)}")
        
        # Load Import File
        import_df, import_file_path = load_import_file(class_folder_path, log_callback)
        if import_df is None:
            raise Exception("Could not load Import File.csv")
        
        result.import_file_path = import_file_path
        result.total_students = len(import_df)
        
        # Split the combined PDF back into individual PDFs
        students_processed = split_combined_pdf(combined_pdf_path, import_df, processing_folder, log_callback)
        
        result.submitted = [f"Student {i+1}" for i in range(students_processed)]
        
        if log_callback:
            log_callback("")
            log_callback("=" * 60)
            log_callback("REVERSE PROCESSING COMPLETE!")
            log_callback(f"Processed {students_processed} students")
            log_callback("=" * 60)
            log_callback("")
        
        return result
    
    except Exception as e:
        if log_callback:
            log_callback("")
            log_callback(format_error_message(e))
        raise


def run_grading_process(drive_letter, class_folder_name, zip_path, log_callback=None):
    """Main processing function"""
    result = ProcessingResult()
    console = Console()
    
    try:
        # Get configured paths
        download_folder = get_downloads_path()
        rosters_path = get_rosters_path()
        class_folder_path = os.path.join(rosters_path, class_folder_name)
        
        processing_folder = os.path.join(class_folder_path, "grade processing")
        pdf_output_folder = os.path.join(processing_folder, "PDFs")
        
        if log_callback:
            log_callback(f"Drive: {drive_letter}:")
            log_callback(f"Class: {class_folder_name}")
            log_callback(f"Processing folder: {processing_folder}")
            log_callback("-" * 60)
        
        # Backup existing processing folder if it exists
        backup_existing_folder(processing_folder, log_callback)
        
        # Extract assignment name from ZIP filename
        base = os.path.splitext(os.path.basename(zip_path))[0]
        assignment_name = base.split(" Download")[0].strip()
        result.assignment_name = assignment_name
        
        if log_callback:
            log_callback(f"Assignment: {assignment_name}")
        
        # Step 1: Extract ZIP
        extract_zip_file(zip_path, processing_folder, log_callback)
        
        # Step 2: Load Import File (skip validation for process quizzes)
        import_df, import_file_path = load_import_file(class_folder_path, log_callback, skip_validation=True)
        if import_df is None:
            raise Exception("Could not load Import File.csv")
        
        result.import_file_path = import_file_path
        result.total_students = len(import_df)
        
        # Step 3: Process submissions
        submitted, unreadable, no_submission, pdf_paths, name_map, student_errors, page_counts = process_submissions(
            processing_folder, import_df, pdf_output_folder, log_callback, is_completion_process=False
        )
        
        # Step 4: Create combined PDF (named after assignment, versioned if exists)
        if len(pdf_paths) == 0:
            raise Exception("Zip file does not contain student assignments")
        
        combined_pdf_path = get_versioned_pdf_path(pdf_output_folder, assignment_name)
        create_combined_pdf(pdf_paths, name_map, combined_pdf_path, log_callback)
        result.combined_pdf_path = combined_pdf_path
        
        if log_callback:
            log_callback(f"   PDF saved as: {os.path.basename(combined_pdf_path)}")
        
        # Step 5: Create assignment column in Import File (but don't add grades yet)
        # Grades will be added later using extract_grades_cli.py after manual grading
        if log_callback:
            log_callback("")
            log_callback("Setting up Import File column...")
        
        try:
            # Create column name
            column_name = f"{assignment_name} Points Grade"
            
            # Check if column already exists
            if column_name not in import_df.columns:
                # Rename column E (index 4) or add new column
                columns = list(import_df.columns)
                if len(columns) > 4:
                    old_name = columns[4]
                    columns[4] = column_name
                    import_df.columns = columns
                    if log_callback:
                        log_callback(f"   Created column: '{column_name}'")
                else:
                    import_df[column_name] = ""
                    if log_callback:
                        log_callback(f"   Added column: '{column_name}'")
                
                # Initialize all cells as blank
                import_df[column_name] = ""
                
                # Save Import File
                try:
                    import_df.to_csv(import_file_path, index=False)
                except PermissionError:
                    friendly_msg = "You might have the import file open, please close and try again!"
                    if log_callback:
                        log_callback(f"   ❌ {friendly_msg}")
                    raise Exception(friendly_msg)
                except OSError as e:
                    # Check if it's a permission denied error (errno 13)
                    if e.errno == 13:
                        friendly_msg = "You might have the import file open, please close and try again!"
                        if log_callback:
                            log_callback(f"   ❌ {friendly_msg}")
                        raise Exception(friendly_msg)
                    else:
                        raise
                if log_callback:
                    log_callback(f"   Import File ready for grade extraction")
            else:
                if log_callback:
                    log_callback(f"   Column already exists: '{column_name}'")
        except Exception as e:
            if log_callback:
                log_callback(f"   Could not setup Import File: {e}")
        
        # Open the combined PDF for grading
        try:
            if log_callback:
                log_callback("")
                log_callback("Opening combined PDF for manual grading...")
            if platform.system() == "Windows":
                os.startfile(combined_pdf_path)
            elif platform.system() == "Darwin":
                subprocess.run(["open", combined_pdf_path])
            else:
                subprocess.run(["xdg-open", combined_pdf_path])
        except Exception as e:
            if log_callback:
                log_callback(f"   Could not open PDF: {e}")
        
        # Store results
        result.submitted = [name_map[pdf] for pdf in pdf_paths]
        result.unreadable = [import_df[import_df["Username"] == u]["First Name"].iloc[0].title() + " " + 
                            import_df[import_df["Username"] == u]["Last Name"].iloc[0].title() 
                            for u in unreadable]
        result.no_submission = [import_df[import_df["Username"] == u]["First Name"].iloc[0].title() + " " + 
                               import_df[import_df["Username"] == u]["Last Name"].iloc[0].title() 
                               for u in no_submission]
        
        if log_callback:
            log_callback("")
            log_callback("=" * 60)
            log_callback("PROCESSING COMPLETE!")
            log_callback("=" * 60)
            log_callback("")
        
        return result
    
    except Exception as e:
        if log_callback:
            log_callback("")
            log_callback(format_error_message(e))
        raise


def run_completion_process(drive_letter, class_folder_name, zip_path, log_callback=None, dont_override=False):
    """
    Completion processing function - same as grading process but auto-assigns 10 points
    to all students who submitted (no OCR extraction needed)
    
    Args:
        dont_override: If True, add new column after column E instead of overriding it.
                       If False, reset to 6 columns and use column E (existing behavior).
    """
    result = ProcessingResult()
    
    try:
        # Get configured paths
        download_folder = get_downloads_path()
        rosters_path = get_rosters_path()
        class_folder_path = os.path.join(rosters_path, class_folder_name)
        
        # Validate import file BEFORE starting processing
        from import_file_handler import validate_import_file_early
        is_valid, error_msg = validate_import_file_early(class_folder_path)
        if not is_valid:
            raise Exception(error_msg)
        
        processing_folder = os.path.join(class_folder_path, "grade processing")
        pdf_output_folder = os.path.join(processing_folder, "PDFs")
        
        if log_callback:
            log_callback(f"Drive: {drive_letter}:")
            log_callback(f"Class: {class_folder_name}")
            log_callback(f"Processing folder: {processing_folder}")
            log_callback("-" * 60)
        
        # Backup existing processing folder if it exists
        backup_existing_folder(processing_folder, log_callback)
        
        # Extract assignment name from ZIP filename
        base = os.path.splitext(os.path.basename(zip_path))[0]
        assignment_name = base.split(" Download")[0].strip()
        result.assignment_name = assignment_name
        
        if log_callback:
            log_callback(f"Assignment: {assignment_name}")
        
        # Step 1: Extract ZIP
        extract_zip_file(zip_path, processing_folder, log_callback)
        
        # Step 2: Load Import File
        import_df, import_file_path = load_import_file(class_folder_path, log_callback)
        if import_df is None:
            raise Exception("Could not load Import File.csv")
        
        result.import_file_path = import_file_path
        result.total_students = len(import_df)
        
        # Step 3: Process submissions
        submitted, unreadable, no_submission, pdf_paths, name_map, student_errors, page_counts = process_submissions(
            processing_folder, import_df, pdf_output_folder, log_callback, is_completion_process=True
        )
        
        # Step 4: Create combined PDF (named after assignment, versioned if exists)
        if len(pdf_paths) == 0:
            raise Exception("Zip file does not contain student assignments")
        
        combined_pdf_path = get_versioned_pdf_path(pdf_output_folder, assignment_name)
        create_combined_pdf(pdf_paths, name_map, combined_pdf_path, log_callback)
        result.combined_pdf_path = combined_pdf_path
        
        if log_callback:
            log_callback(f"   PDF saved as: {os.path.basename(combined_pdf_path)}")
        
        # Step 5: Update Import File with auto-assigned 10 points for completions
        # No OCR needed - just assign 10 points to all submitted students
        update_import_file(
            import_df, 
            import_file_path, 
            assignment_name,
            submitted, 
            unreadable, 
            no_submission,
            grades_map=None,  # No OCR grades - auto-assign 10 points
            log_callback=log_callback,
            dont_override=dont_override
        )
        
        # Store results
        result.submitted = [name_map[pdf] for pdf in pdf_paths]
        result.unreadable = [import_df[import_df["Username"] == u]["First Name"].iloc[0].title() + " " + 
                            import_df[import_df["Username"] == u]["Last Name"].iloc[0].title() 
                            for u in unreadable]
        result.no_submission = [import_df[import_df["Username"] == u]["First Name"].iloc[0].title() + " " + 
                               import_df[import_df["Username"] == u]["Last Name"].iloc[0].title() 
                               for u in no_submission]
        
        if log_callback:
            log_callback("")
            log_callback(f"✅ Auto-assigned 10 points to {len(submitted)} submissions")
            log_callback("✅ Completion processing completed!")
            log_callback("")
            
            # Display student errors at the end in red
            if student_errors:
                log_callback("")
                log_callback("❌ STUDENT ERRORS AND WARNINGS:")
                for error in student_errors:
                    log_callback(f"❌ {error}")
            
            log_callback("")
        
        return result
    
    except Exception as e:
        if log_callback:
            log_callback("")
            log_callback(format_error_message(e))
        raise
