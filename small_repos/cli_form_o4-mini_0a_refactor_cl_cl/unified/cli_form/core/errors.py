"""
Error handling and formatting for the CLI Form Library.
"""
import typing as t


def format_error(
    field_or_message: str, 
    message: t.Optional[str] = None, 
    highlight: bool = False,
    critical: bool = False
) -> str:
    """
    Format an error message with consistent styling.
    
    Args:
        field_or_message: Field name or error message
        message: Optional error message if field is provided separately
        highlight: Whether to highlight the error
        critical: Whether this is a critical error
        
    Returns:
        Formatted error message string
    """
    # Handle the two different calling conventions
    if message is None:
        # Only message provided
        error_msg = field_or_message
        prefix = ""
    else:
        # Field and message provided separately
        error_msg = message
        prefix = f"{field_or_message}: "
    
    # Format based on severity and highlighting
    if critical:
        return f"*** ERROR: {prefix}{error_msg} ***"
    elif highlight:
        return f"**ERROR** {prefix}{error_msg}"
    else:
        return f"ERROR: {prefix}{error_msg}" if not prefix else f"ERROR {prefix}{error_msg}"