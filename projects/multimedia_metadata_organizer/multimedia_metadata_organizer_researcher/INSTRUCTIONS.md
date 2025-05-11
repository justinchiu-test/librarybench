# Scientific Research Media Metadata Management System

## Overview
A specialized metadata organization system for scientific researchers who need to manage thousands of research media files with detailed scientific metadata that connects to study protocols and research findings.

## Persona Description
Dr. Patel conducts marine biology research generating thousands of underwater photographs and videos. She needs to organize research media with scientific metadata that connects to her study protocols and findings.

## Key Requirements
1. **Scientific taxonomy integration**: Implement functionality to use standardized species classification systems and scientific naming conventions. This is essential for maintaining consistent and accurate identification of organisms across research media and enabling integration with broader scientific databases.

2. **Research protocol linking**: Create a system to connect media to specific experiments, methodologies, and research phases. This provides crucial context for understanding the conditions under which observations were made and ensures proper experimental control tracking.

3. **Geospatial habitat mapping**: Develop tools to place observations within ecological contexts using precise geographic coordinates and habitat classification. This enables spatial analysis of species distribution and environmental factors across research sites.

4. **Specimen tracking**: Build functionality to associate multiple observations of the same individual organism across different times or conditions. This is critical for longitudinal studies tracking changes in specific organisms over time.

5. **Publication preparation**: Create mechanisms to extract appropriate media and metadata for journal submissions, following specific publication requirements and formats. This streamlines the process of preparing visual evidence for scientific publications and ensures all required metadata is included.

## Technical Requirements

### Testability Requirements
- All taxonomy and classification functions must be independently testable
- Geospatial functions must support precise coordinate validation
- Use test fixtures with sample scientific metadata and classification hierarchies
- Support simulation of data collection across multiple research protocols

### Performance Expectations
- Process metadata for at least 1,000 research images per minute
- Support research collections with up to 500,000 items
- Geospatial queries should complete in under 3 seconds
- Support batch operations for publication preparation

### Integration Points
- Common image and video formats used in scientific research
- Standard scientific taxonomy databases (e.g., Integrated Taxonomic Information System)
- Geographic information systems and coordinate standards
- Research information management systems
- Academic publication formats and requirements

### Key Constraints
- No UI components - all functionality exposed through Python APIs
- All operations must maintain scientific accuracy and precision
- System must support both online and offline field research scenarios
- Data structures must accommodate evolving scientific classification systems

## Core Functionality

The system must provide a Python library that enables:

1. **Scientific Metadata Management**
   - Implement standard scientific taxonomies for species classification
   - Support custom research-specific metadata fields
   - Validate scientific naming and classification accuracy

2. **Research Context Integration**
   - Link media to research protocols and methodologies
   - Track experimental conditions and parameters
   - Maintain relationships between observations and hypotheses

3. **Geospatial Analysis**
   - Extract and normalize geographic coordinates from various formats
   - Classify and map habitat types and environmental conditions
   - Support spatial querying of research observations

4. **Specimen and Subject Tracking**
   - Identify and associate observations of the same individual
   - Track changes in subjects over time or experimental conditions
   - Support measurement and morphological data association

5. **Academic Output Preparation**
   - Filter and select media based on research criteria
   - Format metadata according to publication requirements
   - Generate appropriate citations and attributions

## Testing Requirements

The implementation must include tests that verify:

1. **Taxonomy Implementation**
   - Test correct implementation of scientific classification hierarchies
   - Verify handling of taxonomic revisions and updates
   - Test search and filtering by taxonomic criteria

2. **Research Protocol Integration**
   - Test linking of media to specific research protocols
   - Verify tracking of experimental conditions
   - Test filtering and organization by research parameters

3. **Geospatial Functionality**
   - Test coordinate extraction and normalization
   - Verify habitat classification and mapping
   - Test spatial queries and proximity analysis

4. **Specimen Tracking**
   - Test association of observations across time and conditions
   - Verify identification of the same individual in different media
   - Test longitudinal analysis of individual subjects

5. **Publication Workflows**
   - Test extraction of media for publication
   - Verify formatting of metadata for academic requirements
   - Test generation of figure sets and supplementary materials

**IMPORTANT:**
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

## Setup Instructions
1. Set up a virtual environment using `uv venv`
2. Activate the environment: `source .venv/bin/activate`
3. Install the project: `uv pip install -e .`

## Success Criteria

The implementation will be considered successful if:

1. All five key requirements are fully implemented
2. The system correctly implements and maintains scientific taxonomies
3. Research protocol linking successfully connects media to experimental contexts
4. Geospatial habitat mapping accurately places observations in ecological contexts
5. Specimen tracking correctly associates observations of the same individual
6. Publication preparation streamlines the creation of journal-ready materials
7. All operations maintain scientific accuracy and precision
8. All tests pass when run with pytest
9. A valid pytest_results.json file is generated showing all tests passing

**REMINDER: Generating and providing pytest_results.json is a CRITICAL requirement for project completion.**
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```