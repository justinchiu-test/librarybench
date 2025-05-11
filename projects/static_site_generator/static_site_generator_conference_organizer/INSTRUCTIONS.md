# Event and Conference Site Generator

A specialized static site generator designed for conference organizers to create and maintain event websites with dynamic schedules, speaker profiles, and venue information that can be quickly updated as event details evolve.

## Overview

This project implements a Python library for generating comprehensive event and conference websites that display schedules, speaker information, session details, and venue information. It focuses on the needs of event organizers who need to maintain up-to-date information as conference details evolve, while providing attendees with well-organized, accessible information.

## Persona Description

Priya organizes tech conferences and needs to create event websites with schedules, speaker information, venue details, and registration information that can be quickly updated as event details evolve.

## Key Requirements

1. **Schedule Builder**: Create a system for generating conference timetables from structured session data, with support for different views and formats.
   - Critical for Priya because conference schedules are complex and frequently change, requiring a streamlined way to update and display the latest information across the site.
   - Must handle multi-day events, concurrent sessions, and last-minute changes efficiently.

2. **Speaker Profile Management**: Implement a comprehensive system for managing speaker information, including biographies, photos, session information, and presentation materials.
   - Essential for Priya because speakers are central to the conference experience, and attendees need easy access to speaker information and materials.
   - Should connect speakers to their sessions and provide proper attribution and contact information.

3. **Multi-Track Session Visualization**: Develop tools to visually represent parallel conference tracks and concurrent sessions across different rooms and time slots.
   - Important for Priya because tech conferences typically have multiple simultaneous tracks, and attendees need clear visual cues to navigate between options.
   - Must provide clear, accessible representations of the conference structure.

4. **Time-Related Tools**: Implement countdown timers, time zone conversion, and scheduling tools for international virtual attendees.
   - Valuable for Priya because modern conferences often have global attendance, requiring clear time-based information that accommodates different time zones.
   - Should include features for personalized scheduling based on attendee time zones.

5. **Sponsor Showcase**: Create a system for featuring conference sponsors with tiered visibility based on sponsorship levels.
   - Critical for Priya because sponsor relationships are key to conference funding, and proper recognition with appropriate prominence is a contractual obligation.
   - Must support different sponsorship tiers with varying levels of visibility and features.

## Technical Requirements

### Testability Requirements
- All components must be individually testable with clear interfaces
- Support snapshot testing for generated schedules and visualizations
- Test dynamic content updates and schedule changes
- Validate time zone conversions for international events
- Support testing with realistic conference data sets

### Performance Expectations
- Schedule generation should process 100+ sessions in under 3 seconds
- Speaker profile pages should build at a rate of 10+ profiles per second
- Site updates for schedule changes should regenerate affected pages in under 5 seconds
- Time-based calculations should handle 1000+ time zone conversions per second
- Full site generation for a typical conference (100 speakers, 200 sessions) should complete in under 30 seconds

### Integration Points
- Calendar and scheduling standards (iCal, etc.)
- Time zone conversion libraries
- Image processing for speaker photos
- Structured data for events (Schema.org)
- Registration and ticketing service integration

### Key Constraints
- IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.
- Must generate completely static HTML that works without server-side processing
- Schedule changes must propagate consistently across all site sections
- Time-based information must be accurate across international time zones
- Output must be fully accessible for attendees with disabilities
- Site performance must be optimized for high traffic during event registration periods

## Core Functionality

The Event and Conference Site Generator should provide a comprehensive Python library with the following core capabilities:

1. **Schedule Management System**
   - Process session data from structured formats (CSV, JSON, etc.)
   - Generate various schedule views (daily, by track, by speaker, etc.)
   - Handle schedule changes and updates efficiently
   - Support for session categorization and filtering
   - Generate personalized schedules for attendees based on preferences
   - Create printable/downloadable schedule formats

2. **Speaker Management**
   - Process speaker profiles with biographical information
   - Handle speaker photos with proper formatting and optimization
   - Link speakers to their sessions and topics
   - Generate speaker directories and indices
   - Support for speaker materials and resources
   - Create speaker cards and featured speaker highlights

3. **Multi-Track Visualization**
   - Generate visual representations of concurrent sessions
   - Create timeline-based views of conference tracks
   - Implement room and location mapping
   - Support for color-coding and visual differentiation
   - Generate navigation between tracks and sessions
   - Create responsive layouts for different device sizes

