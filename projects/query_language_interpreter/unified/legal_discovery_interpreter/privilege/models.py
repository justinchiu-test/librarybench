"""Models for privilege detection in legal discovery."""

from typing import Dict, List, Set, Tuple, Optional, Any, Union

# Import common models
from common.models.legal import (
    PrivilegeType,
    PrivilegeIndicatorCategory,
    PrivilegeStatus,
    PrivilegeIndicator as CommonPrivilegeIndicator,
    Attorney,
    PrivilegeDetectionResult,
    PrivilegeLog,
)


# Create compatibility wrapper for tests that expect different attribute names
class PrivilegeIndicator(CommonPrivilegeIndicator):
    """Compatibility wrapper for PrivilegeIndicator."""

    def __init__(
        self,
        indicator_id: str,
        pattern: str = None,
        name: str = None,
        description: str = "",
        weight: float = 1.0,
        indicator_type: PrivilegeType = PrivilegeType.ATTORNEY_CLIENT,
        category: Optional[PrivilegeIndicatorCategory] = None,
        indicator_category: Optional[PrivilegeIndicatorCategory] = None,
        case_sensitive: bool = False,
        exact_match: bool = False,
        **kwargs,
    ):
        """Initialize with backward compatibility.

        Args:
            indicator_id: Indicator ID
            pattern: Regex pattern
            name: Name (for backward compatibility)
            description: Description
            weight: Weight
            indicator_type: Indicator type
            category: Category (for backward compatibility)
            indicator_category: Indicator category
            case_sensitive: Case sensitive flag
            exact_match: Exact match flag
        """
        # Handle compatibility with old interface
        if name and not description:
            description = name

        if category and not indicator_category:
            indicator_category = category

        if not indicator_category:
            indicator_category = PrivilegeIndicatorCategory.CONTENT

        # Provide a default pattern if none is specified
        if pattern is None:
            pattern = f"(?i){indicator_id}"

        # Initialize parent class
        super().__init__(
            indicator_id=indicator_id,
            pattern=pattern,
            description=description,
            weight=weight,
            indicator_type=indicator_type,
            indicator_category=indicator_category,
            case_sensitive=case_sensitive,
            exact_match=exact_match,
        )

        # Add compatibility attributes
        self.name = name if name else description
        self.category = indicator_category


# Re-export common models to maintain backward compatibility
__all__ = [
    "PrivilegeType",
    "PrivilegeIndicatorCategory",
    "PrivilegeStatus",
    "PrivilegeIndicator",
    "Attorney",
    "PrivilegeDetectionResult",
    "PrivilegeLog",
]
