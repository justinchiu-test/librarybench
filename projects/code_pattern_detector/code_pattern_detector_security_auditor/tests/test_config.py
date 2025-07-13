"""Tests for scanner configuration."""

import pytest
from pathlib import Path
from pydantic import ValidationError

from pypatternguard.config import ScannerConfig


class TestScannerConfig:
    """Test scanner configuration functionality."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = ScannerConfig()
        
        assert config.max_file_size_mb == 10.0
        assert config.file_extensions == [".py", ".pyw"]
        assert config.max_workers == 4
        assert config.min_confidence_threshold == 0.7
        assert config.report_format == "json"
        assert config.include_code_snippets == True
        assert config.enable_heuristics == True
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = ScannerConfig(
            max_file_size_mb=20.0,
            max_workers=8,
            min_confidence_threshold=0.9,
            file_extensions=[".py", ".pyw", ".py3"],
            report_format="xml"
        )
        
        assert config.max_file_size_mb == 20.0
        assert config.max_workers == 8
        assert config.min_confidence_threshold == 0.9
        assert ".py3" in config.file_extensions
        assert config.report_format == "xml"
    
    def test_config_validation(self):
        """Test configuration validation."""
        config = ScannerConfig()
        assert config.validate_config()
        
        # Test invalid values
        with pytest.raises(ValidationError):
            ScannerConfig(min_confidence_threshold=1.5)  # Out of range
        
        with pytest.raises(ValidationError):
            ScannerConfig(min_confidence_threshold=-0.1)  # Negative
        
        with pytest.raises(ValidationError):
            ScannerConfig(report_format="pdf")  # Invalid format
    
    def test_exclude_patterns(self):
        """Test exclude patterns configuration."""
        config = ScannerConfig(
            exclude_patterns=["test_*", "*.pyc", "__pycache__", "migrations"]
        )
        
        assert "test_*" in config.exclude_patterns
        assert "migrations" in config.exclude_patterns
        assert len(config.exclude_patterns) == 4
    
    def test_suppression_file_config(self):
        """Test suppression file configuration."""
        suppression_path = Path("/path/to/suppressions.json")
        config = ScannerConfig(suppression_file=suppression_path)
        
        assert config.suppression_file == suppression_path
        assert isinstance(config.suppression_file, Path)
    
    def test_compliance_frameworks_config(self):
        """Test compliance frameworks configuration."""
        config = ScannerConfig(
            compliance_frameworks=["PCI-DSS", "SOC2", "HIPAA"]
        )
        
        assert "PCI-DSS" in config.compliance_frameworks
        assert "HIPAA" in config.compliance_frameworks
        assert len(config.compliance_frameworks) == 3
    
    def test_performance_settings(self):
        """Test performance-related settings."""
        config = ScannerConfig(
            chunk_size=2000,
            memory_limit_mb=4096,
            timeout_seconds=600,
            ast_timeout_seconds=20
        )
        
        assert config.chunk_size == 2000
        assert config.memory_limit_mb == 4096
        assert config.timeout_seconds == 600
        assert config.ast_timeout_seconds == 20
    
    def test_advanced_settings(self):
        """Test advanced configuration settings."""
        config = ScannerConfig(
            incremental_scan=False,
            cache_results=False,
            enable_auto_suppression=True
        )
        
        assert config.incremental_scan == False
        assert config.cache_results == False
        assert config.enable_auto_suppression == True
    
    def test_custom_rules_path(self):
        """Test custom rules path configuration."""
        rules_path = Path("/custom/rules.yaml")
        config = ScannerConfig(custom_rules_path=rules_path)
        
        assert config.custom_rules_path == rules_path
        assert isinstance(config.custom_rules_path, Path)
    
    def test_snippet_context_lines(self):
        """Test code snippet context lines configuration."""
        config = ScannerConfig(snippet_lines_context=5)
        assert config.snippet_lines_context == 5
        
        config = ScannerConfig(snippet_lines_context=10)
        assert config.snippet_lines_context == 10
    
    def test_invalid_config_values(self):
        """Test that invalid configuration values raise errors."""
        with pytest.raises(ValueError):
            config = ScannerConfig(max_file_size_mb=-1)
            config.validate_config()
        
        with pytest.raises(ValueError):
            config = ScannerConfig(max_workers=0)
            config.validate_config()
        
        with pytest.raises(ValueError):
            config = ScannerConfig(memory_limit_mb=-100)
            config.validate_config()
    
    def test_config_serialization(self):
        """Test configuration serialization."""
        config = ScannerConfig(
            max_workers=6,
            file_extensions=[".py", ".pyx"],
            suppression_file=Path("/tmp/suppress.json")
        )
        
        # Test model_dump (Pydantic v2)
        config_dict = config.model_dump()
        assert config_dict["max_workers"] == 6
        assert config_dict["file_extensions"] == [".py", ".pyx"]
        assert config_dict["suppression_file"] == "/tmp/suppress.json"
    
    def test_dependency_checking_config(self):
        """Test dependency checking configuration."""
        config = ScannerConfig(check_dependencies=True)
        assert config.check_dependencies == True
        
        config = ScannerConfig(check_dependencies=False)
        assert config.check_dependencies == False