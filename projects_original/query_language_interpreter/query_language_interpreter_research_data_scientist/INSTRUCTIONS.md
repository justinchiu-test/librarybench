# Query Language Interpreter for Environmental Research Data Analysis

## Overview
This specialized Query Language Interpreter enables environmental researchers to perform sophisticated queries across heterogeneous data formats, including satellite imagery, sensor measurements, and field observations, without requiring a formal database system. The interpreter supports scientific notation, geospatial operations, and time series analysis specifically tailored for environmental research workflows, ensuring reproducibility and efficient data exploration.

## Persona Description
Dr. Zhang analyzes complex environmental datasets involving satellite imagery, sensor measurements, and field observations. She needs to perform sophisticated queries across heterogeneous data formats without moving everything into a formal database system each time a new analysis question arises.

## Key Requirements
1. **Scientific notation support with units awareness in numerical comparisons**: Enables researchers to query numerical data using scientific notation (e.g., 1.2e-4) and properly compare measurements with different units (e.g., μg/L vs mg/L), automatically converting units during comparisons to ensure accurate results when analyzing sensor data with varied measurement units.

2. **Geospatial query operators for coordinate-based filtering and distance calculations**: Allows filtering data based on geographic coordinates, calculating distances between sampling points, and identifying data points within specific regions or boundaries, essential for analyzing spatially distributed environmental measurements.

3. **Time series specific functions for temporal pattern detection and resampling**: Provides capabilities to detect temporal patterns (seasonality, trends), perform time-based aggregations, and resample time series at different intervals, enabling researchers to identify environmental changes over time and correlate observations across different temporal scales.

4. **Query result visualization hooks generating basic plots directly from query output**: Creates instant visualizations of query results without requiring separate plotting code, allowing researchers to quickly validate query results and identify patterns or anomalies in environmental data.

5. **Scientific workflow integration capturing query provenance for research reproducibility**: Automatically records all query operations, parameters, and data sources, enabling researchers to document their analysis process for publication, peer review, and reproducing results in future research.

## Technical Requirements
### Testability Requirements
- All components must be testable with pytest, with particular emphasis on scientific calculations, geospatial operations, and unit conversion accuracy
- Mock data generators must provide realistic environmental datasets with known patterns for testing temporal and spatial analysis functions
- Tests must verify that unit conversions maintain scientific precision and accuracy
- Query provenance capture must be verified for completeness and accuracy

### Performance Expectations
- Must efficiently handle datasets of at least 10GB in size
- Geospatial queries should complete within 5 seconds for datasets containing up to 1 million coordinate points
- Time series pattern detection algorithms should scale linearly with data size
- Query execution plans should be optimized for scientific operations with large numerical arrays

### Integration Points
- Support for importing from and exporting to common scientific data formats (NetCDF, HDF5)
- Ability to integrate with scientific Python libraries like NumPy, SciPy, and xarray
- Optional hooks for integrating with Matplotlib and other visualization libraries
- Import/export capabilities for workflow management systems common in scientific research

### Key Constraints
- All operations must maintain numerical precision required for scientific research
- Implementation must be pure Python to ensure cross-platform compatibility in research environments
- No external database dependencies to allow operation in field research environments
- Core functionality must operate without network connectivity for remote field use

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The core functionality of this Query Language Interpreter for environmental research includes:

1. **Parser and Interpreter Engine**:
   - Custom SQL-like query language with syntax extensions for scientific operations
   - Support for scientific notation and units in query expressions
   - Parser capable of handling complex geospatial and temporal expressions

2. **Data Source Adapters**:
   - Connectors for reading environmental data from various formats (CSV, JSON, NetCDF, etc.)
   - Metadata extraction and schema inference optimized for scientific datasets
   - Streaming data access for efficient handling of large environmental datasets

3. **Query Processing Engine**:
   - Execution planning optimized for scientific and geospatial operations
   - Support for complex filtering, joining, and aggregation operations
   - Unit-aware calculations and comparisons throughout the execution pipeline

4. **Scientific Function Library**:
   - Geospatial operations (distance calculations, bounding box queries, coordinate transformations)
   - Time series functions (resampling, trend detection, seasonality analysis)
   - Statistical operations relevant to environmental research

5. **Reproducibility Framework**:
   - Complete query provenance capture and storage
   - Query parameter tracking and serialization
   - Export capabilities for research documentation

## Testing Requirements
### Key Functionalities to Verify
- Scientific notation parsing and calculation accuracy
- Unit conversion correctness and precision
- Geospatial operation accuracy and edge cases
- Time series function correctness with various data patterns
- Provenance capture completeness and consistency

### Critical User Scenarios
- Analyzing multi-year sensor data for seasonal patterns
- Filtering observations based on geographic regions
- Correlating measurements across different data sources and units
- Exporting query provenance for research publications
- Testing calculation accuracy against known scientific standards

### Performance Benchmarks
- Query execution time must not exceed 10 seconds for 1GB datasets
- Memory consumption should remain within 2x the size of the working dataset
- Geospatial index operations should achieve O(log n) complexity
- Time series analysis functions should handle at least 10 million data points efficiently

### Edge Cases and Error Conditions
- Handling of missing or inconsistent data points in time series
- Proper treatment of data points at the International Date Line or poles
- Behavior with extremely small or large numerical values in scientific notation
- Graceful handling of inconsistent or incompatible units
- Appropriate error messages for invalid geospatial operations

### Required Test Coverage Metrics
- Minimum 90% code coverage for core functionality
- 100% coverage for unit conversion and scientific calculation functions
- All public APIs must have comprehensive tests
- All error conditions and edge cases must be explicitly tested

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
A successful implementation will:

1. Enable researchers to query environmental data using scientific notation and units, verified by tests demonstrating accurate comparison of values with different unit systems
2. Support sophisticated geospatial queries, confirmed through tests with known coordinate systems and boundary conditions
3. Provide time series analysis capabilities that correctly identify patterns in environmental data
4. Generate basic visualizations directly from query results as demonstrated in functional tests
5. Capture complete query provenance for reproducibility, verified by tests that confirm all relevant metadata is recorded

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup

To set up your development environment:

```bash
# From within the project directory
uv venv
source .venv/bin/activate
uv pip install -e .
```

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY for project completion:
```bash
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```