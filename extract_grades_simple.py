"""Simplified grade extraction - uses modular components."""
import pandas as pd
import tempfile
import os
import platform
import subprocess
import datetime
from pdf2image import convert_from_path
from pypdf import PdfReader, PdfWriter
import numpy as np

# Import our modules
from ocr_utils import extract_text_google_vision, isolate_red_text, TESSERACT_AVAILABLE, GOOGLE_VISION_API_KEY
from grade_parser import extract_grade_from_text, extract_name_from_watermark, GRADE_SEARCH_TOP, GRADE_SEARCH_BOTTOM, GRADE_SEARCH_LEFT, GRADE_SEARCH_RIGHT

if TESSERACT_AVAILABLE:
    import pytesseract


def create_first_pages_pdf(pdf_path, log):
    """Create PDF with only first page of each student."""
    log("📑 Creating 'first pages only' PDF for quick review...")
    
    try:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        first_pages = []
        
        for i in range(len(reader.pages)):
            try:
                page_text = reader.pages[i].extract_text()
                if "(1 of" in page_text:
                    first_pages.append(i)
                    writer.add_page(reader.pages[i])
            except:
                continue
        
        if not first_pages:
            return None
        
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_path = os.path.join(os.path.dirname(pdf_path), f"{base_name}_GRADES_ONLY.pdf")
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        log(f"✅ Created grades-only PDF: {os.path.basename(output_path)}")
        log(f"   📄 Contains {len(first_pages)} student pages")
        
        return output_path
    except Exception as e:
        log(f"⚠️  Could not create first-pages PDF: {e}")
        return None


