# Video Production Metadata Management System

## Overview
A specialized metadata organization system for documentary film production that tracks and organizes terabytes of footage including interviews, B-roll, and archival material, while maintaining relationships between source materials and edited sequences with comprehensive production status tracking.

## Persona Description
Sophia oversees post-production for a documentary film studio managing terabytes of interview footage, B-roll, and archival material. She needs to organize raw footage and track the relationships between source material and final edited sequences.

## Key Requirements
1. **Interview transcription linking**: A system that automatically connects transcriptions with speaker identification and timecode mapping. This feature is critical because it allows production teams to quickly search for specific content within hundreds of hours of interview footage by linking spoken words to precise timecode locations, dramatically reducing the time needed to locate usable quotes and sound bites.

2. **Production status tracking**: Tools showing which clips have been reviewed, selected, or included in edits. This feature is essential because it prevents duplicate work, ensures all material receives proper review, and provides producers with a clear overview of project progress across multiple editors and potentially hundreds of hours of footage.

3. **Licensing status monitoring**: A mechanism for flagging footage with pending or expired usage rights. This capability is vital because documentary productions often include archival material, stock footage, and third-party content with varying license terms, and failing to track these rights can result in costly legal issues or last-minute content removal before distribution.

4. **Edit decision list integration**: Functionality showing which source clips appear in final productions. This feature is crucial because it creates a transparent relationship between raw footage and edited sequences, enabling quick source verification, facilitating revisions, and providing an audit trail of how source material is used throughout the production process.

5. **Content sensitivity flagging**: Tools for identifying footage with potential legal or ethical concerns. This functionality is important because documentary material often contains sensitive content (e.g., traumatic stories, confidential information, or content requiring special permissions) that needs appropriate handling, redaction, or special clearance before inclusion in final productions.

## Technical Requirements
- **Testability requirements**:
  - All transcript-to-timecode linking functions must be independently testable
  - Production status tracking logic must handle complex state transitions
  - License management must be testable with mock calendars and expiration scenarios
  - Edit decision list parsing and integration must be verifiable with standard industry formats
  - Content flagging algorithms must be evaluated against test datasets

- **Performance expectations**:
  - Process at least 10 hours of video metadata per hour
  - Handle projects with up to 500 hours of source footage
  - Support searching across terabytes of video content in seconds
  - Optimize memory usage when dealing with large video files

- **Integration points**:
  - Standard video metadata formats (XMP, MXF)
  - Common transcript formats (SRT, VTT, JSON)
  - Industry-standard edit decision lists (EDL, XML, FCPXML)
  - Rights management and licensing systems
  - Video processing modules for frame extraction

- **Key constraints**:
  - Implementation must be in Python with no external UI components
  - Must handle very large files (individual video files up to 500GB)
  - Must support incremental updates as production progresses
  - Must maintain data integrity across project lifecycle

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The system must provide comprehensive APIs for managing a video production workflow:

1. **Transcript Processing Engine**: Parse, index, and link transcriptions to video timecodes. Identify speakers and map dialogue to specific footage segments. Support searching through transcript text with corresponding video location retrieval.

2. **Production Status Management**: Define, track, and update the status of footage through the production workflow. Maintain status histories and support custom production workflow stages. Generate reports on project completion status.

3. **Rights Management System**: Track licensing terms, usage rights, and permissions for all footage. Monitor expiration dates and usage limitations. Generate alerts for approaching license deadlines or usage violations.

4. **Edit Integration Module**: Parse and process edit decision lists from editing software. Map edited sequences back to source material. Maintain bidirectional relationships between source footage and final productions.

5. **Content Analysis Framework**: Identify and flag potentially sensitive content. Track required permissions, releases, and clearances. Support customizable sensitivity categories and handling protocols.

## Testing Requirements
- **Key functionalities that must be verified**:
  - Accurate linking of transcripts to video timecodes
  - Correct tracking of production status across workflow stages
  - Precise monitoring of licensing terms and expiration dates
  - Accurate mapping between source footage and edited sequences
  - Appropriate flagging of sensitive content

- **Critical user scenarios that should be tested**:
  - Importing and processing new footage with transcriptions
  - Tracking footage through the complete production workflow
  - Managing licensing for third-party content
  - Integrating edit decisions from editing software
  - Identifying and handling sensitive content

- **Performance benchmarks that must be met**:
  - Process metadata for 100GB of video files in under 30 minutes
  - Search across 500 hours of transcribed content in under 5 seconds
  - Generate reports on project status in under 10 seconds
  - Process standard edit decision lists in under 30 seconds

- **Edge cases and error conditions that must be handled properly**:
  - Corrupted or incomplete video files
  - Transcripts with timing errors or speaker misidentification
  - Complex licensing scenarios with multiple overlapping terms
  - Inconsistent or incorrectly formatted edit decision lists
  - Missing metadata in source material
  - Interrupted processing of large files

- **Required test coverage metrics**:
  - 95% code coverage for transcript processing functions
  - 90% coverage for production status management
  - 95% coverage for rights management and licensing tracking
  - 90% coverage for edit decision list integration
  - 90% coverage for content sensitivity analysis

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
The implementation will be considered successful if it meets the following criteria:

1. Demonstrates accurate linking between transcripts and video with 95% timing accuracy
2. Successfully tracks production status through complex workflows without state inconsistencies
3. Correctly manages licensing terms with timely expiration alerts
4. Accurately maps between source footage and edited sequences with bidirectional lookup
5. Appropriately identifies and flags sensitive content based on defined criteria
6. Maintains performance benchmarks with projects containing hundreds of hours of footage
7. Passes all test cases with the required coverage metrics
8. Provides a well-documented API suitable for integration with editing and production systems

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