# Unified Query Language Interpreter Plan

## Overview
This document outlines the detailed architecture and refactoring plan for creating a unified library from multiple persona-specific query language interpreter implementations. The goal is to extract common functionality while preserving the domain-specific extensions required by each persona.

The personas include:
- **Legal Discovery Specialist**: Focused on document retrieval with legal term ontologies, proximity search, communication analysis, temporal management, and privilege detection.
- **Data Privacy Officer**: Focused on PII detection, data minimization, access logging, policy enforcement, and anonymization.

## Common Patterns Identified

After analyzing both implementations, we've identified the following common patterns and functionality:

1. **Query Representation & Processing**:
   - Both use structured query models
   - Both implement parsing from string to object representation
   - Both have query execution pipelines with similar phases
   - Both track execution status and performance metrics

2. **Data Structure & Management**:
   - Both use similar models for representing core entities
   - Both implement caching and optimization strategies
   - Both handle collection/tabular data with similar access patterns

3. **Pattern Detection**:
   - Both use pattern-based detection systems (PII, privilege)
   - Both implement confidence scoring
   - Both use regular expressions and context-aware matching

4. **Logging & Audit**:
   - Both include comprehensive logging functionality
   - Both track access and operations for auditing
   - Both implement structured logging formats

5. **Policy & Rules**:
   - Both enforce rule-based policies on query execution
   - Both validate operations against configurable rules
   - Both implement decision-making based on context

## Architecture Design

### Core Components

The unified `common` library will be structured as follows:

```
common/
├── core/
│   ├── __init__.py
│   ├── query.py          # Base query models and interfaces
│   ├── interpreter.py    # Core interpreter functionality
│   ├── execution.py      # Execution pipeline and context
│   └── result.py         # Result models and formatters
├── pattern/
│   ├── __init__.py
│   ├── detector.py       # Base pattern detection
│   ├── confidence.py     # Confidence scoring
│   └── matcher.py        # Pattern matching utilities
├── logging/
│   ├── __init__.py
│   ├── base.py           # Base logging functionality
│   ├── audit.py          # Audit logging utilities
│   └── formatter.py      # Log formatting utilities
├── policy/
│   ├── __init__.py
│   ├── engine.py         # Policy enforcement engine
│   ├── rule.py           # Rule representation and validation
│   └── context.py        # Execution context for policies
├── models/
│   ├── __init__.py
│   ├── base.py           # Base data models 
│   └── enums.py          # Common enumerations
└── utils/
    ├── __init__.py
    ├── concurrency.py    # Parallelization utilities
    ├── validation.py     # Input validation
    └── text.py           # Text processing utilities
```

### Interface Definitions

#### 1. Query Interface
```python
class BaseQuery:
    """Base class for all query representations."""
    query_type: str
    parameters: Dict[str, Any]
    execution_context: Optional[ExecutionContext]
    
    def validate(self) -> bool:
        """Validate query structure and parameters."""
        pass
        
    def to_string(self) -> str:
        """Convert query back to string representation."""
        pass
```

#### 2. Interpreter Interface
```python
class BaseInterpreter:
    """Base class for query interpreters."""
    
    def parse(self, query_string: str) -> BaseQuery:
        """Parse query string into structured representation."""
        pass
        
    def execute(self, query: BaseQuery) -> QueryResult:
        """Execute a structured query and return results."""
        pass
        
    def validate(self, query: BaseQuery) -> bool:
        """Validate query against interpreter rules."""
        pass
```

#### 3. Pattern Detector Interface
```python
class BasePatternDetector:
    """Base class for pattern detection systems."""
    
    def detect(self, content: Any) -> List[PatternMatch]:
        """Detect patterns in content."""
        pass
        
    def calculate_confidence(self, match: PatternMatch) -> float:
        """Calculate confidence score for a match."""
        pass
```

#### 4. Logging Interface
```python
class BaseLogger:
    """Base class for logging systems."""
    
    def log(self, level: str, message: str, **kwargs) -> None:
        """Log a message with the specified level."""
        pass
        
    def audit(self, action: str, user: str, resource: str, **details) -> None:
        """Log an audit event."""
        pass
```

#### 5. Policy Engine Interface
```python
class BasePolicyEngine:
    """Base class for policy enforcement engines."""
    
    def check_policy(self, action: str, context: Dict[str, Any]) -> bool:
        """Check if an action is allowed in the given context."""
        pass
        
    def get_violations(self, action: str, context: Dict[str, Any]) -> List[PolicyViolation]:
        """Get policy violations for an action in the given context."""
        pass
```

