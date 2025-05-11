# FreelanceFlow - CLI Task Management for Independent Developers

## Overview
A specialized command-line task management system designed for freelance developers managing multiple client projects. The system enables accurate tracking of billable hours, organization of client-specific tasks, and generation of detailed billing reports based on time tracked against specific deliverables.

## Persona Description
Mia works on multiple freelance projects with different clients and needs to track billable hours accurately. Her primary goal is to organize client-specific tasks and generate billing reports based on time tracked against specific deliverables.

## Key Requirements
1. **Client Portal Integration**: Develop a secure API mechanism that allows clients to view task status without requiring CLI access. This is critical for Mia as it enables transparent communication with clients about project progress, eliminates the need for manual status reports, and maintains professional client relationships while protecting project details.

2. **Invoicing Automation**: Create a sophisticated report generation system that produces itemized bills from completed tasks with time tracking data. This feature is essential for Mia to save time on administrative work, ensure accurate billing for all completed work, and provide professional, detailed invoices that clearly justify charges to clients.

3. **Contract Milestone Tracking**: Implement contract milestone management with payment status integration. This capability allows Mia to organize tasks according to contract milestones, track completion percentage against payment schedules, and maintain clear visibility of outstanding payments versus delivered work.

4. **Proposal-to-Task Conversion**: Develop functionality to transform client project proposals into structured task lists with estimates. This feature enables Mia to quickly initialize new projects based on approved proposals, maintain consistency between quoted work and actual tasks, and track scope changes against the original agreement.

5. **Disconnected Mode Operation**: Build a robust local-first operation mode that enables full functionality without internet connection. This capability is crucial for Mia's mobile work style, allowing her to continue tracking time and managing tasks while traveling or working in remote locations, with automatic synchronization when connectivity is restored.

## Technical Requirements

### Testability Requirements
- All components must support offline/online mode testing with appropriate mocking
- Client portal API must be fully testable without requiring an actual web server
- Invoice generation must be verifiable with predetermined time entries and expected outputs
- Contract milestone calculations must be testable with simulated project progress
- Proposal conversion must be testable with standard proposal formats
- All database operations must be testable with in-memory storage options

### Performance Expectations
- System must handle at least 50 simultaneous client projects without performance degradation
- Time tracking operations must have negligible impact on system performance
- Invoice generation for a year's worth of tasks must complete in under 10 seconds
- Local data operations in disconnected mode must perform identically to connected mode
- Synchronization after reconnection must efficiently handle up to 1000 offline changes

### Integration Points
- Secure API endpoint for client portal data access
- Standardized invoice format generation (PDF, HTML, JSON)
- Local data storage with serialization/deserialization for offline mode
- Synchronization mechanism with conflict resolution strategy
- Proposal import mechanism supporting common formats (Markdown, JSON, YAML)

### Key Constraints
- The implementation must maintain complete data privacy with client separation
- All functionality must be accessible via programmatic API without UI components
- The system must be resilient to connection interruptions during synchronization
- Time tracking must be accurate to the minute for proper billing
- Contract milestone and payment data must be stored securely with proper encryption

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The core of this implementation centers on a Python library that provides:

1. **Client-Centric Task Management**: A core module handling CRUD operations for tasks with client segregation, ensuring complete separation of data between different client projects.

2. **Advanced Time Tracking System**: Precise time recording functionality that logs work periods against specific tasks, with support for manual time entry, timer-based recording, and categorization by billable/non-billable status.

3. **Contract and Milestone Manager**: A component that maintains relationship between tasks and contract deliverables, tracking completion percentage and payment status for each milestone.

4. **Invoicing Engine**: A flexible reporting system capable of generating detailed invoices from completed tasks and time entries, with customizable templates and format options.

5. **Proposal Conversion Tool**: Logic to parse project proposals and generate appropriate task structures, estimates, and milestones based on the proposal content.

6. **Synchronization Framework**: A robust mechanism for offline operation, storing changes locally and synchronizing with the main data store when connectivity is restored, including conflict resolution strategies.

7. **Client Portal API**: A secure interface for exposing limited task and progress data to clients, with authentication and authorization controls.

The system should be designed as a collection of Python modules with clean interfaces, allowing components to be used independently or as an integrated solution. All functionality should be accessible through a programmatic API that could be called by a CLI tool (though implementing the CLI itself is not part of this project).

## Testing Requirements

### Key Functionalities to Verify
- Task creation, retrieval, updating, and deletion with client segregation
- Time tracking accuracy including start/stop operations and manual entry
- Invoice generation with correct calculations and formatting
- Contract milestone progress tracking and payment status updates
- Proposal parsing and task list generation
- Offline operation and synchronization with conflict resolution
- Client portal data access with proper security controls

### Critical User Scenarios
- Complete client project lifecycle from proposal to final invoice
- Time tracking across multiple client projects within the same day
- Working offline while traveling and synchronizing upon return
- Client reviewing project progress through the portal interface
- Contract milestone completion and payment tracking
- Generating end-of-month invoices for all active clients

### Performance Benchmarks
- Task operations must complete in <50ms for typical usage
- Time tracking start/stop operations must have <100ms latency
- Invoice generation must process at least 500 time entries per second
- Local database operations must perform within 10% of online operations
- Synchronization after being offline must process at least 100 changes per second

### Edge Cases and Error Conditions
- Handling conflicting changes during synchronization
- Recovery from interrupted time tracking sessions
- Proper handling of timezone differences for remote work
- Accurate calculations with partial hours and minimum billing increments
- Security for client data with proper access controls
- Resilience against network interruptions during data transfer

### Required Test Coverage Metrics
- Minimum 90% line coverage for all functional components
- 100% coverage of all public APIs
- All error handling paths must be explicitly tested
- Performance tests must verify all stated benchmarks
- Security tests must verify client data isolation and access controls

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

1. All five key requirements are fully implemented and pass their respective test cases.
2. The system demonstrates the ability to manage tasks for at least 10 distinct clients with proper data isolation.
3. Time tracking functionality accurately records and reports billable hours with appropriate categorization.
4. Invoicing correctly calculates billing based on tracked time and contracted rates.
5. The system operates fully in offline mode with successful synchronization when reconnected.
6. Client portal API securely exposes appropriate information without compromising data privacy.
7. Contract milestone tracking accurately reflects project progress and payment status.
8. The implementation maintains high performance even with large datasets across many clients.

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Development Setup
1. Use `uv venv` to setup a virtual environment. From within the project directory, activate it with `source .venv/bin/activate`.
2. Install the project with `uv pip install -e .`
3. CRITICAL: Before submitting, run the tests with pytest-json-report:
   ```
   pip install pytest-json-report
   pytest --json-report --json-report-file=pytest_results.json
   ```
4. Verify that all tests pass and the pytest_results.json file has been generated.

REMINDER: Generating and providing the pytest_results.json file is a critical requirement for project completion.