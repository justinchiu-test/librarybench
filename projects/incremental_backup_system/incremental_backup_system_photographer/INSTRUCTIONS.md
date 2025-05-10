# FieldArchive - Expedition-Ready Backup System for Photographers

## Overview
FieldArchive is a specialized incremental backup system designed for professional photographers who need to securely preserve irreplaceable high-resolution images during remote expeditions. The system focuses on media-specific optimization, intelligent prioritization, and reliable operation in environments with limited connectivity and storage capacity.

## Persona Description
Hiroshi is a wildlife photographer who generates thousands of high-resolution RAW images during field expeditions. He needs to securely back up irreplaceable photo shoots while in remote locations with limited connectivity and storage.

## Key Requirements

1. **Media-Specific Deduplication for Image Files**
   - Implement specialized deduplication algorithms optimized for image file formats (RAW, DNG, JPEG, TIFF, etc.)
   - Develop intelligent detection of similar but not identical photos from burst shots or bracketed exposures
   - Create content-aware fingerprinting that recognizes edited versions of the same base image
   - Support for detecting duplicate images across different formats and resolutions
   - This feature is critical for Hiroshi as it significantly reduces storage requirements when backing up large sets of similar shots from wildlife photography sessions

2. **Prioritized Backup Tiers**
   - Design a multi-tier classification system to separate critical "selects" from general captures
   - Implement user-defined priority tags that can be assigned to individual files or groups
   - Create automated prioritization based on metadata (star ratings, color tags) from photo management software
   - Support different backup strategies and frequencies based on priority level
   - This tiering system ensures Hiroshi's most valuable shots are backed up first and most securely, critical when working with limited storage in the field

3. **Metadata-Preserving Backup and Restoration**
   - Ensure complete preservation of all EXIF metadata during backup and restoration
   - Maintain edit histories, adjustment layers, and non-destructive edits from editing software
   - Preserve color profiles, calibration data, and camera-specific metadata
   - Support sidecar files and application-specific metadata formats
   - This feature is essential as the detailed metadata contains irreplaceable information about shooting conditions and edit decisions

4. **Tethered Capture Integration**
   - Implement monitoring of tethered shooting directories for immediate backup
   - Create APIs for direct integration with tethering software
   - Support for backup verification during the capture process
   - Enable on-capture backup policies (format conversions, metadata tagging)
   - This integration ensures images are backed up immediately as they're captured, protecting against camera or computer failures during critical wildlife shooting opportunities

5. **Offline Field Backup with Smart Synchronization**
   - Develop offline backup strategies optimized for limited field storage
   - Implement intelligent synchronization when returning to main storage infrastructure
   - Create conflict resolution for any edits made to field copies before syncing
   - Support partial and prioritized transfers when bandwidth is limited
   - This capability is vital for Hiroshi who needs to work in remote wildlife locations with limited connectivity but must reliably merge field backups when returning to his main system

## Technical Requirements

### Testability Requirements
- All image processing algorithms must be testable with standard image test sets
- Backup operations must be independently testable without requiring actual camera hardware
- Synchronization logic must be verifiable with simulated network conditions
- Metadata handling must be tested across all supported image formats and editing software
- Test fixtures should include representative RAW files from major camera manufacturers

### Performance Expectations
- Backup initiation within 5 seconds of new image detection during tethered shooting
- Processing and fingerprinting of a 50MB RAW file in under 2 seconds
- Deduplication analysis should achieve 50% or better space savings for typical burst sequences
- System must operate within strict resource limitations for field use (CPU, memory, power)
- Synchronization should support resume capabilities for interrupted transfers

### Integration Points
- Standard tethering protocols (PTP/IP, USB Mass Storage) for major camera manufacturers
- Metadata reading/writing libraries for all common image formats
- Editing software sidecar file formats (.XMP, etc.)
- Storage media interfaces (SD cards, CF cards, portable SSDs)
- Field device power management APIs for battery optimization

