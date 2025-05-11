# Legal Consultant Email Automation Suite

## Overview
LegalMail is a specialized email automation library designed for independent legal consultants who need to manage case-related communications, track billable time, monitor legal deadlines, and securely handle client documents. It enables efficient organization of legal correspondence while maintaining appropriate confidentiality, ensuring timely follow-ups on critical legal matters, and tracking billable communications.

## Persona Description
Carlos provides legal consulting services to small businesses and must maintain detailed client communications while ensuring timely follow-ups on legal matters. His primary goal is to manage case-related emails with appropriate confidentiality while tracking billable communications and deadlines.

## Key Requirements

1. **Case-based Email Organization System**
   - Organize emails by client, case, and matter type with confidentiality classification
   - Support tagging and categorization of communications by legal topic
   - Implement appropriate access controls based on confidentiality levels
   - This feature is critical because it ensures all case-related communications are properly organized and secured according to their confidentiality requirements, enabling efficient retrieval while maintaining legal and ethical obligations

2. **Legal Deadline Tracking and Reminder System**
   - Monitor case-specific deadlines and statutes of limitations
   - Generate escalating reminder sequences as deadlines approach
   - Provide notification of urgent or imminent deadlines
   - This feature is essential because missed legal deadlines can have serious consequences for clients and expose the consultant to malpractice risks, making automated tracking and timely reminders vital to legal practice

3. **Billable Time Tracking for Client Communications**
   - Automatically track time spent on email communications by client and case
   - Generate time entries with appropriate case references and activity descriptions
   - Produce billable time reports for invoicing purposes
   - This feature is vital because it captures billable time spent on email communications that might otherwise go unrecorded, ensuring accurate billing while reducing the administrative burden of manual time tracking

4. **Document Request and Management System**
   - Create template-based document requests with tracking
   - Manage document submission deadlines and send reminders
   - Implement secure attachment handling protocols
   - This feature streamlines the collection of necessary legal documents from clients and third parties, ensuring all required materials are received in a timely manner while maintaining appropriate security and chain of custody

5. **Client Portal Notification System**
   - Generate secure document sharing notifications
   - Track document access and acknowledgment
   - Maintain audit trails of client portal interactions
   - This feature is important because it facilitates secure document exchange with clients, providing a more secure alternative to email attachments for sensitive legal documents while maintaining records of client access and review

## Technical Requirements

### Testability Requirements
- All email organization functions must be testable with mock legal communications
- Deadline tracking must be verifiable with test case timelines
- Time tracking algorithms must produce accurate results with test communication data
- Document request tracking must be testable with simulated document submissions
- Portal notification generation must be verifiable with test document sharing scenarios

### Performance Expectations
- Email classification should process at least 100 emails per minute
- Deadline tracking should efficiently monitor at least 200 active deadlines
- Time tracking should process communications in under 100ms each
- The system should handle data for at least 50 active cases without performance degradation
- Document management should support tracking of at least 1000 documents

### Integration Points
- IMAP and SMTP libraries for email retrieval and sending
- Template engine for dynamic content generation
- SQLite or similar database for case, client, and deadline information
- Time tracking API for billable hours recording
- Secure file handling system for document management

### Key Constraints
- All communications must maintain attorney-client privilege and confidentiality
- The system must be compliant with legal ethics rules regarding client communications
- Deadline calculations must account for court calendars and jurisdictional rules
- Document handling must maintain metadata and version control
- All operations must be logged for ethical compliance and audit purposes

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The core of the Legal Consultant Email Automation Suite should provide:

1. **Case Management Module**
   - Organizing and categorizing case-related communications
   - Implementing confidentiality classification and access controls
   - Maintaining case histories and communication records
   - Supporting search and retrieval by case parameters

2. **Deadline Management System**
   - Tracking legal deadlines and statutes of limitations
   - Calculating reminder schedules based on deadline importance
   - Generating escalating reminder notifications
   - Managing calendar rules for different jurisdictions

3. **Time Tracking Engine**
   - Monitoring time spent on email communications
   - Categorizing activities for billing purposes
   - Generating billable time entries with appropriate details
   - Producing time reports for billing and analysis

4. **Document Management System**
   - Creating and tracking document requests
   - Managing document metadata and version control
   - Implementing secure document handling protocols
   - Tracking document submission status and completeness

5. **Secure Communication Module**
   - Generating secure portal notifications
   - Tracking document access and client acknowledgments
   - Maintaining audit trails of client interactions
   - Supporting encryption and secure transmission

## Testing Requirements

### Key Functionalities to Verify
- Case-based classification accuracy for various legal communication types
- Deadline tracking and reminder generation for different deadline types
- Billable time calculation for email communications
- Document request tracking and reminder sequences
- Secure portal notification generation and tracking

### Critical User Scenarios
- Processing and organizing incoming case-related emails with confidentiality classification
- Tracking approaching legal deadlines and generating appropriate reminders
- Recording billable time for client email communications
- Requesting and tracking required legal documents from clients
- Notifying clients of secure documents available in the portal

### Performance Benchmarks
- Email classification should achieve 95% accuracy on test samples
- Deadline tracking should handle at least 200 active deadlines efficiently
- Time tracking should record durations with 1-minute precision
- Document request system should track at least 1000 documents without performance issues
- The system should handle data for at least 50 active legal matters concurrently

### Edge Cases and Error Conditions
- Handling communications that relate to multiple cases or clients
- Managing conflicting or overlapping legal deadlines
- Processing communications with complex or unusual time tracking requirements
- Dealing with failed document submissions or corrupt attachments
- Handling undeliverable notifications or client access issues

### Required Test Coverage Metrics
- Minimum 90% code coverage across all modules
- 100% coverage of confidentiality classification functions
- 100% coverage of deadline calculation and reminder generation
- 100% coverage of billable time tracking algorithm
- Minimum 95% coverage of document request and tracking functions

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

- Case-based email organization correctly classifies test communications
- Deadline tracking accurately monitors test case timelines and generates appropriate reminders
- Billable time tracking correctly calculates time spent on test communications
- Document request system properly tracks test document submissions
- Portal notification system accurately generates and tracks test notifications
- All performance benchmarks are met under load testing
- The system correctly handles all specified edge cases and error conditions

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Getting Started
To set up the development environment:
1. Create a virtual environment using `uv venv`
2. Activate the environment with `source .venv/bin/activate`
3. Install the project with `uv pip install -e .`

CRITICAL: When testing your implementation, you MUST run tests with pytest-json-report and provide the pytest_results.json file:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```

Providing the pytest_results.json file is MANDATORY for demonstrating that your implementation meets the requirements.