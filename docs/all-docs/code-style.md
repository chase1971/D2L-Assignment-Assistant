# Code Style and Best Practices

## Python Style Guidelines

### General Principles
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write self-documenting code with clear variable names
- Keep functions focused on single responsibilities
- Maximum line length: 100 characters

### Naming Conventions

```python
# Classes: PascalCase
class D2LDateProcessor:
    pass

# Functions and methods: snake_case
def process_csv_file():
    pass

# Constants: UPPER_SNAKE_CASE
D2L_BASE_URL = "https://d2l.example.com"
LOGS_DIR = "debug_logs"

# Private methods: _leading_underscore
def _parse_time_str(time_str):
    pass

# Variables: snake_case
assignment_name = "Homework 1"
due_date = "2025-12-31"
```

### Import Organization

```python
# Standard library imports
import os
import sys
import csv
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict

# Third-party imports
import pandas as pd
from selenium import webdriver
from playwright.async_api import async_playwright

# Local imports
from .utils import helper_function
```

## Documentation Standards

### Docstring Format
Use Google-style docstrings:

```python
def set_assignment_due_date(assignment_name: str, due_date: str, due_time: str) -> bool:
    """
    Set the due date for a specific assignment in D2L.

    Args:
        assignment_name: Name of the assignment to update
        due_date: Due date in YYYY-MM-DD format
        due_time: Due time in HH:MM format (24-hour)

    Returns:
        True if successful, False otherwise

    Raises:
        ValueError: If date/time format is invalid
        ElementNotFoundError: If assignment cannot be located

    Example:
        >>> set_assignment_due_date("Homework 1", "2025-12-31", "23:59")
        True
    """
    # Implementation here
    pass
```

### Inline Comments
- Use comments to explain WHY, not WHAT
- Place comments on the line above the code they describe
- Keep comments concise and up-to-date

```python
# Bad - Obvious comment
x = x + 1  # Increment x

# Good - Explains reasoning
x = x + 1  # Adjust for 0-based indexing in D2L API
```

## Error Handling Patterns

### Exception Handling
Be specific with exception types and provide context:

```python
# Bad
try:
    process_data()
except:
    pass

# Good
try:
    process_data()
except FileNotFoundError as e:
    logger.error(f"CSV file not found: {e}")
    raise
except ValueError as e:
    logger.error(f"Invalid data format in CSV: {e}")
    return False
except Exception as e:
    logger.exception(f"Unexpected error during processing: {e}")
    raise
```

### Custom Exceptions
Create custom exceptions for domain-specific errors:

```python
class D2LError(Exception):
    """Base exception for D2L automation errors."""
    pass

class AssignmentNotFoundError(D2LError):
    """Raised when an assignment cannot be located."""
    pass

class DateFormatError(D2LError):
    """Raised when date/time format is invalid."""
    pass

# Usage
if not assignment_found:
    raise AssignmentNotFoundError(
        f"Assignment '{assignment_name}' not found in course"
    )
```

## Logging Best Practices

### Log Levels
Use appropriate log levels:

```python
# DEBUG - Detailed diagnostic information
logger.debug(f"Processing row {row_num}: {row_data}")

# INFO - General informational messages
logger.info(f"Successfully updated assignment: {assignment_name}")

# WARNING - Warning messages for recoverable issues
logger.warning(f"Assignment name fuzzy matched with {match_ratio:.2f} confidence")

# ERROR - Error messages for failures
logger.error(f"Failed to update assignment: {e}")

# CRITICAL - Critical errors requiring immediate attention
logger.critical(f"Database connection lost, cannot continue")
```

### Structured Logging
Include context in log messages:

```python
# Bad
logger.info("Update successful")

# Good
logger.info(
    f"Assignment update successful",
    extra={
        'assignment_name': assignment_name,
        'due_date': due_date,
        'course_code': course_code,
        'duration_ms': elapsed_time
    }
)
```

## Function Design

