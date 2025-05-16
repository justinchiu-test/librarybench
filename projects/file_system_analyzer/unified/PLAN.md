# Unified File System Analyzer - Architecture Plan

This document outlines the architecture and implementation plan for creating a unified library that supports both security auditor and database administrator personas while maintaining the specific functionality required by each.

## 1. Architecture Overview

The unified architecture consists of:

1. **Common Core Library** (`common/`): Shared components and utilities for all persona implementations
2. **Security Auditor Package** (`file_system_analyzer/`): Security and compliance-focused extensions
3. **DB Admin Package** (`file_system_analyzer_db_admin/`): Database optimization-focused extensions

The design follows these principles:
- **Abstraction**: Common interfaces with persona-specific implementations
- **Extension**: Base classes with extension points for specific needs
- **Consistency**: Standardized patterns across all components
- **Reusability**: Shared utilities to minimize duplication
- **Backwards Compatibility**: Preserve existing APIs and behavior

## 2. Core Components

### 2.1 Scanner Framework (`common/core/scanner.py`)

Core scanning capabilities for traversing file systems and analyzing files:

- `BaseScanner`: Abstract base class defining the scanner interface
- `FileScanner`: Scans individual files
- `DirectoryScanner`: Recursive directory scanning
- `ParallelScanner`: Multi-threaded scanning for performance
- `ScanSession`: Manages scan state and results
- `ScanOptions`: Configuration options for scans

```python
# Example architecture
class BaseScanner(ABC):
    @abstractmethod
    def scan(self, target: str, options: ScanOptions) -> ScanResult:
        pass
        
class DirectoryScanner(BaseScanner):
    def scan(self, target: str, options: ScanOptions) -> ScanResult:
        # Implementation
        pass
```

### 2.2 Pattern Matching Framework (`common/core/patterns.py`)

Flexible pattern matching system for different content types:

- `PatternMatcher`: Abstract pattern matching interface
- `RegexPatternMatcher`: Regex-based pattern matching
- `BinaryPatternMatcher`: Binary content pattern matching
- `PatternDefinition`: Structure for pattern specifications
- `PatternRegistry`: Registry for pattern management

```python
# Example architecture
class PatternDefinition:
    def __init__(self, name: str, pattern: str, category: str):
        self.name = name
        self.pattern = pattern
        self.category = category

class PatternMatcher(ABC):
    @abstractmethod
    def match(self, content: bytes, patterns: List[PatternDefinition]) -> List[PatternMatch]:
        pass
```

### 2.3 Analysis Framework (`common/core/analysis.py`)

Framework for analyzing scan results:

- `BaseAnalyzer`: Abstract analysis interface
- `DifferentialAnalyzer`: Base differential analysis implementation
- `AnalysisResult`: Standard structure for analysis results
- `AnalysisOptions`: Configuration for analysis operations

```python
# Example architecture
class BaseAnalyzer(ABC):
    @abstractmethod
    def analyze(self, data: Any, options: AnalysisOptions) -> AnalysisResult:
        pass
        
class DifferentialAnalyzer(BaseAnalyzer):
    def analyze(self, current: Any, baseline: Any, options: AnalysisOptions) -> DifferentialResult:
        # Implementation
        pass
```

### 2.4. Reporting Framework (`common/core/reporting.py`)

Framework for generating reports from analysis results:

- `BaseReporter`: Abstract reporting interface
- `ReportGenerator`: Standard report generation
- `ReportTemplate`: Report template system
- `ReportFormat`: Supported report formats (JSON, HTML, CSV)

```python
# Example architecture
class BaseReporter(ABC):
    @abstractmethod
    def generate(self, data: Any, options: ReportOptions) -> Report:
        pass
        
class ReportGenerator(BaseReporter):
    def generate(self, data: Any, options: ReportOptions) -> Report:
        # Implementation
        pass
```

### 2.5. API Framework (`common/core/api.py`)

Standardized API structure for all functionality:

- `BaseAPI`: Abstract API interface
- `APIResult`: Standard API response format
- `APIOptions`: Standard API configuration options
- `CachingMixin`: Caching functionality for APIs
- `NotificationMixin`: Notification capabilities for APIs

```python
# Example architecture
class BaseAPI(ABC):
    @abstractmethod
    def execute(self, command: str, options: dict) -> APIResult:
        pass
        
class APIResult:
    def __init__(self, success: bool, data: Any = None, error: str = None):
        self.success = success
        self.data = data
        self.error = error
```

### 2.6. Base Classes (`common/core/base.py`)

Common base classes and interfaces:

- `Configurable`: Base class for configurable components
- `Serializable`: Base class for serializable objects
- `Cacheable`: Base class for cacheable objects
- `Validatable`: Base class for objects with validation

```python
# Example architecture
class Serializable(ABC):
    @abstractmethod
    def to_dict(self) -> dict:
        pass
        
    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict) -> 'Serializable':
        pass
```

## 3. Utility Components

### 3.1. File Utilities (`common/utils/file_utils.py`)

File system operations and utilities:

- File metadata retrieval
- MIME type detection
- File content reading
- Recursive directory traversal
- File filtering and selection

### 3.2. Export Utilities (`common/utils/export.py`)

Export functionality for different formats:

- JSON export
- CSV export
- HTML report generation
- Templating system

### 3.3. Caching Utilities (`common/utils/cache.py`)

Caching mechanisms for improved performance:

