# PyPatternGuard - Mobile Development Pattern Detection Engine

## Overview
A specialized code pattern detection system designed for mobile app developers working on cross-platform applications. The system detects platform-specific anti-patterns, analyzes resource usage patterns, and ensures consistent behavior across iOS and Android platforms.

## Persona Description
A mobile app developer working on cross-platform applications who needs to detect platform-specific anti-patterns. She wants to ensure consistent behavior across iOS and Android while avoiding common mobile pitfalls.

## Key Requirements

1. **Platform-specific API misuse detection for mobile frameworks**: Critical for preventing runtime crashes and ensuring proper usage of platform APIs in frameworks like React Native, Flutter, or Kivy, catching common mistakes before they reach production.

2. **Battery drain pattern analysis for background operations**: Essential for mobile app quality by identifying code patterns that could cause excessive battery consumption through inefficient background tasks, wake locks, or polling mechanisms.

3. **Memory management pattern detection for mobile constraints**: Identifies memory leaks, retention cycles, and inefficient memory usage patterns that are particularly problematic on memory-constrained mobile devices.

4. **UI thread blocking pattern identification**: Detects operations that could block the main UI thread causing app freezes, poor responsiveness, and negative user experiences on mobile devices.

5. **Cross-platform compatibility pattern verification**: Ensures code written for one platform doesn't use patterns that fail or behave differently on other platforms, maintaining consistency across iOS and Android.

## Technical Requirements

### Testability Requirements
- All pattern detection must work with code samples from various mobile frameworks
- Support for mocking platform-specific behaviors and constraints
- Ability to simulate different device configurations and limitations
- Clear reporting of platform-specific vs. cross-platform issues

### Performance Expectations
- Analyze mobile app codebases up to 500,000 lines within 5 minutes
- Real-time pattern detection for development workflows
- Memory usage under 1GB to run on developer machines
- Incremental analysis for rapid feedback during development

### Integration Points
- AST analysis for Python-based mobile frameworks (Kivy, BeeWare)
- Pattern detection for Python code interfacing with native modules
- Configuration support for different mobile frameworks
- Export capabilities for mobile-specific linting tools

### Key Constraints
- Must work with Python 3.8+ mobile development code
- No external dependencies beyond Python standard library
- Must handle framework-specific patterns and idioms
- Analysis must not require mobile device or emulator

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system must provide:

1. **Platform API Usage Analyzer**: Scans code for framework-specific API calls, validates correct usage patterns, identifies platform-specific code that should be abstracted, and detects deprecated or dangerous API usage.

2. **Battery Impact Detector**: Analyzes background task patterns, identifies excessive network polling, detects wake lock usage and potential leaks, evaluates sensor usage efficiency, and flags battery-intensive operations.

3. **Memory Pattern Scanner**: Identifies object retention patterns that could cause leaks, detects circular references in event handlers, analyzes image and data caching strategies, and validates proper cleanup in lifecycle methods.

4. **UI Thread Safety Checker**: Detects blocking I/O operations on main thread, identifies synchronous network calls in UI code, analyzes database operations for thread safety, and validates proper async/await usage patterns.

5. **Compatibility Verifier**: Compares code patterns against platform compatibility matrix, identifies platform-specific assumptions in shared code, validates consistent behavior across platforms, and detects usage of platform-exclusive features.

## Testing Requirements

### Key Functionalities to Verify
- Accurate detection of platform-specific API misuse
- Correct identification of battery-draining patterns
- Comprehensive memory leak detection across scenarios
- UI thread blocking detection with low false positives
- Cross-platform compatibility validation accuracy

### Critical User Scenarios
- Analyzing a React Native app for platform-specific issues
- Detecting battery drain in a location-tracking application
- Identifying memory leaks in an image-heavy social app
- Finding UI freezes in a real-time messaging application
- Validating cross-platform consistency in a shopping app

### Performance Benchmarks
- API usage analysis: < 1 second per 1,000 lines of code
- Battery pattern detection: < 2 seconds per module
- Memory pattern scanning: < 500ms per class
- UI thread analysis: < 1 second per view controller
- Full analysis of 50,000 LOC mobile app: < 60 seconds

### Edge Cases and Error Conditions
- Dynamic API loading and reflection usage
- Native module integration points
- Complex async/await chains
- Framework-specific lifecycle methods
- Platform-specific conditional compilation

### Required Test Coverage Metrics
- Line coverage: minimum 90%
- Branch coverage: minimum 85%
- All major mobile frameworks must have test cases
- Platform-specific patterns must be thoroughly tested
- Integration tests covering real mobile app scenarios

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

1. **Pattern Detection Accuracy**: The system identifies 95% of known mobile anti-patterns with less than 5% false positives across different frameworks.

2. **Performance Impact**: Detected battery and memory issues, when fixed, result in measurable improvements in app performance metrics.

3. **Cross-Platform Consistency**: Apps analyzed and corrected using the tool show 90% fewer platform-specific bugs in production.

4. **Developer Productivity**: Integration into development workflow reduces mobile-specific bugs by 80% before code review.

5. **Framework Coverage**: The system effectively analyzes code from at least 3 major Python mobile frameworks.

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