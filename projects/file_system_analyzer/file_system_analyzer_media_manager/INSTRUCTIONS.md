# Media Production Storage Optimizer

A specialized file system analyzer for media production environments focused on optimizing storage for large video, audio, and image assets.

## Overview

The Media Production Storage Optimizer is a Python library designed to help media production managers efficiently organize, track, and optimize storage for large media assets. It provides media-specific metadata extraction, project-based analysis, render farm storage efficiency metrics, bandwidth analysis, and content-aware deduplication to maximize storage efficiency in media production environments.

## Persona Description

Carlos oversees digital assets for a media production company working with large video, audio, and image files. His goal is to optimize storage workflows and ensure efficient organization of media projects.

## Key Requirements

1. **Media-Specific Metadata Extraction and Cataloging**:
   Tools for extracting and organizing detailed technical metadata from media files (resolution, bitrate, codec, color profile). This is critical for Carlos because it enables intelligent organization and search capabilities across vast media libraries. The system must identify and catalog technical specifications, allowing for efficient retrieval based on production requirements.

2. **Project-Based Analysis**:
   Functionality to group files by production timeline and identify orphaned assets. This feature is essential because media production revolves around projects with defined lifecycles. Carlos needs to understand storage allocation per project, identify files that may have been separated from their projects, and track project-specific storage patterns over time.

3. **Render Farm Storage Efficiency Metrics**:
   Analytics that correlate output quality settings with storage requirements for rendering operations. This capability is crucial for optimizing the significant storage demands of render operations. Carlos needs to understand the storage impact of different quality settings to make informed decisions that balance quality requirements with storage constraints.

4. **Bandwidth Analysis**:
   Tools to ensure storage subsystems match media playback and editing requirements. This is vital for maintaining smooth workflow operations. Carlos needs to identify potential bottlenecks where storage performance may not meet the demands of high-resolution media editing, 4K+ playback, or multi-stream compositing.

5. **Content-Aware Deduplication Detection**:
   Algorithms specifically designed to identify slight variations in media files. This feature is essential because media workflows often create multiple similar versions of assets. Carlos needs to identify near-duplicate content even when files have small differences in encoding, resolution, or edit points, without compromising production assets.

## Technical Requirements

### Testability Requirements
- All components must have well-defined interfaces that can be tested independently
- Media analysis functions must be testable with sample media files of various formats
- Project grouping algorithms must be verifiable with known project structures
- Performance claims must be testable through automated benchmark tests
- Test coverage should exceed 90% for all core functionality

### Performance Expectations
- Media metadata extraction should process at least 100GB of media files per hour
- Project analysis should handle libraries with 100,000+ assets
- Storage efficiency calculations should complete in under 10 minutes for 1TB of render output
- Bandwidth analysis should provide results in under 5 minutes
- Content deduplication scanning should process at least 50GB per hour

### Integration Points
- Standard filesystem access interfaces for media storage
- Optional integration with media asset management systems
- Export capabilities for analysis results (JSON, CSV, HTML reports)
- Metadata integration with industry-standard tools (optional)
- APIs for integration with workflow automation systems

### Key Constraints
- All operations must be non-destructive and read-only
- Implementation must handle very large individual files (100GB+)
- System must operate efficiently with limited memory
- Processing must not interfere with ongoing production activities
- Solution must support industry-standard media formats

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The Media Production Storage Optimizer must provide the following core functionality:

1. **Media Asset Analysis Engine**:
   - Technical metadata extraction from video, audio, and image files
   - Format identification and compliance verification
   - Media quality assessment
   - Embedded metadata parsing (camera data, editing history)
   - Storage requirement calculation based on encoding parameters

2. **Project Organization Framework**:
   - Production timeline mapping
   - File relationship detection within projects
   - Orphaned asset identification
   - Project lifecycle stage determination
   - Storage allocation tracking by project

3. **Render Output Optimization**:
   - Quality-to-storage ratio analysis
   - Render setting optimization recommendations
   - Intermediate file impact assessment
   - Render cache efficiency measurement
   - Comparative analysis of compression options

4. **Storage Performance Analysis**:
   - I/O requirement modeling for different media types
   - Bandwidth bottleneck identification
   - Storage tier recommendations based on access patterns
   - Multi-stream performance prediction
   - Network storage performance assessment

5. **Media-Specific Deduplication**:
   - Perceptual hashing for visual similarity
   - Audio waveform fingerprinting
   - Frame-accurate variation detection
   - Resolution and transcode variant identification
   - Proxy and full-resolution file matching

## Testing Requirements

### Key Functionalities to Verify
- Accuracy of media metadata extraction across formats
- Precision of project grouping and orphan detection
- Reliability of render farm storage efficiency calculations
- Accuracy of bandwidth requirement predictions
- Effectiveness of content-aware deduplication

### Critical User Scenarios
- Analysis of post-production storage after project completion
- Identification of optimization opportunities for active projects
- Storage planning for upcoming production schedule
- Investigation of storage performance issues during editing
- Discovery of redundant assets across multiple projects

### Performance Benchmarks
- Complete analysis of 10TB media archive in under 8 hours
- Project analysis for 50 concurrent productions in under 10 minutes
- Render farm analysis processing 5TB of output data in under 30 minutes
- Bandwidth analysis calculations in under 3 minutes
- Deduplication analysis of 1TB media collection in under 2 hours

### Edge Cases and Error Conditions
- Handling of corrupted or partially accessible media files
- Graceful operation with non-standard media formats
- Recovery from interrupted scans of very large files
- Proper handling of media with missing or incorrect metadata
- Appropriate response to access permission restrictions

### Required Test Coverage Metrics
- Minimum 90% code coverage for all modules
- 100% coverage of media format detection code
- Comprehensive tests for all supported media formats
- Performance tests for all resource-intensive operations
- Integration tests for all supported third-party systems

IMPORTANT:
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

The Media Production Storage Optimizer implementation will be considered successful when:

1. Media metadata extraction accurately catalogs technical specifications across common formats
2. Project-based analysis correctly groups files and identifies orphaned assets
3. Render farm efficiency metrics provide actionable insights for storage optimization
4. Bandwidth analysis correctly identifies potential performance bottlenecks
5. Content-aware deduplication successfully identifies similar media variants
6. All performance benchmarks are met or exceeded
7. Code is well-structured, maintainable, and follows Python best practices
8. The system provides clear, actionable recommendations for storage optimization

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

NOTE: To set up your development environment, use `uv venv` to create a virtual environment. From within the project directory, activate the environment with `source .venv/bin/activate`. Install the project with `uv pip install -e .`.

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY for project completion. Use the following commands:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```