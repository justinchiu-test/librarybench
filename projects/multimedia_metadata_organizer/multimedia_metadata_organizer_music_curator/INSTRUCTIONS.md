# Music Collection Metadata Management System

## Overview
A specialized metadata organization system for music collection curators who need to standardize inconsistent metadata across diverse music formats and sources to create a unified listening experience.

## Persona Description
Aisha manages a vast personal music library spanning multiple formats from vinyl rips to streaming purchases. She needs to standardize inconsistent metadata across sources to create a unified listening experience.

## Key Requirements
1. **Audio fingerprinting**: Implement functionality to identify untitled or mislabeled tracks through acoustic signatures. This is essential for correctly identifying tracks when metadata is missing, corrupted, or inconsistent across different sources and formats.

2. **Music-specific taxonomies**: Create a system implementing genre, mood, and theme classification that works consistently across different musical styles and eras. This enables precise organization and discovery of music based on listening preferences rather than just artist or album.

3. **Discography completion**: Develop mechanisms to detect missing tracks or albums within artist collections and identify gaps in the music library. This helps maintain complete collections and highlights acquisition opportunities.

4. **Performance role distinction**: Build a metadata schema that differentiates primary artists from featured guests, session musicians, producers, and other contributors. This provides accurate credit attribution and enables more precise searching and filtering.

5. **Listening history integration**: Create functionality to track personal ratings, play counts, and listening patterns across different playback platforms. This helps prioritize music organization based on personal preferences and listening habits.

## Technical Requirements

### Testability Requirements
- All metadata extraction and normalization functions must be independently testable
- Mock audio fingerprinting services for testing without audio processing
- Use test fixtures with sample music metadata of varying completeness
- Support simulation of listening history and play count data

### Performance Expectations
- Process metadata for at least 1,000 tracks per minute
- Handle music collections with up to 500,000 tracks efficiently
- Search operations should complete in under 1 second
- Support incremental updates to avoid reprocessing entire collections

### Integration Points
- Common audio file formats (MP3, FLAC, AAC, WAV) and their metadata
- Music metadata standards (ID3, Vorbis Comments, APE Tags)
- Audio fingerprinting and acoustic analysis services
- MusicBrainz and other music database APIs
- Playback history from various media players and streaming services

### Key Constraints
- No UI components - all functionality exposed through Python APIs
- Must preserve original metadata while adding standardized enrichment
- Operations must be non-destructive to the original audio files
- System should work offline after initial setup of reference databases

## Core Functionality

The system must provide a Python library that enables:

1. **Music Metadata Extraction and Standardization**
   - Extract metadata from various audio file formats
   - Normalize inconsistent artist, album, and track information
   - Handle multiple metadata standards and merge information

2. **Audio Identification and Analysis**
   - Generate and compare audio fingerprints for track identification
   - Match unidentified tracks against reference databases
   - Extract acoustic features for similarity matching and mood classification

3. **Music-Specific Organization**
   - Implement hierarchical genre classification
   - Support mood and theme tagging
   - Enable custom taxonomies for specialized collections

4. **Artist and Contribution Management**
   - Track detailed contributor information and roles
   - Maintain artist relationships and collaborations
   - Support disambiguation of similar artist names

5. **Collection Analysis and Enhancement**
   - Identify incomplete albums and discographies
   - Track listening patterns and preferences
   - Generate recommendations for collection improvements

## Testing Requirements

The implementation must include tests that verify:

1. **Metadata Extraction and Normalization**
   - Test extraction from various audio formats
   - Verify normalization of inconsistent metadata
   - Test merging of metadata from multiple sources

2. **Audio Identification**
   - Test fingerprint generation and matching
   - Verify identification of tracks with missing metadata
   - Test handling of ambiguous or partial matches

3. **Taxonomy Implementation**
   - Test genre classification across different musical styles
   - Verify mood and theme tagging consistency
   - Test custom taxonomy creation and application

4. **Contributor Management**
   - Test parsing and normalization of contributor information
   - Verify role distinction and attribution
   - Test artist relationship tracking

5. **Collection Analysis**
   - Test detection of missing albums and tracks
   - Verify listening history integration
   - Test recommendation generation based on collection gaps

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
2. The system can accurately identify tracks through audio fingerprinting
3. Music-specific taxonomies effectively organize music by genre, mood, and theme
4. Discography completion correctly identifies gaps in artist collections
5. Performance role distinction accurately tracks and differentiates contributors
6. Listening history integration successfully captures and utilizes playback data
7. All tests pass when run with pytest
8. A valid pytest_results.json file is generated showing all tests passing

**REMINDER: Generating and providing pytest_results.json is a CRITICAL requirement for project completion.**
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```