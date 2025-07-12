"""Tests for the data models."""

from datetime import timedelta

import pytest
from pydantic import ValidationError

from import_performance_optimizer.models import (
    ImportMetrics,
    MemoryFootprint,
    LazyLoadingOpportunity,
    CircularImportInfo,
    DynamicImportSuggestion,
    ImportAnalysisReport
)


class TestImportMetrics:
    """Test suite for ImportMetrics model."""

    def test_valid_import_metrics(self):
        """Test creating valid import metrics."""
        metrics = ImportMetrics(
            module_name="test_module",
            import_time=timedelta(seconds=0.5),
            cumulative_time=timedelta(seconds=1.0),
            parent_module="parent",
            children=["child1", "child2"],
            is_bottleneck=True,
            import_depth=2
        )
        
        assert metrics.module_name == "test_module"
        assert metrics.import_time.total_seconds() == 0.5
        assert metrics.cumulative_time.total_seconds() == 1.0
        assert metrics.parent_module == "parent"
        assert len(metrics.children) == 2
        assert metrics.is_bottleneck is True
        assert metrics.import_depth == 2

    def test_minimal_import_metrics(self):
        """Test creating import metrics with minimal fields."""
        metrics = ImportMetrics(
            module_name="minimal",
            import_time=timedelta(seconds=0.1),
            cumulative_time=timedelta(seconds=0.1)
        )
        
        assert metrics.module_name == "minimal"
        assert metrics.parent_module is None
        assert metrics.children == []
        assert metrics.is_bottleneck is False
        assert metrics.import_depth == 0


class TestMemoryFootprint:
    """Test suite for MemoryFootprint model."""

    def test_valid_memory_footprint(self):
        """Test creating valid memory footprint."""
        footprint = MemoryFootprint(
            module_name="memory_module",
            direct_memory=5 * 1024 * 1024,  # 5MB
            cumulative_memory=10 * 1024 * 1024,  # 10MB
            memory_by_child={"child1": 3 * 1024 * 1024, "child2": 2 * 1024 * 1024},
            percentage_of_total=25.5
        )
        
        assert footprint.module_name == "memory_module"
        assert footprint.direct_memory == 5 * 1024 * 1024
        assert footprint.cumulative_memory == 10 * 1024 * 1024
        assert len(footprint.memory_by_child) == 2
        assert footprint.percentage_of_total == 25.5

    def test_memory_footprint_defaults(self):
        """Test memory footprint with default values."""
        footprint = MemoryFootprint(
            module_name="test",
            direct_memory=1000,
            cumulative_memory=1000
        )
        
        assert footprint.memory_by_child == {}
        assert footprint.percentage_of_total == 0.0


class TestLazyLoadingOpportunity:
    """Test suite for LazyLoadingOpportunity model."""

    def test_valid_lazy_loading_opportunity(self):
        """Test creating valid lazy loading opportunity."""
        opportunity = LazyLoadingOpportunity(
            module_name="lazy_module",
            import_location="file.py:10",
            first_usage_location="file.py:100",
            time_to_first_use=timedelta(seconds=5),
            estimated_time_savings=timedelta(seconds=0.8),
            confidence_score=0.85,
            transformation_suggestion="Move import to function level"
        )
        
        assert opportunity.module_name == "lazy_module"
        assert opportunity.import_location == "file.py:10"
        assert opportunity.first_usage_location == "file.py:100"
        assert opportunity.time_to_first_use.total_seconds() == 5
        assert opportunity.estimated_time_savings.total_seconds() == 0.8
        assert opportunity.confidence_score == 0.85

    def test_unused_import_opportunity(self):
        """Test lazy loading opportunity for unused import."""
        opportunity = LazyLoadingOpportunity(
            module_name="unused_module",
            import_location="file.py:5",
            first_usage_location=None,
            time_to_first_use=None,
            estimated_time_savings=timedelta(seconds=1.0),
            confidence_score=0.95
        )
        
        assert opportunity.first_usage_location is None
        assert opportunity.time_to_first_use is None

    def test_confidence_score_validation(self):
        """Test confidence score validation."""
        with pytest.raises(ValidationError):
            LazyLoadingOpportunity(
                module_name="test",
                import_location="file.py:1",
                estimated_time_savings=timedelta(seconds=0.1),
                confidence_score=1.5  # Invalid: > 1.0
            )
        
        with pytest.raises(ValidationError):
            LazyLoadingOpportunity(
                module_name="test",
                import_location="file.py:1",
                estimated_time_savings=timedelta(seconds=0.1),
                confidence_score=-0.1  # Invalid: < 0.0
            )


