"""Models for PII detection components."""

from typing import Any, Dict, Optional, Union

from common.models.enums import PIICategory
from common.pattern.pii import PIIPatternMatch

# For backward compatibility, create an alias for PIIPatternMatch
PIIMatch = PIIPatternMatch