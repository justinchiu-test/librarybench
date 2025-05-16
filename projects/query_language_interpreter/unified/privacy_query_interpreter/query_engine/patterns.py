"""Pattern detection for privacy query parsing."""

from typing import Any, Dict, List, Optional, Set, Tuple

from common.pattern.detector import BasePatternDetector
from common.pattern.matcher import PatternMatch
from common.pattern.sql import SQLPrivacyPatternDetector
from common.models.enums import PrivacyFunction


class PrivacyPatternDetector(BasePatternDetector):
    """Detector for privacy-specific patterns in SQL queries."""

    def __init__(self):
        """Initialize the privacy pattern detector."""
        super().__init__()
        # Use the common SQL pattern detector
        self.sql_detector = SQLPrivacyPatternDetector()
        # Add PII field patterns
        self._add_pii_field_patterns()

    def _add_pii_field_patterns(self) -> None:
        """Add patterns for common PII fields."""
        pii_fields = {
            "email": ["email", "e_mail", "email_address", "mail"],
            "name": ["name", "fullname", "full_name", "first_name", "last_name"],
            "phone": ["phone", "phone_number", "telephone", "mobile", "cell"],
            "address": [
                "address",
                "street",
                "city",
                "state",
                "country",
                "zip",
                "postal",
            ],
            "id": [
                "ssn",
                "social_security",
                "passport",
                "id_number",
                "id_card",
                "driver_license",
            ],
            "financial": [
                "credit_card",
                "cc_number",
                "account_number",
                "bank_account",
                "iban",
            ],
            "health": [
                "health",
                "medical",
                "diagnosis",
                "treatment",
                "medication",
                "patient",
            ],
            "biometric": [
                "biometric",
                "fingerprint",
                "dna",
                "retina",
                "face_id",
                "voice_print",
            ],
        }

        # Add patterns for each PII field category
        for category, fields in pii_fields.items():
            field_pattern = "|".join(fields)
            self.add_pattern(
                pattern_id=f"pii_field_{category}",
                regex=rf"(?P<table>\w+\.)?(?P<field>{field_pattern})",
                category="pii_field",
                metadata={"pii_type": category},
            )

    def extract_privacy_functions(self, query_text: str) -> List[Dict[str, Any]]:
        """
        Extract privacy function calls from the query.

        Args:
            query_text: The SQL query text

        Returns:
            List of detected privacy functions with their parameters
        """
        # Use the common SQL pattern detector to extract privacy functions
        privacy_func_dicts = self.sql_detector.detect_privacy_functions(query_text)

        # Format the results to match the expected format for backward compatibility
        privacy_funcs = []
        for func_dict in privacy_func_dicts:
            privacy_funcs.append(
                {
                    "function": PrivacyFunction(func_dict["function"]),
                    "field": func_dict["field"],
                    "args": func_dict["args"],
                    "confidence": 1.0,  # Default confidence
                }
            )

        return privacy_funcs

    def detect_pii_fields(self, query_text: str) -> List[Dict[str, Any]]:
        """
        Detect potential PII fields in a query.

        Args:
            query_text: The SQL query text

        Returns:
            List of detected PII fields with metadata
        """
        pii_fields = []

        # Use the pattern detector to find all PII field patterns
        matches = self.detect_by_category(query_text, "pii_field")

        for match in matches:
            # Extract information from the match
            pii_type = match.metadata.get("pii_type")
            field = match.groups.get("field", "")
            table = match.groups.get("table", "")

            # Remove trailing dot from table if present
            if table and table.endswith("."):
                table = table[:-1]

            pii_fields.append(
                {
                    "field": field,
                    "table": table,
                    "pii_type": pii_type,
                    "confidence": match.confidence,
                }
            )

        return pii_fields
