# PyMigrate Scientific Data Migration Framework

## Overview
A specialized data migration framework designed for research scientists migrating petabyte-scale scientific datasets between computing clusters. This implementation optimizes for bandwidth constraints, storage efficiency, and data integrity while handling the unique challenges of large-scale scientific data migration.

## Persona Description
A research scientist migrating large scientific datasets between computing clusters who needs to optimize for bandwidth and storage constraints. He requires efficient compression and chunking strategies for petabyte-scale migrations.

## Key Requirements

1. **Adaptive compression selection based on data entropy analysis**
   - Intelligently selects optimal compression algorithms by analyzing data characteristics. Different scientific data types (genomic sequences, climate models, particle physics) benefit from different compression strategies, maximizing space savings while minimizing compression time.

2. **Bandwidth throttling with network congestion detection**
   - Prevents migration from impacting critical research computations by dynamically adjusting transfer rates. Monitors network conditions and automatically scales bandwidth usage based on available capacity and priority settings.

3. **Checksum verification with automatic corruption recovery**
   - Ensures data integrity for irreplaceable research data through multi-level checksumming. Detects corruption at chunk, file, and dataset levels with automatic retry and recovery mechanisms for damaged segments.

4. **Distributed chunk processing across multiple nodes**
   - Parallelizes migration across cluster nodes for maximum throughput. Implements intelligent chunk distribution considering node capabilities, network topology, and storage characteristics for optimal performance.

5. **Storage tier optimization for hot/cold data separation**
   - Automatically classifies and routes data to appropriate storage tiers based on access patterns. Frequently accessed data goes to high-performance storage while archival data utilizes cost-effective cold storage.

## Technical Requirements

### Testability Requirements
- All components must be testable via pytest without manual intervention
- Simulated large dataset handling without requiring actual petabytes
- Mock cluster environments with configurable node characteristics
- Network condition simulation for throttling tests

### Performance Expectations
- Compression ratios >50% for typical scientific datasets
- Sustained transfer rates >10GB/s on high-speed networks
- Chunk processing parallelization across 100+ nodes
- Checksum verification with <5% performance overhead

### Integration Points
- HPC job schedulers (SLURM, PBS) for resource allocation
- Parallel filesystems (Lustre, GPFS) optimization
- Object storage interfaces (S3, Swift) for cloud migrations
- Scientific data formats (HDF5, NetCDF, FITS) awareness

### Key Constraints
- Zero data corruption tolerance for research integrity
- Minimal impact on concurrent research workloads
- Support for datasets exceeding available RAM
- Resumable transfers for long-running migrations

**IMPORTANT**: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The framework must provide:

1. **Entropy-Based Compressor**: Analyzes data blocks for entropy and patterns, selects from compression algorithm suite (gzip, bzip2, lz4, zstd), applies parallel compression with tunable parameters, and tracks compression effectiveness metrics

2. **Adaptive Bandwidth Controller**: Monitors network utilization and latency, implements token bucket algorithm for rate limiting, responds to congestion signals dynamically, and provides priority-based bandwidth allocation

3. **Integrity Verification System**: Calculates checksums at multiple granularities, maintains checksum database for verification, implements Reed-Solomon error correction, and orchestrates automatic recovery procedures

4. **Distributed Chunk Manager**: Splits datasets into optimal chunk sizes, distributes chunks based on node capabilities, tracks chunk processing status centrally, and handles node failures with redistribution

5. **Storage Tier Classifier**: Analyzes data access patterns over time, applies ML-based classification for tier assignment, implements policy-based routing rules, and manages transparent tier migration

## Testing Requirements

### Key Functionalities to Verify
- Compression algorithm selection optimality for various data types
- Bandwidth throttling responsiveness to network conditions
- Checksum verification catching all corruption scenarios
- Distributed processing scaling linearly with nodes
- Storage tier classification accuracy

### Critical User Scenarios
- Migrating 1PB climate simulation dataset across data centers
- Handling network outages during multi-day transfers
- Recovering from corrupted chunks in genomic data migration
- Optimizing storage costs for historical telescope observations
- Parallelizing migration of millions of small files

### Performance Benchmarks
- Achieve 60% compression for structured scientific data
- Sustain 80% of available bandwidth without congestion
- Detect and recover corruption within 1% of data size
- Scale to 90% efficiency with 100 processing nodes
- Classify storage tiers with 95% accuracy

### Edge Cases and Error Conditions
- Incompressible random data handling
- Network bandwidth fluctuations during migration
- Node failures during distributed processing
- Checksum database corruption
- Storage tier capacity exhaustion

### Required Test Coverage
- Minimum 90% code coverage with pytest
- Compression effectiveness tests for scientific formats
- Network simulation tests for various conditions
- Distributed processing fault tolerance tests
- End-to-end migration validation tests

**IMPORTANT**:
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

The implementation is successful when:

1. **All tests pass** when run with pytest, with 90%+ code coverage
2. **A valid pytest_results.json file** is generated showing all tests passing
3. **Compression** achieves >50% reduction for typical scientific data
4. **Bandwidth control** maintains network stability during migration
5. **Integrity verification** detects and recovers from all corruption
6. **Distributed processing** scales efficiently to 100+ nodes
7. **Storage tiering** correctly classifies data with 95% accuracy

**REQUIRED FOR SUCCESS**:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup

To set up the development environment:

```bash
cd /path/to/data_migration_framework_research_scientist
uv venv
source .venv/bin/activate
uv pip install -e .
```

Install the project and run tests:

```bash
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```

**REMINDER**: The pytest_results.json file is MANDATORY and must be included to demonstrate that all tests pass successfully.