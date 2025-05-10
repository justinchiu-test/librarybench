# Conference Event Site Generator

A specialized static site generator optimized for creating and maintaining event websites for conferences, workshops, and similar professional gatherings.

## Overview

This project provides an event-focused static site generator that enables conference organizers to create, maintain, and update event websites with schedules, speaker information, venue details, and registration information. The system automates the generation of event-appropriate layouts and features while allowing for quick updates as event details evolve.

## Persona Description

Priya organizes tech conferences and needs to create event websites with schedules, speaker information, venue details, and registration information that can be quickly updated as event details evolve.

## Key Requirements

1. **Schedule Builder**: Generate conference timetables from structured session data.
   - As the core of any conference website, Priya needs to present complex event schedules spanning multiple days, tracks, and session types in a clear, navigable format.
   - This feature must support concurrent sessions, different room assignments, varying session durations, and dynamic updates as the schedule evolves.

2. **Speaker Profile Management**: Create and maintain speaker information pages.
   - Speakers are a key attraction for conference attendees, so Priya needs comprehensive speaker profiles with biographies, photos, session information, and social links.
   - The system should support batch import of speaker information, individual updates, and automatic linking between speakers and their sessions.

3. **Multi-track Session Visualization**: Display concurrent conference events across different rooms.
   - With multiple simultaneous sessions, attendees need a visual way to understand what's happening when and where throughout the event.
   - This feature should generate interactive visualizations of the conference program showing time slots, room allocations, and session overlaps.

4. **Countdown Timers and Time Zone Conversion**: Display event timing with attendee-specific time zones.
   - For conferences with international or virtual audiences, showing event times in the attendee's local time zone is essential for planning.
   - The system should generate countdown displays to key events and provide automatic time zone conversion for all scheduled sessions.

5. **Sponsor Showcase**: Present sponsors with tiered visibility based on sponsorship levels.
   - Sponsors provide crucial financial support for conferences, so Priya needs to showcase them appropriately according to their sponsorship tier.
   - This feature should support different sponsorship levels with corresponding visibility and placement throughout the site.

## Technical Requirements

### Testability Requirements
- Schedule generation must be testable with sample conference programs
- Speaker profile generation must verify correct formatting and session relationships
- Multi-track visualization must validate accurate time and room assignments
- Time zone conversion must verify correctness across international time zones
- Sponsor placement must validate appropriate visibility according to tier

### Performance Expectations
- Complete site generation should finish in under 15 seconds for a typical conference site
- Schedule processing should handle 200+ sessions across multiple tracks in under 5 seconds
- Speaker profile generation should process 100+ speakers with their sessions in under 10 seconds
- Time zone calculations should execute in under 50ms per conversion
- Incremental updates should reflect changes in under 3 seconds

### Integration Points
- Calendar formats (iCalendar) for session export
- Time zone databases for international conversions
- Structured data formats for schedule information (CSV, JSON)
- Social media integration for speaker profiles
- Image processing for speaker photos and sponsor logos

### Key Constraints
- Must operate without a database or server-side processing
- Must generate completely static output deployable to any web hosting service
- Must produce accessible content following WCAG 2.1 AA standards
- Must support viewing on mobile devices with responsive layouts
- Must provide printer-friendly versions of key information (schedules, session details)

## Core Functionality

The system should implement a comprehensive platform for conference website generation:

1. **Program Management System**
   - Process structured session data (speakers, times, rooms, descriptions)
   - Create relationships between sessions, tracks, and speakers
   - Generate schedule views at different granularities (day, track, session type)
   - Support filtering and personalization of schedules

2. **Speaker Management**
   - Process speaker information with biographies and credentials
   - Generate profile pages with linked sessions
   - Create speaker directories and search functionality
   - Support social media and external links

3. **Visualization Framework**
   - Generate time-based visualizations of the conference program
   - Create room and track-based views for multi-track events
   - Implement interactive filtering and highlighting
   - Support mobile-friendly schedule views

4. **Time System**
   - Process schedule information with explicit time zones
   - Generate countdown timers to key events
   - Create automatic time zone conversion for displayed times
   - Support calendar export in attendee's local time

5. **Sponsorship System**
   - Define sponsorship tiers with visibility rules
   - Process sponsor information and assets
   - Generate appropriate sponsor showcases by tier
   - Implement sponsor placement throughout the site

## Testing Requirements

### Key Functionalities to Verify
- Schedule generation with accurate session timing and relationships
- Speaker profile creation with correct session associations
- Multi-track visualization with proper concurrent session display
- Time zone conversion accuracy across international boundaries
- Sponsor showcase with correct tier-based visibility

### Critical User Scenarios
- Creating a multi-day, multi-track conference schedule
- Adding and updating speaker information with session assignments
- Viewing the conference program across different visualization modes
- Accessing schedule information in different time zones
- Managing sponsors across different sponsorship tiers

### Performance Benchmarks
- Process 200 conference sessions in under 5 seconds
- Generate 100 speaker profiles with session links in under 10 seconds
- Render multi-track visualization for 8 concurrent tracks in under 3 seconds
- Perform time zone conversions at a rate of at least 100 per second
- Complete full site generation for a typical conference in under 15 seconds

### Edge Cases and Error Conditions
- Handling schedule conflicts and overlapping sessions
- Managing speakers with multiple sessions across different tracks
- Dealing with time zone edge cases (DST transitions during the event)
- Processing last-minute schedule changes and cancellations
- Handling sponsors with special placement requirements

### Required Test Coverage Metrics
- Minimum 90% line coverage for core processing components
- 100% coverage for schedule generation and time handling
- Integration tests for all data import functionality
- Validation tests for generated schedule visualizations
- Performance tests for time-critical operations

## Success Criteria

The implementation will be considered successful if it:

1. Generates accurate conference schedules from structured data with proper handling of multi-track, multi-day events
2. Creates comprehensive speaker profiles with correct links to their sessions and biographical information
3. Produces clear visualizations of concurrent sessions across different rooms and tracks
4. Correctly handles time zone conversions and countdowns for international audiences
5. Presents sponsors according to their tier with appropriate visibility throughout the site
6. Processes a typical conference (200 sessions, 100 speakers, 3 days, 5 tracks) in under 15 seconds
7. Achieves all required test coverage metrics with a clean test suite

## Getting Started

To set up the development environment:

1. Initialize the project using `uv init --lib` in your project directory
2. Install dependencies using `uv sync`
3. Run Python scripts with `uv run python your_script.py`
4. Run tests with `uv run pytest`

When implementing this library, focus on creating well-defined APIs that provide all the required functionality without any user interface components. All features should be implementable as pure Python modules and classes that can be thoroughly tested using pytest.