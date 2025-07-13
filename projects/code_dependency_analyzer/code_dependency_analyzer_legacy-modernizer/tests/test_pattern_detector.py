"""Tests for legacy pattern detection."""

from legacy_analyzer.pattern_detector import PatternDetector
from legacy_analyzer.models import PatternType


class TestPatternDetector:
    """Test legacy pattern detection functionality."""

    def test_detect_god_class(self, temp_codebase):
        """Test detection of god class anti-pattern."""
        detector = PatternDetector()
        patterns = detector.analyze_codebase(temp_codebase)

        # Find god class patterns
        god_classes = [p for p in patterns if p.pattern_type == PatternType.GOD_CLASS]

        assert len(god_classes) > 0
        assert any("user.py" in p.module_path for p in god_classes)

        # Check pattern details
        user_pattern = next(p for p in god_classes if "user.py" in p.module_path)
        assert user_pattern.difficulty.value in ["medium", "high"]
        assert user_pattern.risk.value in ["medium", "high"]
        assert user_pattern.metrics.get("avg_methods_per_class", 0) > 20

    def test_detect_circular_dependencies(self, temp_codebase):
        """Test detection of circular dependencies."""
        detector = PatternDetector()
        patterns = detector.analyze_codebase(temp_codebase)

        # Find circular dependency patterns
        circular_deps = [
            p for p in patterns if p.pattern_type == PatternType.CIRCULAR_DEPENDENCY
        ]

        # We have order_service <-> payment_service circular dependency
        assert len(circular_deps) >= 1
        assert any("order_service" in p.module_path for p in circular_deps)
        assert any("payment_service" in p.module_path for p in circular_deps)

        # Check severity
        for pattern in circular_deps:
            assert pattern.difficulty.value == "critical"
            assert pattern.risk.value == "critical"

    def test_detect_spaghetti_dependencies(self, temp_codebase):
        """Test detection of spaghetti dependencies."""
        detector = PatternDetector()
        patterns = detector.analyze_codebase(temp_codebase)

        # Find spaghetti dependency patterns
        spaghetti = [
            p for p in patterns if p.pattern_type == PatternType.SPAGHETTI_DEPENDENCY
        ]

        assert len(spaghetti) > 0
        assert any("helpers.py" in p.module_path for p in spaghetti)

        # Check that it detected many dependencies
        helpers_pattern = next(p for p in spaghetti if "helpers.py" in p.module_path)
        assert helpers_pattern.metrics["dependency_count"] > 15

    def test_detect_feature_envy(self, temp_codebase):
        """Test detection of feature envy pattern."""
        detector = PatternDetector()
        patterns = detector.analyze_codebase(temp_codebase)

        # Find feature envy patterns
        feature_envy = [
            p for p in patterns if p.pattern_type == PatternType.FEATURE_ENVY
        ]

        assert len(feature_envy) > 0
        assert any("report_generator.py" in p.module_path for p in feature_envy)

    def test_detect_monolithic_structure(self, temp_codebase):
        """Test detection of monolithic structure."""
        detector = PatternDetector()
        patterns = detector.analyze_codebase(temp_codebase)

        # Find monolithic patterns
        monolithic = [
            p for p in patterns if p.pattern_type == PatternType.MONOLITHIC_STRUCTURE
        ]

        # Our test codebase is small but has concentrated code
        if monolithic:
            pattern = monolithic[0]
            assert pattern.difficulty.value == "critical"
            assert pattern.risk.value == "critical"

    def test_empty_codebase(self, tmp_path):
        """Test handling of empty codebase."""
        detector = PatternDetector()
        patterns = detector.analyze_codebase(str(tmp_path))

        assert isinstance(patterns, list)
        assert len(patterns) == 0

    def test_metrics_collection(self, temp_codebase):
        """Test that metrics are properly collected."""
        detector = PatternDetector()
        patterns = detector.analyze_codebase(temp_codebase)

        assert len(detector.module_metrics) > 0

        # Check that metrics contain expected fields
        for module, metrics in detector.module_metrics.items():
            assert "lines_of_code" in metrics
            assert "num_classes" in metrics
            assert "num_functions" in metrics
            assert "num_methods" in metrics
            assert "imports" in metrics
            assert "complexity" in metrics

            # Validate metric values
            assert metrics["lines_of_code"] >= 0
            assert metrics["num_classes"] >= 0
            assert metrics["num_functions"] >= 0
            assert metrics["num_methods"] >= 0
            assert metrics["complexity"] >= 1

    def test_dependency_tracking(self, temp_codebase):
        """Test that dependencies are properly tracked."""
        detector = PatternDetector()
        patterns = detector.analyze_codebase(temp_codebase)

        assert len(detector.dependencies) > 0

        # Check specific dependencies
        assert any(
            any("payment_service" in dep for dep in deps)
            for module, deps in detector.dependencies.items()
            if "order_service" in module
        )
