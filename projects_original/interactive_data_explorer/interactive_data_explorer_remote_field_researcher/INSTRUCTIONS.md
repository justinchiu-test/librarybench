# Field Research Data Explorer

## Overview
A specialized terminal-based data exploration framework optimized for ecologists conducting research in remote wilderness locations with limited connectivity and computing resources. This lightweight yet powerful tool enables analysis of environmental sensor data collected during expeditions using only a laptop without relying on cloud services or specialized hardware.

## Persona Description
Marco conducts ecological studies in remote wilderness locations with limited connectivity and computing resources. He needs to analyze environmental sensor data collected during expeditions using only his laptop without relying on cloud services or specialized hardware.

## Key Requirements
1. **Low-power operating mode** - Implement resource-efficient processing algorithms that optimize battery life during extended field sessions, enabling researchers to conduct data analysis in remote locations without access to reliable power sources. This feature is critical for prolonging field work capability in off-grid environments.

2. **Geospatial visualization** - Provide specialized mapping capabilities with support for custom coordinate systems specific to study regions, allowing researchers to visualize spatial relationships in their data using locally relevant reference frames. Field ecologists often work in remote areas using local coordinate systems rather than standard GPS coordinates.

3. **Offline reference dataset integration** - Enable comparison of collected field data with pre-loaded historical environmental records, helping researchers contextualize new findings without requiring internet connectivity. This is essential for understanding how current observations relate to historical patterns while working in disconnected environments.

4. **Sensor calibration tools** - Identify and correct for environmental interference patterns in raw sensor data, accounting for field conditions that may impact measurement accuracy. Remote research often involves sensors operating in harsh conditions where temperature, humidity, and other factors can affect readings.

5. **Expedition context annotations** - Link data anomalies with field notes and observations, providing critical context for understanding unusual readings or patterns discovered during analysis. Field researchers need to integrate quantitative sensor data with qualitative field observations to properly interpret findings.

## Technical Requirements
- **Testability Requirements**:
  - Battery consumption must be measurable and verifiable against baseline
  - Geospatial functions must be validated with standard GIS test datasets
  - Calibration algorithms must be tested against known interference patterns
  - Annotation linking must maintain data integrity and relationship consistency
  - All operations must maintain defined precision appropriate for field research

- **Performance Expectations**:
  - Must operate with less than 15% CPU utilization during typical operations
  - Memory usage must remain below 500MB to function on field laptops
  - Processing of 1 week of multi-sensor data (10 sensors, 1-minute resolution) within 30 seconds
  - Startup time less than 5 seconds even with large offline reference datasets
  - Visualization generation within 2 seconds for typical data views

- **Integration Points**:
  - Support for common environmental sensor data formats (CSV, JSON, proprietary logger formats)
  - Import/export compatibility with standard GIS formats (Shapefile, GeoJSON, KML)
  - Integration with common field notebook applications and formats
  - Support for various sensor instrument calibration specifications
  - Compatibility with common reference dataset formats (NetCDF, HDF5)

- **Key Constraints**:
  - Must function completely offline with no internet dependency
  - All operations must be efficient enough for laptop use in field conditions
  - Storage footprint must be minimal for use on field computers with limited capacity
  - Must be resilient to unexpected shutdown and power loss
  - Interface must be usable in various lighting conditions (night, bright sun)

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The Field Research Data Explorer must provide a comprehensive framework for environmental field data analysis:

1. **Sensor Data Processing and Analysis**:
   - Import and parse data from various environmental sensor formats
   - Apply appropriate filtering and smoothing techniques for field collected data
   - Calculate derived metrics and indices relevant to ecological research
   - Identify patterns, cycles, and trends in environmental measurements
   - Handle missing data and sensor malfunctions common in field conditions

2. **Geospatial Analysis**:
   - Process location data in multiple coordinate systems and datums
   - Support custom local coordinate systems for specialized study areas
   - Generate spatial visualizations of environmental parameters
   - Calculate spatial statistics and clustering metrics
   - Support for common ecological spatial analysis methods

3. **Resource-Efficient Operation**:
   - Implement low-power processing algorithms and optimization
   - Provide configurable processing modes balancing detail vs. battery life
   - Efficiently manage memory and storage resources
   - Implement data compression for field-collected datasets
   - Support incremental processing to handle large datasets on limited hardware

4. **Calibration and Data Quality**:
   - Implement sensor calibration algorithms for common environmental sensors
   - Detect and correct for environmental interference patterns
   - Apply drift correction and sensitivity adjustments
   - Validate data against physical constraints and expected ranges
   - Quantify uncertainty and confidence levels in measurements

5. **Contextual Integration**:
   - Link numerical data with field notes and observations
   - Support for integrating images and audio recordings with sensor data
   - Enable annotation of data points with expedition context
   - Create timeline views combining multiple data sources
   - Generate reports integrating quantitative and qualitative information

## Testing Requirements
- **Key Functionalities to Verify**:
  - Resource usage stays within defined low-power parameters
  - Geospatial visualization correctly represents location-based data
  - Integration with offline reference datasets produces valid comparisons
  - Calibration tools accurately correct for known interference patterns
  - Annotation system successfully links data points with contextual information

- **Critical User Scenarios**:
  - Analyzing a multi-day collection of environmental sensor data in the field
  - Visualizing spatial distribution of measurements across a study area
  - Comparing field measurements with historical baseline data
  - Calibrating and correcting raw sensor data for environmental factors
  - Annotating unusual readings with field observations and notes

- **Performance Benchmarks**:
  - Process 1 week of data from 10 sensors (1-minute resolution) within 30 seconds
  - Generate geospatial visualization of 1000 data points within 3 seconds
  - Complete sensor calibration algorithms for 24 hours of data within 10 seconds
  - Maintain CPU usage below 15% during standard analysis operations
  - Keep memory usage below 500MB during all operations

- **Edge Cases and Error Conditions**:
  - Handling corrupt or partially damaged sensor data files
  - Managing extreme outliers in environmental measurements
  - Processing data from malfunctioning or miscalibrated sensors
  - Dealing with GPS/location errors and inconsistencies
  - Recovering from unexpected system shutdown during analysis

- **Required Test Coverage Metrics**:
  - 90% code coverage for all core functionality
  - 100% coverage for power optimization and resource management functions
  - All data parsers tested with valid and invalid inputs
  - Complete integration tests for all public APIs
  - Performance tests verifying resource usage constraints

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
A successful implementation of the Field Research Data Explorer will demonstrate:

1. Efficient operation with minimal power consumption suitable for field use
2. Accurate geospatial visualization with support for custom coordinate systems
3. Effective integration with offline reference datasets for historical comparison
4. Reliable sensor calibration correcting for environmental interference
5. Seamless integration of data analysis with field notes and observations

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

To set up the development environment, use:
```
uv venv
source .venv/bin/activate
uv pip install -e .
```

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```