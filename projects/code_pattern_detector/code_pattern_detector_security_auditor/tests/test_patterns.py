"""Tests for pattern detection."""

import ast
import pytest
from pathlib import Path

from pypatternguard.patterns import (
    HardcodedSecretDetector,
    SQLInjectionDetector,
    CryptographicMisuseDetector,
    InputValidationDetector,
)
from pypatternguard.models import VulnerabilityType, SeverityLevel


class TestHardcodedSecretDetector:
    """Test hardcoded secret detection."""
    
    def test_detect_api_key(self):
        """Test detection of hardcoded API keys."""
        detector = HardcodedSecretDetector()
        code = '''
api_key = "sk-1234567890abcdef1234567890abcdef"
API_SECRET = "abcdef1234567890abcdef1234567890"
        '''
        
        vulnerabilities = detector.detect(Path("test.py"), code)
        
        assert len(vulnerabilities) >= 2
        assert all(v.type == VulnerabilityType.HARDCODED_SECRET for v in vulnerabilities)
        assert any("API Key" in v.title for v in vulnerabilities)
        assert any("API Secret" in v.title for v in vulnerabilities)
    
    def test_detect_password(self):
        """Test detection of hardcoded passwords."""
        detector = HardcodedSecretDetector()
        code = '''
password = "mysecretpassword123"
db_password = "admin123456"
pwd = "shortpass"
        '''
        
        vulnerabilities = detector.detect(Path("test.py"), code)
        
        assert len(vulnerabilities) >= 3
        assert all(v.type == VulnerabilityType.HARDCODED_SECRET for v in vulnerabilities)
        assert all("Password" in v.title for v in vulnerabilities)
    
    def test_detect_aws_credentials(self):
        """Test detection of AWS credentials."""
        detector = HardcodedSecretDetector()
        code = '''
aws_access_key = "AKIAIOSFODNN7EXAMPLE"
aws_secret_access_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        '''
        
        vulnerabilities = detector.detect(Path("test.py"), code)
        
        assert len(vulnerabilities) >= 2
        assert any("AWS Access Key" in v.title for v in vulnerabilities)
        assert any("AWS Secret Key" in v.title for v in vulnerabilities)
        assert all(v.severity == SeverityLevel.HIGH for v in vulnerabilities)
    
    def test_detect_private_key(self):
        """Test detection of private keys."""
        detector = HardcodedSecretDetector()
        code = '''
private_key = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA1234567890...
-----END RSA PRIVATE KEY-----"""
        '''
        
        vulnerabilities = detector.detect(Path("test.py"), code)
        
        assert len(vulnerabilities) >= 1
        assert any("Private Key" in v.title for v in vulnerabilities)
        assert any(v.confidence == 1.0 for v in vulnerabilities)
    
    def test_skip_comments(self):
        """Test that secrets in comments are skipped."""
        detector = HardcodedSecretDetector()
        code = '''
# password = "this_is_in_a_comment"
# api_key = "sk-1234567890abcdef1234567890abcdef"
real_password = "actualpassword123"
        '''
        
        vulnerabilities = detector.detect(Path("test.py"), code)
        
        assert len(vulnerabilities) == 1
        assert vulnerabilities[0].location.line_start == 4


class TestSQLInjectionDetector:
    """Test SQL injection detection."""
    
    def test_detect_string_concatenation(self):
        """Test detection of SQL injection via string concatenation."""
        detector = SQLInjectionDetector()
        code = '''
user_id = request.args.get('id')
query = "SELECT * FROM users WHERE id = " + user_id
cursor.execute(query)
        '''
        
        vulnerabilities = detector.detect(Path("test.py"), code)
        
        assert len(vulnerabilities) >= 1
        assert all(v.type == VulnerabilityType.INJECTION for v in vulnerabilities)
        assert all(v.severity == SeverityLevel.CRITICAL for v in vulnerabilities)
    
    def test_detect_string_formatting(self):
        """Test detection of SQL injection via string formatting."""
        detector = SQLInjectionDetector()
        code = '''
username = request.form['username']
query = "SELECT * FROM users WHERE username = '%s'" % username
db.execute(query)
        '''
        
        vulnerabilities = detector.detect(Path("test.py"), code)
        
        assert len(vulnerabilities) >= 1
        assert any("SQL Injection" in v.title for v in vulnerabilities)
    
    def test_detect_f_string_injection(self):
        """Test detection of SQL injection via f-strings."""
        detector = SQLInjectionDetector()
        code = '''
user_input = request.json['search']
query = f"SELECT * FROM products WHERE name LIKE '{user_input}%'"
        '''
        
        vulnerabilities = detector.detect(Path("test.py"), code)
        
        assert len(vulnerabilities) >= 1
        assert all(v.cvss_score == 9.8 for v in vulnerabilities)
    
    def test_detect_format_method(self):
        """Test detection of SQL injection via format method."""
        detector = SQLInjectionDetector()
        code = '''
table = request.args.get('table')
query = "DROP TABLE {}".format(table)
        '''
        
        vulnerabilities = detector.detect(Path("test.py"), code)
        
        assert len(vulnerabilities) >= 1
        assert all("CWE-89" in v.cwe_ids for v in vulnerabilities)
    
    def test_ast_based_detection(self):
        """Test AST-based SQL injection detection."""
        detector = SQLInjectionDetector()
        code = '''
def unsafe_query(user_id):
    query = "SELECT * FROM users WHERE id = " + str(user_id)
    cursor.execute(query)
        '''
        
        tree = ast.parse(code)
        vulnerabilities = detector.detect(Path("test.py"), code, tree)
        
        assert len(vulnerabilities) >= 1
        # Verify we have SQL injection detection
        assert any(v.type == VulnerabilityType.INJECTION for v in vulnerabilities)


