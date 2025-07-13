# PyBinParser - Medical Imaging Data Recovery Tool

## Overview
A specialized binary parser for healthcare professionals working with proprietary medical device formats. This tool enables extraction of patient data from vendor-specific imaging formats when standard tools fail, ensuring critical medical information remains accessible while maintaining data integrity and compliance.

## Persona Description
A healthcare professional working with proprietary medical device formats who needs to extract patient data when vendor tools fail. They must ensure data integrity while converting between formats.

## Key Requirements
1. **DICOM-Style Tag Extraction**: Parse proprietary formats to extract standardized medical imaging tags (patient ID, study date, modality, etc.) even when the format doesn't follow DICOM standards. Essential for maintaining continuity of care when vendor tools are unavailable.

2. **Floating-Point Precision Validation**: Verify and preserve the precision of measurement data, calibration values, and dosage information stored as floating-point numbers, flagging any potential precision loss during extraction or conversion.

3. **Multi-Frame Image Data Extraction**: Extract image sequences from proprietary formats while preserving frame timing, slice positioning, and associated metadata crucial for accurate medical interpretation and diagnosis.

4. **Patient Identifier Anonymization**: Automatically detect and anonymize patient identifiers during parsing to support research use cases and HIPAA compliance, with configurable anonymization rules and audit trails.

5. **Audit Trail Generation**: Create comprehensive logs of all data extraction operations including timestamps, data integrity checks, and transformation steps to meet regulatory requirements and support quality assurance processes.

## Technical Requirements
- **Testability**: All extraction and validation functions must be testable via pytest
- **Data Integrity**: Bit-perfect extraction with cryptographic hash verification
- **Compliance**: Support for HIPAA-compliant anonymization workflows
- **Performance**: Handle multi-gigabyte imaging studies efficiently
- **No UI Components**: Pure library implementation for integration flexibility

## Core Functionality
The parser must provide:
- Proprietary format structure analysis and decoding
- Medical metadata tag extraction and mapping
- Floating-point data validation and precision checking
- Multi-frame image sequence handling
- Patient data detection and anonymization engine
- Comprehensive audit logging system
- Data integrity verification with checksums
- Format conversion with zero data loss

## Testing Requirements
Comprehensive test coverage must include:
- **Tag Extraction**: Verify correct extraction of all medical metadata fields
- **Precision Validation**: Test floating-point accuracy preservation
- **Image Extraction**: Validate multi-frame sequence integrity
- **Anonymization**: Ensure complete removal of patient identifiers
- **Audit Trails**: Verify comprehensive logging of all operations
- **Data Integrity**: Confirm bit-perfect extraction via hash comparison
- **Compliance Tests**: Validate HIPAA-compliant anonymization
- **Performance**: Test handling of large imaging studies (1GB+)

All tests must be executable via:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```

## Success Criteria
The implementation is successful when:
- All pytest tests pass with 100% success rate
- A valid pytest_results.json file is generated showing all tests passing
- Medical tags are extracted accurately from all test formats
- Floating-point precision is maintained without data loss
- Multi-frame sequences preserve all timing and position metadata
- Anonymization removes 100% of patient identifiers in test cases
- Audit trails capture every data operation with full traceability
- Performance allows processing of large studies within clinical timeframes
- All extracted data passes integrity verification checks

## Environment Setup
To set up the development environment:
```
uv venv
source .venv/bin/activate
uv pip install -e .
```