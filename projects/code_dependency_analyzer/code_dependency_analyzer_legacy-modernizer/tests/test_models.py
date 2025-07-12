"""Tests for data models."""

import pytest
from datetime import datetime
from pydantic import ValidationError
from legacy_analyzer.models import (
    PatternType,
    ModernizationDifficulty,
    RiskLevel,
    MilestoneStatus,
    LegacyPattern,
    DatabaseCoupling,
    StranglerFigBoundary,
    ExtractionFeasibility,
    ModernizationMilestone,
    ModernizationRoadmap,
    AnalysisResult,
)


class TestModels:
    """Test data model validation and behavior."""

    def test_legacy_pattern_validation(self):
        """Test LegacyPattern model validation."""
        # Valid pattern
        pattern = LegacyPattern(
            pattern_type=PatternType.GOD_CLASS,
            module_path="test/module.py",
            description="Test pattern",
            difficulty=ModernizationDifficulty.HIGH,
            risk=RiskLevel.MEDIUM,
        )

        assert pattern.pattern_type == PatternType.GOD_CLASS
        assert pattern.module_path == "test/module.py"
        assert pattern.affected_files == []  # Default
        assert pattern.dependencies == []  # Default
        assert pattern.metrics == {}  # Default

    def test_database_coupling_validation(self):
        """Test DatabaseCoupling model validation."""
        # Valid coupling
        coupling = DatabaseCoupling(
            coupled_modules=["module1", "module2"],
            shared_tables=["users"],
            orm_models=["User"],
            coupling_strength=0.75,
            decoupling_effort_hours=40.5,
        )

        assert coupling.coupling_strength == 0.75
        assert coupling.decoupling_effort_hours == 40.5
        assert coupling.raw_sql_queries == []  # Default

        # Test coupling strength bounds
        with pytest.raises(ValidationError):
            DatabaseCoupling(
                coupled_modules=["m1"],
                shared_tables=["t1"],
                orm_models=[],
                coupling_strength=1.5,  # > 1
                decoupling_effort_hours=10,
            )

        with pytest.raises(ValidationError):
            DatabaseCoupling(
                coupled_modules=["m1"],
                shared_tables=["t1"],
                orm_models=[],
                coupling_strength=-0.1,  # < 0
                decoupling_effort_hours=10,
            )

    def test_strangler_fig_boundary_validation(self):
        """Test StranglerFigBoundary model validation."""
        boundary = StranglerFigBoundary(
            boundary_name="auth_boundary",
            internal_modules=["auth/login.py", "auth/logout.py"],
            external_dependencies=["db"],
            internal_dependencies=["shared"],
            api_surface=["auth/api.py"],
            isolation_score=0.85,
            recommended_order=1,
            estimated_effort_hours=120,
        )

        assert boundary.isolation_score == 0.85
        assert boundary.recommended_order == 1

        # Test isolation score bounds
        with pytest.raises(ValidationError):
            StranglerFigBoundary(
                boundary_name="test",
                internal_modules=["m1"],
                external_dependencies=[],
                internal_dependencies=[],
                api_surface=[],
                isolation_score=1.1,  # > 1
                recommended_order=1,
                estimated_effort_hours=10,
            )

    def test_extraction_feasibility_validation(self):
        """Test ExtractionFeasibility model validation."""
        feasibility = ExtractionFeasibility(
            module_path="legacy/module.py",
            feasibility_score=0.65,
            dependencies_to_break=["dep1", "dep2"],
            backward_compatibility_requirements=["API stability"],
            estimated_effort_hours=80,
            risks=["No tests"],
            recommendations=["Add tests first"],
        )

        assert feasibility.feasibility_score == 0.65
        assert len(feasibility.risks) == 1
        assert len(feasibility.recommendations) == 1

        # Test feasibility score bounds
        with pytest.raises(ValidationError):
            ExtractionFeasibility(
                module_path="test.py",
                feasibility_score=-0.1,  # < 0
                dependencies_to_break=[],
                backward_compatibility_requirements=[],
                estimated_effort_hours=10,
                risks=[],
                recommendations=[],
            )

    def test_modernization_milestone(self):
        """Test ModernizationMilestone model."""
        milestone = ModernizationMilestone(
            name="Establish test coverage",
            description="Create comprehensive tests",
            phase=1,
            deliverables=["Unit tests", "Integration tests"],
            estimated_duration_days=10.5,
            risk_level=RiskLevel.LOW,
        )

        assert milestone.status == MilestoneStatus.PENDING  # Default
        assert milestone.dependencies == []  # Default
        assert milestone.phase == 1
        assert milestone.estimated_duration_days == 10.5

    def test_modernization_roadmap(self):
        """Test ModernizationRoadmap model."""
        milestone = ModernizationMilestone(
            name="Test milestone",
            description="Test",
            phase=1,
            deliverables=["Test deliverable"],
            estimated_duration_days=5,
            risk_level=RiskLevel.LOW,
        )

        roadmap = ModernizationRoadmap(
            project_name="Legacy System",
            total_duration_days=100,
            phases={1: [milestone]},
            critical_path=["Test milestone"],
            risk_assessment={"Test Risk": "Description"},
            success_metrics={"metric": 50.0},
        )

        assert roadmap.project_name == "Legacy System"
        assert roadmap.total_duration_days == 100
        assert len(roadmap.phases) == 1
        assert roadmap.phases[1][0].name == "Test milestone"
        assert isinstance(roadmap.generated_at, datetime)

    def test_analysis_result(self):
        """Test AnalysisResult model."""
        pattern = LegacyPattern(
            pattern_type=PatternType.GOD_CLASS,
            module_path="test.py",
            description="Test",
            difficulty=ModernizationDifficulty.HIGH,
            risk=RiskLevel.HIGH,
        )

        result = AnalysisResult(
            legacy_patterns=[pattern],
            database_couplings=[],
            strangler_boundaries=[],
            extraction_feasibilities=[],
            modernization_roadmap=None,
            summary={"total_modules": 5},
            analysis_duration_seconds=2.5,
        )

        assert len(result.legacy_patterns) == 1
        assert result.legacy_patterns[0].pattern_type == PatternType.GOD_CLASS
        assert result.summary["total_modules"] == 5
        assert result.analysis_duration_seconds == 2.5
        assert result.modernization_roadmap is None

    def test_enum_values(self):
        """Test enum value access."""
        assert PatternType.GOD_CLASS.value == "god_class"
        assert ModernizationDifficulty.HIGH.value == "high"
        assert RiskLevel.CRITICAL.value == "critical"
        assert MilestoneStatus.IN_PROGRESS.value == "in_progress"

        # Test all pattern types
        pattern_types = [pt.value for pt in PatternType]
        assert "god_class" in pattern_types
        assert "circular_dependency" in pattern_types
        assert "spaghetti_dependency" in pattern_types

    def test_model_serialization(self):
        """Test model serialization to dict."""
        pattern = LegacyPattern(
            pattern_type=PatternType.GOD_CLASS,
            module_path="test.py",
            description="Test pattern",
            difficulty=ModernizationDifficulty.HIGH,
            risk=RiskLevel.MEDIUM,
            metrics={"complexity": 50},
        )

        # Convert to dict
        pattern_dict = pattern.model_dump()

        assert pattern_dict["pattern_type"] == "god_class"
        assert pattern_dict["module_path"] == "test.py"
        assert pattern_dict["metrics"]["complexity"] == 50

        # Should be JSON serializable
        import json

        json_str = json.dumps(pattern_dict)
        assert isinstance(json_str, str)
