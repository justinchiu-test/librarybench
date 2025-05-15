"""
Field Types for cli_form

This module provides various field types for collecting different kinds of data
in command-line forms. Each field type handles its own validation and rendering.
"""

import re
from datetime import datetime, timezone, timedelta


class TextField:
    """A text input field with validation for patterns and length."""
    
    def __init__(self, name=None, regex=None, max_length=None, placeholder='', mask_sensitive=False):
        """
        Initialize a text field.
        
        Args:
            name (str, optional): Field name for identification
            regex (str, optional): Regular expression pattern for validation
            max_length (int, optional): Maximum length of input
            placeholder (str, optional): Default placeholder text
            mask_sensitive (bool, optional): Whether to mask the value when displayed
        """
        self.name = name
        self.regex = re.compile(regex) if regex else None
        self.max_length = max_length
        self.placeholder = placeholder
        self.mask_sensitive = mask_sensitive
        self._raw_value = None
        
    def validate(self, value):
        """
        Validate the input value against configured constraints.
        
        Args:
            value (str): The input value to validate
            
        Returns:
            tuple: (is_valid, error_message) or True if no error checking is done
            
        Raises:
            ValueError: If validation fails and using exception-based validation
        """
        if self.max_length is not None and len(value) > self.max_length:
            error = f"Value exceeds maximum length of {self.max_length}"
            if self.name:
                error = f"Value for {self.name} {error}"
            
            # Support both return types for backward compatibility
            if hasattr(self, 'input'):
                return False, error
            else:
                raise ValueError(error)
                
        if self.regex and not self.regex.match(value):
            error = "Value does not match required pattern"
            if self.name:
                error = f"Value for {self.name} {error}"
                
            # Support both return types for backward compatibility
            if hasattr(self, 'input'):
                return False, error
            else:
                raise ValueError(error)
                
        # Support both return types for backward compatibility
        if hasattr(self, 'input'):
            return True, None
        else:
            return True
    
    def input(self, value):
        """
        Process and validate input, storing the value if valid.
        
        Args:
            value (str): The input value
            
        Returns:
            tuple: (is_valid, error_message)
        """
        valid, err = self.validate(value) if not isinstance(self.validate(value), bool) else (self.validate(value), None)
        if not valid:
            return False, err
        self._raw_value = value
        return True, None
        
    def get_value(self):
        """
        Get the field's value, masking if necessary.
        
        Returns:
            str: The field value, masked if sensitive
        """
        if self.mask_sensitive and self._raw_value is not None:
            return "*" * len(self._raw_value)
        return self._raw_value


class DateTimePicker:
    """Field for selecting date and time values with validation."""
    
    def __init__(self, timezone_offset_hours=0):
        """
        Initialize a date/time picker.
        
        Args:
            timezone_offset_hours (int, optional): Timezone offset in hours
        """
        self.tz = timezone(timedelta(hours=timezone_offset_hours))
        self.selected_date = None
        self.selected_time = None
        self._picked = None
        
    def pick_date(self, date_str):
        """
        Pick a date from string input.
        
        Args:
            date_str (str): Date in YYYY-MM-DD format
            
        Returns:
            date: The parsed date object
            
        Raises:
            ValueError: If date format is invalid
        """
        try:
            self.selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            return self.selected_date
        except ValueError:
            raise ValueError("Invalid date format, expected YYYY-MM-DD")
    
    def pick_time(self, time_str):
        """
        Pick a time from string input.
        
        Args:
            time_str (str): Time in HH:MM format
            
        Returns:
            time: The parsed time object
            
        Raises:
            ValueError: If time format is invalid
        """
        try:
            self.selected_time = datetime.strptime(time_str, "%H:%M").time()
            return self.selected_time
        except ValueError:
            raise ValueError("Invalid time format, expected HH:MM")
    
    def pick(self, dt):
        """
        Pick a datetime object directly.
        
        Args:
            dt (datetime): The datetime object to use
            
        Returns:
            datetime: The normalized datetime
            
        Raises:
            ValueError: If input is not a valid datetime
        """
        if not isinstance(dt, datetime):
            raise ValueError("Invalid datetime object")
        # Normalize to configured timezone
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        self._picked = dt.astimezone(self.tz)
        return self._picked
    
    def get_value(self):
        """
        Get the picked datetime value.
        
        Returns:
            datetime: The complete datetime or None if not yet picked
        """
        # First try the complete datetime from pick()
        if self._picked is not None:
            return self._picked
        
        # Otherwise try to build from date and time parts
        if self.selected_date and self.selected_time:
            dt = datetime.combine(self.selected_date, self.selected_time)
            return dt.replace(tzinfo=self.tz)
        
        # Fall back to date only
        if self.selected_date:
            return datetime.combine(self.selected_date, datetime.min.time()).replace(tzinfo=self.tz)
            
        return None