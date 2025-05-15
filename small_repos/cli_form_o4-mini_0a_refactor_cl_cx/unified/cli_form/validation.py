"""
Input Validation for cli_form

This module provides functions for validating form input data in real-time.
"""

def validate_input(form_field, value, audit_log_func=None):
    """
    Validate input against a field's rules and optionally log the validation.

    Args:
        form_field: The field object with validation rules
        value: The input value to validate
        audit_log_func (callable, optional): Function to call for audit logging
        
    Returns:
        tuple: (is_valid, error_message or None)
    """
    # Try different validation methods based on the field interface
    try:
        if hasattr(form_field, 'input'):
            # Security officer style validation with return values
            is_valid, error = form_field.input(value)
        elif hasattr(form_field, 'validate'):
            # Clinical researcher style validation with exceptions
            try:
                is_valid = form_field.validate(value)
                error = None
            except ValueError as e:
                is_valid = False
                error = str(e)
        else:
            # Simple validation fallback
            is_valid = True
            error = None
            
    except Exception as e:
        is_valid = False
        error = str(e)
    
    # Log the validation attempt if a logging function is provided
    if audit_log_func:
        audit_log_func(
            action="validate_input",
            field=getattr(form_field, 'name', str(form_field)),
            value=value if not getattr(form_field, 'mask_sensitive', False) else "*****",
            success=is_valid,
            error=error
        )
    
    return is_valid, error