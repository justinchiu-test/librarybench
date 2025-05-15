"""Base pattern detection functionality for query language interpreters."""

import re
from typing import Any, Dict, List, Optional, Pattern, Set, Tuple, Union
from abc import ABC, abstractmethod

from common.pattern.matcher import PatternMatcher, PatternMatch
from common.pattern.confidence import calculate_confidence


class BasePatternDetector(ABC):
    """Base class for pattern detection systems."""

    def __init__(self, patterns: Dict[str, Any] = None):
        """Initialize a pattern detector.

        Args:
            patterns: Dictionary of pattern definitions
        """
        self.patterns = patterns or {}
        self.matchers: Dict[str, PatternMatcher] = {}
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Compile patterns into matchers."""
        for pattern_id, pattern_def in self.patterns.items():
            if isinstance(pattern_def, dict) and "regex" in pattern_def:
                regex = pattern_def["regex"]
                threshold = pattern_def.get("threshold", 0.0)
                category = pattern_def.get("category", "default")
                self.matchers[pattern_id] = PatternMatcher(
                    pattern_id=pattern_id,
                    regex=regex,
                    threshold=threshold,
                    category=category,
                    metadata=pattern_def,
                )

    def add_pattern(
        self,
        pattern_id: str,
        regex: str,
        threshold: float = 0.0,
        category: str = "default",
        metadata: Dict[str, Any] = None,
    ) -> None:
        """Add a pattern to the detector.

        Args:
            pattern_id: Unique pattern identifier
            regex: Regular expression pattern
            threshold: Confidence threshold
            category: Pattern category
            metadata: Additional pattern metadata
        """
        pattern_def = {
            "regex": regex,
            "threshold": threshold,
            "category": category,
        }
        if metadata:
            pattern_def.update(metadata)
        
        self.patterns[pattern_id] = pattern_def
        self.matchers[pattern_id] = PatternMatcher(
            pattern_id=pattern_id,
            regex=regex,
            threshold=threshold,
            category=category,
            metadata=pattern_def,
        )

    def remove_pattern(self, pattern_id: str) -> bool:
        """Remove a pattern from the detector.

        Args:
            pattern_id: Pattern identifier to remove

        Returns:
            bool: True if removed, False if not found
        """
        if pattern_id in self.patterns:
            del self.patterns[pattern_id]
            del self.matchers[pattern_id]
            return True
        return False

    def detect(self, content: str) -> List[PatternMatch]:
        """Detect patterns in content.

        Args:
            content: Content to search for patterns

        Returns:
            List[PatternMatch]: List of pattern matches
        """
        matches = []
        for pattern_id, matcher in self.matchers.items():
            pattern_matches = matcher.find_matches(content)
            matches.extend(pattern_matches)
        return matches

    def detect_by_category(self, content: str, category: str) -> List[PatternMatch]:
        """Detect patterns of a specific category in content.

        Args:
            content: Content to search for patterns
            category: Pattern category to match

        Returns:
            List[PatternMatch]: List of pattern matches
        """
        matches = []
        for pattern_id, matcher in self.matchers.items():
            if matcher.category == category:
                pattern_matches = matcher.find_matches(content)
                matches.extend(pattern_matches)
        return matches

    def has_match(self, content: str) -> bool:
        """Check if content matches any pattern.

        Args:
            content: Content to check

        Returns:
            bool: True if any pattern matches, False otherwise
        """
        return any(matcher.has_match(content) for matcher in self.matchers.values())
        
    def calculate_confidence(self, match: PatternMatch) -> float:
        """Calculate confidence score for a match.

        Args:
            match: Pattern match

        Returns:
            float: Confidence score (0.0 to 1.0)
        """
        return calculate_confidence(match)