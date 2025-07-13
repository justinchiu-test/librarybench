# PyBinParser - Audio Codec Analysis Tool

## Overview
A binary parser specialized for digital signal processing engineers studying proprietary audio codecs and container formats. This tool extracts audio streams, codec parameters, and psychoacoustic model data from undocumented formats, enabling codec research and format reverse engineering.

## Persona Description
A digital signal processing engineer studying proprietary audio codecs and container formats. They need to extract audio streams and metadata from undocumented formats.

## Key Requirements
1. **Audio Frame Boundary Detection**: Identify and extract individual audio frames within binary streams, handling variable-length frames, sync patterns, and frame headers essential for stream parsing and manipulation.

2. **Codec Parameter Extraction**: Extract encoding parameters from file headers and frame data including bit rates, compression settings, channel configurations, and codec-specific parameters needed for proper decoding.

3. **Sample Rate and Bit Depth Auto-Detection**: Automatically determine audio format characteristics by analyzing binary patterns, frame timing, and data structures when explicit metadata is unavailable or unreliable.

4. **Metadata Tag Parsing**: Extract and decode metadata tags from custom containers, including proprietary tag formats, multi-language support, and embedded artwork, preserving all available track information.

5. **Psychoacoustic Model Parameter Extraction**: Identify and extract perceptual coding parameters such as masking thresholds, frequency band allocations, and quantization tables that reveal how the codec models human hearing.

## Technical Requirements
- **Testability**: All detection and extraction functions must be testable via pytest
- **Format Support**: Handle both lossless and lossy codec types
- **Performance**: Real-time analysis of audio streams
- **Accuracy**: Bit-accurate extraction of audio data
- **No UI Components**: Pure library implementation

## Core Functionality
The parser must provide:
- Frame synchronization and boundary detection
- Codec parameter identification and extraction
- Automatic format characteristic detection
- Metadata parser supporting multiple tag formats
- Psychoacoustic parameter analyzer
- Container format structure analysis
- Stream validation and integrity checking
- Multi-channel audio data handling

## Testing Requirements
Comprehensive test coverage must include:
- **Frame Detection**: Test boundary identification in various formats
- **Parameter Extraction**: Verify correct codec parameter parsing
- **Format Detection**: Test auto-detection accuracy across formats
- **Metadata Parsing**: Validate tag extraction from containers
- **Model Parameters**: Test psychoacoustic data extraction
- **Stream Integrity**: Verify complete and accurate extraction
- **Performance**: Ensure real-time processing capabilities
- **Edge Cases**: Handle corrupted headers, partial files

All tests must be executable via:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```

## Success Criteria
The implementation is successful when:
- All pytest tests pass with 100% success rate
- A valid pytest_results.json file is generated showing all tests passing
- Frame boundaries are detected accurately in all test formats
- Codec parameters are extracted correctly and completely
- Format auto-detection achieves 95%+ accuracy
- All metadata tags are preserved during extraction
- Psychoacoustic parameters match codec specifications
- Real-time performance is maintained for stream analysis
- The tool handles proprietary formats without documentation

## Environment Setup
To set up the development environment:
```
uv venv
source .venv/bin/activate
uv pip install -e .
```