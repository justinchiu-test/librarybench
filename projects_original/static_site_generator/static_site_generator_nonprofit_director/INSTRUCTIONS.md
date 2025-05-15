# Non-Profit Organization Site Generator

A specialized static site generator designed for non-profit organizations to create mission-driven websites showcasing their impact, programs, funding opportunities, and volunteer engagement with limited technical resources.

## Overview

This project implements a Python library for generating comprehensive non-profit organization websites that highlight mission, programs, impact stories, and engagement opportunities. It focuses on the needs of non-profit directors who need to maintain an effective online presence with limited technical resources while maximizing donor and volunteer engagement.

## Persona Description

Amara leads a small environmental non-profit and needs to maintain their organization's website with limited technical resources, showcasing their mission, programs, impact stories, and donation opportunities.

## Key Requirements

1. **Impact Story Templates**: Create a system for showcasing the organization's work through compelling narrative templates that highlight outcomes and impact with consistent formatting.
   - Critical for Amara because storytelling is essential for connecting donors and supporters to the organization's mission, and templates ensure consistency with minimal effort.
   - Must include support for multimedia elements, testimonials, and impact metrics.

2. **Donation Integration**: Implement functionality for generating static payment links and donation forms for various fundraising campaigns without requiring server-side infrastructure.
   - Essential for Amara because donations are the lifeblood of non-profit operations, but her organization lacks resources for complex payment processing systems.
   - Should integrate with third-party donation platforms while maintaining brand consistency.

3. **Volunteer Opportunity Management**: Create a system for promoting volunteer positions with detailed descriptions, requirements, and sign-up capabilities.
   - Important for Amara because volunteers provide critical support for the organization's programs, and effective recruitment requires clear, accessible information.
   - Must include scheduling, skill requirements, and simplified application processes.

4. **Event Promotion System**: Develop tools for showcasing upcoming events with registration links and automatic archiving of past events with materials and outcomes.
   - Valuable for Amara because events are key engagement opportunities, and proper promotion before and documentation after helps maximize their impact.
   - Should include countdown features, capacity tracking, and post-event reporting.

5. **Grant and Funding Information**: Create a structured way to organize and present grant and funding information by project with progress updates and impact reporting.
   - Critical for Amara because transparency in funding usage builds trust with donors and grantmakers, while organized information helps with reporting requirements.
   - Must support project breakdowns, milestone tracking, and outcome measurement.

## Technical Requirements

### Testability Requirements
- All components must be individually testable with clear interfaces
- Support snapshot testing for generated pages and templates
- Validate third-party integrations with mock services
- Test donation flows and volunteer sign-up processes
- Support testing with realistic non-profit content sets

### Performance Expectations
- Full site generation should complete in under 30 seconds for typical non-profit sites
- Image optimization should process impact story photos efficiently
- Event calendar generation should handle 100+ events in under 5 seconds
- Donation form integration should add minimal overhead to page loading
- Generated sites should achieve 90+ scores on web performance metrics (to be simulated in tests)

### Integration Points
- Third-party donation and payment processing platforms
- Volunteer management and sign-up services
- Event registration and ticketing systems
- Social media sharing and promotion
- Email newsletter sign-up services
- Impact measurement and tracking tools

### Key Constraints
- IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.
- Must generate completely static HTML that works without server-side processing
- Must work with limited technical resources and ease of maintenance
- Output must be accessible for all potential supporters
- Site performance must be optimized for various device types and connection speeds
- Design must accommodate frequent content updates by non-technical staff

## Core Functionality

The Non-Profit Organization Site Generator should provide a comprehensive Python library with the following core capabilities:

1. **Impact Storytelling System**
   - Process impact story data from structured formats
   - Generate narrative templates with proper formatting
   - Implement multimedia integration for stories
   - Create impact metrics visualizations
   - Support for testimonials and beneficiary voices
   - Generate story archives and categorization

2. **Donation Management**
   - Generate platform-agnostic donation forms
   - Implement integration with popular donation processors
   - Create campaign-specific donation flows
   - Support for suggested donation amounts
   - Implement recurring donation options
   - Generate donation impact visualizations

