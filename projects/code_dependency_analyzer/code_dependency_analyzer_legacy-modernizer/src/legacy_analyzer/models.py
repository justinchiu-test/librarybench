"""Data models for the Legacy System Modernization Analyzer."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PatternType(str, Enum):
    """Types of legacy patterns."""

    GOD_CLASS = "god_class"
    SPAGHETTI_DEPENDENCY = "spaghetti_dependency"
    CIRCULAR_DEPENDENCY = "circular_dependency"
    SHOTGUN_SURGERY = "shotgun_surgery"
    FEATURE_ENVY = "feature_envy"
    TIGHTLY_COUPLED_DATABASE = "tightly_coupled_database"
    OUTDATED_ARCHITECTURE = "outdated_architecture"
    MONOLITHIC_STRUCTURE = "monolithic_structure"


class ModernizationDifficulty(str, Enum):
    """Difficulty levels for modernization."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskLevel(str, Enum):
    """Risk levels for modernization actions."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MilestoneStatus(str, Enum):
    """Status of modernization milestones."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class LegacyPattern(BaseModel):
    """Represents a detected legacy pattern."""

    pattern_type: PatternType
    module_path: str
    description: str
    difficulty: ModernizationDifficulty
    risk: RiskLevel
    affected_files: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    metrics: Dict[str, float] = Field(default_factory=dict)


class DatabaseCoupling(BaseModel):
    """Represents database coupling between modules."""

    coupled_modules: List[str]
    shared_tables: List[str]
    orm_models: List[str]
    raw_sql_queries: List[str] = Field(default_factory=list)
    coupling_strength: float = Field(ge=0, le=1)
    decoupling_effort_hours: float


class StranglerFigBoundary(BaseModel):
    """Represents a potential strangler fig boundary."""

    boundary_name: str
    internal_modules: List[str]
    external_dependencies: List[str]
    internal_dependencies: List[str]
    api_surface: List[str]
    isolation_score: float = Field(ge=0, le=1)
    recommended_order: int
    estimated_effort_hours: float


class ExtractionFeasibility(BaseModel):
    """Represents feasibility analysis for module extraction."""

    module_path: str
    feasibility_score: float = Field(ge=0, le=1)
    dependencies_to_break: List[str]
    backward_compatibility_requirements: List[str]
    estimated_effort_hours: float
    risks: List[str]
    recommendations: List[str]


class ModernizationMilestone(BaseModel):
    """Represents a milestone in the modernization roadmap."""

    name: str
    description: str
    phase: int
    dependencies: List[str] = Field(default_factory=list)
    deliverables: List[str]
    estimated_duration_days: float
    risk_level: RiskLevel
    status: MilestoneStatus = MilestoneStatus.PENDING


class ModernizationRoadmap(BaseModel):
    """Represents a complete modernization roadmap."""

    project_name: str
    total_duration_days: float
    phases: Dict[int, List[ModernizationMilestone]]
    critical_path: List[str]
    risk_assessment: Dict[str, str]
    success_metrics: Dict[str, float]
    generated_at: datetime = Field(default_factory=datetime.now)


class AnalysisResult(BaseModel):
    """Complete analysis result from the Legacy Analyzer."""

    legacy_patterns: List[LegacyPattern]
    database_couplings: List[DatabaseCoupling]
    strangler_boundaries: List[StranglerFigBoundary]
    extraction_feasibilities: List[ExtractionFeasibility]
    modernization_roadmap: Optional[ModernizationRoadmap] = None
    summary: Dict[str, Any] = Field(default_factory=dict)
    analysis_duration_seconds: float
