# Academic Research Group Site Generator

A specialized static site generator optimized for academic research groups to showcase their work, team, publications, and resources.

## Overview

This project provides an academia-focused static site generator that enables research group coordinators to create and maintain websites showcasing the team's publications, ongoing projects, team members, and resources for the scientific community. The system automates the generation of research-appropriate layouts and features while maintaining academic integrity and standards.

## Persona Description

Dr. Chen leads an academic research group and needs to maintain a site showcasing the team's publications, ongoing projects, team members, and resources for the scientific community.

## Key Requirements

1. **Publication Database with Citation Support**: Manage and display academic publications with proper citation formats.
   - As the primary output of academic work, Dr. Chen's research group needs to showcase their publications with complete bibliographic information and proper citation support in multiple formats.
   - This feature must support BibTeX import, proper formatting according to various citation styles, and generation of citation snippets for easy reference.

2. **Team Member Profiles**: Create and maintain profiles for research group members.
   - Highlighting the expertise and contributions of team members is essential for establishing the group's credibility and facilitating collaboration.
   - The system should support structured profiles with research interests, publications, contact information, and academic affiliations, maintaining consistent formatting while allowing for personalization.

3. **Dataset Repository**: Manage and document research datasets for public access.
   - Sharing research data is increasingly important for transparency and reproducibility, so Dr. Chen needs to provide access to datasets with proper metadata.
   - This feature must support dataset documentation with metadata, usage instructions, licensing information, and proper citation guidance.

4. **Research Timeline Visualization**: Display project progression and research milestones.
   - To communicate the group's research narrative and progress, Dr. Chen needs visual representations of project timelines and milestones.
   - The system should generate interactive timelines showing research projects, publications, grants, and other significant events in the group's history.

5. **Academic Event Promotion**: Share information about conferences, workshops, and seminars.
   - Academic networking and dissemination happen through events, so Dr. Chen needs to promote conferences, workshops, and seminars organized by or relevant to the research group.
   - This feature must support structured event information with dates, locations, registration details, and integration with calendar systems.

## Technical Requirements

### Testability Requirements
- Publication management must be testable with sample BibTeX entries
- Profile generation must verify correct formatting and relationship to publications
- Dataset repository must validate metadata completeness and accessibility
- Timeline visualization must verify chronological accuracy and event relationships
- Event calendar must validate date handling and iCalendar compatibility

### Performance Expectations
- Complete site generation should finish in under 30 seconds for a typical research group site
- BibTeX processing should handle libraries with 1000+ entries in under 10 seconds
- Timeline generation should process 100+ research events in under 5 seconds
- Profile generation should handle 50+ team members with their relationships in under 10 seconds
- Dataset metadata validation should process 50+ datasets in under 5 seconds

### Integration Points
- BibTeX parsing and citation formatting libraries
- Academic identifier systems (ORCID, DOI, etc.)
- Calendar formats (iCalendar) for event export
- Visualization libraries for timeline generation
- Schema.org academic and dataset vocabularies

### Key Constraints
- Must operate without a database or server-side processing
- Must generate completely static output deployable to university web hosting
- Must adhere to academic standards for citations and metadata
- Must support accessibility requirements for educational institutions
- Must optimize for discoverability by academic search engines

## Core Functionality

The system should implement a comprehensive platform for academic research group websites:

1. **Publication Management System**
   - Parse and process BibTeX and other bibliographic formats
   - Generate formatted citations in multiple styles (APA, MLA, Chicago, etc.)
   - Create publication lists organized by year, type, or project
   - Support DOI linking and academic metrics integration

2. **Team Management**
   - Process structured team member information
   - Generate profile pages with academic history and contributions
   - Link team members to their publications and projects
   - Create organizational charts and research groups

3. **Dataset Documentation**
   - Process dataset metadata according to academic standards
   - Create dataset landing pages with usage instructions
   - Generate appropriate citations for datasets
   - Support versioning and update history for datasets

4. **Timeline Framework**
   - Parse chronological research events and milestones
   - Generate visual timelines with appropriate grouping
   - Create interactive navigation for exploring research history
   - Support filtering and focusing on specific projects or periods

5. **Academic Event System**
   - Process structured event information
   - Generate event listings with chronological ordering
   - Create calendar exports in standard formats
   - Support recurring events and registration information

## Testing Requirements

### Key Functionalities to Verify
- BibTeX parsing and citation generation in multiple formats
- Team member profile generation with publication links
- Dataset metadata validation and landing page creation
- Timeline visualization with proper chronological ordering
- Academic event formatting and calendar integration

### Critical User Scenarios
- Adding new publications to the research group's bibliography
- Creating and updating team member profiles
- Publishing a new research dataset with complete metadata
- Adding milestones to the research group's timeline
- Creating and promoting academic events

### Performance Benchmarks
- Process 1000 BibTeX entries in under 10 seconds
- Generate 50 team member profiles with publication links in under 10 seconds
- Validate and process 50 datasets with metadata in under 5 seconds
- Generate a timeline with 100 research events in under 5 seconds
- Complete full site generation for a typical research group in under 30 seconds

### Edge Cases and Error Conditions
- Handling incomplete or malformed BibTeX entries
- Managing team members with missing information
- Processing datasets with complex licensing or access restrictions
- Dealing with overlapping or conflicting timeline events
- Handling event date ranges and recurrence patterns

### Required Test Coverage Metrics
- Minimum 90% line coverage for core processing components
- 100% coverage for citation formatting functionality
- Integration tests for all bibliographic processing
- Validation tests for dataset metadata
- Performance tests for bibliography and timeline generation

## Success Criteria

The implementation will be considered successful if it:

1. Correctly imports and formats bibliographic information from BibTeX files with support for at least 3 major citation styles
2. Generates comprehensive team member profiles with accurate publication lists and research interests
3. Creates properly documented dataset repositories with complete metadata and citation information
4. Produces clear, interactive research timelines showing project progression and key milestones
5. Effectively promotes academic events with calendar integration and appropriate details
6. Processes a typical research group site (200 publications, 30 team members, 20 datasets) in under 30 seconds
7. Achieves all required test coverage metrics with a clean test suite

## Getting Started

To set up the development environment:

1. Initialize the project using `uv init --lib` in your project directory
2. Install dependencies using `uv sync`
3. Run Python scripts with `uv run python your_script.py`
4. Run tests with `uv run pytest`

When implementing this library, focus on creating well-defined APIs that provide all the required functionality without any user interface components. All features should be implementable as pure Python modules and classes that can be thoroughly tested using pytest.