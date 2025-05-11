# Academic Research Group Site Generator

A specialized static site generator designed for academic research groups to showcase publications, team members, datasets, ongoing projects, and research timelines.

## Overview

This project implements a Python library for generating comprehensive academic research group websites. It focuses on the needs of research group coordinators who want to maintain an up-to-date online presence showcasing their team's scientific contributions, ongoing projects, and resources for the academic community.

## Persona Description

Dr. Chen leads an academic research group and needs to maintain a site showcasing the team's publications, ongoing projects, team members, and resources for the scientific community.

## Key Requirements

1. **Publication Database with Citation Support**: Create a comprehensive system for managing academic publications with BibTeX/citation support and proper academic formatting.
   - Critical for Dr. Chen because publications are the primary output of academic work, and proper citation formatting is essential for academic credibility and discovery.
   - Must support various citation formats and generate properly formatted references that other researchers can easily cite.

2. **Team Member Profiles**: Implement detailed profiles for research team members with research interests, publications, and contact information.
   - Essential for Dr. Chen because showcasing team members helps establish credibility, facilitates collaboration, and helps recruit talented researchers.
   - Should present each researcher's expertise, contributions, and role within the group.

3. **Dataset Repository**: Develop functionality for hosting and documenting research datasets with metadata, usage instructions, and proper citation information.
   - Important for Dr. Chen because datasets are valuable research outputs that need proper documentation and attribution when used by others.
   - Must include structured metadata and clear documentation for data reuse.

4. **Research Timeline Visualization**: Create a system for visualizing the progression and milestones of research projects over time.
   - Valuable for Dr. Chen because it helps demonstrate research continuity, progression, and planning for grant applications and stakeholder reports.
   - Should clearly show project phases, milestones, and relationships between projects.

5. **Academic Event Promotion**: Implement functionality for promoting academic events with integrated calendars for conferences, workshops, and seminars.
   - Critical for Dr. Chen because academic events are key for disseminating research, networking, and establishing the group's presence in the field.
   - Must support recurring events, registration information, and archiving past events.

## Technical Requirements

### Testability Requirements
- All components must be individually testable through well-defined interfaces
- Support testing with sample publication databases and BibTeX files
- Test suites must validate citation formatting against academic standards
- Support snapshot testing for generated HTML output
- Validate timeline and calendar generation with comprehensive test datasets

### Performance Expectations
- Generate a complete research site with 200+ publications in under 30 seconds
- Publication database queries should return results in under 200ms
- Timeline generation should handle projects spanning 10+ years efficiently
- BibTeX parsing should process 500+ entries in under 5 seconds
- Generated sites should achieve 90+ scores on web performance metrics (to be simulated in tests)

### Integration Points
- BibTeX parsers and citation formatting libraries
- Calendar/event standardized formats (iCal, etc.)
- DOI and academic identifier resolution services
- Data repositories and metadata standards
- Academic search indexing services

### Key Constraints
- IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.
- Must comply with academic publishing standards and citation formats
- Must generate accessible content compliant with academic institution requirements
- Output must facilitate discovery by academic search engines
- Data repository must follow FAIR principles (Findable, Accessible, Interoperable, Reusable)
- Must support internationalization for global academic collaboration

## Core Functionality

The Academic Research Group Site Generator should provide a comprehensive Python library with the following core capabilities:

1. **Publication Management System**
   - Parse and process BibTeX and other bibliographic formats
   - Generate formatted citations in multiple styles (APA, MLA, Chicago, etc.)
   - Implement publication filtering and searching by various criteria
   - Create publication lists by author, year, type, project, etc.
   - Support for DOI linking and academic repository integration
   - Generate publication metrics and visualizations

2. **Team Management**
   - Process researcher profiles with academic information
   - Link researchers to their publications and projects
   - Support for academic affiliations and positions
   - Generate contact information with proper formatting
   - Implement research interest categorization
   - Create network visualizations of collaborations

3. **Dataset Documentation**
   - Process dataset metadata and documentation
   - Generate standardized dataset landing pages
   - Implement citation generation for datasets
   - Support for dataset versioning and updates
   - Create usage examples and documentation
   - Generate data dictionaries and schema documentation

4. **Research Timeline System**
   - Process project timelines and milestones
   - Generate timeline visualizations with appropriate granularity
   - Implement relationship mapping between projects
   - Support for funding periods and deliverables
   - Create progress indicators and status updates
   - Generate reports for specific time periods

5. **Academic Event Management**
   - Process event information and schedules
   - Generate calendar feeds in standard formats
   - Implement event categorization and filtering
   - Support for recurring events and series
   - Create archives of past events with materials
   - Generate registration and participation information

## Testing Requirements

### Key Functionalities to Verify

1. **Publication Processing and Display**
   - Test BibTeX parsing and validation
   - Verify citation formatting in various styles
   - Test publication filtering and grouping
   - Confirm proper handling of special characters in academic content
   - Verify DOI resolution and external linking
   - Test publication metrics calculations

2. **Team Member Management**
   - Test profile generation with various academic roles
   - Verify linking between researchers and their publications
   - Test sorting and filtering of team members
   - Confirm proper handling of international names and affiliations
   - Verify contact information formatting and protection

3. **Dataset Repository**
   - Test dataset metadata extraction and validation
   - Verify generation of standardized dataset pages
   - Test citation generation for datasets
   - Confirm compliance with metadata standards
   - Verify versioning and update tracking

4. **Timeline Visualization**
   - Test timeline generation with complex project structures
   - Verify proper temporal ordering and relationships
   - Test milestone highlighting and progress tracking
   - Confirm proper handling of overlapping projects
   - Verify responsive timeline visualization

5. **Event Management**
   - Test event calendar generation and iCal feed creation
   - Verify recurring event handling and exception dates
   - Test time zone handling for international events
   - Confirm proper archiving of past events
   - Verify filtering and categorization of events

### Critical User Scenarios

1. Adding a new publication and seeing it correctly categorized and formatted
2. Updating a team member's profile and research interests
3. Publishing a new dataset with proper metadata and citation information
4. Creating a timeline of research project progression for a grant report
5. Scheduling and promoting an upcoming academic conference or workshop

### Performance Benchmarks

- Complete site build with 200+ publications should complete in under 30 seconds
- BibTeX processing should handle 1000+ entries in under 10 seconds
- Timeline generation should process 50+ research projects in under 5 seconds
- Dataset repository should handle 100+ datasets with full metadata in under 10 seconds
- Memory usage should not exceed 1GB for typical research group sites

### Edge Cases and Error Conditions

- Test handling of malformed BibTeX entries
- Verify proper error reporting for invalid publication metadata
- Test behavior with extremely long publication lists or author lists
- Verify graceful handling of special characters in academic titles
- Test with missing or incomplete team member information
- Validate behavior with complex timeline relationships and dependencies
- Test calendar generation with timezone edge cases

### Required Test Coverage Metrics

- Minimum 90% code coverage for core functionality
- 100% coverage for citation formatting and validation
- 100% coverage for dataset metadata processing
- Integration tests for the entire site generation pipeline
- Performance tests for both small and large research groups

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

The Academic Research Group Site Generator will be considered successful if it:

1. Correctly manages and displays academic publications with proper citation formatting
2. Creates comprehensive team member profiles linked to their research contributions
3. Effectively documents research datasets with proper metadata and citation information
4. Generates clear and informative research timelines showing project progression
5. Successfully promotes academic events with calendar integration
6. Builds research group sites efficiently with proper academic SEO
7. Produces accessible, standards-compliant HTML output
8. Facilitates discovery and citation of the group's research outputs

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