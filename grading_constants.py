"""Constants for D2L Assignment Assistant - no logic, just values."""

# PDF Settings
TARGET_WIDTH = 612
TARGET_HEIGHT = 792

# Name Matching Thresholds
NAME_MATCH_THRESHOLD_VERY_HIGH = 0.9
NAME_MATCH_THRESHOLD_HIGH = 0.8
NAME_MATCH_THRESHOLD_MEDIUM = 0.7
NAME_MATCH_THRESHOLD_LOW = 0.6
NAME_MATCH_THRESHOLD_VERY_LOW = 0.5
MINIMUM_MATCH_RATE = 0.3

# Page Thresholds
PAGE_COUNT_WARNING_RATIO = 0.7

# OCR Confidence Levels
CONFIDENCE_HIGH = 0.7
CONFIDENCE_MEDIUM = 0.4

# Import File Structure
REQUIRED_COLUMNS_COUNT = 5  # OrgDefinedId, Username, First Name, Last Name, Email
END_OF_LINE_COLUMN_INDEX = 5  # Column index for End-of-Line Indicator (0-indexed)

# Submission Matching
MIN_UNMATCHED_COUNT = 3  # Minimum unmatched submissions before raising error

# OCR Image Processing Thresholds
MIN_RED_PIXELS_THRESHOLD = 50  # Minimum red pixels to consider text as "red handwritten"
GRAYSCALE_DARK_THRESHOLD = 180  # Pixels darker than this are considered "dark"
BRIGHTNESS_THRESHOLD = 200  # Max brightness to consider as text
RED_DOMINANCE_OFFSET = 20  # How much redder R must be than G and B
RED_COMBINED_OFFSET = 30  # Offset for R vs (G+B)/2 comparison
CONTRAST_ENHANCE_FACTOR = 2.0  # Initial contrast enhancement
CONTRAST_ENHANCE_FINAL = 2.5  # Final contrast enhancement for result

# API Settings
API_TIMEOUT_SECONDS = 10  # Timeout for external API calls (e.g., Google Vision)