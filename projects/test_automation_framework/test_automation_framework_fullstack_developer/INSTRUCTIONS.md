# Responsive Test Suite for Full-Stack Applications

## Overview
A specialized test automation framework tailored for full-stack developers who need to efficiently write and maintain tests across the entire application stack while balancing testing needs with feature development and tight deadlines. The framework automatically prioritizes tests for recently modified code, provides instant feedback during development, and handles both frontend and backend testing with minimal configuration.

## Persona Description
Alex works as the primary developer for a rapidly evolving web application with no dedicated QA team. He needs to efficiently write and maintain tests across the entire stack while balancing testing needs with feature development and tight deadlines.

## Key Requirements
1. **Context-aware test runner**: Build a test runner that automatically detects and prioritizes tests relevant to recently modified code. This is critical for Alex because it allows him to focus testing efforts on areas most likely to be affected by recent changes, making the most of limited testing time.

2. **Development mode with instant feedback**: Implement a development mode that provides instant test feedback during coding without requiring manual test execution. This feature is essential because it catches issues immediately as Alex codes, reducing the time between introducing a bug and discovering it.

3. **Unified testing approach for frontend and backend**: Create a unified testing system that covers both frontend JavaScript and backend Python code with minimal configuration. This feature is vital as it eliminates the complexity of managing separate testing frameworks for different parts of the stack, saving valuable time.

4. **IDE integration for inline results and coverage**: Develop APIs that enable IDE plugins to display inline test results and coverage visualization. This capability is important because it makes test results immediately visible in the development environment, enhancing Alex's understanding of test coverage without switching contexts.

5. **Time-boxed testing**: Implement a system that automatically selects and runs critical tests when facing tight deadlines. This feature is crucial for Alex because it ensures that essential functionality is verified even under severe time constraints, preventing critical defects from reaching production.

## Technical Requirements
- **Testability Requirements**:
  - All components must be testable in isolation with appropriate mocking capabilities
  - Support for both synchronous and asynchronous test execution
  - Ability to detect and handle code changes to trigger selective test runs
  - Support for test doubles (mocks, stubs, fakes) for both Python and JavaScript code

- **Performance Expectations**:
  - Test feedback in development mode must be provided in under 2 seconds
  - Full test suite execution should complete in under 5 minutes on standard development hardware
  - Minimal CPU and memory overhead when running in watch mode
  - Test prioritization algorithms must execute in under 500ms

- **Integration Points**:
  - Version control system integration to detect changed files
  - Python test framework compatibility (pytest)
  - JavaScript test framework compatibility (Jest or similar)
  - Common IDE extension APIs
  - CI/CD pipeline integration

- **Key Constraints**:
  - No UI/UX components, all functionality exposed as Python APIs
  - All features must be usable programmatically without manual intervention
  - Minimal external dependencies to ensure quick setup in new projects
  - Cross-platform compatibility (Windows, macOS, Linux)

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The framework must implement these core capabilities:

1. **Change Detection System**:
   - File monitoring for detecting code changes
   - Git integration for identifying recently modified files
   - Source code parsing to build dependency graphs between files
   - Test-to-code mapping to identify which tests cover which code

2. **Test Prioritization Engine**:
   - Algorithms to rank tests based on relevance to recent changes
   - Historical test execution data analysis
   - Critical path identification in application code
   - Code coverage analysis to identify tests with highest impact

3. **Multi-language Test Runner**:
   - Python test execution adapter
   - JavaScript test execution adapter
   - Test result normalization across different languages
   - Unified reporting interface

4. **Development Mode**:
   - Watch mode for continuous test execution
   - Fast test selection for instant feedback
   - Incremental testing based on code changes
   - Test result caching to avoid redundant execution

5. **Time Management**:
   - Test execution time measurement and tracking
   - Time-based test selection algorithms
   - Critical test identification based on application functionality
   - Time budget allocation across test suites

## Testing Requirements
The implementation must include comprehensive tests that verify:

- **Key Functionalities**:
  - Test selection correctly identifies tests affected by code changes
  - Development mode correctly detects file changes and runs relevant tests
  - Time-boxed testing selects the most important tests within constraints
  - Test results are correctly reported for both Python and JavaScript tests
  - File dependencies are correctly mapped for accurate test selection

- **Critical User Scenarios**:
  - Developer modifies code and receives immediate feedback on affected functionality
  - Developer works with tight deadline and framework focuses on critical tests
  - Developer adds new files and framework correctly incorporates them into test selection
  - Developer switches between frontend and backend work with consistent testing experience
  - Test coverage gradually improves as framework identifies undertested areas

- **Performance Benchmarks**:
  - Test feedback latency under 2 seconds in development mode
  - File change detection within 100ms
  - Test selection algorithm completes in under 500ms for projects with up to 1000 test files
  - Memory usage remains under 200MB during continuous operation
  - CPU utilization stays below 10% when idle in watch mode

- **Edge Cases and Error Conditions**:
  - Handling malformed or syntactically incorrect test files
  - Recovery from test execution failures without crashing the framework
  - Correct behavior when file system events are rapid or overwhelming
  - Appropriate fallback when version control information is unavailable
  - Graceful degradation when resource constraints prevent optimal operation

- **Required Test Coverage Metrics**:
  - Minimum 95% line coverage for core framework code
  - 100% coverage of public API functions
  - All error handling paths must be covered
  - All supported language adapters must be thoroughly tested
  - Critical algorithms (dependency analysis, test selection) require extensive property-based testing

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
The implementation will be considered successful when:

1. An experienced developer can add the framework to a new project with less than 10 minutes of setup
2. The framework correctly identifies and runs only the tests affected by code changes with at least 95% accuracy
3. Development mode provides test feedback within 2 seconds of code changes
4. Time-boxed testing mode correctly selects critical tests and completes within the specified time budget
5. Both Python backend and JavaScript frontend tests can be run from a single command with unified results
6. The test framework reduces overall testing time by at least 40% compared to running the full test suite each time
7. Integration points for IDEs provide all necessary information for inline result display
8. Under tight deadline conditions, the framework never fails to run the most critical tests
9. All test functionality is accessible programmatically through well-defined Python APIs
10. The framework can handle projects with at least 1000 test files without performance degradation

## Setup Instructions
To get started with the project:

1. Setup the development environment:
   ```bash
   uv init --lib
   ```

2. Install development dependencies:
   ```bash
   uv sync
   ```

3. Run tests:
   ```bash
   uv run pytest
   ```

4. Execute a specific Python script:
   ```bash
   uv run python script.py
   ```