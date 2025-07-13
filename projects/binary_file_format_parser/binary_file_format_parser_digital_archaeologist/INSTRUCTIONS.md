# PyBinParser - Legacy Format Recovery System

## Overview
A binary parser designed for data preservation specialists who recover information from obsolete file formats and legacy systems. This tool reconstructs data from defunct software formats, enabling migration to modern systems while preserving historical digital artifacts.

## Persona Description
A data preservation specialist who recovers information from obsolete file formats and legacy systems. They work with formats from defunct software and need to reconstruct data without original applications.

## Key Requirements
1. **Character Encoding Detection**: Automatically identify and decode legacy text encodings (EBCDIC, various code pages, pre-Unicode systems) found in old binary formats, essential for recovering text data from systems predating modern standards.

2. **File Format Fingerprinting**: Match unknown binary files against a comprehensive database of historical format signatures, headers, and structural patterns to identify obsolete formats from defunct software packages.

3. **Partial File Recovery**: Extract usable data from corrupted or incomplete files commonly found on degraded media, using heuristics to reconstruct missing structural elements and recover maximum information.

4. **Schema Reconstruction**: Analyze binary structure through pattern recognition and statistical analysis to reverse-engineer undocumented format specifications, creating parseable schemas for previously unknown formats.

5. **Migration Path Generation**: Automatically generate conversion workflows to transform legacy data into modern, sustainable formats while maintaining data fidelity and documenting any necessary compromises.

## Technical Requirements
- **Testability**: All recovery and analysis functions must be testable via pytest
- **Encoding Support**: Handle 50+ legacy character encodings
- **Format Database**: Extensible signature database for format identification
- **Corruption Tolerance**: Graceful handling of damaged data
- **No UI Components**: Command-line and API access only

## Core Functionality
The parser must provide:
- Multi-encoding text detection and conversion
- Format signature matching against historical database
- Corruption-tolerant parsing algorithms
- Statistical structure analysis for schema inference
- Migration workflow generator
- Data validation and integrity reporting
- Metadata preservation during conversion
- Batch processing for archive collections

## Testing Requirements
Comprehensive test coverage must include:
- **Encoding Detection**: Test recognition of various legacy encodings
- **Format Identification**: Verify fingerprinting accuracy with known formats
- **Partial Recovery**: Test data extraction from intentionally corrupted files
- **Schema Reconstruction**: Validate structure inference algorithms
- **Migration Paths**: Test conversion accuracy for supported workflows
- **Edge Cases**: Handle truncated files, mixed encodings, nested formats
- **Performance**: Verify efficient processing of large archives
- **Accuracy Metrics**: Measure recovery success rates

All tests must be executable via:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```

## Success Criteria
The implementation is successful when:
- All pytest tests pass with 100% success rate
- A valid pytest_results.json file is generated showing all tests passing
- Character encoding detection achieves 95%+ accuracy on test corpus
- Format fingerprinting correctly identifies 90%+ of test formats
- Partial recovery extracts meaningful data from 80%+ of corrupted samples
- Schema reconstruction produces valid parsers for test formats
- Migration paths successfully convert data with full fidelity verification
- Performance allows processing of large archives in reasonable time
- The tool handles gracefully all categories of legacy format challenges

## Environment Setup
To set up the development environment:
```
uv venv
source .venv/bin/activate
uv pip install -e .
```