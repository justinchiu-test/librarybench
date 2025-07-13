# Microservices Boundary Analyzer

## Overview
A specialized code dependency analysis tool designed to help cloud architects decompose monolithic applications into microservices by identifying natural service boundaries based on code coupling patterns and architectural principles.

## Persona Description
A cloud architect leading the decomposition of monolithic applications into microservices. They need to identify natural service boundaries by analyzing code dependencies and ensuring clean separation of concerns.

## Key Requirements
1. **Service boundary recommendation based on low-coupling clusters**: The tool must analyze import dependencies and identify clusters of tightly coupled modules that form natural microservice candidates, using metrics like coupling coefficient and cohesion scores to recommend optimal service boundaries.

2. **API surface analysis between proposed service boundaries**: Essential for understanding the communication patterns between proposed services, the tool must identify all function calls, data structures, and shared resources that would become API endpoints when modules are separated into different services.

3. **Shared data model identification across module boundaries**: Critical for preventing distributed monoliths, the system must detect when multiple modules access the same data structures or database models, highlighting potential data consistency challenges in a microservices architecture.

4. **Migration effort estimation with dependency complexity scoring**: To help prioritize decomposition efforts, the tool must calculate complexity scores based on the number of dependencies, circular references, and integration points, providing quantitative estimates for migration difficulty.

5. **Cross-service circular dependency prevention analysis**: Vital for maintaining clean architecture, the system must detect and flag dependency cycles that would span multiple services, suggesting refactoring strategies to eliminate these anti-patterns before migration.

## Technical Requirements
- **Testability requirements**: All analysis algorithms must be unit testable with mock file systems and dependency graphs. Integration tests should verify end-to-end analysis workflows using sample codebases.
- **Performance expectations**: Must analyze codebases with up to 10,000 Python files within 5 minutes on standard hardware. Dependency graph generation should handle projects with 100,000+ import relationships.
- **Integration points**: Must provide programmatic APIs for CI/CD integration, JSON/XML export for visualization tools, and hooks for custom boundary detection algorithms.
- **Key constraints**: Analysis must work with incomplete codebases, handle dynamic imports gracefully, and provide meaningful results even with circular dependencies present.

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The analyzer must parse Python source files to build a comprehensive dependency graph, apply clustering algorithms to identify loosely coupled components, calculate metrics for service boundary recommendations, analyze data flow between proposed boundaries, and generate detailed reports with migration complexity scores and refactoring suggestions. The system should support incremental analysis for large codebases and provide APIs for custom clustering strategies.

## Testing Requirements
- **Key functionalities that must be verified**:
  - Accurate parsing of all Python import types (absolute, relative, dynamic)
  - Correct identification of module clusters using coupling metrics
  - Proper detection of shared data models and circular dependencies
  - Accurate complexity scoring and effort estimation algorithms
  - Reliable API surface analysis between module boundaries

- **Critical user scenarios that should be tested**:
  - Analyzing a monolithic e-commerce application to identify order, inventory, and user services
  - Processing a legacy financial system to separate trading, reporting, and compliance modules
  - Evaluating a content management system for media, authentication, and workflow boundaries
  - Handling projects with complex circular dependencies and suggesting resolution strategies
  - Analyzing codebases with mixed architectural patterns (MVC, layered, event-driven)

- **Performance benchmarks that must be met**:
  - Parse 1,000 Python files in under 30 seconds
  - Generate dependency graphs for 10,000 nodes in under 2 minutes
  - Complete full analysis of 100,000 LOC codebase within 5 minutes
  - Memory usage should not exceed 2GB for typical enterprise applications

- **Edge cases and error conditions that must be handled properly**:
  - Missing imported modules or packages
  - Syntax errors in source files
  - Circular import dependencies
  - Dynamic imports using importlib
  - Multi-language projects with Python components

- **Required test coverage metrics**:
  - Minimum 90% code coverage for core analysis modules
  - 100% coverage for boundary detection algorithms
  - Full coverage of error handling paths
  - Integration tests for all supported Python versions

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
Clear metrics and outcomes that would indicate the implementation successfully meets this persona's needs:
- Successfully identifies service boundaries that align with domain-driven design principles
- Reduces inter-service dependencies by at least 70% compared to random module grouping
- Accurately predicts migration effort with 80% correlation to actual implementation time
- Detects 100% of circular dependencies that would span service boundaries
- Generates actionable refactoring suggestions accepted by architects in 90% of cases

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup
From within the project directory, set up the development environment:
```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```