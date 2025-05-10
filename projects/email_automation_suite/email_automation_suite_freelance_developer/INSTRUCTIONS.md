# MailFlow for Freelancers - Project-Centric Email Management System

## Overview
A specialized email automation system tailored for freelance web developers that organizes communications by client project, automates routine updates, prioritizes support requests, manages invoicing workflows, and facilitates technical communications with embedded code formatting.

## Persona Description
Marcus runs a one-person web development business and manages project communications with multiple clients simultaneously. His primary goal is to maintain consistent client communication while automatically handling routine project updates and support requests based on their urgency and project phase.

## Key Requirements

1. **Project Milestone Notification System**
   - Automated progress update templates with customizable milestone definitions for different project types
   - Ability to generate and schedule status reports based on project timeline
   - Support for inserting project-specific metrics and completion percentages
   - This feature is critical for Marcus to maintain regular client communication with minimal effort, ensuring clients stay informed about project progress without requiring manual status report creation for each milestone.

2. **Support Request Triage System**
   - Automatic urgency assessment based on keyword analysis in client emails
   - Priority assignment based on predefined client tiers and service level agreements
   - Response time tracking to ensure SLA compliance for different urgency levels
   - This feature enables Marcus to focus on the most critical client issues first, preventing important support requests from being buried in his inbox while ensuring all clients receive appropriate response times according to their service tier.

3. **Invoice and Payment Tracking**
   - Template-based invoice generation with project hour logging
   - Automated payment reminder sequences for outstanding invoices
   - Receipt confirmation and payment status tracking
   - This feature streamlines Marcus's financial workflows, ensuring timely billing and reducing the administrative overhead of tracking payments, which is critical for maintaining consistent cash flow in his freelance business.

4. **Code Snippet Formatting for Email Communications**
   - Ability to include properly formatted code blocks in email responses
   - Syntax highlighting and consistent rendering across different email clients
   - Template library for common code explanations and technical instructions
   - This feature allows Marcus to efficiently respond to technical questions with clear, readable code examples, reducing misunderstandings and follow-up questions when explaining technical concepts to clients.

5. **Meeting Scheduler with Availability Management**
   - Automated calendar availability insertion into email responses
   - Timezone detection and conversion for international clients
   - Meeting confirmation and reminder workflows
   - This feature simplifies the scheduling process, reducing the back-and-forth emails typically required to set up client meetings and ensuring Marcus can efficiently book calls across different timezones without manual calculations.

## Technical Requirements

### Testability Requirements
- All components must be testable without requiring actual email server connections
- Mock objects must be available for IMAP/SMTP services and calendar integration
- Project status calculation must be testable with sample project milestone data
- Support request triage algorithms must be testable with sample email content
- Invoice generation and payment tracking must be verifiable with test data

### Performance Expectations
- Processing of new emails should complete within 3 seconds
- Template personalization and sending should complete within 1 second
- Email with code snippets should render and send within 2 seconds
- The system should handle up to 30 active projects and 100 clients without performance degradation
- Daily email volume of up to 150 incoming and 100 outgoing messages

### Integration Points
- IMAP and SMTP protocols for email server communication
- Local database for storing templates, client information, and project details
- Optional calendar system integration for scheduling meetings
- File system for managing project attachments and deliverables
- Export/import functionality for backup and migration

### Key Constraints
- Must work with standard email protocols (IMAP/SMTP)
- Must not require third-party email services or APIs that incur additional costs
- Must preserve code formatting in email communications across various email clients
- Must operate efficiently on standard hardware without requiring cloud resources
- All data must be stored locally with proper backup procedures

## Core Functionality

The system must provide:

1. **Project Management Integration**
   - Store project information with milestones and timelines
   - Track project status and completion percentages
   - Generate automated status reports on schedule
   - Link emails to specific projects and project phases

2. **Client Support System**
   - Process incoming support requests with priority assessment
   - Apply triage rules based on content and client tier
   - Track response times against SLA targets
   - Generate support performance metrics

3. **Financial Management**
   - Track billable time by project and client
   - Generate and send invoices based on templates
   - Monitor payment status with automated reminders
   - Produce financial reports for business analysis

4. **Technical Communication Tools**
   - Format and send code snippets with syntax highlighting
   - Maintain libraries of common technical explanations
   - Ensure proper rendering across email clients
   - Support for technical specification attachments

5. **Meeting Coordination**
   - Manage availability windows for client meetings
   - Handle timezone conversions automatically
   - Send meeting confirmations and reminders
   - Track meeting frequency and duration by client

## Testing Requirements

### Key Functionalities to Verify
- Email classification accuracy for different types of client communications
- Project status calculation and milestone tracking
- Support request prioritization based on multiple factors
- Invoice generation with correct project details and hours
- Code snippet formatting across different email clients

### Critical Scenarios to Test
- Processing support requests with varying urgency levels
- Generating and sending project milestone updates
- Managing payment reminder sequences for overdue invoices
- Scheduling meetings across multiple timezones
- Responding to technical questions with formatted code examples

### Performance Benchmarks
- Email processing rate of at least 30 emails per minute
- Template personalization in under 300ms
- Code formatting and rendering in under 500ms
- System memory usage under 300MB with 50 active projects
- Database query performance with large datasets (5,000+ emails)

### Edge Cases and Error Conditions
- Handling malformed or unusually structured emails
- Processing support requests with ambiguous urgency indicators
- Managing conflicting meeting availability scenarios
- Dealing with partial or failed payments
- Recovering from interrupted automated sequences
- Handling various code languages and formatting requirements

### Required Test Coverage
- Minimum 90% code coverage for core functionality
- 100% coverage of project status calculation algorithms
- 100% coverage of support request triage logic
- 100% coverage of invoice generation system
- Comprehensive integration tests for email processing workflow

## Success Criteria

The implementation will be considered successful if it:

1. Reduces time spent on client communications by at least 40%
2. Ensures all support requests are triaged and responded to within their SLA targets
3. Achieves 95% on-time delivery of scheduled project updates
4. Reduces average payment collection time by at least 30%
5. Decreases the number of follow-up questions after technical explanations by at least 50%
6. Enables Marcus to manage up to 50% more concurrent projects without quality degradation
7. Successfully classifies at least 85% of incoming emails automatically
8. Reduces administrative overhead by at least 10 hours per week

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