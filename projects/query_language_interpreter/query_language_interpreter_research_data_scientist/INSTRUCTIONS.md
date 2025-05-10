# Scientific Data Query Interpreter

A specialized query language interpreter for environmental research datasets with support for scientific notation, geospatial operations, and time series analysis.

## Overview

This project implements a flexible query language interpreter tailored for scientific research, especially environmental sciences. It allows researchers to query heterogeneous data sources (satellite imagery, sensor measurements, field observations) using a SQL-like syntax enhanced with domain-specific operators and functions for scientific data analysis. The interpreter enables sophisticated data manipulation without requiring data migration to formal database systems for each analysis question.

## Persona Description

Dr. Zhang analyzes complex environmental datasets involving satellite imagery, sensor measurements, and field observations. She needs to perform sophisticated queries across heterogeneous data formats without moving everything into a formal database system each time a new analysis question arises.

## Key Requirements

1. **Scientific Notation Support with Units Awareness**
   - Parse and compare quantities with various scientific units (°C, m/s, ppm, etc.)
   - Handle conversions between compatible units automatically during comparisons
   - Support scientific notation (e.g., 1.2E-6) with appropriate precision handling
   - Enable uncertainty ranges in measurements with proper propagation in calculations
   - Critical for Dr. Zhang to compare measurements from different instruments with varying units and precision levels

2. **Geospatial Query Operators**
   - Implement coordinate-based filtering (points within polygons, distance calculations)
   - Support common coordinate systems (WGS84, UTM) with automatic conversion
   - Include functions for spatial relationships (contains, intersects, within distance)
   - Enable bounding box and radius-based searches on geo-referenced data
   - Essential for analyzing spatially distributed environmental measurements and relating them to geographic features

3. **Time Series Functions for Temporal Pattern Detection**
   - Implement functions for temporal aggregation (daily, monthly, seasonal averages)
   - Support for detecting trends, seasonality, and outliers in time series data
   - Enable temporal pattern matching (find similar patterns across different time periods)
   - Include resampling operations to normalize data with different collection frequencies
   - Critical for analyzing environmental data collected over time and detecting temporal patterns in climate and ecological systems

4. **Query Result Visualization Hooks**
   - Provide data output formats compatible with common visualization libraries
   - Include hooks for generating basic plots (scatter, line, heatmap) directly from query results
   - Support exporting geospatial query results in formats readable by GIS tools
   - Enable time series visualization with proper temporal axis handling
   - Important for quickly validating query results visually and sharing preliminary findings without switching tools

5. **Scientific Workflow Integration with Provenance Tracking**
   - Capture complete query history with parameter values for research reproducibility
   - Record data source versions and access timestamps in query metadata
   - Support query templates with parameter substitution for repeated analyses
   - Enable query result caching with invalidation based on source data changes
   - Critical for ensuring research reproducibility and tracking the evolution of analyses during research projects

## Technical Requirements

### Testability Requirements
- All components must expose clear interfaces with well-defined inputs and outputs
- Mock data sources must be available for testing queries without external dependencies
- Scientific calculations must be verifiable against known reference values
- Time-dependent functions should support artificial time sources for deterministic testing
- Unit tests must cover both common cases and edge cases for scientific operations

### Performance Expectations
- Handle datasets up to 10GB without external database requirements
- Complete typical queries on datasets under 1GB in less than 5 seconds
- Support streaming processing for datasets too large to fit in memory
- Optimize geospatial and time series operations for large datasets
- Provide indexing capabilities for frequently queried fields

### Integration Points
- Accept data from standard scientific formats (NetCDF, HDF5, GeoTIFF)
- Provide adapters for CSV, JSON, and columnar data formats
- Support hooks for custom data source extensions
- Integration with common Python scientific libraries (numpy, pandas, xarray)
- Export capabilities to Jupyter notebooks for interactive analysis

### Key Constraints
- All operations must be memory-efficient with large datasets
- Scientific calculations must maintain appropriate precision
- No external database dependencies allowed
- All functionality must be accessible via Python API
- The solution must be deployable in air-gapped research environments

## Core Functionality

The core of this Query Language Interpreter includes:

1. **Query Parser**
   - Parse SQL-like syntax with scientific extensions
   - Support for scientific notation and units in literals
   - Domain-specific functions for environmental data
   - Type checking system aware of dimensions and units

2. **Execution Engine**
   - Optimize query plans for scientific operations
   - Stream processing for large datasets
   - Parallelize operations where possible
   - Handle geospatial and temporal indexes

3. **Data Source Adapters**
   - Connect to scientific file formats (NetCDF, HDF5)
   - Support for tabular data (CSV, Excel)
   - Adapters for remote data through APIs
   - Virtual joins across heterogeneous sources

4. **Scientific Functions Library**
   - Statistical operations for environmental data
   - Geospatial functions (distance, area, containment)
   - Time series analysis (trends, seasonality, resampling)
   - Unit conversion and dimension checking

5. **Provenance Tracker**
   - Record query execution details
   - Version tracking for data sources
   - Capture parameter values and execution context
   - Generate reproducible query workflows

## Testing Requirements

### Key Functionalities to Verify
- Correct parsing of scientific notation and units
- Accurate results for geospatial operations
- Proper handling of time series functions
- Correct application of units in calculations and comparisons
- Completeness of provenance information

### Critical User Scenarios
- Analyzing temperature trends across multiple weather stations
- Correlating satellite imagery with ground sensor readings
- Finding anomalies in environmental measurements over time
- Comparing data across different spatial regions
- Replicating previous analyses with updated datasets

### Performance Benchmarks
- Geospatial queries on 1M points completed within 10 seconds
- Time series aggregation of 10M readings within 30 seconds
- Query execution plan generation within 1 second
- Memory usage below 4GB for datasets up to 10GB
- Linear scaling with dataset size up to memory limits

### Edge Cases and Error Conditions
- Handling missing or invalid data in time series
- Dealing with coordinate system mismatches in geospatial data
- Graceful degradation with extremely large datasets
- Proper error reporting for unit incompatibilities
- Recovery from interrupted long-running queries

### Required Test Coverage Metrics
- Minimum 90% code coverage for core engine
- 100% coverage for scientific calculation functions
- Comprehensive testing of all query operators
- Performance tests for all supported data source types
- Integration tests for complete query workflows

## Success Criteria

1. All scientific notations and units are correctly parsed and computed in queries
2. Geospatial queries produce accurate results across different coordinate systems
3. Time series analyses correctly identify trends and patterns in environmental data
4. Query results can be efficiently visualized through the provided hooks
5. Full provenance tracking enables exact reproduction of any analysis
6. Researchers can analyze multi-gigabyte datasets without external databases
7. Queries on common environmental datasets execute within the performance benchmarks
8. The system integrates smoothly with the Python scientific ecosystem

## Getting Started with Development

To start developing this project:

1. Set up the development environment using `uv`:
   ```
   uv init --lib
   ```

2. Manage dependencies with `uv`:
   ```
   uv pip install numpy pandas
   ```

3. Run your code with:
   ```
   uv run python your_script.py
   ```

4. Run tests with:
   ```
   uv run pytest
   ```