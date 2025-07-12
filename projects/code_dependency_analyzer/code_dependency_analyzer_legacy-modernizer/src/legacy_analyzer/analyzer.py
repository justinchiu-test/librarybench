"""Main Legacy System Modernization Analyzer."""

import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import AnalysisResult
from .pattern_detector import PatternDetector
from .database_coupling_detector import DatabaseCouplingDetector
from .strangler_fig_planner import StranglerFigPlanner
from .extraction_analyzer import ExtractionAnalyzer
from .roadmap_generator import RoadmapGenerator


class LegacyAnalyzer:
    """Main analyzer that orchestrates all analysis components."""

    def __init__(self) -> None:
        self.pattern_detector = PatternDetector()
        self.db_coupling_detector = DatabaseCouplingDetector()
        self.strangler_planner = StranglerFigPlanner()
        self.extraction_analyzer = ExtractionAnalyzer()
        self.roadmap_generator = RoadmapGenerator()

    def analyze_codebase(
        self,
        root_path: str,
        generate_roadmap: bool = True,
        modules_to_extract: Optional[List[str]] = None,
    ) -> AnalysisResult:
        """Perform complete analysis of a legacy codebase."""
        start_time = time.time()

        # Ensure root_path exists
        root = Path(root_path)
        if not root.exists():
            raise ValueError(f"Root path does not exist: {root_path}")
        if not root.is_dir():
            raise ValueError(f"Root path is not a directory: {root_path}")

        # Phase 1: Detect legacy patterns
        patterns = self.pattern_detector.analyze_codebase(root_path)

        # Get dependencies and metrics from pattern detector
        dependencies = self.pattern_detector.dependencies
        module_metrics = self.pattern_detector.module_metrics

        # Phase 2: Detect database coupling
        database_couplings = self.db_coupling_detector.analyze_database_coupling(
            root_path
        )

        # Phase 3: Plan strangler fig boundaries
        strangler_boundaries = self.strangler_planner.plan_boundaries(
            dependencies, module_metrics
        )

        # Phase 4: Analyze extraction feasibility
        extraction_feasibilities = []
        if modules_to_extract:
            # Analyze specific modules
            extraction_feasibilities = (
                self.extraction_analyzer.analyze_multiple_modules(
                    modules_to_extract,
                    dependencies,
                    patterns,
                    database_couplings,
                    module_metrics,
                )
            )
        else:
            # Analyze all modules
            all_modules = list(dependencies.keys())
            extraction_feasibilities = (
                self.extraction_analyzer.analyze_multiple_modules(
                    all_modules[:20],  # Limit to top 20 modules for performance
                    dependencies,
                    patterns,
                    database_couplings,
                    module_metrics,
                )
            )

        # Phase 5: Generate modernization roadmap
        modernization_roadmap = None
        if generate_roadmap:
            modernization_roadmap = self.roadmap_generator.generate_roadmap(
                project_name=Path(root_path).name,
                patterns=patterns,
                boundaries=strangler_boundaries,
                feasibilities=extraction_feasibilities,
                database_couplings=database_couplings,
            )

        # Calculate summary statistics
        summary = self._generate_summary(
            patterns,
            database_couplings,
            strangler_boundaries,
            extraction_feasibilities,
            module_metrics,
        )

        # Calculate analysis duration
        duration = time.time() - start_time

        return AnalysisResult(
            legacy_patterns=patterns,
            database_couplings=database_couplings,
            strangler_boundaries=strangler_boundaries,
            extraction_feasibilities=extraction_feasibilities,
            modernization_roadmap=modernization_roadmap,
            summary=summary,
            analysis_duration_seconds=duration,
        )

    def _generate_summary(
        self,
        patterns,
        database_couplings,
        strangler_boundaries,
        extraction_feasibilities,
        module_metrics,
    ) -> Dict[str, Any]:
        """Generate analysis summary."""
        summary = {
            "total_modules": len(module_metrics),
            "total_lines_of_code": sum(
                m.get("lines_of_code", 0) for m in module_metrics.values()
            ),
            "patterns_found": {
                "total": len(patterns),
                "by_type": {},
                "by_difficulty": {},
                "by_risk": {},
            },
            "database_coupling": {
                "total_couplings": len(database_couplings),
                "high_coupling_count": len(
                    [c for c in database_couplings if c.coupling_strength > 0.7]
                ),
                "modules_with_raw_sql": len(
                    [c for c in database_couplings if c.raw_sql_queries]
                ),
            },
            "strangler_boundaries": {
                "total": len(strangler_boundaries),
                "high_isolation": len(
                    [b for b in strangler_boundaries if b.isolation_score > 0.7]
                ),
                "total_effort_hours": sum(
                    b.estimated_effort_hours for b in strangler_boundaries
                ),
            },
            "extraction_feasibility": {
                "total_analyzed": len(extraction_feasibilities),
                "high_feasibility": len(
                    [f for f in extraction_feasibilities if f.feasibility_score > 0.7]
                ),
                "low_feasibility": len(
                    [f for f in extraction_feasibilities if f.feasibility_score < 0.3]
                ),
            },
        }

        # Count patterns by type
        for pattern in patterns:
            pattern_type = pattern.pattern_type.value
            summary["patterns_found"]["by_type"][pattern_type] = (
                summary["patterns_found"]["by_type"].get(pattern_type, 0) + 1
            )

        # Count patterns by difficulty
        for pattern in patterns:
            difficulty = pattern.difficulty.value
            summary["patterns_found"]["by_difficulty"][difficulty] = (
                summary["patterns_found"]["by_difficulty"].get(difficulty, 0) + 1
            )

        # Count patterns by risk
        for pattern in patterns:
            risk = pattern.risk.value
            summary["patterns_found"]["by_risk"][risk] = (
                summary["patterns_found"]["by_risk"].get(risk, 0) + 1
            )

        return summary
