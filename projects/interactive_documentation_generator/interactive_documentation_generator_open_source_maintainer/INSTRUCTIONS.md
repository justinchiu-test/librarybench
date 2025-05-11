# Open Source Documentation Generator

A specialized documentation generation tool designed for open source project maintainers to reduce documentation burden while supporting diverse user needs.

## Overview

The Open Source Documentation Generator provides automated tools to create, maintain, and evolve documentation for rapidly changing open source projects. It focuses on highlighting API changes, tracking community contributions to documentation, and ensuring consistent quality across multiple platforms and environments.

## Persona Description

Mei is the lead maintainer of a popular open source library with a global contributor base. She needs to make the documentation both approachable for newcomers and comprehensive for experienced users while reducing the maintenance burden as the project evolves rapidly.

## Key Requirements

1. **Automated API Change Detection and Highlighting** - The system must automatically detect and highlight breaking changes between versions of the codebase. This is critical for Mei as it helps contributors and users understand compatibility issues without manual comparison, reducing migration pain points and support requests.

2. **Documentation Contribution Metrics** - The tool must track and display metrics on documentation coverage by community members. This allows Mei to acknowledge contributors' documentation efforts, identify documentation champions within the community, and focus attention on under-documented areas of the codebase.

3. **Multi-Platform Example Generation** - The system must generate and validate code examples across different environments and runtime versions. As an open source maintainer, Mei must ensure documentation works for users across diverse setups, from different Python versions to various operating systems and deployment contexts.

4. **Continuous Documentation Integration** - The tool must provide integration hooks for CI/CD systems (specifically GitHub Actions and GitLab CI) to automatically build, validate, and deploy documentation. This ensures documentation is always up-to-date with the latest code changes without requiring manual intervention from Mei or other maintainers.

5. **Documentation Health Scoring** - The system must calculate and display a health score for each documentation section based on completeness, accuracy, and freshness. This helps Mei quickly identify areas needing community attention and allows potential contributors to find meaningful documentation tasks to tackle.

## Technical Requirements

### Testability Requirements
- All components must be testable in isolation using pytest fixtures and mocks
- API change detection accuracy must be verifiable using version-diffing test cases
- Multi-platform testing must support parametrized tests for different Python versions
- Integration hooks must be testable with mock CI environments

### Performance Expectations
- Documentation generation for projects up to 100,000 lines of code must complete in under 5 minutes
- API change detection between major versions must complete in under 30 seconds
- Health score calculations for the entire documentation set must complete in under 10 seconds

### Integration Points
- Git repository integration for version comparison and contribution tracking
- GitHub/GitLab API integration for contributor information and issue linking
- CI system webhook integration for automated documentation deployment
- Python ecosystem tools (different interpreters, package managers) for cross-platform validation

### Key Constraints
- All functionality must be implementable without UI components
- Must work offline for local documentation generation and validation
- Must support projects with at least 50 contributors and 10,000 stars on GitHub
- Must handle documentation for projects with at least 10 major versions

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system must provide:

1. A code analysis engine that examines source files across versions to detect API changes, with classification of changes as breaking, non-breaking, or deprecation
2. A documentation extraction system that parses docstrings, comments, and dedicated documentation files
3. A contributor tracking system that attributes documentation sections to specific contributors
4. A multi-platform validation engine that verifies code examples work across different environments
5. A documentation health scoring algorithm that evaluates completeness, accuracy, and freshness
6. CI integration components that hook into GitHub Actions and GitLab CI for automated documentation workflows
7. A reporting system that generates contribution metrics and identifies documentation gaps

These components should work together to create a documentation system that evolves with the project and distributes maintenance across the community while maintaining high quality standards.

## Testing Requirements

The implementation must include tests for:

### Key Functionalities Verification
- API change detection correctly identifies breaking vs. non-breaking changes
- Contribution tracking accurately attributes documentation to authors
- Examples run correctly on multiple Python versions (3.8, 3.9, 3.10, 3.11)
- Health scoring identifies undocumented and outdated sections
- CI integration hooks successfully trigger documentation rebuilds

### Critical User Scenarios
- A new contributor adds documentation for an undocumented function
- A core maintainer changes an API interface that requires documentation updates
- A release manager prepares documentation for a new major version
- A user needs to understand breaking changes between versions
- A project lead wants to recognize top documentation contributors

### Performance Benchmarks
- Documentation generation completes within time limits for repositories of varying sizes
- Health score calculation performance scales linearly with codebase size
- API change detection performs efficiently even for large version differences

### Edge Cases and Error Handling
- Handling malformed docstrings and comments
- Dealing with Git history rewrites or force pushes
- Managing conflicts between documentation sources
- Correctly processing documentation with advanced formatting (code blocks, tables, etc.)
- Handling projects with unusual directory structures

### Required Test Coverage
- Minimum 90% test coverage for core functionality
- 100% coverage for the API change detection and health scoring algorithms
- Integration tests for all CI system hooks

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

The implementation will be considered successful if:

1. The API change detection system correctly identifies at least 95% of breaking changes in test scenarios
2. Documentation contribution metrics accurately track and display author information
3. Code examples successfully run on at least 4 different Python versions
4. CI integration hooks successfully trigger documentation rebuilds on code changes
5. Documentation health scoring accurately identifies areas needing improvement

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Development Setup

To set up the development environment:

1. From within the project directory, create a virtual environment:
   ```
   uv venv
   ```

2. Activate the virtual environment:
   ```
   source .venv/bin/activate
   ```

3. Install the project in development mode:
   ```
   uv pip install -e .
   ```

4. Run tests with pytest-json-report to generate the required report:
   ```
   pip install pytest-json-report
   pytest --json-report --json-report-file=pytest_results.json
   ```

REMINDER: Generating and providing the pytest_results.json file is a CRITICAL requirement for project completion.