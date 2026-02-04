"""PDF operations for D2L Assignment Assistant."""

# Standard library
import os
import re
from io import BytesIO
from typing import Optional, Dict, List, Tuple

# Third-party
import pandas as pd
from pypdf import PdfWriter, PdfReader

# Local
from grading_constants import (
    TARGET_WIDTH, TARGET_HEIGHT,
    NAME_MATCH_THRESHOLD_VERY_HIGH, NAME_MATCH_THRESHOLD_HIGH,
    NAME_MATCH_THRESHOLD_MEDIUM, NAME_MATCH_THRESHOLD_LOW
)
from name_matching import names_match_fuzzy
from user_messages import log

# Try for watermarking
try:
    from reportlab.pdfgen import canvas
    WATERMARK_ENABLED = True
except ImportError:
    WATERMARK_ENABLED = False

# Normalization setting
NORMALIZATION_ENABLED = True


def normalize_pdf_with_pypdf(page) -> None:
    """Scale content to fit within target dimensions without cropping."""
    orig_width = float(page.mediabox.width)
    orig_height = float(page.mediabox.height)
    
    scale_x = TARGET_WIDTH / orig_width
    scale_y = TARGET_HEIGHT / orig_height
    scale = min(scale_x, scale_y)
    
    new_width = orig_width * scale
    new_height = orig_height * scale
    
    x_center = (TARGET_WIDTH - new_width) / 2
    y_center = (TARGET_HEIGHT - new_height) / 2
    
    transformation_matrix = [scale, 0, 0, scale, x_center, y_center]
    page.add_transformation(transformation_matrix)
    
    page.mediabox.lower_left = (0, 0)
    page.mediabox.upper_right = (TARGET_WIDTH, TARGET_HEIGHT)
    
    return page


def create_combined_pdf(
    pdf_paths: List[str], 
    name_map: Dict[str, str], 
    output_path: str
) -> str:
    """Create a single combined PDF with watermarks."""
    if not pdf_paths:
        raise Exception("Oops. You've chosen the wrong file or class. Try again.")
    
    log("EMPTY_LINE")
    
    writer = PdfWriter()
    
    def get_last_name(pdf_path):
        name = name_map[pdf_path]
        parts = name.split()
        return " ".join(parts[1:]).lower() if len(parts) >= 2 else name.lower()
    
    sorted_pdfs = sorted(pdf_paths, key=get_last_name)
    
    for pdf in sorted_pdfs:
        name = name_map[pdf]
        try:
            reader = PdfReader(pdf)
            num_pages = len(reader.pages)
            
            if NORMALIZATION_ENABLED:
                for page in reader.pages:
                    normalize_pdf_with_pypdf(page)
            
            for page_num, page in enumerate(reader.pages, start=1):
                if WATERMARK_ENABLED:
                    _add_watermark(page, name, page_num, num_pages)
                writer.add_page(page)
        except Exception as e:
            log("PDF_ERROR_PROCESSING", name=name, error=str(e))
    
    _set_pdf_open_action(writer)
    
    with open(output_path, "wb") as f:
        writer.write(f)
    
    log("EMPTY_LINE")
    # Extract just the filename from the full path
    filename = os.path.basename(output_path)
    log("PDF_COMBINED_SUCCESS", filename=filename)
    log("EMPTY_LINE")
    
    return output_path


def _add_watermark(page, name: str, page_num: int, total_pages: int) -> None:
    """Add watermark text to a PDF page."""
    watermark_text = f"{name} ({page_num} of {total_pages})"
    
    pkt = BytesIO()
    can = canvas.Canvas(pkt, pagesize=(TARGET_WIDTH, TARGET_HEIGHT))
    can.setFont("Helvetica-Bold", 16)
    tw = can.stringWidth(watermark_text, "Helvetica-Bold", 16)
    
    x = TARGET_WIDTH - tw - 15
    y = TARGET_HEIGHT - 25
    
    can.setFillColorRGB(0, 0, 0)
    can.drawString(x, y, watermark_text)
    can.save()
    pkt.seek(0)
    
    try:
        watermark = PdfReader(pkt).pages[0]
        page.merge_page(watermark)
    except Exception:
        pass  # Skip watermark if it fails


def _set_pdf_open_action(writer: PdfWriter) -> None:
    """Set PDF to open at page 1, fit to window."""
    try:
        from pypdf.generic import ArrayObject, NameObject
        if len(writer.pages) > 0:
            first_page = writer.pages[0]
            dest = ArrayObject([first_page.indirect_reference, NameObject("/Fit")])
            writer._root_object[NameObject("/OpenAction")] = dest
    except Exception:
        pass


