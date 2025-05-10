# MailFlow for Non-Profits - Event-Driven Volunteer Management System

## Overview
A specialized email automation system tailored for non-profit organizations that organizes volunteer communications by event, automates scheduling and confirmation workflows, matches volunteers to opportunities based on skills, streamlines recognition processes, and collects post-event feedback.

## Persona Description
Jamal coordinates volunteers for community events at a non-profit organization with limited administrative support. His primary goal is to efficiently manage volunteer schedules and communications while tracking participation and sending personalized appreciation messages.

## Key Requirements

1. **Event-Based Email Segmentation System**
   - Automated email organization by event type, date, and volunteer role
   - Role-specific communication templates with dynamic event details
   - Customizable event categories with inherited communication rules
   - This feature is critical for Jamal to maintain clear communication channels for each event, ensuring volunteers receive only information relevant to their specific roles and preventing confusion when managing multiple events simultaneously.

2. **Attendance Tracking and Reminder System**
   - Automated confirmation request workflows with response tracking
   - Escalating reminder sequences based on proximity to event date
   - Attendance status dashboard with volunteer commitment metrics
   - This feature enables Jamal to reliably track volunteer commitments, reducing no-shows by ensuring timely reminders while maintaining an accurate record of expected attendance for each event without manual tracking.

3. **Volunteer Skills and Interest Database**
   - Structured data storage for volunteer skills, interests, and availability
   - Opportunity matching algorithm to suggest appropriate volunteers for specific roles
   - Communication targeting based on volunteer qualifications
   - This feature allows Jamal to quickly identify and contact the most suitable volunteers for specific roles, ensuring efficient staffing of events while respecting volunteers' interests and availability patterns.

4. **Volunteer Recognition System**
   - Service milestone tracking with automated recognition triggers
   - Personalized appreciation message templates
   - Recognition scheduling based on participation history
   - This feature streamlines the critical process of volunteer recognition, ensuring volunteers receive appropriate acknowledgment for their contributions, which is essential for maintaining volunteer retention and engagement.

5. **Post-Event Feedback Collection**
   - Automated distribution of event-specific feedback forms
   - Response aggregation and basic sentiment analysis
   - Feedback metrics by event type and volunteer role
   - This feature allows Jamal to efficiently gather insights on volunteer experiences, identifying areas for improvement and measuring volunteer satisfaction without requiring manual processing of individual responses.

## Technical Requirements

### Testability Requirements
- All components must be testable without requiring actual email server connections
- Mock objects must be available for IMAP/SMTP services
- Event management system must be testable with sample event data
- Volunteer matching algorithms must be testable with sample skills and roles
- Feedback aggregation must be verifiable with test response data

### Performance Expectations
- Processing of new emails should complete within 3 seconds
- Template personalization and sending should complete within 1 second
- Volunteer matching queries should complete within 2 seconds
- The system should handle up to 200 events and 1000 volunteers without performance degradation
- Batch email operations (e.g., sending reminders) should process at least 100 emails per minute

### Integration Points
- IMAP and SMTP protocols for email server communication
- Local database for storing volunteer information, event details, and communication history
- File system for managing event documents and resources
- Optional calendar system integration for event scheduling
- Export/import functionality for backup and migration

### Key Constraints
- Must work with standard email protocols (IMAP/SMTP)
- Must not require third-party services or APIs that incur additional costs
- Must protect volunteer privacy and comply with data protection regulations
- Must operate efficiently on standard hardware without requiring cloud resources
- All data must be stored locally with proper backup procedures
- Must accommodate limited technical expertise for system maintenance

## Core Functionality

The system must provide:

1. **Event Management System**
   - Store event information with roles, dates, and locations
   - Track event status and volunteer needs
   - Generate role-specific information packages
   - Link communications to specific events

2. **Volunteer Database System**
   - Maintain volunteer profiles with skills and interests
   - Track participation history and hours
   - Calculate engagement metrics and milestone achievements
   - Support volunteer role matching and suggestions

3. **Communication Workflow Engine**
   - Process attendance confirmations and track responses
   - Manage reminder schedules with escalation paths
   - Generate personalized recognition messages
   - Distribute and track post-event feedback requests

4. **Reporting and Analytics**
   - Track volunteer retention and participation trends
   - Analyze response rates to different communication types
   - Measure volunteer satisfaction from feedback data
   - Generate event staffing effectiveness reports

5. **Template Management System**
   - Store and organize communication templates by purpose
   - Support variable substitution for personalization
   - Maintain role-specific content variations
   - Track template effectiveness metrics

## Testing Requirements

### Key Functionalities to Verify
- Email classification and routing for event-related communications
- Volunteer-to-role matching accuracy based on skills and interests
- Reminder sequence execution with correct timing
- Recognition message generation based on service milestones
- Feedback collection and aggregation process

### Critical Scenarios to Test
- Managing multiple concurrent events with overlapping volunteer pools
- Processing volunteer responses to availability requests
- Tracking participation across recurring events
- Generating appropriate recognition for different service levels
- Aggregating and analyzing feedback from diverse event types

### Performance Benchmarks
- Event creation and setup in under 5 seconds
- Volunteer matching query execution in under 1 second
- Batch email sending rate of at least 2 emails per second
- System memory usage under 300MB with 500 volunteers
- Database query performance with large datasets (5,000+ communication records)

### Edge Cases and Error Conditions
- Handling volunteer cancellations close to event time
- Processing ambiguous or partial responses to availability requests
- Managing conflicting volunteer commitments across events
- Dealing with undeliverable emails or bounces
- Recovering from interrupted feedback collection
- Handling volunteers with no email access

### Required Test Coverage
- Minimum 90% code coverage for core functionality
- 100% coverage of volunteer matching algorithms
- 100% coverage of reminder scheduling logic
- 100% coverage of recognition milestone calculations
- Comprehensive integration tests for end-to-end communication workflows

## Success Criteria

The implementation will be considered successful if it:

1. Reduces time spent on volunteer coordination by at least 60%
2. Decreases volunteer no-show rates by at least 40%
3. Increases volunteer satisfaction scores by at least 25%
4. Enables processing of twice the current volunteer volume without additional staff
5. Achieves 95% accuracy in matching volunteers to appropriate roles
6. Ensures consistent recognition of service milestones with zero oversights
7. Collects feedback from at least 60% of event participants
8. Reduces administrative overhead by at least 15 hours per week

## Development Setup

To set up the development environment:

1. Initialize a new project with UV:
   ```
   uv init --lib
   ```

2. Install dependencies:
   ```
   uv sync
   ```

3. Run the code:
   ```
   uv run python your_script.py
   ```

4. Run tests:
   ```
   uv run pytest
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