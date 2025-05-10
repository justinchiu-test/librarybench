"""
Base models for the Academic Knowledge Vault system.

This module defines the core data models used throughout the application.
"""

import datetime
import enum
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Set, Union

from pydantic import BaseModel, Field, validator


class KnowledgeItemType(str, enum.Enum):
    """Types of knowledge items in the system."""

    NOTE = "note"
    CITATION = "citation"
    RESEARCH_QUESTION = "research_question"
    HYPOTHESIS = "hypothesis"
    EVIDENCE = "evidence"
    EXPERIMENT = "experiment"
    GRANT_PROPOSAL = "grant_proposal"
    ANNOTATION = "annotation"


class BaseKnowledgeItem(BaseModel):
    """Base model for all knowledge items in the system."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    title: str
    tags: Set[str] = Field(default_factory=set)

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to the current time."""
        self.updated_at = datetime.datetime.now()


class StorageInfo(BaseModel):
    """Information about where a knowledge item is stored."""

    path: Path
    format: str
    last_sync: Optional[datetime.datetime] = None
    checksum: Optional[str] = None


class Reference(BaseModel):
    """A reference to another knowledge item."""

    item_id: str
    item_type: KnowledgeItemType
    context: Optional[str] = None


class LinkedItem(BaseModel):
    """A link to another knowledge item with bidirectional relationship info."""

    source_id: str
    target_id: str
    source_type: KnowledgeItemType
    target_type: KnowledgeItemType
    relationship_type: str
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    context: Optional[str] = None
    strength: float = 1.0  # Relationship strength score


class Person(BaseModel):
    """A person, such as a collaborator or author."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: Optional[str] = None
    affiliation: Optional[str] = None
    role: Optional[str] = None