def split_combined_pdf(
    combined_pdf_path: str, 
    import_df: pd.DataFrame, 
    extraction_folder: str
) -> int:
    """Split a combined PDF back into individual student PDFs."""
    from user_messages import log_raw
    
    try:
        log_raw(f"   📖 Reading PDF ({os.path.basename(combined_pdf_path)})...", "INFO")
        reader = PdfReader(combined_pdf_path)
        total_pages = len(reader.pages)
        log_raw(f"   📄 Found {total_pages} pages", "INFO")
        
        # Extract names from pages
        log_raw(f"   🔍 Extracting student names from pages...", "INFO")
        extracted_names = _extract_names_from_pages(reader, total_pages)
        
        # Validate that we found actual student names (not all "Unknown" or "No text")
        valid_names = [name for name in extracted_names if not name.startswith("Unknown") and not name.startswith("No text") and not name.startswith("Error")]
        if len(valid_names) == 0:
            log("SPLIT_WRONG_PDF")
            raise Exception("Wrong combined PDF uploaded. Try again.")
        
        log_raw(f"   ✓ Found {len(valid_names)} student submissions", "INFO")
        
        # Build name map from import file
        import_name_map = _build_import_name_map(import_df)
        
        # Process students
        log_raw(f"   ✂️ Splitting into individual PDFs...", "INFO")
        students_processed = _process_all_students(
            extracted_names, reader, total_pages, extraction_folder, 
            import_name_map
        )
        
        log_raw(f"   ✓ Created {students_processed} student PDFs", "INFO")
        
        return students_processed
        
    except Exception as e:
        log("PDF_SPLIT_ERROR", error=str(e))
        raise


def _extract_names_from_pages(
    reader: PdfReader, 
    total_pages: int
) -> List[str]:
    """Extract student names from each PDF page."""
    extracted_names = []
    
    for page_num in range(total_pages):
        name = _extract_name_from_page(reader, page_num)
        extracted_names.append(name)
    
    return extracted_names


def _extract_name_from_page(
    reader: PdfReader, 
    page_num: int
) -> str:
    """Extract student name from a single PDF page."""
    try:
        page = reader.pages[page_num]
        page_text = page.extract_text() or ""
        
        # Try alternate extraction
        try:
            page_text_alt = page.extract_text(
                visitor_text=lambda text, cm, tm, fontDict, fontSize: text
            )
        except Exception:
            page_text_alt = ""
        
        all_text = page_text + " " + (page_text_alt or "")
        
        if not all_text.strip():
            return f"No text (Page {page_num + 1})"
        
        # Look for watermark pattern "Name (X of Y)"
        watermark_match = re.search(r'(.+?)\s*\((\d+)\s+of\s+(\d+)\)', all_text, re.IGNORECASE)
        if watermark_match:
            name = watermark_match.group(1).strip()
            name = re.sub(r'[^\w\s-]+$', '', name).strip()
            return name
        
        # Fallback: look in individual lines
        for line in all_text.split('\n'):
            line = line.strip()
            line_match = re.search(r'(.+?)\s*\((\d+)\s+of\s+(\d+)\)', line, re.IGNORECASE)
            if line_match:
                name = line_match.group(1).strip()
                name = re.sub(r'[^\w\s-]+$', '', name).strip()
                if len(name) > 3 and any(char.isalpha() for char in name):
                    return name
        
        return f"Unknown (Page {page_num + 1})"
        
    except Exception as e:
        return f"Error (Page {page_num + 1})"


def _build_import_name_map(import_df: pd.DataFrame) -> Dict[str, str]:
    """Build a name lookup map from import file."""
    import_name_map = {}
    
    for idx, row in import_df.iterrows():
        first = row["First Name"].strip()
        last = row["Last Name"].strip()
        full_name = f"{first} {last}"
        
        # Add variations for matching
        import_name_map[full_name.lower()] = full_name
        import_name_map[f"{last} {first}".lower()] = full_name
        import_name_map[first.lower()] = full_name
        import_name_map[last.lower()] = full_name
        
        # Partial matches for multi-word names
        first_parts = first.split()
        last_parts = last.split()
        if len(first_parts) > 1:
            import_name_map[first_parts[0].lower()] = full_name
        if len(last_parts) > 1:
            import_name_map[last_parts[0].lower()] = full_name
    
    return import_name_map


