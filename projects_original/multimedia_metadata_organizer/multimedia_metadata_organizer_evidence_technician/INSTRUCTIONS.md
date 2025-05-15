# Digital Evidence Metadata Management System

## Overview
A specialized metadata organization system for law enforcement evidence technicians who need to maintain strict chain of custody for digital media evidence while organizing case-related media in a format suitable for court proceedings.

## Persona Description
Officer Rodriguez processes digital media evidence for law enforcement cases. He needs to maintain strict chain of custody while organizing case-related media in a way that's presentable in court proceedings.

## Key Requirements
1. **Tamper-evident metadata verification**: Implement cryptographic mechanisms to ensure that media files and their metadata have not been modified since acquisition. This is critical for maintaining evidence integrity and admissibility in court, where any modification could render evidence invalid.

2. **Chain of custody logging**: Create a comprehensive system to document every access and modification with officer credentials, timestamps, and actions taken. This provides an unbroken record of evidence handling that can withstand legal scrutiny and is essential for court admissibility.

3. **Case hierarchy organization**: Develop a structured system linking evidence to specific cases, charges, and legal statutes. This enables efficient organization of evidence across complex investigations with multiple subjects, charges, and related cases.

4. **Automatic PII detection**: Build functionality to identify and protect personally identifiable information in media metadata and content. This ensures compliance with privacy regulations and prevents inadvertent disclosure of sensitive information.

5. **Court exhibit preparation**: Create tools to generate properly redacted and formatted files suitable for legal proceedings. This streamlines the creation of court-ready exhibits that meet specific jurisdictional requirements and procedural rules.

## Technical Requirements

### Testability Requirements
- All cryptographic verification functions must be independently testable
- Chain of custody functions must support comprehensive audit testing
- Use test fixtures with sample evidence metadata and access patterns
- Support simulation of access attempts with various authentication levels

### Performance Expectations
- Process verification for at least 100 evidence items per minute
- Support evidence collections with up to 100,000 items per case
- All operations must maintain tamper-evident logs
- Court exhibit generation should complete in under 30 seconds per item

### Integration Points
- Common media file formats (images, videos, audio) and their metadata
- Cryptographic hashing and signature verification systems
- Legal case management data structures
- PII detection algorithms and pattern matching
- Standard court exhibit formats and requirements

### Key Constraints
- No UI components - all functionality exposed through Python APIs
- All operations must maintain cryptographic integrity
- System must function in air-gapped environments
- Access patterns must follow principle of least privilege
- All actions must be non-destructive to original evidence

## Core Functionality

The system must provide a Python library that enables:

1. **Evidence Integrity Management**
   - Generate and verify cryptographic hashes for media files
   - Track and verify metadata integrity separately from content
   - Detect and alert on any unauthorized modifications

2. **Chain of Custody Tracking**
   - Log all access attempts and actions with authentication details
   - Maintain immutable access history for each evidence item
   - Generate chain of custody reports for court submissions

3. **Case Organization and Classification**
   - Structure evidence hierarchically by case, subject, and charge
   - Link evidence to applicable legal statutes
   - Support complex relationships between related cases

4. **Privacy and Compliance**
   - Detect PII in metadata and media content
   - Apply appropriate redaction based on case requirements
   - Track compliance with relevant legal and departmental policies

5. **Legal Presentation Preparation**
   - Generate court-ready exhibits from raw evidence
   - Apply appropriate redactions and annotations
   - Package evidence for different legal proceedings

## Testing Requirements

The implementation must include tests that verify:

1. **Tamper Detection**
   - Test detection of file modifications
   - Test detection of metadata alterations
   - Test verification of cryptographic signatures

2. **Chain of Custody**
   - Test logging of all access and modifications
   - Verify complete chain from acquisition to presentation
   - Test detection of authentication issues

3. **Case Organization**
   - Test hierarchical organization of evidence
   - Verify linking to cases, charges, and statutes
   - Test handling of evidence spanning multiple cases

4. **PII Protection**
   - Test detection of various PII types in metadata
   - Verify appropriate redaction and protection
   - Test handling of different jurisdictional requirements

5. **Exhibit Preparation**
   - Test generation of court exhibits in various formats
   - Verify appropriate redaction in exhibits
   - Test compliance with court submission requirements

**IMPORTANT:**
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

## Setup Instructions
1. Set up a virtual environment using `uv venv`
2. Activate the environment: `source .venv/bin/activate`
3. Install the project: `uv pip install -e .`

## Success Criteria

The implementation will be considered successful if:

1. All five key requirements are fully implemented
2. Tamper-evident verification successfully detects any modifications to evidence
3. Chain of custody logging maintains a complete and verifiable record of all access
4. Case hierarchy organization correctly links evidence to legal contexts
5. PII detection identifies and protects sensitive information
6. Court exhibit preparation generates properly formatted and redacted outputs
7. All operations maintain cryptographic integrity of evidence
8. All tests pass when run with pytest
9. A valid pytest_results.json file is generated showing all tests passing

**REMINDER: Generating and providing pytest_results.json is a CRITICAL requirement for project completion.**
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```