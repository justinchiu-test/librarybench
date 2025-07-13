# PyBinParser - Embedded Firmware Analysis Tool

## Overview
A binary parser tailored for IoT engineers working with microcontroller firmware images. This tool provides memory mapping visualization, peripheral register analysis, and binary patching capabilities essential for embedded systems development and debugging.

## Persona Description
An IoT engineer who works with microcontroller firmware images and needs to extract and analyze binary configurations. They frequently deal with packed structures and hardware-specific data layouts.

## Key Requirements
1. **Memory Map Overlay Support**: Visualize firmware binary contents overlaid on the target microcontroller's memory map, showing code sections, data regions, and peripheral addresses. Critical for understanding how firmware utilizes available memory resources.

2. **Peripheral Register Mapping**: Define and map hardware peripheral registers to their binary offsets within the firmware, enabling analysis of hardware initialization sequences and configuration values stored in the binary.

3. **Endianness Auto-Detection**: Automatically detect endianness of binary data with support for mixed-endian structures common in embedded systems where different peripherals may use different byte orders.

4. **CRC/Checksum Calculator**: Calculate and verify various CRC algorithms and checksums with customizable polynomials, supporting common embedded standards (CRC-8, CRC-16, CRC-32) and vendor-specific implementations.

5. **Binary Patching with Checksum Recalculation**: Safely modify firmware binaries while automatically updating all affected checksums and CRCs to maintain firmware integrity and bootloader compatibility.

## Technical Requirements
- **Testability**: All parsing, analysis, and patching functions must be testable via pytest
- **Architecture Support**: Handle common MCU architectures (ARM, AVR, PIC, STM32)
- **Memory Efficiency**: Process firmware images with minimal RAM usage
- **Checksum Variety**: Support 20+ common CRC/checksum algorithms
- **No UI Components**: Library implementation with programmatic APIs only

## Core Functionality
The parser must provide:
- Memory map definition and overlay system
- Peripheral register database with common MCUs
- Endianness detection and conversion utilities
- Comprehensive CRC/checksum library
- Binary patching engine with integrity preservation
- Firmware structure analysis (vectors, bootloader, application)
- Configuration data extraction
- Symbol table parsing when available

## Testing Requirements
Comprehensive test coverage must include:
- **Memory Mapping**: Verify correct overlay of binary data on memory maps
- **Register Analysis**: Test peripheral register identification and value extraction
- **Endianness Detection**: Validate detection accuracy for known test patterns
- **CRC Algorithms**: Test all supported CRC variants with known test vectors
- **Patching Operations**: Ensure patches maintain firmware integrity
- **Architecture Support**: Test parsing for each supported MCU family
- **Edge Cases**: Handle incomplete images, overlapping sections, invalid checksums
- **Performance**: Verify efficient processing of large firmware images

All tests must be executable via:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```

## Success Criteria
The implementation is successful when:
- All pytest tests pass with 100% success rate
- A valid pytest_results.json file is generated showing all tests passing
- Memory map overlays correctly visualize all firmware sections
- Peripheral registers are accurately mapped to binary offsets
- Endianness detection achieves 100% accuracy on test cases
- All CRC algorithms produce correct results matching test vectors
- Binary patches maintain firmware integrity with proper checksum updates
- Performance allows real-time analysis during debugging sessions
- The tool correctly handles firmware from all supported architectures

## Environment Setup
To set up the development environment:
```
uv venv
source .venv/bin/activate
uv pip install -e .
```