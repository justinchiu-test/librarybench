# Scientific Data Storage Analyzer

A specialized file system analyzer for research data management focused on organizing, tracking, and optimizing large scientific datasets.

## Overview

The Scientific Data Storage Analyzer is a Python library designed to help research data scientists efficiently organize, track, and analyze large scientific datasets. It provides tools for scientific file format recognition, dataset provenance tracking, compute-to-storage optimization, collaboration pattern visualization, and lifecycle management to ensure research data remains accessible and well-organized.

## Persona Description

Dr. Zhang manages large datasets for a research institution, working with terabytes of experimental results and simulation outputs. She needs to efficiently organize and archive research data while maintaining accessibility for ongoing analysis.

## Key Requirements

1. **Scientific File Format Recognition and Analysis**:
   Tools to detect, parse, and analyze specialized scientific file formats (HDF5, FITS, NetCDF, etc.). This is critical for Dr. Zhang because scientific data is often stored in domain-specific formats with complex internal structure. The system must understand the organization within these files, their compression characteristics, and their metadata schemas to enable proper management.

2. **Dataset Provenance Tracking**:
   Mechanisms to establish and maintain links between derivative data products and their original sources. This feature is essential because scientific reproducibility depends on clear data lineage. Dr. Zhang needs to track how processed data connects to raw data, document transformation parameters, and maintain the relationship graph as data evolves through the research lifecycle.

3. **Compute-to-Storage Ratio Optimization**:
   Analytics for balancing computational requirements with storage constraints in high-performance computing environments. This capability is crucial for efficient resource utilization in research computing. Dr. Zhang needs to understand which datasets require fast access for active computation versus which can be moved to archival storage, optimizing both performance and cost.

4. **Collaboration Pattern Visualization**:
   Tools to identify and visualize which datasets are accessed by multiple research teams. This is vital for understanding collaborative data usage. Dr. Zhang needs to discover opportunities for improved data sharing, detect duplication of effort, and understand cross-team dependencies to facilitate better collaboration around shared datasets.

5. **Data Lifecycle Management**:
   Functionality for implementing automated archival recommendations for rarely accessed datasets. This feature is essential for managing the long-term growth of research data. Dr. Zhang needs to establish policies for data retention based on access patterns, research stage, and institutional requirements, automatically identifying candidates for archival or deletion.

## Technical Requirements

### Testability Requirements
- All components must have well-defined interfaces that can be tested independently
- Scientific format parsing must be testable with sample data files
- Provenance tracking must be verifiable with known data lineages
- Optimization algorithms must be evaluated against benchmark datasets
- Test coverage should exceed 90% for all core functionality

### Performance Expectations
- Format recognition should process at least 100GB of scientific data per hour
- Provenance operations should scale to handle graphs with 10,000+ nodes
- Storage optimization analysis should complete in under 10 minutes for 10TB datasets
- Collaboration analysis should handle systems with 100+ users and 1,000+ datasets
- Data lifecycle operations should process at least 10,000 files per minute

### Integration Points
- Standard filesystem access interfaces for various storage systems
- Scientific computing frameworks (NumPy, Pandas, Dask)
- High-performance computing job schedulers (optional)
- Metadata standards for scientific domains
- Export capabilities for analysis results (JSON, CSV, domain-specific formats)

### Key Constraints
- All operations must be non-destructive and primarily read-only
- Implementation must handle very large individual files (100GB+)
- System must minimize memory usage when processing large datasets
- Analysis should not interfere with ongoing computational workloads
- Solution must be adaptable to different scientific domains

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The Scientific Data Storage Analyzer must provide the following core functionality:

1. **Scientific Format Analysis Engine**:
   - Detection and identification of domain-specific file formats
   - Internal structure parsing and representation
   - Metadata extraction and indexing
   - Content summarization for large datasets
   - Format-specific storage efficiency assessment

2. **Provenance Tracking Framework**:
   - Data lineage graph construction and maintenance
   - Processing step documentation and linking
   - Origin and derivative relationship mapping
   - Transformation parameter tracking
   - Reproducibility verification tools

3. **Resource Optimization System**:
   - Access pattern analysis for datasets
   - Computation intensity measurement
   - Storage tier recommendation algorithms
   - Cost-benefit analysis for different storage solutions
   - Performance impact prediction for storage decisions

4. **Collaboration Analysis Tools**:
   - Multi-user access pattern detection
   - Team-based dataset usage clustering
   - Shared dataset identification
   - Collaboration opportunity discovery
   - Cross-project data dependency mapping

5. **Lifecycle Management Engine**:
   - Dataset age and access frequency analysis
   - Archival candidate identification
   - Retention policy implementation and enforcement
   - Data value assessment algorithms
   - Automated lifecycle state transition recommendations

## Testing Requirements

### Key Functionalities to Verify
- Accuracy of scientific format recognition and parsing
- Reliability of provenance tracking across data transformations
- Effectiveness of compute-to-storage optimization recommendations
- Precision of collaboration pattern detection
- Appropriateness of lifecycle management recommendations

### Critical User Scenarios
- Management of a large-scale experimental dataset with multiple derivative products
- Optimization of storage for an active computational project
- Analysis of multi-team collaborative data usage
- Implementation of data retention policies for completed research
- Discovery of relationships between seemingly unrelated datasets

### Performance Benchmarks
- Processing of 1TB of mixed scientific formats in under 10 hours
- Construction of provenance graphs with 10,000 nodes in under 5 minutes
- Optimization analysis for 10TB storage system in under 10 minutes
- Collaboration analysis across 50 research teams in under 5 minutes
- Lifecycle assessment of 1 million files in under 30 minutes

### Edge Cases and Error Conditions
- Handling of corrupted or non-standard scientific file formats
- Recovery from interrupted analysis of very large datasets
- Graceful operation with incomplete provenance information
- Appropriate handling of permission-restricted datasets
- Sensible recommendations with limited historical access data

### Required Test Coverage Metrics
- Minimum 90% code coverage for all modules
- 100% coverage of scientific format parsing code
- Comprehensive tests for all supported file formats
- Performance tests for all resource-intensive operations
- Validation tests against real-world research datasets

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

The Scientific Data Storage Analyzer implementation will be considered successful when:

1. Scientific file format recognition accurately identifies and analyzes domain-specific formats
2. Dataset provenance tracking reliably establishes and maintains data lineage
3. Compute-to-storage optimization provides actionable recommendations for resource allocation
4. Collaboration pattern visualization correctly identifies multi-team dataset usage
5. Data lifecycle management appropriately identifies candidates for archival
6. All performance benchmarks are met or exceeded
7. Code is well-structured, maintainable, and follows Python best practices
8. The system accommodates the needs of diverse scientific domains

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

NOTE: To set up your development environment, use `uv venv` to create a virtual environment. From within the project directory, activate the environment with `source .venv/bin/activate`. Install the project with `uv pip install -e .`.

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY for project completion. Use the following commands:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```