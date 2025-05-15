"""Interactive prompting for missing configuration values."""
import os
import sys
from typing import Any, Optional, Type, TypeVar, cast, List, Union

from ..utils.type_converter import convert_value

T = TypeVar('T')


def prompt_for_value(
    key: str,
    expected_type: Optional[Type[T]] = None,
    prompt: Optional[str] = None,
    default: Optional[Any] = None
) -> Any:
    """Prompt the user for a value.
    
    Args:
        key: The configuration key
        expected_type: Optional expected type for the value
        prompt: Optional custom prompt message
        default: Optional default value
        
    Returns:
        The value entered by the user
        
    Note:
        This function will be skipped in non-interactive environments (like CI)
        and return the default value or None.
    """
    # Skip prompting in CI environments
    if os.environ.get('CI') or os.environ.get('AUTOMATED_TESTING'):
        return default
        
    # Default prompt
    prompt_text = prompt or f"Enter value for '{key}'"
    
    # Add type information if available
    if expected_type is not None:
        type_name = expected_type.__name__
        prompt_text += f" (type: {type_name})"
        
    # Add default value if available
    if default is not None:
        prompt_text += f" [default: {default}]"
        
    prompt_text += ": "
    
    # Get user input
    try:
        value = input(prompt_text)
        
        # Use default if input is empty
        if not value and default is not None:
            return default
            
        # Convert to expected type if specified
        if expected_type is not None:
            try:
                return convert_value(value, expected_type)
            except ValueError:
                print(f"Invalid input: expected {expected_type.__name__}")
                return prompt_for_value(key, expected_type, prompt, default)
                
        return value
    except (KeyboardInterrupt, EOFError):
        print("\nPrompt interrupted")
        return default or None


def prompt_missing(key: str, expected_type: Optional[Type[T]] = None) -> T:
    """Prompt the user for a missing value and convert to the expected type.
    
    Args:
        key: The configuration key
        expected_type: Optional expected type for the value
        
    Returns:
        The value entered by the user, converted to the expected type
    """
    value = prompt_for_value(key, expected_type)
    
    if expected_type is not None and value is not None:
        return cast(T, convert_value(value, expected_type))
        
    return cast(T, value or None)