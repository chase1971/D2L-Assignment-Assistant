"""Shared name matching utilities for student name comparison."""

from typing import Optional, Tuple, List

from grading_constants import NAME_MATCH_THRESHOLD_HIGH, NAME_MATCH_THRESHOLD_MEDIUM


def _normalize_name(name: str) -> str:
    """Normalize a name by converting hyphens to spaces and lowercasing."""
    return name.lower().strip().replace("-", " ")


def names_match_fuzzy(name1: str, name2: str, threshold: float = NAME_MATCH_THRESHOLD_HIGH) -> bool:
    """
    Check if two names match with fuzzy logic.
    
    Args:
        name1: First name to compare
        name2: Second name to compare
        threshold: Minimum similarity ratio (0.0-1.0) to consider a match
    
    Returns:
        True if names match within threshold
    """
    name1_clean = _normalize_name(name1)
    name2_clean = _normalize_name(name2)
    
    # If exact match, return True
    if name1_clean == name2_clean:
        return True
    
    # Split into words (hyphens already converted to spaces)
    words1 = name1_clean.split()
    words2 = name2_clean.split()
    
    # If one name is contained in the other, that's a match
    if name1_clean in name2_clean or name2_clean in name1_clean:
        return True
    
    # Check if first and last names match (ignoring middle names)
    if len(words1) >= 2 and len(words2) >= 2:
        if words1[0] == words2[0] and words1[-1] == words2[-1]:
            return True
    
    # Check if most words match
    if len(words1) > 0 and len(words2) > 0:
        matches = 0
        for word1 in words1:
            for word2 in words2:
                if word1 == word2 or (len(word1) > 3 and len(word2) > 3 and 
                                    (word1 in word2 or word2 in word1)):
                    matches += 1
                    break
        
        # If threshold% of words match, consider it a match
        similarity = matches / max(len(words1), len(words2))
        return similarity >= threshold
    
    return False


def calculate_name_similarity(name1: str, name2: str) -> float:
    """
    Calculate similarity score between two names.
    
    Args:
        name1: First name to compare
        name2: Second name to compare
    
    Returns:
        Similarity score between 0.0 and 1.0
    """
    words1 = set(_normalize_name(name1).split())
    words2 = set(_normalize_name(name2).split())
    
    if not words1 or not words2:
        return 0.0
    
    matching_words = words1 & words2
    return len(matching_words) / max(len(words1), len(words2))


def find_best_name_match(
    name: str, 
    name_list: List[str], 
    threshold: float = NAME_MATCH_THRESHOLD_MEDIUM
) -> Optional[Tuple[str, float]]:
    """
    Find the best matching name from a list.
    
    Args:
        name: Name to search for
        name_list: List of names to search through
        threshold: Minimum similarity to consider a match
    
    Returns:
        Tuple of (matched_name, similarity_score) or None if no match found
    """
    best_match = None
    best_similarity = 0.0
    
    for candidate in name_list:
        if names_match_fuzzy(name, candidate, threshold):
            similarity = calculate_name_similarity(name, candidate)
            
            # Also boost for first+last name match
            name_parts = _normalize_name(name).split()
            candidate_parts = _normalize_name(candidate).split()
            if len(name_parts) >= 2 and len(candidate_parts) >= 2:
                if name_parts[0] == candidate_parts[0] and name_parts[-1] == candidate_parts[-1]:
                    similarity = max(similarity, 0.95)
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = candidate
    
    if best_match:
        return (best_match, best_similarity)
    return None