class TestCryptographicMisuseDetector:
    """Test cryptographic misuse detection."""
    
    def test_detect_weak_algorithms(self):
        """Test detection of weak cryptographic algorithms."""
        detector = CryptographicMisuseDetector()
        code = '''
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()
checksum = hashlib.sha1(data).hexdigest()
        '''
        
        vulnerabilities = detector.detect(Path("test.py"), code)
        
        assert len(vulnerabilities) >= 2
        assert all(v.type == VulnerabilityType.CRYPTO_FAILURE for v in vulnerabilities)
        assert any("MD5" in v.title for v in vulnerabilities)
        assert any("SHA-1" in v.title for v in vulnerabilities)
    
    def test_detect_weak_ciphers(self):
        """Test detection of weak ciphers."""
        detector = CryptographicMisuseDetector()
        code = '''
from Crypto.Cipher import DES, ARC4
cipher1 = DES.new(key, DES.MODE_ECB)
cipher2 = ARC4.new(key)
        '''
        
        vulnerabilities = detector.detect(Path("test.py"), code)
        
        assert len(vulnerabilities) >= 3  # DES, RC4, and ECB mode
        assert any(v.severity == SeverityLevel.CRITICAL for v in vulnerabilities)
    
    def test_detect_hardcoded_iv(self):
        """Test detection of hardcoded IVs."""
        detector = CryptographicMisuseDetector()
        code = '''
iv = "1234567890123456"
salt = "mysalt"
nonce = "abcdef123456"
        '''
        
        vulnerabilities = detector.detect(Path("test.py"), code)
        
        assert len(vulnerabilities) >= 3
        assert any("Hardcoded IV" in v.title for v in vulnerabilities)
        assert any("Hardcoded Salt" in v.title for v in vulnerabilities)
        assert any("Hardcoded Nonce" in v.title for v in vulnerabilities)
        assert all(v.severity == SeverityLevel.HIGH for v in vulnerabilities)
    
    def test_compliance_mappings(self):
        """Test that crypto failures have correct compliance mappings."""
        detector = CryptographicMisuseDetector()
        code = 'password_hash = md5(password)'
        
        vulnerabilities = detector.detect(Path("test.py"), code)
        
        assert len(vulnerabilities) >= 1
        vuln = vulnerabilities[0]
        assert "PCI-DSS" in vuln.compliance_mappings
        assert "3.4" in vuln.compliance_mappings["PCI-DSS"]


class TestInputValidationDetector:
    """Test input validation vulnerability detection."""
    
    def test_detect_eval_usage(self):
        """Test detection of eval with user input."""
        detector = InputValidationDetector()
        code = '''
user_code = request.form['code']
result = eval(user_code)
        '''
        
        tree = ast.parse(code)
        vulnerabilities = detector.detect(Path("test.py"), code, tree)
        
        assert len(vulnerabilities) >= 1
        assert all(v.type == VulnerabilityType.INPUT_VALIDATION for v in vulnerabilities)
        assert any("eval" in v.title for v in vulnerabilities)
        assert all(v.severity == SeverityLevel.CRITICAL for v in vulnerabilities)
    
    def test_detect_exec_usage(self):
        """Test detection of exec with user input."""
        detector = InputValidationDetector()
        code = '''
script = request.data
exec(script)
        '''
        
        tree = ast.parse(code)
        vulnerabilities = detector.detect(Path("test.py"), code, tree)
        
        assert len(vulnerabilities) >= 1
        assert any("Code Injection" in v.description for v in vulnerabilities)
    
    def test_detect_pickle_loads(self):
        """Test detection of unsafe deserialization."""
        detector = InputValidationDetector()
        code = '''
import pickle
data = request.get_data()
obj = pickle.loads(data)
        '''
        
        tree = ast.parse(code)
        vulnerabilities = detector.detect(Path("test.py"), code, tree)
        
        assert len(vulnerabilities) >= 1
        assert any("Deserialization" in v.description for v in vulnerabilities)
        assert all(v.severity == SeverityLevel.CRITICAL for v in vulnerabilities)
    
    def test_detect_command_injection(self):
        """Test detection of command injection vulnerabilities."""
        detector = InputValidationDetector()
        code = '''
filename = request.args.get('file')
os.system(f"cat {filename}")
subprocess.call(["ls", user_input])
        '''
        
        tree = ast.parse(code)
        vulnerabilities = detector.detect(Path("test.py"), code, tree)
        
        assert len(vulnerabilities) >= 2
        assert any("Command Injection" in v.description for v in vulnerabilities)
    
    def test_detect_xss_vulnerabilities(self):
        """Test detection of XSS vulnerabilities."""
        detector = InputValidationDetector()
        code = '''
from flask import render_template_string, Markup
user_name = request.args.get('name')
html = render_template_string('<h1>Hello {{ name|safe }}</h1>', name=user_name)
markup = Markup(user_input)
        '''
        
        tree = ast.parse(code)
        vulnerabilities = detector.detect(Path("test.py"), code, tree)
        
        assert len(vulnerabilities) >= 2
        assert any(v.type == VulnerabilityType.XSS for v in vulnerabilities)
        assert all("CWE-79" in v.cwe_ids for v in vulnerabilities)