# MailFlow for Photography - Event-Centric Client Communication System

## Overview
A specialized email automation system tailored for event photographers that manages booking inquiries and availability, coordinates pre-event details, automates gallery delivery, tracks print sales opportunities, and schedules targeted promotions to optimize booking rates throughout the year.

## Persona Description
Elena photographs weddings and events, managing inquiries, bookings, and client galleries through email. Her primary goal is to streamline her booking process and client communications while ensuring timely delivery of photos and following up on sales opportunities.

## Key Requirements

1. **Booking Inquiry Management System**
   - Automated availability checking against existing calendar commitments
   - Package details and pricing information templates with dynamic content
   - Lead qualification and conversion tracking
   - This feature is critical for Elena to respond promptly to potential clients with accurate availability information, sending professionally formatted package details that match their specific event type, while efficiently tracking which inquiries convert to bookings.

2. **Event Countdown Communication System**
   - Automated pre-event communication sequences based on event date
   - Customizable questionnaire templates for collecting event details
   - Milestone-based planning reminders for both photographer and client
   - This feature ensures Elena maintains consistent client contact before events, collecting all necessary information through structured questionnaires while keeping clients informed about what to expect next, reducing last-minute questions and improving event preparation.

3. **Photo Gallery Delivery Automation**
   - Scheduled delivery notifications with personalized gallery access information
   - Tracking of client gallery access and viewing patterns
   - Automated client viewing reminders for unused gallery links
   - This feature streamlines the crucial post-event workflow of delivering final images, ensuring clients receive their galleries on schedule with proper access instructions while monitoring engagement to identify clients who may need additional follow-up.

4. **Print Sales Follow-up System**
   - Automated follow-up sequences based on gallery engagement metrics
   - Product suggestion templates tailored to event type and client activity
   - Order tracking and fulfillment communication
   - This feature allows Elena to maximize print sales opportunities by targeting clients at optimal times based on their viewing patterns, recommending appropriate products for their specific event type, and following through with order status updates.

5. **Seasonal Promotion Scheduling System**
   - Targeted campaign management for booking slow-season dates
   - Past client re-engagement sequences for annual events or referrals
   - Performance tracking for different promotion types
   - This feature helps Elena maintain consistent booking rates throughout the year by strategically targeting past clients and prospects with seasonal promotions, focusing marketing efforts on typically slower booking periods and tracking which promotions generate the best results.

## Technical Requirements

### Testability Requirements
- All components must be testable without requiring actual email server connections
- Mock objects must be available for IMAP/SMTP services and calendar integration
- Event management system must be testable with sample booking data
- Gallery delivery must be verifiable with test notification sequences
- Campaign targeting must be testable with sample client segments

### Performance Expectations
- Processing of new inquiry emails should complete within 3 seconds
- Template personalization and sending should complete within 1 second
- Availability checking against calendar should complete within 2 seconds
- The system should handle up to 200 events per year and 1000 client contacts
- Batch operations (e.g., gallery announcements) should process at least 50 emails per minute

### Integration Points
- IMAP and SMTP protocols for email server connections
- Local database for storing client information, event details, and communication history
- Calendar system integration for availability checking
- File system for managing email attachments and templates
- Optional integration with gallery hosting platforms for access tracking

### Key Constraints
- Must work with standard email protocols (IMAP/SMTP)
- Must not require third-party services or APIs that incur additional costs
- Must protect client privacy and image access information
- Must operate efficiently on standard hardware without requiring cloud resources
- All data must be stored locally with proper backup procedures
- Must accommodate working with large image collections and gallery links

## Core Functionality

The system must provide:

1. **Booking Management System**
   - Process incoming inquiries with date availability verification
   - Generate appropriate package information based on event type
   - Track inquiry-to-booking conversion through the sales pipeline
   - Maintain comprehensive booking calendar integration

2. **Event Preparation Workflow**
   - Manage pre-event communication sequences with timing rules
   - Generate and track questionnaire completion
   - Provide milestone notifications based on event proximity
   - Store event-specific details for reference

3. **Gallery Delivery System**
   - Schedule and send gallery delivery communications
   - Track client access and viewing activity
   - Generate reminders for unwatched galleries
   - Monitor delivery status and client satisfaction

4. **Sales Opportunity Management**
   - Identify optimal timing for print product suggestions
   - Generate personalized product recommendations
   - Track order status and fulfillment communications
   - Calculate conversion rates for different approaches

5. **Marketing Campaign Engine**
   - Schedule seasonal promotions based on booking patterns
   - Target specific client segments for different promotions
   - Track campaign performance and booking results
   - Optimize timing for maximum conversion

## Testing Requirements

### Key Functionalities to Verify
- Availability checking accuracy against existing bookings
- Event countdown sequence execution with correct timing
- Gallery delivery notification generation and tracking
- Print sales opportunity identification based on viewing patterns
- Seasonal promotion targeting accuracy

### Critical Scenarios to Test
- Processing a new booking inquiry with date checking
- Managing the complete pre-event communication sequence
- Delivering gallery access with subsequent engagement tracking
- Following up on print sales opportunities based on viewing activity
- Executing a seasonal promotion campaign to past clients

### Performance Benchmarks
- Inquiry response generation within 1 second of receipt
- Calendar availability checking in under 500ms
- Batch delivery of gallery notifications to 50 clients in under 2 minutes
- System memory usage under 300MB with 200 annual events
- Database query performance with large client datasets (1,000+ contacts)

### Edge Cases and Error Conditions
- Handling multiple inquiries for the same date
- Processing changes to event dates after questionnaires completed
- Managing gallery delivery failures or access issues
- Dealing with undeliverable emails or bounces
- Recovering from interrupted marketing campaigns
- Handling event cancellations at various stages of the workflow

### Required Test Coverage
- Minimum 90% code coverage for core functionality
- 100% coverage of availability checking algorithms
- 100% coverage of event countdown sequence logic
- 100% coverage of gallery access tracking
- Comprehensive integration tests for end-to-end booking workflow

## Success Criteria

The implementation will be considered successful if it:

1. Reduces inquiry response time to under 10 minutes during business hours
2. Increases booking conversion rate by at least 25%
3. Ensures 100% of clients receive proper pre-event questionnaires and information
4. Delivers all galleries on schedule with 99% successful client access rate
5. Increases print sales conversion by at least 30%
6. Reduces booking seasonality by at least 40% through targeted promotions
7. Decreases administrative time spent on routine communications by 20 hours per week
8. Maintains comprehensive communication records for all client interactions

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