# Academic Research Group Site Generator

A specialized static site generator for academic research groups to showcase publications, team members, datasets, and ongoing research projects in a structured, citation-friendly format.

## Overview

This project is a Python library for generating comprehensive academic research group websites from structured content sources. It focuses on scholarly content presentation, publication management, team profiles, and research asset organization specifically tailored for scientific communication.

## Persona Description

Dr. Chen leads an academic research group and needs to maintain a site showcasing the team's publications, ongoing projects, team members, and resources for the scientific community.

## Key Requirements

1. **Publication Database with Citation Support**: Implement a system to manage and display academic publications with BibTeX support and automatic citation formatting. This feature is essential for Dr. Chen's research visibility, allowing the group to maintain a comprehensive, searchable database of their scholarly output with properly formatted citations that colleagues can easily import into reference management software.

2. **Team Member Profile Management**: Create a system for maintaining detailed researcher profiles with academic backgrounds, research interests, publications, and contact information. This helps Dr. Chen showcase the expertise of team members, creating professional online presences for researchers at different career stages while demonstrating the collective strength and diversity of the research group.

3. **Dataset Repository System**: Develop a framework for presenting research datasets with comprehensive metadata, usage instructions, and citation information. As data sharing becomes increasingly important in academia, this feature allows Dr. Chen's group to make their research data discoverable and reusable while ensuring proper attribution through standardized citations.

4. **Research Timeline Visualization**: Implement a system to generate visual timelines showing project progression, key milestones, and research outputs. This visualization helps Dr. Chen demonstrate the group's research trajectory and achievements to potential collaborators, funding agencies, and students, contextualizing individual publications within broader research narratives.

5. **Academic Event Management**: Create a system for promoting upcoming academic events (conferences, workshops, seminars) with integrated calendar functionality. This allows Dr. Chen to highlight the group's engagement with the broader academic community, promote events they're organizing, and showcase their participation in important conferences relevant to their field.

## Technical Requirements

- **Testability Requirements**:
  - Publication database must correctly parse and format different citation styles
  - Team profile generation must be consistent across various profile types
  - Dataset repository must validate required metadata fields
  - Timeline visualization must accurately represent chronological relationships
  - Event calendar must handle various date formats and time zones

- **Performance Expectations**:
  - Full site generation must complete in under 1 minute for sites with up to 200 publications
  - BibTeX parsing and citation formatting should process 500+ entries in under 5 seconds
  - Publication search functionality should return results in under 100ms
  - Timeline generation should handle projects spanning multiple years efficiently
  - Resource downloads (papers, datasets) should be optimized for size

- **Integration Points**:
  - Citation management systems (BibTeX, DOI, ORCID)
  - Academic identifiers and repositories (arXiv, DBLP, Google Scholar)
  - Calendar standards (iCal) for event management
  - Visualization libraries for timelines and publication networks
  - Repository linking for code and data (GitHub, Zenodo, Dataverse)

- **Key Constraints**:
  - All citation formatting must follow established academic standards
  - Publication data must be easily updatable by non-technical users
  - Site must be accessible according to WCAG 2.1 AA standards
  - All content must be printable with appropriate formatting
  - Generated site must function with JavaScript disabled for core content

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The core functionality must include:

1. **Academic Publication Management**:
   - Parse BibTeX and other citation formats
   - Generate correctly formatted citations in multiple styles
   - Create filterable, searchable publication listings
   - Support for different publication types (journal articles, conference papers, books, etc.)
   - Export capabilities for reference management systems

2. **Research Team Management**:
   - Process structured researcher profile information
   - Generate consistent member profile pages
   - Support hierarchical organization (professors, postdocs, students)
   - Link researchers to their publications and projects
   - Showcase collaboration networks

3. **Research Data Repository**:
   - Manage dataset metadata in standardized formats
   - Generate download packages with appropriate documentation
   - Create citation information for datasets
   - Track dataset usage and versions
   - Link datasets to corresponding publications

4. **Research Visualization Framework**:
   - Generate chronological project timelines
   - Visualize research relationships and themes
   - Create publication impact visualizations
   - Display funding and project relationships
   - Show research evolution over time

5. **Academic Event System**:
   - Manage event information with standardized metadata
   - Generate event listings with filtering capabilities
   - Create calendar exports in standard formats
   - Archive past events with materials and outcomes
   - Support recurring academic events

## Testing Requirements

- **Key Functionalities to Verify**:
  - Accurate parsing and formatting of publication citations
  - Correct generation of researcher profiles with all components
  - Proper dataset representation with complete metadata
  - Accurate timeline visualization with correct chronology
  - Functional event calendar with proper date handling

- **Critical User Scenarios**:
  - Research group adds new publications and updates existing ones
  - New team members are added with their profiles and publications
  - Datasets are published with appropriate documentation and citation information
  - Research projects are visualized across multiple years with milestones
  - Academic events are added to the calendar and exported to standard formats

- **Performance Benchmarks**:
  - Publication database performance with various collection sizes (50, 200, 500 publications)
  - Search and filtering response time for publication database
  - Generation time for complex visualizations
  - Processing time for large BibTeX files
  - Overall build time for sites of different complexity

- **Edge Cases and Error Conditions**:
  - Handling of malformed BibTeX entries
  - Management of special characters in academic names and titles
  - Processing of datasets with unusual or incomplete metadata
  - Visualization of projects with overlapping or uncertain dates
  - Handling of international events across multiple time zones

- **Required Test Coverage**:
  - 95% code coverage for citation parsing and formatting
  - 90% coverage for profile generation
  - 90% coverage for dataset repository functionality
  - 85% coverage for visualization generation
  - 90% coverage for event management

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

The implementation will be considered successful when:

1. Publications are correctly displayed with proper citation formatting and BibTeX export
2. Team member profiles showcase all relevant academic information
3. Datasets are presented with complete metadata and citation information
4. Research timelines visually represent project progression accurately
5. Academic events are properly displayed with calendar integration
6. All academic standards for citations and metadata are correctly implemented
7. All tests pass with at least 90% code coverage
8. The site generation process is efficient enough for regular updates by non-technical users

To set up your development environment:
```
uv venv
source .venv/bin/activate
```