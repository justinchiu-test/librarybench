# Historical Archive Metadata Management System

## Overview
A specialized metadata system for historical archive curators who need to establish standardized cataloging practices for photograph collections spanning over a century. The system focuses on enhancing incomplete metadata using historically accurate information and making collections academically valuable.

## Persona Description
Dr. Chen manages a university's historical photograph collection spanning over a century of images with inconsistent or missing metadata. He needs to establish standardized cataloging practices and enhance existing metadata to make the collection academically valuable.

## Key Requirements
1. **Period-appropriate taxonomies**: Implement historically accurate categorization schemes that allow classification using terminology appropriate to the time period of each photograph. This is crucial for maintaining historical accuracy and enabling proper contextual searching of archives.

2. **Handwritten notation extraction**: Develop functionality to digitize and associate handwritten notes from physical photographs with their digital counterparts. This preserves crucial context that may not exist in other metadata and captures information from the original archivists or photographers.

3. **Historical geocoding**: Create a system to match outdated place names with their modern equivalents, allowing location-based searches using either historical or contemporary geographic references. This is essential for placing photographs in their proper geographic context despite changing boundaries and place names.

4. **Provenance tracking**: Build a comprehensive system for documenting acquisition sources and chain of ownership for each item in the collection. This is vital for establishing authenticity and fulfilling academic requirements for citation and verification.

5. **Academic citation generator**: Implement functionality to create properly formatted references for scholarly use following various academic citation styles. This facilitates the use of the archive in academic publications and ensures proper attribution.

## Technical Requirements

### Testability Requirements
- All metadata enhancement functions must be independently testable
- Mock external OCR services for handwritten notation extraction testing
- Create test fixtures with sample historical metadata of varying completeness
- Ensure all database operations are transactional to allow test isolation

### Performance Expectations
- Process metadata for at least 500 images per minute
- Handle collections with up to 1 million items efficiently
- Search operations should complete in under 3 seconds even with complex historical queries
- Batch operations should be resumable in case of interruption

### Integration Points
- Common image file formats (JPEG, TIFF, PNG) and their metadata structures
- Standard metadata formats (EXIF, IPTC, XMP, Dublin Core)
- OCR services for handwritten notation digitization
- Geocoding and historical mapping services
- Academic citation formats (Chicago, MLA, APA, etc.)

### Key Constraints
- No UI components - all functionality exposed through Python APIs
- Must preserve original metadata even when enhancing or correcting it
- Storage requirements must be optimized for large historical collections
- Must support both modern and historical date formats and calendars

## Core Functionality

The system must provide a Python library that enables:

1. **Historical Taxonomy Management**
   - Define and manage period-appropriate classification schemes
   - Map historical terms to modern equivalents for cross-period searching
   - Support hierarchical taxonomies with proper historical relationships

2. **Metadata Enhancement and Standardization**
   - Extract existing metadata from various file formats
   - Normalize inconsistent metadata using configurable rules
   - Enhance incomplete metadata through inference and external sources

3. **Handwritten Notation Processing**
   - Interface with OCR services to digitize handwritten notes
   - Associate transcribed text with the correct digital image
   - Handle uncertainty in transcription with confidence scoring

4. **Geographic and Temporal Context**
   - Resolve historical place names to both historical and modern geospatial data
   - Handle ambiguous or changing geographic boundaries
   - Normalize various date formats and calendar systems

5. **Provenance and Academic Integration**
   - Track acquisition sources and ownership changes
   - Generate citations in multiple academic formats
   - Create metadata exports suitable for academic databases

## Testing Requirements

The implementation must include tests that verify:

1. **Taxonomy Implementation**
   - Verify correct application of period-appropriate taxonomies
   - Test classification of items across different historical periods
   - Verify taxonomy mapping for cross-period searching

2. **Metadata Processing**
   - Test extraction and normalization from various file formats
   - Verify handling of incomplete or inconsistent metadata
   - Test inference of missing metadata

3. **Notation Extraction**
   - Test OCR integration with various handwriting samples
   - Verify correct association of transcribed text with images
   - Test confidence scoring for uncertain transcriptions

4. **Geographic Functions**
   - Test resolution of historical place names
   - Verify handling of changing geographic boundaries
   - Test searches using both historical and modern place names

5. **Provenance and Citation**
   - Verify tracking of complex acquisition histories
   - Test generation of citations in multiple academic formats
   - Test export compatibility with academic systems

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

1. All five key requirements are fully implemented
2. The system can accurately apply period-appropriate taxonomies
3. Handwritten notation extraction works with reasonable accuracy
4. Historical geocoding successfully maps between historical and modern place names
5. Provenance tracking maintains complete chains of ownership
6. Citation generation works correctly in multiple academic formats
7. All tests pass when run with pytest
8. A valid pytest_results.json file is generated showing all tests passing

**REMINDER: Generating and providing pytest_results.json is a CRITICAL requirement for project completion.**
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```