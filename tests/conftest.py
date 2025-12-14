"""Shared pytest fixtures for D2L Assignment Assistant tests."""

import pytest
import pandas as pd


@pytest.fixture
def sample_roster_df():
    """Create a sample roster DataFrame for testing name matching."""
    return pd.DataFrame({
        "First Name": ["john", "jane", "bob", "mary ann", "jose"],
        "Last Name": ["smith", "doe", "johnson-williams", "o'brien", "garcia lopez"],
        "Username": ["jsmith01", "jdoe02", "bjohnson03", "mobrien04", "jgarcia05"]
    })


@pytest.fixture
def sample_folder_names():
    """Sample Canvas folder names for timestamp parsing tests."""
    return [
        "Assignment 1 - John Smith - Dec 10, 2025 1145 AM",
        "Assignment 1 - Jane Doe - Dec 10, 2025 11:45 AM",
        "Quiz 3 - Bob Johnson - December 5, 2025 230 PM",
        "Quiz 3 - Mary O'Brien - December 5, 2025 2:30 PM",
    ]


@pytest.fixture
def sample_ocr_texts():
    """Sample OCR text for grade extraction tests."""
    return {
        "fraction": "Score: 85/100",
        "percentage": "Grade: 92%",
        "decimal": "Points: 87.5",
        "whole": "Score 78",
        "ocr_errors": "Score: 8S/l00",  # 85/100 with OCR mistakes
        "no_grade": "Please submit your work",
    }


@pytest.fixture
def sample_watermark_texts():
    """Sample watermark text for name extraction tests."""
    return {
        "valid": "John Smith (1 of 3)\nUnit 5 Quiz",
        "no_marker": "John Smith\nUnit 5 Quiz",
        "instructional": "Please submit by midnight (1 of 2)",
        "long_line": "This is a very long instructional line that should be skipped (1 of 2)",
    }

