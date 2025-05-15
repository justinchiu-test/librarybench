"""Models for PII detection components."""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from privacy_query_interpreter.pii_detection.patterns import PIICategory


@dataclass
class PIIMatch:
    """Representation of a detected PII match."""
    
    field_name: str
    pii_type: str
    category: PIICategory
    confidence: float
    sample_value: Optional[str] = None
    match_count: int = 0
    sensitivity_level: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the match to a dictionary."""
        return {
            "field_name": self.field_name,
            "pii_type": self.pii_type,
            "category": self.category,
            "confidence": self.confidence,
            "sample_value": self.sample_value,
            "match_count": self.match_count,
            "sensitivity_level": self.sensitivity_level
        }