# Research Data Lifecycle Management System

## Overview
A specialized file system analysis library for research environments that enables efficient organization, tracking, and archival of large scientific datasets. This solution supports complex scientific file formats, maintains data provenance, and optimizes storage for high-performance computing environments.

## Persona Description
Dr. Zhang manages large datasets for a research institution, working with terabytes of experimental results and simulation outputs. She needs to efficiently organize and archive research data while maintaining accessibility for ongoing analysis.

## Key Requirements
1. **Scientific file format recognition and analysis**
   - Implement comprehensive support for specialized scientific file formats (HDF5, FITS, NetCDF, etc.)
   - Extract metadata and structural information from these complex data formats
   - Analyze internal organization, compression efficiency, and access patterns
   - Provide format-specific optimization recommendations for storage efficiency

2. **Dataset provenance tracking system**
   - Develop a robust framework for linking derivative data products to their original sources
   - Maintain complete lineage information for processed datasets
   - Support for tracking transformation operations and parameters used in data processing
   - Enable verification of complete data lineage for scientific reproducibility

3. **Compute-to-storage ratio optimization**
   - Create analysis tools for high-performance computing environments to balance computational and storage resources
   - Implement metrics for evaluating the efficiency of data storage relative to computation needs
   - Develop recommendations for data organization to optimize parallel processing
   - Support for evaluating various storage strategies (chunking, sharding, compression) for specific compute workloads

4. **Collaboration pattern visualization**
   - Design data structures to represent access patterns across research teams
   - Identify commonly shared datasets and potential collaboration opportunities
   - Track usage patterns of datasets by different research groups
   - Generate insights into cross-team data utilization

5. **Data lifecycle management with archival recommendations**
   - Implement intelligence for identifying rarely accessed datasets as candidates for archival
   - Develop tiered storage recommendation engine based on access frequency and importance
   - Create metadata preservation strategies for archived data
   - Support for automated archival workflows with appropriate metadata enrichment

## Technical Requirements
- **Performance**: Must efficiently handle multi-terabyte datasets with complex internal structures
- **Extensibility**: Architecture must support easy addition of new scientific file formats
- **Accuracy**: Provenance tracking must maintain 100% accuracy for critical research data
- **Integration**: Must provide interfaces compatible with common research computing environments
- **Scalability**: Must scale to support petabyte-scale data collections with complex interdependencies

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
1. **Scientific Format Analysis Engine**
   - Format-specific parsers and analyzers
   - Internal structure and metadata extraction
   - Compression and organization analysis
   - Format conversion and optimization recommendations

2. **Provenance Tracking Framework**
   - Data lineage graph management
   - Processing operation recording
   - Source-to-output relationship mapping
   - Reproducibility verification tools

3. **HPC Storage Optimization System**
   - Compute-to-storage efficiency metrics
   - Access pattern analysis for parallel computing
   - Data organization strategy evaluation
   - Performance benchmarking and recommendation system

4. **Collaboration Analysis Engine**
   - Access tracking and pattern recognition
   - Cross-team usage visualization data models
   - Shared dataset identification
   - Collaboration opportunity detection

5. **Lifecycle Management System**
   - Access frequency and importance scoring
   - Archival candidate identification
   - Metadata preservation strategies
   - Tiered storage recommendation engine

## Testing Requirements
- **Format Support Testing**
  - Test with sample files from each supported scientific format
  - Validate correct extraction of metadata and internal structure
  - Verify optimization recommendations against format best practices
  - Benchmark performance with large scientific files

- **Provenance Testing**
  - Test accuracy of lineage tracking with complex data transformation chains
  - Validate completeness of captured metadata for reproducibility
  - Verify performance with deeply nested provenance relationships
  - Test integrity of lineage data under various failure scenarios

- **HPC Optimization Testing**
  - Test accuracy of compute-to-storage efficiency metrics
  - Validate optimization recommendations with benchmark datasets
  - Verify performance predictions with various storage strategies
  - Test with simulated HPC workloads and access patterns

- **Collaboration Analysis Testing**
  - Test pattern detection with simulated multi-team access data
  - Validate accuracy of shared dataset identification
  - Verify visualization data models with complex collaboration scenarios
  - Test scalability with large numbers of users and datasets

- **Lifecycle Management Testing**
  - Test accuracy of access frequency tracking
  - Validate archival recommendations against established best practices
  - Verify metadata preservation for various scientific formats
  - Test with simulated dataset aging and access patterns

## Success Criteria
1. Successfully process and analyze at least 10 different scientific file formats with 99% accuracy in metadata extraction
2. Maintain complete provenance tracking for data transformation chains with at least 20 steps
3. Demonstrate storage efficiency improvements of at least 30% for HPC workloads through implemented recommendations
4. Accurately identify collaboration patterns across at least 15 different research teams
5. Reduce storage costs by at least 25% through appropriate lifecycle management and archival
6. Process and analyze research datasets up to 10TB in size with reasonable performance

To set up your development environment:
```bash
# Create and activate a virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -e .
```