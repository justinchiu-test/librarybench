# Process Resource Monitor - Database Administrator Edition

## Overview
You are building a Python-based process resource monitoring library specifically designed for Ming, a DBA managing multiple database instances. The library should provide process-level insights into database operations to optimize query execution and prevent resource contention.

## Core Requirements

### 1. Database Process Segregation with Per-Query Resource Tracking
- Identify and isolate database engine processes (PostgreSQL, MySQL, Oracle, SQL Server)
- Track individual query threads/processes and their resource consumption
- Correlate database sessions with system processes
- Monitor connection pool usage and client process mapping
- Support multiple database instances on the same host

### 2. Lock Contention Visualization and Deadlock Detection
- Monitor database lock acquisition and wait times
- Visualize lock dependency graphs between processes
- Detect potential deadlock scenarios before they occur
- Track lock escalation patterns and their resource impact
- Identify long-running transactions holding critical locks

### 3. Buffer Cache and Memory Pool Utilization Monitoring
- Track shared buffer usage and hit ratios per process
- Monitor sort operations and temporary file creation
- Measure work memory allocation for complex queries
- Identify memory pressure and swapping caused by queries
- Analyze buffer eviction patterns and their causes

### 4. I/O Pattern Analysis for Query Optimization Hints
- Track sequential vs random I/O patterns per query
- Measure read/write ratios and block sizes
- Identify table/index scan patterns indicating missing indexes
- Monitor checkpoint and WAL writing impact
- Detect inefficient full table scans and suggest optimizations

### 5. Replication Lag Correlation with Resource Availability
- Monitor replication processes and their resource usage
- Correlate replication lag with system resource constraints
- Track network bandwidth usage for streaming replication
- Identify resource bottlenecks causing replication delays
- Predict replication lag based on current resource trends

## Technical Specifications

### Data Collection
- Integration with database performance schemas and system views
- Process-level metrics collection at 1-second intervals
- Correlation of OS metrics with database internal statistics
- Support for remote database monitoring via connections
- Minimal performance impact on production databases

### API Design
```python
# Example usage
monitor = DatabaseResourceMonitor()

# Add database instances
monitor.add_database(
    name="prod_db1",
    type="postgresql",
    connection_string="postgresql://monitor:pass@localhost:5432/postgres",
    monitor_replication=True
)

# Track query resource usage
query_stats = monitor.get_query_resource_usage(
    database="prod_db1",
    time_range="1h",
    min_duration_ms=1000
)

# Analyze lock contention
locks = monitor.analyze_lock_contention(
    database="prod_db1",
    include_wait_graph=True
)

# Get I/O optimization hints
io_hints = monitor.get_io_optimization_hints(
    database="prod_db1",
    tables=["orders", "customers"],
    confidence_threshold=0.8
)

# Check replication health
repl_status = monitor.get_replication_status(
    include_lag_prediction=True,
    forecast_minutes=30
)
```

### Testing Requirements
- Unit tests covering all major database platforms
- Integration tests with dockerized database instances
- Load tests simulating high-concurrency scenarios
- Lock contention simulation and detection validation
- Use pytest with pytest-json-report for test result formatting
- Mock database connections for offline testing

### Performance Targets
- Monitor up to 50 database instances per host
- Track 1000+ concurrent queries with <2% overhead
- Detect lock contention within 5 seconds
- Generate optimization reports in under 30 seconds
- Store 7 days of detailed metrics with compression

## Implementation Constraints
- Python 3.8+ compatibility required
- Use only Python standard library plus: psutil, psycopg2, pymysql, cx_Oracle
- No GUI components - this is a backend library only
- Database credentials must be securely stored
- Support read-only monitoring without write permissions

## Deliverables
1. Core Python library supporting PostgreSQL, MySQL, Oracle, SQL Server
2. Query resource profiling and optimization hint generator
3. Lock contention detector with deadlock prediction
4. Replication lag monitor with resource correlation
5. CLI tool for DBA investigations and report generation