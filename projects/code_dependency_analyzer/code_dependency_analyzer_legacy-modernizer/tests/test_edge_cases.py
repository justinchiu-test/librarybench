"""Edge case tests for the Legacy System Modernization Analyzer."""

import pytest
from legacy_analyzer import LegacyAnalyzer
from legacy_analyzer.pattern_detector import PatternDetector
from legacy_analyzer.database_coupling_detector import DatabaseCouplingDetector
from legacy_analyzer.models import (
    PatternType,
)


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_python_file(self, tmp_path):
        """Test handling of empty Python files."""
        empty_file = tmp_path / "empty.py"
        empty_file.write_text("")

        detector = PatternDetector()
        patterns = detector.analyze_codebase(str(tmp_path))

        # Should handle empty files gracefully
        assert isinstance(patterns, list)

    def test_syntax_error_in_file(self, tmp_path):
        """Test handling of files with syntax errors."""
        bad_file = tmp_path / "syntax_error.py"
        bad_file.write_text("""
def broken_function(
    # Missing closing parenthesis
    pass
""")

        detector = PatternDetector()
        patterns = detector.analyze_codebase(str(tmp_path))

        # Should skip files with syntax errors
        assert isinstance(patterns, list)

    def test_non_python_files(self, tmp_path):
        """Test that non-Python files are ignored."""
        # Create various non-Python files
        (tmp_path / "readme.txt").write_text("This is a text file")
        (tmp_path / "config.json").write_text('{"key": "value"}')
        (tmp_path / "script.sh").write_text("#!/bin/bash\necho 'hello'")

        detector = PatternDetector()
        patterns = detector.analyze_codebase(str(tmp_path))

        assert len(patterns) == 0

    def test_deeply_nested_directory_structure(self, tmp_path):
        """Test handling of deeply nested directories."""
        # Create nested structure
        deep_path = tmp_path
        for i in range(10):
            deep_path = deep_path / f"level_{i}"
            deep_path.mkdir()

        # Add a Python file at the deepest level
        (deep_path / "deep_module.py").write_text("""
class DeepClass:
    pass
""")

        analyzer = LegacyAnalyzer()
        result = analyzer.analyze_codebase(str(tmp_path))

        assert result.summary["total_modules"] == 1

    def test_circular_imports_in_init_files(self, tmp_path):
        """Test circular imports through __init__.py files."""
        # Create package structure
        pkg_a = tmp_path / "package_a"
        pkg_b = tmp_path / "package_b"
        pkg_a.mkdir()
        pkg_b.mkdir()

        (pkg_a / "__init__.py").write_text("from package_b import ClassB")
        (pkg_b / "__init__.py").write_text("from package_a import ClassA")
        (pkg_a / "module_a.py").write_text("class ClassA: pass")
        (pkg_b / "module_b.py").write_text("class ClassB: pass")

        detector = PatternDetector()
        patterns = detector.analyze_codebase(str(tmp_path))

        circular_patterns = [
            p for p in patterns if p.pattern_type == PatternType.CIRCULAR_DEPENDENCY
        ]
        assert len(circular_patterns) > 0

    def test_unicode_in_source_files(self, tmp_path):
        """Test handling of Unicode characters in source files."""
        unicode_file = tmp_path / "unicode_module.py"
        unicode_file.write_text(
            """
# -*- coding: utf-8 -*-
class UnicodeClass:
    def get_message(self):
        return "Hello 世界 🌍"
    
    def process_data(self):
        data = {"user": "José", "city": "São Paulo"}
        return data
""",
            encoding="utf-8",
        )

        analyzer = LegacyAnalyzer()
        result = analyzer.analyze_codebase(str(tmp_path))

        assert result.summary["total_modules"] == 1

    def test_very_long_lines(self, tmp_path):
        """Test handling of files with very long lines."""
        long_line_file = tmp_path / "long_lines.py"
        very_long_string = "x" * 5000
        long_line_file.write_text(f'''
def function_with_long_line():
    very_long_variable = "{very_long_string}"
    return very_long_variable
''')

        detector = PatternDetector()
        patterns = detector.analyze_codebase(str(tmp_path))

        # Should handle long lines without crashing
        assert isinstance(patterns, list)

    def test_binary_file_in_directory(self, tmp_path):
        """Test handling when binary files are present."""
        # Create a binary file
        binary_file = tmp_path / "binary.pyc"
        binary_file.write_bytes(b"\x00\x01\x02\x03\x04\x05")

        # Create a normal Python file
        (tmp_path / "normal.py").write_text("class Normal: pass")

        analyzer = LegacyAnalyzer()
        result = analyzer.analyze_codebase(str(tmp_path))

        # Should only process .py files
        assert result.summary["total_modules"] == 1

    def test_symlinks(self, tmp_path):
        """Test handling of symbolic links."""
        # Create a module
        real_file = tmp_path / "real_module.py"
        real_file.write_text("class RealClass: pass")

        # Create a symlink
        symlink = tmp_path / "link_module.py"
        try:
            symlink.symlink_to(real_file)

            detector = PatternDetector()
            patterns = detector.analyze_codebase(str(tmp_path))

            # Should handle symlinks gracefully
            assert isinstance(patterns, list)
        except OSError:
            # Skip test if symlinks not supported
            pytest.skip("Symlinks not supported on this system")

    def test_files_with_no_classes_or_functions(self, tmp_path):
        """Test files containing only constants and imports."""
        constants_file = tmp_path / "constants.py"
        constants_file.write_text("""
# Configuration constants
DEBUG = True
API_KEY = "secret"
MAX_RETRIES = 3
TIMEOUT = 30

# Import statements
import os
import sys
from typing import Dict, List
""")

        analyzer = LegacyAnalyzer()
        result = analyzer.analyze_codebase(str(tmp_path))

        # Should still analyze the file
        assert result.summary["total_modules"] == 1

    def test_extraction_with_no_dependencies(self, tmp_path):
        """Test extraction analysis for isolated module."""
        isolated = tmp_path / "isolated.py"
        isolated.write_text("""
class IsolatedClass:
    def method(self):
        return "I have no dependencies"
""")

        analyzer = LegacyAnalyzer()
        result = analyzer.analyze_codebase(
            str(tmp_path), modules_to_extract=["isolated.py"]
        )

        assert len(result.extraction_feasibilities) == 1
        assert result.extraction_feasibilities[0].feasibility_score > 0.9

    def test_database_coupling_with_invalid_sql(self, tmp_path):
        """Test database coupling detection with malformed SQL."""
        bad_sql = tmp_path / "bad_sql.py"
        bad_sql.write_text("""
class BadSQL:
    def query(self):
        # Malformed SQL
        q1 = "SELECT * FROM WHERE"
        q2 = "UPDATE SET value = 1"
        q3 = "This is not SQL at all"
""")

        detector = DatabaseCouplingDetector()
        couplings = detector.analyze_database_coupling(str(tmp_path))

        # Should handle malformed SQL gracefully
        assert isinstance(couplings, list)
