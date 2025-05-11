# Security Research Text Editor

A specialized text editor library designed for security researchers analyzing code and malware samples with advanced safety features.

## Overview

This project implements a text editor library specifically designed for security researchers who analyze suspicious code and malware samples. It provides sandbox mode, binary visualization tools, pattern matching capabilities, safe execution environment, and obfuscation analysis tools.

## Persona Description

Priya analyzes suspicious code and malware samples as part of security investigations. She needs specialized editor features for safely handling potentially malicious files while performing deep analysis.

## Key Requirements

1. **Sandbox Mode**: Implement a protective environment that prevents executed or evaluated code from accessing system resources. This is critical for Priya to safely analyze potentially malicious code without risking compromise of her system, allowing secure inspection of suspicious samples.

2. **Binary Visualization Tools**: Develop capabilities to display hexadecimal and various encodings side-by-side. This allows Priya to identify patterns in binary data, spot encoded payloads, and understand how binary content is structured, making it easier to recognize malicious binary components.

3. **Pattern Matching**: Create advanced search functionality that can highlight potential signature patterns across large codebases. This helps Priya identify known malicious patterns or suspicious code structures across many files, accelerating the process of finding security-relevant code in large projects.

4. **Safe Execution Environment**: Implement a system for running selected code in isolated containers. This enables Priya to observe the behavior of suspicious code in a controlled environment, capturing its actions, network attempts, and file operations without endangering the actual system.

5. **Obfuscation Analysis Tools**: Develop specialized tools for detecting and unwrapping common code hiding techniques. This helps Priya analyze heavily obfuscated malicious code by automatically identifying and reversing obfuscation methods like string encoding, control flow flattening, and dead code insertion.

## Technical Requirements

### Testability Requirements
- Sandbox isolation must be verifiable through attempted resource access
- Binary visualization must be testable with known binary patterns
- Pattern matching must be demonstrable with signature test cases
- Execution environment must prove isolation with resource access attempts
- Obfuscation analysis must be testable with known obfuscation techniques

### Performance Expectations
- Sandbox initialization should complete in under 2 seconds
- Binary visualization should handle files up to 100MB with responsive performance
- Pattern matching should scan at least 10MB of code per second
- Safe execution environment should launch within 3 seconds
- Obfuscation analysis should process at least 5,000 lines of code per minute

### Integration Points
- Container and virtualization technologies
- Binary analysis frameworks
- Signature and pattern databases
- Dynamic analysis tools
- Code transformation and deobfuscation libraries

### Key Constraints
- No UI/UX components; all functionality should be implemented as library code
- Must maintain secure isolation between analyzed code and the host system
- Must handle potentially malformed or intentionally malicious files
- Analysis must not alter original samples without explicit action
- Compatible with Python 3.8+ ecosystem

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The library should implement a text editor core with the following functionality:

1. A sandbox system that:
   - Creates isolated environments for code inspection
   - Prevents access to system resources and network
   - Monitors attempted access to protected resources
   - Provides detailed logs of code behavior

2. A binary visualization system that:
   - Displays data in multiple formats simultaneously (hex, ASCII, etc.)
   - Highlights patterns and structures in binary data
   - Identifies encoded content and potential payloads
   - Supports navigation through binary structures

3. A pattern matching system that:
   - Searches for known malicious signatures
   - Identifies suspicious code patterns
   - Performs fuzzy matching for variant detection
   - Correlates findings across multiple files

4. A safe execution system that:
   - Runs selected code in isolated containers
   - Captures execution behavior and output
   - Monitors resource access attempts
   - Provides detailed execution tracing

5. An obfuscation analysis system that:
   - Detects common obfuscation techniques
   - Unravels string encoding and encryption
   - Simplifies obfuscated control flow
   - Reconstructs original code functionality

## Testing Requirements

### Key Functionalities to Verify
- Sandbox mode successfully prevents access to protected system resources
- Binary visualization correctly displays data in multiple formats
- Pattern matching accurately identifies known malicious signatures
- Safe execution environment properly isolates and monitors code execution
- Obfuscation analysis successfully detects and unwraps common hiding techniques

### Critical User Scenarios
- Analyzing a suspicious JavaScript file with potential system access
- Examining a binary file with embedded encoded payloads
- Scanning a large codebase for potential security vulnerabilities
- Executing a suspicious script to observe its behavior
- Analyzing heavily obfuscated code to determine its true functionality

### Performance Benchmarks
- Sandbox initialization should be ready in under 2 seconds
- Binary visualization should handle at least 50MB files with responsive scrolling
- Pattern matching should scan at least 100,000 lines of code in under 30 seconds
- Safe execution environment should support scripts running for up to 5 minutes
- Obfuscation analysis should handle files with up to 10 layers of obfuscation

### Edge Cases and Error Conditions
- Handling intentionally malformed files designed to crash analysis tools
- Managing extremely large binary files (1GB+)
- Dealing with sophisticated evasion techniques in malicious code
- Recovering from crashes during safe execution
- Handling custom or previously unseen obfuscation methods

### Required Test Coverage Metrics
- Minimum 95% code coverage across all security-critical modules
- 100% coverage of sandbox implementation
- Complete coverage of all public API methods
- All supported file formats must have binary visualization tests
- All known obfuscation techniques must have detection tests

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

1. Sandbox mode effectively prevents potentially malicious code from accessing system resources
2. Binary visualization tools clearly represent binary data in multiple useful formats
3. Pattern matching successfully identifies known malicious signatures across large codebases
4. Safe execution environment properly isolates and monitors code behavior
5. Obfuscation analysis tools successfully detect and unwrap common code hiding techniques

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