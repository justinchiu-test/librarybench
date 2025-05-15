"""Document model for the writer text editor.

This implementation uses the common library's StructuredTextContent.
"""

from __future__ import annotations
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set, Any
import re
import uuid
from pydantic import BaseModel, Field

from common.core.text_content import TextSegment as CommonTextSegment
from common.core.text_content import Section as CommonSection
from common.core.text_content import Revision as CommonRevision
from common.core.text_content import StructuredTextContent


class TextSegment(CommonTextSegment):
    """A segment of text, such as a paragraph or sentence."""

    # Inherits id, content, position, metadata from CommonTextSegment

    def get_word_count(self) -> int:
        """Get the number of words in this segment."""
        return super().get_word_count()


class Section(CommonSection):
    """A section of a document, such as a chapter or scene."""

    # Inherits id, title, segments, metadata from CommonSection

    def get_content(self) -> str:
        """Get the full content of this section."""
        return super().get_content()

    def get_word_count(self) -> int:
        """Get the number of words in this section."""
        return super().get_word_count()

    def add_segment(
        self, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> TextSegment:
        """Add a new segment to this section."""
        # Convert from CommonTextSegment to our TextSegment subclass
        common_segment = super().add_segment(content, metadata)

        # Create our TextSegment with the same properties
        segment = TextSegment(
            id=common_segment.id,
            content=common_segment.content,
            position=common_segment.position,
            metadata=common_segment.metadata,
        )

        # Replace the segment in the list with our version
        index = len(self.segments) - 1
        self.segments[index] = segment

        return segment

    def get_segment(self, position: int) -> Optional[TextSegment]:
        """Get the segment at the specified position."""
        return super().get_segment(position)

    def update_segment(self, position: int, content: str) -> Optional[TextSegment]:
        """Update the content of the segment at the specified position."""
        return super().update_segment(position, content)

    def delete_segment(self, position: int) -> bool:
        """Delete the segment at the specified position."""
        return super().delete_segment(position)


class Revision(CommonRevision):
    """A revision of a document."""

    # Inherits id, name, timestamp, sections, metadata from CommonRevision


class Document(StructuredTextContent):
    """A document in the writer text editor."""

    # Directly add the id attribute to ensure compatibility
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    def __init__(self, title: str, **data: Any):
        """Initialize a new document with the given title."""
        super().__init__(title=title, **data)

    def get_word_count(self) -> int:
        """Get the total number of words in the document."""
        return super().get_word_count()

    def add_section(
        self, title: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Section:
        """Add a new section to the document."""
        # Convert from CommonSection to our Section subclass
        common_section = super().add_section(title, metadata)

        # Create our Section with the same properties
        section = Section(
            id=common_section.id,
            title=common_section.title,
            segments=[],  # We'll add segments separately if needed
            metadata=common_section.metadata,
        )

        # Replace the section in the list with our version
        index = len(self.current_revision.sections) - 1
        self.current_revision.sections[index] = section

        return section

    def get_section(self, index: int) -> Optional[Section]:
        """Get the section at the specified index."""
        if 0 <= index < len(self.current_revision.sections):
            return self.current_revision.sections[index]
        return None

    def get_section_by_title(self, title: str) -> Optional[Section]:
        """Get the first section with the specified title."""
        for section in self.current_revision.sections:
            if section.title == title:
                return section
        return None

    def update_section_title(self, index: int, title: str) -> Optional[Section]:
        """Update the title of the section at the specified index."""
        section = self.get_section(index)
        if section:
            section.title = title
            self.updated_at = datetime.now()
            return section
        return None

    def delete_section(self, index: int) -> bool:
        """Delete the section at the specified index."""
        if 0 <= index < len(self.current_revision.sections):
            self.current_revision.sections.pop(index)
            self.updated_at = datetime.now()
            return True
        return False

    def create_revision(
        self, name: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Revision:
        """Create a new revision of the document."""
        # Convert from CommonRevision to our Revision subclass
        common_revision = super().create_revision(name, metadata)

        # Create our Revision with the same properties
        revision = Revision(
            id=common_revision.id,
            name=common_revision.name,
            timestamp=common_revision.timestamp,
            sections=common_revision.sections.copy(),
            metadata=common_revision.metadata.copy(),
        )

        # Replace the revision in the dict with our version
        self.revisions[name] = revision
        self.current_revision = revision

        return revision

    def get_revision(self, name: str) -> Optional[Revision]:
        """Get a revision by name."""
        return self.revisions.get(name)

    def switch_to_revision(self, name: str) -> bool:
        """Switch to a different revision."""
        revision = self.get_revision(name)
        if revision:
            self.current_revision = revision
            self.updated_at = datetime.now()
            return True
        return False

    def get_content(self) -> str:
        """Get the full content of the document."""
        return super().get_text()

    def find_segments_by_content(
        self, pattern: str
    ) -> List[Tuple[Section, TextSegment]]:
        """Find segments that match the given pattern."""
        results = []
        for section in self.current_revision.sections:
            for segment in section.segments:
                if re.search(pattern, segment.content, re.IGNORECASE):
                    results.append((section, segment))
        return results
