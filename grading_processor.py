import os
import shutil
import re
import pandas as pd
import zipfile
from glob import glob
from io import BytesIO
from pypdf import PdfWriter, PdfReader
from datetime import datetime
import platform
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from config_reader import get_downloads_path, get_rosters_path

# Try for watermarking
try:
    from reportlab.pdfgen import canvas
    WATERMARK_ENABLED = True
except ImportError:
    WATERMARK_ENABLED = False

# Normalization settings
NORMALIZATION_ENABLED = True
TARGET_WIDTH, TARGET_HEIGHT = 612, 792  # letter size in points

# Try to import the simplified extract_grades module
try:
    import extract_grades_simple as extract_grades_module
    EXTRACT_GRADES_MODULE = extract_grades_module
    GRADE_EXTRACTION_ENABLED = True
except Exception as e:
    print(f"WARNING: Failed to load extract_grades_simple module: {e}")
    EXTRACT_GRADES_MODULE = None
    GRADE_EXTRACTION_ENABLED = False

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

def backup_existing_folder(folder_path, log_callback=None):
    """
    If folder exists, rename it to a backup with timestamp
    Returns: True if backup was created, False if folder didn't exist
    """
    if os.path.exists(folder_path):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_name = f"{folder_path} - backup - {timestamp}"
        
        if log_callback:
            log_callback("")
            log_callback("Existing folder found, creating backup...")
            log_callback(f"   Renaming: {os.path.basename(folder_path)}")
            log_callback(f"         to: {os.path.basename(backup_name)}")
        
        try:
            os.rename(folder_path, backup_name)
            if log_callback:
                log_callback(f"   Backup created successfully")
                log_callback("")
            return True
        except Exception as e:
            if log_callback:
                log_callback(f"   Could not create backup: {e}")
                log_callback("")
            return False
    return False

def normalize_pdf_with_pypdf(page):
    """Scale content to fit within target dimensions without cropping"""
    orig_width = float(page.mediabox.width)
    orig_height = float(page.mediabox.height)
    
    # Calculate scale factors to fit within target (preserve aspect ratio)
    scale_x = TARGET_WIDTH / orig_width
    scale_y = TARGET_HEIGHT / orig_height
    scale = min(scale_x, scale_y)
    
    # Calculate new dimensions after scaling
    new_width = orig_width * scale
    new_height = orig_height * scale
    
    # Calculate center position for the scaled content
    x_center = (TARGET_WIDTH - new_width) / 2
    y_center = (TARGET_HEIGHT - new_height) / 2
    
    # Create transformation matrix: scale + translate to center
    transformation_matrix = [
        scale, 0, 0, scale,
        x_center, y_center
    ]
    
    # Apply the transformation to all content on the page
    page.add_transformation(transformation_matrix)
    
    # Set the page to target size
    page.mediabox.lower_left = (0, 0)
    page.mediabox.upper_right = (TARGET_WIDTH, TARGET_HEIGHT)
    
    return page

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
    
    # Count extracted folders
    folder_count = len([d for d in os.listdir(extraction_folder) 
                       if os.path.isdir(os.path.join(extraction_folder, d))])
    
    if log_callback:
        log_callback("")
        log_callback(f"Extracted {folder_count} student folders")
        if index_file_path:
            log_callback(f"   Preserved index.html from original ZIP")
        log_callback("")
    
    return folder_count

def load_import_file(class_folder_path, log_callback=None):
    """Load the Import File.csv"""
    import_file_path = os.path.join(class_folder_path, "Import File.csv")
    
    if not os.path.exists(import_file_path):
        if log_callback:
            log_callback(f"Import File not found: {import_file_path}")
        return None, None
    
    df = pd.read_csv(import_file_path, dtype=str)
    
    if log_callback:
        log_callback("")
        log_callback(f"Loaded Import File: {len(df)} students")
        log_callback("")
    
    return df, import_file_path

