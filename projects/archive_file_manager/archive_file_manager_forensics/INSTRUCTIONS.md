# Forensic Archive Analysis Tool

## Overview
A specialized archive management system designed for digital forensics investigators to extract, analyze, and maintain evidence from various archive formats while ensuring data integrity and maintaining proper chain of custody for legal proceedings.

## Persona Description
A cybersecurity professional who analyzes archived data for evidence in legal cases. They need to extract and examine files from various archive formats while maintaining chain of custody and ensuring data integrity.

## Key Requirements

1. **Forensic Hash Verification with MD5/SHA256 Checksums**
   - Critical for proving evidence hasn't been tampered with during extraction
   - Must calculate and verify checksums for every file before, during, and after extraction
   - Store checksums in a tamper-evident format for court admissibility
   - Support both MD5 (legacy) and SHA256 (modern standard) algorithms

2. **Read-Only Archive Mounting**
   - Essential to prevent accidental modification of original evidence
   - Implement virtual filesystem mounting that prohibits any write operations
   - Ensure all operations create working copies, never modifying source archives
   - Provide verification that original archive remains unmodified after operations

3. **Detailed Extraction Logs with Timestamps and Metadata Preservation**
   - Required for establishing chain of custody in legal proceedings
   - Log every operation with nanosecond-precision timestamps
   - Preserve all original file metadata (creation dates, permissions, attributes)
   - Generate court-admissible reports documenting all forensic activities

4. **Support for Password-Cracking Integration**
   - Necessary for accessing encrypted evidence archives
   - Provide API for integrating with password recovery tools
   - Support dictionary attacks, brute force, and rainbow table methods
   - Log all password attempts and successful recoveries with timestamps

5. **Binary Diff Comparison Between Archive Versions**
   - Critical for tracking changes and identifying evidence tampering
   - Perform byte-level comparisons between different archive versions
   - Generate detailed reports showing exactly what changed between versions
   - Support visualization of binary differences for court presentations

## Technical Requirements

### Testability Requirements
- All functions must be thoroughly testable via pytest
- Mock filesystem operations for isolation
- Simulate various archive formats and corruption scenarios
- Test cryptographic operations with known test vectors

### Performance Expectations
- Process archives up to 100GB efficiently
- Calculate checksums at minimum 100MB/s
- Support parallel processing for multi-core systems
- Minimal memory footprint for resource-constrained forensic workstations

### Integration Points
- Standard forensic tool APIs (EnCase, FTK compatible exports)
- Password cracking tool interfaces (John the Ripper, Hashcat)
- Evidence management system APIs
- Court reporting format generators

### Key Constraints
- Must never modify original evidence files
- All operations must be fully auditable
- Comply with digital forensics best practices
- Support air-gapped operation for secure environments

**IMPORTANT**: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The forensic archive tool must provide:

1. **Evidence Integrity Management**
   - Cryptographic hash calculation and verification
   - Tamper detection mechanisms
   - Chain of custody documentation

2. **Safe Evidence Extraction**
   - Read-only archive access
   - Metadata preservation during extraction
   - Quarantine mechanisms for suspicious files

3. **Forensic Analysis Support**
   - Binary comparison capabilities
   - File carving from corrupted archives
   - Timeline reconstruction from metadata

4. **Password Recovery Integration**
   - Pluggable password attack interfaces
   - Progress tracking and resumption
   - Result logging and reporting

5. **Audit Trail Generation**
   - Comprehensive operation logging
   - Timestamp accuracy and verification
   - Export to standard forensic formats

## Testing Requirements

### Key Functionalities to Verify
- Hash calculation accuracy for various file types and sizes
- Read-only mounting prevents any modifications
- Metadata preservation during extraction operations
- Password recovery integration with mock cracking tools
- Binary diff accuracy for detecting subtle changes

### Critical User Scenarios
- Extract evidence from password-protected archive without modifying original
- Verify integrity of extracted files matches original archive contents
- Compare two versions of an archive to identify tampering
- Generate court-admissible chain of custody documentation
- Recover files from partially corrupted archives

### Performance Benchmarks
- Calculate SHA256 for 1GB file in under 10 seconds
- Extract 10,000 files while preserving all metadata
- Compare two 100MB archives in under 30 seconds
- Support concurrent analysis of multiple archives

### Edge Cases and Error Conditions
- Handle corrupted archive headers gracefully
- Process archives with malformed passwords
- Manage nested encrypted archives
- Deal with filesystem limitations (path length, special characters)
- Recover from interrupted extraction operations

### Required Test Coverage
- Minimum 90% code coverage
- All cryptographic functions must have 100% coverage
- Error handling paths must be thoroughly tested
- Integration tests for password cracking interfaces

**IMPORTANT**:
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

The implementation will be considered successful when:

1. **Evidence Integrity**: All extracted files have verified checksums matching the originals
2. **Legal Compliance**: Generated reports meet court admissibility standards
3. **Non-Modification**: Original archives remain completely unmodified after all operations
4. **Password Recovery**: Successfully integrates with at least two password cracking tools
5. **Change Detection**: Accurately identifies all differences between archive versions
6. **Performance**: Meets all specified performance benchmarks
7. **Reliability**: Handles corrupted archives without data loss or crashes
8. **Auditability**: Every operation is logged with sufficient detail for legal review

**REQUIRED FOR SUCCESS**:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup

Use `uv venv` to setup virtual environments. From within the project directory:
```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

## Final Deliverable Requirements

The completed implementation must include:
1. Python package with all forensic archive functionality
2. Comprehensive pytest test suite
3. Generated pytest_results.json showing all tests passing
4. No UI components - only programmatic interfaces
5. Full compliance with digital forensics best practices