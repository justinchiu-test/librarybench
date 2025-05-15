"""
Form Layout for cli_form

This module provides layout components for organizing form fields into
structured views such as wizards and grouped sections.
"""

class WizardLayout:
    """Multi-page wizard layout for complex forms with navigation between pages."""
    
    def __init__(self, pages):
        """
        Initialize a multi-page wizard layout.
        
        Args:
            pages (list): List of page names or objects
            
        Raises:
            ValueError: If pages list is empty
        """
        if not pages:
            raise ValueError("Wizard requires at least one page")
        
        self.pages = pages
        self.current_page_idx = 0
        self.page_fields = {i: [] for i in range(len(pages))}
        self.page_validators = {}
        self.completion_handlers = []
        
    def get_current_page(self):
        """
        Get the current page.
        
        Returns:
            object: The current page object or name
        """
        return self.pages[self.current_page_idx]
    
    def next_page(self):
        """
        Move to the next page in the wizard.
        
        Returns:
            object: The new current page
        """
        if self.current_page_idx < len(self.pages) - 1:
            self.current_page_idx += 1
        return self.get_current_page()
    
    def prev_page(self):
        """
        Move to the previous page in the wizard.
        
        Returns:
            object: The new current page
        """
        if self.current_page_idx > 0:
            self.current_page_idx -= 1
        return self.get_current_page()
    
    def add_field(self, page_idx, field, label, required=False):
        """
        Add a field to a specific page.
        
        Args:
            page_idx (int): Page index
            field: Field object to add
            label (str): Field label
            required (bool): Whether the field is required
            
        Raises:
            IndexError: If page_idx is out of range
        """
        if page_idx < 0 or page_idx >= len(self.pages):
            raise IndexError(f"Page index {page_idx} out of range")
            
        self.page_fields[page_idx].append({
            'field': field,
            'label': label,
            'required': required
        })
        
    def add_page_validator(self, page_idx, validator_func):
        """
        Add a validator function for an entire page.
        
        Args:
            page_idx (int): Page index
            validator_func (callable): Function that validates page data
        """
        self.page_validators[page_idx] = validator_func
        
    def add_completion_handler(self, handler_func):
        """
        Add a handler function called when the wizard is completed.
        
        Args:
            handler_func (callable): Function that processes wizard's completed data
        """
        self.completion_handlers.append(handler_func)
    
    def validate_current_page(self, values):
        """
        Validate all fields on the current page.
        
        Args:
            values (dict): Field values to validate
            
        Returns:
            tuple: (is_valid, error_message or None)
        """
        # Check required fields
        for field_data in self.page_fields[self.current_page_idx]:
            if field_data['required']:
                label = field_data['label']
                if label not in values or not values[label]:
                    return False, f"Field '{label}' is required"
                
        # Run page validator if defined
        if self.current_page_idx in self.page_validators:
            try:
                result = self.page_validators[self.current_page_idx](values)
                if isinstance(result, tuple):
                    return result
                elif result is False:
                    return False, "Page validation failed"
                # Assume validation passed if not explicitly failed
                return True, None
            except Exception as e:
                return False, str(e)
        
        return True, None
    
    def get_fields_for_current_page(self):
        """
        Get field definitions for the current page.
        
        Returns:
            list: List of field data dictionaries
        """
        return self.page_fields[self.current_page_idx]
    
    def complete(self, all_values):
        """
        Complete the wizard and run completion handlers.
        
        Args:
            all_values (dict): All collected field values
            
        Returns:
            dict: Possibly modified values from completion handlers
        """
        result = all_values
        for handler in self.completion_handlers:
            new_result = handler(result)
            if new_result is not None:
                result = new_result
        return result