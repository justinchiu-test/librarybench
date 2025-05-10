# Scientific Data Query Engine

A query language interpreter specialized for scientific data analysis with support for heterogeneous environmental datasets.

## Overview

The Scientific Data Query Engine provides an advanced query language interpreter tailored for scientific data analysis, with special focus on environmental data. This variant enables researchers to perform sophisticated queries across satellite imagery, sensor measurements, and field observations without converting data into formal database systems, supporting scientific notation, geospatial operations, and time series analysis.

## Persona Description

Dr. Zhang analyzes complex environmental datasets involving satellite imagery, sensor measurements, and field observations. She needs to perform sophisticated queries across heterogeneous data formats without moving everything into a formal database system each time a new analysis question arises.

## Key Requirements

1. **Scientific notation support with units awareness in numerical comparisons**
   - Implement parsing and comparison of values expressed in scientific notation (e.g., 1.2e-6)
   - Support unit conversions during comparisons (e.g., comparing 1.2 kg against 1200 g)
   - Enable error propagation in calculations based on measurement precision
   - This feature is critical because environmental data often spans many orders of magnitude and comes from instruments using different units systems

2. **Geospatial query operators for coordinate-based filtering and distance calculations**
   - Implement coordinate-based filtering (latitude/longitude, UTM, or custom coordinate systems)
   - Support distance calculations between points with different coordinate reference systems
   - Provide geospatial functions (contains, intersects, distance, area)
   - Essential for analyzing environmental data that inherently has spatial components and relationships

3. **Time series specific functions for temporal pattern detection and resampling**
   - Support time-aligned joins between datasets with different sampling frequencies
   - Implement functions for detecting temporal patterns (trends, seasonality, anomalies)
   - Provide resampling and aggregation options for different time scales
   - Critical for understanding environmental patterns and correlations across time

4. **Query result visualization hooks generating basic plots directly from query output**
   - Implement hooks for generating basic visualizations from query results
   - Support time series plots, scatter plots, and geospatial visualizations
   - Enable customization of visualization parameters via query syntax
   - Important for quickly validating results and identifying patterns that may not be apparent in tabular data

5. **Scientific workflow integration capturing query provenance for research reproducibility**
   - Track query history and parameter changes
   - Record data provenance information (source, processing steps)
   - Generate reproducible workflow documentation
   - Essential for research integrity and enabling other scientists to validate and build upon findings

## Technical Requirements

### Testability Requirements
- All functions must be unit-testable with pytest
- Data processing workflows must be testable using sample datasets
- Provide test fixtures for all data types (spatial, temporal, scientific notation)
- Mock external data sources for testing queries against remote datasets
- Test computational correctness using known reference calculations

### Performance Expectations
- Execute queries on datasets up to 10GB without memory issues through streaming processing
- Support incremental query evaluation for time series data
- Process at least 1 million records per second on standard hardware for filtering operations
- Execute geospatial operations within 500ms for datasets with up to 100,000 points
- Support parallel execution for independent query operations

### Integration Points
- Import data from common scientific formats (NetCDF, HDF5, GeoTIFF)
- Export query results to scientific data formats and analysis tools
- Interface with scientific Python libraries (numpy, scipy, pandas, xarray)
- Utilize existing geospatial libraries (geopandas, shapely, pyproj) for spatial operations
- Standardized outputs compatible with visualization libraries (matplotlib, seaborn)

### Key Constraints
- Must process data streams incrementally to handle large datasets
- Ensure all operations preserve data precision and uncertainty values
- Handle missing data and irregular sampling common in environmental measurements
- Support custom coordinate reference systems and transformations
- Maintain data provenance throughout all transformations

### Implementation Notes
IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The Scientific Data Query Engine must implement the following core functionality:

1. **Query Language Parser**
   - Parse SQL-like syntax with extensions for scientific, geospatial, and temporal operations
   - Support specialized functions and operators for scientific data
   - Validate query correctness and data type compatibility
   - Generate optimized execution plans

2. **Data Source Connectors**
   - Interface with common scientific data formats
   - Support streaming access to large datasets
   - Handle appropriate data type conversions
   - Preserve metadata and uncertainty information

3. **Execution Engine**
   - Implement query optimization for scientific workflows
   - Support parallel processing of independent operations
   - Handle distributed data sources efficiently
   - Stream results to minimize memory usage

4. **Scientific Operation Library**
   - Implement unit-aware calculations
   - Support geospatial operations and coordinate transformations
   - Provide time series analysis functions
   - Enable statistical operations with uncertainty propagation

5. **Result Processing System**
   - Generate structured outputs with metadata
   - Support various output formats
   - Capture query provenance information
   - Provide visualization hooks

## Testing Requirements

### Key Functionalities to Verify
- Correct parsing and execution of scientific queries with units
- Accurate geospatial operations and coordinate transformations
- Proper handling of time series operations and temporal patterns
- Correct execution of aggregations and statistical calculations
- Preservation of data provenance throughout processing chains

### Critical User Scenarios
- Querying satellite imagery based on geographic regions and extracting time series
- Comparing sensor measurements with different units and precisions
- Detecting temporal patterns across datasets with different sampling rates
- Executing spatial joins between observation points and polygon regions
- Generating reproducible analysis workflows from query history

### Performance Benchmarks
- Query execution time remains under 5 seconds for datasets up to 1GB
- Memory usage remains below 4GB for streaming operations on large datasets
- Geospatial operations complete within 500ms for typical environmental datasets
- Temporal pattern detection processes 10,000 time points per second

### Edge Cases and Error Conditions
- Handling datasets with mixed precision and quality indicators
- Processing queries with coordinate system transformations at date line and poles
- Managing irregular and gap-filled time series
- Dealing with conflicting units or incompatible measurement types
- Processing data with extreme value ranges (very large or very small values)

### Required Test Coverage Metrics
- Minimum 90% code coverage
- 100% coverage of core scientific operations
- All geospatial functions tested with at least 5 different coordinate reference systems
- Temporal functions tested with regular, irregular, and gap-filled time series
- Unit-aware computations tested with at least 10 different unit combinations

## Success Criteria

The implementation will be considered successful if it meets the following criteria:

1. **Functional Completeness**
   - All five key requirements are fully implemented
   - Core scientific operations produce results matching reference calculations
   - Geospatial operations correctly handle different coordinate systems
   - Time series functions accurately detect patterns in test datasets

2. **Performance Goals**
   - Meets all performance benchmarks specified in the technical requirements
   - Successfully processes test datasets of at least 5GB without memory issues
   - Executes complex queries involving multiple operations within 10 seconds

3. **Quality Metrics**
   - Passes all automated tests with at least 90% code coverage
   - Correctly handles all specified edge cases
   - Successfully reproduces documented scientific workflows

4. **Integration Capabilities**
   - Successfully imports and processes data from all specified scientific formats
   - Integrates with scientific Python libraries as documented
   - Provides correct visualization hooks for common plot types