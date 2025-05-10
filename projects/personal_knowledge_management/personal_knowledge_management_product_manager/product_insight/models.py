"""
Core data models for ProductInsight.

This module defines the main data models used across the ProductInsight system,
implemented using Pydantic for validation and serialization.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


class BaseEntity(BaseModel):
    """Base model for all entities in the system."""
    
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now()


class Tag(BaseModel):
    """A tag for categorizing entities."""
    
    name: str
    color: Optional[str] = None


class SentimentEnum(str, Enum):
    """Sentiment categories for feedback."""
    
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"


class SourceEnum(str, Enum):
    """Source categories for feedback and other data."""
    
    CUSTOMER_INTERVIEW = "customer_interview"
    SURVEY = "survey"
    SUPPORT_TICKET = "support_ticket"
    APP_FEEDBACK = "app_feedback"
    SALES_CALL = "sales_call"
    USER_TESTING = "user_testing"
    SOCIAL_MEDIA = "social_media"
    REVIEW = "review"
    INTERNAL = "internal"
    OTHER = "other"


class PriorityEnum(str, Enum):
    """Priority levels for features and tasks."""
    
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class StatusEnum(str, Enum):
    """Status categories for features and tasks."""
    
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DEFERRED = "deferred"
    CANCELLED = "cancelled"


class StakeholderRoleEnum(str, Enum):
    """Stakeholder roles in the product ecosystem."""
    
    CUSTOMER = "customer"
    ENGINEERING = "engineering"
    PRODUCT = "product"
    DESIGN = "design"
    SALES = "sales"
    MARKETING = "marketing"
    SUPPORT = "support"
    EXECUTIVE = "executive"
    INVESTOR = "investor"
    OTHER = "other"


class InfluenceEnum(str, Enum):
    """Influence levels for stakeholders."""
    
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class MetricTypeEnum(str, Enum):
    """Types of metrics for measuring objectives."""
    
    REVENUE = "revenue"
    ADOPTION = "adoption"
    RETENTION = "retention"
    ENGAGEMENT = "engagement"
    PERFORMANCE = "performance"
    QUALITY = "quality"
    CUSTOM = "custom"


class User(BaseEntity):
    """Represents a user of the system."""
    
    name: str
    email: Optional[str] = None
    role: Optional[str] = None


class FeedbackItem(BaseEntity):
    """Represents a single piece of customer feedback."""
    
    content: str
    source: SourceEnum
    sentiment: Optional[SentimentEnum] = None
    tags: List[Tag] = Field(default_factory=list)
    source_id: Optional[str] = None
    customer_id: Optional[str] = None
    customer_segment: Optional[str] = None
    processed: bool = False
    cluster_id: Optional[UUID] = None
    extracted_features: List[str] = Field(default_factory=list)
    impact_score: Optional[float] = None
    metadata: Dict[str, str] = Field(default_factory=dict)


class FeedbackCluster(BaseEntity):
    """Represents a cluster of related feedback items."""

    name: str
    description: Optional[str] = None
    feedback_ids: List[UUID] = Field(default_factory=list)
    tags: List[Tag] = Field(default_factory=list)
    central_theme: Optional[str] = None
    sentiment_summary: Optional[SentimentEnum] = None
    volume: int = 0
    impact_score: Optional[float] = None
    feature_requests: List[UUID] = Field(default_factory=list)
    common_terms: List[str] = Field(default_factory=list)
    summary: Optional[str] = None
    confidence: float = 0.5

    @model_validator(mode="after")
    def set_volume(self) -> "FeedbackCluster":
        """Set the volume based on the number of feedback items."""
        if self.feedback_ids:
            self.volume = len(self.feedback_ids)
        return self


class StrategicObjective(BaseEntity):
    """Represents a strategic business objective."""
    
    name: str
    description: str
    parent_id: Optional[UUID] = None
    child_ids: List[UUID] = Field(default_factory=list)
    metric_type: Optional[MetricTypeEnum] = None
    metric_target: Optional[float] = None
    metric_current: Optional[float] = None
    timeframe_start: Optional[datetime] = None
    timeframe_end: Optional[datetime] = None
    status: StatusEnum = StatusEnum.PLANNED
    priority: PriorityEnum = PriorityEnum.MEDIUM
    stakeholder_ids: List[UUID] = Field(default_factory=list)
    feature_ids: List[UUID] = Field(default_factory=list)
    tags: List[Tag] = Field(default_factory=list)


class Feature(BaseEntity):
    """Represents a product feature."""
    
    name: str
    description: str
    status: StatusEnum = StatusEnum.PLANNED
    effort_estimate: Optional[float] = None
    value_estimate: Optional[float] = None
    priority_score: Optional[float] = None
    priority_method: Optional[str] = None
    objective_ids: List[UUID] = Field(default_factory=list)
    feedback_ids: List[UUID] = Field(default_factory=list)
    feedback_cluster_ids: List[UUID] = Field(default_factory=list)
    stakeholder_ids: List[UUID] = Field(default_factory=list)
    tags: List[Tag] = Field(default_factory=list)
    dependencies: List[UUID] = Field(default_factory=list)
    kano_category: Optional[str] = None
    technical_debt_impact: Optional[float] = None
    risk_level: Optional[float] = None
    implementation_notes: Optional[str] = None


class PriorityScoreCard(BaseEntity):
    """Represents a priority score for a feature using various methods."""
    
    feature_id: UUID
    rice_score: Optional[float] = None
    value_effort_score: Optional[float] = None
    strategic_alignment_score: Optional[float] = None
    customer_value_score: Optional[float] = None
    innovation_score: Optional[float] = None
    risk_score: Optional[float] = None
    total_score: Optional[float] = None
    custom_scores: Dict[str, float] = Field(default_factory=dict)
    notes: Optional[str] = None


class Competitor(BaseEntity):
    """Represents a competitor in the market."""
    
    name: str
    description: Optional[str] = None
    website: Optional[str] = None
    market_share: Optional[float] = None
    pricing_model: Optional[str] = None
    pricing_details: Optional[str] = None
    target_segments: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    feature_comparison: Dict[str, bool] = Field(default_factory=dict)
    detailed_comparisons: Dict[str, str] = Field(default_factory=dict)
    threat_level: Optional[float] = None
    notes: Optional[str] = None
    tags: List[Tag] = Field(default_factory=list)


class Decision(BaseEntity):
    """Represents a product decision with context and rationale."""

    title: str
    description: str
    context: str
    rationale: str
    alternatives: List[str] = Field(default_factory=list)
    decision_date: datetime = Field(default_factory=datetime.now)
    decided_by: List[UUID] = Field(default_factory=list)
    stakeholder_input: Dict[str, str] = Field(default_factory=dict)  # Use string keys for UUID
    feature_ids: List[UUID] = Field(default_factory=list)
    objective_ids: List[UUID] = Field(default_factory=list)
    supporting_data: List[str] = Field(default_factory=list)
    outcome_notes: Optional[str] = None
    outcome_date: Optional[datetime] = None
    retrospective: Optional[str] = None
    tags: List[Tag] = Field(default_factory=list)


class Stakeholder(BaseEntity):
    """Represents a stakeholder with influence and perspective."""

    name: str
    role: StakeholderRoleEnum
    organization: Optional[str] = None
    email: Optional[str] = None
    influence: InfluenceEnum = InfluenceEnum.MEDIUM
    alignment: Optional[float] = None
    key_concerns: List[str] = Field(default_factory=list)
    feature_preferences: Dict[UUID, float] = Field(default_factory=dict)
    objective_alignment: Dict[UUID, float] = Field(default_factory=dict)
    communication_preferences: Optional[str] = None
    engagement_history: List[str] = Field(default_factory=list)
    notes: Optional[str] = None

    def model_dump(self, **kwargs):
        """Override the model_dump method to convert UUID keys to strings."""
        result = super().model_dump(**kwargs)

        # Convert UUID keys to strings in dictionaries
        if "feature_preferences" in result and result["feature_preferences"]:
            result["feature_preferences"] = {
                str(k): v for k, v in result["feature_preferences"].items()
            }

        if "objective_alignment" in result and result["objective_alignment"]:
            result["objective_alignment"] = {
                str(k): v for k, v in result["objective_alignment"].items()
            }

        return result


class StakeholderPerspective(BaseEntity):
    """Represents a stakeholder's perspective on a specific issue."""

    stakeholder_id: UUID
    topic: str
    perspective: str
    sentiment: SentimentEnum = SentimentEnum.NEUTRAL
    date_recorded: datetime = Field(default_factory=datetime.now)
    context: Optional[str] = None
    related_feature_ids: List[UUID] = Field(default_factory=list)
    related_objective_ids: List[UUID] = Field(default_factory=list)

    @property
    def name(self) -> str:
        """Get a display name for the perspective.

        This is needed for compatibility with other entities that have names.
        """
        return f"Perspective on {self.topic}"


class SearchQuery(BaseModel):
    """Represents a search query across the knowledge base."""
    
    query: str
    include_feedback: bool = True
    include_features: bool = True
    include_objectives: bool = True
    include_decisions: bool = True
    include_competitors: bool = True
    include_stakeholders: bool = True
    tags: List[str] = Field(default_factory=list)
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = 50


class SearchResult(BaseModel):
    """Represents a single search result."""
    
    entity_id: UUID
    entity_type: str
    title: str
    snippet: str
    relevance_score: float
    date: datetime
    tags: List[Tag] = Field(default_factory=list)


class SearchResults(BaseModel):
    """Represents a collection of search results."""
    
    query: str
    results: List[SearchResult] = Field(default_factory=list)
    total_count: int = 0
    execution_time_ms: int = 0
    facets: Dict[str, Dict[str, int]] = Field(default_factory=dict)