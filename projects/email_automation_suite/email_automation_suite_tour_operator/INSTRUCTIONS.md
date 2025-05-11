# Tour Operator Email Automation Suite

## Overview
TourMail is a specialized email automation library designed for local tour operators who manage inquiries, bookings, pre-tour communications, and post-tour follow-ups for various tour packages. It enables efficient handling of availability requests, booking confirmations, group communications, customer feedback collection, and seasonal promotions, allowing tour operators to deliver exceptional customer service while maximizing bookings and customer satisfaction.

## Persona Description
Raj operates a local tour company handling bookings, inquiries, and guest communications for various tour packages. His primary goal is to convert inquiries into bookings through timely, informative responses while managing pre-tour communications and post-tour follow-ups.

## Key Requirements

1. **Tour Package Inquiry and Availability System**
   - Process incoming inquiries and automatically check availability for requested dates
   - Generate appropriate responses with tour package details and availability status
   - Track inquiry conversion rates and response times
   - This feature is critical because it enables prompt, accurate responses to potential customers, increasing booking conversion rates while preventing double-bookings and ensuring that tours operate at optimal capacity

2. **Booking Confirmation and Preparation Sequence**
   - Create multi-stage booking confirmation and preparation email sequences
   - Include dynamic content such as weather forecasts, preparation tips, and meeting instructions
   - Send timely reminders with increasing specificity as tour date approaches
   - This feature is essential because it ensures guests are well-prepared for their tour experience, reduces no-shows and cancellations, and addresses common questions before they arise, improving customer satisfaction and operational efficiency

3. **Group Communication Management Tools**
   - Implement tools for communicating with multiple guests per tour group
   - Support customized messaging to specific subgroups within tours
   - Maintain group communication history and tracking
   - This feature is vital because tour operators frequently need to communicate with entire groups or specific subsets of guests about logistics, changes, or special arrangements, requiring efficient group messaging capabilities that maintain personalization

4. **Post-tour Feedback Collection System**
   - Generate post-tour feedback requests with customized survey content
   - Implement automated review request sequences for popular review platforms
   - Track feedback submission status and follow up with non-responders
   - This feature is important because customer feedback drives service improvements and online reviews significantly impact future bookings, making systematic feedback collection crucial for business growth and reputation management

5. **Seasonal Promotion and Analytics System**
   - Schedule targeted promotional campaigns based on booking pattern analytics
   - Segment past customers and prospects for appropriate tour offerings
   - Track campaign performance metrics and optimize future promotions
   - This feature helps maintain consistent business throughout seasonal fluctuations by using data-driven insights to target the right audiences with appropriate tour promotions, optimizing marketing spend and maximizing booking rates during traditionally slower periods

## Technical Requirements

### Testability Requirements
- All email generation functions must be testable with mock tour and customer data
- Availability checking must be verifiable with test booking scenarios
- Group communication logic must be testable with simulated tour groups
- Feedback collection must produce consistent results with test submission data
- Promotion targeting must be verifiable with test customer segments

### Performance Expectations
- Inquiry response generation should complete in under 200ms per inquiry
- Tour capacity and availability checking should process in under 100ms
- Group communication should handle groups of at least 50 guests efficiently
- Feedback processing should handle at least 100 submissions per day
- The system should efficiently manage data for at least 500 tours per year

### Integration Points
- IMAP and SMTP libraries for email retrieval and sending
- Template engine for dynamic content generation
- SQLite or similar database for tour and customer information
- Basic weather API for tour preparation information
- Analytics tools for booking pattern analysis

### Key Constraints
- The system must function efficiently with limited internet connectivity at remote locations
- All communications must reflect the tour operator's brand and voice
- Customer data must be handled in compliance with privacy regulations
- Email sending must respect anti-spam regulations and sending limits
- The implementation must optimize for performance on modest computing hardware

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The core of the Tour Operator Email Automation Suite should provide:

1. **Inquiry Management Module**
   - Processing incoming tour inquiries with automated parsing
   - Checking tour availability and capacity for requested dates
   - Generating appropriate response templates with package information
   - Tracking inquiry status and conversion metrics

2. **Booking Management System**
   - Handling booking confirmations and payment processing
   - Creating customer profiles with relevant preferences and requirements
   - Managing tour rosters and capacity tracking
   - Supporting booking modifications and special requests

3. **Tour Preparation Engine**
   - Orchestrating pre-tour communication sequences
   - Integrating dynamic content such as weather forecasts
   - Sending preparation guidelines and logistics information
   - Managing final confirmations before tour dates

4. **Group Communication System**
   - Managing communications to entire tour groups
   - Supporting subgroup messaging for specific arrangements
   - Handling tour updates and last-minute changes
   - Maintaining communication history by tour and group

5. **Customer Feedback and Promotion Manager**
   - Creating and processing post-tour feedback requests
   - Generating review solicitations for appropriate platforms
   - Analyzing booking patterns for promotional opportunities
   - Managing seasonal campaigns and special offers

## Testing Requirements

### Key Functionalities to Verify
- Inquiry response generation with accurate availability information
- Booking confirmation and preparation sequence timing and content
- Group communication delivery to correct tour members
- Feedback collection and review request processing
- Promotional campaign targeting based on booking patterns

### Critical User Scenarios
- Processing a new tour inquiry with availability checking
- Managing a customer through the complete booking and preparation sequence
- Sending group communications to specific subsets of tour participants
- Collecting post-tour feedback and requesting online reviews
- Creating and sending targeted seasonal promotions

### Performance Benchmarks
- Inquiry processing should handle at least 100 inquiries per day
- Tour availability checking should complete in under 100ms per check
- Group communication should efficiently handle groups of 50+ guests
- Feedback collection should process at least 100 responses per day
- The system should efficiently manage data for a business handling 500+ tours annually

### Edge Cases and Error Conditions
- Handling inquiries for dates with partial or limited availability
- Managing tour cancellations and associated communication requirements
- Dealing with group communication where some members have undeliverable addresses
- Processing incomplete or ambiguous feedback submissions
- Handling seasonal anomalies that affect typical booking patterns

### Required Test Coverage Metrics
- Minimum 90% code coverage across all modules
- 100% coverage of availability checking functions
- 100% coverage of group communication logic
- 100% coverage of feedback collection processing
- Minimum 95% coverage of promotion targeting algorithms

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

- Tour inquiries receive accurate availability information in timely responses
- Booking confirmation and preparation sequences deliver appropriate content at the right times
- Group communications are correctly delivered to the appropriate tour participants
- Post-tour feedback is systematically collected and review requests are properly generated
- Promotional campaigns are effectively targeted based on accurate booking pattern analysis
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