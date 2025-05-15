"""PII pattern matching utilities for query language interpreters."""

from typing import Any, Dict, Optional

from common.pattern.matcher import PatternMatch
from common.models.enums import PIICategory


class PIIPatternMatch(PatternMatch):
    """Represents a PII pattern match result with additional PII-specific data."""

    def __init__(
        self,
        pattern_id: str,
        matched_text: str,
        start: int = 0,
        end: int = 0,
        field_name: str = "",
        category: PIICategory = PIICategory.DIRECT_IDENTIFIER,
        groups: Dict[str, str] = None,
        confidence: float = 0.0,
        sample_value: Optional[str] = None,
        match_count: int = 0,
        sensitivity_level: int = 0,
        metadata: Dict[str, Any] = None,
    ):
        """Initialize a PII pattern match.

        Args:
            pattern_id: Identifier of the pattern that matched
            matched_text: Text that matched the pattern
            start: Start position of the match
            end: End position of the match
            field_name: Name of the field containing the match
            category: PII category
            groups: Named capturing groups
            confidence: Confidence score for the match
            sample_value: Sample value for reporting
            match_count: Number of matches found
            sensitivity_level: Sensitivity level (0-3)
            metadata: Additional metadata
        """
        super().__init__(
            pattern_id=pattern_id,
            matched_text=matched_text,
            start=start,
            end=end,
            groups=groups,
            confidence=confidence,
            category=category.value if hasattr(category, "value") else str(category),
            metadata=metadata or {},
        )
        
        self.field_name = field_name
        self.pii_type = pattern_id  # Alias for backward compatibility
        self.sample_value = sample_value or matched_text
        self.match_count = match_count
        self.sensitivity_level = sensitivity_level
        self.pii_category = category
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the match to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation
        """
        result = super().to_dict() if hasattr(super(), "to_dict") else {
            "pattern_id": self.pattern_id,
            "matched_text": self.matched_text,
            "start": self.start,
            "end": self.end,
            "confidence": self.confidence,
        }
        
        result.update({
            "field_name": self.field_name,
            "pii_type": self.pii_type,
            "category": self.pii_category,
            "sample_value": self.sample_value,
            "match_count": self.match_count,
            "sensitivity_level": self.sensitivity_level
        })
        
        return result