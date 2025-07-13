# Film Production Archive System

## Overview
A specialized archive management system designed for film production asset managers to handle raw footage, visual effects, and project files efficiently while maintaining quick preview capabilities and supporting industry-standard workflows.

## Persona Description
A post-production coordinator handling raw footage, visual effects, and project files. They need to archive large media files efficiently while maintaining quick preview capabilities.

## Key Requirements

1. **Proxy File Generation and Embedding for Quick Preview Without Extraction**
   - Essential for reviewing content without extracting massive raw files
   - Generate low-resolution proxy versions of video files during archiving
   - Embed proxies as separate streams within the archive
   - Support multiple proxy resolutions (thumbnail, preview, editorial)
   - Maintain frame-accurate correspondence between proxy and original

2. **Archive Streaming Support for Direct Playback of Media Files**
   - Critical for immediate access to archived content without full extraction
   - Implement seekable stream access for video and audio files
   - Support HTTP range requests for network streaming
   - Enable frame-accurate seeking within compressed archives
   - Provide real-time decompression for smooth playback

3. **Timecode-Based Partial Extraction for Specific Scenes or Frames**
   - Necessary for extracting only needed portions of large media files
   - Support SMPTE timecode for frame-accurate extraction
   - Enable in/out point selection for scene extraction
   - Extract with handles (extra frames) for editing flexibility
   - Maintain timecode continuity in extracted segments

4. **Archive Branching for Different Edit Versions Without Duplication**
   - Required for managing multiple cuts efficiently without storage waste
   - Implement copy-on-write for version branching
   - Track differences between versions at the file level
   - Support merging changes between branches
   - Maintain version history and relationships

5. **LTO Tape Archive Format Support for Long-Term Cold Storage**
   - Essential for industry-standard archival practices
   - Generate LTFS (Linear Tape File System) compatible archives
   - Support tape spanning for projects larger than single tapes
   - Include tape catalog generation for offline browsing
   - Implement verification passes for tape write confirmation

## Technical Requirements

### Testability Requirements
- All functions must be thoroughly testable via pytest
- Mock media file operations for efficient testing
- Simulate various video codecs and formats
- Test streaming without actual network operations

### Performance Expectations
- Handle individual media files up to 1TB in size
- Generate proxies at 10x real-time speed or faster
- Stream 4K content without buffering on gigabit networks
- Extract specific timecode ranges in near real-time
- Support archives containing 100TB+ of media

### Integration Points
- FFmpeg for media processing and proxy generation
- Industry standard codecs (ProRes, DNxHD, etc.)
- Editorial systems (Avid, Premiere, DaVinci Resolve)
- Asset management systems (MAM/DAM)
- LTO tape libraries and LTFS drivers

### Key Constraints
- Preserve all video metadata and color information
- Maintain frame accuracy throughout all operations
- Support professional video formats and codecs
- Handle multi-channel audio correctly

**IMPORTANT**: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The film production archive tool must provide:

1. **Proxy Management**
   - Multi-resolution proxy generation
   - Proxy embedding and extraction
   - Automatic proxy selection
   - Proxy quality optimization

2. **Streaming Architecture**
   - Seekable stream implementation
   - Buffering and caching strategies
   - Bandwidth adaptation
   - Multi-client streaming support

3. **Timecode Operations**
   - SMPTE timecode parsing
   - Frame-accurate extraction
   - Timecode range calculations
   - Handle management

4. **Version Control**
   - Branch creation and management
   - Difference tracking
   - Merge operations
   - Version history navigation

5. **Tape Archive Support**
   - LTFS format generation
   - Tape spanning logic
   - Catalog creation
   - Verification procedures

## Testing Requirements

### Key Functionalities to Verify
- Proxy generation maintains visual fidelity at specified resolutions
- Streaming provides smooth playback without full extraction
- Timecode extraction is frame-accurate across all formats
- Version branching doesn't duplicate unchanged files
- LTO format compliance for tape system compatibility

### Critical User Scenarios
- Generate and embed proxies for 100 hours of raw footage
- Stream specific scenes for remote review sessions
- Extract exact frames for VFX work based on EDL timecodes
- Create new version branch for director's cut without duplicating media
- Archive completed project to LTO tape for 10-year storage

### Performance Benchmarks
- Generate HD proxies at 500+ fps
- Stream 4K ProRes with less than 1 second startup time
- Extract 10-minute segment in under 30 seconds
- Create version branch for 10TB project in under 1 minute
- Write to LTO-8 tape at 300MB/s sustained rate

### Edge Cases and Error Conditions
- Handle corrupted media files gracefully
- Process variable frame rate content correctly
- Manage dropouts in streaming connections
- Deal with incomplete timecode information
- Recover from tape write errors

### Required Test Coverage
- Minimum 90% code coverage
- All media format handling must be tested
- Streaming edge cases must have full coverage
- Timecode calculations verified extensively
- Tape format compliance validation

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

1. **Proxy System**: Proxies enable instant preview of any archived content
2. **Streaming Quality**: Smooth playback without extraction for all supported formats
3. **Timecode Accuracy**: Frame-perfect extraction based on timecode ranges
4. **Version Efficiency**: Branching uses minimal additional storage
5. **Tape Compatibility**: Archives work seamlessly with LTO tape systems
6. **Performance**: Meets all specified performance benchmarks
7. **Reliability**: Handles large-scale productions without data loss
8. **Integration**: Compatible with industry-standard post-production tools

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
1. Python package with all film production archive functionality
2. Comprehensive pytest test suite
3. Generated pytest_results.json showing all tests passing
4. No UI components - only programmatic interfaces
5. Full compliance with film industry standards and workflows