# PyBinParser - Audio Codec Analysis Tool

PyBinParser is a specialized binary parser designed for digital signal processing engineers studying proprietary audio codecs and container formats. It provides comprehensive tools for extracting audio streams, codec parameters, and psychoacoustic model data from undocumented formats, enabling codec research and format reverse engineering.

## Features

### Core Functionality

- **Audio Frame Boundary Detection**: Identify and extract individual audio frames within binary streams
- **Codec Parameter Extraction**: Extract encoding parameters including bit rates, compression settings, and channel configurations
- **Sample Rate and Bit Depth Auto-Detection**: Automatically determine audio format characteristics through pattern analysis
- **Metadata Tag Parsing**: Extract and decode metadata tags from various formats (ID3v1/v2, Vorbis Comments, APE, FLAC)
- **Psychoacoustic Model Parameter Extraction**: Identify perceptual coding parameters like masking thresholds and frequency band allocations

### Supported Formats

- MP3 (MPEG Layer III)
- AAC (Advanced Audio Coding)
- FLAC (Free Lossless Audio Codec)
- Ogg Vorbis
- Opus
- WAV (PCM and other codecs)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip or uv package manager

### Install from source

```bash
# Clone the repository
git clone <repository-url>
cd pybinparser

# Create virtual environment (using uv)
uv venv
source .venv/bin/activate

# Install the package in development mode
uv pip install -e .
```

### Install dependencies only

```bash
uv pip install numpy pydantic
```

### Development dependencies

```bash
uv pip install -e ".[dev]"
```

## Usage Examples

### Basic Binary Parsing

```python
from pybinparser import BinaryParser, AudioFormat

# Open and analyze an audio file
with BinaryParser("audio_file.mp3") as parser:
    # Read file header
    header = parser.read(4)
    
    # Find specific pattern
    sync_position = parser.find_pattern(b"\xFF\xFB")
    
    # Read integers with different endianness
    value_16_be = parser.read_uint16_be()
    value_32_le = parser.read_uint32_le()
```

### Format Detection and Frame Extraction

```python
from pybinparser import BinaryParser, FrameDetector

with BinaryParser("unknown_audio.bin") as parser:
    detector = FrameDetector(parser)
    
    # Auto-detect format
    format_type = detector.detect_format()
    print(f"Detected format: {format_type}")
    
    # Extract frames
    frames = detector.find_frames(max_frames=10)
    for i, frame in enumerate(frames):
        print(f"Frame {i}: offset={frame.offset}, size={frame.size}")
```

### Codec Parameter Extraction

```python
from pybinparser import BinaryParser, CodecParameterExtractor, AudioFormat

with BinaryParser("audio_file.mp3") as parser:
    extractor = CodecParameterExtractor(parser)
    params = extractor.extract_parameters(AudioFormat.MP3)
    
    print(f"Bitrate: {params.bitrate} bps")
    print(f"Sample Rate: {params.sample_rate} Hz")
    print(f"Channels: {params.channels}")
    print(f"Compression Ratio: {params.compression_ratio:.2f}")
```

### Automatic Format Characteristics Detection

```python
from pybinparser import BinaryParser, FormatDetector

with BinaryParser("raw_audio.bin") as parser:
    detector = FormatDetector(parser)
    characteristics = detector.detect_format_characteristics()
    
    print(f"Detected Sample Rate: {characteristics['sample_rate']} Hz")
    print(f"Detected Bit Depth: {characteristics['bit_depth']} bits")
    print(f"Detected Channels: {characteristics['channels']}")
    print(f"Byte Order: {characteristics['byte_order']}")
```

### Metadata Tag Parsing

```python
from pybinparser import BinaryParser, MetadataParser, AudioFormat

with BinaryParser("tagged_audio.mp3") as parser:
    metadata_parser = MetadataParser(parser)
    tags = metadata_parser.parse_all_tags(AudioFormat.MP3)
    
    # Display all tags by type
    for tag_type, tag_list in tags.items():
        print(f"\n{tag_type} tags:")
        for tag in tag_list:
            print(f"  {tag.key}: {tag.value}")
    
    # Get embedded artwork
    artwork = metadata_parser.get_artwork()
    for art in artwork:
        print(f"Found {art.picture_type}: {art.mime_type}")
```

