# Film Production Archive System

A specialized archive management system designed for film production workflows, handling raw footage, visual effects, and project files with advanced features for proxy generation, streaming, timecode-based extraction, version control, and LTO tape archiving.

## Features

### 1. Proxy File Generation and Embedding
- Generate low-resolution proxy versions at multiple resolutions (thumbnail, preview, editorial)
- Embed proxies as separate streams within archives for quick preview
- Automatic proxy selection based on bandwidth and display constraints
- Frame-accurate correspondence between proxy and original files

### 2. Archive Streaming Support
- Direct playback of media files without full extraction
- HTTP range request support for network streaming
- Seekable stream access with frame-accurate seeking
- Adaptive buffering based on network conditions
- Multi-client concurrent streaming support

### 3. Timecode-Based Partial Extraction
- SMPTE timecode support for frame-accurate extraction
- Extract specific scenes using in/out points
- Handle support (extra frames) for editing flexibility
- EDL (Edit Decision List) parsing
- Batch extraction of multiple segments

### 4. Archive Branching and Version Control
- Copy-on-write branching without file duplication
- Track changes between versions at the file level
- Merge capabilities between branches
- Complete version history tracking
- Storage optimization through deduplication

### 5. LTO Tape Archive Support
- LTFS (Linear Tape File System) compatible format generation
- Automatic tape spanning for large projects
- Offline browseable catalog generation
- Verification passes for data integrity
- Support for LTO-8 and LTO-9 formats

## Installation

```bash
# Using uv (recommended)
uv venv
source .venv/bin/activate
uv pip install -e .

# Or using pip
pip install -e .
```

## Usage Examples

### Proxy Generation

```python
from film_archive.proxy.generator import ProxyGenerator
from film_archive.core.models import MediaFile, ProxyResolution, VideoCodec

# Initialize proxy generator
proxy_gen = ProxyGenerator()

# Create media file object
media_file = MediaFile(
    file_path=Path("/footage/scene_001.mov"),
    size=10 * 1024 * 1024 * 1024,  # 10GB
    codec=VideoCodec.PRORES_422,
    frame_rate=24.0,
    resolution=(3840, 2160),
    audio_channels=2
)

# Generate proxies
proxies = await proxy_gen.generate_proxies(
    media_file,
    [ProxyResolution.THUMBNAIL, ProxyResolution.PREVIEW]
)
```

### Archive Streaming

```python
from film_archive.streaming.streamer import ArchiveStreamer
from film_archive.core.models import StreamRequest

# Initialize streamer
streamer = ArchiveStreamer()

# Create stream request
request = StreamRequest(
    archive_path=Path("/archives/project.zip"),
    file_path="footage/scene_001.mov",
    start_byte=0,
    buffer_size=1024 * 1024  # 1MB chunks
)

# Stream file data
async for chunk in streamer.stream_file(request):
    # Process chunk
    pass
```

### Timecode-Based Extraction

```python
from film_archive.timecode.extractor import TimecodeExtractor
from film_archive.core.models import Timecode, TimecodeRange

# Initialize extractor
extractor = TimecodeExtractor()

# Define timecode range
tc_range = TimecodeRange(
    start=Timecode(hours=1, minutes=0, seconds=0, frames=0, frame_rate=24.0),
    end=Timecode(hours=1, minutes=0, seconds=30, frames=0, frame_rate=24.0),
    handles=24  # 1 second handles
)

# Extract segment
output_path = await extractor.extract_segment(
    archive_data, media_file, tc_range
)
```

### Version Branching

```python
from film_archive.versioning.branching import ArchiveBranchManager

# Initialize branch manager
branch_mgr = ArchiveBranchManager(repository_root=Path("/archive_repo"))

# Create new branch
branch = await branch_mgr.create_branch(
    archive_path=Path("/archives/master.zip"),
    branch_name="color-grade-v2",
    description="Updated color grading"
)

# Add modified file to branch
await branch_mgr.add_file_to_branch(
    branch.branch_id,
    Path("/graded/scene_001.mov"),
    "project/graded/scene_001.mov"
)
```

### LTO Tape Archiving

```python
from film_archive.tape.lto_manager import LTOTapeManager
from film_archive.core.models import TapeFormat

# Initialize tape manager
lto_mgr = LTOTapeManager()

# Prepare tape archive
tape_archive = await lto_mgr.prepare_tape_archive(
    tape_id="FILM2024001",
    format=TapeFormat.LTO8,
    files_to_archive=[file1, file2, file3]
)

# Write to tape
result = await lto_mgr.write_to_tape(
    tape_archive,
    [(file, f"archive/{file.name}") for file in files],
    verify=True
)
```

## Running Tests

The project includes a comprehensive test suite covering all functionality:

```bash
# Install test dependencies
pip install pytest pytest-json-report

# Run all tests
pytest

# Run with JSON report (required)
pytest --json-report --json-report-file=pytest_results.json

# Run specific test module
pytest tests/test_proxy_generator.py

# Run with coverage
pytest --cov=film_archive --cov-report=html
```

## Project Structure

```
film_archive/
├── core/           # Core models and data structures
├── proxy/          # Proxy generation and management
├── streaming/      # Archive streaming functionality
├── timecode/       # Timecode-based extraction
├── versioning/     # Branching and version control
└── tape/           # LTO tape format support

tests/
├── test_proxy_generator.py
├── test_streaming.py
├── test_timecode_extractor.py
├── test_branching.py
├── test_lto_manager.py
└── test_integration.py
```

## Performance Specifications

- Proxy generation: 500+ fps for HD proxies
- Streaming: 4K ProRes with <1 second startup
- Extraction: 10-minute segment in <30 seconds
- Branching: <1 minute for 10TB projects
- LTO write: 300MB/s sustained rate

## Requirements

- Python 3.8+
- Dependencies listed in requirements.txt
- For full functionality in production:
  - FFmpeg (for real media processing)
  - LTO tape drive and LTFS drivers
  - Sufficient storage for proxy cache

## License

MIT License - See LICENSE file for details