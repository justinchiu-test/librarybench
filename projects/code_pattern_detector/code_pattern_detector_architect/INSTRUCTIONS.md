# PyPatternGuard - Architectural Pattern Detection Engine

## Overview
A specialized code pattern detection system designed for software architects to ensure architectural patterns are followed consistently across microservice architectures. The system detects violations of architectural boundaries, analyzes service coupling, and validates design pattern compliance.

## Persona Description
A software architect designing microservices who needs to ensure architectural patterns are followed consistently. She wants to detect violations of architectural boundaries and service coupling issues.

## Key Requirements

1. **Architectural layer violation detection with dependency graphs**: Critical for maintaining clean architecture by identifying when code in one layer improperly depends on another layer, preventing architectural erosion over time.

2. **Service coupling analysis with cohesion metrics**: Essential for microservice health assessment, measuring how tightly services are coupled and ensuring they maintain appropriate boundaries for independent deployment and scaling.

3. **Design pattern compliance checking against architectural decisions**: Validates that implementation follows documented architectural decisions and patterns, ensuring consistency across teams and preventing architectural drift.

4. **Cross-service communication pattern analysis**: Analyzes inter-service communication to identify anti-patterns like chatty interfaces, circular dependencies, or synchronous call chains that could impact system resilience.

5. **Architectural fitness function evaluation**: Provides quantitative metrics to measure how well the current implementation aligns with architectural goals, enabling data-driven architectural decisions.

## Technical Requirements

### Testability Requirements
- All analysis functions must be deterministic and return consistent results
- Support for mocking file systems and code repositories
- Ability to test with synthetic code samples representing various architectural patterns
- Clear separation between analysis logic and I/O operations

### Performance Expectations
- Analyze codebases up to 1 million lines of code within 5 minutes
- Incremental analysis capability for continuous integration scenarios
- Memory usage should not exceed 2GB for typical microservice projects
- Support parallel analysis of independent services

### Integration Points
- AST parsing using Python's `ast` module
- Git integration for tracking architectural changes over time
- JSON/YAML configuration for architectural rules
- Export capabilities for visualization tools

### Key Constraints
- Must work with Python 3.8+ codebases
- No external dependencies beyond Python standard library
- Analysis must be non-intrusive (read-only operations)
- Must handle incomplete or partially invalid code gracefully

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system must provide:

1. **Dependency Graph Builder**: Constructs a comprehensive dependency graph of the codebase, identifying module, package, and service boundaries with support for various import patterns and dynamic imports.

2. **Layer Violation Detector**: Analyzes the dependency graph against defined architectural layers (e.g., presentation, business, data) and identifies violations where dependencies flow in the wrong direction.

3. **Service Coupling Analyzer**: Calculates coupling metrics between services including afferent/efferent coupling, instability metrics, and identifies tight coupling patterns that could impact service independence.

4. **Pattern Compliance Checker**: Validates implementation against a catalog of architectural patterns (e.g., Repository, Factory, Observer) and reports deviations from expected implementations.

5. **Communication Pattern Analyzer**: Examines cross-service communication patterns by analyzing API calls, message passing, and shared data structures to identify potential architectural risks.

6. **Fitness Function Evaluator**: Computes architectural fitness scores based on configurable metrics including modularity, testability, deployability, and performance characteristics.

## Testing Requirements

### Key Functionalities to Verify
- Accurate dependency graph construction across complex codebases
- Correct identification of layer violations in various architectural styles
- Precise coupling metric calculations matching established formulas
- Pattern detection accuracy with low false positive rates
- Communication pattern analysis covering synchronous and asynchronous patterns

### Critical User Scenarios
- Analyzing a microservice architecture with 10+ services
- Detecting architectural drift after major refactoring
- Validating new service additions against architectural constraints
- Identifying high-risk coupling before service extraction
- Evaluating architectural fitness during design reviews

### Performance Benchmarks
- Dependency graph construction: < 1 second per 10,000 lines of code
- Layer violation detection: < 500ms per service
- Coupling analysis: < 2 seconds for 50 service interactions
- Pattern compliance checking: < 100ms per pattern per file
- Full analysis of 100,000 LOC project: < 60 seconds

### Edge Cases and Error Conditions
- Circular dependencies between services
- Dynamically generated code and metaprogramming
- Incomplete code with syntax errors
- External dependencies not available for analysis
- Extremely deep inheritance hierarchies (>10 levels)

### Required Test Coverage Metrics
- Line coverage: minimum 90%
- Branch coverage: minimum 85%
- Mutation testing score: minimum 75%
- All architectural patterns must have dedicated test cases
- Integration tests covering multi-service scenarios

IMPORTANT:
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches
- REQUIRED: Tests must be run with pytest-json-report to generate a pytest_results.json file:
  ```
  pip install pytest-json-report
  pytest --json-report --json-report-file=pytest_results.json
  ```
- The pytest_results.json file must be included as proof that all tests pass

## Success Criteria

The implementation successfully meets this persona's needs when:

1. **Architectural Integrity**: The system accurately identifies 95% of architectural violations in test codebases with less than 5% false positives.

2. **Actionable Insights**: Analysis results provide clear, actionable recommendations for addressing architectural issues with severity rankings.

3. **Performance Goals**: Full analysis completes within defined time constraints for codebases up to 1 million lines of code.

4. **Integration Success**: The system integrates seamlessly into CI/CD pipelines with configurable quality gates based on architectural metrics.

5. **Fitness Tracking**: Architectural fitness scores show measurable improvement trends when recommendations are followed.

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup

From within the project directory, set up the virtual environment:
```
uv venv
source .venv/bin/activate
uv pip install -e .
```

Run tests with pytest-json-report:
```
uv pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```