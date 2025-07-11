# Geospatial Archive Management System

## Overview
A specialized archive management system designed for satellite imagery analysts to efficiently compress, organize, and access massive geospatial datasets while maintaining quick retrieval capabilities for specific geographic regions and temporal sequences.

## Persona Description
A remote sensing specialist who processes massive geospatial datasets from satellites. They need to efficiently compress and organize terabytes of imagery while maintaining quick access to specific regions.

## Key Requirements

1. **Spatial Indexing Within Archives for Geographic Coordinate-Based Extraction**
   - Essential for rapidly accessing specific regions without extracting entire archives
   - Implement R-tree or similar spatial indexing structures within archive metadata
   - Support bounding box queries for lat/lon coordinate ranges
   - Enable extraction of tiles covering specific geographic areas
   - Maintain index coherency across archive updates

2. **Lossy Compression Options with Configurable Quality for Different Image Bands**
   - Critical for managing storage costs while preserving scientific data quality
   - Support band-specific compression settings (e.g., lossless for NIR, lossy for RGB)
   - Implement quality presets for different use cases (analysis vs. visualization)
   - Provide compression ratio vs. quality trade-off metrics
   - Support multiple compression algorithms optimized for raster data

3. **Tile-Based Archive Organization for Streaming Large Images**
   - Necessary for working with images too large to fit in memory
   - Organize imagery into manageable tiles (e.g., 256x256 or 512x512 pixels)
   - Support streaming decompression of individual tiles on demand
   - Implement tile pyramid structures for multi-resolution access
   - Enable partial archive updates for specific tiles

4. **Archive Metadata Embedding for Sensor Parameters and Acquisition Timestamps**
   - Required for proper scientific analysis and temporal ordering
   - Embed comprehensive metadata including sensor type, acquisition time, sun angle
   - Support standard geospatial metadata formats (GeoTIFF tags, ISO 19115)
   - Maintain metadata searchability without extracting image data
   - Provide metadata versioning for tracking processing history

5. **Delta Compression for Temporal Image Sequences**
   - Essential for efficiently storing time-series satellite data
   - Implement frame differencing for consecutive acquisitions
   - Support keyframe-based compression strategies
   - Enable temporal queries for specific date ranges
   - Optimize for common change detection workflows

## Technical Requirements

### Testability Requirements
- All functions must be thoroughly testable via pytest
- Mock large raster datasets for efficient testing
- Simulate various satellite data formats and projections
- Test spatial queries with known coordinate systems

### Performance Expectations
- Handle individual images up to 50GB in size
- Support archives containing petabyte-scale datasets
- Achieve sub-second tile extraction for any geographic query
- Maintain compression throughput of at least 1GB/s
- Support concurrent access from multiple analysis processes

### Integration Points
- GDAL/OGR library compatibility for geospatial operations
- Cloud-optimized GeoTIFF (COG) format support
- Open Geospatial Consortium (OGC) standard compliance
- Integration with common remote sensing platforms (ENVI, ERDAS)

### Key Constraints
- Preserve geospatial referencing information
- Maintain radiometric accuracy for scientific analysis
- Support coordinate system transformations
- Handle multi-spectral and hyperspectral data formats

**IMPORTANT**: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The geospatial archive tool must provide:

1. **Spatial Data Management**
   - Geographic indexing and querying
   - Tile-based data organization
   - Coordinate system handling
   - Multi-resolution pyramid generation

2. **Optimized Compression**
   - Band-specific compression strategies
   - Lossy/lossless algorithm selection
   - Quality metric calculation
   - Compression performance monitoring

3. **Temporal Data Handling**
   - Time-series optimization
   - Delta compression implementation
   - Temporal indexing and queries
   - Change detection support

4. **Metadata Management**
   - Comprehensive metadata extraction
   - Searchable metadata indices
   - Metadata standard compliance
   - Processing lineage tracking

5. **Streaming Access**
   - Tile-based data streaming
   - Partial archive extraction
   - Memory-efficient processing
   - Concurrent access support

## Testing Requirements

### Key Functionalities to Verify
- Spatial index accuracy for coordinate-based queries
- Compression quality metrics match specified parameters
- Tile extraction maintains geographic alignment
- Metadata preservation through compression cycles
- Delta compression achieves expected space savings

### Critical User Scenarios
- Extract all imagery covering a specific lat/lon bounding box
- Apply different compression settings to different spectral bands
- Stream tiles for real-time visualization of large images
- Query archives for images within specific date ranges
- Update individual tiles without recompressing entire archive

### Performance Benchmarks
- Index 1TB of imagery in under 1 hour
- Extract 1km x 1km region in under 1 second
- Achieve 10:1 compression ratio for typical satellite data
- Support 100 concurrent tile extraction requests
- Process temporal sequences at 100+ frames per second

### Edge Cases and Error Conditions
- Handle corrupt or incomplete satellite data files
- Process images with missing geographic information
- Manage archives exceeding filesystem limits
- Deal with non-standard coordinate systems
- Recover from interrupted compression operations

### Required Test Coverage
- Minimum 90% code coverage
- All spatial operations must have 100% coverage
- Compression algorithms thoroughly tested with reference data
- Edge cases for coordinate system transformations
- Stress tests for concurrent access scenarios

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

1. **Spatial Access**: Geographic queries return correct tiles in under 1 second
2. **Compression Efficiency**: Achieves specified compression ratios while maintaining quality
3. **Streaming Performance**: Large images can be accessed without loading entirely into memory
4. **Metadata Integrity**: All sensor parameters and timestamps are preserved and searchable
5. **Temporal Optimization**: Time-series data shows significant storage savings
6. **Scalability**: System handles petabyte-scale archives efficiently
7. **Concurrency**: Supports multiple simultaneous users without performance degradation
8. **Standards Compliance**: Output compatible with major GIS and remote sensing tools

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
1. Python package with all geospatial archive functionality
2. Comprehensive pytest test suite
3. Generated pytest_results.json showing all tests passing
4. No UI components - only programmatic interfaces
5. Full compliance with geospatial data standards