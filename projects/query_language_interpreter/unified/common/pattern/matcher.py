"""Pattern matching utilities for query language interpreters."""

import re
from typing import Any, Dict, List, Match, Optional, Pattern, Set, Union


class PatternMatch:
    """Represents a pattern match result."""

    def __init__(
        self,
        pattern_id: str,
        matched_text: str,
        start: int,
        end: int,
        groups: Dict[str, str] = None,
        confidence: float = 0.0,
        category: str = "default",
        metadata: Dict[str, Any] = None,
    ):
        """Initialize a pattern match.

        Args:
            pattern_id: Identifier of the pattern that matched
            matched_text: Text that matched the pattern
            start: Start position of the match
            end: End position of the match
            groups: Named capturing groups
            confidence: Confidence score for the match
            category: Category of the pattern
            metadata: Additional metadata
        """
        self.pattern_id = pattern_id
        self.matched_text = matched_text
        self.start = start
        self.end = end
        self.groups = groups or {}
        self.confidence = confidence
        self.category = category
        self.metadata = metadata or {}

    def __str__(self) -> str:
        """String representation of the match.

        Returns:
            str: String representation
        """
        return f"PatternMatch(pattern={self.pattern_id}, text={self.matched_text}, confidence={self.confidence:.2f})"


class PatternMatcher:
    """Matcher for a single pattern."""

    def __init__(
        self,
        pattern_id: str,
        regex: str,
        threshold: float = 0.0,
        category: str = "default",
        metadata: Dict[str, Any] = None,
    ):
        """Initialize a pattern matcher.

        Args:
            pattern_id: Unique pattern identifier
            regex: Regular expression pattern
            threshold: Confidence threshold
            category: Pattern category
            metadata: Additional pattern metadata
        """
        self.pattern_id = pattern_id
        self.regex_str = regex
        self.threshold = threshold
        self.category = category
        self.metadata = metadata or {}
        
        # Compile the regular expression
        try:
            self.regex = re.compile(regex, re.IGNORECASE)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern '{regex}': {str(e)}")

    def find_matches(self, content: str) -> List[PatternMatch]:
        """Find all matches in content.

        Args:
            content: Content to search for matches

        Returns:
            List[PatternMatch]: List of pattern matches
        """
        matches = []
        for match in self.regex.finditer(content):
            # Extract named groups if any
            groups = {}
            if match.groupdict():
                groups = match.groupdict()
            
            # Create pattern match
            pattern_match = PatternMatch(
                pattern_id=self.pattern_id,
                matched_text=match.group(0),
                start=match.start(),
                end=match.end(),
                groups=groups,
                category=self.category,
                metadata=self.metadata,
            )
            
            matches.append(pattern_match)
        
        return matches

    def has_match(self, content: str) -> bool:
        """Check if content matches the pattern.

        Args:
            content: Content to check

        Returns:
            bool: True if pattern matches, False otherwise
        """
        return bool(self.regex.search(content))