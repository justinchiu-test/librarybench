"""
Predefined patterns for sensitive data detection.

This module contains regular expressions and other patterns for detecting
various types of sensitive data, including PII, financial information,
health records, and proprietary business data.
"""

import re
from typing import Dict, List

# Import from common library
from common.utils.types import SensitivityLevel, ComplianceCategory
from common.core.patterns import FilePattern, FilePatternRegistry, PatternValidator


class SensitiveDataPattern(FilePattern):
    """Definition of a sensitive data pattern for security auditing."""
    pass


class PatternDefinitions:
    """Predefined patterns for sensitive data detection."""

    # Social Security Numbers
    SSN = SensitiveDataPattern(
        name="Social Security Number",
        description="US Social Security Number",
        pattern=r"\b(?!000|666|9\d{2})([0-8]\d{2}|7([0-6]\d))-(?!00)(\d{2})-(?!0000)(\d{4})\b",
        sensitivity=SensitivityLevel.HIGH,
        category=ComplianceCategory.PII,
        validation_func="validate_ssn"
    )

    # Credit Card Numbers
    CREDIT_CARD = SensitiveDataPattern(
        name="Credit Card Number",
        description="Credit card number (major brands)",
        pattern=r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12}|(?:2131|1800|35\d{3})\d{11})\b",
        sensitivity=SensitivityLevel.HIGH,
        category=ComplianceCategory.PCI,
        validation_func="validate_credit_card"
    )

    # Credit Card with separators
    CREDIT_CARD_FORMATTED = SensitiveDataPattern(
        name="Formatted Credit Card Number",
        description="Credit card with dashes or spaces",
        pattern=r"\b(?:4[0-9]{3}[\s-]?[0-9]{4}[\s-]?[0-9]{4}[\s-]?[0-9](?:[0-9]{2})?|5[1-5][0-9]{2}[\s-]?[0-9]{4}[\s-]?[0-9]{4}[\s-]?[0-9]{4}|3[47][0-9]{2}[\s-]?[0-9]{6}[\s-]?[0-9]{5})\b",
        sensitivity=SensitivityLevel.HIGH,
        category=ComplianceCategory.PCI,
        validation_func="validate_credit_card"
    )

    # Email Addresses
    EMAIL_ADDRESS = SensitiveDataPattern(
        name="Email Address",
        description="Email address",
        pattern=r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        sensitivity=SensitivityLevel.MEDIUM,
        category=ComplianceCategory.PII
    )

    # Phone Numbers
    PHONE_NUMBER_US = SensitiveDataPattern(
        name="US Phone Number",
        description="US phone number (various formats)",
        pattern=r"\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b",
        sensitivity=SensitivityLevel.MEDIUM,
        category=ComplianceCategory.PII
    )

    # IP Addresses
    IP_ADDRESS = SensitiveDataPattern(
        name="IP Address",
        description="IPv4 address",
        pattern=r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",
        sensitivity=SensitivityLevel.LOW,
        category=ComplianceCategory.OTHER
    )

    # Date of Birth
    DATE_OF_BIRTH = SensitiveDataPattern(
        name="Date of Birth",
        description="Date of birth in common formats",
        pattern=r"\b(?:(?:0[1-9]|1[0-2])[/.-](?:0[1-9]|[12][0-9]|3[01])[/.-](?:19|20)\d{2}|(?:19|20)\d{2}[/.-](?:0[1-9]|1[0-2])[/.-](?:0[1-9]|[12][0-9]|3[01]))\b",
        sensitivity=SensitivityLevel.MEDIUM,
        category=ComplianceCategory.PII
    )

    # Passport Numbers
    PASSPORT_US = SensitiveDataPattern(
        name="US Passport Number",
        description="US passport number",
        pattern=r"\b[A-Z][0-9]{8}\b",
        sensitivity=SensitivityLevel.HIGH,
        category=ComplianceCategory.PII
    )

    # Driver's License
    DRIVERS_LICENSE = SensitiveDataPattern(
        name="Driver's License Number",
        description="Driver's license number (common formats)",
        pattern=r"\b[A-Z][0-9]{7}\b|\b[A-Z][0-9]{8}\b|\b[0-9]{9}\b",
        sensitivity=SensitivityLevel.HIGH,
        category=ComplianceCategory.PII
    )

    # Bank Account Numbers
    BANK_ACCOUNT = SensitiveDataPattern(
        name="Bank Account Number",
        description="Bank account number (common formats)",
        pattern=r"\b[0-9]{9,17}\b",
        sensitivity=SensitivityLevel.HIGH,
        category=ComplianceCategory.FINANCIAL,
        context_rules=["must be near words like account, routing, bank"]
    )

    # API Keys/Tokens
    API_KEY = SensitiveDataPattern(
        name="API Key",
        description="Common API key formats",
        pattern=r"\b[A-Za-z0-9_\-]{32,45}\b",
        sensitivity=SensitivityLevel.HIGH,
        category=ComplianceCategory.CREDENTIALS,
        context_rules=["must be near words like key, api, token, secret"]
    )

    # Medical Record Numbers
    MEDICAL_RECORD = SensitiveDataPattern(
        name="Medical Record Number",
        description="Medical record number (common formats)",
        pattern=r"\bMR[0-9]{6,10}\b|\b[A-Z]{2}[0-9]{6,10}\b",
        sensitivity=SensitivityLevel.HIGH,
        category=ComplianceCategory.PHI
    )

    # Health Insurance Numbers
    HEALTH_INSURANCE = SensitiveDataPattern(
        name="Health Insurance Number",
        description="Health insurance ID number (common formats)",
        pattern=r"\b[A-Z0-9]{6,12}\b",
        sensitivity=SensitivityLevel.HIGH,
        category=ComplianceCategory.PHI,
        context_rules=["must be near words like health, insurance, coverage, plan"]
    )

    # Password patterns
    PASSWORD = SensitiveDataPattern(
        name="Password",
        description="Password in configuration or code",
        pattern=r"(?:password|passwd|pwd)[\s:=]+['\"](.*?)['\"]",
        sensitivity=SensitivityLevel.CRITICAL,
        category=ComplianceCategory.CREDENTIALS
    )

    @classmethod
    def get_all_patterns(cls) -> List[SensitiveDataPattern]:
        """Get all predefined patterns."""
        return [
            getattr(cls, attr) for attr in dir(cls)
            if not attr.startswith('_') and isinstance(getattr(cls, attr), SensitiveDataPattern)
        ]

    @classmethod
    def get_by_category(cls, category: ComplianceCategory) -> List[SensitiveDataPattern]:
        """Get all patterns for a specific compliance category."""
        return [p for p in cls.get_all_patterns() if p.category == category]

    @classmethod
    def get_by_sensitivity(cls, level: SensitivityLevel) -> List[SensitiveDataPattern]:
        """Get all patterns for a specific sensitivity level."""
        return [p for p in cls.get_all_patterns() if p.sensitivity == level]


# Register patterns with the common registry
for pattern in PatternDefinitions.get_all_patterns():
    FilePatternRegistry.register_pattern(pattern, "security_audit")


class PatternValidators:
    """Validation functions for sensitive data patterns."""
    
    @staticmethod
    def validate_ssn(ssn: str) -> bool:
        """Validate a Social Security Number."""
        return PatternValidator.validate_ssn(ssn)
    
    @staticmethod
    def validate_credit_card(cc: str) -> bool:
        """Validate a credit card number using the Luhn algorithm."""
        return PatternValidator.validate_credit_card(cc)