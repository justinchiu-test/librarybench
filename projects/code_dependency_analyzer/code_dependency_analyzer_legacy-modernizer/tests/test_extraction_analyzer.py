"""Tests for module extraction feasibility analysis."""

from legacy_analyzer.extraction_analyzer import ExtractionAnalyzer


class TestExtractionAnalyzer:
    """Test module extraction feasibility analysis."""

    def test_feasibility_analysis(self, sample_patterns, sample_database_couplings):
        """Test basic feasibility analysis."""
        analyzer = ExtractionAnalyzer()

        dependencies = {
            "module_a": {"module_b", "module_c"},
            "module_b": {"module_c"},
            "module_c": set(),
        }

        feasibility = analyzer.analyze_extraction_feasibility(
            "module_a", dependencies, sample_patterns, sample_database_couplings
        )

        assert feasibility.module_path == "module_a"
        assert 0 <= feasibility.feasibility_score <= 1
        assert isinstance(feasibility.dependencies_to_break, list)
        assert isinstance(feasibility.backward_compatibility_requirements, list)
        assert feasibility.estimated_effort_hours > 0
        assert isinstance(feasibility.risks, list)
        assert isinstance(feasibility.recommendations, list)

    def test_circular_dependency_detection(self):
        """Test detection of dependencies to break."""
        analyzer = ExtractionAnalyzer()

        # Circular dependency
        dependencies = {"module_a": {"module_b"}, "module_b": {"module_a"}}

        feasibility = analyzer.analyze_extraction_feasibility(
            "module_a", dependencies, [], []
        )

        # Should identify the circular dependency
        assert len(feasibility.dependencies_to_break) > 0
        assert any(
            "module_a" in dep and "module_b" in dep
            for dep in feasibility.dependencies_to_break
        )

    def test_backward_compatibility_requirements(self):
        """Test identification of backward compatibility needs."""
        analyzer = ExtractionAnalyzer()

        # Module used by others
        dependencies = {
            "api_module": set(),
            "client_1": {"api_module"},
            "client_2": {"api_module"},
            "client_3": {"api_module"},
        }

        feasibility = analyzer.analyze_extraction_feasibility(
            "api_module", dependencies, [], []
        )

        # Should identify need for backward compatibility
        assert len(feasibility.backward_compatibility_requirements) > 0
        assert any(
            "3 dependent modules" in req
            for req in feasibility.backward_compatibility_requirements
        )

    def test_risk_identification(self, sample_patterns, sample_database_couplings):
        """Test risk identification."""
        analyzer = ExtractionAnalyzer()

        dependencies = {"models/user.py": set()}

        feasibility = analyzer.analyze_extraction_feasibility(
            "models/user.py", dependencies, sample_patterns, sample_database_couplings
        )

        # Should identify risks from patterns
        assert len(feasibility.risks) > 0
        assert any("god_class" in risk for risk in feasibility.risks)

    def test_recommendations_generation(self):
        """Test generation of extraction recommendations."""
        analyzer = ExtractionAnalyzer()

        dependencies = {"complex_module": {"dep1", "dep2", "dep3"}}

        module_metrics = {"complex_module": {"lines_of_code": 1000, "complexity": 50}}

        feasibility = analyzer.analyze_extraction_feasibility(
            "complex_module", dependencies, [], [], module_metrics
        )

        # Should recommend breaking into smaller modules
        assert any("smaller modules" in rec for rec in feasibility.recommendations)

        # Should recommend reducing complexity
        assert any("complexity" in rec for rec in feasibility.recommendations)

    def test_feasibility_score_calculation(self, sample_patterns):
        """Test feasibility score calculation logic."""
        analyzer = ExtractionAnalyzer()

        # Simple module with few issues
        simple_deps = {"simple_module": set()}
        simple_feasibility = analyzer.analyze_extraction_feasibility(
            "simple_module", simple_deps, [], []
        )

        # Complex module with many issues
        complex_deps = {
            "models/user.py": {"a", "b", "c"},
            "a": {"models/user.py"},  # Circular
            "b": set(),
            "c": set(),
        }
        complex_feasibility = analyzer.analyze_extraction_feasibility(
            "models/user.py", complex_deps, sample_patterns, []
        )

        # Simple module should have higher feasibility
        assert (
            simple_feasibility.feasibility_score > complex_feasibility.feasibility_score
        )

    def test_effort_estimation_factors(self):
        """Test that effort estimation considers various factors."""
        analyzer = ExtractionAnalyzer()

        # Small module
        small_deps = {"small": set()}
        small_metrics = {"small": {"lines_of_code": 100, "complexity": 5}}

        small_feasibility = analyzer.analyze_extraction_feasibility(
            "small", small_deps, [], [], small_metrics
        )

        # Large module
        large_deps = {
            "large": {"a", "b", "c", "d", "e"},
            "a": {"large"},  # Bidirectional
            "b": set(),
            "c": set(),
            "d": set(),
            "e": set(),
        }
        large_metrics = {"large": {"lines_of_code": 2000, "complexity": 100}}

        large_feasibility = analyzer.analyze_extraction_feasibility(
            "large", large_deps, [], [], large_metrics
        )

        # Large module should require more effort
        assert (
            large_feasibility.estimated_effort_hours
            > small_feasibility.estimated_effort_hours
        )

    def test_analyze_multiple_modules(self, sample_patterns, sample_database_couplings):
        """Test analyzing multiple modules at once."""
        analyzer = ExtractionAnalyzer()

        dependencies = {
            "module_a": {"module_b"},
            "module_b": {"module_c"},
            "module_c": set(),
            "module_d": set(),
        }

        results = analyzer.analyze_multiple_modules(
            ["module_a", "module_b", "module_c", "module_d"],
            dependencies,
            sample_patterns,
            sample_database_couplings,
        )

        assert len(results) == 4

        # Results should be sorted by feasibility score
        for i in range(len(results) - 1):
            assert results[i].feasibility_score >= results[i + 1].feasibility_score

    def test_nonexistent_module(self):
        """Test handling of nonexistent module."""
        analyzer = ExtractionAnalyzer()

        dependencies = {"existing": set()}

        results = analyzer.analyze_multiple_modules(
            ["existing", "nonexistent"], dependencies, [], []
        )

        # Should only analyze existing modules
        assert len(results) == 1
        assert results[0].module_path == "existing"
