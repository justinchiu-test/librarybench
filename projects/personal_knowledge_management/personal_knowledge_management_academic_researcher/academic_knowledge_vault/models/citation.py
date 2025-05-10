"""
Citation models for the Academic Knowledge Vault system.

This module defines the data models for academic citations and references.
"""

import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Union

from pydantic import BaseModel, Field, validator

from academic_knowledge_vault.models.base import (
    BaseKnowledgeItem,
    KnowledgeItemType,
    LinkedItem,
    Person,
    Reference,
    StorageInfo,
)


class PublicationType(str, Enum):
    """Types of academic publications."""

    JOURNAL_ARTICLE = "journal_article"
    CONFERENCE_PAPER = "conference_paper"
    BOOK = "book"
    BOOK_CHAPTER = "book_chapter"
    THESIS = "thesis"
    PREPRINT = "preprint"
    TECHNICAL_REPORT = "technical_report"
    WEBSITE = "website"
    OTHER = "other"


class Citation(BaseKnowledgeItem):
    """A citation to an academic publication."""

    type: PublicationType = PublicationType.JOURNAL_ARTICLE
    authors: List[Person] = Field(default_factory=list)
    publication_year: Optional[int] = None
    journal_or_conference: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    abstract: Optional[str] = None
    citation_key: Optional[str] = None
    bibtex: Optional[str] = None
    pdf_path: Optional[str] = None
    notes: str = ""
    
    # Academic impact metrics
    citation_count: Optional[int] = None
    impact_factor: Optional[float] = None
    
    # Relationships to other papers
    references: List[Reference] = Field(default_factory=list)
    cited_by: List[Reference] = Field(default_factory=list)
    
    # Related knowledge items
    related_notes: List[Reference] = Field(default_factory=list)
    related_questions: List[Reference] = Field(default_factory=list)
    
    # Storage information
    storage: Optional[StorageInfo] = None
    
    def add_author(self, author: Person) -> None:
        """Add an author to the citation."""
        for existing_author in self.authors:
            if existing_author.id == author.id:
                return  # Author already exists
        self.authors.append(author)
        self.update_timestamp()
    
    def remove_author(self, author_id: str) -> None:
        """Remove an author from the citation."""
        self.authors = [author for author in self.authors if author.id != author_id]
        self.update_timestamp()
    
    def add_reference(self, reference: Reference) -> None:
        """Add a reference to another citation."""
        for existing_ref in self.references:
            if existing_ref.item_id == reference.item_id:
                return  # Reference already exists
        self.references.append(reference)
        self.update_timestamp()
    
    def add_citing_paper(self, reference: Reference) -> None:
        """Add a paper that cites this citation."""
        for existing_ref in self.cited_by:
            if existing_ref.item_id == reference.item_id:
                return  # Reference already exists
        self.cited_by.append(reference)
        self.update_timestamp()
    
    def add_related_note(self, note_reference: Reference) -> None:
        """Add a related note to the citation."""
        for existing_ref in self.related_notes:
            if existing_ref.item_id == note_reference.item_id:
                return  # Reference already exists
        self.related_notes.append(note_reference)
        self.update_timestamp()


class CitationCollection(BaseModel):
    """A collection of related citations."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    citation_ids: Set[str] = Field(default_factory=set)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    tags: Set[str] = Field(default_factory=set)
    
    def add_citation(self, citation_id: str) -> None:
        """Add a citation to the collection."""
        self.citation_ids.add(citation_id)
        self.updated_at = datetime.datetime.now()
    
    def remove_citation(self, citation_id: str) -> None:
        """Remove a citation from the collection."""
        if citation_id in self.citation_ids:
            self.citation_ids.remove(citation_id)
            self.updated_at = datetime.datetime.now()


import uuid