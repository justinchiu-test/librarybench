# FieldVault - Incremental Backup System for Professional Photographers

## Overview
A specialized incremental backup system tailored for photographers who generate large volumes of high-resolution images during remote field work. The system enables secure backup of irreplaceable photo assets with limited connectivity, intelligent deduplication of similar images, and tiered backup strategies that balance storage constraints with the critical need to preserve one-of-a-kind shots.

## Persona Description
Hiroshi is a wildlife photographer who generates thousands of high-resolution RAW images during field expeditions. He needs to securely back up irreplaceable photo shoots while in remote locations with limited connectivity and storage.

## Key Requirements
1. **Media-specific Deduplication**: Implement advanced image-aware deduplication that identifies similar but not identical photos (burst shots, minor exposure variations) to dramatically reduce storage requirements. This capability enables Hiroshi to back up entire shoots without worrying about storage limitations, while still maintaining perfect copies of unique captures.

2. **Tiered Backup Prioritization**: Create a flexible prioritization system that allows separating critical selects from general captures with different backup policies, frequencies, and storage allocations. This feature ensures that Hiroshi's most valuable images receive the highest protection level while efficiently managing storage for the thousands of additional frames captured during a shoot.

3. **Metadata-preserving Backup**: Implement comprehensive metadata handling that ensures all EXIF data, camera settings, GPS coordinates, and post-processing adjustments are preserved during backup and restoration. This capability is critical for Hiroshi to maintain the professional value of his images, which depends on accurate technical and location data.

4. **Tethered Capture Integration**: Develop a system for immediate backup of images as they're captured when shooting tethered, with options for automatic culling and categorization. This ensures that critical shots are protected instantly during controlled shooting sessions before any potential equipment failures or card corruptions.

5. **Field Synchronization Logic**: Create intelligent offline field backup with efficient synchronization when returning to main storage systems. This feature allows Hiroshi to make optimal use of limited field storage while ensuring all unique assets are preserved during expeditions, with smart reconciliation upon returning to his studio environment.

## Technical Requirements

### Testability Requirements
- All components must have isolated unit tests with dependency injection for external systems
- Image deduplication algorithms must be tested with standardized image sets
- Metadata preservation must be verified across various image formats and editing software
- Tethered capture integration must be testable with simulated camera connections
- Synchronization logic must be verified with various conflict scenarios and edge cases
- Backup prioritization must be testable with different storage constraint scenarios

### Performance Expectations
- The system must efficiently handle deduplication across libraries of 100,000+ images
- Image similarity analysis must process at least 5 high-resolution RAW files per second
- Metadata extraction and preservation must add less than 50ms overhead per image
- Tethered capture backup must complete within 2 seconds of image capture
- Field synchronization must process at least 1000 images per hour on portable hardware
- Storage efficiency must achieve at least 30% reduction compared to naive backup for typical photoshoots

### Integration Points
- Camera tethering protocols (PTP, proprietary SDKs)
- Image editing software catalogs (Adobe Lightroom, Capture One, etc.)
- RAW processing libraries for various camera manufacturers
- EXIF/metadata manipulation systems
- External drive and portable storage management
- Image analysis and computer vision libraries

### Key Constraints
- The implementation must be portable across macOS and Windows (primary photographer platforms)
- All operations must be non-destructive with original files always preserved
- The system must operate reliably with intermittent or limited connectivity
- Battery impact must be minimized for field operation
- Image quality must never be compromised during any operation
- Storage formats must be accessible without specialized tools in emergency situations

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The core of this implementation centers on a Python library that provides:

1. **Incremental Backup Engine**: A core module handling image file change detection, efficient storage, and versioning with complete preservation of image quality and metadata.

2. **Image Analysis System**: Advanced algorithms for detecting similar images, analyzing visual content, and making intelligent decisions about deduplication while preserving unique captures.

3. **Metadata Management**: Comprehensive extraction, storage, and restoration of all image metadata including camera settings, location data, timestamps, and editing history.

4. **Capture Integration Framework**: Interfaces for connecting to tethered shooting systems, automating backup during image capture, and providing immediate verification of backup integrity.

5. **Prioritization Engine**: Logic for categorizing and prioritizing images based on flags, ratings, content analysis, and user input to apply appropriate backup policies.

6. **Synchronization Controller**: Sophisticated reconciliation system for managing the transition between field backup solutions and main storage systems with conflict resolution.

The system should be designed as a collection of Python modules with clear interfaces between components, allowing them to be used independently or as an integrated solution. All functionality should be accessible through a programmatic API that could be called by various tools (though implementing a UI is not part of this project).

## Testing Requirements

### Key Functionalities to Verify
- Image deduplication with precise control over similarity thresholds
- Complete metadata preservation across backup and restoration operations
- Proper tiered backup with appropriate policy application
- Tethered capture integration with reliable image acquisition
- Field-to-studio synchronization with correct conflict resolution
- Storage efficiency compared to direct file copying

### Critical User Scenarios
- Multi-day wildlife expedition with limited field storage requiring efficient backup
- Studio shooting with immediate tethered backup of critical client work
- Reconciliation of field backups with main storage after returning from expedition
- Recovery from corrupted memory card with minimal image loss
- Retrieval of specific images based on metadata criteria (location, settings, date)
- Balancing backup priorities when storage constraints are significant

### Performance Benchmarks
- Processing of a 1000-image shoot in under 10 minutes for initial backup
- Deduplication analysis achieving at least 25% storage reduction for burst shooting
- Metadata extraction and indexing at a rate of at least 10 images per second
- Tethered backup adding no more than 1.5 seconds delay to workflow
- Field synchronization completing within 2 hours for a 5000-image expedition
- Search operations returning results in under 3 seconds for complex metadata queries

### Edge Cases and Error Conditions
- Handling of corrupted image files with partial recovery capabilities
- Recovery from interrupted backups during power loss in field conditions
- Proper functioning with extremely large panorama or composite images
- Correct behavior when storage targets become full during backup
- Appropriate handling of RAW+JPEG pairs and various sidecar file formats
- Graceful operation with images containing non-standard or corrupted metadata

### Required Test Coverage Metrics
- Minimum 90% line coverage for all functional components
- 100% coverage of all public APIs
- All error handling paths must be explicitly tested
- Performance tests must verify all stated benchmarks
- Integration tests must verify all external system interfaces

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
The implementation will be considered successful when:

1. All five key requirements are fully implemented and pass their respective test cases.
2. The system demonstrates effective deduplication of similar images while preserving unique captures.
3. Metadata is perfectly preserved throughout backup and restoration operations.
4. Tiered backup properly applies different policies based on image priority.
5. Field synchronization correctly reconciles changes between temporary and permanent storage.
6. All performance benchmarks are met under the specified load conditions.
7. The implementation is well-structured with clean separation of concerns between components.
8. Code quality meets professional standards with appropriate documentation.

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Development Setup
1. Use `uv venv` to setup a virtual environment. From within the project directory, activate it with `source .venv/bin/activate`.
2. Install the project with `uv pip install -e .`
3. CRITICAL: Before submitting, run the tests with pytest-json-report:
   ```
   pip install pytest-json-report
   pytest --json-report --json-report-file=pytest_results.json
   ```
4. Verify that all tests pass and the pytest_results.json file has been generated.

REMINDER: Generating and providing the pytest_results.json file is a critical requirement for project completion.