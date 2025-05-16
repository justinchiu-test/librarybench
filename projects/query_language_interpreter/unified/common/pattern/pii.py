"""PII pattern matching utilities for query language interpreters."""

from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

from common.pattern.matcher import PatternMatch
from common.pattern.detector import BasePatternDetector
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
        groups: Optional[Dict[str, str]] = None,
        confidence: float = 0.0,
        sample_value: Optional[str] = None,
        match_count: int = 0,
        sensitivity_level: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
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
            groups=groups or {},
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
        # PatternMatch doesn't have to_dict, so create our own
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
                "field_name": self.field_name,
                "pii_type": self.pii_type,
                "category": self.pii_category,
                "sample_value": self.sample_value,
                "match_count": self.match_count,
                "sensitivity_level": self.sensitivity_level,
            }
        )

        return result


class PIIPatternDetector(BasePatternDetector):
    """Detector for PII patterns in various data sources."""

    def __init__(
        self,
        patterns: Optional[Dict[str, Any]] = None,
        confidence_threshold: float = 0.7,
        custom_patterns: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the PII pattern detector.

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
                    regex=pattern_def.get("regex", ""),
                    threshold=pattern_def.get("threshold", 0.0),
                    category=pattern_def.get("category", "default"),
                    metadata=pattern_def,
                )

    def detect_pii_in_string(
        self, text: str, field_name: str = "text"
    ) -> List[PIIPatternMatch]:
        """Detect PII in a string.

        Args:
            text: String to check for PII
            field_name: Name of the field or column

        Returns:
            List of PIIPatternMatch objects
        """
        matches = []

        # Skip if text is not a string
        if not isinstance(text, str) or not text:
            return matches

        # Find pattern matches
        pattern_matches = self.detect(text)

        # Convert to PIIPatternMatch objects
        for match in pattern_matches:
            confidence = self.calculate_confidence(match)

            # Only include matches that meet the confidence threshold
            if confidence >= self.confidence_threshold:
                # Get category from metadata or default to DIRECT_IDENTIFIER
                category_str = match.metadata.get(
                    "category", PIICategory.DIRECT_IDENTIFIER.value
                )
                try:
                    category = PIICategory(category_str)
                except ValueError:
                    category = PIICategory.DIRECT_IDENTIFIER

                pii_match = PIIPatternMatch(
                    pattern_id=match.pattern_id,
                    matched_text=match.matched_text,
                    start=match.start,
                    end=match.end,
                    field_name=field_name,
                    category=category,
                    confidence=confidence,
                    sensitivity_level=match.metadata.get("sensitivity_level", 1),
                    match_count=1,
                )
                matches.append(pii_match)

        return matches

    def detect_pii_in_dataframe(
        self,
        df: pd.DataFrame,
        sample_size: Optional[int] = None,
        max_sample_size: int = 1000,
    ) -> List[PIIPatternMatch]:
        """Detect PII in a pandas DataFrame.

        Args:
            df: DataFrame to scan
            sample_size: Number of rows to sample
            max_sample_size: Maximum sample size

        Returns:
            List of PIIPatternMatch objects
        """
        matches = []

        # Determine sample size
        if sample_size is None:
            sample_size = min(max_sample_size, len(df))
        else:
            sample_size = min(sample_size, len(df), max_sample_size)

        if sample_size <= 0 or df.empty:
            return matches

        # Sample the DataFrame
        if sample_size < len(df):
            sample_df = df.sample(sample_size)
        else:
            sample_df = df

        # Process each column
        for column in sample_df.columns:
            # Skip non-string columns
            if sample_df[column].dtype not in ["object", "string"]:
                continue

            # Extract non-null values
            values = sample_df[column].dropna().astype(str)
            if values.empty:
                continue

            # Check for PII in values
            for matcher_id, matcher in self.matchers.items():
                # Count matches
                match_count = 0
                sample_value = None

                for value in values:
                    if matcher.has_match(value):
                        match_count += 1
                        if not sample_value:
                            # Get the first match as a sample
                            matches_in_value = matcher.find_matches(value)
                            if matches_in_value:
                                sample_value = matches_in_value[0].matched_text

                # Only create a match if we found PII
                if match_count > 0:
                    # Calculate confidence based on match ratio
                    confidence = (match_count / len(values)) * matcher.threshold

                    # Only include matches that meet the confidence threshold
                    if confidence >= self.confidence_threshold:
                        # Get category from metadata or default to DIRECT_IDENTIFIER
                        category_str = matcher.metadata.get(
                            "category", PIICategory.DIRECT_IDENTIFIER.value
                        )
                        try:
                            category = PIICategory(category_str)
                        except ValueError:
                            category = PIICategory.DIRECT_IDENTIFIER

                        pii_match = PIIPatternMatch(
                            pattern_id=matcher_id,
                            matched_text=sample_value or "",
                            field_name=column,
                            category=category,
                            confidence=confidence,
                            sample_value=sample_value,
                            match_count=match_count,
                            sensitivity_level=matcher.metadata.get(
                                "sensitivity_level", 1
                            ),
                        )
                        matches.append(pii_match)

        return matches

    def is_pii_field(
        self, field_name: str, sample_value: Optional[str] = None
    ) -> Tuple[bool, str, float]:
        """Check if a field is likely to contain PII.

        Args:
            field_name: Name of the field
            sample_value: Optional sample value

        Returns:
            Tuple of (is_pii, pii_type, confidence)
        """
        # Check field name against common PII field names
        pii_name_indicators = {
            "name": (PIICategory.DIRECT_IDENTIFIER, 0.7),
            "email": (PIICategory.CONTACT, 0.8),
            "phone": (PIICategory.CONTACT, 0.8),
            "address": (PIICategory.CONTACT, 0.7),
            "ssn": (PIICategory.GOVERNMENT_ID, 0.9),
            "social": (PIICategory.GOVERNMENT_ID, 0.7),
            "birth": (PIICategory.DIRECT_IDENTIFIER, 0.7),
            "zip": (PIICategory.LOCATION, 0.6),
            "postal": (PIICategory.LOCATION, 0.6),
            "tax": (PIICategory.FINANCIAL, 0.7),
            "password": (PIICategory.CREDENTIAL, 0.9),
            "credit": (PIICategory.FINANCIAL, 0.8),
            "card": (PIICategory.FINANCIAL, 0.6),
            "license": (PIICategory.GOVERNMENT_ID, 0.7),
            "passport": (PIICategory.GOVERNMENT_ID, 0.8),
            "gender": (PIICategory.DIRECT_IDENTIFIER, 0.6),
            "age": (PIICategory.DIRECT_IDENTIFIER, 0.6),
            "account": (PIICategory.FINANCIAL, 0.7),
            "user": (PIICategory.CREDENTIAL, 0.6),
        }

        field_name_lower = field_name.lower()

        # First, check for exact matches
        for indicator, (category, score) in pii_name_indicators.items():
            if indicator == field_name_lower:
                return True, indicator, score

        # Then check for partial matches
        for indicator, (category, score) in pii_name_indicators.items():
            if indicator in field_name_lower:
                # Reduce confidence for partial matches
                return True, indicator, score * 0.8

        # If a sample value is provided, check it against patterns
        if sample_value and isinstance(sample_value, str):
            matches = self.detect_pii_in_string(sample_value, field_name)
            if matches:
                # Use the highest confidence match
                highest_match = max(matches, key=lambda m: m.confidence)
                return True, highest_match.pii_type, highest_match.confidence

        return False, "", 0.0
