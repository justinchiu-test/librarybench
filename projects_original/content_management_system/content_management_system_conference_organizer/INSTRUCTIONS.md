# Tech Conference Content Management System

## Overview
A specialized content management system designed for technology conference organizers to build excitement before events and provide resources during and after. This system enables organizers to showcase speakers and sessions while providing a content platform that transitions through pre-event, live event, and post-event phases with different information priorities.

## Persona Description
Sam organizes annual technology conferences and needs to build excitement before the event and provide resources during and after. His primary goal is to showcase speakers and sessions while providing a content platform that transitions through pre-event, live event, and post-event phases with different information priorities.

## Key Requirements

1. **Speaker profile system with talk proposal submission workflow**
   - Critical for Sam to manage speaker applications and curate a high-quality program
   - Must track the complete lifecycle from call for proposals through final presentation
   - Should include speaker information management, proposal evaluation, and selection tracking

2. **Dynamic agenda builder with personal schedule creation for attendees**
   - Essential for organizing complex event schedules with multiple tracks and sessions
   - Must handle time slots, room assignments, and session categorization
   - Should allow attendees to create personalized schedules and receive relevant updates

3. **Live session status updates with room change notifications**
   - Important for communicating real-time information during the event
   - Must track session status (on time, delayed, cancelled) and location changes
   - Should include push notification capabilities for urgent updates

4. **Content phase transitions triggered by event timeline**
   - Necessary for automatically adapting website content focus based on event phase
   - Must support scheduled transitions between pre-event, live event, and post-event modes
   - Should include different content prioritization and navigation for each phase

5. **Post-conference resource library with presentation archives**
   - Valuable for extending event value beyond the live dates
   - Must organize presentation slides, videos, and supplementary materials
   - Should include search capabilities and related content recommendations

## Technical Requirements

### Testability Requirements
- All components must have unit tests with at least 90% code coverage
- Integration tests must verify the event phase transition logic
- Performance tests must ensure system handles peak loads during live events
- Mock notification systems for testing status updates

### Performance Expectations
- Agenda updates must propagate to all users within 30 seconds
- Personal schedule operations must complete within 500ms
- Live status updates must be delivered within 10 seconds of changes
- Resource library must handle at least a 10x increase in traffic after presentations

### Integration Points
- Video streaming platforms for session recordings
- File storage systems for presentation materials
- Notification systems for status updates
- Calendar systems for schedule export

### Key Constraints
- System must function under intermittent connectivity conditions at the venue
- Content must be accessible on mobile devices with varying capabilities
- Phase transitions must not disrupt active user sessions
- Archive access must respect speaker's intellectual property settings

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system must provide a Python library with the following core components:

1. **Speaker Management**
   - Profile data model with professional information
   - Proposal submission and review workflow
   - Selection and confirmation tracking
   - Speaker-to-session mapping

2. **Session Scheduling**
   - Time slot and track management
   - Room assignment and capacity tracking
   - Session categorization and tagging
   - Schedule conflict detection

3. **Personal Agenda**
   - User preference storage and session selection
   - Schedule optimization suggestions
   - Calendar integration and export
   - Notification preferences and delivery

4. **Event Phase Management**
   - Phase definition and transition logic
   - Content prioritization rules by phase
   - Automated and manual phase triggers
   - Phase-specific features and functions

5. **Resource Library**
   - Presentation material organization
   - Media processing and optimization
   - Permission and access control
   - Search indexing and retrieval

## Testing Requirements

### Key Functionalities to Verify
- Speaker management correctly tracks the entire proposal-to-presentation workflow
- Agenda system accurately manages complex schedules with multiple tracks
- Status updates are promptly processed and delivered to relevant attendees
- Phase transitions correctly adjust content and features at appropriate times
- Resource library properly organizes and provides access to presentation materials

### Critical User Scenarios
- Managing the complete speaker proposal and selection process
- Creating and updating a complex multi-track conference schedule
- Handling live session changes and notifying affected attendees
- Transitioning the platform through all event phases
- Organizing and publishing post-event materials and recordings

### Performance Benchmarks
- System must support conferences with at least 200 sessions and 5,000 attendees
- Schedule builder must handle at least 100 concurrent schedule creations
- Notification system must deliver updates to all relevant attendees within 30 seconds
- Resource library must support at least 10,000 concurrent downloads

### Edge Cases and Error Conditions
- Handling speaker cancellations and emergency replacements
- Managing schedule conflicts and overlapping sessions
- Recovering from failed phase transitions
- Dealing with incomplete or delayed presentation materials
- Handling time zone differences for global virtual attendance

### Required Test Coverage Metrics
- Minimum 90% code coverage across all modules
- 100% coverage of schedule conflict detection logic
- 100% coverage of notification routing logic
- 100% coverage of phase transition rules

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

1. The speaker management system effectively handles the complete proposal workflow
2. The agenda builder correctly manages complex schedules with personal attendance tracking
3. The status update system promptly delivers relevant notifications to attendees
4. The phase transition system appropriately adjusts content based on event timeline
5. The resource library properly organizes and provides access to presentation materials

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Development Setup

To set up the development environment:

1. Use `uv venv` to create a virtual environment
2. From within the project directory, activate the environment with `source .venv/bin/activate`
3. Install the project with `uv pip install -e .`

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```