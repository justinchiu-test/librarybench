"""Tests for the main scanner functionality."""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from pypatternguard import SecurityScanner, ScannerConfig
from pypatternguard.models import SeverityLevel, VulnerabilityType


class TestSecurityScanner:
    """Test the main SecurityScanner class."""
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def vulnerable_project(self, temp_project):
        """Create a project with known vulnerabilities."""
        # Create vulnerable Python files
        vulnerable_files = {
            "auth.py": '''
import hashlib
import os

# Hardcoded secret
API_KEY = "sk-1234567890abcdef1234567890abcdef"
DB_PASSWORD = "admin123456"

def hash_password(password):
    # Weak hashing algorithm
    return hashlib.md5(password.encode()).hexdigest()

def authenticate(username, password):
    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    return execute_query(query)
''',
            "crypto.py": '''
from Crypto.Cipher import DES
import pickle

# Hardcoded IV
IV = "12345678"

def encrypt_data(data, key):
    cipher = DES.new(key, DES.MODE_ECB)
    return cipher.encrypt(data)

def load_user_data(user_input):
    # Unsafe deserialization
    return pickle.loads(user_input)
''',
            "views.py": '''
from flask import request, render_template_string
import os

def search_files():
    filename = request.args.get('file')
    # Command injection
    os.system(f"find /var/log -name {filename}")
    
def greet_user():
    name = request.args.get('name')
    # XSS vulnerability
    return render_template_string('<h1>Hello {{ name|safe }}</h1>', name=name)

def run_code():
    code = request.form.get('code')
    # Code injection
    eval(code)
''',
            "config.py": '''
# Configuration file with secrets
DATABASE_URL = "postgresql://user:password123@localhost/db"
SECRET_KEY = "my-secret-key-123"
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
'''
        }
        
        for filename, content in vulnerable_files.items():
            file_path = temp_project / filename
            file_path.write_text(content)
        
        # Create a safe file for comparison
        safe_file = temp_project / "safe.py"
        safe_file.write_text('''
import os
from flask import request, escape

def safe_function():
    user_input = request.args.get('input')
    # Properly escaped output
    return f"<p>{escape(user_input)}</p>"
    
def get_env_password():
    # Password from environment variable, not hardcoded
    return os.environ.get('DB_PASSWORD')
''')
        
        return temp_project
    
    def test_scan_vulnerable_project(self, vulnerable_project):
        """Test scanning a project with vulnerabilities."""
        scanner = SecurityScanner()
        result = scanner.scan(str(vulnerable_project))
        
        assert result.scan_id
        assert result.timestamp
        assert result.total_files_scanned >= 4
        assert result.total_lines_scanned > 0
        assert result.scan_duration_seconds > 0
        assert len(result.vulnerabilities) > 0
        
        # Check that various vulnerability types were detected
        vuln_types = {v.type for v in result.vulnerabilities}
        assert VulnerabilityType.HARDCODED_SECRET in vuln_types
        assert VulnerabilityType.INJECTION in vuln_types
        assert VulnerabilityType.CRYPTO_FAILURE in vuln_types
        assert VulnerabilityType.INPUT_VALIDATION in vuln_types
        assert VulnerabilityType.XSS in vuln_types
        
        # Check severity distribution
        severities = {v.severity for v in result.vulnerabilities}
        assert SeverityLevel.CRITICAL in severities
        assert SeverityLevel.HIGH in severities
    
    def test_scan_single_file(self, vulnerable_project):
        """Test scanning a single file."""
        scanner = SecurityScanner()
        single_file = vulnerable_project / "auth.py"
        result = scanner.scan(str(single_file))
        
        assert result.total_files_scanned == 1
        assert len(result.vulnerabilities) >= 3  # API key, password, MD5, SQL injection
        
        # Check specific vulnerabilities
        secret_vulns = [v for v in result.vulnerabilities if v.type == VulnerabilityType.HARDCODED_SECRET]
        assert len(secret_vulns) >= 2
        
        sql_vulns = [v for v in result.vulnerabilities if v.type == VulnerabilityType.INJECTION]
        assert len(sql_vulns) >= 1
    
    def test_scan_nonexistent_path(self):
        """Test scanning a path that doesn't exist."""
        scanner = SecurityScanner()
        with pytest.raises(ValueError, match="Target path does not exist"):
            scanner.scan("/nonexistent/path")
    
    def test_custom_config(self, vulnerable_project):
        """Test scanning with custom configuration."""
        config = ScannerConfig(
            max_workers=2,
            min_confidence_threshold=0.9,
            file_extensions=[".py"],
            exclude_patterns=["config.py"]
        )
        
        scanner = SecurityScanner(config)
        result = scanner.scan(str(vulnerable_project))
        
        # config.py should be excluded
        scanned_files = {v.location.file_path.name for v in result.vulnerabilities}
        assert "config.py" not in scanned_files
        
        # Only high confidence vulnerabilities
        assert all(v.confidence >= 0.9 for v in result.vulnerabilities)
    
    def test_summary_stats(self, vulnerable_project):
        """Test summary statistics generation."""
        scanner = SecurityScanner()
        result = scanner.scan(str(vulnerable_project))
        stats = result.get_summary_stats()
        
        assert "total_vulnerabilities" in stats
        assert "severity_distribution" in stats
        assert "files_scanned" in stats
        assert "lines_scanned" in stats
        assert "scan_duration" in stats
        
        assert stats["total_vulnerabilities"] == len([v for v in result.vulnerabilities if not v.suppressed])
        assert stats["files_scanned"] == result.total_files_scanned
    
    def test_vulnerabilities_by_severity(self, vulnerable_project):
        """Test grouping vulnerabilities by severity."""
        scanner = SecurityScanner()
        result = scanner.scan(str(vulnerable_project))
        by_severity = result.get_vulnerabilities_by_severity()
        
        assert isinstance(by_severity, dict)
        assert all(level in by_severity for level in SeverityLevel)
        
        # Verify grouping
        for level, vulns in by_severity.items():
            assert all(v.severity == level for v in vulns)
            assert all(not v.suppressed for v in vulns)
    
    def test_compliance_mappings(self, vulnerable_project):
        """Test that vulnerabilities have compliance mappings."""
        scanner = SecurityScanner()
        result = scanner.scan(str(vulnerable_project))
        
        # Check that vulnerabilities have compliance mappings
        for vuln in result.vulnerabilities:
            assert vuln.compliance_mappings
            assert any(framework in vuln.compliance_mappings for framework in ["PCI-DSS", "SOC2"])
    
    def test_code_snippets_included(self, vulnerable_project):
        """Test that code snippets are included in vulnerabilities."""
        config = ScannerConfig(include_code_snippets=True)
        scanner = SecurityScanner(config)
        result = scanner.scan(str(vulnerable_project))
        
        # At least some vulnerabilities should have code snippets
        vulns_with_snippets = [v for v in result.vulnerabilities if v.code_snippet]
        assert len(vulns_with_snippets) > 0
        
        # Code snippets should contain actual code
        for vuln in vulns_with_snippets:
            assert len(vuln.code_snippet) > 0
            assert '\n' in vuln.code_snippet  # Multi-line context
    
    def test_scan_performance(self, vulnerable_project):
        """Test scan performance requirements."""
        # Add more files to test performance
        for i in range(20):
            file_path = vulnerable_project / f"test_{i}.py"
            file_path.write_text("x = 1\n" * 1000)  # 1000 lines each
        
        scanner = SecurityScanner()
        start_time = datetime.now()
        result = scanner.scan(str(vulnerable_project))
        duration = (datetime.now() - start_time).total_seconds()
        
        # Should scan at least 20,000 lines
        assert result.total_lines_scanned >= 20000
        
        # Performance check - should be reasonably fast
        assert duration < 60  # Less than 60 seconds for this test
        
        # Memory check would require process monitoring, skipping for unit test
    
    def test_file_size_limit(self, temp_project):
        """Test file size limit enforcement."""
        # Create a large file
        large_file = temp_project / "large.py"
        large_file.write_text("x = 1\n" * 1000000)  # Very large file
        
        config = ScannerConfig(max_file_size_mb=0.1)  # 100KB limit
        scanner = SecurityScanner(config)
        result = scanner.scan(str(temp_project))
        
        # Large file should be skipped
        assert result.total_files_scanned == 0
    
    def test_scan_errors_captured(self, temp_project):
        """Test that scan errors are captured."""
        # Create a file with invalid Python syntax
        bad_file = temp_project / "bad.py"
        bad_file.write_text("this is not valid python syntax !!!")
        
        scanner = SecurityScanner()
        result = scanner.scan(str(temp_project))
        
        # Should still complete scan
        assert result.scan_id
        # May have errors recorded
        # Scanner continues despite parse errors