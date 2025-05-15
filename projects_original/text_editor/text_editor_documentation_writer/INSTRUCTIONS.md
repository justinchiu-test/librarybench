# Technical Documentation Text Editor

A specialized text editor library designed for technical documentation writers with advanced features for code sample validation and documentation-specific checks.

## Overview

This project implements a text editor library specifically designed for technical writers who create software documentation. It provides code sample validation, documentation-specific linting, multi-format preview, API reference integration, and screenshot automation capabilities.

## Persona Description

Carlos creates software documentation combining code examples, command sequences, and explanatory text. He needs specialized features for working with mixed content while ensuring technical accuracy.

## Key Requirements

1. **Code Sample Validation**: Implement a system that automatically tests embedded code examples for correctness. This is critical for Carlos to ensure that code samples in documentation are syntactically valid and produce expected results, preventing readers from encountering errors when following tutorials or implementing examples.

2. **Documentation-Specific Linting**: Develop specialized linting capabilities that check for clarity, completeness, and terminology consistency. This helps Carlos maintain high-quality documentation standards by identifying unclear explanations, missing information, inconsistent terms, and other documentation-specific issues that general text editors don't detect.

3. **Multi-Format Preview**: Create functionality showing how documentation content will appear when rendered in different documentation systems. This allows Carlos to visualize how his content will be presented across various platforms (HTML, PDF, in-app help, etc.) without leaving the editor, ensuring consistent appearance and readability.

4. **API Reference Integration**: Implement automatic updating of examples when APIs change in the source code. This keeps Carlos's documentation synchronized with the actual code, automatically flagging outdated examples when APIs evolve and suggesting updates to maintain documentation accuracy.

5. **Screenshot Automation**: Develop capabilities to generate terminal captures from command sequences. This enables Carlos to create accurate, consistent screenshots of command-line operations directly from documented commands, eliminating manual terminal work and ensuring screenshots match the exact commands in the documentation.

## Technical Requirements

### Testability Requirements
- Code validation must be testable with sample code snippets
- Documentation linting must be verifiable with example content containing known issues
- Format preview generation must be testable through predictable output comparison
- API reference tracking must be testable with simulated API changes
- Screenshot generation must be testable with predefined command sequences

### Performance Expectations
- Code validation should complete in under 2 seconds for most language examples
- Linting should process at least 10,000 words per second
- Format previews should generate in under 1 second for standard-length documents
- API reference checks should run in background with minimal performance impact
- Screenshot generation should complete within 5 seconds per command sequence

### Integration Points
- Code execution environments for multiple programming languages
- Documentation style guides and terminology databases
- Documentation format renderers (Markdown, reStructuredText, etc.)
- API documentation extraction from source code
- Terminal emulation for screenshot capture

### Key Constraints
- No UI/UX components; all functionality should be implemented as library code
- Code validation must run in a secure, sandboxed environment
- Must support documentation for multiple programming languages
- Must maintain separation between content and presentation
- Compatible with Python 3.8+ ecosystem

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The library should implement a text editor core with the following functionality:

1. A code validation system that:
   - Extracts code samples from documentation
   - Validates syntax for multiple programming languages
   - Executes code in a secure environment
   - Verifies output against documented expectations

2. A documentation linting system that:
   - Checks for clarity, completeness, and readability
   - Enforces consistent terminology usage
   - Identifies potentially confusing explanations
   - Validates against style guides and best practices

3. A format preview system that:
   - Renders content in multiple documentation formats
   - Shows how content will appear in different contexts
   - Identifies format-specific issues
   - Provides side-by-side comparison of formats

4. An API reference system that:
   - Links documentation to source code definitions
   - Detects when APIs change in the codebase
   - Flags outdated examples and references
   - Suggests updates based on current API signatures

5. A screenshot automation system that:
   - Generates terminal captures from command sequences
   - Ensures consistency between text and visuals
   - Supports different terminal styles and environments
   - Automatically updates screenshots when commands change

## Testing Requirements

### Key Functionalities to Verify
- Code validation correctly identifies valid and invalid code examples
- Documentation linting accurately detects clarity and terminology issues
- Format preview properly renders content in different documentation formats
- API reference integration successfully tracks changes in source code APIs
- Screenshot automation correctly generates terminal captures from commands

### Critical User Scenarios
- Validating Python code examples in a tutorial document
- Checking documentation against company terminology guidelines
- Previewing how content will render in HTML, PDF, and in-app help
- Updating examples when a documented API changes
- Generating a series of terminal screenshots for a command-line tutorial

### Performance Benchmarks
- Code validation should handle at least 50 code samples per minute
- Linting should complete in under 5 seconds for 10,000-word documents
- Format preview generation should support at least 5 different target formats
- API reference checking should process at least 100 API references per second
- Screenshot automation should generate at least 10 screenshots per minute

### Edge Cases and Error Conditions
- Handling code samples that require specific environments or dependencies
- Managing conflicting terminology requirements across different audiences
- Dealing with custom or non-standard documentation formats
- Tracking API changes that involve complex signature modifications
- Handling terminal commands that produce dynamic or timing-dependent output

### Required Test Coverage Metrics
- Minimum 90% code coverage across all core modules
- 100% coverage of code validation logic
- Complete coverage of all public API methods
- All supported documentation formats must have rendering tests
- All screenshot generation paths must have verification tests

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

1. Code sample validation correctly verifies syntax and execution of embedded examples
2. Documentation-specific linting accurately identifies clarity and terminology issues
3. Multi-format preview properly renders content in different documentation systems
4. API reference integration successfully flags outdated examples when APIs change
5. Screenshot automation correctly generates terminal captures from command sequences

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup

To set up the development environment:

1. Create a virtual environment:
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

4. CRITICAL: For running tests and generating the required json report:
   ```
   pip install pytest-json-report
   pytest --json-report --json-report-file=pytest_results.json
   ```

REMINDER: Generating and providing pytest_results.json is a critical requirement for project completion.