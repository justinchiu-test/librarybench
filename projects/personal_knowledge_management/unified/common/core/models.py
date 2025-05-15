"""Core data models for the unified personal knowledge management system."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class KnowledgeNode(BaseModel):
    """Base class for all knowledge nodes in the system."""

    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    tags: Set[str] = Field(default_factory=set)

    def update(self) -> None:
        """Update the last modified timestamp."""
        self.updated_at = datetime.now()


class RelationType(str, Enum):
    """Common relation types between knowledge nodes."""
    
    REFERENCES = "references"
    CITES = "cites"
    CONTAINS = "contains"
    RELATES_TO = "relates_to"
    PART_OF = "part_of"
    ANNOTATES = "annotates"
    DOCUMENTS = "documents"
    INVESTIGATES = "investigates"
    ADDRESSES = "addresses"
    AUTHORED_BY = "authored_by"
    CREATED_BY = "created_by"
    MODIFIED_BY = "modified_by"


class Relation(BaseModel):
    """Represents a relation between two knowledge nodes."""
    
    source_id: UUID
    target_id: UUID
    relation_type: Union[RelationType, str]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)


class Priority(str, Enum):
    """Priority levels for items."""
    
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Status(str, Enum):
    """Common status options for items."""
    
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    DELETED = "deleted"


class Annotation(KnowledgeNode):
    """Represents an annotation or comment on a knowledge node."""

    node_id: UUID  # Reference to the annotated knowledge node
    content: str
    position: Optional[str] = None  # For annotations with specific position in document
    author_id: Optional[UUID] = None  # Who made the annotation
    status: str = "open"  # Status of the annotation (open, addressed, rejected)
    replies: List[UUID] = Field(default_factory=list)  # References to reply annotations
    parent_id: Optional[UUID] = None  # Reference to parent annotation if this is a reply
    resolved_by: Optional[UUID] = None  # Reference to person who resolved this


class NodeType(str, Enum):
    """Types of knowledge nodes in the system."""
    
    NOTE = "note"
    DOCUMENT = "document"
    CITATION = "citation"
    QUESTION = "question"
    EXPERIMENT = "experiment"
    PROJECT = "project"
    PERSON = "person"
    ANNOTATION = "annotation"
    TAG = "tag"
    OTHER = "other"