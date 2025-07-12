"""Tests for strangler fig pattern planning."""

from legacy_analyzer.strangler_fig_planner import StranglerFigPlanner


class TestStranglerFigPlanner:
    """Test strangler fig pattern planning functionality."""

    def test_boundary_creation(self):
        """Test creation of strangler fig boundaries."""
        planner = StranglerFigPlanner()

        # Create sample dependencies
        dependencies = {
            "module_a": {"module_b", "module_c"},
            "module_b": {"module_c"},
            "module_c": {"module_a"},  # Creates a cycle
            "module_d": {"module_e"},
            "module_e": set(),
        }

        boundaries = planner.plan_boundaries(dependencies)

        assert len(boundaries) > 0

        # Check boundary properties
        for boundary in boundaries:
            assert boundary.boundary_name
            assert len(boundary.internal_modules) > 0
            assert isinstance(boundary.isolation_score, float)
            assert 0 <= boundary.isolation_score <= 1
            assert boundary.estimated_effort_hours > 0
            assert boundary.recommended_order > 0

    def test_strongly_connected_components(self):
        """Test that SCCs are identified as boundaries."""
        planner = StranglerFigPlanner()

        # Create circular dependencies
        dependencies = {
            "service_a": {"service_b"},
            "service_b": {"service_c"},
            "service_c": {"service_a"},
            "service_d": set(),
        }

        boundaries = planner.plan_boundaries(dependencies)

        # Should find the SCC with services a, b, c
        scc_boundary = next((b for b in boundaries if "scc" in b.boundary_name), None)

        assert scc_boundary is not None
        assert len(scc_boundary.internal_modules) == 3
        assert all(
            module in scc_boundary.internal_modules
            for module in ["service_a", "service_b", "service_c"]
        )

    def test_isolation_score_calculation(self):
        """Test isolation score calculation."""
        planner = StranglerFigPlanner()

        # Highly isolated modules
        dependencies = {
            "isolated_a": {"isolated_b"},
            "isolated_b": set(),
            "external": {"isolated_a"},
        }

        boundaries = planner.plan_boundaries(dependencies)

        # Find boundary containing isolated modules
        isolated_boundary = next(
            (
                b
                for b in boundaries
                if "isolated_a" in b.internal_modules
                and "isolated_b" in b.internal_modules
            ),
            None,
        )

        if isolated_boundary:
            # Should have good isolation (few external deps)
            assert isolated_boundary.isolation_score > 0.5

    def test_api_surface_identification(self):
        """Test identification of API surface modules."""
        planner = StranglerFigPlanner()

        # Module 'api' is used by external modules
        dependencies = {"api": {"internal"}, "internal": set(), "external": {"api"}}

        boundaries = planner.plan_boundaries(dependencies)

        # Find boundary with api module
        api_boundary = next(
            (b for b in boundaries if "api" in b.internal_modules), None
        )

        if api_boundary:
            # 'api' should be in API surface if external uses it
            if "external" not in api_boundary.internal_modules:
                assert "api" in api_boundary.api_surface

    def test_boundary_prioritization(self):
        """Test that boundaries are properly prioritized."""
        planner = StranglerFigPlanner()

        dependencies = {
            "easy_a": set(),
            "easy_b": {"easy_a"},
            "hard_a": {"hard_b", "hard_c", "external_1", "external_2"},
            "hard_b": {"hard_a", "external_3"},
            "hard_c": {"hard_a"},
            "external_1": set(),
            "external_2": set(),
            "external_3": set(),
        }

        boundaries = planner.plan_boundaries(dependencies)

        # Boundaries should be ordered by recommended_order
        sorted_boundaries = sorted(boundaries, key=lambda b: b.recommended_order)

        for i, boundary in enumerate(sorted_boundaries):
            assert boundary.recommended_order == i + 1

        # Easier boundaries (higher isolation) should come first
        if len(sorted_boundaries) >= 2:
            assert (
                sorted_boundaries[0].isolation_score
                >= sorted_boundaries[-1].isolation_score
            )

    def test_effort_estimation(self):
        """Test effort estimation for boundaries."""
        planner = StranglerFigPlanner()

        # Complex dependencies
        dependencies = {
            f"module_{i}": {f"module_{j}" for j in range(5) if j != i} for i in range(5)
        }

        boundaries = planner.plan_boundaries(dependencies)

        for boundary in boundaries:
            # Effort should be proportional to complexity
            assert boundary.estimated_effort_hours > 0

            # More modules = more effort
            if len(boundary.internal_modules) > 3:
                assert boundary.estimated_effort_hours > 50

            # More external dependencies = more effort
            if len(boundary.external_dependencies) > 5:
                assert boundary.estimated_effort_hours > 40

    def test_empty_dependencies(self):
        """Test handling of empty dependencies."""
        planner = StranglerFigPlanner()
        boundaries = planner.plan_boundaries({})

        assert isinstance(boundaries, list)
        assert len(boundaries) == 0

    def test_single_module(self):
        """Test handling of single module with no dependencies."""
        planner = StranglerFigPlanner()
        dependencies = {"lonely_module": set()}

        boundaries = planner.plan_boundaries(dependencies)

        # Single modules might not form boundaries
        assert isinstance(boundaries, list)
