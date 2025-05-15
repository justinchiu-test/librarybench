# Urban Transit Data Explorer

## Overview
A specialized terminal-based data exploration framework designed for transportation planners who analyze city transit data to optimize public transportation routes and schedules. This tool enables visualization of passenger flow, identification of underserved areas, and modeling of potential service changes on commuter patterns without requiring graphical interfaces or specialized hardware.

## Persona Description
Aisha analyzes city transportation data to optimize public transit routes and schedules. She needs to visualize passenger flow, identify underserved areas, and model the impact of potential service changes on commuter patterns.

## Key Requirements
1. **Geospatial flow visualization** - Generate clear representations showing passenger movement through transit networks, critical for understanding how people navigate the city's transportation system. This feature helps planners identify major corridors, transfer points, and potential bottlenecks in the network.

2. **Temporal demand modeling** - Implement analysis tools to identify peak usage patterns and service gaps across different times of day, days of the week, and seasons. Understanding when and where demand fluctuates helps planners allocate resources efficiently and address service deficiencies.

3. **Route optimization simulation** - Develop modeling capabilities to test schedule modifications against historical demand patterns, predicting the impact of service changes before implementation. This what-if analysis helps planners evaluate potential improvements without costly real-world trials.

4. **Accessibility mapping** - Create visualizations showing transit coverage across different demographics and geographic areas to identify equity issues and underserved populations. This feature ensures transportation resources are distributed fairly and meet the needs of all community members.

5. **Multimodal transfer analysis** - Highlight connection efficiency between different transportation types (bus, subway, bike share, etc.) to improve integration of the overall network. This helps planners understand how well different parts of the transportation system work together.

## Technical Requirements
- **Testability Requirements**:
  - Geospatial visualization must be verified against actual route and ridership data
  - Temporal modeling algorithms must be validated with historical demand patterns
  - Optimization simulations must produce consistent results for identical inputs
  - Accessibility calculations must conform to transportation equity standards
  - Multimodal analysis must accurately represent actual transfer patterns and times

- **Performance Expectations**:
  - Must handle transit networks with up to 500 routes and 10,000 stops
  - Process ridership data for 1 million daily passenger trips
  - Generate visualizations of passenger flow within 10 seconds
  - Run route optimization simulations within 30 seconds
  - Memory usage must remain below 4GB even with comprehensive network data

- **Integration Points**:
  - Support for standard transit data formats (GTFS, GTFS-RT, Shapefile, GeoJSON)
  - Import capabilities for demographic and land use data
  - Export functionality for planning reports and presentations
  - Support for multimodal transportation data integration
  - Integration with census and socioeconomic datasets

- **Key Constraints**:
  - All visualizations must be terminal-compatible without external dependencies
  - Analysis must be reproducible with consistent results for planning justification
  - Must function on standard planning department hardware without cloud dependencies
  - Should handle incomplete or inconsistent transit data common in real-world systems
  - Must support public engagement by generating clear, explainable outputs

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The Urban Transit Data Explorer must provide a comprehensive framework for transportation planning analysis:

1. **Transit Network Analysis**:
   - Parse and process GTFS and other transit schedule data
   - Build network representations of transit systems
   - Calculate connectivity metrics and service levels
   - Identify critical network segments and transfer points
   - Generate network visualizations optimized for terminal display

2. **Passenger Flow Analysis**:
   - Process origin-destination matrices and ridership data
   - Calculate passenger volumes along routes and at stops
   - Identify major travel corridors and patterns
   - Analyze boarding and alighting patterns at stops
   - Generate flow visualizations showing passenger movement

3. **Temporal Demand Analysis**:
   - Analyze ridership patterns across different time periods
   - Identify peak and off-peak demand characteristics
   - Calculate headway adequacy relative to demand
   - Detect service gaps and overcrowding periods
   - Generate temporal heatmaps and demand curves

4. **Route Planning and Optimization**:
   - Implement route optimization algorithms (coverage, efficiency, equity)
   - Model impact of schedule and routing changes
   - Calculate service metrics for proposed modifications
   - Compare different service scenarios using multiple criteria
   - Generate reports on projected impacts of changes

5. **Accessibility and Equity Analysis**:
   - Calculate transit access metrics for different city areas
   - Integrate demographic and socioeconomic data
   - Identify underserved populations and areas
   - Analyze transfer burden across different communities
   - Generate equity-focused visualizations and metrics

## Testing Requirements
- **Key Functionalities to Verify**:
  - Geospatial flow visualization correctly represents passenger movement patterns
  - Temporal demand modeling accurately identifies peak periods and service gaps
  - Route optimization simulation produces realistic predictions for service changes
  - Accessibility mapping correctly identifies underserved areas
  - Multimodal transfer analysis accurately reflects connection efficiency

- **Critical User Scenarios**:
  - Analyzing ridership patterns to identify heavily used corridors
  - Identifying times when service frequency doesn't match passenger demand
  - Simulating the impact of adding a new bus route or changing a schedule
  - Evaluating transit access equity across different neighborhoods
  - Analyzing transfer efficiency between bus lines and subway stations

- **Performance Benchmarks**:
  - Process GTFS data for a 500-route transit system within 20 seconds
  - Generate passenger flow visualization for 1 million daily trips within 15 seconds
  - Complete demand analysis for a week of ridership data within 30 seconds
  - Run route optimization simulation for 10 route modifications within 30 seconds
  - Memory usage below 4GB during all operations

- **Edge Cases and Error Conditions**:
  - Handling incomplete or inconsistent GTFS data
  - Managing special service schedules (holidays, special events)
  - Processing transit systems with complex transfer patterns
  - Dealing with sparse ridership data for certain routes or times
  - Accounting for seasonal variations in travel patterns

- **Required Test Coverage Metrics**:
  - 90% code coverage for all core functionality
  - 100% coverage for optimization and simulation functions
  - All data parsers tested with valid and invalid inputs
  - Complete integration tests for all public APIs
  - Performance tests for all computationally intensive operations

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
A successful implementation of the Urban Transit Data Explorer will demonstrate:

1. Clear visualization of passenger flow through transit networks
2. Accurate identification of temporal demand patterns and service gaps
3. Realistic simulation of route and schedule optimization scenarios
4. Comprehensive mapping of transit accessibility across different demographics
5. Insightful analysis of transfer efficiency between transportation modes

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