def process_submissions(extraction_folder, import_df, pdf_output_folder, log_callback=None, is_completion_process=False):
    """Process all student submissions"""
    if log_callback:
        log_callback("")
        log_callback("-" * 40)
        log_callback("PROCESSING STUDENT SUBMISSIONS")
        log_callback("-" * 40)
    
    # Prepare student data
    import_df["Last Name"] = import_df["Last Name"].str.strip().str.lower()
    import_df["First Name"] = import_df["First Name"].str.strip().str.lower()
    
    submitted = set()
    unreadable = set()
    no_submission = set()
    pdf_paths = []
    name_map = {}
    multiple_pdf_students = []  # Track students with multiple PDFs
    student_errors = []  # Track all student errors for display at end
    page_counts = {}  # Track page count for each student: {name: page_count}
    
    # Create PDF output folder
    os.makedirs(pdf_output_folder, exist_ok=True)
    
    # Clear old PDFs
    for f in os.listdir(pdf_output_folder):
        if f.lower().endswith(".pdf"):
            os.remove(os.path.join(pdf_output_folder, f))
    
    # Helper function to parse timestamp from folder name
    def parse_folder_timestamp(folder_name):
        """
        Parse timestamp from Canvas folder name like:
        "Submission - First Last - Oct 10, 2025 951 PM"
        Returns a datetime object, or None if parsing fails
        """
        try:
            # Extract date/time portion after the second dash
            match = re.search(r"-\s+(.*?)\s+-\s+(.+)$", folder_name)
            if not match:
                return None
            
            date_str = match.group(2).strip()
            
            # Try multiple date formats Canvas might use
            date_formats = [
                "%b %d, %Y %I%M %p",  # Oct 10, 2025 951 PM
                "%b %d, %Y %I:%M %p",  # Oct 10, 2025 9:51 PM
                "%B %d, %Y %I%M %p",  # October 10, 2025 951 PM
                "%B %d, %Y %I:%M %p",  # October 10, 2025 9:51 PM
            ]
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            return None
        except Exception:
            return None
    
    # Group submissions by student name, keeping only the latest
    submission_map = {}  # {student_name: (folder_name, timestamp)}
    
    for fld in os.listdir(extraction_folder):
        fp = os.path.join(extraction_folder, fld)
        if not os.path.isdir(fp):
            continue
        
        # Extract student name from folder (format: "Submission - First Last - date")
        m = re.search(r"-\s+(.*?)\s+-", fld)
        if not m:
            continue
        
        name = m.group(1).strip()
        timestamp = parse_folder_timestamp(fld)
        
        # If we already have this student, keep the one with the latest timestamp
        if name in submission_map:
            existing_folder, existing_timestamp = submission_map[name]
            
            # If both have timestamps, compare them
            if timestamp and existing_timestamp:
                if timestamp > existing_timestamp:
                    submission_map[name] = (fld, timestamp)
                    if log_callback:
                        log_callback(f"   {name}: Found newer submission ({timestamp.strftime('%b %d, %I:%M %p')}), using that")
            # If only the new one has a timestamp, use it
            elif timestamp and not existing_timestamp:
                submission_map[name] = (fld, timestamp)
            # Otherwise keep the existing one
        else:
            # First submission for this student
            submission_map[name] = (fld, timestamp)
    
    if log_callback:
        log_callback("")
        log_callback(f"Found {len(submission_map)} unique students (after filtering duplicates)")
        log_callback("")
    
    # Track unmatched students for validation
    unmatched_count = 0
    
    # Process each unique submission (latest only)
    for name, (fld, timestamp) in submission_map.items():
        fp = os.path.join(extraction_folder, fld)
        
        # Split name for matching
        parts = name.split()
        if len(parts) < 2:
            continue
        
        # Try multiple matching strategies for names with middle names
        hit = None
        
        # Strategy 1: First word = first name, rest = last name
        # Example: "Juliane Erich Labial" → first="juliane", last="erich labial"
        first = parts[0].lower()
        last = " ".join(parts[1:]).lower()
        hit = import_df[(import_df["First Name"] == first) & (import_df["Last Name"] == last)]
        
        # Strategy 2: If no match, try: all but last word = first name, last word = last name
        # Example: "Juliane Erich Labial" → first="juliane erich", last="labial"
        if len(hit) != 1 and len(parts) >= 3:
            first = " ".join(parts[:-1]).lower()
            last = parts[-1].lower()
            hit = import_df[(import_df["First Name"] == first) & (import_df["Last Name"] == last)]
        
        # Strategy 3: If still no match, try last name with hyphen/space variations
        # Example: "Silva Montano" could match "silva montano" or "silva-montano"
        if len(hit) != 1:
            first = parts[0].lower()
            last = " ".join(parts[1:]).lower()
            last_hyphen = "-".join(parts[1:]).lower()
            hit = import_df[
                (import_df["First Name"] == first) & 
                ((import_df["Last Name"] == last) | (import_df["Last Name"] == last_hyphen))
            ]
        
        # Strategy 4: Extract all name parts and require at least 2 matching parts
        # Example: "Jaime Alberto Gonzalez Franco" matches "jaime alberto" + "gonzalez franco"
        # by matching at least 2 of: jaime, alberto, gonzalez, franco
        if len(hit) != 1:
            # Extract all name parts from student name (lowercase, normalized)
            student_name_parts = set([p.lower().strip() for p in parts if p.strip()])
            
            # Find roster entries with at least 2 matching name parts
            matching_rows = []
            for idx, row in import_df.iterrows():
                # Extract all name parts from roster entry
                roster_first = str(row["First Name"]).lower().strip() if pd.notna(row["First Name"]) else ""
                roster_last = str(row["Last Name"]).lower().strip() if pd.notna(row["Last Name"]) else ""
                
                # Split roster names into parts
                roster_parts = set()
                if roster_first:
                    roster_parts.update([p.strip() for p in roster_first.split() if p.strip()])
                if roster_last:
                    roster_parts.update([p.strip() for p in roster_last.split() if p.strip()])
                
                # Count matching parts
                matching_parts = student_name_parts.intersection(roster_parts)
                if len(matching_parts) >= 2:
                    matching_rows.append((idx, len(matching_parts)))
            
            # If we found matches, use the one with the most matching parts
            if matching_rows:
                # Sort by number of matching parts (descending), then take first
                matching_rows.sort(key=lambda x: x[1], reverse=True)
                best_match_idx = matching_rows[0][0]
                hit = import_df.iloc[[best_match_idx]]
                if log_callback:
                    roster_name = f"{hit.iloc[0]['First Name']} {hit.iloc[0]['Last Name']}"
                    log_callback(f"   {name}: Matched using name parts (Strategy 4) → {roster_name}")
        
        if len(hit) != 1:
            unmatched_count += 1
            error_msg = f"{name}: Could not match to roster"
            student_errors.append(error_msg)
            if log_callback:
                log_callback(f"   {error_msg}")
            continue
        
        user = hit.iloc[0]["Username"]
        files = os.listdir(fp)
        pdfs = [f for f in files if f.lower().endswith(".pdf")]
        
        # Handle PDFs
        if pdfs:
            dst = os.path.join(pdf_output_folder, f"{user}.pdf")
            
            if len(pdfs) == 1:
                # Single PDF - just copy it
                src_pdf = os.path.join(fp, pdfs[0])
                shutil.copy(src_pdf, dst)
                # Count pages
                try:
                    reader = PdfReader(src_pdf)
                    page_count = len(reader.pages)
                    page_counts[name] = page_count
                except Exception as e:
                    error_msg = f"{name}: Error reading PDF page count: {e}"
                    student_errors.append(error_msg)
                    if log_callback:
                        log_callback(f"   ⚠️ {error_msg}")
                
                if log_callback:
                    if is_completion_process:
                        log_callback(f"   {name}: PDF found → 10 points")
                    else:
                        log_callback(f"   {name}: PDF found")
            else:
                # Multiple PDFs - combine them
                multiple_pdf_students.append(name)
                if log_callback:
                    if is_completion_process:
                        log_callback(f"   {name}: {len(pdfs)} PDFs found, combining → 10 points")
                    else:
                        log_callback(f"   {name}: {len(pdfs)} PDFs found, combining")
                
                try:
                    # Combine multiple PDFs into one and count pages
                    combined_writer = PdfWriter()
                    total_pages = 0
                    for pdf_file in sorted(pdfs):  # Sort for consistent order
                        pdf_path = os.path.join(fp, pdf_file)
                        try:
                            reader = PdfReader(pdf_path)
                            page_count = len(reader.pages)
                            total_pages += page_count
                            for page in reader.pages:
                                combined_writer.add_page(page)
                        except Exception as e:
                            error_msg = f"{name}: Error reading {pdf_file}: {e}"
                            student_errors.append(error_msg)
                            if log_callback:
                                log_callback(f"      ⚠️ {error_msg}")
                    
                    page_counts[name] = total_pages
                    
                    # Write combined PDF
                    with open(dst, "wb") as output_file:
                        combined_writer.write(output_file)
                    
                except Exception as e:
                    error_msg = f"{name}: Error combining PDFs: {e}"
                    student_errors.append(error_msg)
                    if log_callback:
                        log_callback(f"      ⚠️ {error_msg}")
                    # Fallback: just use the first PDF
                    try:
                        shutil.copy(os.path.join(fp, pdfs[0]), dst)
                        # Count pages for fallback PDF
                        reader = PdfReader(os.path.join(fp, pdfs[0]))
                        page_counts[name] = len(reader.pages)
                    except Exception as e2:
                        error_msg = f"{name}: Error with fallback PDF: {e2}"
                        student_errors.append(error_msg)
            
            pdf_paths.append(dst)
            name_map[dst] = name
            submitted.add(user)
        else:
            # Check for other files (images, etc.)
            others = [f for f in files if not f.lower().endswith(".pdf")]
            if others:
                unreadable.add(user)
                # Check if it's an image
                image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
                has_image = any(f.lower().endswith(tuple(image_extensions)) for f in others)
                file_type = "image file" if has_image else "non-PDF file"
                error_msg = f"{name}: {file_type} → unreadable"
                student_errors.append(error_msg)
                if log_callback:
                    log_callback(f"   {error_msg}")
            else:
                no_submission.add(user)
                error_msg = f"{name}: No submission"
                student_errors.append(error_msg)
                if log_callback:
                    if is_completion_process:
                        log_callback(f"   {name}: No submission → 0 points")
                    else:
                        log_callback(f"   {name}: No submission")
    
    # Move unreadable submissions to separate folder
    unreadable_folder = os.path.join(extraction_folder, "unreadable")
    os.makedirs(unreadable_folder, exist_ok=True)
    
    for fld in os.listdir(extraction_folder):
        fp = os.path.join(extraction_folder, fld)
        if not os.path.isdir(fp) or fld == "unreadable":
            continue
        
        m = re.search(r"-\s+(.*?)\s+-", fld)
        if not m:
            continue
        
        name = m.group(1).strip()
        parts = name.split()
        if len(parts) < 2:
            continue
        
        first = parts[0].lower()
        last = " ".join(parts[1:]).lower()
        hit = import_df[(import_df["First Name"] == first) & (import_df["Last Name"] == last)]
        if len(hit) != 1:
            continue
        
        user = hit.iloc[0]["Username"]
        if user in unreadable:
            dst_folder = os.path.join(unreadable_folder, fld)
            if os.path.exists(dst_folder):
                shutil.rmtree(dst_folder)
            shutil.move(fp, dst_folder)
    
    # Log summary of multiple PDF students at the end
    if multiple_pdf_students and log_callback:
        log_callback("")
        log_callback("Students who submitted multiple PDFs (combined automatically):")
        for student_name in multiple_pdf_students:
            log_callback(f"   • {student_name}")
    
    # Calculate average pages and flag students with fewer pages than average
    if page_counts and len(page_counts) > 0:
        avg_pages = sum(page_counts.values()) / len(page_counts)
        for name, page_count in page_counts.items():
            if page_count < avg_pages * 0.7:  # Flag if less than 70% of average
                error_msg = f"{name}: Has only {page_count} page(s), below average of {avg_pages:.1f} pages"
                student_errors.append(error_msg)
    
    # Validate: Check if we have a mismatch problem (many unmatched, few matched)
    if len(submission_map) > 0:
        match_rate = len(submitted) / len(submission_map) if len(submission_map) > 0 else 0
        if match_rate < 0.3 and unmatched_count > 3:  # Less than 30% match rate and many unmatched
            raise Exception("Oops. You've chosen the wrong file or class. Try again.")
        elif len(submitted) == 0 and len(submission_map) > 0:
            raise Exception("Oops. You've chosen the wrong file or class. Try again.")
    
    return submitted, unreadable, no_submission, pdf_paths, name_map, student_errors, page_counts

