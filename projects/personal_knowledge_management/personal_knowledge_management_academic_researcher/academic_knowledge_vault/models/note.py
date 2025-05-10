"""
Note models for the Academic Knowledge Vault system.

This module defines the data models for research notes and related items.
"""

import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Union

from pydantic import BaseModel, Field, validator

from academic_knowledge_vault.models.base import (
    BaseKnowledgeItem,
    KnowledgeItemType,
    LinkedItem,
    Reference,
    StorageInfo,
)


class NoteType(str, Enum):
    """Types of notes in the system."""

    LITERATURE = "literature"
    CONCEPT = "concept"
    MEETING = "meeting"
    EXPERIMENT = "experiment"
    DRAFT = "draft"
    LECTURE = "lecture"
    IDEA = "idea"
    REVIEW = "review"
    OTHER = "other"


class NoteContent(BaseModel):
    """Content of a note, with support for versioning."""

    content: str
    format: str = "markdown"
    version: int = 1
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    word_count: Optional[int] = None

    @validator("word_count", always=True)
    def compute_word_count(cls, v: Optional[int], values: Dict) -> int:
        """Compute word count if not provided."""
        if v is not None:
            return v
        if "content" in values:
            return len(values["content"].split())
        return 0


class Note(BaseKnowledgeItem):
    """A research note in the knowledge management system."""

    type: NoteType = NoteType.CONCEPT
    content: NoteContent
    parent_id: Optional[str] = None
    summary: Optional[str] = None
    references: List[Reference] = Field(default_factory=list)
    linked_items: List[LinkedItem] = Field(default_factory=list)
    storage: Optional[StorageInfo] = None
    
    # Citation-related metadata
    citation_keys: Set[str] = Field(default_factory=set)
    doi_references: Set[str] = Field(default_factory=set)
    
    # Version history
    version_history: List[NoteContent] = Field(default_factory=list)
    current_version: int = 1
    
    # Organizational metadata
    project: Optional[str] = None
    path: List[str] = Field(default_factory=list)
    priority: Optional[int] = None
    status: Optional[str] = None

    def add_reference(self, reference: Reference) -> None:
        """Add a reference to the note."""
        for existing_ref in self.references:
            if existing_ref.item_id == reference.item_id:
                return  # Reference already exists
        self.references.append(reference)
        self.update_timestamp()

    def remove_reference(self, reference_id: str) -> None:
        """Remove a reference from the note."""
        self.references = [ref for ref in self.references if ref.item_id != reference_id]
        self.update_timestamp()

    def add_linked_item(self, linked_item: LinkedItem) -> None:
        """Add a linked item to the note."""
        for existing_link in self.linked_items:
            if (
                existing_link.source_id == linked_item.source_id
                and existing_link.target_id == linked_item.target_id
            ):
                return  # Link already exists
        self.linked_items.append(linked_item)
        self.update_timestamp()

    def remove_linked_item(self, target_id: str) -> None:
        """Remove a linked item from the note."""
        self.linked_items = [
            link for link in self.linked_items if link.target_id != target_id
        ]
        self.update_timestamp()

    def update_content(self, new_content: str, format: str = "markdown") -> None:
        """Update the note content, preserving version history."""
        # Add current content to version history
        if self.content is not None:
            self.version_history.append(self.content)
        
        # Create new content
        self.content = NoteContent(
            content=new_content, 
            format=format,
            version=self.current_version + 1,
            created_at=datetime.datetime.now()
        )
        self.current_version += 1
        self.update_timestamp()
    
    def get_version(self, version: int) -> Optional[NoteContent]:
        """Get a specific version of the note content."""
        if version == self.current_version:
            return self.content
        
        for past_version in self.version_history:
            if past_version.version == version:
                return past_version
        
        return None


class NoteCollection(BaseModel):
    """A collection of related notes."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    note_ids: Set[str] = Field(default_factory=set)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    tags: Set[str] = Field(default_factory=set)
    
    def add_note(self, note_id: str) -> None:
        """Add a note to the collection."""
        self.note_ids.add(note_id)
        self.updated_at = datetime.datetime.now()
    
    def remove_note(self, note_id: str) -> None:
        """Remove a note from the collection."""
        if note_id in self.note_ids:
            self.note_ids.remove(note_id)
            self.updated_at = datetime.datetime.now()


import uuid