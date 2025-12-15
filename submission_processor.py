"""Submission processing for D2L Assignment Assistant."""

# Standard library
import os
import re
import shutil
from datetime import datetime
from typing import Optional, Dict, List, Tuple, Set, Any

# Third-party
import pandas as pd
from pypdf import PdfWriter, PdfReader

# Local
from grading_constants import PAGE_COUNT_WARNING_RATIO, MINIMUM_MATCH_RATE, MIN_UNMATCHED_COUNT
from user_messages import log


def process_submissions(
    extraction_folder: str,
    import_df: pd.DataFrame,
    pdf_output_folder: str,
    unreadable_folder: str,
    is_completion_process: bool = False
) -> Tuple[Set[str], Set[str], Set[str], List[str], Dict[str, str], List[str], Dict[str, int]]:
    """
    Process all student submissions.
    
    Returns:
        Tuple of (submitted, unreadable, no_submission, pdf_paths, name_map, student_errors, page_counts)
    """
    log("EMPTY_LINE")
    log("SEPARATOR_LINE")
    log("SUBMISSION_PROCESSING_HEADER")
    log("SEPARATOR_LINE")
    
    # Prepare student data
    import_df["Last Name"] = import_df["Last Name"].str.strip().str.lower()
    import_df["First Name"] = import_df["First Name"].str.strip().str.lower()
    
    # Initialize tracking sets and dicts
    submitted = set()
    unreadable = set()
    no_submission = set()
    pdf_paths = []
    name_map = {}
    multiple_pdf_students = []
    student_errors = []
    page_counts = {}
    
    # Create PDF output folder
    os.makedirs(pdf_output_folder, exist_ok=True)
    _clear_old_pdfs(pdf_output_folder)
    
    # Group submissions by student, keeping only latest
    submission_map, newer_submissions = _build_submission_map(extraction_folder)
    
    log("EMPTY_LINE")
    log("SUBMISSION_FOUND_UNIQUE", count=len(submission_map))
    
    # Log any duplicate submissions that were replaced
    for name in newer_submissions:
        log("SUBMISSION_NEWER_FOUND", name=name)
    
    log("EMPTY_LINE")
    
    # Process each submission
    unmatched_count = 0
    for name, (fld, timestamp) in submission_map.items():
        fp = os.path.join(extraction_folder, fld)
        
        # Match to roster
        user, hit = _match_student_to_roster(name, import_df)
        if not user:
            unmatched_count += 1
            student_errors.append(f"{name}: Could not match to roster")
            log("SUBMISSION_NO_MATCH", name=name)
            continue
        
        # Process files
        result = _process_student_files(
            name, fp, user, pdf_output_folder,
            is_completion_process
        )
        
        if result["status"] == "submitted":
            pdf_paths.append(result["pdf_path"])
            name_map[result["pdf_path"]] = name
            submitted.add(user)
            if result.get("page_count"):
                page_counts[name] = result["page_count"]
            if result.get("multiple_pdfs"):
                multiple_pdf_students.append(name)
        elif result["status"] == "unreadable":
            unreadable.add(user)
            student_errors.append(result["error"])
        else:
            no_submission.add(user)
            student_errors.append(result["error"])
        
        if result.get("errors"):
            student_errors.extend(result["errors"])
    
    # Move unreadable submissions to the designated unreadable folder
    _move_unreadable_submissions(extraction_folder, import_df, unreadable, unreadable_folder)
    
    # Log summary
    if multiple_pdf_students:
        log("EMPTY_LINE")
        log("SUBMISSION_MULTIPLE_PDFS_HEADER")
        for student_name in multiple_pdf_students:
            log("SUBMISSION_MULTIPLE_PDF_ITEM", name=student_name)
    
    # Flag students with fewer pages than average
    _check_page_counts(page_counts, student_errors)
    
    # Validation
    _validate_submission_match_rate(submission_map, submitted, unmatched_count)
    
    return submitted, unreadable, no_submission, pdf_paths, name_map, student_errors, page_counts


