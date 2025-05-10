# Scientific Data Management System

A specialized file system analysis library for research scientists to manage, analyze, and optimize large scientific datasets

## Overview

The Scientific Data Management System is a specialized file system analysis library designed for research data scientists working with large experimental and simulation datasets. It provides scientific file format recognition, dataset provenance tracking, compute-to-storage optimization, collaboration pattern visualization, and data lifecycle management to enhance research workflow efficiency and reproducibility.

## Persona Description

Dr. Zhang manages large datasets for a research institution, working with terabytes of experimental results and simulation outputs. She needs to efficiently organize and archive research data while maintaining accessibility for ongoing analysis.

## Key Requirements

1. **Scientific File Format Recognition and Analysis**
   - Implement specialized parsers for common scientific file formats (HDF5, FITS, NetCDF, etc.)
   - Create metadata extraction and indexing capabilities for scientific data structures
   - This feature is critical for Dr. Zhang because scientific data is stored in domain-specific formats that general file analysis tools cannot properly interpret, leading to ineffective organization and poor visibility into dataset contents

2. **Dataset Provenance Tracking**
   - Develop a system to track relationships between original data sources and derivative products
   - Create a provenance graph representation to visualize data lineage
   - This capability is essential because research reproducibility requires clear documentation of how derived data products relate to original sources, and manual tracking becomes impossible at scale

3. **Compute-to-Storage Ratio Optimization**
   - Design analytics to assess computational efficiency relative to dataset size and organization
   - Implement recommendation engine for high-performance computing environments
   - This feature is vital for Dr. Zhang because inefficient data organization can dramatically increase computation time, wasting expensive HPC resources and delaying research outcomes

4. **Collaboration Pattern Visualization**
   - Implement analysis of dataset access patterns across research teams
   - Create visualization tools to identify multi-team usage of shared datasets
   - This functionality is critical because understanding how datasets are used by different teams helps optimize data organization for collaborative research and prevents duplication of effort

5. **Data Lifecycle Management**
   - Develop automated archival recommendation system based on access patterns
   - Create tiered storage management strategies for rarely accessed datasets
   - This feature is crucial for Dr. Zhang because research data accumulates over time, and without systematic lifecycle management, valuable storage resources are wasted on datasets that could be archived to lower-cost storage

## Technical Requirements

### Testability Requirements
- Mock datasets for various scientific file formats (HDF5, FITS, NetCDF, etc.)
- Test fixtures for provenance relationship verification
- Parameterized tests for different compute-to-storage scenarios
- Synthetic access patterns for collaboration testing
- Time-based simulation for lifecycle management testing
- Integration testing with actual scientific file formats

### Performance Expectations
- Support for datasets in the multi-terabyte range
- Efficient handling of files with billions of data points
- Analysis of file metadata without loading entire datasets
- Parallel processing for large dataset collections
- Minimal memory footprint when analyzing large scientific files
- Support for high-performance computing environments and cluster file systems

### Integration Points
- Scientific computing platforms (Jupyter, R Studio, etc.)
- High-performance computing job schedulers
- Domain-specific analysis tools
- Research data repositories and catalogs
- Archival and backup systems
- Metadata standards for scientific data (e.g., DataCite, Dublin Core)

### Key Constraints
- Must not modify original scientific data files
- Support for diverse scientific domains with different file formats
- Handling of extremely large individual files (>100GB)
- Support for specialized file systems used in HPC environments
- Minimal computational overhead to avoid impacting research workloads
- Preservation of complex metadata required for research reproducibility

## Core Functionality

The core functionality of the Scientific Data Management System includes:

1. A scientific file format analyzer that understands domain-specific data structures
2. A metadata extraction and indexing system optimized for scientific data formats
3. A provenance tracking component that maintains relationships between data sources and derivatives
4. A compute efficiency analyzer that evaluates data organization impact on processing time
5. A collaboration pattern analyzer that identifies multi-team dataset usage
6. A lifecycle management system that recommends appropriate archival strategies
7. A visualization engine for scientific data organization and relationships
8. An API layer for integration with scientific computing environments
9. A recommendation system for optimizing research data organization
10. A storage efficiency analyzer specialized for scientific data characteristics

## Testing Requirements

### Key Functionalities to Verify
- Accurate detection and analysis of scientific file formats
- Correct tracking of provenance relationships between datasets
- Accurate assessment of compute-to-storage efficiency
- Proper identification of collaboration patterns
- Appropriate lifecycle management recommendations
- Performance with very large scientific datasets
- Accuracy of metadata extraction from domain-specific formats

### Critical User Scenarios
- Managing multi-terabyte datasets from experimental apparatus
- Tracking derivatives generated through various processing pipelines
- Optimizing data organization for high-performance computing jobs
- Facilitating collaboration between multiple research teams
- Implementing efficient archival strategies for long-term data preservation
- Maintaining accessibility of historical datasets for comparative analysis
- Ensuring reproducibility of research through comprehensive provenance tracking

### Performance Benchmarks
- Analysis of 1TB of scientific data in under 1 hour
- Metadata extraction at a rate of at least 10GB per minute
- Provenance graph generation for 10,000+ related datasets in under 5 minutes
- Support for individual scientific files up to 500GB in size
- Memory usage under 4GB for standard analysis operations
- Minimal CPU impact (<5%) when running in monitoring mode

### Edge Cases and Error Conditions
- Handling corrupted scientific file formats
- Managing interrupted analysis of very large datasets
- Processing uncommon or custom scientific data formats
- Dealing with incomplete provenance information
- Handling datasets with unusual access patterns
- Processing datasets with extremely complex internal structures
- Managing analysis on resource-constrained systems

### Required Test Coverage Metrics
- 100% coverage of scientific format parsing code
- >90% coverage of provenance tracking algorithms
- Complete testing of compute efficiency calculation methods
- Thorough testing with actual scientific datasets
- Comprehensive coverage of lifecycle management logic
- Full testing of collaboration pattern detection
- Verification of correct behavior with various HPC file systems

## Success Criteria

The implementation will be considered successful when it:

1. Accurately recognizes and analyzes at least 10 common scientific file formats
2. Correctly tracks provenance relationships between source and derivative datasets
3. Provides compute-to-storage optimization recommendations that reduce processing time by at least 15%
4. Accurately identifies collaboration patterns across research teams
5. Recommends appropriate archival strategies that reduce active storage requirements by at least 25%
6. Efficiently processes multi-terabyte scientific datasets within reasonable time constraints
7. Integrates with common scientific computing environments
8. Maintains comprehensive metadata that supports research reproducibility
9. Adapts to the specific needs of different scientific domains
10. Enables clear visualization of complex data relationships and organization

To get started with development:

1. Use `uv init --lib` to set up the project structure and create pyproject.toml
2. Install dependencies with `uv sync`
3. Run development tests with `uv run pytest`
4. Run individual tests with `uv run pytest path/to/test.py::test_function_name`
5. Execute modules with `uv run python -m scientific_data_manager.module_name`