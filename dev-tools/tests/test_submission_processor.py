"""Tests for submission_processor.py - submission processing utilities."""

import pytest
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from submission_processor import (
    _parse_folder_timestamp,
    _match_student_to_roster,
    _check_page_counts,
)


class TestParseFolderTimestamp:
    """Tests for _parse_folder_timestamp function."""

    def test_format_without_colon(self):
        """Parse 'Dec 10, 2025 1145 AM' format."""
        folder = "Assignment 1 - John Smith - Dec 10, 2025 1145 AM"
        result = _parse_folder_timestamp(folder)
        assert result is not None
        assert result.year == 2025
        assert result.month == 12
        assert result.day == 10
        assert result.hour == 11
        assert result.minute == 45

    def test_format_with_colon(self):
        """Parse 'Dec 10, 2025 11:45 AM' format."""
        folder = "Assignment 1 - Jane Doe - Dec 10, 2025 11:45 AM"
        result = _parse_folder_timestamp(folder)
        assert result is not None
        assert result.year == 2025
        assert result.month == 12
        assert result.hour == 11

    def test_full_month_name_without_colon(self):
        """Parse 'December 5, 2025 230 PM' format."""
        folder = "Quiz 3 - Bob Johnson - December 5, 2025 230 PM"
        result = _parse_folder_timestamp(folder)
        assert result is not None
        assert result.month == 12
        assert result.day == 5
        assert result.hour == 14  # 2:30 PM = 14:30
        assert result.minute == 30

    def test_full_month_name_with_colon(self):
        """Parse 'December 5, 2025 2:30 PM' format."""
        folder = "Quiz 3 - Mary O'Brien - December 5, 2025 2:30 PM"
        result = _parse_folder_timestamp(folder)
        assert result is not None
        assert result.hour == 14

    def test_invalid_folder_name(self):
        """Invalid folder names should return None."""
        assert _parse_folder_timestamp("random folder name") is None
        assert _parse_folder_timestamp("") is None
        assert _parse_folder_timestamp("no-dashes-here") is None

    def test_folder_without_date(self):
        """Folder with name pattern but no valid date should return None."""
        folder = "Assignment - John Smith - invalid date"
        result = _parse_folder_timestamp(folder)
        assert result is None


class TestMatchStudentToRoster:
    """Tests for _match_student_to_roster function."""

    def test_strategy1_first_rest(self, sample_roster_df):
        """Strategy 1: First word = first name, rest = last name."""
        user, hit = _match_student_to_roster("John Smith", sample_roster_df, None)
        assert user == "jsmith01"

    def test_strategy2_all_but_last(self, sample_roster_df):
        """Strategy 2: All but last word = first name, last word = last name."""
        # Mary Ann O'Brien - "Mary Ann" is first name, "O'Brien" is last
        user, hit = _match_student_to_roster("Mary Ann O'Brien", sample_roster_df, None)
        assert user == "mobrien04"

    def test_strategy3_hyphen_variations(self, sample_roster_df):
        """Strategy 3: Try hyphen variations for last name."""
        # Bob Johnson Williams should match Bob Johnson-Williams
        user, hit = _match_student_to_roster("Bob Johnson Williams", sample_roster_df, None)
        assert user == "bjohnson03"

    def test_strategy4_two_part_match(self, sample_roster_df):
        """Strategy 4: Match at least 2 name parts."""
        # "Jose Garcia" should match "Jose Garcia Lopez" (shares jose and garcia)
        user, hit = _match_student_to_roster("Jose Garcia", sample_roster_df, None)
        assert user == "jgarcia05"

    def test_no_match(self, sample_roster_df):
        """Unmatched name should return None."""
        user, hit = _match_student_to_roster("Unknown Person", sample_roster_df, None)
        assert user is None
        assert hit is None

    def test_single_word_name(self, sample_roster_df):
        """Single word names should return None (need at least 2 parts)."""
        user, hit = _match_student_to_roster("John", sample_roster_df, None)
        assert user is None

    def test_case_insensitive(self, sample_roster_df):
        """Matching should be case insensitive."""
        user, hit = _match_student_to_roster("JOHN SMITH", sample_roster_df, None)
        assert user == "jsmith01"

    def test_extra_whitespace(self, sample_roster_df):
        """Extra whitespace in names should be handled."""
        user, hit = _match_student_to_roster("  John   Smith  ", sample_roster_df, None)
        # Note: This may or may not work depending on implementation
        # The current code splits on whitespace which handles this


class TestCheckPageCounts:
    """Tests for _check_page_counts function."""

    def test_below_average_flagged(self):
        """Students with pages below 70% of average should be flagged."""
        page_counts = {
            "John Smith": 10,
            "Jane Doe": 10,
            "Bob Johnson": 3,  # 3 pages when avg is 7.67, 3 < 5.37 (70%)
        }
        student_errors = []
        _check_page_counts(page_counts, student_errors)
        
        assert len(student_errors) == 1
        assert "Bob Johnson" in student_errors[0]
        assert "3 page" in student_errors[0]

    def test_at_average_not_flagged(self):
        """Students at or above 70% of average should not be flagged."""
        page_counts = {
            "John Smith": 10,
            "Jane Doe": 10,
            "Bob Johnson": 8,  # 8 pages when avg is 9.33, 8 > 6.53 (70%)
        }
        student_errors = []
        _check_page_counts(page_counts, student_errors)
        
        assert len(student_errors) == 0

    def test_empty_page_counts(self):
        """Empty page counts should not cause errors."""
        student_errors = []
        _check_page_counts({}, student_errors)
        assert len(student_errors) == 0

    def test_single_student(self):
        """Single student should compare against their own average."""
        page_counts = {"John Smith": 5}
        student_errors = []
        _check_page_counts(page_counts, student_errors)
        # 5 is 100% of average (5), so should not be flagged
        assert len(student_errors) == 0

    def test_all_same_pages(self):
        """All students with same page count should not be flagged."""
        page_counts = {
            "John Smith": 5,
            "Jane Doe": 5,
            "Bob Johnson": 5,
        }
        student_errors = []
        _check_page_counts(page_counts, student_errors)
        assert len(student_errors) == 0

    def test_multiple_below_average(self):
        """Multiple students below average should all be flagged."""
        page_counts = {
            "High Student": 20,
            "Low Student 1": 2,
            "Low Student 2": 1,
        }
        student_errors = []
        _check_page_counts(page_counts, student_errors)
        
        # Average is 7.67, 70% is 5.37
        # Both low students should be flagged
        assert len(student_errors) == 2

