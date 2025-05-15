# Nonprofit Impact Content Management System

## Overview
A specialized content management system designed for environmental nonprofit organizations to showcase impact stories, maintain event calendars, and coordinate volunteer activities. This system enables nonprofit coordinators to inspire community action while allowing multiple staff members to contribute content with minimal training.

## Persona Description
Jamal coordinates activities for a local environmental organization that needs to inspire community action and recruit volunteers. His primary goal is to showcase impact stories and maintain an active calendar of events while enabling multiple staff members to contribute content with minimal training.

## Key Requirements

1. **Campaign page templates with donation goal tracking**
   - Critical for Jamal to create compelling fundraising campaigns with clear goals and progress visualization
   - Must support multiple concurrent campaigns with different targets and timelines
   - Should include donation recording with progress metrics and milestone celebrations

2. **Volunteer opportunity database with signup workflow**
   - Essential for organizing volunteer activities and managing participant registration
   - Must track skills needed, time commitments, locations, and capacity limits
   - Should include volunteer hour logging and recognition system

3. **Impact visualization tools showing project outcomes**
   - Important for demonstrating the organization's effectiveness to supporters and stakeholders
   - Must convert raw data (trees planted, waste collected, emissions reduced) into compelling visual narratives
   - Should support before/after comparisons and progress over time

4. **Grant-specific reporting page generator**
   - Necessary for fulfilling reporting requirements to different funding organizations
   - Must organize project data according to various funders' specified formats
   - Should track grant deliverables against actual outcomes

5. **Newsletter template system with subscriber management**
   - Valuable for maintaining regular communication with supporters and volunteers
   - Must support content curation from website activities into newsletter format
   - Should include subscriber list management with interest-based segmentation

## Technical Requirements

### Testability Requirements
- All components must have unit tests with at least 85% code coverage
- Integration tests must verify campaign tracking data accuracy
- Performance tests must verify volunteer registration system under load
- Mock data system for testing visualization components

### Performance Expectations
- Campaign pages must load within 2 seconds regardless of donation volume
- Volunteer registration must process signups within 3 seconds
- Impact visualizations must render within 5 seconds with datasets of up to 10,000 points
- Newsletter generation must complete within 10 seconds regardless of content volume

### Integration Points
- Donation processing system integration for campaign tracking
- Calendar export for volunteer opportunities
- Data export for external grant reporting systems
- Email delivery service for newsletter distribution

### Key Constraints
- All personal volunteer data must be encrypted and handled according to privacy regulations
- System must work in low-bandwidth environments for field work
- Data visualizations must be accessible for screen readers
- Content editing must be possible for non-technical staff

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system must provide a Python library with the following core components:

1. **Campaign Management**
   - Campaign data models with goal tracking
   - Donation recording and progress calculation
   - Campaign timeline management
   - Outcome reporting and metrics

2. **Volunteer Coordination**
   - Opportunity definition and scheduling
   - Skill and requirement specification
   - Registration and capacity management
   - Hour tracking and recognition system

3. **Impact Reporting**
   - Data collection and validation
   - Metric calculation and aggregation
   - Visualization data preparation
   - Comparative analysis tools

4. **Grant Compliance**
   - Grant requirement specification
   - Project-to-grant mapping
   - Custom report generation
   - Deliverable tracking and verification

5. **Constituent Communication**
   - Subscriber list management
   - Content curation from website activities
   - Newsletter template system
   - Audience segmentation and targeting

## Testing Requirements

### Key Functionalities to Verify
- Campaigns correctly track donations and progress toward goals
- Volunteer system accurately manages registrations and prevents overbooking
- Impact visualizations correctly represent actual project data
- Grant reporting accurately compiles required information in specified formats
- Newsletter system properly curates content and manages subscriber lists

### Critical User Scenarios
- Creating a new fundraising campaign with specific goals and timeline
- Setting up a volunteer event with required skills and registration workflow
- Generating impact visualizations from project outcome data
- Preparing a grant report with project metrics and outcomes
- Creating and distributing a newsletter to segmented subscriber lists

### Performance Benchmarks
- System must support at least 50 concurrent campaign page views
- Volunteer registration must handle at least 100 simultaneous signups
- Impact visualization must process datasets with at least 10,000 data points
- Newsletter generation must support documents with at least 50 content elements

### Edge Cases and Error Conditions
- Handling campaign goal adjustments mid-campaign
- Managing volunteer cancellations and waitlist processing
- Dealing with incomplete or inconsistent impact data
- Adapting to changing grant reporting requirements
- Recovering from interrupted newsletter distribution

### Required Test Coverage Metrics
- Minimum 85% code coverage across all modules
- 100% coverage of donation calculation logic
- 100% coverage of volunteer registration workflows
- 100% coverage of data visualization preparation

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

1. The campaign system accurately tracks donations and progress toward goals
2. The volunteer system effectively manages opportunities and participant registration
3. The impact visualization system correctly represents project outcomes
4. The grant reporting system generates accurate reports in required formats
5. The newsletter system properly manages subscribers and content curation

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