class TestCircularImportInfo:
    """Test suite for CircularImportInfo model."""

    def test_valid_circular_import_info(self):
        """Test creating valid circular import info."""
        info = CircularImportInfo(
            modules_involved=["module_a", "module_b", "module_c"],
            performance_impact=timedelta(seconds=0.5),
            memory_overhead=2 * 1024 * 1024,  # 2MB
            import_chain=["module_a -> module_b", "module_b -> module_c", "module_c -> module_a"],
            severity="high"
        )
        
        assert len(info.modules_involved) == 3
        assert info.performance_impact.total_seconds() == 0.5
        assert info.memory_overhead == 2 * 1024 * 1024
        assert len(info.import_chain) == 3
        assert info.severity == "high"

    def test_severity_validation(self):
        """Test severity field validation."""
        valid_severities = ["low", "medium", "high", "critical"]
        
        for severity in valid_severities:
            info = CircularImportInfo(
                modules_involved=["a", "b"],
                performance_impact=timedelta(seconds=0.1),
                memory_overhead=1000,
                import_chain=["a -> b", "b -> a"],
                severity=severity
            )
            assert info.severity == severity
        
        with pytest.raises(ValidationError):
            CircularImportInfo(
                modules_involved=["a", "b"],
                performance_impact=timedelta(seconds=0.1),
                memory_overhead=1000,
                import_chain=["a -> b", "b -> a"],
                severity="invalid"  # Invalid severity
            )


class TestDynamicImportSuggestion:
    """Test suite for DynamicImportSuggestion model."""

    def test_valid_dynamic_import_suggestion(self):
        """Test creating valid dynamic import suggestion."""
        suggestion = DynamicImportSuggestion(
            module_name="dynamic_module",
            current_import_statement="import dynamic_module",
            suggested_import_statement="# Move import inside function",
            usage_patterns=["file.py::function1", "file.py::function2"],
            estimated_time_improvement=timedelta(seconds=0.3),
            estimated_memory_savings=5 * 1024 * 1024,  # 5MB
            code_examples=["def func():\n    import dynamic_module\n    return dynamic_module.process()"]
        )
        
        assert suggestion.module_name == "dynamic_module"
        assert "import dynamic_module" in suggestion.current_import_statement
        assert len(suggestion.usage_patterns) == 2
        assert suggestion.estimated_time_improvement.total_seconds() == 0.3
        assert suggestion.estimated_memory_savings == 5 * 1024 * 1024
        assert len(suggestion.code_examples) == 1

    def test_dynamic_suggestion_defaults(self):
        """Test dynamic suggestion with default values."""
        suggestion = DynamicImportSuggestion(
            module_name="test",
            current_import_statement="import test",
            suggested_import_statement="# Dynamic import",
            usage_patterns=["usage1"],
            estimated_time_improvement=timedelta(seconds=0.1),
            estimated_memory_savings=1000
        )
        
        assert suggestion.code_examples == []


class TestImportAnalysisReport:
    """Test suite for ImportAnalysisReport model."""

    def test_valid_import_analysis_report(self):
        """Test creating valid import analysis report."""
        # Create sample data
        metrics = ImportMetrics(
            module_name="bottleneck",
            import_time=timedelta(seconds=1.0),
            cumulative_time=timedelta(seconds=2.0),
            is_bottleneck=True
        )
        
        opportunity = LazyLoadingOpportunity(
            module_name="lazy",
            import_location="file.py:1",
            estimated_time_savings=timedelta(seconds=0.5),
            confidence_score=0.8
        )
        
        circular = CircularImportInfo(
            modules_involved=["a", "b"],
            performance_impact=timedelta(seconds=0.2),
            memory_overhead=1000,
            import_chain=["a -> b", "b -> a"],
            severity="medium"
        )
        
        dynamic = DynamicImportSuggestion(
            module_name="dynamic",
            current_import_statement="import dynamic",
            suggested_import_statement="# Dynamic",
            usage_patterns=["func"],
            estimated_time_improvement=timedelta(seconds=0.3),
            estimated_memory_savings=2000
        )
        
        report = ImportAnalysisReport(
            total_import_time=timedelta(seconds=5.0),
            total_memory_footprint=100 * 1024 * 1024,  # 100MB
            bottleneck_modules=[metrics],
            lazy_loading_opportunities=[opportunity],
            circular_imports=[circular],
            dynamic_import_suggestions=[dynamic],
            optimization_summary={
                "total_savings": 2.0,
                "recommendations": 10
            }
        )
        
        assert report.total_import_time.total_seconds() == 5.0
        assert report.total_memory_footprint == 100 * 1024 * 1024
        assert len(report.bottleneck_modules) == 1
        assert len(report.lazy_loading_opportunities) == 1
        assert len(report.circular_imports) == 1
        assert len(report.dynamic_import_suggestions) == 1
        assert report.optimization_summary["total_savings"] == 2.0

    def test_empty_analysis_report(self):
        """Test creating empty analysis report."""
        report = ImportAnalysisReport(
            total_import_time=timedelta(seconds=0),
            total_memory_footprint=0,
            bottleneck_modules=[],
            lazy_loading_opportunities=[],
            circular_imports=[],
            dynamic_import_suggestions=[]
        )
        
        assert report.total_import_time.total_seconds() == 0
        assert report.total_memory_footprint == 0
        assert len(report.bottleneck_modules) == 0
        assert report.optimization_summary == {}

    def test_timedelta_serialization(self):
        """Test that timedelta fields can be properly serialized."""
        metrics = ImportMetrics(
            module_name="test",
            import_time=timedelta(seconds=1.5),
            cumulative_time=timedelta(seconds=2.5)
        )
        
        # Should be able to convert to dict
        data = metrics.model_dump()
        assert isinstance(data['import_time'], timedelta)
        assert data['import_time'].total_seconds() == 1.5