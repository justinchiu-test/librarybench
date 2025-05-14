"""
Tests for the main Compliance Data Discovery Scanner.

This module contains tests for the main scanner functionality that integrates
all components of the system.
"""

import os
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

from file_system_analyzer.scanner import (
    ComplianceScanner,
    ComplianceScanOptions
)
from file_system_analyzer.detection.scanner import (
    ScanOptions, 
    ScanResult,
    FileMetadata
)
from file_system_analyzer.detection.patterns import (
    PatternDefinitions,
    ComplianceCategory,
    SensitivityLevel
)
from file_system_analyzer.utils.crypto import CryptoProvider


class TestComplianceScanOptions:
    """Tests for compliance scan options."""
    
    def test_default_options(self):
        """Test default compliance scan options."""
        options = ComplianceScanOptions()
        
        # Check default values
        assert options.scan_options is not None
        assert options.output_dir is None
        assert options.user_id == "system"
        assert options.baseline_id is None
        assert options.create_baseline is False
        assert options.baseline_name is None
        assert options.generate_reports is True
        assert len(options.report_frameworks) == 0
        assert options.create_evidence_package is False
        assert options.evidence_package_name is None
        assert options.audit_log_file is None
    
    def test_custom_options(self):
        """Test custom compliance scan options."""
        scan_options = ScanOptions(
            recursive=False,
            max_file_size=1024 * 1024,
            categories=[ComplianceCategory.PII]
        )
        
        options = ComplianceScanOptions(
            scan_options=scan_options,
            output_dir="/test/output",
            user_id="test_user",
            create_baseline=True,
            baseline_name="Test Baseline",
            report_frameworks=["gdpr", "pci-dss"],
            create_evidence_package=True,
            evidence_package_name="Test Package",
            audit_log_file="/test/audit.log"
        )
        
        # Check custom values
        assert options.scan_options == scan_options
        assert options.scan_options.recursive is False
        assert options.output_dir == "/test/output"
        assert options.user_id == "test_user"
        assert options.create_baseline is True
        assert options.baseline_name == "Test Baseline"
        assert "gdpr" in options.report_frameworks
        assert "pci-dss" in options.report_frameworks
        assert options.create_evidence_package is True
        assert options.evidence_package_name == "Test Package"
        assert options.audit_log_file == "/test/audit.log"


class TestComplianceScanner:
    """Tests for the main compliance scanner."""
    
    def test_scanner_initialization(self):
        """Test scanner initialization."""
        # Default initialization
        scanner = ComplianceScanner()
        
        assert scanner.options is not None
        assert scanner.crypto_provider is not None
        assert scanner.scanner is not None
        assert scanner.audit_logger is not None
        assert scanner.diff_analyzer is not None
        assert scanner.evidence_packager is not None
        
        # Custom initialization
        options = ComplianceScanOptions(
            user_id="test_user",
            audit_log_file="/test/audit.log"
        )
        
        crypto_provider = CryptoProvider.generate()
        
        scanner = ComplianceScanner(
            options=options,
            crypto_provider=crypto_provider
        )
        
        assert scanner.options == options
        assert scanner.options.user_id == "test_user"
        assert scanner.crypto_provider == crypto_provider
        assert scanner.audit_logger.user_id == "test_user"
        assert scanner.audit_logger.log_file == "/test/audit.log"
    
    def test_scan_directory(self, tmp_path):
        """Test scanning a directory."""
        # Create test directories
        scan_dir = tmp_path / "scan_dir"
        scan_dir.mkdir()

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create audit log file
        audit_log_file = tmp_path / "audit.log"

        # Create sample files with sensitive data
        file1 = scan_dir / "file1.txt"
        file1.write_text("This file contains SSN 123-45-6789")

        file2 = scan_dir / "file2.txt"
        file2.write_text("This file contains a credit card 4111111111111111")

        config_file = scan_dir / "config.json"
        config_file.write_text('{"password": "secret123", "api_key": "abcdef123456"}')

        # Create options
        options = ComplianceScanOptions(
            output_dir=str(output_dir),
            audit_log_file=str(audit_log_file),
            generate_reports=True,
            report_frameworks=["gdpr"],
            create_baseline=True,
            baseline_name="test_baseline"
        )

        # Create scanner
        scanner = ComplianceScanner(options=options)

        # Perform scan
        summary = scanner.scan_directory(str(scan_dir))

        # Verify scan completed successfully
        assert summary is not None
        assert summary.total_files > 0
        assert summary.files_with_sensitive_data > 0

        # Verify outputs were created
        baseline_file = list(output_dir.glob("test_baseline.json"))
        assert len(baseline_file) == 1

        report_files = list(output_dir.glob("compliance_report_*.json"))
        assert len(report_files) > 0

        # Verify audit log was created
        assert audit_log_file.exists()

        # Verify scanner state
        assert scanner.baseline is not None
        assert scanner.scan_results is not None
        assert len(scanner.scan_results) > 0
        assert len(scanner.reports) > 0
    
    @patch('file_system_analyzer.differential.analyzer.DifferentialAnalyzer.load_baseline')
    def test_differential_scan(self, mock_load_baseline, sample_data_dir, tmp_path):
        """Test differential scanning with baseline."""
        # Create mock baseline
        mock_baseline = MagicMock()
        mock_baseline.baseline_id = "test-baseline"
        mock_baseline.verification_info = None
        mock_baseline.files = {}
        
        # Configure mock
        mock_load_baseline.return_value = mock_baseline
        
        # Create output directory
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        # Create baseline file
        baseline_file = output_dir / "test-baseline.json"
        baseline_file.write_text("{}")
        
        # Create options
        options = ComplianceScanOptions(
            output_dir=str(output_dir),
            baseline_id="test-baseline"
        )
        
        # Create scanner
        scanner = ComplianceScanner(options=options)
        
        # Scan directory
        summary = scanner.scan_directory(sample_data_dir)
        
        # Check scan results
        assert summary is not None
        assert summary.total_files > 0
        
        # Check diff result
        assert scanner.diff_result is not None
        assert scanner.diff_result.baseline_id == "test-baseline"
        
        # Verify mock called
        mock_load_baseline.assert_called_once_with(os.path.join(str(output_dir), "test-baseline.json"))
    
    def test_error_handling(self, tmp_path):
        """Test scanner error handling."""
        # Create scanner with invalid baseline ID to trigger error
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        options = ComplianceScanOptions(
            output_dir=str(output_dir),
            baseline_id="nonexistent_baseline"  # This will cause a FileNotFoundError
        )

        scanner = ComplianceScanner(options=options)

        # Create test directory
        scan_dir = tmp_path / "scan_dir"
        scan_dir.mkdir()

        # Add a test file
        test_file = scan_dir / "test.txt"
        test_file.write_text("Sample content")

        # Scan should raise an exception due to missing baseline
        with pytest.raises(FileNotFoundError):
            scanner.scan_directory(str(scan_dir))

        # Test handling of scan errors (using a non-existent directory)
        scanner = ComplianceScanner()

        with pytest.raises(Exception):
            scanner.scan_directory("/nonexistent/directory")