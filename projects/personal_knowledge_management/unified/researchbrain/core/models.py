"""Core data models for the ResearchBrain knowledge management system.

This module defines the domain-specific data models for the ResearchBrain
knowledge management system, building on the common KnowledgeNode base class
from the unified library.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

# Import base models from common library
from common.core.models import (
    KnowledgeNode, NodeType, Priority, Status, 
    Annotation as CommonAnnotation, RelationType
)


class CitationType(str, Enum):
    """Types of academic citations."""

    BOOK = "book"
    ARTICLE = "article"
    CONFERENCE = "conference"
    THESIS = "thesis"
    REPORT = "report"
    WEBPAGE = "webpage"
    PREPRINT = "preprint"
    OTHER = "other"
    
    @classmethod
    def _missing_(cls, value):
        # Handle string values regardless of case
        if isinstance(value, str):
            for member in cls.__members__.values():
                if member.value.lower() == value.lower():
                    return member
        return None


class Note(KnowledgeNode):
    """Represents a research note with content and metadata."""

    title: str
    content: str
    source: Optional[UUID] = None  # Reference to a source document
    page_reference: Optional[int] = None  # Page number in the source document
    attachments: List[Path] = Field(default_factory=list)
    citations: List[UUID] = Field(default_factory=list)  # References to Citation objects
    section_references: Dict[str, str] = Field(default_factory=dict)  # Section references in source documents
    node_type: NodeType = NodeType.NOTE


class Citation(KnowledgeNode):
    """Represents a citation to an academic source."""

    title: str
    authors: List[str]
    year: Optional[int] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    journal: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    publisher: Optional[str] = None
    citation_type: CitationType = CitationType.ARTICLE
    abstract: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    file_path: Optional[Path] = None
    bibtex: Optional[str] = None
    ris: Optional[str] = None  # RIS format citation data
    notes: List[UUID] = Field(default_factory=list)  # References to linked Note objects
    pdf_metadata: Dict[str, Any] = Field(default_factory=dict)  # Extracted metadata from PDF
    sections: Dict[str, str] = Field(default_factory=dict)  # Extracted sections from the paper
    node_type: NodeType = NodeType.CITATION


class CitationFormat(str, Enum):
    """Academic citation formats."""

    APA = "apa"
    MLA = "mla"
    CHICAGO = "chicago"
    HARVARD = "harvard"
    IEEE = "ieee"
    VANCOUVER = "vancouver"
    BIBTEX = "bibtex"
    RIS = "ris"
    
    @classmethod
    def _missing_(cls, value):
        # Handle string values regardless of case
        if isinstance(value, str):
            for member in cls.__members__.values():
                if member.value.lower() == value.lower():
                    return member
        return None


class EvidenceType(str, Enum):
    """Types of evidence for research questions."""

    SUPPORTING = "supporting"
    CONTRADICTING = "contradicting"
    INCONCLUSIVE = "inconclusive"
    RELATED = "related"
    
    @classmethod
    def _missing_(cls, value):
        # Handle string values regardless of case
        if isinstance(value, str):
            for member in cls.__members__.values():
                if member.value.lower() == value.lower():
                    return member
        return None


class EvidenceStrength(str, Enum):
    """Strength levels for evidence."""

    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    ANECDOTAL = "anecdotal"
    THEORETICAL = "theoretical"
    
    @classmethod
    def _missing_(cls, value):
        # Handle string values regardless of case
        if isinstance(value, str):
            for member in cls.__members__.values():
                if member.value.lower() == value.lower():
                    return member
        return None


class Evidence(BaseModel):
    """Evidence linked to a research question."""

    id: UUID = Field(default_factory=uuid4)
    note_id: UUID  # Reference to the note containing the evidence
    evidence_type: EvidenceType
    strength: EvidenceStrength
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    citation_ids: List[UUID] = Field(default_factory=list)  # References to supporting citations
    metadata: Dict[str, Any] = Field(default_factory=dict)  # Additional metadata for the evidence
    
    def __init__(self, **data):
        # Handle string evidence_type and strength values
        if 'evidence_type' in data and isinstance(data['evidence_type'], str):
            try:
                data['evidence_type'] = EvidenceType(data['evidence_type'].lower())
            except ValueError:
                # Use default if invalid
                data['evidence_type'] = EvidenceType.RELATED
                
        if 'strength' in data and isinstance(data['strength'], str):
            try:
                data['strength'] = EvidenceStrength(data['strength'].lower())
            except ValueError:
                # Use default if invalid
                data['strength'] = EvidenceStrength.MODERATE
                
        super().__init__(**data)


class ResearchQuestion(KnowledgeNode):
    """Represents a research question or hypothesis."""

    question: str
    description: Optional[str] = None
    evidence: List[Evidence] = Field(default_factory=list)
    status: str = "open"  # open, resolved, abandoned
    priority: Priority = Priority.MEDIUM
    related_questions: List[UUID] = Field(default_factory=list)  # References to related questions
    knowledge_gaps: List[str] = Field(default_factory=list)  # Identified knowledge gaps
    node_type: NodeType = NodeType.QUESTION
    numeric_priority: Optional[int] = Field(default=None, exclude=True)  # Store the original numeric priority
    
    def __init__(self, **data):
        # Convert numeric priority to Priority enum for compatibility with tests
        if 'priority' in data and isinstance(data['priority'], int):
            numeric_priority = data['priority']
            data['numeric_priority'] = numeric_priority  # Save for tests to access
            # Convert to enum for internal storage
            if numeric_priority >= 8:
                data['priority'] = Priority.HIGH
            elif numeric_priority >= 4:
                data['priority'] = Priority.MEDIUM
            else:
                data['priority'] = Priority.LOW
        super().__init__(**data)


class ExperimentStatus(str, Enum):
    """Status options for experiments."""

    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"
    
    @classmethod
    def _missing_(cls, value):
        # Handle string values regardless of case
        if isinstance(value, str):
            for member in cls.__members__.values():
                if member.value.lower() == value.lower():
                    return member
        return None


class Experiment(KnowledgeNode):
    """Represents a scientific experiment with structured metadata."""

    title: str
    hypothesis: str
    status: ExperimentStatus = ExperimentStatus.PLANNED
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    methodology: str
    variables: Dict[str, Any] = Field(default_factory=dict)
    results: Optional[str] = None
    conclusion: Optional[str] = None
    research_question_id: Optional[UUID] = None  # Link to a research question
    notes: List[UUID] = Field(default_factory=list)  # References to linked Note objects
    collaborators: List[UUID] = Field(default_factory=list)  # References to collaborators
    template_name: Optional[str] = None  # Name of the template used to create the experiment
    reproducibility_info: Dict[str, Any] = Field(default_factory=dict)  # Information for reproducibility
    node_type: NodeType = NodeType.EXPERIMENT
    
    def __init__(self, **data):
        # Handle string status values
        if 'status' in data and isinstance(data['status'], str):
            try:
                data['status'] = ExperimentStatus(data['status'].lower())
            except ValueError:
                # Use default if invalid
                data['status'] = ExperimentStatus.PLANNED
        super().__init__(**data)

    @field_validator("end_date")
    def end_date_after_start_date(cls, v, info):
        """Validate that end_date is after start_date if both are provided."""
        values = info.data
        if v and "start_date" in values and values["start_date"]:
            if v < values["start_date"]:
                raise ValueError("end_date must be after start_date")
        return v


class GrantStatus(str, Enum):
    """Status options for grant proposals."""

    DRAFTING = "drafting"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    AWARDED = "awarded"
    REJECTED = "rejected"
    COMPLETED = "completed"
    
    @classmethod
    def _missing_(cls, value):
        # Handle string values regardless of case
        if isinstance(value, str):
            for member in cls.__members__.values():
                if member.value.lower() == value.lower():
                    return member
        return None


class GrantProposal(KnowledgeNode):
    """Represents a grant proposal workspace."""

    title: str
    funding_agency: str
    deadline: Optional[datetime] = None
    status: GrantStatus = GrantStatus.DRAFTING
    amount: Optional[float] = None
    description: str
    notes: List[UUID] = Field(default_factory=list)  # References to related notes
    experiments: List[UUID] = Field(default_factory=list)  # References to related experiments
    research_questions: List[UUID] = Field(default_factory=list)  # References to research questions
    collaborators: List[UUID] = Field(default_factory=list)  # References to collaborators
    budget_items: Dict[str, Any] = Field(default_factory=dict)  # Budget line items and justifications
    timeline: Dict[str, Any] = Field(default_factory=dict)  # Project timeline information
    export_history: List[Dict[str, Any]] = Field(default_factory=list)  # Record of exports
    node_type: NodeType = NodeType.PROJECT
    
    def __init__(self, **data):
        # Handle string status values
        if 'status' in data and isinstance(data['status'], str):
            try:
                data['status'] = GrantStatus(data['status'].lower())
            except ValueError:
                # Use default if invalid
                data['status'] = GrantStatus.DRAFTING
        super().__init__(**data)


class CollaboratorRole(str, Enum):
    """Roles for collaborators."""

    PRINCIPAL_INVESTIGATOR = "principal_investigator"
    CO_INVESTIGATOR = "co_investigator"
    COLLABORATOR = "collaborator"
    ADVISOR = "advisor"
    CONSULTANT = "consultant"
    STUDENT = "student"
    
    @classmethod
    def _missing_(cls, value):
        # Handle string values regardless of case
        if isinstance(value, str):
            for member in cls.__members__.values():
                if member.value.lower() == value.lower():
                    return member
            # Also try to match with underscores replaced by spaces
            value_with_spaces = value.lower().replace(" ", "_")
            for member in cls.__members__.values():
                if member.value.lower() == value_with_spaces:
                    return member
        return None


class Collaborator(KnowledgeNode):
    """Represents a research collaborator."""

    name: str
    email: Optional[str] = None
    affiliation: Optional[str] = None
    role: CollaboratorRole = CollaboratorRole.COLLABORATOR
    notes: List[UUID] = Field(default_factory=list)  # References to notes they've contributed to
    permissions: Dict[str, bool] = Field(default_factory=dict)  # Permissions for different operations
    experiments: List[UUID] = Field(default_factory=list)  # Experiments they're involved in
    grants: List[UUID] = Field(default_factory=list)  # Grants they're involved in
    node_type: NodeType = NodeType.PERSON
    
    def __init__(self, **data):
        # Handle string role values
        if 'role' in data and isinstance(data['role'], str):
            try:
                data['role'] = CollaboratorRole(data['role'].lower())
            except ValueError:
                # Try with underscores instead of spaces
                try:
                    data['role'] = CollaboratorRole(data['role'].lower().replace(' ', '_'))
                except ValueError:
                    # Use default if invalid
                    data['role'] = CollaboratorRole.COLLABORATOR
        super().__init__(**data)


class Annotation(CommonAnnotation):
    """Represents an annotation or comment on a knowledge node.
    
    This class extends the CommonAnnotation from the common library,
    but adds ResearchBrain-specific fields and behavior.
    """

    collaborator_id: UUID  # Who made the annotation
    # Rename from parent CommonAnnotation class
    
    def __init__(self, **data):
        # Map collaborator_id to author_id for compatibility with CommonAnnotation
        if 'collaborator_id' in data and 'author_id' not in data:
            data['author_id'] = data['collaborator_id']
        super().__init__(**data)
    
    @property
    def author_id(self) -> Optional[UUID]:
        # Compatibility with brain.py
        return self.collaborator_id
        
    node_type: NodeType = NodeType.ANNOTATION