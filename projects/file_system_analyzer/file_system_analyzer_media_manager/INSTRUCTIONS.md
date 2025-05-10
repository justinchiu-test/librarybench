# Media Asset Storage Analytics System

## Overview
A specialized file system analysis library for media production environments that optimizes storage workflows and organization of large video, audio, and image files. This solution extracts media-specific metadata, analyzes project organization, and provides insights for optimizing render farm storage and bandwidth utilization.

## Persona Description
Carlos oversees digital assets for a media production company working with large video, audio, and image files. His goal is to optimize storage workflows and ensure efficient organization of media projects.

## Key Requirements
1. **Media-specific metadata extraction and cataloging**
   - Implement comprehensive support for extracting technical metadata from various media formats (video, audio, images)
   - Catalog resolution, bitrate, codec, color profile, audio channels, and other media-specific attributes
   - Identify and extract embedded metadata (EXIF, XMP, ID3, etc.)
   - Create searchable indexes for media files based on their technical characteristics

2. **Project-based analysis and organization system**
   - Develop algorithms to identify and group files belonging to the same production project
   - Track file relationships across project timelines and workflows
   - Identify orphaned assets that are no longer associated with active projects
   - Generate recommendations for project organization based on production type and workflow

3. **Render farm storage efficiency analytics**
   - Create tools to correlate output quality settings with storage requirements
   - Analyze temporary files and intermediate renders for optimization opportunities
   - Track storage efficiency across different rendering techniques and engines
   - Develop metrics for optimal quality-to-storage ratios for various delivery formats

4. **Bandwidth analysis for storage subsystems**
   - Implement tools to analyze storage subsystem performance relative to media playback and editing requirements
   - Model bandwidth needs for various workflows (real-time editing, color grading, VFX, etc.)
   - Identify potential bottlenecks in storage architecture for media-intensive operations
   - Recommend optimal storage configurations for specific media workflows

5. **Content-aware deduplication detection**
   - Develop sophisticated algorithms for identifying near-duplicate media files with slight variations
   - Detect alternate versions, proxies, and derivatives of original media assets
   - Identify redundant storage of the same content in different formats or quality settings
   - Suggest consolidation strategies that preserve necessary variants while eliminating waste

## Technical Requirements
- **Accuracy**: Media metadata extraction must achieve 99%+ accuracy across supported formats
- **Performance**: Must efficiently process multi-terabyte media collections without excessive resource usage
- **Compatibility**: Must support current industry-standard media formats and metadata standards
- **Extensibility**: Architecture must allow for easy addition of new media formats as they emerge
- **Efficiency**: Analysis operations must be optimized to handle large media files with minimal memory footprint

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
1. **Media Metadata Analysis Engine**
   - Format-specific parsers for various media types
   - Technical parameter extraction and normalization
   - Embedded metadata recognition and extraction
   - Searchable catalog generation

2. **Project Organization Analyzer**
   - Project boundary detection algorithms
   - File relationship and dependency mapping
   - Temporal analysis of project evolution
   - Orphaned asset identification

3. **Render Analysis System**
   - Quality-to-storage ratio analytics
   - Intermediate file analysis
   - Render setting optimization engine
   - Delivery format efficiency comparison

4. **Storage Performance Analysis**
   - Bandwidth requirement modeling
   - Workflow-specific performance profiling
   - Bottleneck identification and analysis
   - Configuration recommendation engine

5. **Media Deduplication Framework**
   - Perceptual hashing for near-duplicate detection
   - Derivative and proxy identification
   - Format redundancy analysis
   - Consolidation planning tools

## Testing Requirements
- **Metadata Extraction Testing**
  - Test with diverse collection of media files (various formats, codecs, etc.)
  - Validate accuracy of extracted technical parameters against known values
  - Verify handling of corrupt or non-standard metadata
  - Benchmark performance with large media collections

- **Project Analysis Testing**
  - Test project boundary detection with various folder organizations
  - Validate relationship mapping with known project dependencies
  - Verify orphaned asset detection with simulated production scenarios
  - Test with large and complex project structures

- **Render Efficiency Testing**
  - Test quality-to-storage analysis with various render settings
  - Validate optimization recommendations against industry practices
  - Verify storage predictions with actual render outputs
  - Test with diverse rendering scenarios and output formats

- **Bandwidth Analysis Testing**
  - Test accuracy of bandwidth requirement predictions
  - Validate bottleneck identification with simulated storage configurations
  - Verify recommendations against established performance benchmarks
  - Test with various workflow profiles and media types

- **Deduplication Testing**
  - Test near-duplicate detection with controlled variations
  - Validate accuracy metrics (precision, recall) for similarity detection
  - Verify performance with large media libraries
  - Test consolidation planning with complex interdependencies

## Success Criteria
1. Successfully extract and catalog metadata from at least 20 different media formats with 99% accuracy
2. Correctly identify project relationships and dependencies with at least 95% accuracy
3. Achieve storage savings of at least 30% through render optimization recommendations
4. Accurately predict bandwidth requirements for various media workflows within 10% margin of error
5. Identify at least 90% of near-duplicate media with less than 5% false positives
6. Process and analyze media collections up to 50TB with acceptable performance

To set up your development environment:
```bash
# Create and activate a virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv sync
```