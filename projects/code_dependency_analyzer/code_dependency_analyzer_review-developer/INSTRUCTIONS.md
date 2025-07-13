# Architectural Review Automation System

## Overview
An automated code review tool that leverages dependency analysis to detect architectural violations, enforce coding standards based on module relationships, and generate intelligent review comments for dependency-related issues.

## Persona Description
A tools engineer building automated code review systems. They need to detect architectural violations and enforce coding standards based on dependency rules.

## Key Requirements
1. **Architectural rule validation with custom policies**: The tool must support defining custom architectural rules (layering, module boundaries, dependency directions) and automatically validate code changes against these policies during review.

2. **Layered architecture violation detection**: Critical for maintaining clean architecture, the system must detect when code violates layer boundaries (e.g., UI accessing database directly), identifying specific imports that break architectural contracts.

3. **Code review comment generation for dependency issues**: To provide actionable feedback, the tool must generate human-readable review comments explaining dependency violations, suggesting specific fixes, and referencing architectural guidelines.

4. **Git hook integration for pre-commit validation**: Essential for shift-left practices, the system must integrate with Git hooks to validate dependency rules before commits, providing fast feedback and preventing architectural drift.

5. **Team-specific dependency convention checking**: For organizational scaling, the tool must support team-specific rules and conventions, allowing different parts of the codebase to have tailored architectural constraints based on team ownership.

## Technical Requirements
- **Testability requirements**: All rule validation logic must be unit testable with mock repositories and rule sets. Integration tests should verify Git hook functionality and comment generation.
- **Performance expectations**: Pre-commit validation must complete within 5 seconds for typical commits. Full repository scans should handle 100,000+ files within 10 minutes.
- **Integration points**: Must integrate with Git hooks, popular code review platforms (GitHub, GitLab, Bitbucket), and provide APIs for custom rule engines.
- **Key constraints**: Must work with various Git workflows, handle merge commits gracefully, and provide meaningful feedback even with partial code context.

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The analyzer must parse architectural rule definitions in various formats, analyze code changes to detect rule violations, generate contextual review comments with fix suggestions, integrate with Git for pre-commit validation, and support team-based rule customization. The system should provide APIs for rule extension and integration with existing review workflows.

## Testing Requirements
- **Key functionalities that must be verified**:
  - Accurate architectural rule parsing and validation
  - Correct layering violation detection
  - Helpful review comment generation
  - Reliable Git hook integration
  - Proper team-specific rule application

- **Critical user scenarios that should be tested**:
  - Detecting UI layer accessing database in an MVC application
  - Validating microservice boundary violations in commits
  - Generating fix suggestions for circular dependencies
  - Enforcing team-specific import restrictions
  - Pre-commit validation of architectural changes

- **Performance benchmarks that must be met**:
  - Validate single file changes in under 100ms
  - Process commits with 100 changed files in under 5 seconds
  - Generate review comments for 50 violations in under 2 seconds
  - Full repository scan of 10,000 files in under 5 minutes

- **Edge cases and error conditions that must be handled properly**:
  - Renamed or moved files in commits
  - Binary files and non-Python content
  - Malformed architectural rule definitions
  - Network issues accessing review platforms
  - Concurrent Git operations

- **Required test coverage metrics**:
  - Minimum 95% code coverage for rule validation engine
  - 100% coverage for violation detection algorithms
  - Full coverage of Git hook integration
  - Integration tests for all supported platforms

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
- Catches 95% of architectural violations before merge
- Reduces architecture-related bugs by 80% through early detection
- Generates fix suggestions accepted by developers in 85% of cases
- Completes pre-commit validation fast enough to not impact workflow
- Enables teams to maintain architectural integrity with 90% less manual effort

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