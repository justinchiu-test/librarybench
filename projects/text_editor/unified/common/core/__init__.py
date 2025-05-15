"""
Core functionality for text editors.

This module provides the fundamental building blocks for text editor implementations,
including text content management, positioning, history tracking, and file operations.
"""

from common.core.text_content import (
    TextContent,
    LineBasedTextContent,
    StructuredTextContent,
)
from common.core.position import Position, LineColumnPosition, StructuredPosition
from common.core.history import (
    History,
    Operation,
    InsertOperation,
    DeleteOperation,
    ReplaceOperation,
)
from common.core.file_manager import FileManager
