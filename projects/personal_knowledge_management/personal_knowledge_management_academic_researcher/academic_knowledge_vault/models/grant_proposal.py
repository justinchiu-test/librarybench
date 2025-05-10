"""
Grant Proposal models for the Academic Knowledge Vault system.

This module defines the data models for grant proposals and funding applications.
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


class FundingStatus(str, enum.Enum):
    """Status categories for grant proposals."""

    DRAFTING = "drafting"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    REVISIONS_REQUESTED = "revisions_requested"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"


class FundingAgencyType(str, enum.Enum):
    """Types of funding agencies."""

    GOVERNMENT = "government"
    FOUNDATION = "foundation"
    INDUSTRY = "industry"
    ACADEMIC = "academic"
    NONPROFIT = "nonprofit"
    INTERNATIONAL = "international"
    OTHER = "other"


class ProposalSection(BaseModel):
    """A section of a grant proposal."""

    title: str
    content: str
    version: int = 1
    word_count: Optional[int] = None
    character_count: Optional[int] = None
    last_edited: datetime.datetime = Field(default_factory=datetime.datetime.now)
    
    # Version history
    previous_versions: List[Dict[str, Union[str, int, datetime.datetime]]] = Field(
        default_factory=list
    )
    
    # References used in this section
    citation_references: List[Reference] = Field(default_factory=list)
    note_references: List[Reference] = Field(default_factory=list)
    
    @validator("word_count", always=True)
    def compute_word_count(cls, v: Optional[int], values: Dict) -> int:
        """Compute word count if not provided."""
        if v is not None:
            return v
        if "content" in values:
            return len(values["content"].split())
        return 0
    
    @validator("character_count", always=True)
    def compute_char_count(cls, v: Optional[int], values: Dict) -> int:
        """Compute character count if not provided."""
        if v is not None:
            return v
        if "content" in values:
            return len(values["content"])
        return 0
    
    def update_content(self, new_content: str) -> None:
        """Update the section content, preserving version history."""
        # Store the current version in history
        self.previous_versions.append({
            "content": self.content,
            "version": self.version,
            "edited_at": self.last_edited
        })
        
        # Update with new content
        self.content = new_content
        self.version += 1
        self.last_edited = datetime.datetime.now()
        self.word_count = len(new_content.split())
        self.character_count = len(new_content)


class BudgetItem(BaseModel):
    """A budget item in a grant proposal."""

    category: str
    item_name: str
    amount: float
    justification: str
    year: Optional[int] = None
    
    # For tracking across proposal versions
    status: str = "active"  # active, removed, modified
    previous_amount: Optional[float] = None


class GrantProposal(BaseKnowledgeItem):
    """A grant proposal or funding application."""

    # Basic proposal information
    title: str
    short_title: Optional[str] = None
    abstract: Optional[str] = None
    status: FundingStatus = FundingStatus.DRAFTING
    
    # Funding information
    funding_agency: str
    agency_type: FundingAgencyType = FundingAgencyType.GOVERNMENT
    program_name: Optional[str] = None
    grant_number: Optional[str] = None
    requested_amount: Optional[float] = None
    awarded_amount: Optional[float] = None
    
    # Dates and deadlines
    submission_deadline: Optional[datetime.datetime] = None
    start_date: Optional[datetime.datetime] = None
    end_date: Optional[datetime.datetime] = None
    submitted_date: Optional[datetime.datetime] = None
    decision_date: Optional[datetime.datetime] = None
    
    # People involved
    investigators: List[Person] = Field(default_factory=list)
    collaborators: List[Person] = Field(default_factory=list)
    
    # Proposal content
    sections: Dict[str, ProposalSection] = Field(default_factory=dict)
    
    # Budget
    budget_items: List[BudgetItem] = Field(default_factory=list)
    
    # Research content references
    research_questions: List[Reference] = Field(default_factory=list)
    hypotheses: List[Reference] = Field(default_factory=list)
    supporting_evidence: List[Reference] = Field(default_factory=list)
    key_citations: List[Reference] = Field(default_factory=list)
    related_notes: List[Reference] = Field(default_factory=list)
    
    # Previous versions or related proposals
    previous_submission_id: Optional[str] = None
    related_proposals: List[Reference] = Field(default_factory=list)
    
    # Storage information
    storage: Optional[StorageInfo] = None
    
    def add_section(self, section_name: str, section: ProposalSection) -> None:
        """Add a section to the proposal."""
        self.sections[section_name] = section
        self.update_timestamp()
    
    def update_section(self, section_name: str, new_content: str) -> None:
        """Update content of an existing section."""
        if section_name in self.sections:
            self.sections[section_name].update_content(new_content)
            self.update_timestamp()
    
    def add_budget_item(self, item: BudgetItem) -> None:
        """Add a budget item to the proposal."""
        self.budget_items.append(item)
        self.update_timestamp()
    
    def update_status(self, status: FundingStatus) -> None:
        """Update the funding status of the proposal."""
        self.status = status
        self.update_timestamp()
    
    def add_investigator(self, person: Person) -> None:
        """Add an investigator to the proposal."""
        for existing_person in self.investigators:
            if existing_person.id == person.id:
                return  # Person already exists
        self.investigators.append(person)
        self.update_timestamp()
    
    def add_research_question(self, question_ref: Reference) -> None:
        """Add a research question to the proposal."""
        for existing_ref in self.research_questions:
            if existing_ref.item_id == question_ref.item_id:
                return  # Reference already exists
        self.research_questions.append(question_ref)
        self.update_timestamp()
    
    def add_key_citation(self, citation_ref: Reference) -> None:
        """Add a key citation to the proposal."""
        for existing_ref in self.key_citations:
            if existing_ref.item_id == citation_ref.item_id:
                return  # Reference already exists
        self.key_citations.append(citation_ref)
        self.update_timestamp()
    
    def calculate_budget_total(self) -> float:
        """Calculate the total budget amount requested."""
        return sum(item.amount for item in self.budget_items if item.status == "active")
    
    def calculate_word_count(self) -> int:
        """Calculate the total word count across all sections."""
        return sum(section.word_count or 0 for section in self.sections.values())


class GrantProposalWorkspace(BaseModel):
    """A workspace for organizing materials for a grant proposal."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    proposal_id: Optional[str] = None  # Reference to the actual proposal
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    
    # Collections of related materials
    note_ids: Set[str] = Field(default_factory=set)
    citation_ids: Set[str] = Field(default_factory=set)
    question_ids: Set[str] = Field(default_factory=set)
    experiment_ids: Set[str] = Field(default_factory=set)
    
    # Organizational metadata
    tags: Set[str] = Field(default_factory=set)
    status: str = "active"
    deadline: Optional[datetime.datetime] = None
    
    def add_note(self, note_id: str) -> None:
        """Add a note to the workspace."""
        self.note_ids.add(note_id)
        self.updated_at = datetime.datetime.now()
    
    def remove_note(self, note_id: str) -> None:
        """Remove a note from the workspace."""
        if note_id in self.note_ids:
            self.note_ids.remove(note_id)
            self.updated_at = datetime.datetime.now()
    
    def add_citation(self, citation_id: str) -> None:
        """Add a citation to the workspace."""
        self.citation_ids.add(citation_id)
        self.updated_at = datetime.datetime.now()
    
    def add_question(self, question_id: str) -> None:
        """Add a research question to the workspace."""
        self.question_ids.add(question_id)
        self.updated_at = datetime.datetime.now()
    
    def add_experiment(self, experiment_id: str) -> None:
        """Add an experiment to the workspace."""
        self.experiment_ids.add(experiment_id)
        self.updated_at = datetime.datetime.now()


import uuid