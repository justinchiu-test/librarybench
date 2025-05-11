# Database Storage Optimization System

## Overview
A specialized file system analysis library for database environments that analyzes database files, logs, and backups to optimize storage usage and performance. This solution provides database-specific insights, transaction log analysis, and recommendations for improving storage efficiency.

## Persona Description
Elena manages large database deployments and needs to analyze how storage is used by database files, logs, and backups. Her goal is to optimize performance and minimize storage costs while ensuring data integrity.

## Key Requirements
1. **Database-specific file pattern recognition**
   - Implement specialized detection and analysis for files from major database engines (MySQL, PostgreSQL, MongoDB, etc.)
   - Identify and classify database components (data files, indexes, logs, temporary files, etc.)
   - Extract database-specific metadata to correlate files with database structures
   - Create specialized insights for each database engine's unique storage characteristics

2. **Transaction log analysis engine**
   - Develop algorithms to analyze transaction log growth patterns
   - Correlate log growth with database operations and activity types
   - Track log rotation, archiving, and cleanup efficiency
   - Generate recommendations for log configuration optimization

3. **Index efficiency metrics system**
   - Create tools to measure storage overhead versus query performance benefits for indexes
   - Identify potentially redundant or unnecessary indexes
   - Track index fragmentation and maintenance effectiveness
   - Provide recommendations for index optimization and consolidation

4. **Tablespace fragmentation visualization**
   - Implement analysis for database file fragmentation at both file system and database levels
   - Create data models for visualizing fragmentation patterns
   - Track fragmentation growth over time
   - Generate optimization and maintenance recommendations

5. **Backup compression efficiency analysis**
   - Develop comparative analysis for various backup compression algorithms and strategies
   - Track backup storage efficiency over time and across database versions
   - Identify opportunities for improved compression or deduplication
   - Create recommendations for optimal backup configurations based on data characteristics

## Technical Requirements
- **Compatibility**: Must support major database engines (MySQL/MariaDB, PostgreSQL, Oracle, SQL Server, MongoDB)
- **Safety**: Must operate without interfering with database operations or risking data integrity
- **Performance**: Analysis operations must be optimized to minimize impact on production systems
- **Accuracy**: Recommendations must be data-driven and aligned with database engine best practices
- **Security**: Must respect database security boundaries and access controls

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
1. **Database File Analysis Engine**
   - Database engine-specific file detection
   - Component classification and cataloging
   - Metadata extraction and correlation
   - Engine-specific optimization analysis

2. **Transaction Log Analysis System**
   - Log growth pattern detection
   - Operation correlation algorithms
   - Rotation and archival efficiency tracking
   - Configuration recommendation engine

3. **Index Optimization Framework**
   - Storage-to-performance ratio analysis
   - Redundancy and usage pattern detection
   - Fragmentation measurement algorithms
   - Maintenance effectiveness tracking

4. **Fragmentation Analysis Engine**
   - Multi-level fragmentation detection
   - Temporal pattern analysis
   - Impact assessment algorithms
   - Defragmentation planning tools

5. **Backup Analysis System**
   - Compression algorithm comparison
   - Efficiency trending over time
   - Opportunity identification algorithms
   - Configuration optimization engine

## Testing Requirements
- **Database File Testing**
  - Test with sample files from each supported database engine
  - Validate classification accuracy with known database file sets
  - Verify metadata extraction against actual database metadata
  - Test with various database sizes and configurations

- **Transaction Log Testing**
  - Test pattern detection with simulated log data
  - Validate correlation accuracy with known database activities
  - Verify recommendation quality against expert configurations
  - Test with various logging configurations and workloads

- **Index Analysis Testing**
  - Test ratio calculations with benchmark index configurations
  - Validate redundancy detection with known suboptimal indexes
  - Verify fragmentation measurements against database tools
  - Test with various index types and usage patterns

- **Fragmentation Testing**
  - Test detection algorithms with deliberately fragmented files
  - Validate impact assessment against measured performance
  - Verify pattern analysis with time-series fragmentation data
  - Test with various fragmentation scenarios and severity levels

- **Backup Testing**
  - Test compression comparison with various backup strategies
  - Validate efficiency calculations against actual backup sizes
  - Verify recommendation quality against expert configurations
  - Test with different data types and compression algorithms

## Success Criteria
1. Successfully identify and classify database files with at least 99% accuracy across supported engines
2. Generate transaction log recommendations that reduce log storage requirements by at least 30%
3. Identify index optimization opportunities that reduce storage by 20%+ while maintaining or improving performance
4. Accurately detect and assess fragmentation with recommendations that improve access times by at least 15%
5. Provide backup configuration recommendations that reduce backup storage requirements by at least 25%
6. Process and analyze database environments up to 100TB in size with minimal impact on production systems

To set up your development environment:
```bash
# Create and activate a virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -e .
```