def _process_all_students(
    extracted_names: List[str],
    reader: PdfReader,
    total_pages: int,
    extraction_folder: str,
    import_name_map: Dict[str, str]
) -> int:
    """Process all students and write their PDFs."""
    students_processed = 0
    current_student = None
    student_pages = []
    
    for page_num, pdf_name in enumerate(extracted_names):
        if pdf_name.startswith(("Unknown", "No text", "Error")):
            continue
        
        final_name = _clean_and_match_name(pdf_name, import_name_map)
        
        if len(final_name) < 5 or not any(char.isalpha() for char in final_name):
            continue
        
        if current_student != final_name:
            # Process previous student
            if current_student and student_pages:
                success = _process_student_pdf(
                    current_student, student_pages, reader, total_pages,
                    extraction_folder, import_name_map
                )
                if success:
                    students_processed += 1
            
            current_student = final_name
            student_pages = [page_num]
        else:
            student_pages.append(page_num)
    
    # Process last student
    if current_student and student_pages:
        success = _process_student_pdf(
            current_student, student_pages, reader, total_pages,
            extraction_folder, import_name_map
        )
        if success:
            students_processed += 1
    
    return students_processed


def _clean_and_match_name(pdf_name: str, import_name_map: Dict[str, str]) -> str:
    """Clean extracted name and try to match with import file."""
    cleaned_name = pdf_name.strip()
    
    # Remove common prefixes
    prefixes = ["CamScanner", "CamScanner "]
    for prefix in prefixes:
        if cleaned_name.startswith(prefix):
            cleaned_name = cleaned_name[len(prefix):].strip()
    
    # Remove watermark patterns
    cleaned_name = re.sub(r'\s*\(\d+\s+of\s+\d+\)', '', cleaned_name, flags=re.IGNORECASE).strip()
    
    # Remove duplicate names (e.g., "First Last First Last")
    words = cleaned_name.split()
    if len(words) >= 4:
        mid = len(words) // 2
        if names_match_fuzzy(" ".join(words[:mid]), " ".join(words[mid:]), threshold=NAME_MATCH_THRESHOLD_VERY_HIGH):
            cleaned_name = " ".join(words[:mid])
    
    # Try to match with import file
    cleaned_lower = cleaned_name.lower()
    if cleaned_lower in import_name_map:
        return import_name_map[cleaned_lower]
    
    # Try fuzzy matching
    best_match = None
    best_score = 0
    for key, value in import_name_map.items():
        if names_match_fuzzy(cleaned_name, key, threshold=NAME_MATCH_THRESHOLD_MEDIUM):
            words1 = set(cleaned_lower.split())
            words2 = set(key.split())
            score = len(words1 & words2) / max(len(words1), len(words2)) if words1 or words2 else 0
            if score > best_score:
                best_score = score
                best_match = value
    
    return best_match if best_match else cleaned_name


def _process_student_pdf(
    student_name: str,
    student_pages: List[int],
    reader: PdfReader,
    total_pages: int,
    extraction_folder: str,
    import_name_map: Dict[str, str]
) -> bool:
    """Process a student's pages and write to their folder. Returns success."""
    student_folder = _find_student_folder(student_name, extraction_folder)
    
    if not student_folder:
        log("PDF_NO_FOLDER_FOR", name=student_name)
        return False
    
    # Removed verbose logging: processing, folder found, replacing, complete messages
    
    # Create PDF with student's pages
    writer = PdfWriter()
    for page_idx in student_pages:
        if page_idx < total_pages:
            writer.add_page(reader.pages[page_idx])
    
    # Find and replace original PDF
    files = os.listdir(student_folder)
    original_pdfs = [f for f in files if f.lower().endswith(".pdf")]
    
    if not original_pdfs:
        log("PDF_NO_PDF_IN_FOLDER", name=student_name)
        return False
    
    target_pdf = os.path.join(student_folder, original_pdfs[0])
    
    with open(target_pdf, "wb") as f:
        writer.write(f)
    
    return True


def _find_student_folder(student_name: str, extraction_folder: str) -> Optional[str]:
    """Find the submission folder for a student."""
    for fld in os.listdir(extraction_folder):
        fp = os.path.join(extraction_folder, fld)
        if not os.path.isdir(fp) or fld in ("unreadable", "PDFs"):
            continue
        
        # Extract name from folder (format: "Submission - First Last - date")
        m = re.search(r"-\s+(.*?)\s+-", fld)
        if not m:
            continue
        
        folder_name = m.group(1).strip()
        
        # Try high threshold match
        if names_match_fuzzy(student_name, folder_name, threshold=NAME_MATCH_THRESHOLD_HIGH):
            return fp
        
        # Try lower threshold with first/last name check
        if names_match_fuzzy(student_name, folder_name, threshold=NAME_MATCH_THRESHOLD_LOW):
            words1 = student_name.lower().split()
            words2 = folder_name.lower().split()
            if len(words1) >= 2 and len(words2) >= 2:
                if words1[0] == words2[0] and words1[-1] == words2[-1]:
                    return fp
    
    return None
