"""
Layout engines for the CLI Form Library.
"""
import typing as t


class WizardLayout:
    """
    Layout engine for multi-page forms with navigation.
    """
    
    def __init__(self, pages: t.List[t.Any]):
        """
        Initialize the wizard layout with a list of pages.
        
        Args:
            pages: List of pages, where each page can be any object 
                  (string, list of fields, etc.)
        
        Raises:
            ValueError: If pages list is empty
        """
        if not pages:
            raise ValueError("Pages list cannot be empty")
            
        self.pages = pages
        self.current_idx = 0
        
    def get_current_page(self) -> t.Any:
        """Get the current page content."""
        return self.pages[self.current_idx]
        
    def current_page(self) -> t.Any:
        """Alternative name for get_current_page."""
        return self.get_current_page()
        
    def next_page(self) -> t.Any:
        """
        Navigate to the next page and return its content.
        If already at the last page, stay there.
        """
        if self.current_idx < len(self.pages) - 1:
            self.current_idx += 1
        return self.get_current_page()
        
    def next(self) -> t.Any:
        """Alternative name for next_page."""
        return self.next_page()
        
    def prev_page(self) -> t.Any:
        """
        Navigate to the previous page and return its content.
        If already at the first page, stay there.
        """
        if self.current_idx > 0:
            self.current_idx -= 1
        return self.get_current_page()
        
    def prev(self) -> t.Any:
        """Alternative name for prev_page."""
        return self.prev_page()
        
    def is_finished(self) -> bool:
        """Check if we're at the last page."""
        return self.current_idx == len(self.pages) - 1