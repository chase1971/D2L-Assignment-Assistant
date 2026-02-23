"""OCR utility functions for grade extraction."""
import io
import requests
import base64
import os
from PIL import Image, ImageEnhance
import numpy as np

from grading_constants import (
    API_TIMEOUT_SECONDS,
    MIN_RED_PIXELS_THRESHOLD,
    GRAYSCALE_DARK_THRESHOLD,
    BRIGHTNESS_THRESHOLD,
    RED_DOMINANCE_OFFSET,
    RED_COMBINED_OFFSET,
    CONTRAST_ENHANCE_FACTOR,
    CONTRAST_ENHANCE_FINAL,
)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, continue anyway

# Google Cloud Vision API Key - loaded from environment variable
GOOGLE_VISION_API_KEY = os.getenv("GOOGLE_VISION_API_KEY", "")

# Try to import Tesseract
try:
    import pytesseract
    if os.name == 'nt':
        tesseract_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
        ]
        for path in tesseract_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                break
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


def extract_text_google_vision(img, return_confidence=False):
    """Use Google Cloud Vision API to extract text from image."""
    if not GOOGLE_VISION_API_KEY:
        return (None, 0.0) if return_confidence else None
    
    try:
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        image_base64 = base64.b64encode(img_byte_arr).decode('utf-8')
        
        url = f"https://vision.googleapis.com/v1/images:annotate?key={GOOGLE_VISION_API_KEY}"
        request_body = {
            "requests": [{
                "image": {"content": image_base64},
                "features": [{"type": "DOCUMENT_TEXT_DETECTION"}]
            }]
        }
        
        response = requests.post(url, json=request_body, timeout=API_TIMEOUT_SECONDS)
        
        if response.status_code != 200:
            # Log API errors
            print(f"[DEBUG] Google Vision API error: {response.status_code} - {response.text[:200]}")
            return (None, 0.0) if return_confidence else None
        
        result = response.json()
        if 'responses' in result and len(result['responses']) > 0:
            if 'textAnnotations' in result['responses'][0]:
                text = result['responses'][0]['textAnnotations'][0]['description'].strip()
                
                confidence = 0.0
                if 'fullTextAnnotation' in result['responses'][0]:
                    pages = result['responses'][0]['fullTextAnnotation'].get('pages', [])
                    confidences = []
                    for page in pages:
                        for block in page.get('blocks', []):
                            if 'confidence' in block:
                                confidences.append(block['confidence'])
                    if confidences:
                        confidence = sum(confidences) / len(confidences)
                
                if return_confidence:
                    return (text, confidence)
                return text
        
        return (None, 0.0) if return_confidence else None
    except Exception as e:
        print(f"[DEBUG] Google Vision API exception: {e}")
        return (None, 0.0) if return_confidence else None


def isolate_red_text(img):
    """Isolate ONLY red handwritten text from the image."""
    if img.mode != 'RGB':
        img_gray = img.convert('L')
        img_array = np.array(img_gray)
        dark_mask = img_array < GRAYSCALE_DARK_THRESHOLD
        
        result = np.ones_like(img_array) * 255
        result[dark_mask] = img_array[dark_mask]
        
        result_img = Image.fromarray(result.astype('uint8'))
        enhancer = ImageEnhance.Contrast(result_img)
        return enhancer.enhance(CONTRAST_ENHANCE_FACTOR)
    
    img_array = np.array(img)
    
    r = img_array[:, :, 0].astype(float)
    g = img_array[:, :, 1].astype(float)
    b = img_array[:, :, 2].astype(float)
    
    red_mask = ((r > g + RED_DOMINANCE_OFFSET) & (r > b + RED_DOMINANCE_OFFSET)) | (r > (g + b) / 2 + RED_COMBINED_OFFSET)
    brightness = (r + g + b) / 3
    dark_enough = brightness < BRIGHTNESS_THRESHOLD
    final_mask = red_mask & dark_enough
    
    red_pixel_count = np.sum(final_mask)
    
    if red_pixel_count < MIN_RED_PIXELS_THRESHOLD:
        gray = (r + g + b) / 3
        dark_mask = gray < GRAYSCALE_DARK_THRESHOLD
        result = np.ones_like(img_array) * 255
        result[dark_mask] = [0, 0, 0]
    else:
        result = np.ones_like(img_array) * 255
        result[final_mask] = [0, 0, 0]
    
    result_img = Image.fromarray(result.astype('uint8'))
    result_gray = result_img.convert('L')
    enhancer = ImageEnhance.Contrast(result_gray)
    result_gray = enhancer.enhance(CONTRAST_ENHANCE_FINAL)
    
    return result_gray

