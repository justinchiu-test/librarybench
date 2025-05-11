# Genomic Data Processing Pipeline

## Overview
A specialized concurrent task scheduler designed for processing genomic sequencing data through complex analytical pipelines with stringent data integrity requirements. This system optimizes throughput on expensive sequencing equipment while ensuring data provenance, validation, and error recovery throughout all processing stages.

## Persona Description
Dr. Zhang processes genomic sequencing data through complex analytical pipelines with strict accuracy requirements. His primary goal is to ensure data integrity throughout processing while maximizing throughput on expensive sequencing equipment.

## Key Requirements

1. **Data Provenance Tracking System**
   - Implement comprehensive tracking of all data transformations and processing steps across the entire analysis pipeline
   - This feature is critical for Dr. Zhang as it enables verification of results, validation of methods, and compliance with scientific reproducibility standards
   - The system must record detailed metadata about each processing step, including software versions, parameters, and environmental conditions

2. **Pipeline Validation Framework**
   - Create a validation system that performs pre-execution integrity checks on data, dependencies, and configurations
   - This feature is essential for Dr. Zhang as it prevents costly errors by ensuring that pipelines are correctly configured and that input data meets quality standards before committing expensive computational resources
   - Must validate both structural correctness (formats, schemas) and domain-specific quality metrics

3. **Stage-Specific Error Handling**
   - Implement customizable error-handling strategies for different analysis stages based on their specific characteristics and requirements
   - This feature is crucial for Dr. Zhang as different genomic analysis steps have unique failure modes and recovery options that require specialized handling
   - Must support automatic retries, alternative processing paths, and graceful degradation depending on the stage

4. **Sample Priority Management**
   - Develop a priority adjustment system based on sample degradation timelines and other biological constraints
   - This feature is vital for Dr. Zhang as biological samples have varying stability periods after which they become unusable, requiring their processing to be prioritized accordingly
   - Must dynamically reorder tasks based on time-sensitive biological constraints

5. **Equipment Utilization Optimization**
   - Create a scheduling system that maximizes expensive sequencing equipment utilization while integrating with predictive maintenance information
   - This feature is important for Dr. Zhang as sequencing hardware represents a significant capital investment with maintenance requirements that must be factored into scheduling decisions
   - Must balance maximum throughput against equipment reliability and maintenance needs

## Technical Requirements

### Testability Requirements
- All components must be independently testable with clear interfaces
- System must support simulation of sequencing equipment and sample processing
- Test scenarios must verify data integrity throughout processing stages
- Test coverage should exceed 90% for all data handling and integrity verification components

### Performance Expectations
- Support for at least 50 concurrent sequencing and analysis pipelines
- Overhead for provenance tracking should not exceed 3% of total processing time
- Scheduling decisions must complete in under 100ms even with complex constraints
- System should achieve at least 95% equipment utilization during normal operations

### Integration Points
- Integration with common bioinformatics tools (BWA, GATK, Samtools)
- Support for standard genomic data formats (FASTQ, BAM, VCF)
- Interfaces for laboratory information management systems (LIMS)
- Compatibility with scientific workflow systems (Galaxy, Nextflow)

### Key Constraints
- IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.
- The system must maintain complete data provenance for regulatory compliance
- All operations must be fully auditable and reproducible
- Must operate in environments with strict data privacy requirements
- System must be resilient to failures while preserving data integrity

## Core Functionality

The Genomic Data Processing Pipeline must provide:

1. **Genomic Workflow Definition**
   - A declarative API for defining complex genomic analysis workflows with their dependencies
   - Support for specifying data quality requirements and validation criteria
   - Integration with standard bioinformatics tools and formats

2. **Data Integrity and Provenance**
   - Comprehensive tracking of all data transformations from raw sequencing to final results
   - Checksums and validation at each processing stage
   - Complete audit trail for regulatory compliance and research reproducibility

3. **Intelligent Resource Management**
   - Optimal scheduling of tasks to maximize equipment utilization
   - Priority-based resource allocation that accounts for sample degradation timelines
   - Integration with maintenance schedules to prevent processing interruptions

4. **Error Handling and Recovery**
   - Customizable error handling strategies for different pipeline stages
   - Automatic retries and fallback options for recoverable errors
   - Data preservation and safe states during failure conditions

5. **Performance Monitoring and Optimization**
   - Collection of detailed performance metrics for all pipeline components
   - Analysis of throughput and resource utilization patterns
   - Identification of bottlenecks and optimization opportunities

## Testing Requirements

### Key Functionalities to Verify
- Data provenance correctly tracks all processing steps and transformations
- Pipeline validation properly identifies configuration and data quality issues
- Error handling appropriately manages different failure types across pipeline stages
- Priority adjustments correctly account for sample degradation timelines
- Equipment utilization consistently meets or exceeds target thresholds

### Critical Scenarios to Test
- Processing of large genomic datasets through complete analysis pipelines
- Recovery from simulated hardware and software failures at various stages
- Management of multiple competing pipelines with different priority levels
- Handling of samples with imminent degradation deadlines
- Integration with scheduled equipment maintenance windows

### Performance Benchmarks
- Provenance tracking overhead should not exceed 3% of total processing time
- System should support at least 50 concurrent analysis pipelines
- Equipment utilization should exceed 95% during normal operations
- Validation checks should complete in under a minute for typical datasets

### Edge Cases and Error Conditions
- Handling of malformed or corrupted genomic data files
- Recovery from partial processing failures without data loss
- Correct behavior when equipment unexpectedly becomes unavailable
- Proper prioritization when multiple high-priority samples require processing
- Graceful degradation under extreme resource contention

### Required Test Coverage
- Minimum 90% line coverage for all data handling components
- Comprehensive integration tests for complete processing pipelines
- Performance tests simulating production-scale genomic analysis workflows
- Data integrity verification tests for all transformation operations

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

The implementation will be considered successful if:

1. Data provenance tracking captures all processing steps with complete metadata
2. Pipeline validation prevents execution of improperly configured workflows
3. Error handling strategies effectively manage different failure types
4. Sample prioritization correctly accounts for degradation timelines
5. Equipment utilization consistently exceeds 95% while respecting maintenance requirements

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Setup Instructions

1. Setup a virtual environment using UV:
   ```
   uv venv
   source .venv/bin/activate
   ```

2. Install the project in development mode:
   ```
   uv pip install -e .
   ```

3. CRITICAL: Run tests with pytest-json-report to generate pytest_results.json:
   ```
   pip install pytest-json-report
   pytest --json-report --json-report-file=pytest_results.json
   ```

REMINDER: Generating and providing pytest_results.json is a critical requirement for project completion.