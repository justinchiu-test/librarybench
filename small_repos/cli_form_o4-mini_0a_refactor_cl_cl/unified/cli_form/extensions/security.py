"""
Security-specific features for the CLI Form Library.
"""
import re
import typing as t


def mask_sensitive_data(value: str, mask_char: str = "*") -> str:
    """
    Mask sensitive data with the specified character.
    
    Args:
        value: String to mask
        mask_char: Character to use for masking
        
    Returns:
        Masked string
    """
    return mask_char * len(value)


def sanitize_input(value: str) -> str:
    """
    Sanitize input by removing potentially dangerous characters.
    
    Args:
        value: Input string to sanitize
        
    Returns:
        Sanitized string
    """
    # Remove HTML/XML tags and special characters
    return re.sub(r'[<>&;"]', '', value)


def validate_security_field(field_type: str, value: str) -> t.Tuple[bool, t.Optional[str]]:
    """
    Validate security-specific field types.
    
    Args:
        field_type: Type of security field
        value: Input value to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if field_type == "incident_id":
        if not re.match(r'^INC-\d{4}$', value):
            return False, "Incident ID must be in format INC-NNNN"
    elif field_type == "ip_address":
        if not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', value):
            return False, "Invalid IP address format"
    elif field_type == "cve_id":
        if not re.match(r'^CVE-\d{4}-\d+$', value):
            return False, "Invalid CVE ID format"
            
    return True, None