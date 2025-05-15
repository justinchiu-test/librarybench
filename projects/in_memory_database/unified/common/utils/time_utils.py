"""
Time-related utilities.

This module provides functions for handling and formatting timestamps and dates.
"""

import time
import datetime
from typing import Optional, Union


def get_timestamp() -> float:
    """
    Get the current timestamp.
    
    Returns:
        The current time as a Unix timestamp (seconds since epoch).
    """
    return time.time()


def format_timestamp(
    timestamp: float,
    format_str: str = "%Y-%m-%d %H:%M:%S"
) -> str:
    """
    Format a timestamp as a string.
    
    Args:
        timestamp: Unix timestamp (seconds since epoch).
        format_str: Format string for the output. Default is "%Y-%m-%d %H:%M:%S".
    
    Returns:
        Formatted timestamp string.
    """
    dt = datetime.datetime.fromtimestamp(timestamp)
    return dt.strftime(format_str)


def parse_timestamp(
    timestamp_str: str,
    format_str: Optional[str] = None
) -> float:
    """
    Parse a timestamp string into a Unix timestamp.
    
    Args:
        timestamp_str: String representation of a timestamp.
        format_str: Format string for parsing. If None, several common formats
                    will be tried.
    
    Returns:
        Unix timestamp (seconds since epoch).
    
    Raises:
        ValueError: If the string cannot be parsed as a timestamp.
    """
    if format_str:
        # Parse with the specified format
        dt = datetime.datetime.strptime(timestamp_str, format_str)
        return dt.timestamp()
    
    # Try common formats
    formats = [
        "%Y-%m-%d %H:%M:%S",  # 2023-01-30 12:34:56
        "%Y-%m-%dT%H:%M:%S",   # 2023-01-30T12:34:56
        "%Y-%m-%dT%H:%M:%S.%fZ",  # 2023-01-30T12:34:56.789Z
        "%Y-%m-%d",            # 2023-01-30
        "%m/%d/%Y %H:%M:%S",   # 01/30/2023 12:34:56
        "%m/%d/%Y",            # 01/30/2023
    ]
    
    for fmt in formats:
        try:
            dt = datetime.datetime.strptime(timestamp_str, fmt)
            return dt.timestamp()
        except ValueError:
            continue
    
    # Try parsing an ISO format string
    try:
        dt = datetime.datetime.fromisoformat(timestamp_str)
        return dt.timestamp()
    except ValueError:
        pass
    
    # Try parsing as a Unix timestamp
    try:
        return float(timestamp_str)
    except ValueError:
        pass
    
    raise ValueError(f"Could not parse timestamp string: {timestamp_str}")


def time_since(
    timestamp: float
) -> str:
    """
    Format the time elapsed since a timestamp in a human-readable format.
    
    Args:
        timestamp: Unix timestamp (seconds since epoch).
    
    Returns:
        Human-readable string representing the elapsed time (e.g., "2 hours ago").
    """
    now = time.time()
    diff = now - timestamp
    
    if diff < 60:
        return "just now"
    elif diff < 3600:
        minutes = int(diff / 60)
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    elif diff < 86400:
        hours = int(diff / 3600)
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff < 604800:
        days = int(diff / 86400)
        return f"{days} day{'s' if days > 1 else ''} ago"
    elif diff < 2592000:
        weeks = int(diff / 604800)
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    elif diff < 31536000:
        months = int(diff / 2592000)
        return f"{months} month{'s' if months > 1 else ''} ago"
    else:
        years = int(diff / 31536000)
        return f"{years} year{'s' if years > 1 else ''} ago"