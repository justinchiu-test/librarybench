"""
Form Renderer for cli_form

This module provides rendering capabilities for displaying forms in the console,
with support for both curses-based and fallback text-only rendering.
"""

import curses
import os
import sys
from contextlib import contextmanager


class CursesRenderer:
    """A curses-based renderer for full-screen forms with navigation."""
    
    def __init__(self, accessibility_mode=False):
        """
        Initialize the curses renderer.
        
        Args:
            accessibility_mode (bool): Enable accessibility features
        """
        self.stdscr = None
        self.fields = []
        self.current_field_idx = 0
        self.accessibility_mode = accessibility_mode
        self.help_text = {}
        self.status_message = ""
        self.is_initialized = False
        
    def initialize(self):
        """Initialize the curses screen if not already initialized."""
        if not self.is_initialized:
            self.stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()
            self.stdscr.keypad(True)
            if not self.accessibility_mode:
                curses.start_color()
                curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)    # Normal
                curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)   # Selected
                curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)     # Error
            self.is_initialized = True
        
    def cleanup(self):
        """Clean up the curses environment."""
        if self.is_initialized:
            self.stdscr.keypad(False)
            curses.nocbreak()
            curses.echo()
            curses.endwin()
            self.is_initialized = False
    
    @contextmanager
    def screen(self):
        """Context manager for the curses screen."""
        try:
            self.initialize()
            yield self.stdscr
        finally:
            self.cleanup()
            
    def add_field(self, field, label, help_text=None):
        """
        Add a field to the form.
        
        Args:
            field: The field object
            label (str): Display label for the field
            help_text (str, optional): Help text shown when field is focused
        """
        self.fields.append({'field': field, 'label': label})
        if help_text:
            self.help_text[len(self.fields) - 1] = help_text
    
    def next_field(self):
        """Move to the next field in the form."""
        if self.fields:
            self.current_field_idx = (self.current_field_idx + 1) % len(self.fields)
        
    def prev_field(self):
        """Move to the previous field in the form."""
        if self.fields:
            self.current_field_idx = (self.current_field_idx - 1) % len(self.fields)
    
    def set_status(self, message):
        """
        Set a status message to display at the bottom of the form.
        
        Args:
            message (str): The status message
        """
        self.status_message = message
    
    def render(self):
        """
        Render the form using curses if available, or fall back to line-by-line prompts.
        
        Returns:
            dict: Collected field values
        """
        # Check if curses is available (might not be in some environments)
        if 'TERM' not in os.environ or os.environ['TERM'] == 'dumb':
            return self._fallback_render()
            
        try:
            with self.screen() as stdscr:
                return self._curses_render(stdscr)
        except Exception:
            # Fallback to simple rendering if curses fails
            return self._fallback_render()
    
    def _curses_render(self, stdscr):
        """
        Render using curses for full-screen interface.
        
        Args:
            stdscr: The curses screen
            
        Returns:
            dict: Collected field values
        """
        values = {}
        
        while True:
            stdscr.clear()
            height, width = stdscr.getmaxyx()
            
            # Draw title bar
            title = "Form"
            stdscr.addstr(0, (width - len(title)) // 2, title, curses.A_BOLD)
            
            # Draw fields
            for i, field_data in enumerate(self.fields):
                field = field_data['field']
                label = field_data['label']
                
                is_current = i == self.current_field_idx
                
                # Calculate y position, leaving space for title and status
                y_pos = 2 + i * 2
                
                # Skip if beyond screen bounds
                if y_pos >= height - 3:
                    continue
                
                # Draw label
                if is_current and not self.accessibility_mode:
                    stdscr.addstr(y_pos, 2, label, curses.color_pair(2))
                else:
                    stdscr.addstr(y_pos, 2, label)
                
                # Draw field value or placeholder
                value = getattr(field, 'get_value', lambda: None)()
                if value is None:
                    value = getattr(field, 'placeholder', '')
                    
                if y_pos + 1 < height - 3:
                    if is_current and not self.accessibility_mode:
                        stdscr.addstr(y_pos + 1, 4, str(value), curses.color_pair(2))
                    else:
                        stdscr.addstr(y_pos + 1, 4, str(value))
            
            # Draw help text for current field
            if self.current_field_idx in self.help_text and height > 5:
                help_y = min(height - 5, 2 + len(self.fields) * 2 + 1)
                help_text = self.help_text[self.current_field_idx]
                if len(help_text) > width - 4:
                    help_text = help_text[:width - 7] + "..."
                stdscr.addstr(help_y, 2, help_text, curses.A_ITALIC)
            
            # Draw status bar
            if self.status_message and height > 3:
                if self.accessibility_mode:
                    stdscr.addstr(height - 3, 2, self.status_message)
                else:
                    stdscr.addstr(height - 3, 2, self.status_message, curses.color_pair(3))
            
            # Draw navigation hints
            if height > 2:
                nav_text = "↑/↓: Navigate  Tab: Next  Enter: Complete  Esc: Cancel"
                if len(nav_text) > width - 2:
                    nav_text = nav_text[:width - 5] + "..."
                stdscr.addstr(height - 2, 2, nav_text)
            
            # Refresh and handle input
            stdscr.refresh()
            key = stdscr.getch()
            
            # Navigation keys
            if key == curses.KEY_UP:
                self.prev_field()
            elif key == curses.KEY_DOWN or key == ord('\t'):
                self.next_field()
            # Enter to edit current field
            elif key == ord('\n'):
                if self.current_field_idx < len(self.fields):
                    field = self.fields[self.current_field_idx]['field']
                    # Edit the field value
                    # For simplicity, we'll clear the line and get input
                    edit_y = 2 + self.current_field_idx * a2 + 1
                    if edit_y < height - 3:
                        stdscr.move(edit_y, 4)
                        stdscr.clrtoeol()
                        curses.echo()
                        value = ""
                        # Get input, limiting to available width
                        max_input_width = width - 6
                        input_chars = []
                        
                        while True:
                            ch = stdscr.getch()
                            if ch == ord('\n'):
                                break
                            elif ch == 27:  # Escape
                                input_chars = []
                                break
                            elif ch == curses.KEY_BACKSPACE or ch == 127:
                                if input_chars:
                                    input_chars.pop()
                                    stdscr.addstr(edit_y, 4 + len(input_chars), ' ')
                                    stdscr.move(edit_y, 4 + len(input_chars))
                            elif len(input_chars) < max_input_width:
                                input_chars.append(chr(ch))
                                stdscr.addch(ch)
                        
                        value = ''.join(input_chars)
                        curses.noecho()
                        
                        # Validate and store if valid
                        if hasattr(field, 'input'):
                            valid, error = field.input(value)
                            if not valid and error:
                                self.set_status(error)
                            else:
                                values[self.fields[self.current_field_idx]['label']] = field.get_value()
                                self.set_status("")
                        elif hasattr(field, 'validate'):
                            try:
                                field.validate(value)
                                # Set internal value 
                                if hasattr(field, '_raw_value'):
                                    field._raw_value = value
                                values[self.fields[self.current_field_idx]['label']] = value
                                self.set_status("")
                            except ValueError as e:
                                self.set_status(str(e))
            # Escape to exit
            elif key == 27:
                break
        
        return values
    
    def _fallback_render(self):
        """
        Render line-by-line prompts as fallback when curses is unavailable.
        
        Returns:
            dict: Collected field values
        """
        values = {}
        
        print("\n--- Form ---\n")
        
        for i, field_data in enumerate(self.fields):
            field = field_data['field']
            label = field_data['label']
            
            # Show help text if available
            if i in self.help_text:
                print(f"  {self.help_text[i]}")
            
            # Show placeholder if available
            placeholder = getattr(field, 'placeholder', '')
            if placeholder:
                prompt = f"{label} [{placeholder}]: "
            else:
                prompt = f"{label}: "
            
            # Keep trying until valid input or empty input to skip
            while True:
                value = input(prompt)
                
                # Skip if empty and not required
                if not value:
                    break
                    
                # Validate input
                if hasattr(field, 'input'):
                    valid, error = field.input(value)
                    if valid:
                        values[label] = field.get_value()
                        break
                    else:
                        print(f"  Error: {error}")
                elif hasattr(field, 'validate'):
                    try:
                        field.validate(value)
                        if hasattr(field, '_raw_value'):
                            field._raw_value = value
                        values[label] = value
                        break
                    except ValueError as e:
                        print(f"  Error: {e}")
            
            print()
        
        return values