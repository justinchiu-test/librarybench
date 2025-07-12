"""Error handling tests for the Legacy System Modernization Analyzer."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch
from legacy_analyzer import LegacyAnalyzer
from legacy_analyzer.pattern_detector import PatternDetector
from legacy_analyzer.database_coupling_detector import DatabaseCouplingDetector
from legacy_analyzer.strangler_fig_planner import StranglerFigPlanner
from legacy_analyzer.extraction_analyzer import ExtractionAnalyzer
from legacy_analyzer.roadmap_generator import RoadmapGenerator


class TestErrorHandling:
    """Test error handling and recovery."""

    def test_nonexistent_module_in_extraction_list(self):
        """Test handling of nonexistent modules in extraction list."""
        analyzer = LegacyAnalyzer()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create one real module
            real_module = Path(tmpdir) / "real.py"
            real_module.write_text("class Real: pass")

            # Request extraction of both real and nonexistent modules
            result = analyzer.analyze_codebase(
                tmpdir, modules_to_extract=["real.py", "nonexistent.py", "fake.py"]
            )

            # Should only analyze the real module
            assert len(result.extraction_feasibilities) == 1
            assert result.extraction_feasibilities[0].module_path == "real.py"

    def test_permission_denied_on_file(self, tmp_path):
        """Test handling of permission errors."""
        restricted_file = tmp_path / "restricted.py"
        restricted_file.write_text("class Restricted: pass")

        # Make file unreadable (Unix only)
        try:
            os.chmod(restricted_file, 0o000)

            detector = PatternDetector()
            patterns = detector.analyze_codebase(str(tmp_path))

            # Should handle permission errors gracefully
            assert isinstance(patterns, list)
        finally:
            # Restore permissions for cleanup
            os.chmod(restricted_file, 0o644)

    def test_circular_dependency_detection_with_self_import(self, tmp_path):
        """Test handling of modules that import themselves."""
        self_import = tmp_path / "self_import.py"
        self_import.write_text("""
from self_import import SomeClass  # Self import!

class SomeClass:
    pass
""")

        detector = PatternDetector()
        patterns = detector.analyze_codebase(str(tmp_path))

        # Should handle self-imports without infinite loops
        assert isinstance(patterns, list)

    def test_empty_dependency_graph(self):
        """Test strangler fig planning with no dependencies."""
        planner = StranglerFigPlanner()
        boundaries = planner.plan_boundaries({})

        assert boundaries == []

    def test_single_node_dependency_graph(self):
        """Test strangler fig planning with single isolated module."""
        planner = StranglerFigPlanner()
        boundaries = planner.plan_boundaries({"module_a": set()})

        # Single modules don't form boundaries
        assert isinstance(boundaries, list)

    def test_extraction_with_empty_patterns_and_couplings(self):
        """Test extraction analysis with no patterns or couplings."""
        analyzer = ExtractionAnalyzer()

        feasibility = analyzer.analyze_extraction_feasibility(
            "module.py",
            {"module.py": set()},
            [],  # No patterns
            [],  # No database couplings
            {"module.py": {"lines_of_code": 100}},
        )

        assert feasibility.module_path == "module.py"
        assert feasibility.feasibility_score > 0
        assert len(feasibility.risks) >= 0

    def test_roadmap_generation_with_no_data(self):
        """Test roadmap generation with empty inputs."""
        generator = RoadmapGenerator()

        roadmap = generator.generate_roadmap(
            "Empty Project",
            [],  # No patterns
            [],  # No boundaries
            [],  # No feasibilities
            [],  # No couplings
        )

        assert roadmap.project_name == "Empty Project"
        assert len(roadmap.phases) > 0  # Should still have foundation phase
        assert roadmap.total_duration_days > 0

    def test_database_coupling_with_no_shared_tables(self, tmp_path):
        """Test database coupling when modules use different tables."""
        # Module 1
        (tmp_path / "module1.py").write_text("""
class Module1:
    def query(self):
        return "SELECT * FROM table1"
""")

        # Module 2
        (tmp_path / "module2.py").write_text("""
class Module2:
    def query(self):
        return "SELECT * FROM table2"
""")

        detector = DatabaseCouplingDetector()
        couplings = detector.analyze_database_coupling(str(tmp_path))

        # No coupling when tables are different
        assert len(couplings) == 0

    def test_invalid_python_version_syntax(self, tmp_path):
        """Test handling of Python 2 syntax in Python 3 analyzer."""
        py2_file = tmp_path / "python2_code.py"
        py2_file.write_text("""
# Python 2 syntax
print "Hello World"
exec "x = 1"

class OldStyle:
    pass
""")

        detector = PatternDetector()
        patterns = detector.analyze_codebase(str(tmp_path))

        # Should handle syntax errors from old Python versions
        assert isinstance(patterns, list)

    @patch("os.walk")
    def test_os_walk_exception(self, mock_walk):
        """Test handling of OS errors during directory traversal."""
        mock_walk.side_effect = OSError("Permission denied")

        detector = PatternDetector()
        patterns = detector.analyze_codebase("/some/path")

        # Should handle OS errors gracefully
        assert patterns == []

    def test_extremely_large_complexity_score(self, tmp_path):
        """Test handling of extremely complex functions."""
        complex_file = tmp_path / "complex.py"

        # Generate extremely nested code
        nested_ifs = ""
        indent = "    "
        for i in range(50):
            nested_ifs += f"{indent}if condition_{i}:\n"
            indent += "    "
        nested_ifs += f"{indent}pass"

        complex_file.write_text(f"""
def extremely_complex_function():
{nested_ifs}
""")

        detector = PatternDetector()
        patterns = detector.analyze_codebase(str(tmp_path))

        # Should handle high complexity without overflow
        assert isinstance(patterns, list)
        # Check if any pattern was detected for the complex file
        assert any(p.module_path == "complex.py" for p in patterns)

    def test_module_with_only_imports(self, tmp_path):
        """Test module containing only import statements."""
        imports_only = tmp_path / "imports_only.py"
        imports_only.write_text("""
import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict
import numpy as np
import pandas as pd
""")

        analyzer = LegacyAnalyzer()
        result = analyzer.analyze_codebase(str(tmp_path))

        assert result.summary["total_modules"] == 1

    def test_relative_import_beyond_root(self, tmp_path):
        """Test relative imports that go beyond package root."""
        deep_module = tmp_path / "package" / "subpackage" / "module.py"
        deep_module.parent.mkdir(parents=True)
        deep_module.write_text("""
from ....outside import Something  # Too many levels up!
""")

        detector = PatternDetector()
        patterns = detector.analyze_codebase(str(tmp_path))

        # Should handle invalid relative imports
        assert isinstance(patterns, list)
