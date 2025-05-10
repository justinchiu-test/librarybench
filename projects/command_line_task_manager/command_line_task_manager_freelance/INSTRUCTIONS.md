# FreelanceFlow - A Freelance Developer's Task Management Library

## Overview
FreelanceFlow is a specialized task management library designed specifically for freelance developers who work on multiple projects with different clients. This library provides robust APIs for organizing client-specific tasks, tracking billable hours, managing client portals, monitoring project milestones, and supporting disconnected operation to optimize workflow and financial management for independent contractors.

## Persona Description
Mia works on multiple freelance projects with different clients and needs to track billable hours accurately. Her primary goal is to organize client-specific tasks and generate billing reports based on time tracked against specific deliverables.

## Key Requirements
1. **Client Portal Integration**: The library must provide functionality to expose task status information to clients without requiring direct CLI access. This is critical for Mia to maintain transparency with clients about project progress while preserving her private task management workspace and limiting client access to only relevant information.

2. **Invoicing Automation**: The system should support generating itemized bills based on completed tasks and tracked time. This feature is essential for Mia to streamline her billing process, ensuring accurate accounting for all billable work and reducing administrative overhead in creating client invoices.

3. **Contract Milestone Tracking**: The library must offer comprehensive tracking of project milestones with payment status integration. This functionality is crucial for Mia to monitor progress against contractual obligations, track which milestones have been invoiced and paid, and maintain clear financial records for each project.

4. **Proposal-to-Task Conversion**: The system needs to support converting client project proposals into structured task lists. This feature is vital for Mia to seamlessly transition from the business development phase to project execution, ensuring all proposed deliverables are properly tracked as actionable tasks.

5. **Disconnected Mode Operation**: The library must provide local-first operation that functions without internet connectivity. This capability is important for Mia to maintain productivity while traveling or working in remote locations, ensuring continuous access to her task management system regardless of network availability.

## Technical Requirements
- **Testability Requirements**:
  - All components must be individually testable with mock client and project data
  - Client portal functionality must be testable without actual external access
  - Invoicing generation must be verifiable with predefined task and time data
  - Milestone tracking must be testable with simulated project progress
  - Offline synchronization must be comprehensively testable

- **Performance Expectations**:
  - Task creation and retrieval by client/project < 30ms
  - Invoice generation < 100ms for projects with hundreds of time entries
  - Milestone status updates < 20ms
  - Proposal conversion < 50ms
  - Synchronization operations < 500ms
  - The system must handle at least 50 concurrent client projects with no performance degradation

- **Integration Points**:
  - Client portal interfaces (web APIs, data export)
  - Accounting and invoicing systems
  - Contract management tools
  - Proposal management systems
  - Synchronization mechanisms for offline operation
  - Time tracking systems

- **Key Constraints**:
  - Must operate efficiently on limited bandwidth connections
  - Client data must be properly segregated and secured
  - Financial calculations must be precise and auditable
  - Must support various currencies and billing rates
  - Storage efficiency for offline operation on mobile devices

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The library must provide the following core functionality:

1. **Task Management System**: 
   - Create, read, update, and delete tasks with client and project association
   - Support for task prioritization, categorization, and status tracking
   - Client and project filtering capabilities
   - Comprehensive task metadata for deliverable tracking

2. **Client Management**: 
   - Organize tasks by client and project
   - Manage client information and contact details
   - Control data visibility for client portal access
   - Support different billing rates and terms by client

3. **Time Tracking**: 
   - Record time spent on tasks with start/stop functionality
   - Associate time entries with specific deliverables
   - Support for different billing categories (billable, non-billable)
   - Generate time reports by client, project, and time period

4. **Financial Management**: 
   - Generate invoices from completed tasks and time entries
   - Track milestone payments and contract values
   - Monitor outstanding and received payments
   - Support for different billing models (hourly, fixed-price, retainer)

5. **Proposal Management**: 
   - Convert project proposals to structured task lists
   - Track proposal status (draft, submitted, accepted, rejected)
   - Estimate time and effort for proposed work
   - Maintain connection between proposal items and resulting tasks

6. **Offline Operation**: 
   - Support local-first data storage
   - Synchronize data when connectivity is restored
   - Resolve conflicts in data modified while offline
   - Optimize storage for limited-resource environments

## Testing Requirements
To validate a successful implementation, the following testing should be conducted:

- **Key Functionalities to Verify**:
  - Task creation, retrieval, updating, and deletion with client association
  - Client portal data generation and access control
  - Invoice generation with accurate financial calculations
  - Milestone tracking and payment status updates
  - Proposal conversion to task lists
  - Offline operation and synchronization

- **Critical User Scenarios**:
  - Creating and organizing tasks for multiple client projects
  - Generating client-viewable progress reports
  - Creating itemized invoices based on completed work
  - Tracking milestone completion and payment status
  - Converting a client proposal to actionable tasks
  - Working offline and synchronizing upon reconnection

- **Performance Benchmarks**:
  - Task retrieval by client < 30ms
  - Invoice generation < 100ms for complex projects
  - Milestone updates < 20ms
  - Proposal conversion < 50ms
  - Synchronization < 500ms for a day's work

- **Edge Cases and Error Conditions**:
  - Handling complex billing scenarios with multiple rates
  - Managing conflicting changes during synchronization
  - Dealing with partially completed milestones
  - Processing rejected proposals or scope changes
  - Managing very large client projects with hundreds of tasks

- **Required Test Coverage Metrics**:
  - Minimum 90% line coverage for all modules
  - 100% coverage for financial calculation components
  - All public APIs must have comprehensive test cases
  - All error handling code paths must be tested

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
A successful implementation of the FreelanceFlow library will meet the following criteria:

1. **Functionality Completeness**:
   - All five key requirements are fully implemented and operational
   - Client portal integration provides appropriate visibility
   - Invoicing accurately reflects completed work and time
   - Milestone tracking comprehensively monitors project progress
   - Proposal conversion creates well-structured task lists
   - Offline operation functions reliably in disconnected environments

2. **Performance Metrics**:
   - All performance benchmarks are met or exceeded
   - The system handles multiple concurrent client projects efficiently
   - Operations remain responsive even with large historical datasets

3. **Quality Assurance**:
   - Test coverage meets or exceeds the specified metrics
   - All identified edge cases and error conditions are properly handled
   - No critical bugs in core functionality, especially in financial calculations

4. **Integration Capability**:
   - The library provides clean interfaces for external systems
   - Financial data can be exported in standard formats
   - Synchronization mechanisms are robust against various network conditions

## Setup Instructions
To set up this project:

1. Use `uv init --lib` to create a proper Python library project structure with a `pyproject.toml` file.

2. Install dependencies using `uv sync`.

3. Run your code with `uv run python script.py`.

4. Run tests with `uv run pytest`.

5. Format code with `uv run ruff format`.

6. Check code quality with `uv run ruff check .`.

7. Verify type hints with `uv run pyright`.