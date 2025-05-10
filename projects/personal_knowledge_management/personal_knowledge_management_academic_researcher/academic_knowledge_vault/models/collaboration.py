"""
Collaboration models for the Academic Knowledge Vault system.

This module defines the data models for collaborative annotations and shared knowledge.
"""

import datetime
import enum
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


class AnnotationType(str, enum.Enum):
    """Types of annotations made by collaborators."""

    COMMENT = "comment"
    SUGGESTION = "suggestion"
    QUESTION = "question"
    CRITIQUE = "critique"
    PRAISE = "praise"
    REFERENCE = "reference"
    CORRECTION = "correction"


class AnnotationStatus(str, enum.Enum):
    """Status categories for annotations."""

    NEW = "new"
    REVIEWED = "reviewed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    INTEGRATED = "integrated"
    HIDDEN = "hidden"


class Annotation(BaseKnowledgeItem):
    """An annotation made by a collaborator on a knowledge item."""

    # Basic annotation information
    annotation_type: AnnotationType = AnnotationType.COMMENT
    content: str
    status: AnnotationStatus = AnnotationStatus.NEW
    
    # Source information
    author: Person
    target_item_id: str
    target_item_type: KnowledgeItemType
    target_context: Optional[str] = None  # Specific part of the item being annotated
    
    # Related knowledge items
    references: List[Reference] = Field(default_factory=list)
    
    # Integration tracking
    integrated_into_id: Optional[str] = None  # ID of item that integrated this annotation
    integration_date: Optional[datetime.datetime] = None
    integration_notes: Optional[str] = None
    
    # Response tracking
    responses: List[Reference] = Field(default_factory=list)  # References to other annotations
    
    def update_status(self, status: AnnotationStatus) -> None:
        """Update the status of the annotation."""
        self.status = status
        self.update_timestamp()
    
    def mark_as_integrated(self, item_id: str, notes: Optional[str] = None) -> None:
        """Mark the annotation as integrated into a knowledge item."""
        self.status = AnnotationStatus.INTEGRATED
        self.integrated_into_id = item_id
        self.integration_date = datetime.datetime.now()
        if notes:
            self.integration_notes = notes
        self.update_timestamp()
    
    def add_response(self, annotation_ref: Reference) -> None:
        """Add a response to this annotation."""
        for existing_ref in self.responses:
            if existing_ref.item_id == annotation_ref.item_id:
                return  # Reference already exists
        self.responses.append(annotation_ref)
        self.update_timestamp()


class CollaborationPermission(str, enum.Enum):
    """Permission levels for collaborators."""

    VIEW = "view"
    COMMENT = "comment"
    EDIT = "edit"
    ADMIN = "admin"


class Collaborator(BaseModel):
    """A collaborator with specific permissions."""

    person: Person
    permissions: CollaborationPermission = CollaborationPermission.VIEW
    joined_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    last_active: Optional[datetime.datetime] = None
    notes: Optional[str] = None


class CollaborationSession(BaseModel):
    """A session for collaborative work on knowledge items."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    
    # Collaborators and permissions
    owner: Person
    collaborators: List[Collaborator] = Field(default_factory=list)
    
    # Shared knowledge items
    shared_items: Dict[str, KnowledgeItemType] = Field(default_factory=dict)
    
    # Annotations
    annotations: List[str] = Field(default_factory=list)  # IDs of annotations
    
    # Session metadata
    tags: Set[str] = Field(default_factory=set)
    start_date: Optional[datetime.datetime] = None
    end_date: Optional[datetime.datetime] = None
    status: str = "active"
    
    def add_collaborator(self, collaborator: Collaborator) -> None:
        """Add a collaborator to the session."""
        for existing_collab in self.collaborators:
            if existing_collab.person.id == collaborator.person.id:
                # Update existing collaborator
                existing_collab.permissions = collaborator.permissions
                existing_collab.notes = collaborator.notes
                return
        self.collaborators.append(collaborator)
        self.updated_at = datetime.datetime.now()
    
    def add_shared_item(self, item_id: str, item_type: KnowledgeItemType) -> None:
        """Add a shared item to the session."""
        self.shared_items[item_id] = item_type
        self.updated_at = datetime.datetime.now()
    
    def remove_shared_item(self, item_id: str) -> None:
        """Remove a shared item from the session."""
        if item_id in self.shared_items:
            del self.shared_items[item_id]
            self.updated_at = datetime.datetime.now()
    
    def add_annotation(self, annotation_id: str) -> None:
        """Add an annotation to the session."""
        if annotation_id not in self.annotations:
            self.annotations.append(annotation_id)
            self.updated_at = datetime.datetime.now()


class ImportedAnnotation(BaseModel):
    """An annotation imported from a collaborator's system."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_annotation_id: str
    source_system: Optional[str] = None
    imported_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    
    # The imported annotation data
    annotation: Annotation
    
    # Import metadata
    import_notes: Optional[str] = None
    importer_id: str  # ID of the person who imported the annotation
    
    # Integration status
    integration_status: str = "pending"  # pending, integrated, rejected
    local_item_id: Optional[str] = None  # ID of the local item this was applied to
    
    def mark_as_integrated(self, local_item_id: str) -> None:
        """Mark the imported annotation as integrated."""
        self.integration_status = "integrated"
        self.local_item_id = local_item_id
    
    def reject(self) -> None:
        """Mark the imported annotation as rejected."""
        self.integration_status = "rejected"


import uuid