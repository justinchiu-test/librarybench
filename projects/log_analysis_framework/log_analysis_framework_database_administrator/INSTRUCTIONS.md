# Database Performance Log Analysis Framework

A specialized log analysis framework designed for database administrators to monitor and optimize database performance.

## Overview

This project implements a comprehensive log analysis system tailored for database administrators. It provides query performance analysis, lock contention monitoring, index usage statistics, storage growth prediction, and replication monitoring to help maintain and optimize critical database systems.

## Persona Description

Dr. Chen manages large-scale database clusters supporting critical business applications. She needs to monitor query performance, resource utilization, and identify optimization opportunities across different database technologies.

## Key Requirements

1. **Query Performance Analysis**
   - Implement functionality to extract execution plans and identify bottlenecks
   - Critical for Dr. Chen to find slow queries that impact application performance and understand why they're slow
   - Must parse database logs to extract query execution details, plans, and metrics
   - Should categorize performance issues (I/O bound, CPU bound, memory bound, lock contention)
   - Must support multiple database types (PostgreSQL, MySQL, SQL Server, Oracle)

2. **Lock Contention Visualization**
   - Create a system to analyze transaction blocking patterns and deadlocks
   - Essential for Dr. Chen to identify applications or queries causing concurrency issues and blocking others
   - Should detect lock chains, blocking duration, and frequency of contention
   - Must identify deadlock patterns and suggest mitigation strategies
   - Should correlate lock issues with specific transactions, tables, and time periods

3. **Index Usage Statistics**
   - Develop analysis capabilities to highlight underutilized or missing indexes
   - Necessary for Dr. Chen to optimize database performance through proper indexing
   - Should identify unused indexes consuming space and maintenance overhead
   - Must suggest potential new indexes based on query patterns
   - Should analyze index fragmentation and maintenance needs

4. **Storage Growth Prediction**
   - Build predictive analytics for database storage needs by table and schema
   - Important for Dr. Chen to plan capacity and manage storage resources effectively
   - Should analyze historical growth patterns and project future needs
   - Must identify tables with unusual growth rates or patterns
   - Should account for seasonal variations in data growth

5. **Replication Lag Monitoring**
   - Implement monitoring for replication health with automated root cause analysis
   - Vital for Dr. Chen to ensure data consistency across replicated database systems
   - Should track replication lag metrics and identify patterns affecting synchronization
   - Must detect conditions that could lead to replication failure
   - Should correlate replication issues with system events or query patterns

## Technical Requirements

### Testability Requirements
- All functionality must be testable via pytest using appropriate fixtures and mocks
- Tests must validate correct parsing of various database log formats
- Test coverage should exceed 85% for all modules
- Performance tests must simulate high-volume database workloads to verify analysis capabilities
- Tests should validate accuracy of predictive algorithms using historical data

### Performance Expectations
- Must process logs from databases handling 10,000+ queries per second
- Should analyze terabytes of historical log data efficiently for trend analysis
- Query analysis should complete within seconds even for complex execution plans
- Should support both real-time monitoring and historical batch analysis
- Must handle bursts of log activity during peak database load periods

### Integration Points
- Compatible with major database systems (PostgreSQL, MySQL, SQL Server, Oracle)
- Support for both self-hosted and cloud-managed database services
- Integration with database metrics systems (Prometheus, CloudWatch, etc.)
- Optional integration with monitoring platforms and alerting systems

### Key Constraints
- Should operate with read-only access to database logs (no direct database modifications)
- Must minimize performance impact on production database systems
- Implementation should be database-agnostic with adapters for specific systems
- Should work with both complete and partial logging configurations

## Core Functionality

The system must implement these core capabilities:

1. **Log Collection & Parsing**
   - Extract information from various database log formats
   - Normalize data from different database systems
   - Parse query text and execution plans
   - Process both error logs and performance logs

2. **Query Analysis Engine**
   - Analyze query execution plans and statistics
   - Identify performance bottlenecks and resource constraints
   - Compare similar queries for optimization opportunities
   - Track query performance trends over time

3. **Concurrency Analyzer**
   - Monitor lock acquisition and release patterns
   - Detect blocking chains and deadlocks
   - Analyze transaction durations and contention
   - Identify applications or users causing lock issues

4. **Schema Optimizer**
   - Track index usage and effectiveness
   - Identify missing or redundant indexes
   - Monitor table growth and access patterns
   - Analyze data distribution and cardinality

5. **Replication Monitor**
   - Track replication lag and throughput
   - Detect replication topology changes
   - Identify causes of replication delays
   - Monitor data consistency across replicas

## Testing Requirements

### Key Functionalities to Verify

- **Query Parsing**: Verify correct parsing and analysis of queries from different database systems
- **Performance Analysis**: Ensure accurate identification of query bottlenecks and resource constraints
- **Lock Detection**: Validate correct tracking of lock contention and deadlock situations
- **Index Analysis**: Confirm accurate reporting of index usage and missing index opportunities
- **Storage Prediction**: Verify accuracy of storage growth predictions against actual historical data
- **Replication Monitoring**: Ensure correct detection and analysis of replication lag causes

### Critical User Scenarios

- Identifying the top 10 resource-intensive queries in a production database
- Analyzing a sudden increase in lock timeouts during peak business hours
- Forecasting storage requirements for the next quarter based on growth trends
- Determining which indexes are unused and safe to remove
- Troubleshooting intermittent replication lag between primary and secondary databases

### Performance Benchmarks

- Process and analyze 1 million query log entries in under 5 minutes
- Complete lock contention analysis for 24 hours of database activity in under 2 minutes
- Generate index usage reports for databases with 1,000+ tables in under 3 minutes
- Predict storage growth with 90% accuracy using 6 months of historical data
- Analyze replication lag patterns across 10+ database replicas in real-time

### Edge Cases and Error Handling

- Handle corrupted or incomplete log entries gracefully
- Process logs during database version upgrades with changing log formats
- Manage analysis during database schema changes
- Handle temporary spikes in database activity without analysis degradation
- Process logs from databases with partial logging enabled

### Test Coverage Requirements

- 90% coverage for log parsing and normalization
- 90% coverage for query analysis algorithms
- 85% coverage for lock contention detection
- 85% coverage for index usage analysis
- 90% coverage for storage prediction algorithms
- 85% coverage for replication monitoring
- 85% overall code coverage

## Success Criteria

The implementation meets Dr. Chen's needs when it can:

1. Correctly identify and categorize the top 20 performance-impacting queries with >95% accuracy
2. Detect and visualize lock contention patterns, reducing resolution time by at least 50%
3. Identify unused and missing indexes with >90% accuracy, improving query performance by at least 30%
4. Predict future storage needs with at least 85% accuracy three months in advance
5. Detect and diagnose causes of replication lag with >90% accuracy
6. Process database logs from systems handling 10,000+ queries per second without performance degradation
7. Support at least four major database platforms (PostgreSQL, MySQL, SQL Server, Oracle)

## Getting Started

To set up your development environment and start working on this project:

1. Initialize a new Python library project using uv:
   ```
   uv init --lib
   ```

2. Install dependencies:
   ```
   uv sync
   ```

3. Run tests:
   ```
   uv run pytest
   ```

4. Run specific tests:
   ```
   uv run pytest tests/test_query_analyzer.py
   ```

5. Run your code:
   ```
   uv run python examples/analyze_postgres_logs.py
   ```

Remember that all functionality should be implemented as importable Python modules with well-defined APIs, not as user-facing applications.