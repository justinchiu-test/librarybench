"""Legal pattern matching utilities for query language interpreters."""

from typing import Any, Dict, List, Optional, Tuple, Union
from enum import Enum

from common.pattern.matcher import PatternMatch
from common.pattern.detector import BasePatternDetector
from common.models.legal import (
    PrivilegeType,
    PrivilegeIndicatorCategory,
    PrivilegeStatus,
)


class LegalPatternMatch(PatternMatch):
    """Represents a legal pattern match result with additional legal-specific data."""

    def __init__(
        self,
        pattern_id: str,
        matched_text: str,
        start: int = 0,
        end: int = 0,
        pattern_type: str = "",
        category: str = "",
        groups: Optional[Dict[str, str]] = None,
        confidence: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
        weight: float = 1.0,
        indicator_type: Optional[Union[str, PrivilegeType]] = None,
        indicator_category: Optional[Union[str, PrivilegeIndicatorCategory]] = None,
    ):
        """Initialize a legal pattern match.

        Args:
            pattern_id: Identifier of the pattern that matched
            matched_text: Text that matched the pattern
            start: Start position of the match
            end: End position of the match
            pattern_type: Type of the pattern
            category: Category of the match
            groups: Named capturing groups
            confidence: Confidence score for the match
            metadata: Additional metadata
            weight: Weight of the match for scoring
            indicator_type: Type of legal indicator (e.g., privilege type)
            indicator_category: Category of legal indicator
        """
        super().__init__(
            pattern_id=pattern_id,
            matched_text=matched_text,
            start=start,
            end=end,
            groups=groups or {},
            confidence=confidence,
            category=category,
            metadata=metadata or {},
        )

        self.pattern_type = pattern_type
        self.weight = weight

        # Handle indicator_type
        if isinstance(indicator_type, PrivilegeType):
            self.indicator_type = indicator_type
        elif indicator_type is not None:
            try:
                self.indicator_type = PrivilegeType(indicator_type)
            except (ValueError, TypeError):
                self.indicator_type = None
        else:
            self.indicator_type = None

        # Handle indicator_category
        if isinstance(indicator_category, PrivilegeIndicatorCategory):
            self.indicator_category = indicator_category
        elif indicator_category is not None:
            try:
                self.indicator_category = PrivilegeIndicatorCategory(indicator_category)
            except (ValueError, TypeError):
                self.indicator_category = None
        else:
            self.indicator_category = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert the match to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation
        """
        result = {
            "pattern_id": self.pattern_id,
            "matched_text": self.matched_text,
            "start": self.start,
            "end": self.end,
            "confidence": self.confidence,
            "category": self.category,
            "metadata": self.metadata.copy() if hasattr(self, "metadata") else {},
        }

        result.update(
            {
                "pattern_type": self.pattern_type,
                "weight": self.weight,
                "indicator_type": self.indicator_type.value
                if self.indicator_type
                else None,
                "indicator_category": self.indicator_category.value
                if self.indicator_category
                else None,
            }
        )

        return result


class LegalPatternDetector(BasePatternDetector):
    """Detector for legal-specific patterns in documents."""

    def __init__(
        self,
        patterns: Optional[Dict[str, Any]] = None,
        confidence_threshold: float = 0.5,
        custom_patterns: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the legal pattern detector.

        Args:
            patterns: Dictionary of pattern definitions
            confidence_threshold: Minimum confidence threshold
            custom_patterns: Additional custom patterns
        """
        super().__init__(patterns or {})
        self.confidence_threshold = confidence_threshold

        # Add custom patterns if provided
        if custom_patterns:
            for pattern_id, pattern_def in custom_patterns.items():
                self.add_pattern(
                    pattern_id=pattern_id,
                    regex=pattern_def.get("pattern", ""),
                    threshold=pattern_def.get("weight", 0.0),
                    category=pattern_def.get("category", "legal"),
                    metadata=pattern_def,
                )

    def detect_legal_patterns(
        self, text: str, category_filter: Optional[str] = None
    ) -> List[LegalPatternMatch]:
        """Detect legal patterns in a text.

        Args:
            text: Text to check for legal patterns
            category_filter: Optional category to filter results

        Returns:
            List of LegalPatternMatch objects
        """
        matches = []

        # Skip if text is not a string
        if not isinstance(text, str) or not text:
            return matches

        # Find pattern matches
        pattern_matches = self.detect(text)

        # Convert to LegalPatternMatch objects
        for match in pattern_matches:
            confidence = self.calculate_confidence(match)

            # Only include matches that meet the confidence threshold
            if confidence >= self.confidence_threshold:
                metadata = match.metadata or {}

                # Apply category filter if specified
                if category_filter and metadata.get("category") != category_filter:
                    continue

                indicator_type = metadata.get("indicator_type")
                indicator_category = metadata.get("indicator_category")
                weight = float(metadata.get("weight", 1.0))

                legal_match = LegalPatternMatch(
                    pattern_id=match.pattern_id,
                    matched_text=match.matched_text,
                    start=match.start,
                    end=match.end,
                    pattern_type=metadata.get("pattern_type", "legal"),
                    category=metadata.get("category", "legal"),
                    confidence=confidence,
                    metadata=metadata,
                    weight=weight,
                    indicator_type=indicator_type,
                    indicator_category=indicator_category,
                )
                matches.append(legal_match)

        return matches

    def detect_privilege_indicators(self, text: str) -> Dict[str, float]:
        """Detect privilege indicators in a text.

        Args:
            text: Text to check for privilege indicators

        Returns:
            Dictionary mapping indicator IDs to confidence scores
        """
        matches = self.detect_legal_patterns(text, category_filter="privilege")
        return {match.pattern_id: match.weight for match in matches}

    def calculate_privilege_score(
        self, detected_indicators: Dict[str, float], attorneys_involved: List[str]
    ) -> Tuple[float, List[str]]:
        """Calculate a privilege score.

        Args:
            detected_indicators: Dictionary mapping indicator IDs to confidence scores
            attorneys_involved: List of attorney IDs or emails involved

        Returns:
            Tuple of confidence score and list of detected privilege types
        """
        if not detected_indicators and not attorneys_involved:
            return 0.0, []

        # Calculate base score from indicators
        indicator_score = 0.0
        max_score = 0.0
        detected_types = set()

        for indicator_id, confidence in detected_indicators.items():
            matcher = self.matchers.get(indicator_id)
            if matcher:
                indicator_score += confidence
                max_score += 1.0

                # Get privilege type from matcher metadata
                indicator_type = matcher.metadata.get("indicator_type")
                if indicator_type:
                    detected_types.add(indicator_type)

        # Normalize indicator score
        if max_score > 0:
            indicator_score /= max_score

        # Add attorney component
        attorney_score = min(1.0, len(attorneys_involved) * 0.3)

        # Combine scores
        # Weight: 70% indicators, 30% attorneys
        combined_score = (indicator_score * 0.7) + (attorney_score * 0.3)

        return combined_score, list(detected_types)

    def determine_privilege_status(self, confidence: float) -> PrivilegeStatus:
        """Determine privilege status based on confidence score.

        Args:
            confidence: Confidence score

        Returns:
            Privilege status
        """
        if confidence >= 0.8:
            return PrivilegeStatus.PRIVILEGED
        elif confidence >= 0.5:
            return PrivilegeStatus.POTENTIALLY_PRIVILEGED
        elif confidence > 0:
            return PrivilegeStatus.NOT_PRIVILEGED
        else:
            return PrivilegeStatus.UNKNOWN
