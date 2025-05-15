"""Utility functions for the unified task manager library.

This module provides common utility functions that can be used across
all persona implementations, reducing code duplication and ensuring
consistent behavior.
"""

import json
import os
import re
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Union, TypeVar, Generic, Callable


class ValidationHelper:
    """Validation utilities for data handling."""
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
        """
        Validate that all required fields are present in the data.
        
        Args:
            data: The data to validate
            required_fields: List of required field names
            
        Returns:
            List[str]: List of missing field names (empty if all required fields are present)
        """
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
        return missing_fields
    
    @staticmethod
    def validate_field_type(value: Any, expected_type: Any) -> bool:
        """
        Validate that a value is of the expected type.
        
        Args:
            value: The value to validate
            expected_type: The expected type or types
            
        Returns:
            bool: True if value is of the expected type, False otherwise
        """
        return isinstance(value, expected_type)
    
    @staticmethod
    def validate_string_length(value: str, min_length: int = 0, max_length: Optional[int] = None) -> bool:
        """
        Validate that a string's length is within the specified range.
        
        Args:
            value: The string to validate
            min_length: The minimum allowed length
            max_length: The maximum allowed length (optional)
            
        Returns:
            bool: True if string length is valid, False otherwise
        """
        if not isinstance(value, str):
            return False
        
        if len(value) < min_length:
            return False
        
        if max_length is not None and len(value) > max_length:
            return False
        
        return True
    
    @staticmethod
    def validate_pattern(value: str, pattern: str) -> bool:
        """
        Validate that a string matches a regular expression pattern.
        
        Args:
            value: The string to validate
            pattern: The regular expression pattern
            
        Returns:
            bool: True if string matches pattern, False otherwise
        """
        if not isinstance(value, str):
            return False
        
        return bool(re.match(pattern, value))


class TimeUtils:
    """Date and time utilities."""
    
    @staticmethod
    def get_current_datetime() -> datetime:
        """
        Get the current datetime.
        
        Returns:
            datetime: The current datetime
        """
        return datetime.now()
    
    @staticmethod
    def get_current_date_string(format_str: str = "%Y-%m-%d") -> str:
        """
        Get the current date as a formatted string.
        
        Args:
            format_str: The date format string
            
        Returns:
            str: The formatted date string
        """
        return datetime.now().strftime(format_str)
    
    @staticmethod
    def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
        """
        Parse a datetime string.
        
        Args:
            date_str: The datetime string to parse
            format_str: The date format string
            
        Returns:
            Optional[datetime]: The parsed datetime, or None if parsing failed
        """
        try:
            return datetime.strptime(date_str, format_str)
        except ValueError:
            return None
    
    @staticmethod
    def datetime_to_string(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        Convert a datetime to a formatted string.
        
        Args:
            dt: The datetime to convert
            format_str: The date format string
            
        Returns:
            str: The formatted date string
        """
        return dt.strftime(format_str)
    
    @staticmethod
    def days_between(start_date: datetime, end_date: datetime) -> int:
        """
        Calculate the number of days between two dates.
        
        Args:
            start_date: The start date
            end_date: The end date
            
        Returns:
            int: The number of days between the dates
        """
        return (end_date - start_date).days
    
    @staticmethod
    def add_days(dt: datetime, days: int) -> datetime:
        """
        Add days to a datetime.
        
        Args:
            dt: The datetime
            days: The number of days to add
            
        Returns:
            datetime: The resulting datetime
        """
        return dt + timedelta(days=days)


class IDGenerator:
    """Utilities for generating and handling IDs."""
    
    @staticmethod
    def generate_uuid() -> uuid.UUID:
        """
        Generate a new UUID.
        
        Returns:
            uuid.UUID: A new UUID
        """
        return uuid.uuid4()
    
    @staticmethod
    def generate_uuid_str() -> str:
        """
        Generate a new UUID as a string.
        
        Returns:
            str: A new UUID as a string
        """
        return str(uuid.uuid4())
    
    @staticmethod
    def is_valid_uuid(uuid_str: str) -> bool:
        """
        Check if a string is a valid UUID.
        
        Args:
            uuid_str: The string to check
            
        Returns:
            bool: True if string is a valid UUID, False otherwise
        """
        try:
            uuid.UUID(uuid_str)
            return True
        except ValueError:
            return False


class FileUtils:
    """File-related utilities."""
    
    @staticmethod
    def ensure_directory_exists(directory_path: str) -> bool:
        """
        Ensure that a directory exists, creating it if necessary.
        
        Args:
            directory_path: The directory path
            
        Returns:
            bool: True if directory exists or was created, False otherwise
        """
        try:
            os.makedirs(directory_path, exist_ok=True)
            return True
        except Exception:
            return False
    
    @staticmethod
    def path_exists(path: str) -> bool:
        """
        Check if a path exists.
        
        Args:
            path: The path to check
            
        Returns:
            bool: True if path exists, False otherwise
        """
        return os.path.exists(path)
    
    @staticmethod
    def is_file(path: str) -> bool:
        """
        Check if a path is a file.
        
        Args:
            path: The path to check
            
        Returns:
            bool: True if path is a file, False otherwise
        """
        return os.path.isfile(path)
    
    @staticmethod
    def is_directory(path: str) -> bool:
        """
        Check if a path is a directory.
        
        Args:
            path: The path to check
            
        Returns:
            bool: True if path is a directory, False otherwise
        """
        return os.path.isdir(path)
    
    @staticmethod
    def join_paths(*paths: str) -> str:
        """
        Join path components.
        
        Args:
            *paths: Path components to join
            
        Returns:
            str: The joined path
        """
        return os.path.join(*paths)


class JsonUtils:
    """JSON handling utilities."""
    
    @staticmethod
    def to_json(obj: Any, **kwargs) -> str:
        """
        Convert an object to JSON.
        
        Args:
            obj: The object to convert
            **kwargs: Additional arguments to pass to json.dumps
            
        Returns:
            str: The JSON string
        """
        return json.dumps(obj, **kwargs)
    
    @staticmethod
    def from_json(json_str: str, **kwargs) -> Any:
        """
        Parse a JSON string.
        
        Args:
            json_str: The JSON string to parse
            **kwargs: Additional arguments to pass to json.loads
            
        Returns:
            Any: The parsed object
        """
        return json.loads(json_str, **kwargs)
    
    @staticmethod
    def save_to_file(obj: Any, file_path: str, **kwargs) -> bool:
        """
        Save an object to a JSON file.
        
        Args:
            obj: The object to save
            file_path: The file path
            **kwargs: Additional arguments to pass to json.dumps
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            with open(file_path, 'w') as f:
                json.dump(obj, f, **kwargs)
            return True
        except Exception:
            return False
    
    @staticmethod
    def load_from_file(file_path: str, **kwargs) -> Optional[Any]:
        """
        Load an object from a JSON file.
        
        Args:
            file_path: The file path
            **kwargs: Additional arguments to pass to json.loads
            
        Returns:
            Optional[Any]: The loaded object, or None if loading failed
        """
        try:
            with open(file_path, 'r') as f:
                return json.load(f, **kwargs)
        except Exception:
            return None