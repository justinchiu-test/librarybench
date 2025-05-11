# Web Developer Email Automation Suite

## Overview
DevMail is a specialized email automation library designed for freelance web developers managing multiple client projects simultaneously. It enables efficient project communication, client request management, support ticket handling, and automated billing workflows, helping developers maintain consistent client relationships while minimizing time spent on administrative email tasks.

## Persona Description
Marcus runs a one-person web development business and manages project communications with multiple clients simultaneously. His primary goal is to maintain consistent client communication while automatically handling routine project updates and support requests based on their urgency and project phase.

## Key Requirements

1. **Project Milestone Notification System**
   - Create and manage project milestone templates with progress update automation
   - Support dynamic content insertion for project-specific details and completion percentages
   - Enable scheduling of project updates based on milestone completion
   - This feature is essential because it ensures clients are kept informed of project progress without requiring manual updates for each milestone, saving significant time while maintaining professional communications

2. **Support Request Triage Engine**
   - Automatically categorize incoming support emails based on urgency keywords and phrases
   - Implement client tier-based prioritization (premium clients get higher priority)
   - Generate appropriate response templates based on issue category
   - This feature is critical because it helps the developer prioritize urgent issues while ensuring all support requests are handled according to client importance, preventing important issues from being missed

3. **Invoice and Payment Tracking**
   - Generate and send invoices based on project milestones or time periods
   - Track payment status and automatically send reminders for overdue payments
   - Maintain payment history and generate financial reports
   - This feature is vital because it streamlines the billing process, ensures timely follow-up on unpaid invoices, and maintains comprehensive financial records, reducing payment delays and improving cash flow

4. **Code Snippet and Technical Specification Formatting**
   - Format and send code snippets with proper syntax highlighting in email responses
   - Create structured technical specification templates for project requirements
   - Support markdown or similar lightweight formatting for technical documentation
   - This feature is important because it enables clear, professional communication of technical information, ensuring clients receive properly formatted code examples and specifications that are easy to understand

5. **Meeting Scheduler with Availability Management**
   - Manage availability calendar and automatically suggest meeting times
   - Create meeting templates with timezone-aware scheduling
   - Send calendar invitations and meeting reminders automatically
   - This feature saves significant time by automating the back-and-forth of scheduling client meetings, handling timezone conversions, and ensuring all meetings are properly confirmed and reminder notices sent

## Technical Requirements

### Testability Requirements
- All email processing and generation functions must be testable with mock data
- Template rendering must be verifiable with different project data inputs
- Support request classification algorithms must be testable with sample support emails
- Invoice generation and reminder logic must be verifiable with test scenarios
- Meeting scheduling functions must be testable with mock availability data

### Performance Expectations
- Template processing should complete in under 100ms per template
- Support request triage should process at least 30 emails per second
- Invoice generation should complete within 200ms
- Code snippet formatting should handle up to 1000 lines of code efficiently
- The system should manage data for at least 50 concurrent client projects without performance degradation

### Integration Points
- IMAP and SMTP libraries for email retrieval and sending
- Template engine for dynamic content generation
- SQLite or similar database for storing project and client information
- Calendar system for availability management
- Markdown or similar library for code and documentation formatting

### Key Constraints
- All email content must be generable as both plain text and HTML
- Code snippets must maintain proper indentation and syntax highlighting in emails
- The system must be secure, especially for client billing information
- Timezone handling must be robust for international clients
- Email sending must respect rate limits to prevent being flagged as spam

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The core of the Web Developer Email Automation Suite should provide:

1. **Project Management Module**
   - Storing and tracking project information including milestones and deadlines
   - Generating progress updates based on milestone completion
   - Maintaining project history and client communications
   - Supporting project phase transitions and associated notifications

2. **Client Communication Engine**
   - Retrieving and processing incoming client emails
   - Categorizing and prioritizing client requests
   - Generating appropriate response templates
   - Maintaining communication history by client and project

3. **Support Request Handler**
   - Analyzing and categorizing support requests by urgency and type
   - Prioritizing requests based on client tier and issue severity
   - Suggesting response templates for common issues
   - Tracking support request resolution status

4. **Financial Management System**
   - Creating and sending professional invoices
   - Tracking payment status and history
   - Generating payment reminders with appropriate urgency
   - Producing financial reports for business analysis

5. **Meeting Coordination Module**
   - Managing developer availability calendar
   - Suggesting meeting times based on availability
   - Handling meeting confirmations and calendar invitations
   - Sending automated meeting reminders

## Testing Requirements

### Key Functionalities to Verify
- Milestone notification generation and scheduling
- Support request classification and prioritization
- Invoice generation and payment reminder sequencing
- Code snippet formatting in email responses
- Meeting time suggestion and calendar invitation creation

### Critical User Scenarios
- Sending automated project updates when milestones are completed
- Triaging incoming support requests from clients of different tiers
- Generating invoices and following up on unpaid amounts
- Responding to technical questions with properly formatted code examples
- Scheduling client meetings across different timezones

### Performance Benchmarks
- Email classification should achieve 95% accuracy on test samples
- Template rendering must complete in under 100ms
- The system should handle at least 1000 emails per day without performance degradation
- Code formatting should process snippets of up to 1000 lines in under 500ms
- Database operations should complete within 200ms for typical queries

### Edge Cases and Error Conditions
- Handling malformed or HTML-only emails
- Dealing with complex code snippets in email replies
- Managing conflicting meeting requests
- Processing partially paid invoices
- Recovering from interrupted email operations

### Required Test Coverage Metrics
- Minimum 90% code coverage across all modules
- 100% coverage of invoice generation functions
- 100% coverage of support request triage algorithm
- 100% coverage of meeting scheduling logic
- Minimum 95% coverage of project milestone notification system

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

- Project milestone notifications are correctly generated and scheduled
- Support requests are accurately categorized by urgency and client tier
- Invoices are properly generated and payment reminders sent on schedule
- Code snippets are formatted correctly in email responses
- Meeting scheduling correctly handles availability and timezone differences
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