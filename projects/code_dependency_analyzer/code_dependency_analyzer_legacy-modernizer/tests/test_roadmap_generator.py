"""Tests for modernization roadmap generation."""

from datetime import datetime
from legacy_analyzer.roadmap_generator import RoadmapGenerator
from legacy_analyzer.models import (
    StranglerFigBoundary,
    ExtractionFeasibility,
)


class TestRoadmapGenerator:
    """Test modernization roadmap generation."""

    def test_roadmap_generation(self, sample_patterns, sample_database_couplings):
        """Test basic roadmap generation."""
        generator = RoadmapGenerator()

        boundaries = [
            StranglerFigBoundary(
                boundary_name="auth_boundary",
                internal_modules=["auth/login.py", "auth/logout.py"],
                external_dependencies=["db", "cache"],
                internal_dependencies=[],
                api_surface=["auth/login.py"],
                isolation_score=0.8,
                recommended_order=1,
                estimated_effort_hours=100,
            )
        ]

        feasibilities = [
            ExtractionFeasibility(
                module_path="auth/login.py",
                feasibility_score=0.75,
                dependencies_to_break=[],
                backward_compatibility_requirements=["Maintain login API"],
                estimated_effort_hours=40,
                risks=["No test coverage"],
                recommendations=["Add tests first"],
            )
        ]

        roadmap = generator.generate_roadmap(
            "Legacy System",
            sample_patterns,
            boundaries,
            feasibilities,
            sample_database_couplings,
        )

        assert roadmap.project_name == "Legacy System"
        assert roadmap.total_duration_days > 0
        assert len(roadmap.phases) > 0
        assert len(roadmap.critical_path) > 0
        assert len(roadmap.risk_assessment) > 0
        assert len(roadmap.success_metrics) > 0
        assert isinstance(roadmap.generated_at, datetime)

    def test_foundation_phase(self, sample_patterns):
        """Test foundation phase generation."""
        generator = RoadmapGenerator()

        roadmap = generator.generate_roadmap(
            "Test Project", sample_patterns, [], [], []
        )

        # Should always have phase 1 (foundation)
        assert 1 in roadmap.phases
        foundation_milestones = roadmap.phases[1]

        # Check for essential foundation milestones
        milestone_names = [m.name for m in foundation_milestones]
        assert any("test" in name.lower() for name in milestone_names)
        assert any("document" in name.lower() for name in milestone_names)
        assert any("feature flag" in name.lower() for name in milestone_names)

    def test_database_phase(self, sample_database_couplings):
        """Test database decoupling phase generation."""
        generator = RoadmapGenerator()

        roadmap = generator.generate_roadmap(
            "Test Project", [], [], [], sample_database_couplings
        )

        # Should have database phase when couplings exist
        assert 2 in roadmap.phases
        db_milestones = roadmap.phases[2]

        # Check for database milestones
        milestone_names = [m.name for m in db_milestones]
        assert any("database" in name.lower() for name in milestone_names)

    def test_extraction_phases(self):
        """Test module extraction phase generation."""
        generator = RoadmapGenerator()

        boundaries = [
            StranglerFigBoundary(
                boundary_name=f"boundary_{i}",
                internal_modules=[f"module_{i}"],
                external_dependencies=[],
                internal_dependencies=[],
                api_surface=[],
                isolation_score=0.7,
                recommended_order=i,
                estimated_effort_hours=50,
            )
            for i in range(3)
        ]

        roadmap = generator.generate_roadmap("Test Project", [], boundaries, [], [])

        # Should have extraction phases
        extraction_phases = [p for p in roadmap.phases.keys() if p > 1]
        assert len(extraction_phases) >= len(boundaries)

    def test_cleanup_phase(self, sample_patterns):
        """Test cleanup phase generation."""
        generator = RoadmapGenerator()

        roadmap = generator.generate_roadmap(
            "Test Project", sample_patterns, [], [], []
        )

        # Should have final cleanup phase
        final_phase = max(roadmap.phases.keys())
        cleanup_milestones = roadmap.phases[final_phase]

        # Check for cleanup milestones
        milestone_names = [m.name for m in cleanup_milestones]
        assert any("optimization" in name.lower() for name in milestone_names)
        assert any("rollout" in name.lower() for name in milestone_names)

    def test_critical_path_calculation(self):
        """Test critical path calculation."""
        generator = RoadmapGenerator()

        roadmap = generator.generate_roadmap("Test Project", [], [], [], [])

        # Critical path should include key milestones
        assert len(roadmap.critical_path) > 0

        # Foundation milestones should be in critical path
        phase_1_names = [m.name for m in roadmap.phases.get(1, [])]
        assert any(name in roadmap.critical_path for name in phase_1_names)

    def test_risk_assessment(self, sample_patterns, sample_database_couplings):
        """Test risk assessment generation."""
        generator = RoadmapGenerator()

        # Add some low feasibility extractions
        low_feasibility = [
            ExtractionFeasibility(
                module_path="risky_module",
                feasibility_score=0.2,
                dependencies_to_break=["many", "dependencies"],
                backward_compatibility_requirements=[],
                estimated_effort_hours=200,
                risks=["High complexity", "No tests"],
                recommendations=[],
            )
        ]

        roadmap = generator.generate_roadmap(
            "Test Project",
            sample_patterns,
            [],
            low_feasibility,
            sample_database_couplings,
        )

        # Should identify various risks
        assert "Critical Legacy Patterns" in roadmap.risk_assessment
        assert "Database Coupling" in roadmap.risk_assessment
        assert "Extraction Difficulty" in roadmap.risk_assessment

    def test_success_metrics(self, sample_patterns):
        """Test success metrics calculation."""
        generator = RoadmapGenerator()

        boundaries = [
            StranglerFigBoundary(
                boundary_name="test_boundary",
                internal_modules=["module1", "module2"],
                external_dependencies=[],
                internal_dependencies=[],
                api_surface=[],
                isolation_score=0.9,
                recommended_order=1,
                estimated_effort_hours=50,
            )
        ]

        feasibilities = [
            ExtractionFeasibility(
                module_path="module1",
                feasibility_score=0.8,
                dependencies_to_break=[],
                backward_compatibility_requirements=[],
                estimated_effort_hours=20,
                risks=[],
                recommendations=[],
            )
        ]

        roadmap = generator.generate_roadmap(
            "Test Project", sample_patterns, boundaries, feasibilities, []
        )

        # Check success metrics
        assert "pattern_reduction_percentage" in roadmap.success_metrics
        assert "new_service_boundaries" in roadmap.success_metrics
        assert "high_feasibility_extractions" in roadmap.success_metrics
        assert "risk_reduction_potential" in roadmap.success_metrics
        assert "estimated_productivity_gain" in roadmap.success_metrics

        # Validate metric values
        assert roadmap.success_metrics["new_service_boundaries"] == 1.0
        assert roadmap.success_metrics["high_feasibility_extractions"] == 1.0

    def test_total_duration_calculation(self):
        """Test total project duration calculation."""
        generator = RoadmapGenerator()

        roadmap = generator.generate_roadmap("Test Project", [], [], [], [])

        # Calculate expected duration from all milestones
        expected_duration = 0
        for milestones in roadmap.phases.values():
            for milestone in milestones:
                expected_duration += milestone.estimated_duration_days

        assert roadmap.total_duration_days == expected_duration

    def test_milestone_dependencies(self, sample_database_couplings):
        """Test milestone dependency tracking."""
        generator = RoadmapGenerator()

        roadmap = generator.generate_roadmap(
            "Test Project", [], [], [], sample_database_couplings
        )

        # Database phase should have dependencies
        if 2 in roadmap.phases:
            db_milestones = roadmap.phases[2]

            # Later milestones might depend on earlier ones
            for i in range(1, len(db_milestones)):
                if db_milestones[i].dependencies:
                    # Dependencies should reference existing milestones
                    assert any(
                        dep in [m.name for m in db_milestones[:i]]
                        for dep in db_milestones[i].dependencies
                    )
