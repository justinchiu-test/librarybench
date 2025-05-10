# Scientific Research Media Metadata Management System

## Overview
A specialized metadata organization system for marine biology researchers that connects research media with scientific taxonomies, research protocols, geospatial data, and specimen tracking to facilitate scientific analysis and publication preparation.

## Persona Description
Dr. Patel conducts marine biology research generating thousands of underwater photographs and videos. She needs to organize research media with scientific metadata that connects to her study protocols and findings.

## Key Requirements
1. **Scientific taxonomy integration**: A system using standardized species classification systems. This feature is critical because it ensures all observations are properly categorized according to established scientific nomenclature, allowing for accurate species identification, consistent classification across studies, and seamless integration with global biodiversity databases.

2. **Research protocol linking**: Tools connecting media to specific experiments and methodologies. This feature is essential because it provides critical experimental context for each media item, documenting the exact research conditions, equipment configurations, and methodological parameters that influenced the captured data, which is fundamental for scientific reproducibility and validity.

3. **Geospatial habitat mapping**: Functionality placing observations within ecological contexts. This capability is vital because marine biology research is inherently spatial, and understanding the precise location and environmental context of observations allows for analysis of habitat preferences, species distributions, and ecological interactions across different marine environments.

4. **Specimen tracking**: A mechanism for associating multiple observations of the same individual organism. This feature is crucial because long-term studies of individual specimens provide valuable data on growth, behavior patterns, and life cycles, and the ability to link observations of the same individual across time creates powerful longitudinal datasets that reveal biological processes.

5. **Publication preparation**: Tools extracting appropriate media and metadata for journal submissions. This functionality is important because efficient preparation of research for publication is a core scientific activity, and automated extraction of publication-ready media with properly formatted metadata significantly reduces the time required to prepare manuscripts while ensuring all scholarly requirements are met.

## Technical Requirements
- **Testability requirements**:
  - All taxonomy integration functions must be independently testable
  - Protocol linking must be verifiable with sample research workflows
  - Geospatial mapping must be validated against known coordinates
  - Specimen tracking must maintain accurate relationships across observations
  - Publication extraction must comply with common journal requirements

- **Performance expectations**:
  - Process collections of up to 100,000 research media items
  - Handle high-resolution images and 4K video footage
  - Support complex metadata queries across multiple dimensions
  - Enable efficient batch processing of newly collected data
  - Optimize for both field use (limited connectivity) and lab analysis

- **Integration points**:
  - Standard scientific taxonomy databases (WoRMS, ITIS, GBIF)
  - Common research data formats (Darwin Core, EML)
  - Geospatial standards (GeoJSON, KML)
  - Citation management systems
  - Institutional repositories and data archives

- **Key constraints**:
  - Implementation must be in Python with no external UI components
  - Must preserve all raw data and metadata without alteration
  - Must handle both structured and unstructured scientific annotations
  - Must support offline operation for field research
  - Must comply with scientific data management best practices

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The system must provide comprehensive APIs for managing scientific research media:

1. **Taxonomic Classification Engine**: Implement standardized scientific classification systems. Map between taxonomic hierarchies. Validate species identifications against authoritative databases. Handle taxonomic revisions and nomenclature changes.

2. **Research Protocol Manager**: Define and document experimental protocols and methodologies. Link media to specific research activities and parameters. Track equipment configurations and calibration data. Maintain relationships between protocols and collected data.

3. **Geospatial Analysis Framework**: Process and standardize location data from various sources. Map observations to habitat types and environmental parameters. Support spatial queries and distribution analysis. Validate coordinate accuracy and precision.

4. **Specimen Identification System**: Create and manage individual specimen profiles. Link multiple observations of the same individual across time. Track morphological measurements and observed behaviors. Generate longitudinal datasets for individual specimens.

5. **Publication Asset Generator**: Extract research media according to journal requirements. Format metadata to scientific publication standards. Generate citation information and data availability statements. Prepare supplementary material packages.

## Testing Requirements
- **Key functionalities that must be verified**:
  - Accurate application of scientific taxonomies
  - Correct linking of media to research protocols
  - Precise geospatial mapping of observations
  - Reliable tracking of individual specimens across multiple observations
  - Proper extraction of publication-ready assets

- **Critical user scenarios that should be tested**:
  - Processing a new batch of field research media
  - Searching for all observations of a specific species
  - Analyzing the spatial distribution of observations
  - Tracking the developmental progression of an individual specimen
  - Preparing a complete set of media assets for journal submission

- **Performance benchmarks that must be met**:
  - Classify 10,000 observations according to taxonomy in under 10 minutes
  - Link 5,000 media items to research protocols in under 5 minutes
  - Process geospatial data for 10,000 observations in under 15 minutes
  - Generate publication assets for a complete study in under 20 minutes
  - Search across 100,000 items with complex criteria in under 30 seconds

- **Edge cases and error conditions that must be handled properly**:
  - Unidentified or newly discovered species
  - Media with missing or corrupted metadata
  - Uncertain or approximate geospatial coordinates
  - Ambiguous specimen identifications
  - Complex or non-standard research protocols
  - Conflicts between different taxonomic classification systems
  - Media collected with inconsistent methodologies

- **Required test coverage metrics**:
  - 95% code coverage for taxonomy integration functions
  - 90% coverage for protocol linking systems
  - 95% coverage for geospatial analysis features
  - 90% coverage for specimen tracking functionality
  - 90% coverage for publication preparation tools

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
The implementation will be considered successful if it meets the following criteria:

1. Demonstrates accurate integration with scientific taxonomic systems
2. Successfully links media to detailed research protocols with complete parameter documentation
3. Correctly maps observations to precise geospatial locations with habitat context
4. Reliably tracks individual specimens across multiple observations over time
5. Efficiently generates publication-ready assets that comply with scientific journal requirements
6. Passes all test cases with the required coverage metrics
7. Processes research collections efficiently within the performance benchmarks
8. Provides a well-documented API suitable for integration with scientific research workflows

## Project Setup
To set up the development environment:

1. Create a virtual environment and initialize the project using `uv`:
   ```
   uv init --lib
   ```

2. Install the necessary dependencies:
   ```
   uv sync
   ```

3. Run tests:
   ```
   uv run pytest
   ```

4. Run a specific test:
   ```
   uv run pytest path/to/test.py::test_function_name
   ```

5. Format the code:
   ```
   uv run ruff format
   ```

6. Lint the code:
   ```
   uv run ruff check .
   ```

7. Type check:
   ```
   uv run pyright
   ```

8. Run a Python script:
   ```
   uv run python script.py
   ```