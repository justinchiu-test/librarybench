"""
Core data models for the ProductMind knowledge management system.
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Sentiment(str, Enum):
    """Sentiment classification for feedback."""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    MIXED = "mixed"


class Priority(str, Enum):
    """Priority levels for features and stakeholders."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


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


class Feedback(BaseModel):
    """Customer feedback model."""
    id: UUID = Field(default_factory=uuid4)
    content: str
    source: SourceType
    source_id: Optional[str] = None
    customer_id: Optional[str] = None
    customer_segment: Optional[str] = None
    sentiment: Optional[Sentiment] = None
    created_at: datetime = Field(default_factory=datetime.now)
    themes: List[str] = Field(default_factory=list)
    cluster_id: Optional[int] = None
    impact_score: Optional[float] = None


class Theme(BaseModel):
    """Extracted theme from feedback."""
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    frequency: int = 0
    impact_score: float = 0.0
    sentiment_distribution: Dict[Sentiment, int] = Field(default_factory=dict)
    feedback_ids: List[UUID] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class FeedbackCluster(BaseModel):
    """Cluster of related feedback items."""
    id: int
    name: str
    description: Optional[str] = None
    centroid: List[float] = Field(default_factory=list)
    feedback_ids: List[UUID] = Field(default_factory=list)
    themes: List[str] = Field(default_factory=list)
    sentiment_distribution: Dict[Sentiment, int] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class StrategicGoal(BaseModel):
    """Strategic business objective."""
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str
    priority: Priority
    metrics: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Feature(BaseModel):
    """Product feature for prioritization."""
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str
    status: str = "proposed"
    priority: Optional[Priority] = None
    effort_estimate: Optional[float] = None
    value_estimate: Optional[float] = None
    risk_level: Optional[float] = None
    dependencies: List[UUID] = Field(default_factory=list)
    themes: List[str] = Field(default_factory=list)
    strategic_alignment: Dict[UUID, float] = Field(default_factory=dict)
    feedback_ids: List[UUID] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Competitor(BaseModel):
    """Competitor profile."""
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    website: Optional[str] = None
    market_share: Optional[float] = None
    target_segments: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    feature_comparison: Dict[str, bool] = Field(default_factory=dict)
    price_points: Dict[str, float] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class CompetitiveFeature(BaseModel):
    """Feature for competitive analysis."""
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str
    category: str
    importance: float = 1.0
    our_implementation: Optional[str] = None
    our_rating: Optional[float] = None
    competitor_implementations: Dict[str, Optional[str]] = Field(default_factory=dict)
    competitor_ratings: Dict[str, Optional[float]] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class MarketGap(BaseModel):
    """Identified gap in the market."""
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str
    size_estimate: Optional[float] = None
    opportunity_score: float = 0.0
    related_feedback: List[UUID] = Field(default_factory=list)
    competing_solutions: List[UUID] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)


class Alternative(BaseModel):
    """Alternative option for a decision."""
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    estimated_cost: Optional[float] = None
    estimated_benefit: Optional[float] = None
    estimated_risk: Optional[float] = None
    score: Optional[float] = None


class Decision(BaseModel):
    """Product decision with context and rationale."""
    id: UUID = Field(default_factory=uuid4)
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
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Perspective(BaseModel):
    """Stakeholder perspective on a topic."""
    id: UUID = Field(default_factory=uuid4)
    topic: str
    content: str
    priority: Priority
    influence_level: float = 1.0
    agreement_level: float = 0.0
    stakeholder_id: UUID


class Stakeholder(BaseModel):
    """Stakeholder profile."""
    id: UUID = Field(default_factory=uuid4)
    name: str
    title: str
    department: str
    type: StakeholderType
    influence_level: float = 1.0
    perspectives: List[UUID] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class StakeholderRelationship(BaseModel):
    """Relationship between stakeholders."""
    id: UUID = Field(default_factory=uuid4)
    stakeholder1_id: UUID
    stakeholder2_id: UUID
    relationship_type: str
    alignment_level: float = 0.0
    notes: Optional[str] = None