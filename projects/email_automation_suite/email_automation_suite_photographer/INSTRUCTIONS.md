# Photographer Email Automation Suite

## Overview
PhotoMail is a specialized email automation library designed for professional event photographers who need to manage client communications throughout the booking, event preparation, and photo delivery process. It enables streamlined management of inquiries, bookings, pre-event coordination, photo delivery, and print order opportunities, allowing photographers to maintain excellent client service while focusing on their creative work.

## Persona Description
Elena photographs weddings and events, managing inquiries, bookings, and client galleries through email. Her primary goal is to streamline her booking process and client communications while ensuring timely delivery of photos and following up on sales opportunities.

## Key Requirements

1. **Booking Inquiry Management System**
   - Process and categorize incoming booking inquiries
   - Check availability against existing bookings for requested dates
   - Generate appropriate responses with package information and pricing
   - This feature is critical because it enables quick, professional responses to potential clients, increasing booking conversion rates while accurately managing the photographer's calendar and preventing double-bookings

2. **Event Countdown Communication Sequence**
   - Create automated communication sequences leading up to booked events
   - Distribute pre-event questionnaires and collect essential event details
   - Send timely reminders about final payments and preparation information
   - This feature is essential because it ensures clients are well-prepared for their photo sessions, all necessary information is collected in advance, and the photographer has the details needed for successful event coverage

3. **Photo Gallery Delivery Automation**
   - Generate and send personalized gallery access information
   - Track when clients view their galleries for the first time
   - Monitor overall engagement with delivered photos
   - This feature is vital because it streamlines the delivery of final photos to clients, creates a professional delivery experience, and provides insights into how clients are engaging with their images

4. **Print Order Opportunity Follow-up System**
   - Create targeted follow-up sequences based on gallery engagement
   - Generate personalized product suggestions based on viewed images
   - Track conversion from gallery views to print orders
   - This feature is important because it increases post-delivery sales through timely, relevant follow-ups that are triggered by client behavior, maximizing the revenue potential of each client relationship

5. **Seasonal Promotion Scheduling**
   - Plan and schedule promotional campaigns for booking slow periods
   - Target appropriate client segments based on past booking patterns
   - Track campaign performance and booking conversions
   - This feature helps maintain consistent business throughout the year by proactively filling calendar gaps with targeted promotions to the right client segments at optimal times

## Technical Requirements

### Testability Requirements
- All email generation functions must be testable with mock client and booking data
- Calendar availability checking must be verifiable with test booking scenarios
- Event countdown sequence logic must be testable with simulated timelines
- Gallery engagement tracking must produce consistent results with test access data
- Campaign targeting must be testable with sample client segments

### Performance Expectations
- Inquiry processing should handle at least 50 inquiries per day efficiently
- Event communication sequences should manage at least 100 active events simultaneously
- Gallery delivery should process at least 20 full event galleries per day
- Client engagement tracking should monitor at least 500 active galleries
- The system should efficiently manage data for at least 1000 past and future clients

### Integration Points
- IMAP and SMTP libraries for email retrieval and sending
- Template engine for dynamic content generation
- SQLite or similar database for client and booking information
- Calendar system for availability management
- Basic analytics tools for engagement tracking

### Key Constraints
- All communications must maintain consistent brand voice and professional presentation
- Gallery delivery must handle sensitive access credentials securely
- The system must respect client privacy and data protection regulations
- Email sending must be rate-limited to prevent being flagged as spam
- The implementation must be economical in terms of computational resources

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The core of the Photographer Email Automation Suite should provide:

1. **Inquiry Management Module**
   - Processing incoming booking inquiries with automated parsing
   - Checking calendar availability for requested dates
   - Generating appropriate response templates with package information
   - Tracking inquiry status and follow-up requirements

2. **Booking Management System**
   - Handling booking confirmations and contract processes
   - Managing deposits and payment tracking
   - Creating event profiles with all relevant details
   - Supporting booking modifications and special requests

3. **Event Preparation Engine**
   - Orchestrating pre-event communication sequences
   - Distributing and collecting questionnaires and shot lists
   - Sending preparation guidelines and logistics information
   - Managing final confirmations before events

4. **Gallery Delivery System**
   - Creating and distributing gallery access credentials
   - Tracking client engagement with delivered photos
   - Monitoring download and viewing patterns
   - Supporting client selections and favorites

5. **Sales Opportunity Manager**
   - Identifying print and product opportunities based on engagement
   - Generating targeted follow-up communications
   - Managing promotional campaigns and special offers
   - Tracking conversion from gallery views to product orders

## Testing Requirements

### Key Functionalities to Verify
- Inquiry response generation with accurate availability information
- Event countdown sequence timing and content appropriateness
- Gallery delivery notification generation and tracking functionality
- Print opportunity follow-up based on engagement triggers
- Seasonal campaign targeting and delivery to appropriate segments

### Critical User Scenarios
- Processing a new booking inquiry with availability checking
- Managing communications for an upcoming event through the full countdown sequence
- Delivering a completed photo gallery and tracking client engagement
- Generating follow-up communications based on gallery viewing patterns
- Creating and sending targeted seasonal promotions to fill calendar gaps

### Performance Benchmarks
- Inquiry processing should complete within 200ms per inquiry
- Event sequence generation should handle 100+ simultaneous active events
- Gallery tracking should monitor engagement for at least 500 active galleries
- The system should efficiently process email for a business handling 200+ events per year
- Database operations should complete within 200ms for typical queries

### Edge Cases and Error Conditions
- Handling inquiries for dates with partial availability
- Managing rescheduled events and updated communication sequences
- Dealing with delivery failures or access issues with galleries
- Processing unusual engagement patterns that don't fit standard follow-up triggers
- Handling conflicts between automated promotions and existing bookings

### Required Test Coverage Metrics
- Minimum 90% code coverage across all modules
- 100% coverage of availability checking functions
- 100% coverage of event sequence generation logic
- 100% coverage of gallery engagement tracking
- Minimum 95% coverage of follow-up trigger conditions

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

- Booking inquiry responses are correctly generated with accurate availability information
- Event countdown sequences execute according to appropriate timelines
- Gallery delivery notifications are properly generated and engagement is accurately tracked
- Print opportunity follow-ups are triggered based on correct engagement patterns
- Seasonal promotions are appropriately targeted to relevant client segments
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