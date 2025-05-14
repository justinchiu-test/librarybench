"""
Core field types for CLI Form Library.
"""
import re
from datetime import datetime, timezone, timedelta
import typing as t


class TextField:
    """Base text field with validation capabilities."""
    
    def __init__(
        self, 
        name: str = "",
        regex: t.Optional[str] = None, 
        pattern: t.Optional[str] = None,  # Alternative name for regex
        max_length: t.Optional[int] = None, 
        length_limit: t.Optional[int] = None,  # Alternative name for max_length
        placeholder: str = "", 
        mask_sensitive: bool = False,
        required: bool = False
    ):
        self.name = name
        self.regex = regex or pattern
        self.max_length = max_length or length_limit
        self.placeholder = placeholder
        self.mask_sensitive = mask_sensitive
        self.required = required
        self._value = ""
        
    def validate(self, value: str) -> t.Union[bool, t.Tuple[bool, str]]:
        """Validate the input value against the field's constraints."""
        self._value = value
        
        # Check if value is required but empty
        if self.required and not value:
            error_msg = f"{self.name} is required"
            return False, error_msg
            
        # Check for max length
        if self.max_length is not None and len(value) > self.max_length:
            error_msg = f"{self.name} exceeds max length ({self.max_length})"
            return False, error_msg
            
        # Check for regex pattern
        if self.regex and not re.match(self.regex, value):
            error_msg = f"{self.name} does not match pattern: {self.regex}"
            return False, error_msg
            
        return True, ""
        
    def input(self, value: str) -> t.Tuple[bool, t.Optional[str]]:
        """Process input and store value if valid."""
        valid, error = self.validate(value)
        return valid, error if not valid else None
        
    def get_value(self) -> str:
        """Get the field's value, masked if sensitive."""
        if self.mask_sensitive and self._value:
            return '*' * len(self._value)
        return self._value


class DateTimePicker:
    """Field for selecting date and time values."""
    
    def __init__(self, timezone_offset_hours: t.Optional[int] = 0):
        self.timezone_offset_hours = timezone_offset_hours
        
    def pick_date(self, date_str: str) -> datetime:
        """Parse and validate a date string."""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD format.")
            
    def pick_time(self, time_str: str) -> datetime.time:
        """Parse and validate a time string."""
        try:
            time_obj = datetime.strptime(time_str, "%H:%M").time()
            return time_obj
        except ValueError:
            raise ValueError(f"Invalid time format: {time_str}. Use HH:MM format.")
            
    def pick(self, value=None) -> datetime:
        """Create datetime with timezone information."""
        if value is None:
            dt = datetime.now()
        elif isinstance(value, datetime):
            dt = value
        else:
            raise ValueError("Input must be a datetime object")
            
        # If the datetime is naive (no timezone), assign one
        if dt.tzinfo is None:
            tzinfo = timezone(timedelta(hours=self.timezone_offset_hours))
            dt = dt.replace(tzinfo=tzinfo)
        # If it already has timezone, convert to the target timezone
        else:
            tzinfo = timezone(timedelta(hours=self.timezone_offset_hours))
            dt = dt.astimezone(tzinfo)
            
        return dt