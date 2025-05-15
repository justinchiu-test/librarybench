# Craft Brewery Content Management System

## Overview
A specialized content management system designed for craft breweries to showcase their story, current tap offerings, and upcoming events. This system enables brewery owners to frequently update beer descriptions and availability while building brand loyalty through an engaging content experience that reflects the brewery's unique personality.

## Persona Description
Carlos needs to showcase his brewery's story, current tap offerings, and upcoming events to beer enthusiasts. His primary goal is to frequently update beer descriptions and availability while building brand loyalty through an engaging content experience that reflects his brewery's unique personality.

## Key Requirements

1. **Product catalog with customizable attributes for beer characteristics**
   - Critical for Carlos to maintain detailed information about each beer, including style, ABV, IBU, ingredients, flavor notes, and brewing process
   - Must support custom attribute creation for unique characteristics of specialty beers
   - Should include versioning to track changes in recipes and batches over time

2. **Tap room status board with real-time availability updates**
   - Essential for keeping customers informed about what's currently pouring and how much remains
   - Must provide an easy updating mechanism for staff to adjust keg levels and availability
   - Should include integration options for digital display boards in the physical tap room

3. **Beer release countdown timers with notification signup**
   - Important for building anticipation and traffic for new beer releases and special batches
   - Must track multiple upcoming releases with configurable countdown displays
   - Should include a notification system for customers to receive alerts about specific releases

4. **Recipe and brewing process documentation templates**
   - Valuable for sharing brewing knowledge with the community and establishing craft credibility
   - Must support structured documentation of brewing processes with appropriate terminology
   - Should include appropriate level of detail while protecting proprietary brewing techniques

5. **Age verification system with regional compliance settings**
   - Necessary for legal compliance when displaying alcoholic product information
   - Must implement age verification appropriate to different jurisdictions
   - Should include content restriction controls based on verified age

## Technical Requirements

### Testability Requirements
- All components must have unit tests with at least 85% code coverage
- Integration tests must verify product catalog accuracy and tap status updates
- Performance tests must ensure real-time updates function under load
- Mock notification system for testing release countdown functionality

### Performance Expectations
- Tap status updates must propagate within 5 seconds
- Product catalog queries must complete within 200ms regardless of catalog size
- Notification processing must handle at least 100 subscriptions per second
- Age verification must complete within 1 second

### Integration Points
- Point-of-sale system for tap status synchronization
- Email/SMS gateway for release notifications
- Social media platforms for promotion sharing
- Digital signage systems for in-store displays

### Key Constraints
- Product information must be structured for both human and machine consumption (Untappd, BeerAdvocate)
- Age verification must comply with regulations in multiple jurisdictions
- Real-time status must be accurate across multiple access points
- System must function in the brewery environment (limited connectivity, high temperature/humidity)

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system must provide a Python library with the following core components:

1. **Beer Catalog Management**
   - Product data model with flexible attributes
   - Beer style classification system
   - Version control and batch tracking
   - Search and filtering capabilities

2. **Tap Room Inventory**
   - Real-time status tracking
   - Availability calculation and display
   - Staff update interface
   - Historical consumption analytics

3. **Release Management**
   - Event scheduling and countdown
   - Notification subscription handling
   - Audience targeting and segmentation
   - Release promotion automation

4. **Brewing Documentation**
   - Template system for process documentation
   - Ingredient management and tracking
   - Process visualization preparation
   - Public/private information control

5. **Compliance Management**
   - Age verification mechanisms
   - Regional regulation configuration
   - Access control based on verification
   - Audit logging for compliance verification

## Testing Requirements

### Key Functionalities to Verify
- Product catalog correctly stores and retrieves all beer attributes
- Tap status updates accurately reflect current availability
- Countdown system correctly tracks and notifies for upcoming releases
- Documentation system properly formats and protects brewing information
- Age verification correctly implements rules for different regions

### Critical User Scenarios
- Adding a new beer to the catalog with complete information
- Updating tap status during a busy service period
- Setting up a special release with countdown and notifications
- Documenting a new brewing process with appropriate detail levels
- Configuring regional compliance settings for distribution expansion

### Performance Benchmarks
- System must support catalog with at least 500 beer entries
- Tap status must handle at least 50 updates per hour
- Notification system must support at least 10,000 subscribers
- Age verification must process at least 100 verifications per minute

### Edge Cases and Error Conditions
- Handling conflicting tap status updates from multiple staff members
- Managing notification delivery failures and retries
- Dealing with incomplete product information
- Recovering from interrupted brewing documentation
- Handling age verification in undefined regulatory regions

### Required Test Coverage Metrics
- Minimum 85% code coverage across all modules
- 100% coverage of tap status update logic
- 100% coverage of age verification rules
- 100% coverage of notification dispatch

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

1. The product catalog effectively manages beer information with custom attributes
2. The tap status system accurately tracks and communicates current availability
3. The release countdown correctly manages dates and notifications
4. The documentation system properly structures brewing information
5. The age verification system correctly implements appropriate restrictions

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Development Setup

To set up the development environment:

1. Use `uv venv` to create a virtual environment
2. From within the project directory, activate the environment with `source .venv/bin/activate`
3. Install the project with `uv pip install -e .`

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```