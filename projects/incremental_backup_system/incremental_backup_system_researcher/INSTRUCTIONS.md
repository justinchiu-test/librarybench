# DataProvenance - Incremental Backup System with Research Integrity

## Overview
A specialized incremental backup system designed for academic researchers conducting computational experiments. The system enables preservation of both raw data and analysis scripts with comprehensive provenance tracking, ensuring reproducibility of scientific results while providing proper attribution and data lineage documentation for academic integrity.

## Persona Description
Dr. Rivera conducts computational research generating large datasets from experiments. He needs to preserve both raw data and analysis scripts with proper attribution and provenance tracking for academic integrity and reproducibility.

## Key Requirements
1. **Data Provenance Tracking**: Implement a comprehensive system that records and maintains the relationships between input data, analysis scripts, and output results throughout the backup process. This capability allows Dr. Rivera to establish clear lineage for all research artifacts, ensuring the origin and processing history of every data point can be traced for verification and reproducibility.

2. **Research Notebook Integration**: Create seamless integration with popular scientific notebook formats (Jupyter, R Markdown) that captures the context, parameters, and execution state of experiments at backup time. This feature ensures that Dr. Rivera's experimental procedures are preserved alongside the data they generate, maintaining the critical context needed for proper interpretation of results.

3. **Citation-ready Backup Snapshots**: Develop a mechanism for creating immutable, versioned snapshots with permanent identifiers that can be formally referenced in academic publications. This allows Dr. Rivera to cite specific versions of datasets and code in his papers, providing a transparent record for peer reviewers and other researchers to verify his work.

4. **Collaborative Backup Policies**: Implement a policy framework supporting secure sharing of backup sets with research team members while maintaining appropriate access controls and contribution tracking. This capability enables collaborative research while ensuring that individual contributions are properly attributed and protected against unauthorized modifications.

5. **Data Validation Framework**: Create comprehensive validation tools that verify the integrity and consistency of scientific datasets during backup and restoration operations. This feature helps Dr. Rivera ensure that his valuable research data remains uncorrupted throughout the backup lifecycle, preventing subtle errors that could invalidate research conclusions.

## Technical Requirements

### Testability Requirements
- All components must have isolated unit tests with dependency injection for external systems
- Provenance tracking must be tested with complex data transformation workflows
- Notebook integration must be tested with various notebook formats and execution states
- Citation snapshot mechanisms must verify immutability and identifier persistence
- Collaborative policy enforcement must be tested with simulated multi-user scenarios
- Data validation must be verifiable with datasets containing deliberate corruptions

### Performance Expectations
- The system must efficiently handle datasets up to 10TB with millions of individual files
- Provenance graph operations must complete in under 10 seconds for typical research workflows
- Notebook state capture must add less than 5 seconds overhead to backup operations
- Citation snapshot creation must complete within 30 seconds including all integrity checks
- Collaborative backup synchronization must process changes at a rate of at least 100MB/minute
- Validation operations must process at least 1GB of structured data per minute

### Integration Points
- Scientific notebook environments (Jupyter, RStudio)
- Data analysis libraries and frameworks (NumPy, Pandas, TensorFlow, etc.)
- Academic repository systems (Zenodo, Figshare, DataVerse)
- Workflow management systems (Snakemake, Nextflow, etc.)
- Institutional storage systems and HPC environments
- Metadata standards (DataCite, Dublin Core)

### Key Constraints
- The implementation must work across Linux, macOS, and Windows platforms
- All operations must maintain perfect data fidelity with no possibility of silent corruption
- The system must accommodate both very large files (instrument data) and large quantities of small files (analysis outputs)
- Storage formats must follow open standards for long-term archival value
- Provenance metadata must conform to established scientific standards where applicable
- System must operate efficiently in both high-performance computing environments and personal workstations

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The core of this implementation centers on a Python library that provides:

1. **Incremental Backup Engine**: A core module handling file change detection, efficient delta storage, and versioned backup creation with scientific data integrity preservation.

2. **Provenance Graph System**: A sophisticated tracking system that maintains directed acyclic graphs of data transformations, linking inputs through processing steps to outputs with full metadata.

3. **Notebook State Capture**: Specialized adapters for extracting, storing, and restoring the execution state, environment, and results of computational notebooks in various formats.

4. **Citation and Publication Framework**: Tools for creating immutable snapshots with permanent identifiers, verification checksums, and standardized citation metadata for academic publication.

5. **Collaboration Control System**: Logic for managing access controls, tracking contributions, and synchronizing backup sets across research team members while maintaining provenance integrity.

6. **Scientific Data Validator**: Advanced validation capabilities for various scientific data formats, ensuring integrity through checksumming, schema validation, and format-specific consistency checks.

The system should be designed as a collection of Python modules with clear interfaces between components, allowing them to be used independently or as an integrated solution. All functionality should be accessible through a programmatic API that could be called by various research tools (though implementing a UI is not part of this project).

## Testing Requirements

### Key Functionalities to Verify
- Provenance tracking with accurate relationship maintenance throughout backup operations
- Notebook integration with proper state preservation and restoration
- Citation snapshot creation with persistent identifiers and verification
- Collaborative backup policies with appropriate access controls
- Data validation with detection of various corruption scenarios
- Incremental backup efficiency for large scientific datasets

### Critical User Scenarios
- Complete research workflow from raw data acquisition through analysis to publication
- Collaborative project with multiple researchers contributing to shared datasets
- Reproduction of published results from archived snapshots
- Verification of data integrity after hardware failure or migration
- Tracing the lineage of a specific research finding back to source data
- Version comparison between different experimental approaches

### Performance Benchmarks
- Initial backup of a 1TB dataset completing in under 4 hours
- Incremental backup detecting and storing changes at 500MB/minute
- Provenance graph queries returning results in under 5 seconds for 10-step workflows
- Notebook state capture adding less than 3 seconds overhead per notebook
- Citation snapshot creation processing at least 50GB/hour including verification
- Validation operations detecting corruption with 99.9999% accuracy

### Edge Cases and Error Conditions
- Handling of corrupted research data with clear identification of affected results
- Recovery from interrupted backups during compute node failures
- Proper functioning with extremely large individual files (instrument data, simulation results)
- Correct behavior with complex nested provenance relationships
- Appropriate handling of binary data formats and proprietary scientific file types
- Graceful operation in restricted environments (air-gapped systems, limited permissions)

### Required Test Coverage Metrics
- Minimum 90% line coverage for all functional components
- 100% coverage of all public APIs
- All error handling paths must be explicitly tested
- Performance tests must verify all stated benchmarks
- Integration tests must verify all external system interfaces

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

1. All five key requirements are fully implemented and pass their respective test cases.
2. The system demonstrates comprehensive provenance tracking across complex research workflows.
3. Integration with at least one notebook format preserves execution state and results.
4. Citation snapshots can be created with proper metadata and verification mechanisms.
5. Collaborative policies correctly enforce access controls while tracking contributions.
6. Data validation successfully identifies various forms of corruption or inconsistency.
7. All performance benchmarks are met under the specified load conditions.
8. Code quality meets professional standards with appropriate documentation.

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Development Setup
1. Use `uv venv` to setup a virtual environment. From within the project directory, activate it with `source .venv/bin/activate`.
2. Install the project with `uv pip install -e .`
3. CRITICAL: Before submitting, run the tests with pytest-json-report:
   ```
   pip install pytest-json-report
   pytest --json-report --json-report-file=pytest_results.json
   ```
4. Verify that all tests pass and the pytest_results.json file has been generated.

REMINDER: Generating and providing the pytest_results.json file is a critical requirement for project completion.