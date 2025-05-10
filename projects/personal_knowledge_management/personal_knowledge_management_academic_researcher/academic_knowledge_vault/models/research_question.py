"""
Research Question models for the Academic Knowledge Vault system.

This module defines the data models for research questions, hypotheses, and evidence.
"""

import datetime
import enum
from typing import Dict, List, Optional, Set, Union

from pydantic import BaseModel, Field, validator

from academic_knowledge_vault.models.base import (
    BaseKnowledgeItem,
    KnowledgeItemType,
    LinkedItem,
    Reference,
    StorageInfo,
)


class EvidenceType(str, enum.Enum):
    """Types of evidence for research questions."""

    SUPPORTING = "supporting"
    CONTRADICTING = "contradicting"
    INCONCLUSIVE = "inconclusive"
    METHODOLOGY = "methodology"
    THEORETICAL = "theoretical"
    EMPIRICAL = "empirical"


class EvidenceStrength(str, enum.Enum):
    """Strength categories for evidence."""

    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    ANECDOTAL = "anecdotal"
    UNKNOWN = "unknown"


class Evidence(BaseKnowledgeItem):
    """Evidence related to a research question or hypothesis."""

    evidence_type: EvidenceType
    strength: EvidenceStrength = EvidenceStrength.UNKNOWN
    description: str
    source: Optional[Reference] = None  # Citation, Note, or Experiment reference
    confidence_score: float = 0.5  # 0.0 to 1.0
    methodology_notes: Optional[str] = None
    
    # Relationships to questions and hypotheses
    supports: List[Reference] = Field(default_factory=list)
    contradicts: List[Reference] = Field(default_factory=list)
    
    # Version tracking
    version: int = 1
    last_reviewed: datetime.datetime = Field(default_factory=datetime.datetime.now)
    
    def add_supports(self, reference: Reference) -> None:
        """Add a research item that this evidence supports."""
        for existing_ref in self.supports:
            if existing_ref.item_id == reference.item_id:
                return  # Reference already exists
        self.supports.append(reference)
        self.update_timestamp()
    
    def add_contradicts(self, reference: Reference) -> None:
        """Add a research item that this evidence contradicts."""
        for existing_ref in self.contradicts:
            if existing_ref.item_id == reference.item_id:
                return  # Reference already exists
        self.contradicts.append(reference)
        self.update_timestamp()
    
    def update_strength(self, strength: EvidenceStrength) -> None:
        """Update the strength assessment of this evidence."""
        self.strength = strength
        self.last_reviewed = datetime.datetime.now()
        self.update_timestamp()


class HypothesisStatus(str, enum.Enum):
    """Status categories for research hypotheses."""

    PROPOSED = "proposed"
    INVESTIGATING = "investigating"
    SUPPORTED = "supported"
    REJECTED = "rejected"
    REVISED = "revised"
    PUBLISHED = "published"


class Hypothesis(BaseKnowledgeItem):
    """A specific hypothesis related to a research question."""

    statement: str
    status: HypothesisStatus = HypothesisStatus.PROPOSED
    research_question_id: Optional[str] = None
    
    # Evidence tracking
    supporting_evidence: List[Reference] = Field(default_factory=list)
    contradicting_evidence: List[Reference] = Field(default_factory=list)
    
    # Version tracking
    version: int = 1
    parent_hypothesis_id: Optional[str] = None  # For tracking revisions
    
    # Related knowledge items
    related_citations: List[Reference] = Field(default_factory=list)
    related_notes: List[Reference] = Field(default_factory=list)
    related_experiments: List[Reference] = Field(default_factory=list)
    
    # Metrics
    evidence_strength_score: float = 0.0  # Calculated from evidence
    confidence_level: float = 0.0  # 0.0 to 1.0
    
    def add_supporting_evidence(self, evidence_ref: Reference) -> None:
        """Add supporting evidence to the hypothesis."""
        for existing_ref in self.supporting_evidence:
            if existing_ref.item_id == evidence_ref.item_id:
                return  # Reference already exists
        self.supporting_evidence.append(evidence_ref)
        self.update_timestamp()
    
    def add_contradicting_evidence(self, evidence_ref: Reference) -> None:
        """Add contradicting evidence to the hypothesis."""
        for existing_ref in self.contradicting_evidence:
            if existing_ref.item_id == evidence_ref.item_id:
                return  # Reference already exists
        self.contradicting_evidence.append(evidence_ref)
        self.update_timestamp()
    
    def update_status(self, status: HypothesisStatus) -> None:
        """Update the status of the hypothesis."""
        self.status = status
        self.update_timestamp()
    
    def calculate_evidence_strength(self) -> float:
        """
        Calculate the overall evidence strength score.
        This is a placeholder - actual implementation would be more sophisticated.
        """
        # Simple placeholder calculation - would be replaced with actual algorithm
        supporting_count = len(self.supporting_evidence)
        contradicting_count = len(self.contradicting_evidence)
        
        if supporting_count + contradicting_count == 0:
            return 0.0
        
        return supporting_count / (supporting_count + contradicting_count)


