# Tech Conference CMS

A specialized content management system designed for technology conference organizers to manage event content through pre-event, live, and post-event phases.

## Overview

Tech Conference CMS is a comprehensive content management library tailored for technology conference organizers. It enables organizers to showcase speakers and sessions, manage the event agenda, provide real-time updates during the conference, and transition content through different event phases while maintaining a valuable resource archive.

## Persona Description

Sam organizes annual technology conferences and needs to build excitement before the event and provide resources during and after. His primary goal is to showcase speakers and sessions while providing a content platform that transitions through pre-event, live event, and post-event phases with different information priorities.

## Key Requirements

1. **Speaker Profile and Proposal System**: Develop a comprehensive speaker management system with profile creation and talk proposal submission workflow. This is critical for Sam as it streamlines speaker recruitment, simplifies the selection process, enables efficient communication with presenters, and creates compelling promotional content to attract attendees based on speaker expertise.

2. **Dynamic Agenda Builder**: Create a flexible schedule management system with personal attendee agenda creation capabilities. This feature is essential as it allows organizers to design complex multi-track conference schedules while enabling attendees to plan their personalized conference experience, maximizing the value of their attendance by focusing on relevant sessions.

3. **Live Session Status Updates**: Implement a real-time notification system for room changes, delays, and cancellations. This functionality is vital during the event to minimize disruption and attendee frustration, ensure maximum participation in sessions despite inevitable schedule changes, and maintain positive attendee experience throughout the conference.

4. **Content Phase Transitions**: Develop an automated system for transforming website content based on pre-event, live event, and post-event phases. This capability is crucial for maintaining relevant information priorities throughout the conference lifecycle, focusing on promotion before the event, practical information during, and resources after, all without requiring manual site redesigns.

5. **Post-Conference Resource Library**: Create a structured content archive for session recordings, presentations, and supplementary materials. This feature is important for extending the value of the conference beyond the event dates, providing ongoing resources to attendees, and creating valuable content that promotes future events while serving as a reference for the technology community.

## Technical Requirements

### Testability Requirements
- All components must have unit tests with at least 90% coverage
- Scheduling algorithms must be thoroughly tested
- Phase transition logic must be verifiable through test fixtures
- Notification systems must be validated with comprehensive test cases
- Archive organization must be tested for proper structure

### Performance Expectations
- Speaker profile searches must complete within 200ms
- Schedule generation should process within 500ms
- Live updates must propagate within 3 seconds
- Phase transitions should complete within 5 minutes
- Resource library searches should return results within 300ms

### Integration Points
- Support for common storage backends (local filesystem, SQLite, optional cloud storage)
- Video hosting platform integration
- Calendar export in standard formats (iCal, etc.)
- Mobile app API compatibility
- Email notification system

### Key Constraints
- All code must be pure Python with minimal dependencies
- No JavaScript dependencies or browser-specific code
- No direct coupling to web frameworks, though adaptors can be provided
- All content must be serializable for backup/restore
- Clear separation between content phases with audit trail

## Core Functionality

The library must provide the following core components:

1. **Speaker Management System**:
   - Speaker profile creation and editing
   - Talk proposal submission and review
   - Selection workflow and communication
   - Speaker categorization and filtering
   - Profile analytics and promotion tools

2. **Schedule Management**:
   - Track and room definition
   - Session time slot allocation
   - Schedule conflict detection
   - Personalized agenda creation
   - Schedule visualization generation

3. **Real-time Update System**:
   - Session status tracking
   - Change notification generation
   - Room reassignment handling
   - Cancellation management
   - Audience communication

4. **Phase Management**:
   - Phase definition and configuration
   - Content transformation rules
   - Automatic and manual transition triggers
   - Phase-specific templates and layouts
   - Preview capabilities for upcoming phases

5. **Resource Archive**:
   - Session recording management
   - Presentation file organization
   - Supplementary material cataloging
   - Resource tagging and categorization
   - Search optimization

6. **Attendee Experience**:
   - User profile and preference management
   - Session bookmarking and planning
   - Feedback and rating collection
   - Networking facilitation
   - Post-event engagement tools

## Testing Requirements

### Key Functionalities to Verify
- Creation and management of speaker profiles and proposals
- Accurate schedule generation and personal agenda building
- Timely propagation of live session updates
- Proper content transformation through event phases
- Organized archiving of session resources

### Critical User Scenarios
- Managing the speaker recruitment and selection process
- Creating and updating a multi-track conference schedule
- Handling room changes during the live event
- Transitioning from pre-event to live to post-event phases
- Organizing and publishing session recordings and materials

### Performance Benchmarks
- Speaker profile system with 100+ speakers
- Schedule builder with 5+ tracks and 50+ sessions
- Update propagation with 1000+ concurrent users
- Phase transition with complete site content
- Archive performance with 100+ recorded sessions

### Edge Cases and Error Conditions
- Handling speaker cancellations or replacements
- Managing schedule conflicts and overlapping sessions
- Recovery from interrupted phase transitions
- Behavior when live updates cannot be delivered
- Managing incomplete post-conference materials

### Required Test Coverage Metrics
- Minimum 90% line coverage for all core components
- 100% coverage of schedule conflict detection
- All error handling paths must be tested
- Performance tests for live update propagation
- Security tests for speaker and attendee data

## Success Criteria

The implementation will be considered successful when:

1. The complete speaker management cycle can be handled from recruitment through post-event
2. Complex multi-track schedules can be created and maintained with personalized attendee views
3. Live session updates are reliably delivered to relevant attendees
4. Content seamlessly transitions through pre-event, live, and post-event phases
5. Session resources are properly archived and made accessible after the event
6. All operations can be performed programmatically through a well-documented API
7. The entire system can be thoroughly tested using pytest with high coverage
8. Performance meets or exceeds the specified benchmarks

## Setup and Development

To set up your development environment:

1. Create a new Python library project:
   ```
   uv init --lib
   ```

2. Install necessary development dependencies:
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

5. Format code:
   ```
   uv run ruff format
   ```

6. Lint code:
   ```
   uv run ruff check .
   ```

7. Type check:
   ```
   uv run pyright
   ```

Remember to adhere to the code style guidelines in the project's CLAUDE.md file, including proper type hints, docstrings, and error handling.