def create_combined_pdf(pdf_paths, name_map, output_path, log_callback=None):
    """Create a single combined PDF with watermarks"""
    # Don't create PDF if there are no submissions
    if not pdf_paths or len(pdf_paths) == 0:
        raise Exception("Oops. You've chosen the wrong file or class. Try again.")
    
    if log_callback:
        log_callback("")
        log_callback("-" * 40)
        log_callback("NORMALIZING AND COMBINING PDFs")
        log_callback("-" * 40)
    
    writer = PdfWriter()
    
    # Sort PDFs by last name (extract from name_map: "First Last" -> sort by "Last")
    def get_last_name(pdf_path):
        name = name_map[pdf_path]
        parts = name.split()
        if len(parts) >= 2:
            return " ".join(parts[1:]).lower()  # Last name
        return name.lower()
    
    sorted_pdfs = sorted(pdf_paths, key=get_last_name)
    
    for pdf in sorted_pdfs:
        name = name_map[pdf]
        
        try:
            reader = PdfReader(pdf)
            num_pages = len(reader.pages)
            
            # Normalize each page if enabled
            if NORMALIZATION_ENABLED:
                for page in reader.pages:
                    normalize_pdf_with_pypdf(page)
            
            # Add pages to combined PDF with individual watermarks
            for page_num, page in enumerate(reader.pages, start=1):
                # Create watermark for this specific page
                if WATERMARK_ENABLED:
                    watermark_text = f"{name} ({page_num} of {num_pages})"
                    
                    pkt = BytesIO()
                    can = canvas.Canvas(pkt, pagesize=(TARGET_WIDTH, TARGET_HEIGHT))
                    can.setFont("Helvetica-Bold", 16)
                    tw = can.stringWidth(watermark_text, "Helvetica-Bold", 16)
                    
                    # Position in top-right corner
                    x = TARGET_WIDTH - tw - 15
                    y = TARGET_HEIGHT - 25
                    
                    can.setFillColorRGB(0, 0, 0)
                    can.drawString(x, y, watermark_text)
                    can.save()
                    pkt.seek(0)
                    watermark = PdfReader(pkt).pages[0]
                    
                    try:
                        page.merge_page(watermark)
                    except Exception:
                        pass  # Skip watermark if it fails
                
                writer.add_page(page)
        
        except Exception as e:
            if log_callback:
                log_callback(f"   Error processing {name}: {e}")
    
    # Set PDF to open at page 1, fit to window
    try:
        from pypdf.generic import ArrayObject, NameObject, NumberObject, DictionaryObject
        
        if len(writer.pages) > 0:
            # Create OpenAction to go to first page with "Fit" view
            first_page = writer.pages[0]
            dest = ArrayObject([
                first_page.indirect_reference,
                NameObject("/Fit")
            ])
            writer._root_object[NameObject("/OpenAction")] = dest
    except Exception:
        # If setting open action fails, just continue without it
        pass
    
    # Write combined PDF
    with open(output_path, "wb") as f:
        writer.write(f)
    
    if log_callback:
        log_callback("")
        log_callback(f"Created combined PDF: {len(pdf_paths)} submissions (sorted by last name)")
        log_callback("")
    
    return output_path