class ResearchQuestionStatus(str, enum.Enum):
    """Status categories for research questions."""

    ACTIVE = "active"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    ABANDONED = "abandoned"
    PUBLISHED = "published"


class ResearchQuestion(BaseKnowledgeItem):
    """A research question being investigated."""

    question: str
    description: Optional[str] = None
    status: ResearchQuestionStatus = ResearchQuestionStatus.ACTIVE
    
    # Related hypotheses
    hypotheses: List[Reference] = Field(default_factory=list)
    
    # Evidence directly related to the question
    supporting_evidence: List[Reference] = Field(default_factory=list)
    contradicting_evidence: List[Reference] = Field(default_factory=list)
    
    # Related knowledge items
    related_citations: List[Reference] = Field(default_factory=list)
    related_notes: List[Reference] = Field(default_factory=list)
    related_experiments: List[Reference] = Field(default_factory=list)
    related_grant_proposals: List[Reference] = Field(default_factory=list)
    
    # Knowledge gap tracking
    knowledge_gaps: List[str] = Field(default_factory=list)
    
    # Project management
    priority: int = 3  # 1-5 scale, 1 being highest priority
    deadline: Optional[datetime.datetime] = None
    
    def add_hypothesis(self, hypothesis_ref: Reference) -> None:
        """Add a hypothesis to the research question."""
        for existing_ref in self.hypotheses:
            if existing_ref.item_id == hypothesis_ref.item_id:
                return  # Reference already exists
        self.hypotheses.append(hypothesis_ref)
        self.update_timestamp()
    
    def add_supporting_evidence(self, evidence_ref: Reference) -> None:
        """Add supporting evidence to the research question."""
        for existing_ref in self.supporting_evidence:
            if existing_ref.item_id == evidence_ref.item_id:
                return  # Reference already exists
        self.supporting_evidence.append(evidence_ref)
        self.update_timestamp()
    
    def add_contradicting_evidence(self, evidence_ref: Reference) -> None:
        """Add contradicting evidence to the research question."""
        for existing_ref in self.contradicting_evidence:
            if existing_ref.item_id == evidence_ref.item_id:
                return  # Reference already exists
        self.contradicting_evidence.append(evidence_ref)
        self.update_timestamp()
    
    def add_knowledge_gap(self, gap_description: str) -> None:
        """Add a knowledge gap related to the research question."""
        if gap_description not in self.knowledge_gaps:
            self.knowledge_gaps.append(gap_description)
            self.update_timestamp()
    
    def calculate_evidence_landscape(self) -> Dict[str, float]:
        """
        Calculate metrics about the evidence landscape for this question.
        This is a placeholder - actual implementation would be more sophisticated.
        """
        return {
            "supporting_count": len(self.supporting_evidence),
            "contradicting_count": len(self.contradicting_evidence),
            "hypothesis_count": len(self.hypotheses),
            "knowledge_gap_count": len(self.knowledge_gaps),
        }


class ResearchQuestionCollection(BaseModel):
    """A collection of related research questions."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    question_ids: Set[str] = Field(default_factory=set)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    tags: Set[str] = Field(default_factory=set)
    
    def add_question(self, question_id: str) -> None:
        """Add a research question to the collection."""
        self.question_ids.add(question_id)
        self.updated_at = datetime.datetime.now()
    
    def remove_question(self, question_id: str) -> None:
        """Remove a research question from the collection."""
        if question_id in self.question_ids:
            self.question_ids.remove(question_id)
            self.updated_at = datetime.datetime.now()


import uuid