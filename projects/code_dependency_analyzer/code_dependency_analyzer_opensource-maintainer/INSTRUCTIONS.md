# Open Source API Impact Analyzer

## Overview
A dependency analysis tool tailored for open source maintainers to track API usage across dependent projects, assess breaking change impacts, and manage deprecation cycles while maintaining backward compatibility for their community.

## Persona Description
A community leader managing a popular open-source library who needs to ensure backward compatibility while evolving the codebase. They must understand how external projects depend on their APIs.

## Key Requirements
1. **Public API usage tracking across dependent repositories**: The tool must scan external repositories that depend on the library to identify which public APIs are actually used in the wild, providing usage statistics and patterns to inform API evolution decisions.

2. **Breaking change impact analysis with affected function mapping**: Critical for responsible API evolution, the system must analyze proposed changes against known usage patterns, creating detailed maps of which external functions and classes would be affected by modifications to the library's API.

3. **Semantic versioning recommendation based on changes**: To maintain trust with the community, the tool must analyze code changes and automatically recommend appropriate version bumps (major, minor, patch) based on the nature of API modifications and their potential impact.

4. **Deprecation timeline planning with usage statistics**: Essential for smooth transitions, the system must track deprecated API usage over time, providing data-driven recommendations for deprecation timelines based on actual adoption rates of newer alternatives.

5. **Plugin architecture compatibility verification**: Since many open source projects support plugins, the tool must verify that API changes maintain compatibility with existing plugin interfaces and detect when plugin APIs need coordinated updates.

## Technical Requirements
- **Testability requirements**: All API analysis functions must be unit testable with mock repositories and usage data. Integration tests should verify analysis against real-world dependency scenarios.
- **Performance expectations**: Must analyze 1,000 dependent repositories within 30 minutes. API usage scanning should handle codebases with millions of lines efficiently through incremental analysis.
- **Integration points**: Must integrate with Git for change detection, GitHub/GitLab APIs for repository scanning, and provide webhooks for CI/CD systems to automate compatibility checks.
- **Key constraints**: Must work with incomplete repository access, handle various Python versions gracefully, and provide meaningful results even when some dependencies are private or unavailable.

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The analyzer must clone and scan dependent repositories, parse their code to identify API usage patterns, compare current APIs with proposed changes, calculate semantic versioning recommendations, track deprecation adoption rates, and generate comprehensive compatibility reports. The system should support caching of analysis results and provide APIs for custom compatibility rules.

## Testing Requirements
- **Key functionalities that must be verified**:
  - Accurate identification of public API usage in external codebases
  - Correct breaking change detection across different change types
  - Proper semantic versioning recommendations following semver spec
  - Reliable deprecation tracking and timeline calculations
  - Accurate plugin compatibility verification

- **Critical user scenarios that should be tested**:
  - Analyzing impact of removing a widely-used function parameter
  - Tracking adoption of a new API to replace deprecated functionality
  - Verifying plugin compatibility when modifying extension points
  - Assessing impact of changing return types on dependent projects
  - Planning deprecation timeline for legacy API based on usage data

- **Performance benchmarks that must be met**:
  - Scan 100 dependent repositories in under 10 minutes
  - Analyze 10,000 API calls per minute
  - Generate compatibility reports for 1,000 changes in under 60 seconds
  - Cache hit rate of 80% for previously analyzed repositories

- **Edge cases and error conditions that must be handled properly**:
  - Private or deleted dependent repositories
  - Repositories with syntax errors or non-standard structures
  - Dynamic API usage through getattr or eval
  - Monkey-patched APIs in dependent code
  - Multi-version compatibility requirements

- **Required test coverage metrics**:
  - Minimum 95% code coverage for API detection modules
  - 100% coverage for breaking change detection logic
  - Full coverage of semantic versioning rules
  - Integration tests covering all supported repository platforms

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
- Detects 95% of actual API usage patterns in dependent projects
- Accurately predicts breaking change impact with less than 5% false positives
- Provides semantic version recommendations that align with community expectations
- Enables deprecation cycles that maintain 99% compatibility throughout transition
- Reduces unintended breaking changes by 90% through proactive analysis

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