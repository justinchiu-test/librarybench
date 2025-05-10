# Conference Event Site Generator

A specialized static site generator for efficiently creating and managing event websites with dynamic schedules, speaker information, and venue details.

## Overview

This project is a Python library for generating comprehensive conference and event websites from structured data sources. It focuses on schedule management, speaker profiles, venue information, and event logistics specifically designed for technical conferences and professional events.

## Persona Description

Priya organizes tech conferences and needs to create event websites with schedules, speaker information, venue details, and registration information that can be quickly updated as event details evolve.

## Key Requirements

1. **Schedule Builder System**: Implement a comprehensive system for generating conference timetables from structured session data. This feature is crucial for Priya as it allows her to organize complex multi-track conference schedules, handle last-minute changes, and present the schedule in various formats (daily view, track view, personal agenda) without manual HTML editing for each update.

2. **Speaker Profile Management**: Create a system for maintaining and displaying speaker information with biographies, photos, and presentation materials. As speakers are the main draw for tech conferences, this feature enables Priya to showcase speaker expertise, link to their sessions, and provide comprehensive information that helps attendees decide which talks to attend.

3. **Multi-Track Session Visualization**: Develop a framework for displaying parallel sessions across different rooms or virtual spaces. This visualization is essential for attendees to understand the conference structure, identify potential scheduling conflicts, and plan their personal conference schedule effectively across multiple simultaneous tracks.

4. **Timezone Conversion System**: Implement functionality for displaying event times with countdown timers and automatic conversion between different time zones. With virtual and hybrid conferences becoming common, this system ensures that international attendees can easily understand when sessions occur in their local time, reducing confusion and missed sessions.

5. **Sponsor Showcase Framework**: Create a tiered system for displaying sponsor information with visibility levels based on sponsorship tiers. Since sponsors often fund conferences, this feature allows Priya to fulfill sponsorship commitments by providing appropriate visibility to different sponsors based on their contribution level.

## Technical Requirements

- **Testability Requirements**:
  - Schedule generation must be deterministic and handle conflict detection
  - Speaker profile generation must consistently format various fields
  - Track visualization must scale from single-track to 10+ parallel tracks
  - Time conversion must handle all global time zones correctly
  - Sponsor visibility must respect tier-based display requirements

- **Performance Expectations**:
  - Full site generation must complete in under 30 seconds for events with up to 100 sessions
  - Schedule data updates should trigger rebuilds in under 10 seconds
  - Page load time should remain under 2 seconds on standard connections
  - Timezone calculations should complete in under 50ms
  - Generated site should work efficiently on mobile devices

- **Integration Points**:
  - Calendar systems (iCal, Google Calendar) for schedule export
  - Time zone databases for accurate conversion
  - Social media platforms for speaker and event promotion
  - Registration systems for linking to ticket purchase
  - Feedback collection for session evaluations

- **Key Constraints**:
  - All schedule information must be updatable via structured data files
  - Speaker information must be privacy-conscious with opt-in fields
  - Time displays must explicitly show time zone information
  - Sponsor visibility must be precisely controllable
  - Generated site must function without JavaScript for basic information

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The core functionality must include:

1. **Conference Schedule Management**:
   - Process structured session data from YAML, JSON, or CSV
   - Handle multi-track, multi-day event scheduling
   - Detect and warn about scheduling conflicts
   - Generate different schedule views (by time, by track, by topic)
   - Create personal schedule builders with selections

2. **Speaker Management System**:
   - Process speaker profiles with standardized fields
   - Link speakers to their sessions and materials
   - Support speaker categorization (keynote, invited, regular)
   - Generate speaker directories and individual profiles
   - Create speaker galleries with filtering

3. **Session Visualization Framework**:
   - Generate timeline-based views of parallel sessions
   - Create track-based views showing room allocations
   - Support color coding and iconography for session types
   - Handle varying session durations and breaks
   - Provide room and location information for sessions

4. **Time Management System**:
   - Process session times in a reference time zone
   - Generate displays with user's local time conversion
   - Create countdown timers to upcoming sessions
   - Support calendar exports with correct time zone information
   - Handle daylight saving time transitions

5. **Sponsorship Management**:
   - Process sponsor information with tier classifications
   - Apply visibility rules based on sponsorship level
   - Generate sponsor showcases with appropriate prominence
   - Create sponsor directories and detail pages
   - Support special sponsor requirements (logo placement, etc.)

## Testing Requirements

- **Key Functionalities to Verify**:
  - Accurate generation of conflict-free schedules across multiple tracks
  - Correct display of speaker information with appropriate links
  - Proper visualization of parallel sessions with accurate timing
  - Successful time zone conversion across international boundaries
  - Correct sponsor display according to tier requirements

- **Critical User Scenarios**:
  - Conference organizer updates the schedule with last-minute changes
  - Attendee views the schedule in their local time zone
  - Speaker updates their profile information and materials
  - Organizer adds a new sponsor with specific visibility requirements
  - Attendee exports selected sessions to their personal calendar

- **Performance Benchmarks**:
  - Schedule generation time for different conference sizes (20, 50, 100 sessions)
  - Rebuild time after data changes to schedule or speakers
  - Time zone conversion accuracy and performance
  - Page load time for schedule pages with multiple tracks
  - Export time for different calendar formats

- **Edge Cases and Error Conditions**:
  - Handling of overlapping sessions or double-booked speakers
  - Management of very long conference days or 24-hour events
  - Processing of speakers with incomplete profile information
  - Conversion between unusual or deprecated time zones
  - Recovery from malformed schedule or speaker data

- **Required Test Coverage**:
  - 95% code coverage for schedule generation
  - 90% coverage for speaker profile management
  - 90% coverage for multi-track visualization
  - 95% coverage for time zone conversion
  - 90% coverage for sponsor management

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

The implementation will be considered successful when:

1. Conference schedules are correctly generated from structured data without conflicts
2. Speaker profiles are consistently formatted with all relevant information
3. Parallel sessions are clearly visualized across multiple tracks and rooms
4. Time zone conversion works correctly for international attendees
5. Sponsors are displayed according to their tier-based visibility requirements
6. Updates to conference data are reflected quickly in the generated site
7. All tests pass with at least 90% code coverage
8. The system can be used for conferences of varying sizes and complexities

To set up your development environment:
```
uv venv
source .venv/bin/activate
```