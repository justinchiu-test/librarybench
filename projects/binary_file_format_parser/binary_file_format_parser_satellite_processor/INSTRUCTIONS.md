# PyBinParser - Satellite Telemetry Processor

## Overview
A binary parser optimized for earth observation scientists processing raw satellite telemetry and sensor data. This tool extracts calibrated measurements from complex packed binary structures, enabling scientific analysis of satellite observations and environmental monitoring data.

## Persona Description
An earth observation scientist working with raw satellite telemetry and sensor data in various binary formats. They need to extract calibrated measurements from complex packed structures.

## Key Requirements
1. **Bit-Field Extraction**: Parse densely packed telemetry data where measurements span non-byte boundaries, extracting values from arbitrary bit positions and lengths. Essential for maximizing data transmission efficiency from space-constrained satellite systems.

2. **Scientific Unit Conversion**: Apply calibration curves and conversion formulas to transform raw sensor readings into scientifically meaningful units (temperature, radiance, pressure) using satellite-specific calibration parameters.

3. **Time Series Extraction**: Extract and organize sequential measurements from binary records into time-ordered datasets, handling various timestamp formats and maintaining temporal relationships for scientific analysis.

4. **Quality Flag Interpretation**: Decode and apply quality indicators and data flags embedded in telemetry streams to filter out corrupted or degraded measurements, ensuring only valid data enters scientific processing pipelines.

5. **Georeferencing Data Extraction**: Extract spacecraft position, attitude, and pointing information from navigation fields to georeference observations, enabling accurate mapping of measurements to Earth coordinates.

## Technical Requirements
- **Testability**: All extraction and calibration functions must be testable via pytest
- **Precision**: Maintain full numeric precision for scientific calculations
- **Performance**: Process multi-gigabyte telemetry files efficiently
- **Flexibility**: Support various satellite formats and instrument types
- **No UI Components**: Pure library implementation for pipeline integration

## Core Functionality
The parser must provide:
- Bit-level data extraction with configurable field definitions
- Calibration formula engine with curve fitting
- Time series dataset generation
- Quality flag system with filtering rules
- Georeferencing calculator with coordinate transforms
- Metadata preservation for data provenance
- Batch processing for operational pipelines
- Format validation against specifications

## Testing Requirements
Comprehensive test coverage must include:
- **Bit-Field Extraction**: Verify correct extraction from all bit alignments
- **Calibration Accuracy**: Test unit conversions against known values
- **Time Series Integrity**: Validate temporal ordering and completeness
- **Quality Filtering**: Ensure correct application of quality flags
- **Georeferencing**: Test coordinate calculations and transformations
- **Numeric Precision**: Verify no loss of precision in calculations
- **Performance**: Confirm processing speed for large datasets
- **Format Compliance**: Validate against satellite format specifications

All tests must be executable via:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```

## Success Criteria
The implementation is successful when:
- All pytest tests pass with 100% success rate
- A valid pytest_results.json file is generated showing all tests passing
- Bit-field extraction correctly handles all packing scenarios
- Calibrated values match reference calculations within tolerance
- Time series maintain proper temporal relationships
- Quality filtering removes all flagged bad data
- Georeferencing produces accurate Earth coordinates
- Processing performance meets operational requirements
- Full numeric precision is maintained throughout pipeline

## Environment Setup
To set up the development environment:
```
uv venv
source .venv/bin/activate
uv pip install -e .
```