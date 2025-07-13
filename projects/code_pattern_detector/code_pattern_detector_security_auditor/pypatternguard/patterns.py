"""Security pattern definitions and detection logic."""

import ast
import re
from typing import List, Dict, Any, Optional, Set, Tuple
from pathlib import Path

from .models import Vulnerability, VulnerabilityType, SeverityLevel, Location


class PatternDetector:
    """Base class for pattern detection."""
    
    def __init__(self):
        self.vulnerabilities: List[Vulnerability] = []
    
    def detect(self, file_path: Path, content: str, tree: Optional[ast.AST] = None) -> List[Vulnerability]:
        """Detect patterns in file content."""
        raise NotImplementedError


class HardcodedSecretDetector(PatternDetector):
    """Detects hardcoded secrets and credentials."""
    
    SECRET_PATTERNS = {
        # API Keys
        r'(?i)["\']?api[_-]?key["\']?\s*[:=]\s*["\'][a-zA-Z0-9\-]{16,}["\']': ("API Key", 0.9),
        r'(?i)["\']?api[_-]?secret["\']?\s*[:=]\s*["\'][a-zA-Z0-9]{16,}["\']': ("API Secret", 0.9),
        
        # Passwords
        r'["\']?password["\']?\s*[:=]\s*["\'][^"\']+["\']': ("Hardcoded Password", 0.8),
        r'["\']?passwd["\']?\s*[:=]\s*["\'][^"\']+["\']': ("Hardcoded Password", 0.8),
        r'["\']?pwd["\']?\s*[:=]\s*["\'][^"\']+["\']': ("Hardcoded Password", 0.7),
        r'(?i)["\']?database[_-]?password["\']?\s*[:=]\s*["\'][^"\']+["\']': ("Database Password", 0.8),
        
        # Tokens
        r'["\']?token["\']?\s*[:=]\s*["\'][a-zA-Z0-9]{20,}["\']': ("Authentication Token", 0.9),
        r'["\']?auth[_-]?token["\']?\s*[:=]\s*["\'][a-zA-Z0-9]{20,}["\']': ("Auth Token", 0.9),
        
        # Database credentials
        r'["\']?db[_-]?password["\']?\s*[:=]\s*["\'][^"\']+["\']': ("Database Password", 0.8),
        
        # AWS credentials
        r'AKIA[0-9A-Z]{16}': ("AWS Access Key", 0.95),
        r'["\']?aws[_-]?secret[_-]?access[_-]?key["\']?\s*[:=]\s*["\'][a-zA-Z0-9/+=]{40}["\']': ("AWS Secret Key", 0.95),
        
        # Private keys
        r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----': ("Private Key", 1.0),
        r'["\']?private[_-]?key["\']?\s*[:=]\s*["\'][^"\']{50,}["\']': ("Private Key", 0.85),
        
        # Additional secrets for comprehensive detection
        r'["\']?secret[_-]?key["\']?\s*[:=]\s*["\'][^"\']+["\']': ("Secret Key", 0.8),
        r'["\']?client[_-]?secret["\']?\s*[:=]\s*["\'][^"\']+["\']': ("Client Secret", 0.8),
        r'(?i)stripe[_-]?api[_-]?key["\']?\s*[:=]\s*["\'][^"\']+["\']': ("Stripe API Key", 0.9),
        r'(?i)paypal[_-]?client[_-]?secret["\']?\s*[:=]\s*["\'][^"\']+["\']': ("PayPal Secret", 0.9),
        r'(?i)jwt[_-]?secret["\']?\s*[:=]\s*["\'][^"\']+["\']': ("JWT Secret", 0.85),
        r'(?i)redis[_-]?password["\']?\s*[:=]\s*["\'][^"\']+["\']': ("Redis Password", 0.85),
        r'(?i)encryption[_-]?key["\']?\s*[:=]\s*["\'][^"\']+["\']': ("Encryption Key", 0.85),
    }
    
    def detect(self, file_path: Path, content: str, tree: Optional[ast.AST] = None) -> List[Vulnerability]:
        """Detect hardcoded secrets in code."""
        vulnerabilities = []
        lines = content.split('\n')
        
        for pattern, (secret_type, confidence) in self.SECRET_PATTERNS.items():
            for match in re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
                line_num = content[:match.start()].count('\n') + 1
                
                # Skip if in comment
                line = lines[line_num - 1] if line_num <= len(lines) else ""
                if line.strip().startswith('#') or line.strip().startswith('//'):
                    continue
                
                vuln = Vulnerability(
                    id=f"SEC-{file_path.name}-{line_num}-{len(vulnerabilities)}",
                    type=VulnerabilityType.HARDCODED_SECRET,
                    severity=SeverityLevel.HIGH,
                    title=f"Hardcoded {secret_type} Detected",
                    description=f"A hardcoded {secret_type} was found in the code. "
                               f"Secrets should be stored in environment variables or secure vaults.",
                    location=Location(
                        file_path=file_path,
                        line_start=line_num,
                        line_end=line_num,
                        column_start=match.start() - content.rfind('\n', 0, match.start()),
                        column_end=match.end() - content.rfind('\n', 0, match.end())
                    ),
                    code_snippet=self._get_code_snippet(lines, line_num),
                    remediation="Store secrets in environment variables or use a secrets management system. "
                               "Never commit secrets to version control.",
                    cwe_ids=["CWE-798", "CWE-259"],
                    confidence=confidence,
                    compliance_mappings={
                        "PCI-DSS": ["2.3", "8.2.1"],
                        "SOC2": ["CC6.1", "CC6.7"]
                    }
                )
                vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _get_code_snippet(self, lines: List[str], line_num: int, context: int = 3) -> str:
        """Get code snippet with context."""
        start = max(0, line_num - context - 1)
        end = min(len(lines), line_num + context)
        return '\n'.join(lines[start:end])