4. **Time Tools and International Support**
   - Implement countdown timers to key conference events
   - Process time zone information for international attendees
   - Generate personalized schedules in local time zones
   - Create time conversion tools and references
   - Support for calendar integration and reminders
   - Handle daylight saving time transitions during events

5. **Sponsorship Management**
   - Process sponsor information and categorization
   - Implement tiered visibility based on sponsorship levels
   - Generate sponsor directories and showcases
   - Create sponsor-specific pages and recognition elements
   - Support for sponsor logos and materials
   - Implement sponsor analytics and reporting tools

## Testing Requirements

### Key Functionalities to Verify

1. **Schedule Generation and Management**
   - Test creation of schedules from various data sources
   - Verify proper session organization and categorization
   - Test schedule updates and change propagation
   - Confirm generation of different schedule views
   - Verify handling of schedule conflicts and special cases
   - Test filtering and personalization of schedules

2. **Speaker Profile System**
   - Test speaker profile generation with various data formats
   - Verify proper linking between speakers and sessions
   - Test handling of speaker photos and materials
   - Confirm generation of speaker directories and lists
   - Verify proper attribution and contact information
   - Test updates to speaker information

3. **Track Visualization**
   - Test generation of multi-track visualizations
   - Verify proper representation of concurrent sessions
   - Test responsiveness for different screen sizes
   - Confirm accessibility of track visualizations
   - Verify navigation between tracks and sessions
   - Test visual differentiation between tracks

4. **Time Management Tools**
   - Test time zone conversion for various global locations
   - Verify countdown timer accuracy and updates
   - Test generation of personalized time-based content
   - Confirm handling of daylight saving time transitions
   - Verify calendar integration formats
   - Test internationalization of time and date formats

5. **Sponsor Management**
   - Test sponsor categorization by tier
   - Verify proper visibility based on sponsorship level
   - Test generation of sponsor directories and pages
   - Confirm proper logo display and optimization
   - Verify sponsor links and attribution
   - Test sponsor analytics and reporting

### Critical User Scenarios

1. Creating a complete conference schedule and updating it as sessions change
2. Managing speaker profiles and connecting them to appropriate sessions
3. Visualizing multiple concurrent tracks for a complex conference
4. Providing time information for international attendees across time zones
5. Showcasing sponsors with appropriate visibility based on contribution level

### Performance Benchmarks

- Full conference site with 100+ speakers and 200+ sessions should build in under 30 seconds
- Schedule updates should propagate to all affected pages in under 5 seconds
- Speaker profile generation should process 50+ profiles in under 10 seconds
- Track visualization should handle 10+ concurrent tracks efficiently
- Memory usage should not exceed 500MB for typical conference sites

### Edge Cases and Error Conditions

- Test handling of last-minute schedule changes
- Verify behavior with cancelled or rescheduled sessions
- Test with speakers presenting multiple sessions
- Verify handling of sessions spanning midnight or day boundaries
- Test with unusual time zones and daylight saving transitions
- Verify behavior with incomplete sponsor or speaker information
- Test with extremely large conferences (1000+ sessions)

### Required Test Coverage Metrics

- Minimum 90% code coverage for core functionality
- 100% coverage for schedule generation and updates
- 100% coverage for time zone conversion logic
- Integration tests for the entire site generation pipeline
- Performance tests for both small and large conferences

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

The Event and Conference Site Generator will be considered successful if it:

1. Correctly generates and updates conference schedules from structured data
2. Properly manages speaker profiles with appropriate session connections
3. Creates clear visual representations of multi-track conference sessions
4. Successfully handles time zone conversions and time-based content for international attendees
5. Implements appropriate sponsor showcasing with tiered visibility
6. Builds conference sites efficiently with proper cross-linking and organization
7. Produces accessible, mobile-friendly HTML output
8. Facilitates quick updates when conference details change

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

### Development Environment Setup

To set up your development environment:

1. Create a virtual environment using UV:
   ```
   uv venv
   ```

2. Activate the virtual environment:
   ```
   source .venv/bin/activate
   ```

3. Install the project in development mode:
   ```
   uv pip install -e .
   ```

4. CRITICAL: When testing, you must generate the pytest_results.json file:
   ```
   pip install pytest-json-report
   pytest --json-report --json-report-file=pytest_results.json
   ```

This file is MANDATORY proof that all tests pass and must be included with your implementation.