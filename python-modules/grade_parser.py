"""Grade parsing utilities."""
import re

# Grade search region settings
GRADE_SEARCH_TOP = 0.00
GRADE_SEARCH_BOTTOM = 0.15
GRADE_SEARCH_LEFT = 0.30
GRADE_SEARCH_RIGHT = 0.70


def extract_grade_from_text(text):
    """Extract grade from OCR text with smart OCR mistake handling."""
    if not text:
        return "No grade found"
    
    # Clean up common OCR mistakes
    text = text.replace(',', '.')
    text = text.replace('o', '0')  # o -> 0
    text = text.replace('O', '0')  # O -> 0
    text = text.replace('l', '1')  # l -> 1
    text = text.replace('I', '1')  # I -> 1
    text = text.replace('s', '5')  # s -> 5 (common mistake)
    text = text.replace('S', '5')  # S -> 5
    text = text.replace('g', '9')  # g -> 9
    text = text.replace('G', '9')  # G -> 9
    text = text.replace('b', '6')  # b -> 6
    text = text.replace('B', '6')  # B -> 6
    text = text.replace('Z', '2')  # Z -> 2
    text = text.replace('z', '2')  # z -> 2
    
    # Look for fraction format
    match = re.search(r'(\d+\.?\d*)\s*/\s*(\d+)', text)
    if match:
        return f"{match.group(1)}/{match.group(2)}"
    
    # Look for percentage
    match = re.search(r'(\d+\.?\d*)\s*%', text)
    if match:
        return f"{match.group(1)}%"
    
    # Look for decimal numbers
    decimal_numbers = re.findall(r'(\d+\.\d+)', text)
    if decimal_numbers:
        for num in decimal_numbers:
            val = float(num)
            if 0 <= val <= 100:
                return num
    
    # Look for whole numbers (prefer two-digit)
    whole_numbers = re.findall(r'\b(\d+)\b', text)
    if whole_numbers:
        for num in whole_numbers:
            val = float(num)
            if 10 <= val <= 100:
                return num
        
        for num in whole_numbers:
            val = float(num)
            if 0 <= val <= 9:
                return num
    
    # If no numbers found, try to extract any digit sequence
    digit_sequences = re.findall(r'\d+', text)
    if digit_sequences:
        for seq in digit_sequences:
            val = float(seq)
            if 0 <= val <= 100:
                return seq
    
    return "No grade found"


def extract_name_from_watermark(text_top, log=None, debug=False):
    """Extract student name from watermark text."""
    name = None
    
    # First, check if this is a student page (has "(1 of X)" marker)
    has_student_marker = "(1 of" in text_top or "( 1 of" in text_top
    
    if not has_student_marker:
        if debug and log:
            log(f"   🔍 DEBUG: Page doesn't have student marker '(1 of X)'")
        return None
    
    # Words/phrases that indicate this is NOT a name (instructional text, etc.)
    excluded_phrases = [
        'page', 'camscanner', 'unit', 'quiz', 'graded', 'submit', 'scan', 
        'midnight', 'tonight', 'key', 'video', 'posted', 'tomorrow', 'points',
        'name:', 'you must', 'must submit', 'scan in', 'will be posted',
        'submit and scan', 'points name', 'instructions', 'please'
    ]
    
    # Look for lines that look like names (2-4 words, mostly capitalized words)
    for line in text_top.splitlines():
        line = line.strip()
        
        # Skip if line contains excluded phrases
        line_lower = line.lower()
        if any(phrase in line_lower for phrase in excluded_phrases):
            continue
        
        # Skip very long lines (likely instructional text)
        if len(line) > 50:
            continue
        
        # Skip lines with too many words (likely sentences, not names)
        word_count = len(line.split())
        if word_count > 5:
            continue
        
        # Look for lines with letters that could be names
        if re.search(r"[A-Za-z]{2,}", line) and len(line) > 5:
            original_line = line
            # Remove "(1 of X)" pattern
            name = re.sub(r'\(\d+\s+of\s+\d+\)', '', line).strip()
            name = re.sub(r'^[^A-Za-z]+|[^A-Za-z]+$', '', name).strip()
            name = re.sub(r'[^A-Za-z\s]', ' ', name).strip()
            name = re.sub(r'\s+', ' ', name)
            
            # Additional validation: name should be 2-4 words, mostly letters
            name_words = name.split()
            if len(name_words) < 2 or len(name_words) > 4:
                if debug and log:
                    log(f"   🔍 DEBUG: Skipping '{name}' - wrong word count ({len(name_words)})")
                continue
            
            # Check if most words are reasonable length (names are usually 2-15 chars)
            valid_words = sum(1 for w in name_words if 2 <= len(w) <= 15)
            if valid_words < len(name_words) * 0.7:  # At least 70% of words should be valid length
                if debug and log:
                    log(f"   🔍 DEBUG: Skipping '{name}' - words don't look like names")
                continue
            
            if debug and log and name:
                log(f"   🔍 DEBUG: Name extraction: '{original_line}' → '{name}'")
            
            if len(name) > 3:
                return name
    
    if debug and log:
        log(f"   🔍 DEBUG: Could not extract name from watermark text")
    return None

