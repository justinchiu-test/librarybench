"""
Helper functions for formatting in the CLI Form Library.
"""
import typing as t
from datetime import datetime


def format_date(date: datetime, format_str: str = "%Y-%m-%d") -> str:
    """
    Format a date according to the specified format.
    
    Args:
        date: Date to format
        format_str: Format string
        
    Returns:
        Formatted date string
    """
    return date.strftime(format_str)


def format_time(time, format_str: str = "%H:%M") -> str:
    """
    Format a time according to the specified format.
    
    Args:
        time: Time to format (can be datetime or time)
        format_str: Format string
        
    Returns:
        Formatted time string
    """
    if hasattr(time, 'strftime'):
        return time.strftime(format_str)
    return str(time)


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to the specified length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
        
    return text[:max_length - len(suffix)] + suffix


def format_field_value(value: t.Any, field_type: str) -> str:
    """
    Format a field value based on its type.
    
    Args:
        value: Value to format
        field_type: Type of the field
        
    Returns:
        Formatted value as a string
    """
    if field_type == "date":
        if isinstance(value, datetime):
            return format_date(value)
        return value
    elif field_type == "time":
        return format_time(value)
    elif field_type == "datetime":
        if isinstance(value, datetime):
            return f"{format_date(value)} {format_time(value)}"
        return value
    elif field_type == "boolean":
        return "Yes" if value else "No"
    elif field_type == "number":
        return str(value)
        
    # Default: string
    return str(value)