class SQLInjectionDetector(PatternDetector):
    """Detects potential SQL injection vulnerabilities."""
    
    UNSAFE_SQL_PATTERNS = [
        # String concatenation
        (r'(?:SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION).*?\+.*?(?:request|params|args|input|data|user)', 0.9),
        # String formatting
        (r'(?:SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION).*?%\s*(?:s|d).*?%.*?(?:request|params|args|input|data|user)', 0.8),
        # f-strings with user input
        (r'f["\'].*?(?:SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION).*?\{.*?(?:request|params|args|input|data|user).*?\}', 0.9),
        # .format() with user input
        (r'["\'].*?(?:SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION).*?["\']\.format\(.*?(?:request|params|args|input|data|user|table)', 0.85),
        # Additional format pattern for table names
        (r'(?:DROP|CREATE|ALTER)\s+TABLE\s+\{\}.*?\.format', 0.9),
    ]
    
    def detect(self, file_path: Path, content: str, tree: Optional[ast.AST] = None) -> List[Vulnerability]:
        """Detect SQL injection vulnerabilities."""
        vulnerabilities = []
        lines = content.split('\n')
        
        for pattern, confidence in self.UNSAFE_SQL_PATTERNS:
            for match in re.finditer(pattern, content, re.IGNORECASE | re.DOTALL):
                line_num = content[:match.start()].count('\n') + 1
                
                vuln = Vulnerability(
                    id=f"SQLI-{file_path.name}-{line_num}-{len(vulnerabilities)}",
                    type=VulnerabilityType.INJECTION,
                    severity=SeverityLevel.CRITICAL,
                    title="Potential SQL Injection Vulnerability",
                    description="User input appears to be directly concatenated or formatted into SQL query. "
                               "This can lead to SQL injection attacks.",
                    location=Location(
                        file_path=file_path,
                        line_start=line_num,
                        line_end=line_num + match.group().count('\n')
                    ),
                    code_snippet=self._get_code_snippet(lines, line_num),
                    remediation="Use parameterized queries or prepared statements. "
                               "Never concatenate or format user input directly into SQL queries.",
                    cwe_ids=["CWE-89"],
                    cvss_score=9.8,
                    confidence=confidence,
                    compliance_mappings={
                        "PCI-DSS": ["6.5.1"],
                        "SOC2": ["CC6.1"]
                    }
                )
                vulnerabilities.append(vuln)
        
        # AST-based detection
        if tree:
            vulnerabilities.extend(self._detect_ast_patterns(file_path, tree, lines))
        
        return vulnerabilities
    
    def _detect_ast_patterns(self, file_path: Path, tree: ast.AST, lines: List[str]) -> List[Vulnerability]:
        """Detect SQL injection patterns using AST analysis."""
        vulnerabilities = []
        
        class SQLVisitor(ast.NodeVisitor):
            def __init__(self):
                self.vulns = []
            
            def visit_Call(self, node):
                # Check for execute() calls with string operations
                if (hasattr(node.func, 'attr') and 
                    node.func.attr in ['execute', 'executemany', 'executescript'] and
                    node.args):
                    
                    sql_arg = node.args[0]
                    if self._is_unsafe_sql(sql_arg):
                        vuln = Vulnerability(
                            id=f"SQLI-AST-{file_path.name}-{node.lineno}",
                            type=VulnerabilityType.INJECTION,
                            severity=SeverityLevel.CRITICAL,
                            title="SQL Injection via String Operation",
                            description="SQL query constructed using string operations with potential user input.",
                            location=Location(
                                file_path=file_path,
                                line_start=node.lineno,
                                line_end=node.end_lineno or node.lineno
                            ),
                            code_snippet='\n'.join(lines[max(0, node.lineno-4):node.lineno+3]),
                            remediation="Use parameterized queries instead of string concatenation.",
                            cwe_ids=["CWE-89"],
                            cvss_score=9.8,
                            confidence=0.85,
                            compliance_mappings={
                                "PCI-DSS": ["6.5.1"],
                                "SOC2": ["CC6.1"]
                            }
                        )
                        self.vulns.append(vuln)
                
                self.generic_visit(node)
            
            def _is_unsafe_sql(self, node) -> bool:
                """Check if SQL construction is unsafe."""
                if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Mod)):
                    return True
                if isinstance(node, ast.JoinedStr):  # f-string
                    return True
                if isinstance(node, ast.Call) and hasattr(node.func, 'attr') and node.func.attr == 'format':
                    return True
                return False
        
        visitor = SQLVisitor()
        visitor.visit(tree)
        return visitor.vulns
    
    def _get_code_snippet(self, lines: List[str], line_num: int, context: int = 3) -> str:
        """Get code snippet with context."""
        start = max(0, line_num - context - 1)
        end = min(len(lines), line_num + context)
        return '\n'.join(lines[start:end])


