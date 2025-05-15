# Manufacturing Operations Query Language Interpreter

## Overview
This specialized Query Language Interpreter enables operational dashboard developers to efficiently query and analyze real-time manufacturing data alongside historical trends without impacting production systems. The interpreter provides optimized sliding time window computations, threshold monitoring capabilities, equipment hierarchy traversal, statistical process control functions, and production schedule integration, making it an ideal foundation for manufacturing monitoring displays.

## Persona Description
Miguel creates real-time monitoring displays for manufacturing processes. He needs to query live production data, historical trends, and alert conditions without impacting operational systems.

## Key Requirements
1. **Sliding time window computations showing recent metrics with configurable history**: Provides efficient calculations over moving time windows (last hour, shift, day, etc.) with configurable window sizes and update frequencies, enabling operators to monitor recent performance and identify developing issues without being overwhelmed by historical data or requiring full reprocessing for each update.

2. **Threshold monitoring expressions generating alerts based on query results**: Enables the definition of threshold conditions using complex expressions (statistical deviations, rate-of-change calculations, multi-variable correlations) that automatically generate alerts when exceeded, allowing for proactive monitoring of manufacturing conditions before they become critical failures.

3. **Equipment hierarchy traversal enabling drill-down from plant to specific sensors**: Implements a flexible equipment hierarchy model (enterprise → plant → area → line → machine → component → sensor) that allows queries to seamlessly aggregate data up the hierarchy or drill down for details, making it easy to identify which specific components are affecting overall system performance.

4. **Statistical process control functions detecting manufacturing variations**: Incorporates specialized SPC (Statistical Process Control) calculations including control limits, capability indices, and rule violations (Western Electric, Nelson) that automatically identify abnormal process variations requiring attention, essential for maintaining consistent product quality.

5. **Production schedule integration correlating measurements with planned operations**: Connects real-time measurements with production schedule data (products, batches, changeovers, maintenance periods), enabling contextual analysis that distinguishes between normal variations due to planned changes and unexpected deviations requiring intervention.

## Technical Requirements
### Testability Requirements
- Time window calculations must be testable with simulated real-time data streams
- Threshold monitoring must be verified for various alert conditions and edge cases
- Equipment hierarchy traversal must be tested with complex multi-level equipment structures
- SPC functions must be validated against industry-standard statistical methods
- Schedule integration must be tested for correlation accuracy during various production states

### Performance Expectations
- Must process manufacturing data at rates exceeding 10,000 data points per second
- Time window queries should return results in under 500ms regardless of historical data volume
- Alert evaluations should complete within 250ms to ensure timely notifications
- System should handle at least 1,000 simultaneous sensor streams without performance degradation
- Query execution should avoid impacting operational systems through efficient resource utilization

### Integration Points
- Support for common industrial data protocols (OPC UA, MQTT, Modbus, etc.)
- Integration with historian databases and time-series storage
- Compatibility with production scheduling systems
- Alert forwarding to notification systems and SCADA platforms
- Data export for reporting and analysis tools

### Key Constraints
- Must operate with minimal impact on production systems
- Implementation must handle 24/7 continuous operation requirements
- Real-time monitoring must maintain consistent performance
- System must maintain data integrity during production changes
- Security considerations for sensitive manufacturing data

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The core functionality of this Manufacturing Operations Query Language Interpreter includes:

1. **Real-Time Query Engine**:
   - SQL-like language with manufacturing-specific extensions
   - Time window operations with sliding and tumbling window support
   - Equipment-aware query syntax for hierarchy traversal
   - Optimized execution planning for time-series industrial data

2. **Time Window Framework**:
   - Efficient sliding window implementations
   - Incremental update mechanisms to avoid full reprocessing
   - Memory management optimized for long-running windows
   - High-performance aggregation functions for numeric data

3. **Alert Management System**:
   - Threshold expression evaluation engine
   - Configurable alert generation with severity levels
   - Hysteresis and debouncing to prevent alert floods
   - Alert state tracking and notification management

4. **Equipment Model**:
   - Hierarchical equipment representation
   - Efficient traversal and aggregation operations
   - Asset metadata integration for context
   - Change management during equipment reconfiguration

5. **Statistical Analysis Framework**:
   - Implementation of key SPC functions and rules
   - Process capability calculations
   - Statistical anomaly detection algorithms
   - Trend and pattern recognition for manufacturing processes

## Testing Requirements
### Key Functionalities to Verify
- Accuracy of sliding time window calculations for various window configurations
- Correct triggering of alerts based on threshold conditions
- Proper aggregation and drill-down through equipment hierarchies
- Accuracy of SPC calculations compared to industry standards
- Proper correlation of measurements with scheduled production activities

### Critical User Scenarios
- Monitoring real-time production metrics across multiple manufacturing lines
- Detecting and alerting on process deviations before quality issues occur
- Analyzing performance trends by equipment level or production area
- Comparing current process metrics against statistical control limits
- Distinguishing between planned production changes and unexpected variations

### Performance Benchmarks
- Sliding window computations should process at least 50,000 data points per second
- Threshold evaluations should handle at least 5,000 concurrent conditions
- Equipment hierarchy traversal should support structures with at least 10,000 nodes
- SPC calculations should complete within 100ms for typical process datasets
- System should maintain performance while processing at least 1,000 sensor streams simultaneously

### Edge Cases and Error Conditions
- Behavior during equipment reconfiguration or hierarchy changes
- Handling of communications interruptions with data sources
- Proper management of schedule changes and production exceptions
- Graceful degradation under extreme data volumes or system load
- Appropriate treatment of missing or invalid sensor readings

### Required Test Coverage Metrics
- Minimum 90% code coverage across all modules
- 100% coverage for time window calculations and threshold evaluations
- All SPC functions must have dedicated test cases with known outcomes
- Equipment hierarchy operations must be tested with various structure types
- Schedule integration must be tested for all production state transitions

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

1. Efficiently perform sliding time window calculations with configurable history periods, verified through performance testing with simulated data streams
2. Correctly trigger alerts based on complex threshold conditions, validated through test scenarios with known violation patterns
3. Properly traverse equipment hierarchies for aggregation and drill-down, confirmed with tests using complex equipment structures
4. Accurately perform statistical process control calculations, verified against industry-standard SPC examples
5. Successfully correlate measurements with scheduled production activities, demonstrated through tests with various production state changes

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