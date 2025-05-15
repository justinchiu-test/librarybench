# Open Source Repository Organization Analyzer

A specialized file system analyzer for open source project maintainers focused on repository structure optimization and contributor experience.

## Overview

The Open Source Repository Organization Analyzer is a Python library designed to help open source project maintainers understand and improve repository structure, organization, and contributor experience. It provides tools for contributor impact analysis, cross-repository comparison, license compliance scanning, dependency visualization, and newcomer experience metrics to ensure projects remain efficient and well-organized.

## Persona Description

Raj maintains several popular open source projects and needs to ensure the repositories remain efficient and well-organized. His goal is to understand how the project structure impacts new contributors and identify areas for optimization.

## Key Requirements

1. **Contributor Impact Analysis**:
   Tools to analyze how different developers affect repository size and organization over time. This is critical for Raj because it helps identify both positive organizational patterns and anti-patterns across contributors. The system must attribute structural changes to specific contributors and track how their patterns influence overall repository health.

2. **Cross-Repository Comparison**:
   Functionality to highlight structural differences between similar projects. This feature is essential because it allows Raj to benchmark his project organization against successful similar projects. By identifying organizational patterns from other successful projects, Raj can adopt best practices and avoid common pitfalls.

3. **License Compliance Scanning**:
   Mechanisms to detect incompatible or missing license information throughout the codebase. This capability is crucial for maintaining legal compliance in open source projects. Raj needs to ensure all code has proper licensing, identify any potentially incompatible licenses from dependencies or contributions, and verify license headers exist where required.

4. **Dependency Tree Visualization**:
   Analytics showing the storage impact and organization of included libraries and frameworks. This is vital for understanding how dependencies affect project structure and size. Raj needs to visualize complex dependency relationships, identify redundancies, and understand how external code is organized within the project.

5. **Newcomer Experience Metrics**:
   Tools to identify areas of the codebase that might confuse new contributors due to organization or complexity. This feature is essential for growing the contributor base. Raj needs to pinpoint areas where directory structures, naming conventions, or code organization create barriers to entry for new contributors.

## Technical Requirements

### Testability Requirements
- All components must have well-defined interfaces that can be tested independently
- Repository analysis must work with sample repositories containing known patterns
- Comparison algorithms must be verifiable with predetermined results
- License detection must be tested against a comprehensive database of license types
- Test coverage should exceed 90% for all core functionality

### Performance Expectations
- Repository structure analysis should complete in under 5 minutes for projects up to 1GB
- Cross-repository comparison should complete in under 10 minutes for 5 similar projects
- License scanning should process at least 10,000 files per minute
- Dependency analysis should handle projects with 1,000+ dependencies
- Newcomer metrics calculations should complete in under 5 minutes

### Integration Points
- Git, GitHub, GitLab, and other version control system APIs
- License database references for compliance checking
- Package management systems for dependency resolution
- Export capabilities for analysis results (JSON, CSV, Markdown)
- Optional integration with contribution guidelines and documentation

### Key Constraints
- All operations must be non-destructive and read-only
- Implementation must respect API rate limits for hosted services
- System must work with repositories hosted on various platforms
- Analysis should be performant even with limited resources
- Solution must accommodate diverse project types and languages

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The Open Source Repository Organization Analyzer must provide the following core functionality:

1. **Contributor Analysis Framework**:
   - Commit pattern analysis by contributor
   - File organization impact measurement
   - Directory structure change attribution
   - Statistical analysis of contributor patterns
   - Identification of organizational best practices

2. **Repository Structure Comparison**:
   - Directory tree similarity metrics
   - Naming convention analysis
   - File distribution comparison
   - Organization pattern extraction
   - Best practice recommendation engine

3. **License Management System**:
   - License detection and identification
   - Compatibility analysis across components
   - Missing license detection
   - License conflict resolution suggestions
   - License header verification

4. **Dependency Analysis Engine**:
   - Dependency tree construction and visualization
   - Storage impact calculation by dependency
   - Unused or redundant dependency detection
   - Version and compatibility tracking
   - Dependency organization recommendations

5. **Contributor Experience Assessment**:
   - Directory complexity scoring
   - Navigation path analysis
   - Documentation-to-code ratio measurement
   - Entry point identification
   - Onboarding path optimization

## Testing Requirements

### Key Functionalities to Verify
- Accuracy of contributor pattern attribution
- Precision of cross-repository structural comparison
- Reliability of license detection and compatibility analysis
- Correctness of dependency tree construction
- Effectiveness of newcomer experience metrics

### Critical User Scenarios
- Analysis of a growing project with increasing contributor base
- Comparison with similar projects to identify organization improvements
- License compliance audit before a major release
- Dependency rationalization to simplify project structure
- Repository restructuring to improve contributor experience

### Performance Benchmarks
- Complete analysis of a 1GB repository in under 5 minutes
- Comparison of 5 similar projects in under 10 minutes
- License scanning of 50,000 files in under 5 minutes
- Dependency analysis of a project with 1,000 dependencies in under 3 minutes
- Contributor metrics calculation in under 5 minutes even for large projects

### Edge Cases and Error Conditions
- Handling repositories with unusual or non-standard structures
- Graceful operation with limited API access
- Recovery from interrupted analysis operations
- Proper handling of extremely large individual files
- Appropriate response to malformed dependency declarations

### Required Test Coverage Metrics
- Minimum 90% code coverage across all modules
- 100% coverage of license detection algorithms
- Comprehensive tests for all supported repository platforms
- Performance tests for all resource-intensive operations
- Integration tests for all supported external services

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

The Open Source Repository Organization Analyzer implementation will be considered successful when:

1. Contributor impact analysis accurately attributes organizational patterns to specific contributors
2. Cross-repository comparison provides actionable insights for structural improvement
3. License compliance scanning correctly identifies missing and incompatible licenses
4. Dependency tree visualization clearly shows storage impact and organizational structure
5. Newcomer experience metrics identify actual barriers to entry for new contributors
6. All performance benchmarks are met or exceeded
7. Code is well-structured, maintainable, and follows Python best practices
8. The library provides clear, actionable recommendations for repository improvement

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

NOTE: To set up your development environment, use `uv venv` to create a virtual environment. From within the project directory, activate the environment with `source .venv/bin/activate`. Install the project with `uv pip install -e .`.

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY for project completion. Use the following commands:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```