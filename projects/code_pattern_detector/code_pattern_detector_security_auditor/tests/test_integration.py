"""Integration tests for the complete system."""

import pytest
import tempfile
import shutil
import json
from pathlib import Path

from pypatternguard import SecurityScanner, ScannerConfig
from pypatternguard.models import SeverityLevel, VulnerabilityType


class TestIntegration:
    """Integration tests for the complete PyPatternGuard system."""
    
    @pytest.fixture
    def fintech_project(self):
        """Create a realistic fintech project structure."""
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir)
        
        # Create project structure
        (project_path / "app").mkdir()
        (project_path / "app" / "auth").mkdir()
        (project_path / "app" / "payments").mkdir()
        (project_path / "app" / "api").mkdir()
        (project_path / "config").mkdir()
        (project_path / "tests").mkdir()
        
        # Authentication module with vulnerabilities
        auth_code = '''
import hashlib
import pickle
from flask import request, session

# Configuration
SECRET_KEY = "super-secret-key-12345"  # Hardcoded secret
API_TOKEN = "sk-proj-1234567890abcdef"  # API token

class AuthManager:
    def __init__(self):
        self.salt = "fixed-salt-value"  # Hardcoded salt
        
    def hash_password(self, password):
        # Weak hashing algorithm
        return hashlib.md5((password + self.salt).encode()).hexdigest()
    
    def authenticate(self, username, password):
        # SQL injection vulnerability
        query = f"SELECT * FROM users WHERE username='{username}' AND password_hash='{self.hash_password(password)}'"
        return self.execute_query(query)
    
    def load_session(self, session_data):
        # Insecure deserialization
        return pickle.loads(session_data)
    
    def execute_query(self, query):
        # Placeholder for database execution
        pass
'''
        (project_path / "app" / "auth" / "manager.py").write_text(auth_code)
        
        # Payment processing with vulnerabilities
        payment_code = '''
import os
import subprocess
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

class PaymentProcessor:
    def __init__(self):
        # Hardcoded encryption key
        self.encryption_key = b"1234567890123456"
        self.iv = b"1234567890123456"  # Static IV
    
    def encrypt_card_number(self, card_number):
        # Using ECB mode (insecure)
        cipher = Cipher(algorithms.AES(self.encryption_key), modes.ECB())
        encryptor = cipher.encryptor()
        return encryptor.update(card_number.encode())
    
    def process_refund(self, transaction_id):
        # Command injection vulnerability
        cmd = f"refund_tool --transaction {transaction_id}"
        os.system(cmd)
    
    def validate_amount(self, amount):
        # Using eval for validation (dangerous)
        return eval(f"{amount} > 0 and {amount} < 10000")
'''
        (project_path / "app" / "payments" / "processor.py").write_text(payment_code)
        
        # API endpoints with vulnerabilities
        api_code = '''
from flask import Flask, request, render_template_string, jsonify
import yaml

app = Flask(__name__)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    # XSS vulnerability
    return render_template_string(f'<h1>Search results for: {query}</h1>')

@app.route('/api/config', methods=['POST'])
def update_config():
    config_data = request.get_data()
    # Unsafe YAML deserialization
    config = yaml.load(config_data)
    return jsonify({"status": "updated"})

@app.route('/api/user/<user_id>')
def get_user(user_id):
    # SQL injection via string formatting
    query = "SELECT * FROM users WHERE id = %s" % user_id
    # Execute query...
    return jsonify({"user_id": user_id})

# Hardcoded AWS credentials
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
'''
        (project_path / "app" / "api" / "endpoints.py").write_text(api_code)
        
        # Configuration file with secrets
        config_code = '''
import os

# Database configuration
DATABASE_HOST = "localhost"
DATABASE_USER = "admin"
DATABASE_PASSWORD = "admin123"  # Hardcoded password

# API Keys
STRIPE_API_KEY = "sk_live_4eC39HqLyjWDarjtT1zdp7dc"
PAYPAL_CLIENT_SECRET = "EBWKjlELKMYqRNQ6sYvFo64FtaRLRR5BdHEESmha49TM"

# Encryption settings
ENCRYPTION_KEY = "weak-key-123"

# JWT Secret
JWT_SECRET = "jwt-secret-key"

# Redis password
REDIS_PASSWORD = "redis-password-123"
'''
        (project_path / "config" / "settings.py").write_text(config_code)
        
        # Create suppression rules file
        suppression_rules = {
            "rules": [
                {
                    "id": "suppress-test",
                    "pattern": "tests/.*",
                    "reason": "Test files are not production code",
                    "created_at": "2024-01-01T00:00:00",
                    "created_by": "security_team",
                    "active": True
                }
            ]
        }
        (project_path / "suppressions.json").write_text(json.dumps(suppression_rules))
        
        yield project_path
        shutil.rmtree(temp_dir)
    
    def test_full_scan_workflow(self, fintech_project):
        """Test the complete scanning workflow."""
        # Configure scanner
        config = ScannerConfig(
            max_workers=2,
            min_confidence_threshold=0.7,
            suppression_file=fintech_project / "suppressions.json",
            compliance_frameworks=["PCI-DSS", "SOC2"]
        )
        
        # Run scan
        scanner = SecurityScanner(config)
        scan_result = scanner.scan(str(fintech_project))
        
        # Verify scan completed
        assert scan_result.scan_id
        assert scan_result.total_files_scanned >= 4
        assert scan_result.total_lines_scanned > 0
        assert len(scan_result.vulnerabilities) > 0
        
        # Check vulnerability types detected
        vuln_types = {v.type for v in scan_result.vulnerabilities}
        assert VulnerabilityType.HARDCODED_SECRET in vuln_types
        assert VulnerabilityType.INJECTION in vuln_types
        assert VulnerabilityType.CRYPTO_FAILURE in vuln_types
        assert VulnerabilityType.INPUT_VALIDATION in vuln_types
        assert VulnerabilityType.XSS in vuln_types
        
        # Check severity levels
        severities = {v.severity for v in scan_result.vulnerabilities}
        assert SeverityLevel.CRITICAL in severities
        assert SeverityLevel.HIGH in severities
        
        # Generate compliance report
        compliance_report = scanner.generate_compliance_report(scan_result)
        
        assert compliance_report.report_id
        assert compliance_report.scan_result_id == scan_result.scan_id
        assert len(compliance_report.requirements) > 0
        assert compliance_report.compliance_scores
        
        # Check compliance scores (should be failing due to vulnerabilities)
        assert compliance_report.compliance_scores["PCI-DSS"] < 100
        assert compliance_report.compliance_scores["SOC2"] < 100
        
        # Export results
        with tempfile.TemporaryDirectory() as export_dir:
            export_path = Path(export_dir)
            
            # Export scan results as JSON
            scanner.export_results(
                scan_result,
                str(export_path / "scan_results.json"),
                "json"
            )
            assert (export_path / "scan_results.json").exists()
            
            # Export scan results as XML
            scanner.export_results(
                scan_result,
                str(export_path / "scan_results.xml"),
                "xml"
            )
            assert (export_path / "scan_results.xml").exists()
            
            # Verify JSON export
            with open(export_path / "scan_results.json", 'r') as f:
                json_data = json.load(f)
                assert json_data["scan_id"] == scan_result.scan_id
                assert len(json_data["vulnerabilities"]) == len(scan_result.vulnerabilities)
    
    def test_specific_vulnerability_detection(self, fintech_project):
        """Test detection of specific vulnerability patterns."""
        scanner = SecurityScanner()
        scan_result = scanner.scan(str(fintech_project))
        
        vulnerabilities = scan_result.vulnerabilities
        
        # Check hardcoded secrets
        secret_vulns = [v for v in vulnerabilities if v.type == VulnerabilityType.HARDCODED_SECRET]
        assert len(secret_vulns) >= 10  # Multiple secrets in the code
        
        # Verify specific secrets detected
        secret_titles = [v.title for v in secret_vulns]
        assert any("API" in title for title in secret_titles)
        assert any("Password" in title for title in secret_titles)
        assert any("AWS" in title for title in secret_titles)
        
        # Check SQL injection
        sql_vulns = [v for v in vulnerabilities if v.type == VulnerabilityType.INJECTION]
        assert len(sql_vulns) >= 2
        assert all(v.severity == SeverityLevel.CRITICAL for v in sql_vulns)
        
        # Check crypto failures
        crypto_vulns = [v for v in vulnerabilities if v.type == VulnerabilityType.CRYPTO_FAILURE]
        assert len(crypto_vulns) >= 3  # MD5, ECB mode, hardcoded IV
        
        # Check input validation
        input_vulns = [v for v in vulnerabilities if v.type == VulnerabilityType.INPUT_VALIDATION]
        assert len(input_vulns) >= 3  # eval, pickle, yaml.load
    
    def test_suppression_functionality(self, fintech_project):
        """Test that suppression rules work correctly."""
        # Add test file that should be suppressed
        test_file = fintech_project / "tests" / "test_auth.py"
        test_file.parent.mkdir(exist_ok=True)
        test_file.write_text('''
# Test file with vulnerabilities that should be suppressed
password = "test-password-123"
api_key = "sk-test-1234567890"
''')
        
        config = ScannerConfig(
            suppression_file=fintech_project / "suppressions.json"
        )
        scanner = SecurityScanner(config)
        scan_result = scanner.scan(str(fintech_project))
        
        # Check that test file vulnerabilities are suppressed
        test_vulns = [
            v for v in scan_result.vulnerabilities
            if "tests/" in str(v.location.file_path)
        ]
        
        assert all(v.suppressed for v in test_vulns)
        assert all(v.suppression_reason for v in test_vulns)
    
    def test_performance_requirements(self, fintech_project):
        """Test that performance requirements are met."""
        # Add more files to create a larger codebase
        for i in range(100):
            file_path = fintech_project / f"module_{i}.py"
            # Each file has 1000 lines
            content = '\n'.join([f"line_{j} = {j}" for j in range(1000)])
            file_path.write_text(content)
        
        scanner = SecurityScanner()
        import time
        
        start_time = time.time()
        scan_result = scanner.scan(str(fintech_project))
        duration = time.time() - start_time
        
        # Should scan 100,000+ lines
        assert scan_result.total_lines_scanned >= 100000
        
        # Should complete within 5 minutes (300 seconds)
        assert duration < 300
        
        # Verify scan completed successfully
        assert scan_result.scan_id
        assert scan_result.total_files_scanned >= 100
    
    def test_incremental_scan_simulation(self, fintech_project):
        """Test incremental scanning simulation."""
        scanner = SecurityScanner()
        
        # First scan
        first_scan = scanner.scan(str(fintech_project))
        first_vuln_count = len(first_scan.vulnerabilities)
        
        # Add a new vulnerable file
        new_file = fintech_project / "app" / "new_feature.py"
        new_file.write_text('''
password = "new-hardcoded-password"
def unsafe_query(user_input):
    query = "SELECT * FROM table WHERE id = " + user_input
    return query
''')
        
        # Second scan (would be incremental in real implementation)
        second_scan = scanner.scan(str(fintech_project))
        second_vuln_count = len(second_scan.vulnerabilities)
        
        # Should find additional vulnerabilities
        assert second_vuln_count > first_vuln_count
        
        # New vulnerabilities should be in the new file
        new_vulns = [
            v for v in second_scan.vulnerabilities
            if "new_feature.py" in str(v.location.file_path)
        ]
        assert len(new_vulns) >= 2  # Password and SQL injection
    
    def test_compliance_mapping_accuracy(self, fintech_project):
        """Test accuracy of compliance mappings."""
        scanner = SecurityScanner()
        scan_result = scanner.scan(str(fintech_project))
        compliance_report = scanner.generate_compliance_report(scan_result)
        
        # Check PCI-DSS mappings
        pci_requirements = [
            r for r in compliance_report.requirements
            if r.framework == "PCI-DSS"
        ]
        
        # Requirement 3.4 - Encryption of stored data
        req_3_4 = next((r for r in pci_requirements if r.requirement_id == "3.4"), None)
        assert req_3_4
        assert req_3_4.status == "not_compliant"  # Due to weak encryption
        
        # Requirement 6.5.1 - Injection flaws
        req_6_5_1 = next((r for r in pci_requirements if r.requirement_id == "6.5.1"), None)
        assert req_6_5_1
        assert req_6_5_1.status == "not_compliant"  # Due to SQL injection
        
        # Requirement 8.2.1 - Strong authentication
        req_8_2_1 = next((r for r in pci_requirements if r.requirement_id == "8.2.1"), None)
        assert req_8_2_1
        assert req_8_2_1.status == "not_compliant"  # Due to hardcoded credentials