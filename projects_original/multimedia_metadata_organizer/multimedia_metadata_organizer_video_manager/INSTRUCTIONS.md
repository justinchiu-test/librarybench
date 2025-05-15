# Video Production Metadata Management System

## Overview
A specialized metadata organization system for video production managers who need to track and organize terabytes of interview footage, B-roll, and archival material while maintaining relationships between source footage and final edited sequences.

## Persona Description
Sophia oversees post-production for a documentary film studio managing terabytes of interview footage, B-roll, and archival material. She needs to organize raw footage and track the relationships between source material and final edited sequences.

## Key Requirements
1. **Interview transcription linking**: Develop a system that associates transcripts with video timestamps and automatically identifies speakers. This is critical for quickly locating specific content within hours of interview footage and enabling content-based searches across the entire video library.

2. **Production status tracking**: Create a workflow system showing which clips have been reviewed, selected, or included in edits. This is essential for managing the production pipeline and preventing duplicate work across team members.

3. **Licensing status monitoring**: Implement functionality to flag footage with pending or expired usage rights. This is crucial for legal compliance and avoiding costly rights violations, particularly when working with archival material from various sources.

4. **Edit decision list integration**: Build a system that tracks which source clips appear in final productions and maintains bidirectional relationships between raw footage and finished sequences. This provides critical context for archival purposes and facilitates future reuse of footage.

5. **Content sensitivity flagging**: Create a mechanism to identify and tag footage containing potential legal or ethical concerns. This helps production teams handle sensitive material appropriately and ensures proper review before inclusion in final productions.

## Technical Requirements

### Testability Requirements
- All metadata extraction and association functions must be independently testable
- Mock external transcription services for testing without real audio processing
- Use test fixtures with sample video files and metadata
- Support transaction rollback for testing modification operations

### Performance Expectations
- Process metadata for video files at a rate of at least 10 hours of footage per hour
- Handle relationships between thousands of source clips and dozens of final productions
- Search operations should complete in under 5 seconds even with complex criteria
- Support incremental updates to avoid reprocessing entire video files

### Integration Points
- Common video file formats (MP4, MOV, MXF, AVI) and their metadata
- Professional video editing formats (EDL, XML, AAF)
- Transcription services and subtitle formats
- Rights management databases and licensing systems
- Timecode standards and frame rate conversions

### Key Constraints
- No UI components - all functionality exposed through Python APIs
- Must handle various timecode formats and frame rates consistently
- Storage requirements must be optimized for large video collections
- Operations should be resumable in case of interruption

## Core Functionality

The system must provide a Python library that enables:

1. **Video Metadata Extraction and Organization**
   - Extract technical metadata from various video formats
   - Organize footage by production, shoot date, and content type
   - Support custom metadata fields specific to documentary production

2. **Transcription and Content Analysis**
   - Interface with transcription services to generate timestamped text
   - Identify speakers within interview footage
   - Enable content-based searching across transcribed material

3. **Production Workflow Management**
   - Track the status of clips through the production process
   - Maintain relationships between source footage and edited sequences
   - Record edit decisions and version history

4. **Rights and Licensing Management**
   - Track usage rights for all footage, especially archival material
   - Monitor license expirations and usage limitations
   - Generate reports on licensing status for productions

5. **Sensitive Content Handling**
   - Flag content with potential legal or ethical concerns
   - Track review status for sensitive material
   - Implement access controls for sensitive footage

## Testing Requirements

The implementation must include tests that verify:

1. **Metadata Extraction Accuracy**
   - Test extraction from various video formats
   - Verify correct handling of timecodes and frame rates
   - Test behavior with corrupt or incomplete metadata

2. **Transcription Integration**
   - Test association of transcripts with video timestamps
   - Verify speaker identification functionality
   - Test content-based searching across transcripts

3. **Production Tracking**
   - Test workflow status tracking through production stages
   - Verify relationship mapping between source and edited material
   - Test version tracking and history maintenance

4. **Rights Management**
   - Test license expiration alerting
   - Verify tracking of complex usage rights
   - Test reporting on licensing status

5. **Sensitivity Controls**
   - Test flagging of sensitive content
   - Verify review status tracking
   - Test access control mechanisms

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
2. The system can accurately extract and organize metadata from various video formats
3. Transcription linking works correctly with proper timestamp alignment
4. Production status tracking maintains accurate workflow information
5. Licensing status monitoring correctly identifies and alerts on expiring rights
6. Edit decision list integration maintains proper relationships between source and final footage
7. Content sensitivity flagging works correctly for various sensitive content types
8. All tests pass when run with pytest
9. A valid pytest_results.json file is generated showing all tests passing

**REMINDER: Generating and providing pytest_results.json is a CRITICAL requirement for project completion.**
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```