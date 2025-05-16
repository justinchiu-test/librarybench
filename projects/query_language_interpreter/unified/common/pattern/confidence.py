"""Confidence scoring for pattern matches."""

from typing import Any, Dict, List, Optional, Pattern, Set, Union
import re

from common.pattern.matcher import PatternMatch


def calculate_confidence(match: PatternMatch) -> float:
    """Calculate confidence score for a pattern match.

    This function can be extended with more sophisticated confidence scoring algorithms.

    Args:
        match: Pattern match to score

    Returns:
        float: Confidence score (0.0 to 1.0)
    """
    # Start with a base confidence
    base_confidence = 0.7

    # Get match metadata
    metadata = match.metadata or {}

    # If confidence is already set, use it
    if match.confidence > 0:
        return match.confidence

    # If pattern has a predefined weight, use it
    if "weight" in metadata:
        return float(metadata["weight"])

    # Factors that might increase confidence
    adjustments = 0.0

    # Length of matched text (longer matches might be more confident)
    text_length = len(match.matched_text)
    if text_length > 20:
        adjustments += 0.1
    elif text_length > 10:
        adjustments += 0.05

    # Number of capturing groups (more structure might indicate higher confidence)
    if match.groups:
        adjustments += min(0.1, len(match.groups) * 0.02)

    # Context-specific adjustments could be added here

    # Final confidence score, capped at 1.0
    confidence = min(1.0, base_confidence + adjustments)

    return confidence


def adjust_confidence_with_validation(
    match: PatternMatch, validation_result: bool, adjustment: float = 0.2
) -> float:
    """Adjust confidence based on validation result.

    Args:
        match: Pattern match to adjust
        validation_result: Result of validation check
        adjustment: Amount to adjust confidence

    Returns:
        float: Adjusted confidence score
    """
    if validation_result:
        return min(1.0, match.confidence + adjustment)
    else:
        return max(0.0, match.confidence - adjustment)


def aggregate_confidence(matches: List[PatternMatch]) -> float:
    """Aggregate confidence scores from multiple matches.

    Args:
        matches: List of pattern matches

    Returns:
        float: Aggregated confidence score
    """
    if not matches:
        return 0.0

    # Simple averaging
    total_confidence = sum(match.confidence for match in matches)
    return total_confidence / len(matches)
