# MailFlow for Real Estate - Property-Centric Email Management System

## Overview
A specialized email automation system tailored for real estate professionals that focuses on organizing communications by property listing, automating personalized responses to inquiries, and implementing strategic follow-up sequences to nurture leads through the property buying/selling lifecycle.

## Persona Description
Sofia manages listings and client communications for her independent real estate business, handling dozens of property inquiries daily. Her primary goal is to promptly respond to potential buyers and sellers with personalized information while automatically organizing communications by property and client status.

## Key Requirements

1. **Property Listing Template System**
   - Dynamic email templates with variable fields for different property types (residential, commercial, land)
   - Ability to insert property-specific data (price, square footage, amenities, photos) automatically
   - Support for formatting variations to highlight different property features
   - This feature is critical for Sofia to quickly respond to inquiries with accurate, professionally formatted property information without retyping details for each response.

2. **Automated Client Follow-up Sequences**
   - Time-based follow-up email scheduling triggered by specific client interactions
   - Customizable sequence patterns with different content based on client interest level
   - Ability to pause, modify or resume sequences based on client responses
   - This feature enables Sofia to maintain consistent communication with prospects without manually tracking when to send follow-ups, ensuring no potential client falls through the cracks during busy periods.

3. **Client Categorization System**
   - Categorization framework for classifying contacts (buyer/seller, price range, preferred neighborhoods)
   - Automatic tagging based on email content analysis
   - Analytics on client category distribution and conversion rates
   - This feature allows Sofia to quickly identify high-priority leads and tailor communications based on specific client needs and preferences.

4. **Property-Specific Email Organization**
   - Automatic threading and filing of emails by property listing ID
   - Attachment management system optimized for property photos and documents
   - Search functionality across property-specific communications
   - This feature helps Sofia maintain an organized record of all communications related to each property, ensuring she can quickly access the complete history of interactions about a specific listing.

5. **Inquiry Source Tracking**
   - Automated detection and tagging of lead sources from email content
   - Performance analytics comparing conversion rates across marketing channels
   - ROI calculation for different marketing initiatives
   - This feature enables Sofia to measure which marketing channels generate the most valuable leads, allowing her to optimize her marketing budget and strategy.

## Technical Requirements

### Testability Requirements
- All components must be testable without requiring actual email server connections
- Mock objects must be available for IMAP/SMTP services
- Template rendering must be testable with property data fixtures
- Client categorization algorithms must be testable with sample email content
- Follow-up sequence logic must be verifiable with time manipulation

### Performance Expectations
- Processing of new emails should complete within 5 seconds
- Template personalization and sending should complete within 2 seconds
- Search across property-related emails should return results within 3 seconds
- The system should handle up to 500 properties and 2000 clients without performance degradation
- Daily email volume of up to 200 incoming and 300 outgoing messages

### Integration Points
- IMAP and SMTP protocols for email server communication
- Local database for storing templates, rules, and client information
- File system for managing property attachments
- Optional calendar system integration for scheduling property viewings
- Export/import functionality for backup and migration

### Key Constraints
- Must work with standard email protocols (IMAP/SMTP)
- Must not require third-party email services or APIs that incur additional costs
- Must protect client privacy and comply with real estate communication regulations
- Must operate efficiently on standard hardware without requiring cloud resources
- All data must be stored locally with proper backup procedures

## Core Functionality

The system must provide:

1. **Email Processing Engine**
   - Connect to email accounts via IMAP
   - Process incoming messages with rule-based classification
   - Apply property and client identification algorithms
   - Organize conversations by property listing and client

2. **Template Management System**
   - Store and organize property listing templates
   - Support variable substitution for property details
   - Preview rendered templates before sending
   - Track template performance metrics

3. **Client Relationship Management**
   - Store client information and preferences
   - Track communication history by client
   - Categorize clients by type, stage, and preferences
   - Generate client interaction reports

4. **Follow-up Automation**
   - Define multi-stage follow-up sequences
   - Schedule follow-ups based on client interactions
   - Adjust sequences based on client responses
   - Track sequence completion and effectiveness

5. **Analytics and Reporting**
   - Track inquiry sources and conversion rates
   - Measure response times and communication patterns
   - Analyze property interest levels across client segments
   - Generate performance reports by marketing channel

## Testing Requirements

### Key Functionalities to Verify
- Email classification accuracy for different property inquiries
- Template rendering with various property types and details
- Follow-up sequence execution with correct timing
- Client categorization based on email content analysis
- Attachment management for property photos and documents

### Critical Scenarios to Test
- Processing a new property inquiry from different sources
- Generating appropriate responses to common question types
- Following up with a prospect through multiple stages
- Transitioning a client from buyer to seller or vice versa
- Handling multiple simultaneous inquiries about the same property

### Performance Benchmarks
- Email processing rate of at least 40 emails per minute
- Template personalization in under 500ms
- Search response time under 1 second for specific property queries
- System memory usage under 500MB with 1000 properties
- Database query performance with large datasets (10,000+ emails)

### Edge Cases and Error Conditions
- Handling malformed email structures
- Processing emails with missing expected information
- Dealing with bounced follow-up messages
- Managing duplicate property inquiries
- Recovering from interrupted follow-up sequences
- Handling very large attachments or unusual file formats

### Required Test Coverage
- Minimum 90% code coverage for core functionality
- 100% coverage of template rendering engine
- 100% coverage of client categorization logic
- 100% coverage of follow-up scheduling algorithms
- Comprehensive integration tests for email processing workflow

## Success Criteria

The implementation will be considered successful if it:

1. Reduces email response time by at least 75% for common property inquiries
2. Ensures 100% follow-up compliance with no missed client communications
3. Creates a fully searchable archive organized by property and client
4. Provides actionable analytics on marketing channel effectiveness
5. Accommodates at least 100 active property listings with associated communications
6. Enables Sofia to manage twice her current client volume without additional time investment
7. Successfully classifies at least 90% of incoming emails automatically
8. Reduces email management time by at least 15 hours per week

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