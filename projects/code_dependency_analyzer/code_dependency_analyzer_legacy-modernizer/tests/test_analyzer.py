"""Tests for the main Legacy Analyzer."""

import pytest
import time
from legacy_analyzer import LegacyAnalyzer


class TestLegacyAnalyzer:
    """Test the main analyzer functionality."""

    def test_complete_analysis(self, temp_codebase):
        """Test complete codebase analysis."""
        analyzer = LegacyAnalyzer()
        result = analyzer.analyze_codebase(temp_codebase)

        # Check all components are present
        assert result.legacy_patterns is not None
        assert result.database_couplings is not None
        assert result.strangler_boundaries is not None
        assert result.extraction_feasibilities is not None
        assert result.modernization_roadmap is not None
        assert result.summary is not None
        assert result.analysis_duration_seconds > 0

        # Check that patterns were found
        assert len(result.legacy_patterns) > 0

        # Check summary structure
        assert "total_modules" in result.summary
        assert "total_lines_of_code" in result.summary
        assert "patterns_found" in result.summary
        assert "database_coupling" in result.summary
        assert "strangler_boundaries" in result.summary
        assert "extraction_feasibility" in result.summary

    def test_analysis_without_roadmap(self, temp_codebase):
        """Test analysis without roadmap generation."""
        analyzer = LegacyAnalyzer()
        result = analyzer.analyze_codebase(temp_codebase, generate_roadmap=False)

        assert result.modernization_roadmap is None
        assert result.legacy_patterns is not None
        assert result.database_couplings is not None

    def test_specific_module_extraction(self, temp_codebase):
        """Test analyzing specific modules for extraction."""
        analyzer = LegacyAnalyzer()

        # Get some module paths from the temp codebase
        modules_to_extract = [
            "legacy_app/models/user.py",
            "legacy_app/services/order_service.py",
        ]

        result = analyzer.analyze_codebase(
            temp_codebase, modules_to_extract=modules_to_extract
        )

        # Should analyze only specified modules
        analyzed_paths = [f.module_path for f in result.extraction_feasibilities]

        # At least one of our requested modules should be analyzed
        assert any(module in analyzed_paths for module in modules_to_extract)

    def test_nonexistent_path(self):
        """Test handling of nonexistent path."""
        analyzer = LegacyAnalyzer()

        with pytest.raises(ValueError, match="does not exist"):
            analyzer.analyze_codebase("/nonexistent/path")

    def test_file_instead_of_directory(self, tmp_path):
        """Test handling of file path instead of directory."""
        analyzer = LegacyAnalyzer()

        # Create a file
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        with pytest.raises(ValueError, match="not a directory"):
            analyzer.analyze_codebase(str(test_file))

    def test_empty_codebase(self, tmp_path):
        """Test analysis of empty codebase."""
        analyzer = LegacyAnalyzer()
        result = analyzer.analyze_codebase(str(tmp_path))

        assert len(result.legacy_patterns) == 0
        assert len(result.database_couplings) == 0
        assert result.summary["total_modules"] == 0
        assert result.summary["total_lines_of_code"] == 0

    def test_performance_benchmark(self, temp_codebase):
        """Test that analysis completes within reasonable time."""
        analyzer = LegacyAnalyzer()

        start_time = time.time()
        result = analyzer.analyze_codebase(temp_codebase)
        duration = time.time() - start_time

        # Should complete small codebase analysis quickly
        assert duration < 10  # 10 seconds for small codebase

        # Duration should match reported duration
        assert abs(result.analysis_duration_seconds - duration) < 0.1

    def test_summary_statistics(self, temp_codebase):
        """Test summary statistics calculation."""
        analyzer = LegacyAnalyzer()
        result = analyzer.analyze_codebase(temp_codebase)

        summary = result.summary

        # Patterns summary
        patterns_summary = summary["patterns_found"]
        assert patterns_summary["total"] == len(result.legacy_patterns)

        # Count by type should sum to total
        type_count = sum(patterns_summary["by_type"].values())
        assert type_count == patterns_summary["total"]

        # Database coupling summary
        db_summary = summary["database_coupling"]
        assert db_summary["total_couplings"] == len(result.database_couplings)

        # Strangler boundaries summary
        boundary_summary = summary["strangler_boundaries"]
        assert boundary_summary["total"] == len(result.strangler_boundaries)

        # Effort should be sum of all boundaries
        total_effort = sum(
            b.estimated_effort_hours for b in result.strangler_boundaries
        )
        assert boundary_summary["total_effort_hours"] == total_effort

    def test_pattern_type_counts(self, temp_codebase):
        """Test pattern counting by type."""
        analyzer = LegacyAnalyzer()
        result = analyzer.analyze_codebase(temp_codebase)

        # Manually count patterns by type
        type_counts = {}
        for pattern in result.legacy_patterns:
            pattern_type = pattern.pattern_type.value
            type_counts[pattern_type] = type_counts.get(pattern_type, 0) + 1

        # Compare with summary
        summary_counts = result.summary["patterns_found"]["by_type"]
        assert type_counts == summary_counts

    def test_integration_with_all_components(self, temp_codebase):
        """Test that all components work together."""
        analyzer = LegacyAnalyzer()
        result = analyzer.analyze_codebase(temp_codebase)

        # Patterns should reference real files
        for pattern in result.legacy_patterns:
            assert any(
                pattern.module_path in path or path in pattern.affected_files
                for path in analyzer.pattern_detector.module_metrics.keys()
            )

        # Database couplings should reference real modules
        for coupling in result.database_couplings:
            for module in coupling.coupled_modules:
                assert any(
                    module in path
                    for path in analyzer.pattern_detector.module_metrics.keys()
                )

        # Roadmap should reference found issues
        if result.modernization_roadmap:
            # Check that roadmap addresses real patterns
            risk_assessment = result.modernization_roadmap.risk_assessment

            if any(p.risk.value == "critical" for p in result.legacy_patterns):
                assert "Critical Legacy Patterns" in risk_assessment