## Extension Points

The common library will provide extension points to allow persona-specific implementations:

1. **Query Language Extensions**: Domain-specific query language features
2. **Custom Pattern Detectors**: Specialized detection for different domains
3. **Policy Rules**: Domain-specific policy rules and enforcement
4. **Result Formatters**: Specialized output formats for different domains
5. **Custom Execution Handlers**: Domain-specific execution steps

## Migration Strategy

### 1. Legal Discovery Interpreter

For the Legal Discovery Interpreter, we will:

1. **Core Functionality**:
   - Refactor `LegalDiscoveryQuery` to inherit from `common.core.query.BaseQuery`
   - Migrate base interpreter functionality to use `common.core.interpreter.BaseInterpreter`
   - Adapt document processing to use common execution framework

2. **Pattern Detection**:
   - Move privilege detection to extend `common.pattern.detector.BasePatternDetector`
   - Implement legal-specific pattern matchers using common matcher framework

3. **Logging**:
   - Refactor legal auditing to use `common.logging.audit`
   - Preserve legal-specific logging requirements as extensions

4. **Extensions**:
   - Keep legal ontology as domain-specific extension
   - Maintain proximity search as legal-specific functionality
   - Preserve communication analysis as legal-specific module
   - Keep temporal management as legal-specific feature

### 2. Privacy Query Interpreter

For the Privacy Query Interpreter, we will:

1. **Core Functionality**:
   - Adapt SQL parser to use `common.core.query` base classes
   - Migrate engine to leverage common execution framework
   - Implement privacy-specific execution handlers

2. **Pattern Detection**:
   - Refactor PII detection to extend `common.pattern.detector.BasePatternDetector`
   - Move pattern libraries to use common pattern framework

3. **Logging**:
   - Adapt access logging to use `common.logging.audit`
   - Preserve privacy-specific logging features as extensions

4. **Policy Enforcement**:
   - Refactor policy engine to use `common.policy.engine.BasePolicyEngine`
   - Maintain privacy-specific policy rules as extensions

5. **Extensions**:
   - Keep anonymization as privacy-specific functionality
   - Preserve data minimization as privacy-specific feature

## Implementation Plan

### Phase 1: Common Library Implementation
1. Create base directory structure
2. Implement core interfaces and base classes
3. Develop common utilities and helper functions
4. Add comprehensive docstrings and type hints

### Phase 2: Legal Discovery Refactoring
1. Refactor core query functionality to use common library
2. Adapt document processing and search to use common patterns
3. Move privilege detection to use common pattern detection
4. Update logging to use common logging framework
5. Ensure all tests continue to pass

### Phase 3: Privacy Query Refactoring
1. Refactor SQL parser to use common query framework
2. Adapt PII detection to use common pattern detection
3. Move policy enforcement to use common policy engine
4. Update access logging to use common logging framework
5. Ensure all tests continue to pass

### Phase 4: Integration Testing
1. Verify both implementations work with refactored code
2. Run comprehensive tests across all modules
3. Generate test report and validate functionality

## Trade-offs and Decisions

1. **Class Hierarchy vs. Composition**:
   - We've chosen inheritance for core interfaces to enforce consistent behavior
   - We'll use composition for specialized functionality to allow flexibility

2. **Generalization Level**:
   - We've generalized interfaces where clear patterns exist across implementations
   - We've kept domain-specific functionality separate to preserve specialized behavior

3. **Backward Compatibility**:
   - Original package structures are preserved to maintain compatibility with tests
   - Implementation details may change but public interfaces will remain stable

4. **Shared vs. Specialized Code**:
   - Common patterns are moved to the shared library
   - Highly specialized functions remain in domain-specific packages

## Performance Considerations

1. **Runtime Overhead**:
   - Base classes are designed to add minimal overhead
   - Performance-critical operations are optimized in specialized implementations

2. **Memory Usage**:
   - Common patterns reduce duplicated code and memory footprint
   - Shared utilities optimize resource usage across implementations

3. **Scalability**:
   - Common framework is designed to scale with data volume
   - Execution pipeline supports parallel processing where appropriate

## Future Extensions

The unified architecture is designed to support future extensions:

1. **Additional Personas**:
   - New personas can extend the common interfaces
   - Domain-specific needs can be implemented as extensions

2. **New Features**:
   - Common framework provides hooks for adding new capabilities
   - Extensibility is built into the core design

## Development Workflow

1. Implement common library components
2. Refactor each persona implementation incrementally
3. Maintain continuous testing to ensure functionality is preserved
4. Document interfaces and extension points thoroughly