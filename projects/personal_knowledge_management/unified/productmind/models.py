"""Core data models for the ProductMind knowledge management system.

This module defines the domain-specific data models for the ProductMind
knowledge management system, building on the common KnowledgeNode base class
from the unified library.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

# Import base models from common library
from common.core.models import KnowledgeNode, Priority, NodeType, Relation, RelationType, Status


class Sentiment(str, Enum):
    """Sentiment classification for feedback."""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    MIXED = "mixed"


class SourceType(str, Enum):
    """Types of feedback sources."""
    SURVEY = "survey"
    SUPPORT_TICKET = "support_ticket"
    INTERVIEW = "interview"
    APP_REVIEW = "app_review"
    SOCIAL_MEDIA = "social_media"
    SALES_CALL = "sales_call"
    CUSTOMER_MEETING = "customer_meeting"
    BETA_FEEDBACK = "beta_feedback"
    OTHER = "other"


class StakeholderType(str, Enum):
    """Types of stakeholders."""
    EXECUTIVE = "executive"
    PRODUCT = "product"
    ENGINEERING = "engineering"
    DESIGN = "design"
    MARKETING = "marketing"
    SALES = "sales"
    CUSTOMER_SUCCESS = "customer_success"
    FINANCE = "finance"
    LEGAL = "legal"
    CUSTOMER = "customer"
    PARTNER = "partner"
    OTHER = "other"


class Feedback(KnowledgeNode):
    """Customer feedback model."""
    title: str = ""  # Added to match common pattern
    content: str
    source: SourceType
    source_id: Optional[str] = None
    customer_id: Optional[str] = None
    customer_segment: Optional[str] = None
    sentiment: Optional[Sentiment] = None
    themes: List[str] = Field(default_factory=list)
    cluster_id: Optional[int] = None
    impact_score: Optional[float] = None
    node_type: NodeType = NodeType.OTHER


class Theme(KnowledgeNode):
    """Extracted theme from feedback."""
    name: str
    description: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    frequency: int = 0
    impact_score: float = 0.0
    sentiment_distribution: Dict[str, int] = Field(default_factory=dict)
    feedback_ids: List[UUID] = Field(default_factory=list)
    node_type: NodeType = NodeType.TAG


class FeedbackCluster(KnowledgeNode):
    """Cluster of related feedback items."""
    cluster_numeric_id: int  # Store the numeric ID as a separate field
    name: str
    description: Optional[str] = None
    centroid: List[float] = Field(default_factory=list)
    feedback_ids: List[UUID] = Field(default_factory=list)
    themes: List[str] = Field(default_factory=list)
    sentiment_distribution: Dict[str, int] = Field(default_factory=dict)
    node_type: NodeType = NodeType.OTHER
    
    def __init__(self, **data):
        # If cluster_id is provided in the constructor, use it as cluster_numeric_id
        if 'cluster_id' in data and 'cluster_numeric_id' not in data:
            data['cluster_numeric_id'] = data.pop('cluster_id')
        # If id is provided as an integer, convert to cluster_numeric_id
        elif 'id' in data and isinstance(data['id'], int):
            data['cluster_numeric_id'] = data['id']
            data['id'] = uuid4()  # Generate a proper UUID for id
        
        super().__init__(**data)
    
    @property
    def cluster_id(self) -> int:
        """Maintain compatibility with old code."""
        return self.cluster_numeric_id
        
    @cluster_id.setter
    def cluster_id(self, value: int):
        self.cluster_numeric_id = value


class StrategicGoal(KnowledgeNode):
    """Strategic business objective."""
    name: str
    description: str
    priority: Priority
    metrics: List[str] = Field(default_factory=list)
    node_type: NodeType = NodeType.OTHER


class Feature(KnowledgeNode):
    """Product feature for prioritization."""
    name: str
    description: str
    status: str = "proposed"
    priority: Optional[Priority] = None
    effort_estimate: Optional[float] = None
    value_estimate: Optional[float] = None
    risk_level: Optional[float] = None
    dependencies: List[UUID] = Field(default_factory=list)
    themes: List[str] = Field(default_factory=list)
    strategic_alignment: Dict[str, float] = Field(default_factory=dict)
    feedback_ids: List[UUID] = Field(default_factory=list)
    node_type: NodeType = NodeType.OTHER


class Competitor(KnowledgeNode):
    """Competitor profile."""
    name: str
    description: Optional[str] = None
    website: Optional[str] = None
    market_share: Optional[float] = None
    target_segments: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    feature_comparison: Dict[str, bool] = Field(default_factory=dict)
    price_points: Dict[str, float] = Field(default_factory=dict)
    node_type: NodeType = NodeType.OTHER


class CompetitiveFeature(KnowledgeNode):
    """Feature for competitive analysis."""
    name: str
    description: str
    category: str
    importance: float = 1.0
    our_implementation: Optional[str] = None
    our_rating: Optional[float] = None
    competitor_implementations: Dict[str, Optional[str]] = Field(default_factory=dict)
    competitor_ratings: Dict[str, Optional[float]] = Field(default_factory=dict)
    node_type: NodeType = NodeType.OTHER


class MarketGap(KnowledgeNode):
    """Identified gap in the market."""
    name: str
    description: str
    size_estimate: Optional[float] = None
    opportunity_score: float = 0.0
    related_feedback: List[UUID] = Field(default_factory=list)
    competing_solutions: List[UUID] = Field(default_factory=list)
    node_type: NodeType = NodeType.OTHER


class Alternative(KnowledgeNode):
    """Alternative option for a decision."""
    name: str
    description: str
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    estimated_cost: Optional[float] = None
    estimated_benefit: Optional[float] = None
    estimated_risk: Optional[float] = None
    score: Optional[float] = None
    node_type: NodeType = NodeType.OTHER


class Decision(KnowledgeNode):
    """Product decision with context and rationale."""
    title: str
    description: str
    context: str
    problem_statement: str
    decision_date: datetime
    decision_maker: str
    chosen_alternative: UUID
    alternatives: List[Alternative] = Field(default_factory=list)
    rationale: str
    success_criteria: List[str] = Field(default_factory=list)
    related_decisions: List[UUID] = Field(default_factory=list)
    related_feedback: List[UUID] = Field(default_factory=list)
    related_features: List[UUID] = Field(default_factory=list)
    status: str = "decided"
    outcome_assessment: Optional[str] = None
    node_type: NodeType = NodeType.OTHER


class Perspective(KnowledgeNode):
    """Stakeholder perspective on a topic."""
    topic: str
    content: str
    priority: Priority
    influence_level: float = 1.0
    agreement_level: float = 0.0
    stakeholder_id: UUID
    node_type: NodeType = NodeType.OTHER


class Stakeholder(KnowledgeNode):
    """Stakeholder profile."""
    name: str
    title: str
    department: str
    type: StakeholderType
    influence_level: float = 1.0
    perspectives: List[UUID] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
    node_type: NodeType = NodeType.PERSON


class StakeholderRelationship(BaseModel):
    """Relationship between stakeholders."""
    id: UUID = Field(default_factory=uuid4)
    stakeholder1_id: UUID
    stakeholder2_id: UUID
    relationship_type: str = "stakeholder_relationship"
    alignment_level: float = 0.0
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Fields needed for compatibility with Relation
    source_id: UUID = None
    target_id: UUID = None
    relation_type: Union[RelationType, str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def __init__(self, **data):
        # Extract and process fields first
        relation_id = data.get("id", uuid4())
        stakeholder1_id = data.get("stakeholder1_id")
        stakeholder2_id = data.get("stakeholder2_id")
        relation_type = data.get("relationship_type", "stakeholder_relationship")
        alignment_level = data.get("alignment_level", 0.0)
        notes = data.get("notes")
        
        # Convert to RelationType if possible
        if isinstance(relation_type, str):
            try:
                relation_type_enum = RelationType(relation_type)
            except ValueError:
                # Keep as string if not a valid RelationType
                relation_type_enum = relation_type
        else:
            relation_type_enum = relation_type
        
        # Prepare the metadata
        metadata = {
            "alignment_level": alignment_level,
            "notes": notes
        }
        
        # Initialize the model with all fields
        super().__init__(
            id=relation_id,
            stakeholder1_id=stakeholder1_id,
            stakeholder2_id=stakeholder2_id,
            relationship_type=relation_type if isinstance(relation_type, str) else relation_type.value,
            alignment_level=alignment_level,
            notes=notes,
            # Relation compatibility fields
            source_id=stakeholder1_id,
            target_id=stakeholder2_id,
            relation_type=relation_type_enum,
            metadata=metadata
        )