def update_import_file(import_df, import_file_path, assignment_name, 
                       submitted, unreadable, no_submission, grades_map=None, log_callback=None, dont_override=False):
    """Update the Import File with grades
    
    Args:
        dont_override: If True, add new column after column E instead of overriding it.
                       If False, reset to 6 columns and use column E (existing behavior).
    """
    try:
        if log_callback:
            log_callback("")
            log_callback("-" * 40)
            log_callback("UPDATING IMPORT FILE")
            log_callback("-" * 40)
            log_callback(f"Current columns: {list(import_df.columns)}")
            log_callback("")
        
        # Create column name
        column_name = f"{assignment_name} Points Grade"
        
        if log_callback:
            log_callback(f"   New column name: '{column_name}'")
        
        # Handle dont_override flag
        if dont_override:
            # Don't override mode: Insert new column after column E (index 4)
            if log_callback:
                log_callback(f"   Mode: Don't override - adding new column after column E")
            
            # Ensure we have at least 5 columns (A-E)
            if len(import_df.columns) < 5:
                if log_callback:
                    log_callback(f"   Warning: Less than 5 columns, adding empty columns")
                while len(import_df.columns) < 5:
                    import_df[f'Column_{len(import_df.columns)}'] = ""
            
            # Check if column already exists
            if column_name in import_df.columns:
                if log_callback:
                    log_callback(f"   Column '{column_name}' already exists, using existing column")
            else:
                # Insert new column after column E (at position/index 5)
                # First add the column with empty values
                import_df.insert(5, column_name, "")
                
                if log_callback:
                    log_callback(f"   Added new column '{column_name}' at index 5 (after column E)")
        else:
            # Override mode: Delete all columns between E and End-of-Line, keep only A-E and End-of-Line
            if log_callback:
                log_callback(f"   Mode: Override - removing all columns between E and End-of-Line Indicator")
            
            # Identify the first 5 columns (A-E) and the last column (End-of-Line Indicator)
            first_five_columns = list(import_df.columns[:5])  # Keep first 5 columns (A-E)
            last_column_name = import_df.columns[-1]  # Keep the last column (End-of-Line Indicator)
            
            if log_callback:
                log_callback(f"   First 5 columns: {first_five_columns}")
                log_callback(f"   Last column (End-of-Line): {last_column_name}")
                log_callback(f"   Current total columns: {len(import_df.columns)}")
            
            # Check if there are columns to remove between E and End-of-Line
            if len(import_df.columns) > 6:
                columns_to_remove = list(import_df.columns[5:-1])  # All columns between E and End-of-Line
                if log_callback:
                    log_callback(f"   Removing {len(columns_to_remove)} columns: {columns_to_remove}")
            
            # Create new column list: A, B, C, D, Assignment Name, End-of-Line
            # Rename column E (index 4) to the assignment name
            new_column_names = first_five_columns.copy()
            new_column_names[4] = column_name  # Rename column E to assignment name
            new_column_names.append(last_column_name)  # Add End-of-Line Indicator
            
            # Select only the columns we want to keep: first 5 + last column
            columns_to_keep = first_five_columns + [last_column_name]
            import_df = import_df[columns_to_keep].copy()
            
            # Rename the columns
            import_df.columns = new_column_names
            
            if log_callback:
                log_callback(f"   Reset to 6 columns: {new_column_names}")
                log_callback(f"   Renamed column E to '{column_name}'")
        
        # Update grades
        if log_callback:
            log_callback(f"   Updating grades...")
        
        # Create a lowercase name map for matching
        name_to_username = {}
        for idx, row in import_df.iterrows():
            first = row["First Name"].strip().lower()
            last = row["Last Name"].strip().lower()
            full_name = f"{first} {last}"
            name_to_username[full_name] = row["Username"]
        
        # Track fuzzy matches for logging
        fuzzy_match_warnings = []
        
        for idx, row in import_df.iterrows():
            user = row["Username"]
            
            # Try to find OCR-extracted grade first
            grade_value = None
            is_fuzzy_match = False
            matched_student_name = None
            
            if grades_map:
                # Match by username or by name
                first = row["First Name"].strip().lower()
                last = row["Last Name"].strip().lower()
                full_name = f"{first} {last}"
                
                # First try exact matching
                for student_name, grade_data in grades_map.items():
                    # Handle both dict format {name: {grade, confidence}} and simple format {name: grade}
                    if isinstance(grade_data, dict):
                        grade = grade_data.get('grade', '')
                    else:
                        grade = grade_data
                    
                    student_name_lower = student_name.strip().lower()
                    if student_name_lower == full_name or student_name_lower == f"{last} {first}":
                        grade_value = grade
                        matched_student_name = student_name
                        break
                
                # If exact match failed, try fuzzy matching
                if grade_value is None:
                    best_match = None
                    best_grade = None
                    best_similarity = 0
                    
                    for student_name, grade_data in grades_map.items():
                        # Handle both dict format {name: {grade, confidence}} and simple format {name: grade}
                        if isinstance(grade_data, dict):
                            grade = grade_data.get('grade', '')
                        else:
                            grade = grade_data
                        
                        student_name_lower = student_name.strip().lower()
                        
                        # Try fuzzy matching
                        if _names_match_fuzzy(student_name_lower, full_name, threshold=0.7):
                            # Calculate similarity score
                            words1 = set(student_name_lower.split())
                            words2 = set(full_name.split())
                            similarity = len(words1 & words2) / max(len(words1), len(words2)) if words1 or words2 else 0
                            
                            # Also check first+last name match (ignoring middle)
                            if len(student_name_lower.split()) >= 2 and len(full_name.split()) >= 2:
                                name_parts = student_name_lower.split()
                                csv_parts = full_name.split()
                                if name_parts[0] == csv_parts[0] and name_parts[-1] == csv_parts[-1]:
                                    similarity = max(similarity, 0.95)  # Boost for first+last match
                            
                            if similarity > best_similarity:
                                best_similarity = similarity
                                best_match = student_name
                                best_grade = grade
                    
                    if best_match and best_grade:
                        grade_value = best_grade
                        matched_student_name = best_match
                        is_fuzzy_match = True
                        fuzzy_match_warnings.append(f"   {best_match} → {full_name.title()} (fuzzy match)")
            
            # Update the grade
            if user in submitted:
                if grade_value and grade_value != "No grade found":
                    import_df.at[idx, column_name] = grade_value
                else:
                    import_df.at[idx, column_name] = "10"  # Default if OCR failed
            elif user in unreadable:
                import_df.at[idx, column_name] = "unreadable"
            else:
                import_df.at[idx, column_name] = "0"
        
        if log_callback:
            log_callback(f"   Saving to: {import_file_path}")
        
        # Save the file
        try:
            import_df.to_csv(import_file_path, index=False)
        except PermissionError:
            friendly_msg = "You might have the import file open, please close and try again!"
            if log_callback:
                log_callback(f"")
                log_callback(f"❌ {friendly_msg}")
            raise Exception(friendly_msg)
        except OSError as e:
            # Check if it's a permission denied error (errno 13)
            if e.errno == 13:
                friendly_msg = "You might have the import file open, please close and try again!"
                if log_callback:
                    log_callback(f"")
                    log_callback(f"❌ {friendly_msg}")
                raise Exception(friendly_msg)
            else:
                raise
        
        if log_callback:
            log_callback("")
            if fuzzy_match_warnings:
                log_callback("   ⚠️  Fuzzy name matches (please verify):")
                for warning in fuzzy_match_warnings:
                    log_callback(warning)
                log_callback("")
            log_callback(f"Updated grades for {len(import_df)} students")
            log_callback("")
        
        return import_df
    
    except Exception as e:
        # Don't show the error message if it's already been replaced with a friendly message
        error_msg = str(e)
        if "You might have the import file open" not in error_msg:
            if log_callback:
                log_callback(f"Error updating import file: {error_msg}")
        raise

