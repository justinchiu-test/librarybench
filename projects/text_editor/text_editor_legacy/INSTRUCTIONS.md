# Legacy Mainframe Text Editor Library

## Overview
A specialized text editing library designed for working with legacy mainframe systems and obsolete programming languages. This implementation focuses on fixed-width format handling, card deck simulation, EBCDIC encoding support, batch edit scripting, and vintage terminal emulation to facilitate maintenance of decades-old codebases.

## Persona Description
Eleanor works with decades-old codebases on mainframe systems. She needs specialized editing capabilities for obsolete languages and file formats while handling the constraints of terminal-based mainframe access.

## Key Requirements

1. **Fixed-Width Format Awareness**
   - Implement specialized handling for column-oriented languages like COBOL and Fortran
   - Critical for Eleanor as it maintains the strict positional format required by legacy languages where column position determines code meaning
   - Must enforce column constraints, visualize column boundaries, and provide column-aware text operations

2. **Card Deck Simulation**
   - Develop a system that represents the traditional 80-column punch card boundaries
   - Essential for maintaining compatibility with systems originally designed around physical card constraints
   - Must provide card-oriented operations, sequence numbering, and visualization of card boundaries

3. **EBCDIC Encoding Support**
   - Create comprehensive handling for mainframe-specific character encodings
   - Crucial for accurate representation and manipulation of files that use non-ASCII encoding standards
   - Must convert between EBCDIC, ASCII, and Unicode while preserving special characters and formatting

4. **Batch Edit Scripting**
   - Build a robust scripting system for applying consistent changes across ancient codebases
   - Allows Eleanor to perform systematic changes and refactoring across large legacy codebases
   - Must support pattern matching, positional editing, and record-oriented operations specific to mainframe files

5. **Vintage Terminal Emulation**
   - Implement support for historical display limitations and escape sequences
   - Provides accurate representation of how code will appear in native mainframe environments
   - Must emulate various terminal types (3270, VT100, etc.) with appropriate constraints and capabilities

## Technical Requirements

### Testability Requirements
- Column-aware editing must be testable with sample fixed-width code
- Card deck simulation must be verifiable for 80-column compliance
- EBCDIC conversion must be testable with reference conversion tables
- Batch edit scripts must be testable with sample mainframe code
- Terminal emulation must be verifiable for escape sequence handling

### Performance Expectations
- Column format validation should complete in under 100ms for 10,000-line files
- Card deck operations should process at least 1,000 records per second
- EBCDIC/ASCII conversion should process at least 5MB per second
- Batch edit operations should handle at least 500 files per minute
- Terminal emulation overhead should not exceed 10% of base operations

### Integration Points
- Character encoding conversion libraries
- Mainframe connectivity protocols (3270, TN3270)
- Job Control Language (JCL) integration
- Batch processing systems
- Record-oriented file formats (VSAM, ISAM, etc.)

### Key Constraints
- All functionality must be accessible programmatically with no UI dependencies
- The system must preserve exact formatting and whitespace
- Operations must maintain backward compatibility with legacy systems
- Column constraints must be strictly enforced where required
- File operations must preserve record-oriented structure

## Core Functionality

The implementation should provide a comprehensive legacy system editing library with:

1. **Column-Oriented Editing Engine**
   - Fixed-width format enforcement
   - Column boundary visualization
   - Area-specific operations (A/B margins in COBOL)
   - Column-aware search and manipulation

2. **Card Deck Management System**
   - 80-column record management
   - Card sequence numbering
   - Deck organization and navigation
   - Card-oriented operations

3. **Character Encoding Framework**
   - EBCDIC/ASCII/Unicode conversion
   - Code page support for various mainframes
   - Special character handling
   - Binary data representation

4. **Batch Processing System**
   - Scripted edit operations
   - Pattern matching for legacy formats
   - Mass file transformation
   - Auditing and reporting

5. **Terminal Compatibility Layer**
   - Escape sequence handling
   - Display limitation simulation
   - Color and attribute mapping
   - Line-oriented editing modes

## Testing Requirements

### Key Functionalities to Verify
- Correct handling of column-oriented code formats
- Proper enforcement of 80-column card boundaries
- Accurate conversion between character encodings
- Reliable execution of batch edit operations
- Faithful emulation of vintage terminal behavior

### Critical User Scenarios
- Editing COBOL code with strict column constraints
- Converting between EBCDIC and ASCII file formats
- Applying consistent changes across hundreds of similar files
- Working with record-oriented mainframe file formats
- Visualizing output as it would appear on native terminals

### Performance Benchmarks
- Column validation should process >10,000 lines per second
- EBCDIC conversion should handle >5MB per second
- Batch edit operations should process >100 files per minute
- Card deck operations should handle >1,000 cards per second
- All operations should maintain memory usage below 200MB

### Edge Cases and Error Conditions
- Mixed encoding files with both EBCDIC and ASCII sections
- Malformed or corrupted punch card data
- Invalid column usage in fixed-width formats
- Complex batch edit scenarios with dependencies
- Unusual or proprietary terminal escape sequences

### Required Test Coverage Metrics
- >95% code coverage for column format handling
- >90% coverage for EBCDIC conversion
- >90% coverage for batch edit scripting
- >85% coverage for terminal emulation
- >90% overall project coverage

## Success Criteria
- Fixed-width format editing correctly maintains column constraints
- Card deck operations accurately simulate 80-column boundaries
- EBCDIC encoding support correctly handles character conversion
- Batch edit scripting successfully applies changes across multiple files
- Terminal emulation faithfully reproduces legacy display characteristics
- Eleanor can efficiently maintain decades-old codebases with appropriate tools

## Getting Started

To set up your development environment:

```bash
# Create a new virtual environment and install dependencies
uv init --lib

# Run a Python script
uv run python your_script.py

# Run tests
uv run pytest

# Check code quality
uv run ruff check .
uv run pyright
```

Focus on implementing the core functionality as library components with well-defined APIs. Remember that this implementation should have NO UI components and should be designed for testing with sample legacy code formats.