# Database Performance Log Analysis Framework

## Overview
A specialized log analysis framework designed for database administrators to monitor query performance, resource utilization, and optimization opportunities across various database technologies. This system provides insights into query execution, lock contention, index usage, and storage growth to help maintain efficient and reliable database operations.

## Persona Description
Dr. Chen manages large-scale database clusters supporting critical business applications. She needs to monitor query performance, resource utilization, and identify optimization opportunities across different database technologies.

## Key Requirements

1. **Query Performance Analysis**
   - Extraction and analysis of execution plans from database logs
   - Identification of bottleneck queries and suboptimal execution patterns
   - Historical trending of query performance with correlation to database load and configuration changes
   - This feature is critical because slow queries can significantly impact application performance, and identifying problematic patterns enables targeted optimization of database workloads.

2. **Lock Contention Visualization**
   - Detailed analysis of transaction blocking patterns and deadlocks
   - Identification of hotspot tables and resources causing concurrency issues
   - Temporal analysis of lock acquisition and wait times across transactions
   - This feature is essential because lock contention directly impacts database throughput and response times, and understanding complex blocking chains is difficult without visualization tools.

3. **Index Usage Statistics**
   - Monitoring and analysis of index utilization across database operations
   - Identification of unused or underutilized indexes
   - Recommendation of missing indexes based on query patterns
   - This feature is vital because proper indexing is fundamental to database performance, while unnecessary indexes waste storage and slow down write operations.

4. **Storage Growth Prediction**
   - Tracking and forecasting of storage usage patterns by table and schema
   - Anomaly detection for unusual growth rates or data accumulation
   - Capacity planning recommendations based on projected growth
   - This feature is important because unexpected storage growth can lead to outages, while accurate forecasting enables proactive capacity management.

5. **Replication Lag Monitoring**
   - Analysis of replication performance across database instances
   - Automated root cause analysis for synchronization issues
   - Correlation between replication delays and database workload patterns
   - This feature is necessary because replication lag affects data consistency and failover reliability in distributed database environments.

## Technical Requirements

### Testability Requirements
- All database analysis algorithms must be testable with synthetic log data representing various database engines
- Query execution plan parsing must be verifiable with sample plans from different database technologies
- Performance measurement accuracy must be quantifiably verifiable
- Tests must cover various database scenarios including high concurrency and resource constraints

### Performance Expectations
- Process log entries from databases generating at least 10,000 log entries per minute
- Complete complex analysis operations (query analysis, lock visualization) in under 30 seconds
- Support for historical analysis of at least 90 days of database logs
- Minimal resource usage to avoid impact on production database servers

### Integration Points
- Support for major database engines (PostgreSQL, MySQL, Oracle, SQL Server, MongoDB)
- Log collection from database servers and monitoring systems
- Export capabilities for integration with database management tools
- Alerting integration for proactive notification of database issues

### Key Constraints
- Must operate without requiring direct database access (log-based analysis only)
- Should not require installation of custom extensions or agents on database servers
- Must handle vendor-specific log formats and query plan representations
- Should provide value without requiring disclosure of actual query content (for sensitive environments)

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The core functionality of the Database Performance Log Analysis Framework includes:

1. **Database Log Collection and Parsing**
   - Multi-format log parsers for different database engines
   - Query extraction and normalization
   - Execution plan parsing and analysis
   - Transaction and lock event correlation

2. **Performance Analysis Engine**
   - Query performance measurement and benchmarking
   - Lock contention detection and dependency chain analysis
   - Index usage tracking and recommendation generation
   - Resource utilization analysis and bottleneck identification

3. **Storage and Capacity Management**
   - Storage usage tracking at table and schema levels
   - Growth pattern analysis and forecasting
   - Anomaly detection for unexpected data changes
   - Archival recommendations based on access patterns

4. **Replication and Consistency Analysis**
   - Replication lag measurement and tracking
   - Master-replica synchronization monitoring
   - Transaction throughput balancing
   - Conflict detection in multi-master setups

5. **Recommendation Engine**
   - Data-driven optimization suggestions
   - Index creation and removal recommendations
   - Query rewrite suggestions based on pattern analysis
   - Configuration parameter tuning advice

## Testing Requirements

### Key Functionalities to Verify
- Accurate parsing and analysis of query execution plans
- Correct identification of lock contention patterns and deadlocks
- Reliable detection of unused and missing indexes
- Precise storage growth forecasting based on historical patterns
- Accurate measurement and diagnosis of replication lag issues

### Critical User Scenarios
- Identifying the root cause of a sudden performance degradation
- Diagnosing lock contention issues causing application timeouts
- Optimizing index usage for a high-volume transaction system
- Planning storage capacity for rapid database growth
- Troubleshooting replication delays in a distributed database environment

### Performance Benchmarks
- Log processing throughput: Minimum 10,000 database log entries per minute
- Query analysis: Process and analyze 1,000 distinct queries in under 20 seconds
- Lock contention analysis: Reconstruct dependency graphs for 100 concurrent transactions in under 10 seconds
- Storage analysis: Generate growth forecasts for databases with 10,000+ tables in under 2 minutes
- Replication monitoring: Calculate and correlate lag metrics across 50 database instances in real-time

### Edge Cases and Error Conditions
- Handling corrupted or truncated log entries
- Processing logs during database schema migrations
- Analyzing performance during extreme load conditions
- Managing logs from database engines running non-standard configurations
- Dealing with mixed workloads (OLTP and OLAP) on the same database instance

### Required Test Coverage Metrics
- Minimum 90% line coverage across all modules
- 100% coverage of critical query analysis and lock detection algorithms
- Comprehensive testing of different database engine log formats
- Full testing of storage growth prediction algorithms with various growth patterns

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

The implementation will be considered successful if:

1. It accurately identifies and analyzes performance bottlenecks in database queries
2. It correctly detects and visualizes lock contention patterns and deadlocks
3. It reliably analyzes index usage and generates appropriate recommendations
4. It accurately predicts storage growth based on historical data patterns
5. It precisely measures and diagnoses replication lag issues across database instances
6. It supports multiple major database engines with their specific log formats
7. It meets performance benchmarks for processing high volumes of database logs
8. It provides a well-documented API for integration with database management tools

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Development Setup

1. Set up a virtual environment using `uv venv`
2. From within the project directory, activate the environment with `source .venv/bin/activate`
3. Install the project with `uv pip install -e .`
4. Install test dependencies with `uv pip install pytest pytest-json-report`

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```