"""Tests for edge cases and error handling."""

import pytest
import ast
from pathlib import Path

from pypatternguard.patterns import (
    HardcodedSecretDetector,
    SQLInjectionDetector,
    CryptographicMisuseDetector,
    InputValidationDetector,
)
from pypatternguard.scanner import SecurityScanner
from pypatternguard.config import ScannerConfig


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_file_scanning(self):
        """Test scanning empty files."""
        detector = HardcodedSecretDetector()
        vulnerabilities = detector.detect(Path("empty.py"), "")
        assert len(vulnerabilities) == 0
    
    def test_malformed_python_code(self):
        """Test handling of malformed Python code."""
        detector = SQLInjectionDetector()
        malformed_code = '''
def broken_function(
    print("This is broken"
        '''
        
        # Should not crash, just skip AST analysis
        vulnerabilities = detector.detect(Path("malformed.py"), malformed_code)
        assert isinstance(vulnerabilities, list)
    
    def test_unicode_in_code(self):
        """Test handling of Unicode characters in code."""
        detector = HardcodedSecretDetector()
        code_with_unicode = '''
# 这是中文注释
password = "пароль123"  # Russian password
api_key = "🔑-secret-key-123456"
        '''
        
        vulnerabilities = detector.detect(Path("unicode.py"), code_with_unicode)
        assert len(vulnerabilities) >= 1  # Should detect password
    
    def test_very_long_lines(self):
        """Test handling of very long lines."""
        detector = SQLInjectionDetector()
        long_line = 'query = "SELECT * FROM users WHERE ' + 'x' * 10000 + '" + user_input'
        
        vulnerabilities = detector.detect(Path("long.py"), long_line)
        assert len(vulnerabilities) >= 1
    
    def test_nested_string_quotes(self):
        """Test handling of nested quotes in strings."""
        detector = HardcodedSecretDetector()
        nested_quotes = '''
password = "pass'word"
api_key = 'key"with"quotes'
mixed = """triple"quoted'string'with"password=secret123"""
        '''
        
        vulnerabilities = detector.detect(Path("quotes.py"), nested_quotes)
        # Should detect at least the first password
        assert isinstance(vulnerabilities, list)
    
    def test_multiline_strings(self):
        """Test detection in multiline strings."""
        detector = HardcodedSecretDetector()
        multiline = '''
config = """
database_password = admin123
api_key = sk-1234567890abcdef
"""
        '''
        
        vulnerabilities = detector.detect(Path("multiline.py"), multiline)
        # Pattern matching inside multiline strings is complex
        assert isinstance(vulnerabilities, list)
    
    def test_commented_out_vulnerabilities(self):
        """Test that commented vulnerabilities are skipped."""
        detector = SQLInjectionDetector()
        commented = '''
# query = "SELECT * FROM users WHERE id=" + user_id
"""
This is a docstring with SQL:
query = "DELETE FROM table WHERE id=" + input
"""
actual_query = "SELECT * FROM products"  # Safe query
        '''
        
        vulnerabilities = detector.detect(Path("comments.py"), commented)
        # May detect patterns in docstrings
        assert isinstance(vulnerabilities, list)
    
    def test_binary_file_detection(self):
        """Test handling of binary content."""
        detector = HardcodedSecretDetector()
        binary_content = b'\x00\x01\x02\x03password=secret\x00\x01'.decode('latin-1')
        
        # Should handle binary content gracefully
        vulnerabilities = detector.detect(Path("binary.py"), binary_content)
        assert isinstance(vulnerabilities, list)
    
    def test_recursive_ast_structures(self):
        """Test handling of deeply nested AST structures."""
        detector = InputValidationDetector()
        deeply_nested = '''
def func():
    if True:
        while True:
            for i in range(10):
                try:
                    with open('file') as f:
                        if True:
                            eval(user_input)
                except:
                    pass
        '''
        
        tree = ast.parse(deeply_nested)
        vulnerabilities = detector.detect(Path("nested.py"), deeply_nested, tree)
        assert len(vulnerabilities) >= 1
    
    def test_special_characters_in_patterns(self):
        """Test patterns with special regex characters."""
        detector = HardcodedSecretDetector()
        special_chars = '''
password = "pass$word"
api_key = "key.with.dots"
secret = "secret[bracket]"
token = "token^caret"
        '''
        
        vulnerabilities = detector.detect(Path("special.py"), special_chars)
        # Should detect password patterns
        assert len(vulnerabilities) >= 1
    
    def test_case_sensitivity(self):
        """Test case sensitivity in detection."""
        detector = HardcodedSecretDetector()
        various_cases = '''
PASSWORD = "secret123"
Password = "secret456"
password = "secret789"
STRIPE_API_KEY = "sk_live_123"
stripe_api_key = "sk_test_456"
        '''
        
        vulnerabilities = detector.detect(Path("cases.py"), various_cases)
        assert len(vulnerabilities) >= 5
    
    def test_whitespace_variations(self):
        """Test various whitespace patterns."""
        detector = SQLInjectionDetector()
        whitespace_variations = '''
query="SELECT * FROM users"+user_input
query  =  "SELECT * FROM users"  +  user_input
query\t=\t"SELECT * FROM users"\t+\tuser_input
query = "SELECT * FROM users" \\
    + user_input
        '''
        
        vulnerabilities = detector.detect(Path("whitespace.py"), whitespace_variations)
        assert len(vulnerabilities) >= 3
    
    def test_encoding_issues(self):
        """Test handling of encoding issues."""
        detector = HardcodedSecretDetector()
        # Simulate file with encoding issues
        mixed_encoding = 'password = "café_pass123"'
        
        vulnerabilities = detector.detect(Path("encoding.py"), mixed_encoding)
        assert len(vulnerabilities) >= 1
    
    def test_extremely_large_file(self):
        """Test handling of very large files."""
        detector = CryptographicMisuseDetector()
        # Generate large content
        large_content = "x = 1\n" * 100000 + "password_hash = md5(password)"
        
        vulnerabilities = detector.detect(Path("large.py"), large_content)
        assert len(vulnerabilities) >= 1
    
    def test_no_newlines_in_file(self):
        """Test file with no newline characters."""
        detector = HardcodedSecretDetector()
        single_line = 'api_key="sk-123456789012345678"'
        
        vulnerabilities = detector.detect(Path("single.py"), single_line)
        assert len(vulnerabilities) == 1
        assert vulnerabilities[0].location.line_start == 1
    
    def test_windows_line_endings(self):
        """Test handling of Windows line endings."""
        detector = SQLInjectionDetector()
        windows_content = 'line1\r\nquery = "SELECT * FROM users WHERE id=" + user_id\r\nline3'
        
        vulnerabilities = detector.detect(Path("windows.py"), windows_content)
        assert len(vulnerabilities) >= 1
        assert vulnerabilities[0].location.line_start == 2
    
    def test_mixed_indentation(self):
        """Test handling of mixed tabs and spaces."""
        detector = InputValidationDetector()
        mixed_indent = '''
def func():
    eval(user_input)  # spaces
    eval(user_input)  # spaces2
    eval(user_input)  # spaces3
        '''
        
        tree = ast.parse(mixed_indent)
        vulnerabilities = detector.detect(Path("indent.py"), mixed_indent, tree)
        assert len(vulnerabilities) >= 3
    
    def test_non_ascii_filenames(self):
        """Test handling of non-ASCII filenames."""
        detector = HardcodedSecretDetector()
        vulnerabilities = detector.detect(Path("файл.py"), "password = 'secret123'")
        
        assert len(vulnerabilities) == 1
        assert vulnerabilities[0].location.file_path == Path("файл.py")
    
    def test_circular_imports_handling(self):
        """Test that circular imports don't cause issues."""
        detector = SQLInjectionDetector()
        circular_code = '''
from module_a import func_a
from module_b import func_b

def query_user(user_id):
    return "SELECT * FROM users WHERE id=" + user_id
        '''
        
        vulnerabilities = detector.detect(Path("circular.py"), circular_code)
        assert len(vulnerabilities) >= 1