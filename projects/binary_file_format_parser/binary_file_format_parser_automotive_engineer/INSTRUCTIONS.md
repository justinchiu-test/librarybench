# PyBinParser - Automotive Diagnostics Decoder

## Overview
A binary parser designed for vehicle systems engineers analyzing proprietary diagnostic data and firmware from various manufacturers. This tool decodes controller-specific formats without vendor documentation, enabling independent diagnostics and troubleshooting of modern vehicle systems.

## Persona Description
A vehicle systems engineer who analyzes proprietary diagnostic data and firmware from various manufacturers. They need to decode controller-specific formats without vendor documentation.

## Key Requirements
1. **CAN Bus Data Structure Mapping**: Decode and map CAN (Controller Area Network) message structures to meaningful vehicle parameters, identifying signal boundaries, scaling factors, and unit conversions within packed binary frames.

2. **Diagnostic Trouble Code Extraction**: Parse diagnostic trouble codes (DTCs) from various ECU binary log formats, including manufacturer-specific codes, freeze frame data, and pending codes essential for vehicle troubleshooting.

3. **Sensor Calibration Data Interpretation**: Extract and interpret sensor calibration tables, curves, and correction factors stored in ECU memory, enabling accurate sensor reading interpretation and diagnostics.

4. **ECU Flash Memory Layout Analysis**: Analyze and map ECU firmware structure including bootloader, calibration areas, and application code sections, supporting firmware analysis and modification for diagnostics purposes.

5. **Vehicle-Specific Encryption Key Derivation**: Calculate security access keys using vehicle-specific algorithms and seed-key procedures, enabling legitimate diagnostic access while respecting manufacturer security protocols.

## Technical Requirements
- **Testability**: All parsing and decoding functions must be testable via pytest
- **Protocol Support**: Handle multiple CAN variants (CAN 2.0A/B, CAN-FD)
- **ECU Compatibility**: Support common automotive microcontroller architectures
- **Security**: Implement standard automotive security algorithms safely
- **No UI Components**: Library implementation for tool integration

## Core Functionality
The parser must provide:
- CAN message decoder with DBC-style signal definitions
- DTC parser supporting multiple diagnostic protocols
- Calibration data extractor with interpolation
- Flash memory structure analyzer
- Security algorithm library for common manufacturers
- Binary log file parser for various formats
- Checksum verification for data integrity
- Parameter identification database

## Testing Requirements
Comprehensive test coverage must include:
- **CAN Decoding**: Test signal extraction from packed CAN frames
- **DTC Parsing**: Verify code extraction from various log formats
- **Calibration Data**: Test interpretation of sensor tables and curves
- **Memory Layout**: Validate flash structure analysis algorithms
- **Security Keys**: Test key derivation with known seed-key pairs
- **Multi-Manufacturer**: Ensure compatibility across brands
- **Data Integrity**: Verify checksum calculations
- **Edge Cases**: Handle corrupted logs, unknown formats

All tests must be executable via:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```

## Success Criteria
The implementation is successful when:
- All pytest tests pass with 100% success rate
- A valid pytest_results.json file is generated showing all tests passing
- CAN messages are decoded accurately for all test cases
- DTCs are extracted correctly from various diagnostic formats
- Calibration data produces accurate sensor readings
- ECU memory layouts are correctly mapped
- Security keys are derived successfully for test vehicles
- Performance allows real-time diagnostic data processing
- The tool handles proprietary formats from major manufacturers

## Environment Setup
To set up the development environment:
```
uv venv
source .venv/bin/activate
uv pip install -e .
```