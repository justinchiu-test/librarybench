# Professional Photographer's Metadata Management System

## Overview
A specialized metadata organization system for professional photographers who need to efficiently catalog, search, and deliver thousands of images monthly to different clients while maintaining a consistent organization system for growing archives.

## Persona Description
Isabella is a commercial photographer who shoots thousands of images monthly for different clients across various industries. She needs to efficiently catalog, search, and deliver photos to clients while maintaining a consistent organization system for her growing archives.

## Key Requirements
1. **Client-project hierarchy automation**: Create a system that automatically generates standardized folder structures based on shoot metadata. This is critical as it allows Isabella to maintain consistency across projects and quickly organize new shoots without manual reorganization.

2. **Deliverable preparation tools**: Implement functionality to generate client-ready files with appropriate metadata and optional watermarking. This feature is essential for efficiently preparing and delivering final assets to clients while ensuring proper branding and protection.

3. **Usage rights tracking**: Develop a mechanism to flag images with specific licensing restrictions or expiration dates. This is crucial for preventing usage rights violations and managing image licensing across multiple clients and projects.

4. **Equipment-specific metadata extraction**: Create tools to identify which gear produces the best results by analyzing metadata across shoots. This helps Isabella optimize her equipment choices for specific shooting scenarios and improve overall image quality.

5. **Client portal integration**: Generate secure sharing links with customized metadata visibility for client review. This streamlines the client approval process and allows selective sharing of relevant metadata while keeping sensitive information private.

## Technical Requirements

### Testability Requirements
- All functionality must be implemented as Python modules with clear APIs
- Each feature must have comprehensive unit tests using pytest
- Mock external services (like image processors) for consistent testing
- Use test fixtures to represent different image metadata scenarios

### Performance Expectations
- Process and organize at least 1,000 high-resolution images in under 5 minutes
- Metadata extraction should complete in under 1 second per image
- Search operations should return results in under 2 seconds for libraries with up to 100,000 images

### Integration Points
- Standard image file formats (JPEG, RAW, TIFF, PNG) and their metadata structures
- Metadata standards including EXIF, IPTC, and XMP
- SQLite database for metadata storage and indexing
- Filesystem operations for organization and hierarchy management

### Key Constraints
- No UI components allowed - all functionality exposed through Python APIs
- Image processing limited to metadata operations (no image manipulation except for watermarking)
- Must operate efficiently on standard hardware without specialized GPU requirements
- All operations must be transactional to prevent metadata corruption

## Core Functionality

The system must provide a Python library that enables:

1. **Metadata Extraction and Standardization**
   - Extract technical metadata from various image formats
   - Normalize metadata fields across different cameras and file types
   - Preserve original metadata while extending with custom fields

2. **Client-Project Organization**
   - Define client and project hierarchies programmatically
   - Generate folder structures based on metadata patterns
   - Support batch reorganization of existing image libraries

3. **Rights Management**
   - Track licensing terms, usage rights, and expiration dates
   - Set up alerts for approaching expiration dates
   - Filter searches by license status and restrictions

4. **Delivery Preparation**
   - Batch prepare images with appropriate metadata for delivery
   - Apply watermarks based on delivery settings
   - Generate secure sharing links with expiration dates

5. **Analytics and Reporting**
   - Track equipment usage and performance metrics
   - Generate reports on project completion and image delivery status
   - Analyze client history and project patterns

## Testing Requirements

The implementation must include tests that verify:

1. **Metadata Extraction Accuracy**
   - Test extraction from various camera models and file formats
   - Verify preservation of original metadata during processing
   - Test handling of corrupt or incomplete metadata

2. **Organization Functionality**
   - Verify correct folder structure creation based on metadata patterns
   - Test batch reorganization with various naming conventions
   - Verify handling of duplicates and conflicts

3. **Rights Management**
   - Test expiration date calculations and alerts
   - Verify license status tracking across multiple clients
   - Test filtering and search by license status

4. **Delivery Workflow**
   - Test watermark application and positioning
   - Verify secure link generation and expiration
   - Test batch delivery preparation with various client settings

5. **Performance Requirements**
   - Benchmark metadata extraction on large image sets
   - Test search performance with large metadata databases
   - Verify system performance under various load conditions

**IMPORTANT:**
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

## Setup Instructions
1. Set up a virtual environment using `uv venv`
2. Activate the environment: `source .venv/bin/activate`
3. Install the project: `uv pip install -e .`

## Success Criteria

The implementation will be considered successful if:

1. All features are implemented according to requirements
2. All tests pass when run with pytest
3. A valid pytest_results.json file is generated showing all tests passing
4. The system can process 1,000 images in under 5 minutes
5. The metadata extraction is accurate across multiple camera models and file types
6. Rights management correctly tracks and alerts on licensing terms
7. Client delivery workflow functions correctly with proper watermarking and metadata

**REMINDER: Generating and providing pytest_results.json is a CRITICAL requirement for project completion.**
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```