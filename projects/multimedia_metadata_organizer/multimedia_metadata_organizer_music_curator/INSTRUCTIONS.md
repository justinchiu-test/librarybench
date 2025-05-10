# Music Collection Metadata Management System

## Overview
A specialized metadata organization system for music enthusiasts and collectors that standardizes inconsistent music metadata across various sources and formats, implementing comprehensive music-specific taxonomies and employing audio fingerprinting to create a unified listening collection with rich, accurate information.

## Persona Description
Aisha manages a vast personal music library spanning multiple formats from vinyl rips to streaming purchases. She needs to standardize inconsistent metadata across sources to create a unified listening experience.

## Key Requirements
1. **Audio fingerprinting**: A system to identify untitled or mislabeled tracks through acoustic signatures. This feature is critical because music collections often contain tracks with missing, incorrect, or inconsistent metadata, especially from legacy formats or user-created recordings, and acoustic fingerprinting provides a reliable way to identify such tracks without requiring manual research.

2. **Music-specific taxonomies**: Tools implementing genre, mood, and theme classification. This feature is essential because standard music metadata often lacks the nuanced categorization needed by serious collectors, and a comprehensive taxonomy system allows for precise organization beyond basic genre classifications, creating rich cross-connections between stylistically related music.

3. **Discography completion**: Functionality for detecting missing tracks or albums within artist collections. This capability is vital because music enthusiasts strive for complete collections, and an automated system that identifies gaps in discographies (missing tracks from albums, missing albums from artists) helps collectors systematically build comprehensive libraries without manual discography research.

4. **Performance role distinction**: A method for differentiating primary artists from featured guests and session musicians. This feature is crucial because accurate credit attribution is important for music collectors, and standard metadata often fails to distinguish between various contributor roles (lead artist, featured vocalist, producer, session musician), leading to inconsistent artist cataloging.

5. **Listening history integration**: Tools tracking personal ratings and play counts across platforms. This functionality is important because personal listening habits and preferences are valuable metadata for collectors, and integrating this information across fragmented listening platforms (streaming services, desktop players, mobile apps) creates a unified history that enhances music discovery and personal curation.

## Technical Requirements
- **Testability requirements**:
  - All audio fingerprinting functions must be testable with sample audio fragments
  - Taxonomy classification must be verifiable with known genre/mood reference datasets
  - Discography completion must be testable against known artist catalogs
  - Role distinction must correctly identify different types of contributors
  - Listening history integration must handle multiple platform data formats

- **Performance expectations**:
  - Process collections of up to 100,000 audio tracks
  - Audio fingerprinting must complete within 10 seconds per track
  - Metadata standardization should process at least 1,000 tracks per minute
  - Search operations should return results in under 2 seconds
  - Memory usage should scale efficiently with collection size

- **Integration points**:
  - Standard audio formats (MP3, FLAC, WAV, AAC, OGG)
  - Common music metadata formats (ID3, Vorbis comments, APE tags)
  - Music fingerprinting databases
  - External music databases (MusicBrainz, Discogs)
  - Streaming service history export formats

- **Key constraints**:
  - Implementation must be in Python with no external UI components
  - Must preserve original files while enhancing metadata
  - Must handle multiple audio formats with different metadata capabilities
  - Should be optimized for periodic batch processing
  - Must support incremental updates to large collections

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The system must provide comprehensive APIs for managing a music collection:

1. **Audio Identification Engine**: Analyze audio content to generate acoustic fingerprints. Match fingerprints against reference databases to identify unknown tracks. Provide confidence scores for matches and handle ambiguous cases.

2. **Taxonomy Management System**: Define, apply, and maintain hierarchical music classification schemes. Support multiple taxonomy dimensions (genre, mood, era, instrumentation). Enable custom classification rules and hybrid categorization.

3. **Collection Completeness Analyzer**: Track artist discographies and album compositions. Identify missing items within collections. Generate completeness reports and acquisition recommendations.

4. **Contributor Role Manager**: Parse and standardize artist and contributor information. Differentiate between primary artists, featured artists, producers, and session musicians. Normalize name variations and apply consistent crediting.

5. **Listening Metrics Integrator**: Import and normalize play count and rating data from multiple sources. Maintain unified listening history. Generate insights based on listening patterns and preferences.

## Testing Requirements
- **Key functionalities that must be verified**:
  - Accurate identification of tracks through audio fingerprinting
  - Correct application of multi-dimensional taxonomies
  - Reliable detection of missing items in collections
  - Accurate distinction between different contributor roles
  - Proper integration of listening data from multiple sources

- **Critical user scenarios that should be tested**:
  - Processing a batch of newly acquired music with inconsistent metadata
  - Identifying and correcting mislabeled tracks
  - Analyzing collection completeness for selected artists
  - Standardizing contributor credits across a collection
  - Importing and normalizing listening history from different platforms

- **Performance benchmarks that must be met**:
  - Fingerprint and identify 100 tracks in under 20 minutes
  - Apply taxonomy classification to 10,000 tracks in under 30 minutes
  - Analyze completeness for a collection of 50,000 tracks in under 5 minutes
  - Process contributor information for 5,000 tracks in under 10 minutes
  - Import listening history with 10,000 entries in under 3 minutes

- **Edge cases and error conditions that must be handled properly**:
  - Audio files with corrupted or missing metadata
  - Tracks with conflicting metadata from different sources
  - Unusual artist collaboration scenarios (supergroups, anonymous contributors)
  - Genre-crossing music that defies simple classification
  - Files with unsupported metadata formats
  - Tracks that cannot be fingerprinted reliably
  - Duplicate tracks with different metadata

- **Required test coverage metrics**:
  - 90% code coverage for audio fingerprinting functions
  - 95% coverage for taxonomy and classification systems
  - 90% coverage for collection completeness analysis
  - 95% coverage for contributor role management
  - 90% coverage for listening history integration

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
The implementation will be considered successful if it meets the following criteria:

1. Correctly identifies at least 85% of unmarked tracks through audio fingerprinting
2. Successfully applies music-specific taxonomies with consistent classification
3. Accurately identifies gaps in artist discographies and album tracklistings
4. Properly distinguishes between different types of music contributors
5. Successfully integrates listening history from multiple source formats
6. Passes all test cases with the required coverage metrics
7. Processes collections efficiently within the performance benchmarks
8. Provides a well-documented API suitable for integration with music management systems

## Project Setup
To set up the development environment:

1. Create a virtual environment and initialize the project using `uv`:
   ```
   uv init --lib
   ```

2. Install the necessary dependencies:
   ```
   uv sync
   ```

3. Run tests:
   ```
   uv run pytest
   ```

4. Run a specific test:
   ```
   uv run pytest path/to/test.py::test_function_name
   ```

5. Format the code:
   ```
   uv run ruff format
   ```

6. Lint the code:
   ```
   uv run ruff check .
   ```

7. Type check:
   ```
   uv run pyright
   ```

8. Run a Python script:
   ```
   uv run python script.py
   ```