### Single Responsibility Principle
Keep functions focused:

```python
# Bad - Function does too much
def process_and_update_assignments(csv_path, course_url):
    # Read CSV
    # Validate data
    # Open browser
    # Login to D2L
    # Navigate to course
    # Update each assignment
    # Generate report
    pass

# Good - Separate concerns
def read_assignments_from_csv(csv_path: str) -> List[Dict]:
    """Read and validate assignment data from CSV."""
    pass

def update_assignment_dates(assignments: List[Dict], course_url: str) -> bool:
    """Update assignment dates in D2L."""
    pass

def generate_update_report(results: List[Dict]) -> str:
    """Generate report of update operations."""
    pass
```

### Function Length
- Aim for functions under 50 lines
- If a function is longer, consider breaking it into smaller functions
- Each function should do one thing well

### Default Arguments
Use mutable defaults carefully:

```python
# Bad - Mutable default argument
def add_assignment(assignments=[]):
    assignments.append(new_assignment)
    return assignments

# Good - Use None and create new instance
def add_assignment(assignments=None):
    if assignments is None:
        assignments = []
    assignments.append(new_assignment)
    return assignments
```

## Testing Patterns

### Test Structure
Organize tests clearly:

```python
import unittest
from unittest.mock import Mock, patch

class TestD2LDateProcessor(unittest.TestCase):
    """Tests for D2LDateProcessor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = D2LDateProcessor()
        self.test_csv = "test_data/sample.csv"

    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'driver'):
            self.driver.quit()

    def test_parse_valid_date(self):
        """Test parsing of valid date string."""
        result = self.processor.parse_date("2025-12-31")
        self.assertEqual(result, datetime(2025, 12, 31))

    def test_parse_invalid_date_raises_error(self):
        """Test that invalid date raises appropriate error."""
        with self.assertRaises(DateFormatError):
            self.processor.parse_date("invalid-date")

    @patch('selenium.webdriver.Chrome')
    def test_setup_driver_with_profile(self, mock_chrome):
        """Test driver setup with persistent profile."""
        driver = self.processor.setup_driver(use_profile=True)
        mock_chrome.assert_called_once()
        # Assert profile options were set
```

## Configuration Management

### Pattern: Centralized Configuration
Keep configuration in one place:

```python
# config.py
import os
from pathlib import Path

class Config:
    """Application configuration."""

    # Base paths
    BASE_DIR = Path(__file__).parent
    LOGS_DIR = BASE_DIR / "debug_logs"
    TEMP_DIR = BASE_DIR / "temp"

    # D2L Configuration
    D2L_BASE_URL = os.getenv("D2L_BASE_URL", "https://d2l.example.com")
    COURSE_URLS = {
        'CS101': f"{D2L_BASE_URL}/courses/12345",
        'MATH200': f"{D2L_BASE_URL}/courses/67890"
    }

    # Browser Configuration
    BROWSER_TIMEOUT = int(os.getenv("BROWSER_TIMEOUT", "30"))
    USE_PERSISTENT_PROFILE = os.getenv("USE_PERSISTENT_PROFILE", "true").lower() == "true"

    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist."""
        cls.LOGS_DIR.mkdir(exist_ok=True)
        cls.TEMP_DIR.mkdir(exist_ok=True)
```

## Performance Considerations

### Avoid Unnecessary Waits
Use explicit waits instead of sleep:

```python
# Bad
import time
time.sleep(5)  # Arbitrary wait

# Good
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, 'element-id'))
)
```

### Resource Management
Use context managers for resource cleanup:

```python
# Good - Automatic cleanup
from contextlib import contextmanager

@contextmanager
def managed_driver(use_profile=True):
    """Context manager for WebDriver with automatic cleanup."""
    driver = setup_driver(use_profile)
    try:
        yield driver
    finally:
        driver.quit()

# Usage
with managed_driver() as driver:
    driver.get(url)
    # Do work
# Driver automatically cleaned up
```
