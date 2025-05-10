# FieldBackup - Incremental Backup System for Professional Photographers

## Overview
FieldBackup is a specialized incremental backup system designed for professional photographers who generate large volumes of high-resolution images during remote shoots. The system provides secure, efficient, and intelligent backup capabilities optimized for image files, with features like media-specific deduplication, tiered backup priorities, metadata preservation, tethered capture integration, and offline field backup with smart synchronization.

## Persona Description
Hiroshi is a wildlife photographer who generates thousands of high-resolution RAW images during field expeditions. He needs to securely back up irreplaceable photo shoots while in remote locations with limited connectivity and storage.

## Key Requirements

1. **Media-specific deduplication for image files**
   - Implement an advanced deduplication system specifically optimized for image file formats that can detect similar but not identical photos (such as burst shots or bracketed exposures)
   - This capability is critical for wildlife photographers who often capture multiple shots of the same subject with minor variations, allowing significant storage savings without losing unique imagery

2. **Prioritized backup tiers**
   - Develop a tiered backup system that allows photographers to separate critical selects from general captures, ensuring the most important images receive priority for backup resources (storage, bandwidth, verification)
   - This prioritization is essential when working with limited storage in the field, ensuring that the most valuable photos are secured first while managing large volumes of raw captures

3. **Metadata-preserving backup and restoration**
   - Create a backup system that maintains all EXIF, IPTC, and other metadata during backup and restoration, including edit history, ratings, keywords, and GPS coordinates
   - Preserving this rich metadata is vital for professional photography workflows, as this information is often as valuable as the images themselves for organization, client deliverables, and image licensing

4. **Tethered capture integration**
   - Implement integration with common tethered shooting setups to automatically back up images as they are captured, providing immediate protection for new photos
   - This real-time backup capability is crucial for safeguarding images as they're created, protecting against camera card failures and providing immediate validation of backup status during shoots

5. **Offline field backup with intelligent synchronization**
   - Design a system for secure field backups without internet connectivity, with intelligent synchronization that efficiently updates the main storage archive when returning from remote locations
   - This capability addresses the unique challenge of protecting irreplaceable images created in remote locations, then efficiently merging those backups with the primary archive upon return

## Technical Requirements

### Testability Requirements
- All components must have comprehensive unit tests with at least 85% code coverage
- Test suites must include image file fixtures representing various camera formats (RAW, CR2, NEF, ARW, DNG, etc.)
- Mocks must be developed to simulate tethered capture systems and camera interfaces
- Stress tests must verify performance with large batches of high-resolution files
- Synchronization tests must validate the integrity of field-to-main backup merges

### Performance Expectations
- Initial backup of 64GB memory card (approximately 1,000 RAW images) should complete in under 30 minutes
- Incremental backup during tethered shooting should complete within 5 seconds of image capture
- Field-to-main synchronization should process at least 10GB per hour on typical hardware
- Deduplication algorithms should identify at least 90% of similar images accurately
- Metadata extraction and preservation should add no more than 10% overhead to backup operations

### Integration Points
- Must support common tethered shooting systems and protocols (USB, network)
- Should interface with standard image metadata libraries (ExifTool compatible)
- Must work with various storage media (SD cards, external drives, network storage)
- Should provide a Python API for customization and extension

### Key Constraints
- The system must operate reliably on battery power with minimal consumption
- All operations must be atomic to prevent corruption during power loss
- Must maintain compatibility with standard image file formats and metadata standards
- Cannot modify original image files during backup or analysis
- Must function without internet connectivity for field operations

## Core Functionality

The FieldBackup system must implement these core components:

1. **Image-Aware Backup Engine**
   - A specialized backup system that understands image file formats and structures
   - Optimized handling for large RAW files from various camera manufacturers
   - Efficient storage mechanisms for high-resolution images

2. **Intelligent Deduplication System**
   - Advanced algorithms for detecting similar image content
   - Configurable similarity thresholds for different photography styles
   - Storage-efficient handling of burst sequences and bracketed exposures

3. **Metadata Management System**
   - Complete preservation of all image metadata during backup operations
   - Verification of metadata integrity during restoration
   - Indexing of metadata for search and organization

4. **Tiered Priority Framework**
   - Configurable priority levels for different types of images
   - Resource allocation based on image importance
   - Status tracking for prioritized backup operations

5. **Tethered Capture Integration**
   - Interfaces with tethered shooting systems
   - Real-time backup during image capture
   - Verification and notification of successful backup

6. **Field and Main Storage Synchronization**
   - Offline backup capabilities for field operation
   - Efficient synchronization algorithms for updating main archives
   - Conflict resolution for changes made in multiple locations

## Testing Requirements

### Key Functionalities Verification
- Verify correct handling and integrity of various image file formats
- Confirm accurate deduplication of similar but non-identical images
- Test complete preservation and restoration of all image metadata
- Validate tethered capture integration with various camera systems
- Verify field-to-main synchronization with different connectivity scenarios

### Critical User Scenarios
- Field expedition backup with limited storage and power
- Tethered studio shooting with real-time backup
- Archive synchronization after returning from remote locations
- Selective restoration based on metadata and image ratings
- Recovery from corrupted or damaged storage media

### Performance Benchmarks
- Backup speed must exceed 2GB per minute for typical image sets on standard hardware
- Deduplication must achieve at least 30% storage reduction for typical burst sequences
- Metadata indexing and search must return results in under 2 seconds for archives up to 100,000 images
- System resource usage must remain below 15% CPU and 500MB RAM during standard operations
- Field-to-main synchronization must properly handle at least 10,000 new images per session

### Edge Cases and Error Handling
- The system must recover gracefully from interrupted backup operations
- Proper handling of corrupted image files without affecting the backup process
- Correct operation with unusual metadata values and extended metadata
- Graceful handling of storage space limitations with clear user feedback
- Recovery from power loss during critical operations

### Required Test Coverage
- Minimum 85% code coverage for all components
- Tests must cover all supported image formats and metadata types
- Performance tests must include small shoots (100 images) and large expeditions (5,000+ images)
- All error handling paths must be explicitly tested
- Integration tests must verify compatibility with actual camera equipment

## Success Criteria

A successful implementation of FieldBackup will meet these criteria:

1. **Efficiency Metrics**
   - Storage space reduction of at least 30% compared to straight file copies for typical photography workflows
   - Processing time under 3 seconds per high-resolution RAW file on standard hardware
   - Battery consumption not exceeding 5% per hour on standard laptop during backup operations

2. **Reliability Targets**
   - Zero data loss in recovery testing scenarios
   - 100% metadata preservation verified across all supported file formats
   - Field-to-main synchronization with 100% accuracy across 1,000 test iterations

3. **Photographer Experience Goals**
   - Backup operations never interfere with active shooting sessions
   - Confidence that critical selects are prioritized and secured first
   - No noticeable performance impact during tethered shooting

4. **Functional Completeness**
   - All five key requirements fully implemented and passing acceptance tests
   - Support for all major camera manufacturers' RAW formats
   - Complete metadata preservation and usability in post-processing workflows

5. **Project Setup and Management**
   - Use `uv init --lib` to set up the project as a library with virtual environments
   - Manage dependencies with `uv sync`
   - Run the system with `uv run python your_script.py`
   - Execute tests with `uv run pytest`