def _clear_old_pdfs(pdf_output_folder: str) -> None:
    """Remove old PDFs from output folder."""
    for f in os.listdir(pdf_output_folder):
        if f.lower().endswith(".pdf"):
            os.remove(os.path.join(pdf_output_folder, f))


def _parse_folder_timestamp(folder_name: str) -> Optional[datetime]:
    """Parse timestamp from Canvas folder name."""
    try:
        match = re.search(r"-\s+(.*?)\s+-\s+(.+)$", folder_name)
        if not match:
            return None
        
        date_str = match.group(2).strip()
        
        date_formats = [
            "%b %d, %Y %I%M %p",
            "%b %d, %Y %I:%M %p",
            "%B %d, %Y %I%M %p",
            "%B %d, %Y %I:%M %p",
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    except (ValueError, AttributeError, IndexError):
        return None


def _build_submission_map(
    extraction_folder: str
) -> Dict[str, Tuple[str, Optional[datetime]]]:
    """Group submissions by student name, keeping only the latest."""
    submission_map = {}
    newer_submissions = []  # Track which ones were replaced
    
    for fld in os.listdir(extraction_folder):
        fp = os.path.join(extraction_folder, fld)
        if not os.path.isdir(fp):
            continue
        
        m = re.search(r"-\s+(.*?)\s+-", fld)
        if not m:
            continue
        
        name = m.group(1).strip()
        timestamp = _parse_folder_timestamp(fld)
        
        if name in submission_map:
            existing_folder, existing_timestamp = submission_map[name]
            if timestamp and existing_timestamp and timestamp > existing_timestamp:
                submission_map[name] = (fld, timestamp)
                newer_submissions.append(name)  # Track for logging later
            elif timestamp and not existing_timestamp:
                submission_map[name] = (fld, timestamp)
        else:
            submission_map[name] = (fld, timestamp)
    
    return submission_map, newer_submissions


def _match_standard_format(name: str, import_df: pd.DataFrame) -> pd.DataFrame:
    """
    Strategy 1: Standard "First Last" format.
    
    First word = first name, remaining words = last name.
    Example: "John Smith" → first="john", last="smith"
    """
    parts = name.split()
    if len(parts) < 2:
        return pd.DataFrame()
    
    first = parts[0].lower()
    last = " ".join(parts[1:]).lower()
    return import_df[(import_df["First Name"] == first) & (import_df["Last Name"] == last)]


def _match_multiword_first_name(name: str, import_df: pd.DataFrame) -> pd.DataFrame:
    """
    Strategy 2: Multi-word first name (for names with 3+ parts).
    
    All but last word = first name, last word = last name.
    Example: "Mary Ann Smith" → first="mary ann", last="smith"
    """
    parts = name.split()
    if len(parts) < 3:
        return pd.DataFrame()
    
    first = " ".join(parts[:-1]).lower()
    last = parts[-1].lower()
    return import_df[(import_df["First Name"] == first) & (import_df["Last Name"] == last)]


def _match_hyphen_variations(name: str, import_df: pd.DataFrame) -> pd.DataFrame:
    """
    Strategy 3: Hyphen variations.
    
    Tries both space-separated and hyphen-joined versions of last name.
    Example: "Bob Johnson Williams" matches "Bob Johnson-Williams"
    """
    parts = name.split()
    if len(parts) < 2:
        return pd.DataFrame()
    
    first = parts[0].lower()
    last = " ".join(parts[1:]).lower()
    last_hyphen = "-".join(parts[1:]).lower()
    return import_df[
        (import_df["First Name"] == first) & 
        ((import_df["Last Name"] == last) | (import_df["Last Name"] == last_hyphen))
    ]


def _match_fuzzy_parts(
    name: str, 
    import_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Strategy 4: Fuzzy part matching (fallback).
    
    Finds roster entries sharing at least 2 name parts.
    Picks the one with most matching parts.
    Example: "Jose Garcia" matches "Jose Garcia Lopez"
    """
    parts = name.split()
    if len(parts) < 2:
        return pd.DataFrame()
    
    student_name_parts = set([p.lower().strip() for p in parts if p.strip()])
    matching_rows = []
    
    for idx, row in import_df.iterrows():
        roster_first = str(row["First Name"]).lower().strip() if pd.notna(row["First Name"]) else ""
        roster_last = str(row["Last Name"]).lower().strip() if pd.notna(row["Last Name"]) else ""
        
        roster_parts = set()
        roster_parts.update([p.strip() for p in roster_first.split() if p.strip()])
        roster_parts.update([p.strip() for p in roster_last.split() if p.strip()])
        
        matching_parts = student_name_parts.intersection(roster_parts)
        if len(matching_parts) >= 2:
            matching_rows.append((idx, len(matching_parts)))
    
    if matching_rows:
        matching_rows.sort(key=lambda x: x[1], reverse=True)
        best_idx = matching_rows[0][0]
        hit = import_df.iloc[[best_idx]]
        roster_name = f"{hit.iloc[0]['First Name']} {hit.iloc[0]['Last Name']}"
        log("SUBMISSION_NAME_PARTS_MATCH", name=name, roster_name=roster_name)
        return hit
    
    return pd.DataFrame()


def _match_student_to_roster(
    name: str,
    import_df: pd.DataFrame
) -> Tuple[Optional[str], Optional[pd.DataFrame]]:
    """
    Match student name from submission folder to roster.
    
    Uses 4 strategies in order, stopping when exactly one match is found:
    
    Strategy 1: Standard "First Last" format
        - First word = first name, remaining words = last name
        - Example: "John Smith" → first="john", last="smith"
        
    Strategy 2: Multi-word first name (for names with 3+ parts)
        - All but last word = first name, last word = last name  
        - Example: "Mary Ann Smith" → first="mary ann", last="smith"
        
    Strategy 3: Hyphen variations
        - Tries both space-separated and hyphen-joined versions of last name
        - Example: "Bob Johnson Williams" matches "Bob Johnson-Williams"
        
    Strategy 4: Fuzzy part matching (fallback)
        - Finds roster entries sharing at least 2 name parts
        - Picks the one with most matching parts
        - Example: "Jose Garcia" matches "Jose Garcia Lopez"
    
    Args:
        name: Student name extracted from submission folder
        import_df: Roster DataFrame with "First Name", "Last Name", "Username" columns
    
    Returns:
        Tuple of (username, matching_row) or (None, None) if no unique match found
    """
    # Strategy 1: Standard format
    hit = _match_standard_format(name, import_df)
    
    # Strategy 2: Multi-word first name
    if len(hit) != 1:
        hit = _match_multiword_first_name(name, import_df)
    
    # Strategy 3: Hyphen variations
    if len(hit) != 1:
        hit = _match_hyphen_variations(name, import_df)
    
    # Strategy 4: Fuzzy part matching
    if len(hit) != 1:
        hit = _match_fuzzy_parts(name, import_df)
    
    if len(hit) != 1:
        return None, None
    
    return hit.iloc[0]["Username"], hit


def _process_student_files(
    name: str,
    folder_path: str,
    user: str,
    pdf_output_folder: str,
    is_completion_process: bool
) -> Dict[str, Any]:
    """Process files for a single student. Returns result dict."""
    files = os.listdir(folder_path)
    pdfs = [f for f in files if f.lower().endswith(".pdf")]
    result = {"errors": []}
    
    if pdfs:
        dst = os.path.join(pdf_output_folder, f"{user}.pdf")
        
        if len(pdfs) == 1:
            result.update(_process_single_pdf(name, folder_path, pdfs[0], dst, is_completion_process))
        else:
            result.update(_process_multiple_pdfs(name, folder_path, pdfs, dst, is_completion_process))
        
        result["pdf_path"] = dst
        result["status"] = "submitted"
    else:
        others = [f for f in files if not f.lower().endswith(".pdf")]
        if others:
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
            has_image = any(f.lower().endswith(tuple(image_extensions)) for f in others)
            file_type = "image file" if has_image else "non-PDF file"
            result["status"] = "unreadable"
            result["error"] = f"{name}: {file_type} → unreadable"
            log("SUBMISSION_ERROR", error=result['error'])
        else:
            result["status"] = "no_submission"
            result["error"] = f"{name}: No submission"
            if is_completion_process:
                log("SUBMISSION_NO_SUB_POINTS", name=name)
            else:
                log("SUBMISSION_NO_SUB", name=name)
    
    return result


def _process_single_pdf(
    name: str,
    folder_path: str,
    pdf_file: str,
    dst: str,
    is_completion_process: bool
) -> Dict[str, Any]:
    """Process a single PDF file."""
    result = {"errors": []}
    src_pdf = os.path.join(folder_path, pdf_file)
    shutil.copy(src_pdf, dst)
    
    try:
        reader = PdfReader(src_pdf)
        result["page_count"] = len(reader.pages)
    except Exception as e:
        result["errors"].append(f"{name}: Error reading PDF page count: {e}")
    
    if is_completion_process:
        log("SUBMISSION_PDF_FOUND_POINTS", name=name)
    else:
        log("SUBMISSION_PDF_FOUND", name=name)
    
    return result


def _process_multiple_pdfs(
    name: str,
    folder_path: str,
    pdfs: List[str],
    dst: str,
    is_completion_process: bool
) -> Dict[str, Any]:
    """Process multiple PDFs by combining them."""
    result = {"errors": [], "multiple_pdfs": True}
    
    if is_completion_process:
        log("SUBMISSION_MULTI_PDF_POINTS", name=name, count=len(pdfs))
    else:
        log("SUBMISSION_MULTI_PDF", name=name, count=len(pdfs))
    
    try:
        combined_writer = PdfWriter()
        total_pages = 0
        
        for pdf_file in sorted(pdfs):
            pdf_path = os.path.join(folder_path, pdf_file)
            try:
                reader = PdfReader(pdf_path)
                total_pages += len(reader.pages)
                for page in reader.pages:
                    combined_writer.add_page(page)
            except Exception as e:
                result["errors"].append(f"{name}: Error reading {pdf_file}: {e}")
        
        result["page_count"] = total_pages
        
        with open(dst, "wb") as f:
            combined_writer.write(f)
            
    except Exception as e:
        result["errors"].append(f"{name}: Error combining PDFs: {e}")
        # Fallback: use first PDF
        try:
            shutil.copy(os.path.join(folder_path, pdfs[0]), dst)
            reader = PdfReader(os.path.join(folder_path, pdfs[0]))
            result["page_count"] = len(reader.pages)
        except Exception as e2:
            result["errors"].append(f"{name}: Error with fallback PDF: {e2}")
    
    return result


def _move_unreadable_submissions(
    extraction_folder: str,
    import_df: pd.DataFrame,
    unreadable: Set[str],
    unreadable_folder: str
) -> None:
    """Move unreadable submissions to separate folder."""
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


def _check_page_counts(page_counts: Dict[str, int], student_errors: List[str]) -> None:
    """Flag students with fewer pages than average."""
    if not page_counts:
        return
    
    avg_pages = sum(page_counts.values()) / len(page_counts)
    for name, page_count in page_counts.items():
        if page_count < avg_pages * PAGE_COUNT_WARNING_RATIO:
            student_errors.append(
                f"{name}: Has only {page_count} page(s), below average of {avg_pages:.1f} pages"
            )


def _validate_submission_match_rate(
    submission_map: Dict,
    submitted: Set[str],
    unmatched_count: int
) -> None:
    """Validate that we matched enough submissions."""
    if len(submission_map) == 0:
        return
    
    match_rate = len(submitted) / len(submission_map)
    
    if match_rate < MINIMUM_MATCH_RATE and unmatched_count > MIN_UNMATCHED_COUNT:
        raise Exception("Oops. You've chosen the wrong file or class. Try again.")
    
    if len(submitted) == 0 and len(submission_map) > 0:
        raise Exception("Oops. You've chosen the wrong file or class. Try again.")
