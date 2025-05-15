"""Focus mode system for the writer text editor.

This implementation uses the common library's StructuredPosition where appropriate.
"""

from __future__ import annotations
import time
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union, Any
from pydantic import BaseModel, Field

from common.core.position import StructuredPosition, StructuredElementType
from writer_text_editor.document import Document, Section, TextSegment


class FocusLevel(str, Enum):
    """The level of focus."""

    PARAGRAPH = "paragraph"
    SENTENCE = "sentence"
    SECTION = "section"


class FocusContext(BaseModel):
    """Context information about the focused element."""

    document: Document
    section: Section
    segment: TextSegment
    level: FocusLevel
    start_time: float = Field(default_factory=time.time)
    position: Optional[StructuredPosition] = None

    class Config:
        arbitrary_types_allowed = True
        
    def __init__(self, **data):
        super().__init__(**data)
        # Create structured position if not provided
        if not self.position and self.section and self.segment:
            self.position = StructuredPosition(
                view_id="focus",
                element_id=self.segment.id,
                element_type=StructuredElementType.SEGMENT,
                section_index=self.document.current_revision.sections.index(self.section),
                segment_index=self.section.segments.index(self.segment),
                offset_in_segment=0
            )


class FocusMode:
    """The focus mode system."""

    def __init__(self, document: Document):
        """Initialize the focus mode system with the given document."""
        self.document = document
        self.active_focus: Optional[FocusContext] = None
        self.focus_history: List[FocusContext] = []

    def is_active(self) -> bool:
        """Check if focus mode is currently active."""
        return self.active_focus is not None

    def get_focus_context(self) -> Optional[FocusContext]:
        """Get the current focus context if focus mode is active."""
        return self.active_focus

    def enter_focus(
        self,
        section_index: int,
        segment_index: int,
        level: FocusLevel = FocusLevel.PARAGRAPH,
    ) -> Optional[FocusContext]:
        """Enter focus mode for the specified section and segment."""
        section = self.document.get_section(section_index)
        if not section:
            return None

        segment = section.get_segment(segment_index)
        if not segment:
            return None

        # Create position object
        position = StructuredPosition(
            view_id="focus",
            element_id=segment.id,
            element_type=StructuredElementType.SEGMENT,
            section_index=section_index,
            segment_index=segment_index,
            offset_in_segment=0
        )
        
        self.active_focus = FocusContext(
            document=self.document, 
            section=section, 
            segment=segment, 
            level=level,
            position=position
        )
        self.focus_history.append(self.active_focus)
        return self.active_focus

    def exit_focus(self) -> bool:
        """Exit focus mode."""
        if self.active_focus:
            self.active_focus = None
            return True
        return False

    def move_focus(self, direction: int = 1) -> Optional[FocusContext]:
        """Move the focus to the next or previous segment."""
        if not self.active_focus:
            return None

        current_segment = self.active_focus.segment
        current_section = self.active_focus.section
        current_position = self.active_focus.position
        
        if not current_position:
            return None

        # Find the next segment within the current section
        next_segment_index = current_position.segment_index + direction
        next_segment = current_section.get_segment(next_segment_index)

        if next_segment:
            # Move focus within the same section
            new_position = StructuredPosition(
                view_id=current_position.view_id,
                element_id=next_segment.id,
                element_type=StructuredElementType.SEGMENT,
                section_index=current_position.section_index,
                segment_index=next_segment_index,
                offset_in_segment=0
            )
            
            self.active_focus = FocusContext(
                document=self.document,
                section=current_section,
                segment=next_segment,
                level=self.active_focus.level,
                position=new_position
            )
            self.focus_history.append(self.active_focus)
            return self.active_focus

        # Try to move to a different section
        current_section_idx = current_position.section_index
        next_section_idx = current_section_idx + direction

        if 0 <= next_section_idx < len(self.document.current_revision.sections):
            next_section = self.document.current_revision.sections[next_section_idx]

            # Get the first or last segment of the next section depending on direction
            target_segment_index = 0 if direction > 0 else len(next_section.segments) - 1
            if 0 <= target_segment_index < len(next_section.segments):
                next_segment = next_section.segments[target_segment_index]
                
                new_position = StructuredPosition(
                    view_id=current_position.view_id,
                    element_id=next_segment.id,
                    element_type=StructuredElementType.SEGMENT,
                    section_index=next_section_idx,
                    segment_index=target_segment_index,
                    offset_in_segment=0
                )

                self.active_focus = FocusContext(
                    document=self.document,
                    section=next_section,
                    segment=next_segment,
                    level=self.active_focus.level,
                    position=new_position
                )
                self.focus_history.append(self.active_focus)
                return self.active_focus

        return None

    def change_focus_level(self, level: FocusLevel) -> Optional[FocusContext]:
        """Change the level of focus."""
        if not self.active_focus:
            return None

        self.active_focus.level = level
        self.focus_history.append(self.active_focus)
        return self.active_focus

    def edit_focused_content(self, new_content: str) -> Optional[TextSegment]:
        """Edit the content of the focused segment."""
        if not self.active_focus:
            return None

        self.active_focus.segment.content = new_content
        self.document.updated_at = time.time()
        return self.active_focus.segment

    def get_focus_time(self) -> float:
        """Get the time spent in the current focus session in seconds."""
        if not self.active_focus:
            return 0.0

        return time.time() - self.active_focus.start_time

    def get_surrounding_context(self, context_size: int = 2) -> List[TextSegment]:
        """Get the surrounding segments around the focused segment."""
        if not self.active_focus or not self.active_focus.position:
            return []

        section = self.active_focus.section
        position = self.active_focus.position.segment_index

        start = max(0, position - context_size)
        end = min(len(section.segments), position + context_size + 1)

        return section.segments[start:end]
