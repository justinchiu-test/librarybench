"""Error classes for configuration validation."""
from typing import Optional, List, Any, Union, Dict


class ValidationError(Exception):
    """Error raised when configuration validation fails."""
    
    def __init__(self, 
                message: str,
                file: Optional[str] = None,
                line: Optional[int] = None,
                section: Optional[str] = None,
                key: Optional[str] = None,
                path: Optional[str] = None,
                expected: Optional[str] = None,
                actual: Optional[str] = None,
                suggestions: Optional[List[str]] = None):
        """Initialize a validation error.
        
        Args:
            message: The error message
            file: Optional configuration file path
            line: Optional line number in the configuration file
            section: Optional section in the configuration file
            key: Optional key in the configuration
            path: Optional dot notation path in the configuration
            expected: Optional expected type or value
            actual: Optional actual type or value
            suggestions: Optional list of suggested corrections
        """
        self.message = message
        self.file = file
        self.line = line
        self.section = section
        self.key = key
        self.path = path
        self.expected = expected
        self.actual = actual
        self.suggestions = suggestions or []
        
        # Construct a detailed error message
        details = []
        
        if file:
            details.append(f"File '{file}'")
            
        if line:
            details.append(f"Line {line}")
            
        if section:
            details.append(f"In section '{section}'")
            
        if key:
            details.append(f"Key '{key}'")
            
        if path:
            details.append(f"Path '{path}'")
            
        if expected and actual:
            details.append(f"Expected type: {expected}, got: {actual}")
            
        details.append(message)
        
        if suggestions:
            details.append(f"Suggestions: {', '.join(suggestions)}")
            
        super().__init__(". ".join(details))


class ConfigurationError(Exception):
    """Error raised when configuration loading or parsing fails."""
    
    def __init__(self, message: str, file: Optional[str] = None):
        """Initialize a configuration error.
        
        Args:
            message: The error message
            file: Optional configuration file path
        """
        self.message = message
        self.file = file
        
        if file:
            super().__init__(f"Error in configuration file '{file}': {message}")
        else:
            super().__init__(f"Configuration error: {message}")


class SchemaError(Exception):
    """Error raised when schema generation or validation fails."""
    
    def __init__(self, message: str):
        """Initialize a schema error.
        
        Args:
            message: The error message
        """
        self.message = message
        super().__init__(f"Schema error: {message}")