class CryptographicMisuseDetector(PatternDetector):
    """Detects cryptographic misuse and weak algorithms."""
    
    WEAK_ALGORITHMS = {
        'md5': ('MD5', SeverityLevel.HIGH),
        'sha1': ('SHA-1', SeverityLevel.HIGH),
        'des': ('DES', SeverityLevel.CRITICAL),
        '3des': ('3DES', SeverityLevel.HIGH),
        'rc4': ('RC4', SeverityLevel.CRITICAL),
        'ecb': ('ECB mode', SeverityLevel.HIGH),
    }
    
    WEAK_KEY_SIZES = {
        'rsa': 2048,  # Minimum recommended
        'dsa': 2048,
        'ecdsa': 224,
        'aes': 128,
    }
    
    def detect(self, file_path: Path, content: str, tree: Optional[ast.AST] = None) -> List[Vulnerability]:
        """Detect cryptographic misuse."""
        vulnerabilities = []
        lines = content.split('\n')
        
        # Check for weak algorithms
        for algo, (name, severity) in self.WEAK_ALGORITHMS.items():
            pattern = rf'\b{algo}\b'
            for match in re.finditer(pattern, content, re.IGNORECASE):
                line_num = content[:match.start()].count('\n') + 1
                
                vuln = Vulnerability(
                    id=f"CRYPTO-{file_path.name}-{line_num}-{algo}",
                    type=VulnerabilityType.CRYPTO_FAILURE,
                    severity=severity,
                    title=f"Weak Cryptographic Algorithm: {name}",
                    description=f"The {name} algorithm is considered cryptographically weak and should not be used.",
                    location=Location(
                        file_path=file_path,
                        line_start=line_num,
                        line_end=line_num
                    ),
                    code_snippet=self._get_code_snippet(lines, line_num),
                    remediation=f"Replace {name} with a stronger algorithm. "
                               f"Use SHA-256 or SHA-3 for hashing, AES for encryption.",
                    cwe_ids=["CWE-327", "CWE-326"],
                    confidence=0.9,
                    compliance_mappings={
                        "PCI-DSS": ["3.4", "4.1"],
                        "SOC2": ["CC6.1"]
                    }
                )
                vulnerabilities.append(vuln)
        
        # Check for hardcoded IVs and salts
        iv_patterns = [
            (r'iv\s*=\s*["\'][a-fA-F0-9]{16,32}["\']', "Hardcoded IV"),
            (r'salt\s*=\s*["\'][^"\']+["\']', "Hardcoded Salt"),
            (r'nonce\s*=\s*["\'][a-fA-F0-9]+["\']', "Hardcoded Nonce"),
        ]
        
        for pattern, issue in iv_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                line_num = content[:match.start()].count('\n') + 1
                
                vuln = Vulnerability(
                    id=f"CRYPTO-IV-{file_path.name}-{line_num}",
                    type=VulnerabilityType.CRYPTO_FAILURE,
                    severity=SeverityLevel.HIGH,
                    title=f"{issue} Detected",
                    description=f"{issue} makes encryption predictable and vulnerable to attacks.",
                    location=Location(
                        file_path=file_path,
                        line_start=line_num,
                        line_end=line_num
                    ),
                    code_snippet=self._get_code_snippet(lines, line_num),
                    remediation="Generate random IVs, salts, and nonces for each encryption operation.",
                    cwe_ids=["CWE-329", "CWE-760"],
                    confidence=0.95,
                    compliance_mappings={
                        "PCI-DSS": ["3.4"],
                        "SOC2": ["CC6.1"]
                    }
                )
                vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _get_code_snippet(self, lines: List[str], line_num: int, context: int = 3) -> str:
        """Get code snippet with context."""
        start = max(0, line_num - context - 1)
        end = min(len(lines), line_num + context)
        return '\n'.join(lines[start:end])


