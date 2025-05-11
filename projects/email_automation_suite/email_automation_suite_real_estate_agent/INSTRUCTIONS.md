# Real Estate Agent Email Automation Suite

## Overview
MailFlow for Real Estate is a specialized email automation library designed for independent real estate agents who manage multiple property listings and client communications. It enables agents to efficiently organize property-related emails, send personalized listing information, track client inquiries, and maintain consistent follow-up sequences with minimal manual intervention.

## Persona Description
Sofia manages listings and client communications for her independent real estate business, handling dozens of property inquiries daily. Her primary goal is to promptly respond to potential buyers and sellers with personalized information while automatically organizing communications by property and client status.

## Key Requirements

1. **Property Listing Template System**
   - Create dynamic email templates with variable insertion for different property types (residential, commercial, land)
   - Support for automatic population of property details including price, square footage, bedrooms, bathrooms, and amenities
   - Allow customization of template styling and formatting to maintain brand consistency
   - This feature is critical because it allows the agent to quickly respond to property inquiries with accurate, detailed information without having to manually craft each email

2. **Client Follow-up Sequence Engine**
   - Implement time-based follow-up sequences triggered by specific client interactions
   - Configure multi-stage sequences (initial response, 3-day follow-up, 7-day check-in, etc.)
   - Support conditional logic based on client response or lack thereof
   - This feature is essential for nurturing leads and maintaining engagement without requiring the agent to remember and manually track dozens of follow-up timelines

3. **Client Categorization System**
   - Create a robust classification system for contacts (buyer/seller, price range, property preferences)
   - Support for tagging and segmentation based on client status and requirements
   - Enable automatic categorization based on email content analysis
   - This feature helps the agent organize their client database and prioritize communications based on likelihood to transact, preventing important clients from falling through the cracks

4. **Property-specific Email Organization**
   - Implement property-based threading and organization of all communications
   - Support automatic filing and retrieval of property-related attachments (photos, documents)
   - Create property dossiers that aggregate all communications about a specific listing
   - This feature is vital because it centralizes all communications related to each property, making it easy to track the history and status of each listing

5. **Inquiry Source Tracking and Analytics**
   - Identify and track the source of inquiries (websites, referrals, advertising channels)
   - Generate reports on conversion rates by source
   - Measure response time and effectiveness across marketing channels
   - This feature allows the agent to assess which marketing channels are most effective, enabling data-driven decisions about where to allocate marketing resources

## Technical Requirements

### Testability Requirements
- All email processing functions must be testable with mock email data
- Template rendering must be verifiable with different property data inputs
- Follow-up sequence logic must be testable with simulated time progression
- Client categorization algorithms must be verifiable with test classification cases
- Analytics functions must produce consistent, verifiable outputs

### Performance Expectations
- Template processing should complete in under 100ms per template
- Email classification and filing should process at a rate of at least 50 emails per second
- Follow-up scheduling must handle at least 1000 active sequences without performance degradation
- Database operations for client categorization should complete within 200ms
- The system should be able to handle a database of at least 10,000 clients and 500 property listings

### Integration Points
- IMAP and SMTP libraries for email retrieval and sending
- Template engine for dynamic content generation
- SQLite or similar database for storing client information and property details
- Scheduling system for follow-up sequences
- Analytics engine for marketing channel effectiveness reporting

### Key Constraints
- All email content must be generable as both plain text and HTML
- The implementation must respect email rate limits to prevent being flagged as spam
- Client data must be securely stored with appropriate encryption
- Property photos and attachments must be handled efficiently to minimize storage requirements
- The system must be resilient to network interruptions and email service downtime

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The core of the Real Estate Agent Email Automation Suite should provide:

1. **Email Management Engine**
   - Retrieving and sending emails via IMAP and SMTP
   - Classifying incoming emails by client, property, and inquiry type
   - Filing and organizing emails into appropriate categories
   - Handling attachments related to properties

2. **Template Management System**
   - Creating and storing property listing templates
   - Variable substitution for dynamic content
   - Support for different property types and marketing angles
   - Template versioning and effectiveness tracking

3. **Client Relationship Management**
   - Storing and categorizing client information
   - Tracking client preferences and requirements
   - Maintaining communication history
   - Prioritizing clients based on engagement and likelihood to transact

4. **Automated Follow-up System**
   - Scheduling follow-up communications based on configurable rules
   - Handling multi-stage communication sequences
   - Adjusting follow-up timing based on client engagement
   - Providing notification of sequence completion or client response

5. **Analytics Module**
   - Tracking inquiry sources and conversion rates
   - Measuring response times and effectiveness
   - Analyzing communication patterns
   - Reporting on marketing channel ROI

## Testing Requirements

### Key Functionalities to Verify
- Email retrieval and classification accuracy
- Template rendering with various property data inputs
- Client categorization logic correctness
- Follow-up sequence execution with proper timing
- Inquiry source identification and tracking

### Critical User Scenarios
- Processing new client inquiries about a specific property
- Generating and sending dynamic property listings with complete details
- Creating and executing multi-stage follow-up sequences
- Properly categorizing clients based on their needs and status
- Tracking and reporting on marketing channel effectiveness

### Performance Benchmarks
- Template rendering must complete in under 100ms
- Email processing (retrieval, classification, filing) should handle 50+ emails per second
- Database operations should complete within 200ms
- Follow-up scheduling must handle 1000+ active sequences simultaneously
- The system should efficiently store and retrieve attachments for 500+ property listings

### Edge Cases and Error Conditions
- Handling malformed or spam emails
- Dealing with bounced emails or invalid addresses
- Managing template rendering when property data is incomplete
- Recovering from network interruptions during email operations
- Handling duplicate client records or property listings

### Required Test Coverage Metrics
- Minimum 90% code coverage across all modules
- 100% coverage of core email processing functions
- 100% coverage of template rendering system
- 100% coverage of client categorization logic
- Minimum 95% coverage of follow-up sequence engine

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

- All email templates render correctly with dynamic property data
- Client categorization accurately classifies test client data
- Follow-up sequences execute according to specified timelines
- Inquiry source tracking correctly identifies marketing channels
- Email organization properly files communications by property and client
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