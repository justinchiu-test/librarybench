# Theater Production CMS

A specialized content management system designed for community theater groups to manage productions, cast information, and ticket sales.

## Overview

Theater Production CMS is a comprehensive content management library tailored for community theater organizations. It enables theater directors to delegate content responsibilities, manage productions and events, track cast and crew information, handle ticket sales, and organize media content, all while maintaining consistent branding across the site.

## Persona Description

Marcus manages a community theater group and needs to update their website with new productions, cast information, and ticket sales. His primary goal is to delegate specific content responsibilities to different team members while maintaining consistent branding and design across the entire site.

## Key Requirements

1. **Role-based Content Management**: Develop a comprehensive permission system that allows different team members to edit specific sections of content while restricting access to others. This is critical for Marcus as it enables him to delegate responsibilities (program notes, cast bios, ticket information) to appropriate team members while preventing unauthorized changes to sensitive content.

2. **Production Calendar and Scheduling**: Create a robust event management system that handles rehearsals, performances, special events, and can display different views (public vs. internal). This feature is essential for keeping both the audience and theater company members informed about upcoming events, location details, and any schedule changes.

3. **Cast and Crew Directory**: Implement a flexible personnel management system that stores and displays cast/crew information, headshots, biographies, and roles across different productions. This allows Marcus to showcase talent while building a persistent database of everyone who has contributed to the theater's productions over time.

4. **Ticket Sales and Seating Management**: Develop a comprehensive ticket inventory system that tracks seat availability, handles various pricing tiers, and manages reservation data. This functionality is vital for the theater's financial operations, allowing for advanced sales tracking and attendance reporting.

5. **Production Media Gallery**: Create a structured media management system that organizes photos and videos by production with embedded playback capabilities. This enables Marcus to build a visual archive of past productions while using media assets for promotion and historical documentation.

## Technical Requirements

### Testability Requirements
- All components must have unit tests with at least 90% coverage
- Authentication and authorization logic must be thoroughly tested with various permission scenarios
- Calendar and scheduling functions must be testable with mocked time functions
- Seating chart algorithms must be validated with comprehensive test cases
- Media organization functions must be verified with test fixtures

### Performance Expectations
- Directory searches must complete within 100ms
- Calendar rendering operations must complete within 200ms
- Ticket availability checks must process within 50ms, even with concurrent access
- Media gallery operations should be optimized for various collection sizes
- Full production data should load within 300ms

### Integration Points
- Support for common storage backends (local filesystem, SQLite, optional cloud storage)
- Webhook support for notification systems (schedule changes, ticket sales)
- Export capabilities for program generation (PDF, structured data)
- CSV import/export for bulk data management
- Optional email integration for notifications and ticket confirmations

### Key Constraints
- All code must be pure Python with minimal dependencies
- No JavaScript dependencies or browser-specific code
- No direct coupling to web frameworks, though adaptors can be provided
- All content must be serializable for backup/restore
- Must support offline content creation and planning

## Core Functionality

The library must provide the following core components:

1. **User and Permission System**:
   - Role definition and management
   - Section-based access controls
   - User authentication logic
   - Permission verification and enforcement
   - Audit logging of content changes

2. **Production Management**:
   - Production metadata (title, dates, synopsis, etc.)
   - Production status tracking (planning, rehearsal, active, archived)
   - Performance schedule management
   - Production-specific settings and configurations

3. **Event Calendar System**:
   - Multi-view calendar (public/private/role-specific)
   - Rehearsal scheduling with room allocation
   - Performance scheduling with ticket availability
   - Custom event types and categorization
   - Recurring event patterns

4. **Personnel Directory**:
   - Cast and crew profiles with contact information
   - Role and production history tracking
   - Biography management with formatting
   - Headshot and photo management
   - Privacy controls for sensitive information

5. **Ticket and Seating System**:
   - Venue configuration and seat mapping
   - Multiple ticket types and pricing tiers
   - Reservation status tracking
   - Sales reporting and analytics
   - Seating chart visualization data

6. **Media Management**:
   - Production-based media organization
   - Photo gallery management
   - Video hosting integration
   - Metadata tagging and searching
   - Usage tracking for promotional materials

## Testing Requirements

### Key Functionalities to Verify
- Creation, retrieval, update, and deletion of all content types
- Proper enforcement of permissions across different roles
- Correct calendar and scheduling behavior with different date scenarios
- Ticket inventory accuracy under various sales conditions
- Media organization and retrieval by production

### Critical User Scenarios
- Adding a new production with complete details and schedule
- Managing cast assignments across multiple productions
- Setting up differentiated access for various team members
- Processing ticket sales and tracking availability
- Organizing production photos into galleries

### Performance Benchmarks
- Directory search speed with growing personnel database
- Calendar rendering with different date ranges and event densities
- Concurrent ticket reservations without conflicts
- Media gallery performance with large collections
- System behavior under multiple simultaneous content updates

### Edge Cases and Error Conditions
- Handling scheduling conflicts
- Proper management of sold-out performances
- Recovery from invalid permission settings
- Behavior when productions overlap in schedule
- Handling duplicate personnel entries

### Required Test Coverage Metrics
- Minimum 90% line coverage for all core components
- 100% coverage of permission-related code
- All error handling paths must be tested
- Performance tests for calendar and ticket operations
- Security tests for access control mechanisms

## Success Criteria

The implementation will be considered successful when:

1. Different team members can successfully edit their assigned sections without accessing unauthorized content
2. Production schedules, rehearsals, and events are accurately managed and displayed in appropriate views
3. A comprehensive directory of all cast and crew is maintained with production history
4. Ticket inventory accurately reflects sales and availability for all performances
5. Media content is properly organized by production and accessible for promotional use
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