### Key Constraints
- Must function reliably with intermittent or no connectivity
- Storage optimization is critical due to limited field media capacity
- System must be resilient to unexpected power loss common in field conditions
- Minimal CPU usage to preserve battery life on field equipment
- Operations must be atomic to prevent partial backups in case of interruption

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system must provide these core capabilities:

1. **Image-Aware Backup Engine**
   - Media-specific file format handling for all common photography formats
   - Specialized delta algorithms optimized for image file characteristics
   - Lossless compression and deduplication tailored to photographic content
   - Complete metadata extraction, indexing, and preservation

2. **Similarity Detection**
   - Perceptual hashing algorithms for identifying visually similar images
   - Burst sequence detection based on timestamps and content
   - Bracketing and HDR set identification
   - Edit version tracking across multiple passes

3. **Priority Management**
   - Classification engine for separating selects from general captures
   - Priority queue management for backup operations
   - Storage allocation strategies based on image importance
   - Configurable policies for different priority tiers

4. **Tethered Capture Handling**
   - Real-time monitoring of tethered shooting directories
   - Immediate backup triggers on file creation
   - Verification during the capture process
   - Parallel processing to keep up with rapid shooting

5. **Synchronization Engine**
   - Efficient differential sync between field and main storage
   - Conflict detection and resolution strategies
   - Bandwidth-aware transfer optimization
   - Recovery from interrupted transfers

## Testing Requirements

### Key Functionalities to Verify
- Accurate deduplication of similar but not identical images
- Proper application and enforcement of priority tiers
- Complete preservation of all metadata during backup and restoration
- Reliable operation of tethered capture backup
- Successful synchronization between field and main storage systems

### Critical User Scenarios
- Multi-day wildlife expedition with limited storage and power
- High-volume burst shooting of fast-moving wildlife subjects
- On-location sorting and rating of images between shooting sessions
- Return to main studio with field backups requiring synchronization
- Recovery from corrupted media or interrupted backups

### Performance Benchmarks
- Process and back up a 32GB memory card of RAW files in under 30 minutes
- Identify and properly handle burst sequences at a rate of 20 images per second
- Maintain complete backups while keeping at least 20% free space on field storage
- Battery impact: less than 10% additional power consumption on laptop during field backup
- Synchronization speed: transfer optimized backup sets at least 50% faster than raw files

### Edge Cases and Error Conditions
- Sudden power loss during backup or synchronization
- Corruption of image files during transfer
- Extremely large panorama or composite files
- Proprietary or unusual metadata formats
- Conflicting edits between field and main storage copies
- Limited storage scenarios requiring tough prioritization decisions

### Required Test Coverage Metrics
- 95% line coverage for core image processing and backup modules
- 100% coverage of error recovery paths
- Performance tests must simulate real-world photography workflows
- Comprehensive format compatibility tests across camera manufacturers
- Stress tests for high-volume shooting scenarios

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

The implementation will be considered successful when:

1. The system can identify and optimize storage for similar images from burst sequences, achieving at least 40% space savings compared to full backups
2. Critical "select" images are prioritized and verified with higher redundancy than general captures
3. All image metadata, including EXIF data and editing information, is completely preserved during backup and restoration
4. Images are backed up immediately and reliably when captured through tethered shooting
5. Field backups successfully synchronize with main storage when returning from expeditions, with proper conflict resolution
6. The system operates efficiently within the resource constraints of field equipment
7. All backed-up images can be perfectly restored with their complete metadata
8. The implementation passes all test suites with required coverage metrics
9. The system proves resilient in simulated field conditions with power and connectivity interruptions
10. Storage requirements are minimized while maintaining backup integrity and completeness

To get started with implementation:
1. Set up a Python virtual environment: `uv venv`
2. Activate the environment: `source .venv/bin/activate`
3. Install development dependencies
4. Implement the core modules following the requirements
5. Create comprehensive tests for all functionality