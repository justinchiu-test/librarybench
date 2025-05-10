# Legacy System Code Editor Library

## Overview
A specialized text editor library designed for maintaining decades-old codebases on legacy systems, with particular focus on fixed-width formats, mainframe conventions, EBCDIC encoding support, batch editing capabilities, and vintage terminal emulation. This implementation addresses the unique challenges of working with obsolete languages and file formats.

## Persona Description
Eleanor works with decades-old codebases on mainframe systems. She needs specialized editing capabilities for obsolete languages and file formats while handling the constraints of terminal-based mainframe access.

## Key Requirements
1. **Fixed-Width Format Handler**: Implement a specialized text management system that enforces column-oriented formatting rules for languages like COBOL, FORTRAN, and Assembly. This is critical for Eleanor to maintain proper code structure in languages where precise column positioning determines syntax validity, preventing errors that would be introduced by modern free-form editing.

2. **Card Deck Simulation**: Create a visualization and editing paradigm that shows traditional 80-column boundaries and supports card-oriented operations. This helps Eleanor understand and maintain legacy code originally designed for punch card systems, preserving the mental model and constraints under which the original code was written.

3. **EBCDIC Encoding Support**: Develop comprehensive handling for EBCDIC character encoding used in mainframe environments, including conversion, display, and editing capabilities. This allows Eleanor to work directly with mainframe files without corruption or character set mismatches that would introduce subtle and dangerous bugs.

4. **Batch Edit Scripting System**: Build a powerful scripting system for applying consistent changes across large legacy codebases with pattern matching and transformation rules. This addresses Eleanor's need to make systematic changes across thousands of files while respecting the rigid formatting requirements of legacy languages.

5. **Vintage Terminal Emulation**: Implement support for historical terminal limitations and escape sequences, accurately representing how code appears on legacy systems. This ensures that Eleanor can preview code exactly as it will display on the target systems, preventing formatting surprises when code is deployed to mainframe environments.

## Technical Requirements
- **Testability Requirements**:
  - Column positioning rules must be verifiable against language specifications
  - Card deck visualization must conform to historical standards
  - EBCDIC conversion must be validated against reference implementations
  - Batch edit scripts must produce consistent results for identical inputs
  - Terminal emulation must accurately reproduce vintage display characteristics

- **Performance Expectations**:
  - Fixed-width formatting rules should apply with negligible overhead
  - EBCDIC/ASCII conversion should process at least 10MB per second
  - Batch edit operations should scale linearly with file size
  - The system should efficiently handle very large codebases (millions of lines)
  - Operations should complete with response times acceptable on vintage systems

- **Integration Points**:
  - Support for mainframe file transfer protocols (FTP, IND$FILE)
  - Compatibility with version control systems for tracking changes
  - Integration with legacy language compilers and tools
  - Support for common mainframe dataset formats
  - Connectivity with emulated or real mainframe environments

- **Key Constraints**:
  - Must strictly preserve column-oriented formatting
  - Must handle line lengths and file sizes dictated by legacy system limitations
  - Must preserve end-of-line conventions specific to target systems
  - Must not introduce modern characters unsupported in legacy environments
  - Must provide transparent conversion between modern and legacy encodings

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The text editor library should implement:

1. **Column-Aware Text Buffer**: A specialized text storage system that enforces fixed-width formatting rules.

2. **Card-Based Visualization**: Components for representing text in 80-column card formats and managing card-oriented operations.

3. **Character Encoding Engine**: Comprehensive tools for handling EBCDIC and other legacy encodings.

4. **Batch Transformation System**: A framework for defining and applying systematic changes across codebases.

5. **Terminal Rendering Engine**: Tools for simulating how text will appear on vintage terminal systems.

6. **Legacy Language Support**: Specific handlers for COBOL, FORTRAN, Assembly, and other legacy languages.

7. **Mainframe Connectivity**: Utilities for transferring files between modern systems and mainframes.

The library should use specialized data structures optimized for fixed-width text with column significance. It should provide programmatic interfaces for all functions without requiring a graphical interface, allowing it to be integrated with modern development environments while preserving compatibility with legacy systems.

## Testing Requirements
- **Key Functionalities to Verify**:
  - Accuracy of fixed-width formatting for various legacy languages
  - Correct visualization of card boundaries and column positions
  - Fidelity of EBCDIC encoding conversion
  - Reliability of batch editing across diverse file types
  - Accuracy of terminal emulation for different vintage systems

- **Critical User Scenarios**:
  - Editing COBOL programs with strict column requirements
  - Converting between mainframe and modern file formats
  - Applying systematic changes to large legacy codebases
  - Working with mixed-encoding files from different systems
  - Preparing code that will display correctly on vintage terminals

- **Performance Benchmarks**:
  - Column validation should add no more than 10% overhead to editing operations
  - EBCDIC conversion should process files at a rate of at least 20MB per minute
  - Batch edit operations should process at least 1000 files per hour
  - The system should handle codebases with up to 1 million lines efficiently
  - Operations should complete within timeframes appropriate for mainframe interaction

- **Edge Cases and Error Conditions**:
  - Handling files with mixed encodings or corrupted bytes
  - Managing line lengths that exceed traditional card limits
  - Dealing with legacy control characters and escape sequences
  - Recovering from interrupted batch operations
  - Handling incompatible language constructs across different mainframe systems

- **Required Test Coverage**:
  - 95% line coverage for column positioning and formatting rules
  - 100% coverage for EBCDIC conversion functionality
  - 90% coverage for batch editing operations
  - 90% coverage for terminal emulation features
  - Comprehensive tests for all supported legacy language formats

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
The implementation will be considered successful if:

1. It correctly enforces fixed-width formatting rules for legacy languages like COBOL and FORTRAN.

2. The card deck visualization accurately represents 80-column boundaries and card-oriented operations.

3. EBCDIC encoding support provides flawless conversion between mainframe and modern character sets.

4. Batch edit scripting enables efficient, systematic changes across large legacy codebases.

5. Terminal emulation accurately shows how code will appear on vintage display systems.

6. The system can effectively handle files from various mainframe environments without corruption.

7. All tests pass, demonstrating the reliability and accuracy of the implementation for legacy system maintenance.

To set up the virtual environment, use `uv venv` from within the project directory. The environment can be activated with `source .venv/bin/activate`.