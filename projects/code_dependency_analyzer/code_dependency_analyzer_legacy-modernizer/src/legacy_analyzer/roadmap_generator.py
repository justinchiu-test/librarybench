"""Modernization roadmap generator."""

from datetime import datetime
from typing import Dict, List

from .models import (
    ModernizationRoadmap,
    ModernizationMilestone,
    RiskLevel,
    LegacyPattern,
    StranglerFigBoundary,
    ExtractionFeasibility,
    DatabaseCoupling,
)


class RoadmapGenerator:
    """Generates phased modernization roadmaps."""

    def __init__(self) -> None:
        self.phases: Dict[int, List[ModernizationMilestone]] = {}

    def generate_roadmap(
        self,
        project_name: str,
        patterns: List[LegacyPattern],
        boundaries: List[StranglerFigBoundary],
        feasibilities: List[ExtractionFeasibility],
        database_couplings: List[DatabaseCoupling],
    ) -> ModernizationRoadmap:
        """Generate a comprehensive modernization roadmap."""
        self.phases.clear()

        # Phase 1: Foundation and preparation
        self._generate_foundation_phase(patterns, database_couplings)

        # Phase 2: Database decoupling
        if database_couplings:
            self._generate_database_phase(database_couplings)

        # Phase 3-N: Module extraction phases
        self._generate_extraction_phases(boundaries, feasibilities)

        # Final phase: Cleanup and optimization
        self._generate_cleanup_phase(patterns)

        # Calculate critical path
        critical_path = self._calculate_critical_path()

        # Generate risk assessment
        risk_assessment = self._generate_risk_assessment(
            patterns, boundaries, feasibilities, database_couplings
        )

        # Calculate success metrics
        success_metrics = self._calculate_success_metrics(
            patterns, boundaries, feasibilities
        )

        # Calculate total duration
        total_duration = sum(
            milestone.estimated_duration_days
            for milestones in self.phases.values()
            for milestone in milestones
        )

        return ModernizationRoadmap(
            project_name=project_name,
            total_duration_days=total_duration,
            phases=self.phases,
            critical_path=critical_path,
            risk_assessment=risk_assessment,
            success_metrics=success_metrics,
            generated_at=datetime.now(),
        )

    def _generate_foundation_phase(
        self, patterns: List[LegacyPattern], database_couplings: List[DatabaseCoupling]
    ) -> None:
        """Generate foundation phase milestones."""
        phase_milestones = []

        # Test infrastructure setup
        phase_milestones.append(
            ModernizationMilestone(
                name="Establish comprehensive test coverage",
                description="Create unit and integration tests for critical paths",
                phase=1,
                deliverables=[
                    "Test framework setup",
                    "Critical path test coverage > 80%",
                    "CI/CD pipeline with test automation",
                ],
                estimated_duration_days=90,  # Increased for large systems
                risk_level=RiskLevel.LOW,
            )
        )

        # Documentation milestone
        phase_milestones.append(
            ModernizationMilestone(
                name="Document current architecture",
                description="Create comprehensive documentation of current system",
                phase=1,
                deliverables=[
                    "Architecture diagrams",
                    "Dependency maps",
                    "Data flow documentation",
                    "API documentation",
                ],
                estimated_duration_days=60,
                risk_level=RiskLevel.LOW,
            )
        )

        # Quick wins based on patterns
        quick_win_patterns = [
            p for p in patterns if p.difficulty.value == "low" and p.risk.value == "low"
        ]
        if quick_win_patterns:
            phase_milestones.append(
                ModernizationMilestone(
                    name="Address low-risk legacy patterns",
                    description="Fix easy-to-resolve legacy patterns for quick wins",
                    phase=1,
                    deliverables=[
                        f"Resolve {len(quick_win_patterns)} low-risk patterns",
                        "Improve code quality metrics",
                    ],
                    estimated_duration_days=max(90, len(quick_win_patterns) * 15),
                    risk_level=RiskLevel.LOW,
                )
            )

        # Feature flag infrastructure
        phase_milestones.append(
            ModernizationMilestone(
                name="Implement feature flag system",
                description="Setup feature flags for safe gradual rollout",
                phase=1,
                deliverables=[
                    "Feature flag framework",
                    "Management interface",
                    "Integration with deployment pipeline",
                ],
                estimated_duration_days=90,
                risk_level=RiskLevel.MEDIUM,
            )
        )

        self.phases[1] = phase_milestones

    def _generate_database_phase(
        self, database_couplings: List[DatabaseCoupling]
    ) -> None:
        """Generate database decoupling phase."""
        phase_milestones = []
        phase_num = 2

        # Group couplings by strength
        high_coupling = [c for c in database_couplings if c.coupling_strength > 0.7]
        medium_coupling = [
            c for c in database_couplings if 0.3 < c.coupling_strength <= 0.7
        ]

        if high_coupling:
            phase_milestones.append(
                ModernizationMilestone(
                    name="Decouple high-strength database dependencies",
                    description="Address most critical database coupling issues",
                    phase=phase_num,
                    deliverables=[
                        f"Decouple {len(high_coupling)} high-strength couplings",
                        "Implement repository pattern",
                        "Create database abstraction layer",
                    ],
                    estimated_duration_days=sum(
                        c.decoupling_effort_hours / 8 for c in high_coupling
                    ),
                    risk_level=RiskLevel.HIGH,
                )
            )

        if medium_coupling:
            phase_milestones.append(
                ModernizationMilestone(
                    name="Address medium database couplings",
                    description="Reduce remaining database dependencies",
                    phase=phase_num,
                    dependencies=["Decouple high-strength database dependencies"]
                    if high_coupling
                    else [],
                    deliverables=[
                        f"Resolve {len(medium_coupling)} medium couplings",
                        "Standardize data access patterns",
                    ],
                    estimated_duration_days=sum(
                        c.decoupling_effort_hours / 8 for c in medium_coupling
                    ),
                    risk_level=RiskLevel.MEDIUM,
                )
            )

        # Raw SQL migration
        raw_sql_modules = [c for c in database_couplings if c.raw_sql_queries]
        if raw_sql_modules:
            phase_milestones.append(
                ModernizationMilestone(
                    name="Migrate raw SQL to ORM",
                    description="Replace raw SQL queries with ORM or query builder",
                    phase=phase_num,
                    deliverables=[
                        "Migrate all raw SQL queries",
                        "Implement query optimization",
                        "Add query performance monitoring",
                    ],
                    estimated_duration_days=len(raw_sql_modules) * 5,
                    risk_level=RiskLevel.MEDIUM,
                )
            )

        if phase_milestones:
            self.phases[phase_num] = phase_milestones

    def _generate_extraction_phases(
        self,
        boundaries: List[StranglerFigBoundary],
        feasibilities: List[ExtractionFeasibility],
    ) -> None:
        """Generate module extraction phases."""
        base_phase = max(self.phases.keys()) + 1 if self.phases else 1

        # Group boundaries by recommended order
        for idx, boundary in enumerate(boundaries[:5]):  # Limit to top 5 boundaries
            phase_num = base_phase + idx
            phase_milestones = []

            # Main extraction milestone
            phase_milestones.append(
                ModernizationMilestone(
                    name=f"Extract {boundary.boundary_name} boundary",
                    description=f"Implement strangler fig pattern for {len(boundary.internal_modules)} modules",
                    phase=phase_num,
                    deliverables=[
                        f"Extract {len(boundary.internal_modules)} modules",
                        "Create new service boundary",
                        "Implement API gateway if needed",
                        "Migrate dependent systems",
                    ],
                    estimated_duration_days=max(
                        30, boundary.estimated_effort_hours / 8
                    ),  # Minimum 30 days per boundary
                    risk_level=RiskLevel.HIGH
                    if boundary.isolation_score < 0.5
                    else RiskLevel.MEDIUM,
                )
            )

            # Add feasibility-based extractions for modules in this boundary
            relevant_feasibilities = [
                f
                for f in feasibilities
                if f.module_path in boundary.internal_modules
                and f.feasibility_score > 0.5
            ]

            for feasibility in relevant_feasibilities[:3]:  # Top 3 feasible modules
                phase_milestones.append(
                    ModernizationMilestone(
                        name=f"Extract module: {feasibility.module_path}",
                        description=f"Extract module with {feasibility.feasibility_score:.2f} feasibility score",
                        phase=phase_num,
                        dependencies=[f"Extract {boundary.boundary_name} boundary"],
                        deliverables=feasibility.recommendations[:3],
                        estimated_duration_days=feasibility.estimated_effort_hours / 8,
                        risk_level=RiskLevel.HIGH
                        if feasibility.feasibility_score < 0.6
                        else RiskLevel.MEDIUM,
                    )
                )

            if phase_milestones:
                self.phases[phase_num] = phase_milestones

    def _generate_cleanup_phase(self, patterns: List[LegacyPattern]) -> None:
        """Generate final cleanup and optimization phase."""
        final_phase = max(self.phases.keys()) + 1 if self.phases else 1
        phase_milestones = []

        # Address remaining high-risk patterns
        remaining_patterns = [
            p
            for p in patterns
            if p.risk.value in ["high", "critical"] and p.difficulty.value != "critical"
        ]

        if remaining_patterns:
            phase_milestones.append(
                ModernizationMilestone(
                    name="Address remaining legacy patterns",
                    description="Clean up remaining technical debt",
                    phase=final_phase,
                    deliverables=[
                        f"Resolve {len(remaining_patterns)} remaining patterns",
                        "Improve overall code quality",
                    ],
                    estimated_duration_days=len(remaining_patterns) * 5,
                    risk_level=RiskLevel.MEDIUM,
                )
            )

        # Performance optimization
        phase_milestones.append(
            ModernizationMilestone(
                name="Performance optimization",
                description="Optimize system performance post-modernization",
                phase=final_phase,
                deliverables=[
                    "Performance benchmarking",
                    "Query optimization",
                    "Caching implementation",
                    "Load testing",
                ],
                estimated_duration_days=120,
                risk_level=RiskLevel.LOW,
            )
        )

        # Final migration
        phase_milestones.append(
            ModernizationMilestone(
                name="Complete modernization rollout",
                description="Full production rollout of modernized system",
                phase=final_phase,
                deliverables=[
                    "Production deployment",
                    "Legacy system decommissioning plan",
                    "Knowledge transfer documentation",
                    "Post-modernization support plan",
                ],
                estimated_duration_days=90,
                risk_level=RiskLevel.MEDIUM,
            )
        )

        self.phases[final_phase] = phase_milestones

    def _calculate_critical_path(self) -> List[str]:
        """Calculate the critical path through the roadmap."""
        critical_path = []

        # Add foundation milestones (always critical)
        if 1 in self.phases:
            critical_path.extend([m.name for m in self.phases[1]])

        # Add database decoupling if present
        if 2 in self.phases:
            critical_path.append(self.phases[2][0].name)

        # Add first extraction from each phase
        for phase_num in sorted(self.phases.keys())[2:]:
            if self.phases[phase_num]:
                critical_path.append(self.phases[phase_num][0].name)

        return critical_path

    def _generate_risk_assessment(
        self,
        patterns: List[LegacyPattern],
        boundaries: List[StranglerFigBoundary],
        feasibilities: List[ExtractionFeasibility],
        database_couplings: List[DatabaseCoupling],
    ) -> Dict[str, str]:
        """Generate risk assessment for the modernization project."""
        assessment = {}

        # Pattern-based risks
        critical_patterns = [p for p in patterns if p.risk.value == "critical"]
        if critical_patterns:
            assessment["Critical Legacy Patterns"] = (
                f"{len(critical_patterns)} critical patterns identified that could "
                "block modernization if not addressed early"
            )

        # Coupling risks
        high_coupling = [c for c in database_couplings if c.coupling_strength > 0.8]
        if high_coupling:
            assessment["Database Coupling"] = (
                f"{len(high_coupling)} instances of high database coupling that "
                "require careful decoupling strategy"
            )
        elif database_couplings:
            assessment["Database Coupling"] = (
                f"{len(database_couplings)} database coupling instances found that "
                "should be addressed during modernization"
            )

        # Extraction risks
        low_feasibility = [f for f in feasibilities if f.feasibility_score < 0.3]
        if low_feasibility:
            assessment["Extraction Difficulty"] = (
                f"{len(low_feasibility)} modules with low extraction feasibility "
                "may require significant refactoring"
            )

        # Boundary risks
        low_isolation = [b for b in boundaries if b.isolation_score < 0.4]
        if low_isolation:
            assessment["Boundary Definition"] = (
                f"{len(low_isolation)} proposed boundaries have low isolation scores "
                "and may be difficult to implement"
            )

        # General risks
        assessment["Testing Coverage"] = (
            "Comprehensive test coverage must be established before major refactoring"
        )
        assessment["Team Knowledge"] = (
            "Team requires training on new architectural patterns and tools"
        )

        return assessment

    def _calculate_success_metrics(
        self,
        patterns: List[LegacyPattern],
        boundaries: List[StranglerFigBoundary],
        feasibilities: List[ExtractionFeasibility],
    ) -> Dict[str, float]:
        """Calculate expected success metrics."""
        metrics = {}

        # Pattern reduction
        total_patterns = len(patterns)
        addressable_patterns = len(
            [p for p in patterns if p.difficulty.value != "critical"]
        )
        metrics["pattern_reduction_percentage"] = (
            (addressable_patterns / total_patterns * 100) if total_patterns > 0 else 0
        )

        # Modularity improvement
        metrics["new_service_boundaries"] = float(len(boundaries))

        # Extraction success rate
        high_feasibility = len([f for f in feasibilities if f.feasibility_score > 0.7])
        metrics["high_feasibility_extractions"] = float(high_feasibility)

        # Risk reduction
        high_risk_patterns = len(
            [p for p in patterns if p.risk.value in ["high", "critical"]]
        )
        metrics["risk_reduction_potential"] = 70.0 if high_risk_patterns > 5 else 40.0

        # Estimated productivity improvement
        metrics["estimated_productivity_gain"] = 40.0  # Conservative estimate

        return metrics
