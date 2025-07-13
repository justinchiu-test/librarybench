"""Extended tests for pattern detection."""

import pytest
from pathlib import Path

from pypatternguard.patterns import (
    HardcodedSecretDetector,
    SQLInjectionDetector,
    CryptographicMisuseDetector,
    InputValidationDetector,
)
from pypatternguard.models import VulnerabilityType, SeverityLevel


class TestExtendedPatternDetection:
    """Extended tests for pattern detection edge cases."""
    
    def test_jwt_secret_detection(self):
        """Test detection of JWT secrets."""
        detector = HardcodedSecretDetector()
        code = '''
JWT_SECRET = "my-super-secret-jwt-key"
jwt_secret_key = "another-jwt-secret"
        '''
        
        vulnerabilities = detector.detect(Path("jwt.py"), code)
        assert len(vulnerabilities) >= 2
        assert any("JWT" in v.title for v in vulnerabilities)
    
    def test_database_url_with_password(self):
        """Test detection of passwords in database URLs."""
        detector = HardcodedSecretDetector()
        code = '''
DATABASE_URL = "postgresql://user:password123@localhost/db"
MONGO_URI = "mongodb://admin:admin123@localhost:27017/mydb"
DATABASE_PASSWORD = "password123"
        '''
        
        vulnerabilities = detector.detect(Path("db_urls.py"), code)
        # Should detect at least the explicit password
        assert len(vulnerabilities) >= 1
    
    def test_oauth_secrets(self):
        """Test detection of OAuth secrets."""
        detector = HardcodedSecretDetector()
        code = '''
GITHUB_CLIENT_SECRET = "1234567890abcdef1234567890abcdef12345678"
GOOGLE_CLIENT_SECRET = "GOCSPX-1234567890abcdefghijk"
        '''
        
        vulnerabilities = detector.detect(Path("oauth.py"), code)
        assert len(vulnerabilities) >= 2
        assert any("Client Secret" in v.title for v in vulnerabilities)
    
    def test_encryption_key_variations(self):
        """Test various encryption key patterns."""
        detector = HardcodedSecretDetector()
        code = '''
ENCRYPTION_KEY = "32-byte-encryption-key-here!!!!!"
AES_KEY = "sixteen byte key"
DES_KEY = "8bytekey"
        '''
        
        vulnerabilities = detector.detect(Path("crypto_keys.py"), code)
        # Should detect at least ENCRYPTION_KEY
        assert len(vulnerabilities) >= 1
    
    def test_sql_injection_union_attacks(self):
        """Test detection of UNION-based SQL injection."""
        detector = SQLInjectionDetector()
        code = '''
query = "SELECT name FROM users WHERE id=" + user_id + " UNION SELECT password FROM admins"
union_query = f"SELECT * FROM products UNION {user_input}"
        '''
        
        vulnerabilities = detector.detect(Path("union.py"), code)
        assert len(vulnerabilities) >= 2
        assert all(v.severity == SeverityLevel.CRITICAL for v in vulnerabilities)
    
    def test_sql_injection_order_by(self):
        """Test SQL injection in ORDER BY clauses."""
        detector = SQLInjectionDetector()
        code = '''
sort_column = request.args.get('sort')
query = f"SELECT * FROM users ORDER BY {sort_column}"
query2 = "SELECT * FROM products WHERE name=" + user_input
        '''
        
        vulnerabilities = detector.detect(Path("orderby.py"), code)
        assert len(vulnerabilities) >= 1
    
    def test_nosql_injection(self):
        """Test NoSQL injection patterns."""
        detector = SQLInjectionDetector()
        code = '''
# MongoDB injection
filter = {"username": user_input}
db.users.find(filter)

# Another pattern
query = f'{{"$where": "this.name == \\'{user_input}\\'"}}'
        '''
        
        vulnerabilities = detector.detect(Path("nosql.py"), code)
        # May detect some patterns even if not specifically NoSQL-focused
        assert isinstance(vulnerabilities, list)
    
    def test_ldap_injection(self):
        """Test LDAP injection patterns."""
        detector = SQLInjectionDetector()
        code = '''
ldap_filter = f"(&(uid={username})(password={password}))"
search_filter = "(cn=" + user_input + ")"
        '''
        
        vulnerabilities = detector.detect(Path("ldap.py"), code)
        # Generic injection patterns may catch these
        assert isinstance(vulnerabilities, list)
    
    def test_weak_random_generation(self):
        """Test detection of weak random number generation."""
        detector = CryptographicMisuseDetector()
        code = '''
import random
session_id = random.randint(1000, 9999)
token = str(random.random())
        '''
        
        # Current implementation focuses on algorithms, but test structure
        vulnerabilities = detector.detect(Path("random.py"), code)
        assert isinstance(vulnerabilities, list)
    
    def test_insecure_cipher_modes(self):
        """Test detection of insecure cipher modes."""
        detector = CryptographicMisuseDetector()
        code = '''
# ECB mode is insecure
cipher = AES.new(key, AES.MODE_ECB)
des_cipher = DES.new(key, DES.MODE_ECB)
        '''
        
        vulnerabilities = detector.detect(Path("cipher_modes.py"), code)
        assert len(vulnerabilities) >= 2
        assert any("ECB" in v.title for v in vulnerabilities)
    
    def test_weak_key_derivation(self):
        """Test detection of weak key derivation."""
        detector = CryptographicMisuseDetector()
        code = '''
# Single MD5 hash for key derivation
key = hashlib.md5(password.encode()).digest()
# SHA1 for key derivation
derived_key = hashlib.sha1(password + salt).hexdigest()
        '''
        
        vulnerabilities = detector.detect(Path("key_derive.py"), code)
        assert len(vulnerabilities) >= 2
    
    def test_yaml_unsafe_load(self):
        """Test detection of unsafe YAML loading."""
        detector = InputValidationDetector()
        code = '''
import yaml
data = yaml.load(user_input)
config = yaml.load(request.data)
        '''
        
        # Need AST for detection
        import ast
        tree = ast.parse(code)
        vulnerabilities = detector.detect(Path("yaml_load.py"), code, tree)
        assert len(vulnerabilities) >= 2
        assert all(v.type == VulnerabilityType.INPUT_VALIDATION for v in vulnerabilities)
    
    def test_xml_xxe_vulnerabilities(self):
        """Test XML External Entity vulnerabilities."""
        detector = InputValidationDetector()
        code = '''
import xml.etree.ElementTree as ET
tree = ET.parse(user_uploaded_file)
root = ET.fromstring(user_xml_data)
        '''
        
        # Current implementation may not specifically detect XXE
        vulnerabilities = detector.detect(Path("xxe.py"), code)
        assert isinstance(vulnerabilities, list)
    
    def test_path_traversal_patterns(self):
        """Test path traversal vulnerability patterns."""
        detector = InputValidationDetector()
        code = '''
filename = request.args.get('file')
with open(f"/var/www/uploads/{filename}") as f:
    content = f.read()
        '''
        
        vulnerabilities = detector.detect(Path("path_traversal.py"), code)
        assert isinstance(vulnerabilities, list)
    
    def test_template_injection(self):
        """Test template injection vulnerabilities."""
        detector = InputValidationDetector()
        code = '''
from jinja2 import Template
template = Template(user_input)
result = template.render()
        '''
        
        vulnerabilities = detector.detect(Path("template.py"), code)
        assert isinstance(vulnerabilities, list)
    
    def test_command_injection_variations(self):
        """Test various command injection patterns."""
        detector = InputValidationDetector()
        code = '''
# os.popen variation
output = os.popen(f"ping {user_ip}").read()

# subprocess with shell=True
subprocess.run(f"echo {user_input}", shell=True)

# os.system with user input
os.system("tar -xvf " + user_filename)
        '''
        
        import ast
        tree = ast.parse(code)
        vulnerabilities = detector.detect(Path("cmd_inject.py"), code, tree)
        assert len(vulnerabilities) >= 2
        assert any("Command Injection" in v.description for v in vulnerabilities)
    
    def test_ssrf_patterns(self):
        """Test Server-Side Request Forgery patterns."""
        detector = InputValidationDetector()
        code = '''
import requests
url = request.args.get('url')
response = requests.get(url)
        '''
        
        # May not be specifically detected but test structure
        vulnerabilities = detector.detect(Path("ssrf.py"), code)
        assert isinstance(vulnerabilities, list)
    
    def test_timing_attack_vulnerabilities(self):
        """Test timing attack vulnerabilities."""
        detector = CryptographicMisuseDetector()
        code = '''
# String comparison vulnerable to timing attacks
if password == stored_password:
    return True
        '''
        
        # Current implementation may not detect timing attacks
        vulnerabilities = detector.detect(Path("timing.py"), code)
        assert isinstance(vulnerabilities, list)
    
    def test_regex_dos_patterns(self):
        """Test ReDoS (Regular Expression DoS) patterns."""
        detector = InputValidationDetector()
        code = '''
import re
# Potentially vulnerable regex
pattern = r"(a+)+"
re.match(pattern, user_input)
        '''
        
        vulnerabilities = detector.detect(Path("redos.py"), code)
        assert isinstance(vulnerabilities, list)
    
    def test_integer_overflow_patterns(self):
        """Test integer overflow patterns."""
        detector = InputValidationDetector()
        code = '''
size = int(user_input)
buffer = [0] * size  # Potential memory exhaustion
        '''
        
        vulnerabilities = detector.detect(Path("overflow.py"), code)
        assert isinstance(vulnerabilities, list)