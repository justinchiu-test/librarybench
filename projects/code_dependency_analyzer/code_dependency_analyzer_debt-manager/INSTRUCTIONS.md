# Technical Debt Dependency Analyzer

## Overview
A comprehensive dependency analysis tool designed for engineering managers to quantify technical debt in code relationships, prioritize refactoring efforts based on dependency complexity, and plan sprint work effectively.

## Persona Description
A engineering manager responsible for maintaining code health metrics and planning refactoring sprints. They need to quantify technical debt and prioritize refactoring efforts.

## Key Requirements
1. **Technical debt scoring based on dependency complexity**: The tool must calculate quantitative debt scores using metrics like cyclomatic complexity, coupling coefficients, and dependency depth, providing managers with objective measures to justify refactoring investments.

2. **Refactoring impact prediction with risk assessment**: Essential for planning, the system must predict how refactoring efforts will propagate through the dependency graph, estimating effort required and identifying potential risks to other system components.

3. **Code smell detection in dependency patterns**: Critical for proactive debt management, the tool must identify anti-patterns like god modules, circular dependencies, and inappropriate intimacy between modules, categorizing them by severity and fix difficulty.

4. **Team ownership mapping for coupled modules**: To facilitate coordination, the system must integrate with code ownership data to identify which teams own tightly coupled modules, highlighting cross-team dependencies that complicate refactoring efforts.

5. **Sprint planning integration with complexity estimates**: For actionable planning, the tool must generate refactoring tickets with effort estimates based on dependency analysis, supporting various ticket formats and providing suggested task breakdowns.

## Technical Requirements
- **Testability requirements**: All debt calculation algorithms must be unit testable with sample dependency graphs. Integration tests should verify accurate scoring against known anti-pattern scenarios.
- **Performance expectations**: Must analyze codebases with 100,000+ lines within 10 minutes. Debt scoring should be incremental to support continuous monitoring.
- **Integration points**: Must integrate with version control for ownership data, issue tracking systems (Jira, GitHub Issues) for ticket creation, and provide APIs for dashboard integration.
- **Key constraints**: Must work with various code ownership formats (CODEOWNERS, custom), handle incomplete historical data, and provide meaningful metrics even for legacy codebases.

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The analyzer must calculate comprehensive technical debt scores using multiple complexity metrics, detect and categorize dependency-related code smells, predict refactoring impact through dependency analysis, map code ownership to identify coordination requirements, and generate prioritized refactoring plans with effort estimates. The system should support custom debt scoring rules and trend analysis over time.

## Testing Requirements
- **Key functionalities that must be verified**:
  - Accurate technical debt score calculation
  - Correct code smell pattern detection
  - Reliable refactoring impact predictions
  - Proper team ownership mapping
  - Valid sprint planning estimates

- **Critical user scenarios that should be tested**:
  - Analyzing a legacy monolith to prioritize decomposition efforts
  - Detecting circular dependencies in a microservices transition
  - Planning quarterly refactoring sprints with resource constraints
  - Identifying cross-team coupling in a large organization
  - Tracking debt reduction progress over multiple sprints

- **Performance benchmarks that must be met**:
  - Calculate debt scores for 10,000 modules in under 60 seconds
  - Generate refactoring plans for 100 identified issues in under 30 seconds
  - Process ownership data for 1,000 contributors in under 10 seconds
  - Incremental analysis of changes in under 5 seconds

- **Edge cases and error conditions that must be handled properly**:
  - Missing or inconsistent ownership data
  - Extremely tangled legacy dependencies
  - Modules with no clear ownership
  - Partially migrated codebases
  - Generated code and vendored dependencies

- **Required test coverage metrics**:
  - Minimum 90% code coverage for debt scoring algorithms
  - 100% coverage for code smell detection patterns
  - Full coverage of planning estimate calculations
  - Integration tests for all supported ticket systems

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
- Provides debt scores that correlate with actual refactoring effort (R² > 0.8)
- Identifies 90% of high-priority refactoring opportunities
- Generates sprint plans accepted by teams in 85% of cases
- Reduces cross-team coordination issues by 60% through ownership mapping
- Enables 40% reduction in technical debt over 6 months through targeted efforts

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