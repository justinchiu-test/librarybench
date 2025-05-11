# Legacy System Maintenance Text Editor

A specialized text editor library designed for maintaining decades-old codebases on mainframe systems with support for obsolete languages and file formats.

## Overview

This project implements a text editor library specifically designed for developers working with legacy codebases on mainframe systems. It provides fixed-width format awareness, card deck simulation, EBCDIC encoding support, batch edit scripting, and vintage terminal emulation capabilities.

## Persona Description

Eleanor works with decades-old codebases on mainframe systems. She needs specialized editing capabilities for obsolete languages and file formats while handling the constraints of terminal-based mainframe access.

## Key Requirements

1. **Fixed-Width Format Awareness**: Implement support for column-oriented languages like COBOL where code positioning is significant. This is critical for Eleanor to maintain proper code alignment and prevent syntax errors in legacy languages where horizontal positioning affects program behavior.

2. **Card Deck Simulation**: Create a visual reference system showing traditional 80-column boundaries that mirrors punch card constraints. This helps Eleanor understand and maintain the historical formatting limitations that shaped legacy codebases, ensuring compatibility with systems that still enforce these boundaries.

3. **EBCDIC Encoding Support**: Develop conversion and display capabilities for Extended Binary Coded Decimal Interchange Code used in mainframe file formats. This allows Eleanor to work with authentic mainframe encodings, preventing character corruption when files are transferred between modern systems and legacy mainframes.

4. **Batch Edit Scripting**: Implement a system for defining and applying consistent changes across large legacy codebases. This enables Eleanor to safely make systematic modifications to widespread patterns in ancient code without introducing inconsistencies or errors during manual editing.

5. **Vintage Terminal Emulation**: Create support for historical display limitations and escape sequences used by legacy terminals. This helps Eleanor test how code will actually appear on original mainframe terminals, ensuring compatibility with older display technologies still in use for legacy system maintenance.

## Technical Requirements

### Testability Requirements
- Fixed-width formatting must be programmatically verifiable
- Card deck boundaries must be testable through column position detection
- EBCDIC conversion must be verifiable with known encoding test cases
- Batch edit operations must be testable with before/after comparison
- Terminal emulation must be validateable through escape sequence processing

### Performance Expectations
- Fixed-width format validation should process at least 5,000 lines per second
- Card deck visualization data should generate in under 10ms per line
- EBCDIC conversion should process at least 1MB per second
- Batch edit operations should handle at least 10,000 files in a single run
- Terminal emulation should process escape sequences with less than 5ms latency

### Integration Points
- Mainframe file transfer protocols
- EBCDIC conversion libraries
- Legacy language parsers (COBOL, FORTRAN, etc.)
- Batch processing systems
- Terminal emulation protocols

### Key Constraints
- No UI/UX components; all functionality should be implemented as library code
- Must handle files with line lengths up to 132 columns (wide format)
- Must preserve exact spacing and positioning in column-sensitive code
- Must prevent corruption of special EBCDIC characters
- Compatible with Python 3.8+ ecosystem

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The library should implement a text editor core with the following functionality:

1. A fixed-width formatting system that:
   - Maintains precise column positioning
   - Enforces language-specific column rules
   - Highlights position-dependent syntax elements
   - Prevents formatting errors in column-oriented code

2. A card deck visualization system that:
   - Shows 80-column boundaries
   - Provides card-oriented navigation
   - Simulates historical card deck organization
   - Enforces punch card constraints when needed

3. An encoding system that:
   - Converts between ASCII/Unicode and EBCDIC
   - Preserves special EBCDIC characters and control codes
   - Handles different EBCDIC code pages and variants
   - Prevents encoding corruption during file operations

4. A batch editing system that:
   - Defines reusable edit operations
   - Applies consistent changes across multiple files
   - Provides preview and validation of changes
   - Supports rollback of batch operations

5. A terminal emulation system that:
   - Processes legacy terminal escape sequences
   - Simulates display limitations of vintage terminals
   - Handles historical control codes
   - Shows how text will appear on legacy displays

## Testing Requirements

### Key Functionalities to Verify
- Fixed-width formatting correctly maintains column positioning
- Card deck visualization properly shows 80-column boundaries
- EBCDIC conversion accurately handles encoding transformations
- Batch edit scripting successfully applies consistent changes across files
- Vintage terminal emulation correctly processes historical escape sequences

### Critical User Scenarios
- Editing a COBOL program with column-significant syntax
- Working with code that must respect card deck boundaries
- Converting files between ASCII and EBCDIC encodings
- Applying a consistent change pattern across a legacy codebase
- Testing how code will appear on a vintage terminal display

### Performance Benchmarks
- Fixed-width validation should process at least 10,000 lines of code per minute
- Card deck visualization should handle files up to 100,000 lines
- EBCDIC conversion should support files up to 50MB
- Batch editing should process at least 1,000 files per minute
- Terminal emulation should handle at least 1,000 escape sequences per second

### Edge Cases and Error Conditions
- Handling lines that exceed traditional column limits
- Managing files with mixed encoding or corrupted characters
- Dealing with unsupported terminal control sequences
- Recovering from errors during batch edit operations
- Supporting very old versions of legacy languages

### Required Test Coverage Metrics
- Minimum 90% code coverage across all core modules
- 100% coverage of encoding conversion code
- Complete coverage of all public API methods
- All supported legacy formats must have verification tests
- All batch edit operations must have test coverage

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

1. Fixed-width format awareness correctly handles column-oriented languages
2. Card deck simulation properly represents 80-column boundaries
3. EBCDIC encoding support accurately converts between encodings
4. Batch edit scripting successfully applies consistent changes across files
5. Vintage terminal emulation correctly represents historical display limitations

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