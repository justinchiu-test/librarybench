# Theater Group Content Management System

## Overview
A specialized content management system designed for theater groups to manage productions, cast information, events, and ticket sales. This system enables theater directors to delegate specific content responsibilities to different team members while maintaining consistent branding and design across the entire site.

## Persona Description
Marcus manages a community theater group and needs to update their website with new productions, cast information, and ticket sales. His primary goal is to delegate specific content responsibilities to different team members while maintaining consistent branding and design across the entire site.

## Key Requirements

1. **Role-based content editing with section-specific permissions**
   - Critical for Marcus to delegate responsibilities to different team members (e.g., production manager updates show details, marketing coordinator handles ticket promotions)
   - Must support granular permissions for specific content areas without allowing access to the entire system
   - Should include approval workflows for content that requires director oversight before publication

2. **Event calendar with rehearsal and performance scheduling**
   - Essential for managing complex production schedules including rehearsals, performances, and special events
   - Must distinguish between internal events (rehearsals, tech runs) and public events (performances, open houses)
   - Should support recurring event patterns, exceptions, and rescheduling with notification capabilities

3. **Cast and crew directory with bio management tools**
   - Important for showcasing talent and recognizing contributions of volunteers and performers
   - Must support self-service updates where cast/crew can edit their own profiles within guidelines
   - Should include role history tracking to build performance history for each individual

4. **Ticket sales tracking with seat selection visualization**
   - Critical for managing venue capacity and ticket availability for each performance
   - Must track sales, reservations, and attendance for financial and planning purposes
   - Should visualize seat selection status for venues with assigned seating

5. **Media gallery organized by production with video hosting integration**
   - Necessary for archiving and promoting productions through photos, videos, and press materials
   - Must organize media by production with appropriate metadata and searching
   - Should support integration with video platforms for rehearsal recordings and production highlights

## Technical Requirements

### Testability Requirements
- All components must have unit tests with at least 85% code coverage
- Integration tests must verify the permission system correctly restricts and allows appropriate access
- Performance tests must ensure calendar operations scale with complex event schedules
- Mock authentication system for testing role-based permissions

### Performance Expectations
- Calendar operations must complete within 200ms regardless of event volume
- Media gallery must handle at least 1000 assets per production without performance degradation
- Directory searches must return results within 500ms even with complex filtering
- Ticket system must support at least 100 concurrent seat selection operations

### Integration Points
- Authentication system for role-based access control
- Calendar export in iCal/Google Calendar format
- Email notification system for schedule changes and approvals
- API for ticket sales integration with external payment processors

### Key Constraints
- All user data must be securely stored with appropriate encryption
- Media storage must support a variety of file formats with proper validation
- System must maintain audit logs for all content changes for accountability
- Calendar system must handle timezone considerations for touring productions

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system must provide a Python library with the following core components:

1. **User and Permission Management**
   - Role definition and assignment system
   - Section-based permission control
   - Content approval workflows
   - Audit logging for content operations

2. **Production Management**
   - Production data model with all relevant metadata
   - Season and programming structure
   - Show description and information management
   - Performance schedule coordination

3. **Calendar and Scheduling System**
   - Advanced event management with categorization
   - Recurring event pattern support
   - Conflict detection and resolution
   - Public/private event distinction

4. **Cast and Crew Directory**
   - Biography data model with role history
   - Self-service profile management
   - Role assignment and tracking
   - Directory search and filtering

5. **Ticketing Infrastructure**
   - Venue and seating chart management
   - Ticket inventory and availability tracking
   - Reservation and sales recording
   - Performance attendance reporting

6. **Media Asset Management**
   - Production-oriented media organization
   - Metadata tagging and categorization
   - Gallery and collection creation
   - Video integration and embedding

## Testing Requirements

### Key Functionalities to Verify
- Role-based permissions correctly limit access to appropriate content sections
- Calendar correctly handles complex scheduling patterns including conflicts
- Directory accurately maintains biographical information and role history
- Ticket system properly tracks availability and prevents double-booking
- Media assets are correctly organized by production with appropriate metadata

### Critical User Scenarios
- Adding a new production with complete information and schedule
- Delegating content responsibilities to different team members
- Managing cast changes and updating associated content
- Setting up a new venue with custom seating arrangement
- Creating a comprehensive media archive for a past production

### Performance Benchmarks
- Calendar system must handle a season with 200+ events in under 500ms
- Directory searches must complete in under 300ms with 100+ cast/crew members
- Media gallery must load metadata for 500+ assets in under 1 second
- Permission checks must not add more than 50ms overhead to content operations

### Edge Cases and Error Conditions
- Handling scheduling conflicts and overlapping events
- Managing cast changes mid-production
- Recovering from incomplete content submissions
- Handling duplicate biographical information
- Managing sold-out performances and waiting lists

### Required Test Coverage Metrics
- Minimum 85% code coverage across all modules
- 100% coverage of permission control logic
- 100% coverage of ticket availability calculations
- 100% coverage of calendar conflict detection

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

1. The permission system correctly enforces role-based access to different content sections
2. The calendar system accurately manages complex production schedules with public/private distinction
3. The directory maintains comprehensive cast/crew information with role history
4. The ticketing system tracks availability and prevents booking conflicts
5. The media system organizes assets by production with appropriate metadata

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