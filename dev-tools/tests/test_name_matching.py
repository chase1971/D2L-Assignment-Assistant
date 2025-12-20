"""Tests for name_matching.py - fuzzy name matching utilities."""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from name_matching import names_match_fuzzy, calculate_name_similarity, find_best_name_match


class TestNamesMatchFuzzy:
    """Tests for the names_match_fuzzy function."""

    def test_exact_match(self):
        """Identical names should match."""
        assert names_match_fuzzy("John Smith", "John Smith") is True

    def test_case_insensitive(self):
        """Matching should be case insensitive."""
        assert names_match_fuzzy("JOHN SMITH", "john smith") is True
        assert names_match_fuzzy("John Smith", "JOHN SMITH") is True

    def test_whitespace_handling(self):
        """Leading/trailing whitespace should be ignored."""
        assert names_match_fuzzy("  John Smith  ", "John Smith") is True

    def test_first_last_match_ignores_middle(self):
        """First and last name match should work even with middle names."""
        assert names_match_fuzzy("John Michael Smith", "John Smith") is True
        assert names_match_fuzzy("John Smith", "John Michael Smith") is True

    def test_containment_match(self):
        """One name contained in another should match."""
        assert names_match_fuzzy("John", "John Smith") is True
        assert names_match_fuzzy("Smith", "John Smith") is True

    def test_no_match_different_names(self):
        """Completely different names should not match."""
        assert names_match_fuzzy("John Smith", "Jane Doe") is False

    def test_partial_word_match(self):
        """Names sharing some words should match based on threshold."""
        # "John" matches, but "Smith" vs "Doe" don't - depends on threshold
        result = names_match_fuzzy("John Smith", "John Doe", threshold=0.5)
        assert result is True  # 1/2 words match = 0.5, meets threshold
        
        result = names_match_fuzzy("John Smith", "John Doe", threshold=0.8)
        assert result is False  # 1/2 words match = 0.5, below 0.8 threshold

    def test_hyphenated_names(self):
        """Hyphenated names are normalized to match space-separated versions."""
        # Hyphens are converted to spaces, so these match
        assert names_match_fuzzy("Bob Johnson-Williams", "Bob Johnson Williams") is True
        # Exact hyphenated match also works
        assert names_match_fuzzy("Bob Johnson-Williams", "Bob Johnson-Williams") is True
        # Works in either direction
        assert names_match_fuzzy("Mary O'Brien-Smith", "Mary O'Brien Smith") is True

    def test_multi_word_first_names(self):
        """Multi-word first names should work."""
        assert names_match_fuzzy("Mary Ann Smith", "Mary Ann Smith") is True

    def test_empty_strings(self):
        """Empty string behavior - containment check makes empty match anything."""
        assert names_match_fuzzy("", "") is True  # Both empty = exact match
        # Empty string is "contained in" any string, so these return True
        assert names_match_fuzzy("John", "") is True  # "" in "john" is True
        assert names_match_fuzzy("", "John") is True  # "" in "john" is True


class TestCalculateNameSimilarity:
    """Tests for the calculate_name_similarity function."""

    def test_identical_names(self):
        """Identical names should have similarity of 1.0."""
        assert calculate_name_similarity("John Smith", "John Smith") == 1.0

    def test_no_match(self):
        """No matching words should return 0.0."""
        assert calculate_name_similarity("John Smith", "Jane Doe") == 0.0

    def test_partial_match(self):
        """Partial word overlap should return proportional score."""
        # "John" matches, "Smith" vs "Doe" don't = 1/2 = 0.5
        score = calculate_name_similarity("John Smith", "John Doe")
        assert score == 0.5

    def test_empty_name(self):
        """Empty names should return 0.0."""
        assert calculate_name_similarity("John Smith", "") == 0.0
        assert calculate_name_similarity("", "John Smith") == 0.0
        assert calculate_name_similarity("", "") == 0.0

    def test_case_insensitive(self):
        """Similarity should be case insensitive."""
        assert calculate_name_similarity("JOHN SMITH", "john smith") == 1.0

    def test_uses_max_length_denominator(self):
        """Score should use max word count as denominator."""
        # "John" matches, "Michael" and "Smith" don't
        # 1 match / max(3, 2) = 1/3 ≈ 0.333
        score = calculate_name_similarity("John Michael Smith", "John Doe")
        assert abs(score - 1/3) < 0.01


class TestFindBestNameMatch:
    """Tests for the find_best_name_match function."""

    def test_exact_match_in_list(self):
        """Should find exact match in list."""
        names = ["Jane Doe", "John Smith", "Bob Johnson"]
        result = find_best_name_match("John Smith", names)
        assert result is not None
        assert result[0] == "John Smith"
        assert result[1] == 1.0

    def test_no_match_returns_none(self):
        """Should return None when no match above threshold."""
        names = ["Jane Doe", "Bob Johnson"]
        result = find_best_name_match("John Smith", names, threshold=0.9)
        assert result is None

    def test_best_match_selected(self):
        """Should select the best match when multiple candidates exist."""
        names = ["John Doe", "John Smith", "Jane Smith"]
        result = find_best_name_match("John Smith", names)
        assert result is not None
        assert result[0] == "John Smith"

    def test_first_last_boost(self):
        """First+last name match should get boosted to 0.95."""
        names = ["John Michael Smith", "John Doe"]
        result = find_best_name_match("John Smith", names)
        assert result is not None
        # John Smith matches John Michael Smith on first+last
        assert result[0] == "John Michael Smith"
        assert result[1] >= 0.95

    def test_empty_list(self):
        """Empty list should return None."""
        result = find_best_name_match("John Smith", [])
        assert result is None

    def test_threshold_filtering(self):
        """Results below threshold should be filtered out."""
        names = ["John Doe", "Jane Doe"]  # Only "Doe" matches for Jane
        result = find_best_name_match("Jane Smith", names, threshold=0.9)
        assert result is None  # No match meets 0.9 threshold

