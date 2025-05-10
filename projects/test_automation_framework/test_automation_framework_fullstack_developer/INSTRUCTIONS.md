# Rapid Testing Framework for Full-Stack Development

## Overview
A specialized test automation framework designed specifically for full-stack developers in startup environments who need to efficiently test across the entire application stack while balancing testing with rapid feature development. This framework prioritizes speed, simplicity, and developer productivity with minimal overhead.

## Persona Description
Alex works as the primary developer for a rapidly evolving web application with no dedicated QA team. He needs to efficiently write and maintain tests across the entire stack while balancing testing needs with feature development and tight deadlines.

## Key Requirements
1. **Context-aware test runner automatically detecting and prioritizing tests for recently modified code** - This feature is essential for Alex to focus testing efforts on components he's actively working on, eliminating the need to manually select tests and ensuring the most relevant parts of the codebase receive attention.

2. **Development mode with instant test feedback during coding without manual test execution** - As Alex constantly shifts between writing application code and tests, having tests automatically run in the background provides immediate feedback without interrupting his workflow, significantly improving development speed.

3. **Unified testing approach covering both frontend JavaScript and backend Python with minimal configuration** - With responsibility for the entire application stack, Alex needs a cohesive testing approach that works seamlessly across languages and layers, eliminating context switching and duplicate test setups.

4. **IDE integration providing inline test results and coverage visualization** - Direct integration with development environments helps Alex understand test status and coverage without leaving his editor, making testing a natural part of the development process rather than a separate activity.

5. **Time-boxed testing automatically selecting critical tests when facing tight deadlines** - During crunch periods before releases, this feature ensures essential tests still run while deferring less critical ones, helping Alex balance quality with delivery timelines.

## Technical Requirements
- **Testability requirements**
  - Must provide a unified Python API that can execute tests across different layers of the application stack
  - All components must be independently testable with minimal mocking requirements
  - Test execution must have deterministic results and be repeatable
  - Must support both synchronous and asynchronous testing patterns

- **Performance expectations**
  - Test discovery should complete in under 1 second for projects up to 100,000 lines of code
  - Development mode feedback should be provided within 2 seconds of saving a file
  - Should support running at least 500 tests per minute on standard development hardware
  - Memory usage should not exceed 200MB during normal test operations

- **Integration points**
  - Source control integration for detecting changed files
  - Editor/IDE integration capabilities via standard protocols
  - CI/CD platform integration for extended testing
  - Support for JavaScript test runners to enable cross-stack testing

- **Key constraints**
  - No UI components; all functionality exposed through APIs
  - Minimal external dependencies to ensure quick setup in new environments
  - All core functionality must work offline without external services
  - Cannot impact application performance when not in testing mode

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The framework needs to implement:

1. **File Change Monitoring System**: A module that watches file system changes, analyzes version control history, and maintains a priority index of which files need testing most urgently.

2. **Test Prioritization Engine**: An algorithm that ranks tests based on multiple factors: recency of code changes, test execution history, dependency relationships, and historical failure rates.

3. **Cross-language Test Runner**: A unified orchestration layer that can execute and collect results from both Python and JavaScript test frameworks through a common interface.

4. **Test Importance Classifier**: A system to categorize tests by criticality (must-run vs. deferrable) based on their coverage of core business logic and historical stability.

5. **Results Aggregation API**: A service that collects, normalizes, and exposes test results programmatically for consumption by IDEs and reporting tools.

6. **Observer Pattern Implementation**: A publisher-subscriber system for notifying listeners about file changes and test results in real-time.

7. **Resource Usage Optimizer**: Logic to control parallel test execution based on available system resources and prioritization needs.

## Testing Requirements
- **Key functionalities that must be verified**
  - Correct detection and prioritization of tests for changed files
  - Accurate execution of language-appropriate test runners
  - Proper time allocation for critical vs. non-critical tests
  - Reliable publisher-subscriber notification system

- **Critical user scenarios that should be tested**
  - Full-stack developer making simultaneous changes to frontend and backend components
  - Working under tight deadline conditions with limited testing time
  - Gradual accumulation of tests over time and impact on discovery performance
  - Responding to test failures across different application layers

- **Performance benchmarks that must be met**
  - Test prioritization should compute in under 500ms for codebases with up to 1000 tests
  - Complete feedback cycle under 3 seconds for affected tests after a file change
  - Memory consumption should remain stable regardless of test execution history 
  - Sequential execution of 100 tests should complete in under 10 seconds

- **Edge cases and error conditions that must be handled properly**
  - Detection of flaky tests that inconsistently pass/fail
  - Handling integration tests with external dependencies gracefully
  - Managing tests with interdependencies correctly
  - Recovery from unexpected test runner crashes

- **Required test coverage metrics**
  - Statement coverage: 85% minimum for core modules
  - Branch coverage: 80% minimum for prioritization algorithms
  - Function coverage: 90% minimum for public APIs
  - Tests for all public methods and properties

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
The implementation will be considered successful when:

1. A developer can modify multiple files across frontend and backend and have relevant tests automatically run within 5 seconds
2. Test prioritization correctly identifies and runs the most critical tests first when under time constraints
3. Test runs are at least 50% faster compared to running the full test suite
4. The system correctly tracks and reports test coverage across the full stack
5. Test results can be consumed programmatically by external tools through a well-defined API
6. All core functionality works without requiring any UI components
7. The framework can be initialized in a new project in under 2 minutes

To set up your development environment, use `uv venv` to create a virtual environment. From within the project directory, the environment can be activated with `source .venv/bin/activate`.