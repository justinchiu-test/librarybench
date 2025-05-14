"""Document model for the writer text editor."""

from __future__ import annotations
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set, Any
import re
import uuid
from pydantic import BaseModel, Field


class TextSegment(BaseModel):
    """A segment of text, such as a paragraph or sentence."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    position: int
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def get_word_count(self) -> int:
        """Get the number of words in this segment."""
        return len(re.findall(r'\b\w+\b', self.content))


class Section(BaseModel):
    """A section of a document, such as a chapter or scene."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    segments: List[TextSegment] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def get_content(self) -> str:
        """Get the full content of this section."""
        return "\n".join([segment.content for segment in self.segments])
    
    def get_word_count(self) -> int:
        """Get the number of words in this section."""
        return sum(segment.get_word_count() for segment in self.segments)
    
    def add_segment(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> TextSegment:
        """Add a new segment to this section."""
        position = len(self.segments)
        segment = TextSegment(
            content=content,
            position=position,
            metadata=metadata or {}
        )
        self.segments.append(segment)
        return segment
    
    def get_segment(self, position: int) -> Optional[TextSegment]:
        """Get the segment at the specified position."""
        if 0 <= position < len(self.segments):
            return self.segments[position]
        return None
    
    def update_segment(self, position: int, content: str) -> Optional[TextSegment]:
        """Update the content of the segment at the specified position."""
        segment = self.get_segment(position)
        if segment:
            segment.content = content
            return segment
        return None
    
    def delete_segment(self, position: int) -> bool:
        """Delete the segment at the specified position."""
        if 0 <= position < len(self.segments):
            self.segments.pop(position)
            # Update positions of all segments after the deleted one
            for i in range(position, len(self.segments)):
                self.segments[i].position = i
            return True
        return False


class Revision(BaseModel):
    """A revision of a document."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    timestamp: datetime = Field(default_factory=datetime.now)
    sections: List[Section] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Document(BaseModel):
    """A document in the writer text editor."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    current_revision: Revision
    revisions: Dict[str, Revision] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, title: str, **data: Any):
        """Initialize a new document with the given title."""
        initial_revision = Revision(name="Initial")
        super().__init__(
            title=title,
            current_revision=initial_revision,
            **data
        )
        self.revisions["Initial"] = initial_revision
    
    def get_word_count(self) -> int:
        """Get the total number of words in the document."""
        return sum(section.get_word_count() for section in self.current_revision.sections)
    
    def add_section(self, title: str, metadata: Optional[Dict[str, Any]] = None) -> Section:
        """Add a new section to the document."""
        section = Section(title=title, metadata=metadata or {})
        self.current_revision.sections.append(section)
        self.updated_at = datetime.now()
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
    
    def create_revision(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> Revision:
        """Create a new revision of the document."""
        # Deep copy the current revision
        import copy
        new_revision = copy.deepcopy(self.current_revision)
        new_revision.id = str(uuid.uuid4())
        new_revision.name = name
        new_revision.timestamp = datetime.now()
        new_revision.metadata = metadata or {}
        
        self.revisions[name] = new_revision
        self.current_revision = new_revision
        self.updated_at = datetime.now()
        
        return new_revision
    
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
        return "\n\n".join([
            f"# {section.title}\n\n{section.get_content()}"
            for section in self.current_revision.sections
        ])
    
    def find_segments_by_content(self, pattern: str) -> List[Tuple[Section, TextSegment]]:
        """Find segments that match the given pattern."""
        results = []
        for section in self.current_revision.sections:
            for segment in section.segments:
                if re.search(pattern, segment.content, re.IGNORECASE):
                    results.append((section, segment))
        return results