def extract_grades(pdf_path, log=lambda msg: print(msg), debug_images_folder=None):
    """Extract student names and grades from PDF."""
    log(f"📄 Reading PDF: {os.path.basename(pdf_path)}")
    
    # Create grades-only PDF
    grades_only_pdf = create_first_pages_pdf(pdf_path, log)
    pdf_to_scan = grades_only_pdf if grades_only_pdf else pdf_path
    
    log(f"✅ Google Vision API: {'Ready' if GOOGLE_VISION_API_KEY else 'Not configured'}")
    log(f"✅ Tesseract: {'Ready' if TESSERACT_AVAILABLE else 'Not available'}")
    
    # Convert PDF to images
    try:
        if os.name == 'nt':
            # Try both possible poppler paths
            poppler_paths = [
                r"C:\poppler\poppler-24.08.0\Library\bin",
                r"C:\poppler\Library\bin"
            ]
            poppler_path = None
            for path in poppler_paths:
                if os.path.exists(path):
                    poppler_path = path
                    break
            
            if poppler_path:
                # Process all pages
                pages = convert_from_path(pdf_to_scan, dpi=150, poppler_path=poppler_path)
            else:
                pages = convert_from_path(pdf_to_scan, dpi=150)
        else:
            pages = convert_from_path(pdf_to_scan, dpi=150)
        
        if len(pages) == 0:
            raise Exception("Oops. You've chosen the wrong file or class. Try again.")
        
        log(f"📊 Scanning {len(pages)} pages for grades")
    except Exception as e:
        error_msg = str(e)
        if "Could not convert PDF to images" in error_msg or "empty" in error_msg.lower():
            raise Exception("Oops. You've chosen the wrong file or class. Try again.")
        log(f"Error converting PDF: {error_msg}")
        raise Exception(f"Could not convert PDF to images: {error_msg}")
    
    results = []
    skipped_pages = []
    log("🔍 Extracting names and grades...")
    
    # Get PDF reader for watermark extraction
    try:
        pdf_reader = PdfReader(pdf_to_scan)
    except:
        pdf_reader = None
    
    for i, img in enumerate(pages):
        w, h = img.size
        
        # Extract watermark from PDF text layer
        # Watermarks follow the pattern: "Name (X of Y)" and are placed in top-right corner
        # We should ONLY extract text matching this watermark pattern, ignoring all other text
        text_top = ""
        if pdf_reader and i < len(pdf_reader.pages):
            try:
                import re
                # Extract all text from page
                all_text = pdf_reader.pages[i].extract_text()
                
                # Look ONLY for watermark pattern "Name (X of Y)" - this is the watermark format
                # This pattern is unique to watermarks and won't match instructional text
                watermark_pattern = r'(.+?)\s*\(\s*(\d+)\s+of\s+(\d+)\s*\)'
                watermark_match = re.search(watermark_pattern, all_text, re.IGNORECASE)
                
                if watermark_match:
                    # Extract ONLY the line containing the watermark pattern
                    # This ensures we only get the watermark text, not instructional text
                    lines = all_text.split('\n')
                    for line in lines:
                        if re.search(r'\(\s*\d+\s+of\s+\d+\s*\)', line):
                            text_top = line.strip()
                            break
                    
                    # If we found the pattern but couldn't extract the line, use the matched text
                    if not text_top and watermark_match:
                        text_top = watermark_match.group(0).strip()
                else:
                    # No watermark pattern found - this might not be a watermarked page
                    # Log this for debugging
                    if len(results) < 3:
                        log(f"   🔍 DEBUG: No watermark pattern found on page {i+1}")
            except Exception as e:
                # If extraction fails, log but continue
                if len(results) < 3:
                    log(f"   🔍 DEBUG: Error extracting watermark: {e}")
                pass
        
        # Check if first page
        if "(1 of" not in text_top:
            skipped_pages.append((i+1, "Not a first page (no '(1 of' marker)"))
            continue
        
        log(f"🔍 Processing page {i+1} (first page of student)...")
        
        # Extract name from watermark text
        # Only use watermark text (which has pattern "Name (X of Y)") - don't use OCR fallback
        # as it could pick up instructional text from the page
        name = extract_name_from_watermark(text_top, log, debug=len(results) < 3)
        
        # Note: We don't use OCR fallback for name extraction because:
        # 1. The watermark should be in the PDF text layer (extracted above)
        # 2. OCR on the image could pick up instructional text from the page
        # 3. If watermark extraction fails, we'll label it as "Unknown Student" instead
        
        # Crop grade region
        crop_left = int(w * GRADE_SEARCH_LEFT)
        crop_right = int(w * GRADE_SEARCH_RIGHT)
        crop_top = int(h * GRADE_SEARCH_TOP)
        crop_bottom = int(h * GRADE_SEARCH_BOTTOM)
        grade_img = img.crop((crop_left, crop_top, crop_right, crop_bottom))
        
        # Try red text isolation
        grade_img_red = isolate_red_text(grade_img)
        red_array = np.array(grade_img_red)
        very_dark_count = np.sum(red_array < 100)
        
        # Use red-filtered if enough dark pixels found
        grade_img_processed = grade_img_red if very_dark_count >= 50 else grade_img
        
        # Save debug images
        if debug_images_folder and name:
            try:
                os.makedirs(debug_images_folder, exist_ok=True)
                import re
                safe_name = re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')
                grade_img.save(os.path.join(debug_images_folder, f"{safe_name}_crop.png"))
                grade_img_processed.save(os.path.join(debug_images_folder, f"{safe_name}_red_only.png"))
            except:
                pass
        
        # OCR
        grade_text, confidence = extract_text_google_vision(grade_img_processed, return_confidence=True)
        
        if not grade_text and TESSERACT_AVAILABLE:
            try:
                custom_config = r'--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789./'
                grade_text = pytesseract.image_to_string(grade_img_processed, config=custom_config).strip()
                confidence = 0.5  # Tesseract doesn't provide confidence, assume medium
            except:
                grade_text = None
                confidence = 0.0
        
        # Extract grade
        grade = extract_grade_from_text(grade_text or "")
        
        # Validate name - reject if it looks like instructions or gibberish
        if name:
            name_lower = name.lower()
            # Reject if contains common instruction words
            instruction_words = ['submit', 'scan', 'midnight', 'tonight', 'key', 'video', 'posted', 
                              'tomorrow', 'points', 'must', 'please', 'instructions', 'you']
            if any(word in name_lower for word in instruction_words):
                log(f"   ⚠️  Warning: Rejected invalid name '{name}' (contains instruction words)")
                name = None
            
            # Reject if name is too long (likely a sentence)
            if name and len(name) > 50:
                log(f"   ⚠️  Warning: Rejected invalid name '{name}' (too long)")
                name = None
            
            # Reject if name has too many short words (likely OCR gibberish)
            if name:
                words = name.split()
                short_words = sum(1 for w in words if len(w) <= 2)
                if len(words) > 3 and short_words > len(words) * 0.5:
                    log(f"   ⚠️  Warning: Rejected invalid name '{name}' (too many short words)")
                    name = None
        
        if not name:
            name = f"Unknown Student (Page {i+1})"
            log(f"   ⚠️  Warning: Could not extract valid name from page {i+1}")
        
        log(f"   ✅ Name: {name}")
        log(f"   📊 Grade: {grade} (confidence: {confidence:.2f})")
        if grade_text:
            log(f"   🔍 OCR text: '{grade_text}'")
        else:
            log(f"   ⚠️  Warning: No OCR text extracted")
        
        # Track if grade extraction failed
        if not grade or grade == "No grade found":
            log(f"   ⚠️  Warning: Could not extract grade for {name}")
        
        results.append({
            "Student Name": name, 
            "Grade": grade,
            "Grade Raw": grade_text or "",  # Add raw OCR text
            "Confidence": confidence,
            "Page": i+1
        })
    
    if not results:
        log("⚠️  No student pages found")
        if skipped_pages:
            log(f"   Skipped {len(skipped_pages)} pages that were not first pages")
        return None
    
    # Process results
    log(f"✅ Extraction complete! Processed {len(results)} students.")
    
    if skipped_pages:
        log(f"   ⚠️  Skipped {len(skipped_pages)} pages (not first pages of students)")
    
    if grades_only_pdf:
        log(f"📑 Grades-only PDF created: {os.path.basename(grades_only_pdf)}")
    
    log("")
    log("📋 EXTRACTED GRADES:")
    for i, result in enumerate(results, 1):
        conf = result['Confidence']
        conf_indicator = "✅" if conf >= 0.7 else "⚠️" if conf >= 0.4 else "❌"
        log(f"   {i:2d}. {result['Student Name']}: {result['Grade']} {conf_indicator} (confidence: {conf:.2f})")
    
    # Return results as a dict with grades and confidence scores
    # Format: {name: {"grade": "XX.X", "grade_raw": "raw text", "confidence": 0.XX}}
    grades_dict = {
        r['Student Name']: {
            "grade": r['Grade'], 
            "grade_raw": r['Grade Raw'],
            "confidence": r['Confidence']
        } 
        for r in results
    }
    return grades_dict