class InputValidationDetector(PatternDetector):
    """Detects missing input validation vulnerabilities."""
    
    DANGEROUS_FUNCTIONS = {
        'eval': ('Code Injection', SeverityLevel.CRITICAL),
        'exec': ('Code Injection', SeverityLevel.CRITICAL),
        'compile': ('Code Injection', SeverityLevel.CRITICAL),
        '__import__': ('Code Injection', SeverityLevel.HIGH),
        'pickle.loads': ('Deserialization', SeverityLevel.CRITICAL),
        'yaml.load': ('Deserialization', SeverityLevel.HIGH),
        'subprocess.call': ('Command Injection', SeverityLevel.HIGH),
        'subprocess.run': ('Command Injection', SeverityLevel.HIGH),
        'os.system': ('Command Injection', SeverityLevel.CRITICAL),
        'os.popen': ('Command Injection', SeverityLevel.CRITICAL),
    }
    
    def detect(self, file_path: Path, content: str, tree: Optional[ast.AST] = None) -> List[Vulnerability]:
        """Detect input validation vulnerabilities."""
        vulnerabilities = []
        
        if tree:
            vulnerabilities.extend(self._detect_dangerous_calls(file_path, tree, content.split('\n')))
            vulnerabilities.extend(self._detect_xss_vulnerabilities(file_path, tree, content.split('\n')))
        
        return vulnerabilities
    
    def _detect_dangerous_calls(self, file_path: Path, tree: ast.AST, lines: List[str]) -> List[Vulnerability]:
        """Detect calls to dangerous functions."""
        vulnerabilities = []
        
        class DangerousCallVisitor(ast.NodeVisitor):
            def __init__(self):
                self.vulns = []
            
            def visit_Call(self, node):
                func_name = self._get_func_name(node)
                
                if func_name in InputValidationDetector.DANGEROUS_FUNCTIONS:
                    vuln_type, severity = InputValidationDetector.DANGEROUS_FUNCTIONS[func_name]
                    
                    # Check if user input is involved
                    if self._has_user_input(node):
                        vuln = Vulnerability(
                            id=f"INPUT-{file_path.name}-{node.lineno}-{func_name}",
                            type=VulnerabilityType.INPUT_VALIDATION,
                            severity=severity,
                            title=f"Dangerous Function Call: {func_name}",
                            description=f"Use of {func_name} with user input can lead to {vuln_type} vulnerabilities.",
                            location=Location(
                                file_path=file_path,
                                line_start=node.lineno,
                                line_end=node.end_lineno or node.lineno
                            ),
                            code_snippet='\n'.join(lines[max(0, node.lineno-4):node.lineno+3]),
                            remediation=f"Avoid using {func_name} with user input. "
                                      f"Implement proper input validation and use safer alternatives.",
                            cwe_ids=["CWE-20", "CWE-94", "CWE-502"],
                            confidence=0.9,
                            compliance_mappings={
                                "PCI-DSS": ["6.5.1", "6.5.8"],
                                "SOC2": ["CC6.1"]
                            }
                        )
                        self.vulns.append(vuln)
                
                self.generic_visit(node)
            
            def _get_func_name(self, node) -> str:
                """Extract function name from call node."""
                if isinstance(node.func, ast.Name):
                    return node.func.id
                elif isinstance(node.func, ast.Attribute):
                    parts = []
                    current = node.func
                    while isinstance(current, ast.Attribute):
                        parts.append(current.attr)
                        current = current.value
                    if isinstance(current, ast.Name):
                        parts.append(current.id)
                    return '.'.join(reversed(parts))
                return ''
            
            def _has_user_input(self, node) -> bool:
                """Check if node involves user input."""
                # Simple heuristic - check for common user input sources
                user_input_indicators = ['request', 'params', 'args', 'input', 'data', 'user', 'form']
                node_str = ast.dump(node)
                return any(indicator in node_str.lower() for indicator in user_input_indicators)
        
        visitor = DangerousCallVisitor()
        visitor.visit(tree)
        return visitor.vulns
    
    def _detect_xss_vulnerabilities(self, file_path: Path, tree: ast.AST, lines: List[str]) -> List[Vulnerability]:
        """Detect potential XSS vulnerabilities."""
        vulnerabilities = []
        
        # Simple pattern matching for template rendering without escaping
        xss_patterns = [
            (r'render_template.*?(?:safe|autoescape\s*=\s*False)', "Template autoescape disabled"),
            (r'\|\s*safe\b', "Jinja2 safe filter used"),
            (r'Markup\(.*?(?:request|params|args|input|data|user)', "Markup with user input"),
            (r'render_template_string\([^)]*\)', "Template string rendering"),
        ]
        
        content = '\n'.join(lines)
        for pattern, issue in xss_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                line_num = content[:match.start()].count('\n') + 1
                
                vuln = Vulnerability(
                    id=f"XSS-{file_path.name}-{line_num}",
                    type=VulnerabilityType.XSS,
                    severity=SeverityLevel.HIGH,
                    title=f"Potential XSS Vulnerability: {issue}",
                    description="User input rendered without proper escaping can lead to XSS attacks.",
                    location=Location(
                        file_path=file_path,
                        line_start=line_num,
                        line_end=line_num
                    ),
                    code_snippet=self._get_code_snippet(lines, line_num),
                    remediation="Enable autoescape in templates and sanitize user input before rendering.",
                    cwe_ids=["CWE-79"],
                    confidence=0.85,
                    compliance_mappings={
                        "PCI-DSS": ["6.5.7"],
                        "SOC2": ["CC6.1"]
                    }
                )
                vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _get_code_snippet(self, lines: List[str], line_num: int, context: int = 3) -> str:
        """Get code snippet with context."""
        start = max(0, line_num - context - 1)
        end = min(len(lines), line_num + context)
        return '\n'.join(lines[start:end])