- Memory cache
- Disk cache
- TTL-based expiration
- Cache invalidation

### 3.4. Cryptographic Utilities (`common/utils/crypto.py`)

Cryptographic functions for security:

- Hash calculation
- Signature creation and verification
- Cryptographic verification
- Tamper detection

### 3.5. Type Definitions (`common/utils/types.py`)

Common data models and type definitions:

- `FileMetadata`
- `ScanResult`
- `ScanMatch`
- `ScanSummary`
- Enum definitions for statuses and categories

## 4. Extension Points

### 4.1. Scanner Extensions

Extend `BaseScanner` for specialized scanning:

- Security Auditor: `SensitiveDataScanner` for compliance patterns
- DB Admin: `DatabaseFileScanner` for database file recognition

### 4.2. Pattern Extensions

Extend `PatternDefinition` for specialized patterns:

- Security Auditor: Regulatory compliance patterns (PII, PCI, etc.)
- DB Admin: Database file patterns for different engines

### 4.3. Analysis Extensions

Extend `BaseAnalyzer` for specialized analysis:

- Security Auditor: Compliance violation analysis
- DB Admin: Performance optimization analysis

### 4.4. Reporting Extensions

Extend `BaseReporter` for specialized reports:

- Security Auditor: Compliance reports by regulation
- DB Admin: Optimization recommendation reports

## 5. Migration Strategy

### 5.1. Security Auditor Package Migration

1. Update import paths to use `common` library components
2. Refactor classes to extend common base classes
3. Move shared functionality to common library
4. Keep security-specific functionality in place
5. Ensure backward compatibility with existing tests

Example migration:

```python
# Before
from file_system_analyzer.utils import scanner

# After
from common.core import scanner
```

### 5.2. DB Admin Package Migration

1. Update import paths to use `common` library components
2. Refactor classes to extend common base classes
3. Move shared functionality to common library
4. Keep DB-specific functionality in place
5. Ensure backward compatibility with existing tests

Example migration:

```python
# Before
from file_system_analyzer_db_admin.utils import file_utils

# After
from common.utils import file_utils
```

## 6. Implementation Steps

### 6.1. Core Library Implementation

1. Create basic directory structure for common library
2. Implement core scanning framework
3. Implement pattern matching framework
4. Implement analysis framework
5. Implement reporting framework
6. Implement API framework
7. Implement utility components

### 6.2. Persona-Specific Refactoring

1. Refactor Security Auditor package to use common library
2. Refactor DB Admin package to use common library
3. Verify all functionality works correctly
4. Run tests to ensure backward compatibility

### 6.3. Testing and Validation

1. Run all tests for both personas
2. Verify that functionality is preserved
3. Verify performance meets or exceeds original implementation
4. Generate test report

## 7. Key Interfaces

### 7.1. Scanner Interface

```python
class BaseScanner(ABC):
    @abstractmethod
    def scan(self, target: str, options: ScanOptions) -> ScanResult:
        """Scan a target (file or directory) with the given options."""
        pass
    
    @abstractmethod
    def can_scan(self, target: str) -> bool:
        """Check if this scanner can scan the given target."""
        pass
```

### 7.2. Pattern Matcher Interface

```python
class PatternMatcher(ABC):
    @abstractmethod
    def match(self, content: bytes, patterns: List[PatternDefinition]) -> List[PatternMatch]:
        """Match patterns against content."""
        pass
    
    @abstractmethod
    def register_pattern(self, pattern: PatternDefinition) -> bool:
        """Register a new pattern."""
        pass
```

### 7.3. Analyzer Interface

```python
class BaseAnalyzer(ABC):
    @abstractmethod
    def analyze(self, data: Any, options: AnalysisOptions) -> AnalysisResult:
        """Analyze data with the given options."""
        pass
    
    @abstractmethod
    def can_analyze(self, data: Any) -> bool:
        """Check if this analyzer can analyze the given data."""
        pass
```

### 7.4. Reporter Interface

```python
class BaseReporter(ABC):
    @abstractmethod
    def generate(self, data: Any, options: ReportOptions) -> Report:
        """Generate a report from data with the given options."""
        pass
    
    @abstractmethod
    def supports_format(self, format: str) -> bool:
        """Check if this reporter supports the given format."""
        pass
```

### 7.5. API Interface

```python
class BaseAPI(ABC):
    @abstractmethod
    def execute(self, command: str, options: dict) -> APIResult:
        """Execute a command with the given options."""
        pass
    
    @abstractmethod
    def list_commands(self) -> List[str]:
        """List available commands."""
        pass
```

## 8. Expected Benefits

1. **Code Reduction**: Significant reduction in duplicate code
2. **Maintainability**: Easier maintenance with centralized core components
3. **Consistency**: Standardized interfaces and patterns
4. **Extensibility**: Simplified creation of new features
5. **Performance**: Optimized shared components
6. **Testability**: Improved test coverage with shared test utilities

## 9. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Breaking existing functionality | Comprehensive testing of all features |
| Performance regression | Performance benchmarking during development |
| Increased complexity | Clear documentation and simple interfaces |
| Test failures | Incremental refactoring with continuous testing |

## 10. Conclusion

This architecture plan provides a comprehensive approach to unifying the file system analyzer implementations while preserving persona-specific functionality. The common library will reduce code duplication and provide a consistent foundation for both the security auditor and database administrator implementations.