def _names_match_fuzzy(name1, name2, threshold=0.8):
    """Check if two names match with fuzzy logic (90% similarity)"""
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
        
        # If 80% of words match, consider it a match
        similarity = matches / max(len(words1), len(words2))
        return similarity >= threshold
    
    return False

def split_combined_pdf(combined_pdf_path, import_df, extraction_folder, log_callback=None):
    """Split a combined PDF back into individual student PDFs"""
    if log_callback:
        log_callback("")
        log_callback("-" * 40)
        log_callback("SPLITTING COMBINED PDF")
        log_callback("-" * 40)
    
    try:
        # Read the combined PDF
        reader = PdfReader(combined_pdf_path)
        total_pages = len(reader.pages)
        
        if log_callback:
            log_callback(f"   Combined PDF has {total_pages} pages")
        
        # SIMPLE APPROACH: Extract names from PDF and match to folders
        if log_callback:
            log_callback(f"   Extracting student names from PDF...")
        
        # Extract names from the PDF using the EXACT same logic as the "Extract Names" function
        extracted_names = []
        name_patterns = []
        
        for page_num in range(total_pages):
            try:
                page = reader.pages[page_num]
                
                # Try multiple extraction methods
                page_text = page.extract_text()
                
                # Also try extracting text with different parameters
                try:
                    page_text_alt = page.extract_text(visitor_text=lambda text, cm, tm, fontDict, fontSize: text)
                except:
                    page_text_alt = ""
                
                # Try extracting text from specific regions (like watermarks in top-right)
                try:
                    # Extract text from top-right corner (where watermarks usually are)
                    page_text_region = page.extract_text(visitor_text=lambda text, cm, tm, fontDict, fontSize: 
                        text if tm[4] > 400 and tm[5] > 600 else "")  # Top-right region
                except:
                    page_text_region = ""
                
                # Combine all extraction methods
                all_text = (page_text or "") + " " + (page_text_alt or "") + " " + (page_text_region or "")
                
                # Debug: Show what text was extracted for first few pages
                if page_num < 5 and all_text.strip() and log_callback:
                    log_callback(f"   Page {page_num + 1} extracted text: '{all_text[:100]}...'")
                
                if all_text.strip():
                    # FIRST: Look for watermark pattern "Name (X of Y)" - this is the most reliable
                    watermark_pattern = re.search(r'(.+?)\s*\((\d+)\s+of\s+(\d+)\)', all_text, re.IGNORECASE)
                    if watermark_pattern:
                        # Extract name from watermark pattern
                        name_from_watermark = watermark_pattern.group(1).strip()
                        # Clean up the name - remove any trailing punctuation or extra text
                        name_from_watermark = re.sub(r'[^\w\s-]+$', '', name_from_watermark).strip()
                        extracted_names.append(name_from_watermark)
                        name_patterns.append(f"Page {page_num + 1}: {name_from_watermark} (from watermark)")
                        
                        if page_num < 10 and log_callback:
                            log_callback(f"   Page {page_num + 1}: Found name from watermark '{name_from_watermark}'")
                        continue
                    
                    # SECOND: Look for name patterns in lines
                    lines = all_text.split('\n')
                    potential_names = []
                    
                    for line in lines:
                        line = line.strip()
                        # Look for watermark pattern in individual lines
                        line_watermark = re.search(r'(.+?)\s*\((\d+)\s+of\s+(\d+)\)', line, re.IGNORECASE)
                        if line_watermark:
                            name = line_watermark.group(1).strip()
                            name = re.sub(r'[^\w\s-]+$', '', name).strip()
                            if len(name) > 3 and any(char.isalpha() for char in name):
                                potential_names.append(name)
                                continue
                        
                        # Look for lines that might contain student names
                        if (len(line) > 5 and len(line) < 80 and 
                            any(char.isalpha() for char in line) and
                            not line.isdigit() and
                            not line.startswith(('Page', 'of', 'Total', 'Assignment', 'Unit', 'Quiz', 'Graded')) and
                            '(' not in line or 'of' not in line):  # Avoid lines that look like watermarks but aren't parsed correctly
                            
                            words = line.split()
                            # Check if it looks like a name (2-5 words, mostly letters)
                            if len(words) >= 2 and len(words) <= 5:
                                # Check that most words are name-like (contain letters, not all numbers)
                                name_like = sum(1 for w in words if any(char.isalpha() for char in w)) >= 2
                                if name_like:
                                    potential_names.append(line)
                    
                    # Find the best name for this page
                    if potential_names:
                        # Take the first reasonable name found, but prioritize shorter names (less likely to be duplicates)
                        best_name = min(potential_names, key=len)
                        extracted_names.append(best_name)
                        name_patterns.append(f"Page {page_num + 1}: {best_name}")
                        
                        if page_num < 10 and log_callback:
                            log_callback(f"   Page {page_num + 1}: Found '{best_name}'")
                    else:
                        # LAST RESORT: Try to construct a name from words
                        all_words = all_text.split()
                        potential_name_words = []
                        
                        for word in all_words:
                            if (len(word) > 2 and any(char.isalpha() for char in word) and 
                                not word.isdigit() and not word.lower() in ['page', 'of', 'total', 'assignment', 'unit', 'quiz', 'graded', '(1', '(2', '(3', '(4']):
                                potential_name_words.append(word)
                        
                        if len(potential_name_words) >= 2:
                            # Take first 2-3 words as name (avoid duplicates)
                            constructed_name = " ".join(potential_name_words[:3])
                            extracted_names.append(constructed_name)
                            name_patterns.append(f"Page {page_num + 1}: {constructed_name} (constructed)")
                            
                            if page_num < 10 and log_callback:
                                log_callback(f"   Page {page_num + 1}: Found constructed name '{constructed_name}'")
                        else:
                            extracted_names.append(f"Unknown (Page {page_num + 1})")
                            name_patterns.append(f"Page {page_num + 1}: No name found")
                            
                            if page_num < 10 and log_callback:
                                log_callback(f"   Page {page_num + 1}: No name found")
                else:
                    extracted_names.append(f"No text (Page {page_num + 1})")
                    name_patterns.append(f"Page {page_num + 1}: No text extracted")
                    
                    if page_num < 10 and log_callback:  # Show first 10 for debugging
                        log_callback(f"   Page {page_num + 1}: No text extracted")
                        
            except Exception as e:
                extracted_names.append(f"Error (Page {page_num + 1})")
                name_patterns.append(f"Page {page_num + 1}: Error - {str(e)}")
                
                if page_num < 10 and log_callback:  # Show first 10 for debugging
                    log_callback(f"   Page {page_num + 1}: Error - {str(e)}")
        
        if log_callback:
            log_callback(f"   Extracted {len(extracted_names)} names from PDF")
            log_callback(f"   First 10 names found:")
            for i, name in enumerate(extracted_names[:10], 1):
                log_callback(f"      {i:2d}. {name}")
            if len(extracted_names) > 10:
                log_callback(f"      ... and {len(extracted_names) - 10} more")
        
        # Build a map of names from import file for validation and matching
        # Create both "First Last" and "Last First" versions for matching
        import_name_map = {}  # Maps various name formats to folder name format
        for idx, row in import_df.iterrows():
            first = row["First Name"].strip()
            last = row["Last Name"].strip()
            full_name = f"{first} {last}"  # Format used in folders
            
            # Add variations for matching
            import_name_map[full_name.lower()] = full_name
            import_name_map[f"{last} {first}".lower()] = full_name
            import_name_map[first.lower()] = full_name  # Just first name might help
            import_name_map[last.lower()] = full_name   # Just last name might help
            
            # If name has multiple words in first or last, add partial matches
            first_parts = first.split()
            last_parts = last.split()
            if len(first_parts) > 1:
                import_name_map[first_parts[0].lower()] = full_name
            if len(last_parts) > 1:
                import_name_map[last_parts[0].lower()] = full_name
        
        # Now process each student: find their folder and replace their PDF
        students_processed = 0
        current_page = 0
        
        # Group consecutive pages by student name
        current_student = None
        student_pages = []
        
        for page_num, pdf_name in enumerate(extracted_names):
            if pdf_name.startswith(("Unknown", "No text", "Error")):
                # Skip pages without valid names
                current_page += 1
                continue
            
            # Clean the extracted name - remove extra text and duplicates
            cleaned_name = pdf_name.strip()
            
            # Remove common prefixes/suffixes that might be extracted
            prefixes_to_remove = ["CamScanner", "CamScanner ", "CamScanner 10-", "CamScanner 10-09-2025", "CamScanner 10-10-2025"]
            for prefix in prefixes_to_remove:
                if cleaned_name.startswith(prefix):
                    cleaned_name = cleaned_name[len(prefix):].strip()
            
            # Remove any remaining watermark patterns
            cleaned_name = re.sub(r'\s*\(\d+\s+of\s+\d+\)', '', cleaned_name, flags=re.IGNORECASE).strip()
            
            # Remove duplicate names (e.g., "Lilli Broussard Lilli Broussard" -> "Lilli Broussard")
            # Or "Timothy Adelman Timothy Adelman" -> "Timothy Adelman"
            words = cleaned_name.split()
            
            # Check if name is duplicated (pattern: "First Last First Last")
            if len(words) >= 4:
                mid_point = len(words) // 2
                first_half = " ".join(words[:mid_point])
                second_half = " ".join(words[mid_point:])
                
                # If first and second halves are similar, it's a duplicate
                if _names_match_fuzzy(first_half, second_half, threshold=0.9):
                    cleaned_name = first_half
            
            # Try to match with import file to get correct name format
            cleaned_lower = cleaned_name.lower()
            matched_full_name = None
            
            # Try exact match first
            if cleaned_lower in import_name_map:
                matched_full_name = import_name_map[cleaned_lower]
            else:
                # Try fuzzy matching with import file names
                best_match = None
                best_score = 0
                for import_name_key, import_name_value in import_name_map.items():
                    if _names_match_fuzzy(cleaned_name, import_name_key, threshold=0.7):
                        # Calculate a simple similarity score
                        words1 = set(cleaned_lower.split())
                        words2 = set(import_name_key.split())
                        similarity = len(words1 & words2) / max(len(words1), len(words2)) if words1 or words2 else 0
                        if similarity > best_score:
                            best_score = similarity
                            best_match = import_name_value
                
                if best_match:
                    matched_full_name = best_match
            
            # Use matched name if found, otherwise use cleaned name
            final_name = matched_full_name if matched_full_name else cleaned_name
            
            # Skip if name is too short or doesn't look like a real name
            if len(final_name) < 5 or not any(char.isalpha() for char in final_name):
                continue
            
            if current_student != final_name:
                # New student found, process the previous one
                if current_student and student_pages:
                    # Find the folder for this student
                    student_folder = None
                    all_folder_names = []
                    
                    for fld in os.listdir(extraction_folder):
                        fp = os.path.join(extraction_folder, fld)
                        if not os.path.isdir(fp) or fld == "unreadable" or fld == "PDFs":
                            continue
                        
                        # Extract name from folder
                        m = re.search(r"-\s+(.*?)\s+-", fld)
                        if m:
                            folder_name = m.group(1).strip()
                            all_folder_names.append(folder_name)
                            
                            # Fuzzy matching - try multiple thresholds for better matching
                            # First try exact/first-last match (more strict)
                            if _names_match_fuzzy(current_student, folder_name, threshold=0.8):
                                student_folder = fp
                                break
                            
                            # Also try lower threshold for names that might have middle names/initials
                            if _names_match_fuzzy(current_student, folder_name, threshold=0.6):
                                # Check if first and last name match
                                words1 = current_student.lower().split()
                                words2 = folder_name.lower().split()
                                if len(words1) >= 2 and len(words2) >= 2:
                                    if words1[0] == words2[0] and words1[-1] == words2[-1]:
                                        student_folder = fp
                                        break
                    
                    if student_folder:
                        if log_callback:
                            log_callback(f"   Processing {current_student}: {len(student_pages)} pages")
                            log_callback(f"      Found folder: {os.path.basename(student_folder)}")
                        
                        # Create PDF with the student's pages
                        writer = PdfWriter()
                        for page_idx in student_pages:
                            if page_idx < total_pages:
                                writer.add_page(reader.pages[page_idx])
                        
                        # Find and replace the original PDF
                        files = os.listdir(student_folder)
                        original_pdfs = [f for f in files if f.lower().endswith(".pdf")]
                        
                        if original_pdfs:
                            target_pdf = os.path.join(student_folder, original_pdfs[0])
                            
                            if log_callback:
                                log_callback(f"      Replacing: {original_pdfs[0]}")
                            
                            with open(target_pdf, "wb") as output_file:
                                writer.write(output_file)
                            
                            if log_callback:
                                log_callback(f"   {current_student}: {len(student_pages)} pages → {original_pdfs[0]}")
                            
                            students_processed += 1
                        else:
                            if log_callback:
                                log_callback(f"   No PDF found in {current_student}'s folder")
                    else:
                        if log_callback:
                            log_callback(f"   Could not find folder for: {current_student}")
                            
                            # Try to find closest match from import file
                            closest_match = None
                            best_similarity = 0
                            for import_name_key, import_name_value in import_name_map.items():
                                if _names_match_fuzzy(current_student, import_name_value, threshold=0.6):
                                    # Calculate similarity
                                    words1 = set(current_student.lower().split())
                                    words2 = set(import_name_value.lower().split())
                                    similarity = len(words1 & words2) / max(len(words1), len(words2)) if words1 or words2 else 0
                                    if similarity > best_similarity:
                                        best_similarity = similarity
                                        closest_match = import_name_value
                            
                            if closest_match:
                                log_callback(f"      Suggested match from roster: '{closest_match}'")
                            
                            if all_folder_names:
                                # Show all folder names for debugging
                                log_callback(f"      All available folders ({len(all_folder_names)} total):")
                                # Show in chunks to avoid too long lines
                                for i in range(0, len(all_folder_names), 5):
                                    chunk = all_folder_names[i:i+5]
                                    log_callback(f"         {', '.join(chunk)}")
                                
                                # Also try to find the closest matching folder name
                                closest_folder = None
                                best_folder_sim = 0
                                for folder_name in all_folder_names:
                                    if _names_match_fuzzy(current_student, folder_name, threshold=0.5):
                                        words1 = set(current_student.lower().split())
                                        words2 = set(folder_name.lower().split())
                                        similarity = len(words1 & words2) / max(len(words1), len(words2)) if words1 or words2 else 0
                                        if similarity > best_folder_sim:
                                            best_folder_sim = similarity
                                            closest_folder = folder_name
                                
                                if closest_folder:
                                    log_callback(f"      Closest folder match: '{closest_folder}' (similarity: {best_folder_sim:.2%})")
                
                # Start new student
                current_student = final_name
                student_pages = [page_num]
            else:
                # Same student, add this page
                student_pages.append(page_num)
        
        # Process the last student
        if current_student and student_pages:
            # Find the folder for this student
            student_folder = None
            all_folder_names = []
            
            for fld in os.listdir(extraction_folder):
                fp = os.path.join(extraction_folder, fld)
                if not os.path.isdir(fp) or fld == "unreadable" or fld == "PDFs":
                    continue
                
                # Extract name from folder
                m = re.search(r"-\s+(.*?)\s+-", fld)
                if m:
                    folder_name = m.group(1).strip()
                    all_folder_names.append(folder_name)
                    
                    # Fuzzy matching - try multiple thresholds for better matching
                    # First try exact/first-last match (more strict)
                    if _names_match_fuzzy(current_student, folder_name, threshold=0.8):
                        student_folder = fp
                        break
                    
                    # Also try lower threshold for names that might have middle names/initials
                    if _names_match_fuzzy(current_student, folder_name, threshold=0.6):
                        # Check if first and last name match
                        words1 = current_student.lower().split()
                        words2 = folder_name.lower().split()
                        if len(words1) >= 2 and len(words2) >= 2:
                            if words1[0] == words2[0] and words1[-1] == words2[-1]:
                                student_folder = fp
                                break
            
            if student_folder:
                if log_callback:
                    log_callback(f"   Processing {current_student}: {len(student_pages)} pages")
                    log_callback(f"      Found folder: {os.path.basename(student_folder)}")
                
                # Create PDF with the student's pages
                writer = PdfWriter()
                for page_idx in student_pages:
                    if page_idx < total_pages:
                        writer.add_page(reader.pages[page_idx])
                
                # Find and replace the original PDF
                files = os.listdir(student_folder)
                original_pdfs = [f for f in files if f.lower().endswith(".pdf")]
                
                if original_pdfs:
                    target_pdf = os.path.join(student_folder, original_pdfs[0])
                    
                    if log_callback:
                        log_callback(f"      Replacing: {original_pdfs[0]}")
                    
                    with open(target_pdf, "wb") as output_file:
                        writer.write(output_file)
                    
                    if log_callback:
                        log_callback(f"   {current_student}: {len(student_pages)} pages → {original_pdfs[0]}")
                    
                    students_processed += 1
                else:
                    if log_callback:
                        log_callback(f"   No PDF found in {current_student}'s folder")
            else:
                if log_callback:
                    log_callback(f"   Could not find folder for: {current_student}")
                    
                    # Try to find closest match from import file
                    closest_match = None
                    best_similarity = 0
                    for import_name_key, import_name_value in import_name_map.items():
                        if _names_match_fuzzy(current_student, import_name_value, threshold=0.6):
                            # Calculate similarity
                            words1 = set(current_student.lower().split())
                            words2 = set(import_name_value.lower().split())
                            similarity = len(words1 & words2) / max(len(words1), len(words2)) if words1 or words2 else 0
                            if similarity > best_similarity:
                                best_similarity = similarity
                                closest_match = import_name_value
                    
                    if closest_match:
                        log_callback(f"      Suggested match from roster: '{closest_match}'")
                    
                    if all_folder_names:
                        # Show all folder names for debugging
                        log_callback(f"      All available folders ({len(all_folder_names)} total):")
                        # Show in chunks to avoid too long lines
                        for i in range(0, len(all_folder_names), 5):
                            chunk = all_folder_names[i:i+5]
                            log_callback(f"         {', '.join(chunk)}")
                        
                        # Also try to find the closest matching folder name
                        closest_folder = None
                        best_folder_sim = 0
                        for folder_name in all_folder_names:
                            if _names_match_fuzzy(current_student, folder_name, threshold=0.5):
                                words1 = set(current_student.lower().split())
                                words2 = set(folder_name.lower().split())
                                similarity = len(words1 & words2) / max(len(words1), len(words2)) if words1 or words2 else 0
                                if similarity > best_folder_sim:
                                    best_folder_sim = similarity
                                    closest_folder = folder_name
                        
                        if closest_folder:
                            log_callback(f"      Closest folder match: '{closest_folder}' (similarity: {best_folder_sim:.2%})")
        
        if log_callback:
            log_callback("")
            log_callback(f"Successfully split PDF for {students_processed} students")
            log_callback("")
        
        return students_processed
        
    except Exception as e:
        if log_callback:
            log_callback(f"Error splitting combined PDF: {e}")
        raise

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
        
        # Step 2: Load Import File
        import_df, import_file_path = load_import_file(class_folder_path, log_callback)
        if import_df is None:
            raise Exception("Could not load Import File.csv")
        
        result.import_file_path = import_file_path
        result.total_students = len(import_df)
        
        # Step 3: Process submissions (extract PDFs)
        submitted, unreadable, no_submission, pdf_paths, name_map, student_errors, page_counts = process_submissions(
            processing_folder, import_df, pdf_output_folder, log_callback, is_completion_process=False
        )
        
        # Step 4: Create combined PDF
        combined_pdf_path = os.path.join(pdf_output_folder, "1combinedpdf.pdf")
        create_combined_pdf(pdf_paths, name_map, combined_pdf_path, log_callback)
        result.combined_pdf_path = combined_pdf_path
        
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
            log_callback("=" * 60)
            log_callback("COMBINED PDF CREATED!")
            log_callback("Ready for grading or splitting back to individual PDFs")
            log_callback("=" * 60)
            log_callback("")
        
        return result
    
    except Exception as e:
        if log_callback:
            log_callback("")
            log_callback(f"ERROR: {str(e)}")
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
        combined_pdf_path = os.path.join(pdf_output_folder, "1combinedpdf.pdf")
        
        if log_callback:
            log_callback(f"Drive: {drive_letter}:")
            log_callback(f"Class: {class_folder_name}")
            log_callback(f"Processing folder: {processing_folder}")
            log_callback("-" * 60)
        
        # Check if combined PDF exists
        if not os.path.exists(combined_pdf_path):
            raise Exception(f"Combined PDF not found: {combined_pdf_path}")
        
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
            log_callback(f"ERROR: {str(e)}")
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
        
        # Step 2: Load Import File
        import_df, import_file_path = load_import_file(class_folder_path, log_callback)
        if import_df is None:
            raise Exception("Could not load Import File.csv")
        
        result.import_file_path = import_file_path
        result.total_students = len(import_df)
        
        # Step 3: Process submissions
        submitted, unreadable, no_submission, pdf_paths, name_map, student_errors, page_counts = process_submissions(
            processing_folder, import_df, pdf_output_folder, log_callback, is_completion_process=False
        )
        
        # Step 4: Create combined PDF
        if len(pdf_paths) == 0:
            raise Exception("Oops. You've chosen the wrong file or class. Try again.")
        
        combined_pdf_path = os.path.join(pdf_output_folder, "1combinedpdf.pdf")
        create_combined_pdf(pdf_paths, name_map, combined_pdf_path, log_callback)
        result.combined_pdf_path = combined_pdf_path
        
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
            log_callback(f"ERROR: {str(e)}")
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
        
        # Step 4: Create combined PDF
        if len(pdf_paths) == 0:
            raise Exception("Oops. You've chosen the wrong file or class. Try again.")
        
        combined_pdf_path = os.path.join(pdf_output_folder, "1combinedpdf.pdf")
        create_combined_pdf(pdf_paths, name_map, combined_pdf_path, log_callback)
        result.combined_pdf_path = combined_pdf_path
        
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
            log_callback("=" * 60)
            log_callback("COMPLETION PROCESSING COMPLETE!")
            log_callback(f"✅ Auto-assigned 10 points to {len(submitted)} submissions")
            log_callback("=" * 60)
            
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
            log_callback(f"ERROR: {str(e)}")
        raise