### Psychoacoustic Model Analysis

```python
from pybinparser import BinaryParser, FrameDetector, PsychoacousticAnalyzer, AudioFormat

with BinaryParser("audio_file.mp3") as parser:
    # First get frames
    detector = FrameDetector(parser)
    frames = detector.find_frames(max_frames=5)
    
    # Analyze psychoacoustic parameters
    analyzer = PsychoacousticAnalyzer(parser)
    psycho_params = analyzer.extract_parameters(AudioFormat.MP3, frames)
    
    print(f"Model Type: {psycho_params.model_type}")
    print(f"Window Type: {psycho_params.window_type}")
    print(f"Block Switching: {psycho_params.block_switching}")
    
    # Display frequency bands
    for band in psycho_params.frequency_bands[:5]:
        print(f"Band {band.start_freq}-{band.end_freq} Hz: "
              f"{band.bits_allocated} bits, "
              f"quantization step: {band.quantization_step}")
```

### Complete Analysis Pipeline

```python
from pybinparser import (
    BinaryParser, FrameDetector, CodecParameterExtractor,
    MetadataParser, PsychoacousticAnalyzer
)

def analyze_audio_file(filepath):
    with BinaryParser(filepath) as parser:
        # 1. Detect format
        frame_detector = FrameDetector(parser)
        format_type = frame_detector.detect_format()
        
        # 2. Extract codec parameters
        codec_extractor = CodecParameterExtractor(parser)
        codec_params = codec_extractor.extract_parameters(format_type)
        
        # 3. Find and validate frames
        frames = frame_detector.find_frames(max_frames=100)
        valid, errors = frame_detector.validate_frame_sequence(frames)
        
        # 4. Parse metadata
        metadata_parser = MetadataParser(parser)
        tags = metadata_parser.parse_all_tags(format_type)
        
        # 5. Extract psychoacoustic parameters
        psycho_analyzer = PsychoacousticAnalyzer(parser)
        psycho_params = psycho_analyzer.extract_parameters(format_type, frames[:10])
        
        return {
            "format": format_type,
            "codec_params": codec_params,
            "frame_count": len(frames),
            "valid_stream": valid,
            "metadata": tags,
            "psychoacoustic": psycho_params
        }

# Use the analyzer
results = analyze_audio_file("test_audio.mp3")
print(f"Format: {results['format']}")
print(f"Valid stream: {results['valid_stream']}")
```

## Running Tests

The project includes a comprehensive test suite covering all functionality.

### Install test dependencies

```bash
uv pip install pytest pytest-json-report
```

### Run all tests

```bash
pytest
```

### Run with JSON report (required for validation)

```bash
pytest --json-report --json-report-file=pytest_results.json
```

### Run specific test file

```bash
pytest tests/test_core.py
```

### Run with coverage

```bash
pytest --cov=pybinparser tests/
```

## API Reference

### Core Classes

- **BinaryParser**: Main binary file parser with low-level read operations
- **FrameDetector**: Detects format and extracts audio frames
- **CodecParameterExtractor**: Extracts codec-specific parameters
- **FormatDetector**: Auto-detects audio format characteristics
- **MetadataParser**: Parses various metadata tag formats
- **PsychoacousticAnalyzer**: Extracts psychoacoustic model parameters

### Data Models

- **AudioFormat**: Enum of supported audio formats
- **CodecType**: Enum of codec types (lossy, lossless, uncompressed)
- **AudioFrame**: Represents a single audio frame
- **CodecParameters**: Contains extracted codec parameters
- **MetadataTag**: Represents a metadata tag
- **PsychoacousticParameters**: Contains psychoacoustic model data

## Performance Considerations

- The parser is designed for real-time analysis of audio streams
- Large files are processed in chunks to maintain memory efficiency
- Pattern searching uses optimized algorithms with configurable chunk sizes
- Frame detection limits can be set to control processing time

## Contributing

Contributions are welcome! Please ensure:

1. All tests pass (`pytest`)
2. Code follows the project style (use `ruff format` and `ruff check`)
3. Type hints are included for all functions
4. New features include appropriate tests

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

This tool was developed for digital signal processing engineers and researchers working with proprietary audio formats. Special thanks to the open-source audio community for format documentation and insights.