3. **Volunteer Engagement Tools**
   - Process volunteer opportunity information
   - Generate role descriptions and requirements
   - Implement sign-up form integration
   - Create volunteer recognition features
   - Support for volunteer hour tracking
   - Generate volunteer impact reporting

4. **Event System**
   - Process event data and schedules
   - Generate event promotional materials
   - Implement registration integration
   - Create event archives with materials
   - Support for recurring events and series
   - Generate event outcomes and impact reports

5. **Funding Transparency**
   - Process grant and funding information
   - Generate project-based funding breakdowns
   - Implement progress tracking and milestones
   - Create funding source acknowledgment
   - Support for impact reporting by project
   - Generate financial transparency visualizations

## Testing Requirements

### Key Functionalities to Verify

1. **Impact Story Generation**
   - Test impact story template generation
   - Verify multimedia integration in stories
   - Test impact metric visualization
   - Confirm proper formatting and layout
   - Verify story categorization and filtering
   - Test responsive design for various devices

2. **Donation System Integration**
   - Test donation form generation for various platforms
   - Verify third-party integration functionality
   - Test campaign-specific donation flows
   - Confirm secure handling of payment links
   - Verify donation impact visualization
   - Test integration with popular payment processors

3. **Volunteer Management**
   - Test volunteer opportunity listing generation
   - Verify sign-up form functionality
   - Test role description formatting
   - Confirm accessibility of volunteer information
   - Verify volunteer recognition features
   - Test scheduling and availability display

4. **Event Promotion**
   - Test event calendar and listing generation
   - Verify registration link functionality
   - Test event archiving process
   - Confirm proper event categorization
   - Verify countdown and timing features
   - Test event outcome reporting

5. **Funding Information**
   - Test project funding breakdown generation
   - Verify milestone and progress tracking
   - Test grant acknowledgment formatting
   - Confirm transparency visualization
   - Verify project-based reporting
   - Test financial information presentation

### Critical User Scenarios

1. Creating and publishing a new impact story with multimedia elements and metrics
2. Setting up a fundraising campaign with custom donation forms and progress tracking
3. Posting new volunteer opportunities with clear requirements and sign-up process
4. Promoting an upcoming event and later archiving it with outcome information
5. Reporting on grant usage with project milestones and impact measurements

### Performance Benchmarks

- Full site generation should complete in under 30 seconds for typical non-profit sites
- Image processing should optimize 50+ impact story images in under 15 seconds
- Donation form integration should add less than 200ms to page load times
- Event system should process 100+ events in under 5 seconds
- Memory usage should not exceed 500MB for typical non-profit sites

### Edge Cases and Error Conditions

- Test handling of missing impact metrics or incomplete stories
- Verify graceful degradation when third-party donation services are unavailable
- Test behavior with cancelled or rescheduled events
- Verify handling of volunteer opportunities with unusual requirements
- Test with incomplete funding information or missing grant details
- Validate behavior with large image files or unusual media formats

### Required Test Coverage Metrics

- Minimum 90% code coverage for core functionality
- 100% coverage for donation integration logic
- 100% coverage for volunteer management
- Integration tests for the entire site generation pipeline
- Performance tests for both small and large non-profit sites

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

The Non-Profit Organization Site Generator will be considered successful if it:

1. Creates compelling impact stories with proper formatting and multimedia support
2. Integrates donation options that work with third-party processors without server-side code
3. Effectively promotes volunteer opportunities with clear information and sign-up process
4. Successfully manages event promotion and archiving with registration capabilities
5. Presents funding and grant information with appropriate transparency and project tracking
6. Builds non-profit sites efficiently with proper organization and minimal technical overhead
7. Produces accessible, mobile-friendly HTML output
8. Enables non-technical staff to maintain and update content easily

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

### Development Environment Setup

To set up your development environment:

1. Create a virtual environment using UV:
   ```
   uv venv
   ```

2. Activate the virtual environment:
   ```
   source .venv/bin/activate
   ```

3. Install the project in development mode:
   ```
   uv pip install -e .
   ```

4. CRITICAL: When testing, you must generate the pytest_results.json file:
   ```
   pip install pytest-json-report
   pytest --json-report --json-report-file=pytest_results.json
   ```

This file is MANDATORY proof that all tests pass and must be included with your implementation.