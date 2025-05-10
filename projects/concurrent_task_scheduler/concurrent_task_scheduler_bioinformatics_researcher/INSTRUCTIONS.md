# Genomic Data Processing Pipeline Scheduler

A concurrent task scheduler optimized for genomic sequencing analysis with data integrity assurance and equipment utilization optimization.

## Overview

The Genomic Data Processing Pipeline Scheduler is a specialized task execution framework designed for managing complex bioinformatics workflows. It provides robust data provenance tracking, pipeline validation, customizable error handling, priority adjustments based on biological constraints, and equipment utilization optimization to ensure maximum throughput for expensive sequencing equipment while maintaining strict data integrity requirements.

## Persona Description

Dr. Zhang processes genomic sequencing data through complex analytical pipelines with strict accuracy requirements. His primary goal is to ensure data integrity throughout processing while maximizing throughput on expensive sequencing equipment.

## Key Requirements

1. **Data Provenance Tracking**
   - Comprehensive tracking system that records the full lineage of all data as it moves through various processing stages
   - Critical for Dr. Zhang because genomic analysis requires complete transparency in how data is transformed, enabling validation of results and troubleshooting of anomalies by tracing back through the entire processing chain

2. **Pipeline Validation System**
   - Pre-execution validation framework that performs integrity checks on data, pipeline configuration, and dependencies before committing to execution
   - Essential for preventing costly processing errors by confirming that all pipeline stages are properly configured with compatible parameters and that input data meets quality thresholds before beginning resource-intensive computation

3. **Stage-Specific Error Handling**
   - Customizable error response strategies for different analysis stages based on their specific requirements and failure implications
   - Vital for maintaining data quality as different processing stages (sequencing, alignment, variant calling, etc.) have vastly different error characteristics and recovery requirements, needing specialized handling to maintain result integrity

4. **Time-Based Priority Adjustment**
   - Dynamic task priority system that accounts for sample degradation timelines and adjusts execution order accordingly
   - Critical because some biological samples have limited stability timeframes, requiring expedited processing to prevent quality degradation and ensuring the most time-sensitive samples receive processing priority

5. **Equipment Utilization Optimization**
   - Scheduling algorithms that maximize expensive sequencing and processing equipment usage with integration to predictive maintenance cycles
   - Important for optimizing the return on investment for costly sequencing equipment by ensuring maximum throughput while avoiding disruptions due to maintenance needs

## Technical Requirements

### Testability Requirements
- Pipeline configuration must be verifiable through automated validation
- Data transformations must be traceable and reproducible
- Error injection capability for testing recovery mechanisms
- Time acceleration for testing degradation-based prioritization

### Performance Expectations
- Support processing of at least 100 concurrent genomic samples
- Equipment utilization maintained above 90% during operational hours
- Pipeline validation completes in under 30 seconds for typical workflows
- Provenance queries resolve in under 5 seconds for any data point

### Integration Points
- Genomic data format compatibility (FASTQ, BAM, VCF, etc.)
- Equipment monitoring interface for utilization tracking
- Storage systems for raw and processed genomic data
- Metadata standards compliance (e.g., FAIR principles)

### Key Constraints
- Must maintain cryptographic verification of data integrity
- No data duplication without explicit provenance records
- All operations must be fully reproducible from records
- Storage efficiency for high-volume genomic data

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The Genomic Data Processing Pipeline Scheduler should provide the following core functionality:

1. **Workflow Definition and Management**
   - Python API for defining bioinformatics processing pipelines
   - Data flow specification with integrity requirements
   - Resource requirement declarations for processing stages

2. **Data Integrity and Provenance**
   - Cryptographic verification throughout processing stages
   - Complete data lineage tracking and querying
   - Metadata association with all processing steps

3. **Task Scheduling and Execution**
   - Sample prioritization based on biological constraints
   - Equipment-aware task allocation
   - Execution monitoring with quality metrics

4. **Error Handling and Recovery**
   - Stage-specific error detection and response
   - Partial results preservation during failures
   - Recovery strategies with minimal reprocessing

5. **Resource Optimization**
   - Equipment utilization tracking and forecasting
   - Maintenance-aware scheduling
   - Resource allocation based on sample priorities

## Testing Requirements

### Key Functionalities to Verify
- Data provenance correctly tracks all transformations
- Pipeline validation detects configuration issues before execution
- Error handling strategies execute correctly for each processing stage
- Priority adjustments correctly respect sample degradation timelines
- Equipment utilization meets optimization targets

### Critical User Scenarios
- Complete genomic analysis pipeline from sequencing to variant calling
- Recovery from processing errors with appropriate stage-specific handling
- Prioritization of time-sensitive samples based on degradation rates
- Equipment scheduling around maintenance windows
- Provenance queries for regulatory compliance verification

### Performance Benchmarks
- Pipeline validation completes in under 30 seconds
- Provenance tracking adds less than 5% overhead to processing
- Equipment utilization remains above 90% during normal operation
- Priority recalculation completes in under 2 seconds for 100 samples
- Sample throughput meets or exceeds 95% of theoretical maximum

### Edge Cases and Error Conditions
- Corrupted input data detection and handling
- Equipment failure during processing
- Conflicting priority requirements between samples
- Storage exhaustion during analysis
- Metadata inconsistencies in pipeline specification

### Required Test Coverage Metrics
- 100% coverage of all data transformation operations
- Complete verification of provenance recording pathways
- All error handling strategies tested for each pipeline stage
- Full coverage of prioritization logic including time-sensitivity
- Equipment utilization optimization algorithms fully verified

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

The implementation will be considered successful when:

1. Complete data provenance is maintained and queryable for all processing
2. Pipeline validation prevents execution of misconfigured workflows
3. Errors are handled according to stage-specific requirements
4. Time-sensitive samples are processed according to degradation constraints
5. Equipment utilization exceeds 90% during operational periods
6. All genomic data formats are processed with full integrity verification
7. All tests pass, including data corruption and recovery scenarios
8. Performance metrics meet or exceed the specified benchmarks

## Setup and Development

To set up the development environment:

```bash
# Initialize the project with uv
uv init --lib

# Install development dependencies
uv sync
```

To run the code:

```bash
# Run a script
uv run python script.py

# Run tests
uv run pytest
```