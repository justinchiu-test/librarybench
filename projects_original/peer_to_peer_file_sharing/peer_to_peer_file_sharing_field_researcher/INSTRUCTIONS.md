# FieldSync - Resilient Data Sharing for Remote Research

## Overview
FieldSync is a specialized peer-to-peer file sharing library designed for environmental researchers working in remote locations with limited connectivity. It enables resilient data sharing between field sites and base stations through intermittent connectivity optimization, bandwidth-aware synchronization, mesh networking, scientific instrument integration, and differential synchronization.

## Persona Description
Marco conducts environmental research in remote areas with limited internet connectivity. He needs to share large datasets with colleagues at base camp and headquarters without relying on stable internet connections or central servers.

## Key Requirements

1. **Intermittent Connectivity Optimization**
   - Implement store-and-forward techniques that queue and resume transfers when connections are re-established
   - Critical for Marco's fieldwork in areas where network connectivity is unpredictable and intermittent
   - Must preserve transfer state and resume from interruption points without data loss
   - Should include intelligent retry mechanisms with exponential backoff to conserve battery power

2. **Bandwidth-Aware Synchronization**
   - Create a prioritization system that transfers critical data first when connections are limited
   - Essential for ensuring that the most important research data reaches colleagues despite poor connectivity
   - Must support user-defined priority levels for different data types
   - Should dynamically adjust transfer rates based on available bandwidth and remaining battery life

3. **Mesh Networking Support**
   - Develop peer-to-peer mesh networking capabilities for creating local sharing networks without internet access
   - Vital for maintaining data flow between researchers spread across a remote study site
   - Must support ad-hoc network formation using available wireless technologies
   - Should optimize routing to minimize power consumption while maximizing data throughput

4. **Data Collection Device Integration**
   - Implement interfaces for direct data transfer from common scientific instruments
   - Important for automating the collection and sharing of environmental sensor data
   - Must support common scientific data formats and protocols
   - Should include metadata preservation to maintain context and calibration information

5. **Differential Sync for Dataset Updates**
   - Create efficient synchronization that only transfers changes made to previously shared datasets
   - Critical for reducing bandwidth needs when updating large environmental datasets with small changes
   - Must correctly identify and extract only the modified portions of complex data files
   - Should maintain version history to allow rollback to previous states if needed

## Technical Requirements

- **Testability Requirements**
  - All network resilience features must be testable with simulated connectivity disruptions
  - Bandwidth optimization must be testable with configurable bandwidth limitations
  - Mesh networking capabilities must be testable in simulated multi-node environments
  - Scientific instrument integration must be testable with mock instrument data sources

- **Performance Expectations**
  - System must operate efficiently on devices with limited processing power and battery capacity
  - Synchronization must minimize data transfer to conserve bandwidth (at least 80% reduction for incremental updates)
  - Mesh network throughput must achieve at least 50% of theoretical maximum for the simulated radio technology
  - Storage requirements must be optimized for devices with limited capacity

- **Integration Points**
  - Common scientific data formats (CSV, NetCDF, HDF5, GeoTIFF, etc.)
  - Standard instrument communication protocols
  - Common wireless technologies (WiFi, Bluetooth, LoRa where appropriate)
  - GPS/location services for geographic metadata

- **Key Constraints**
  - All functionality must operate without reliance on internet connectivity
  - Power efficiency must be a primary consideration in all operations
  - Implementation must be pure Python with minimal dependencies
  - All algorithms must be robust against frequent disruptions and failures

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The FieldSync implementation should provide these core functions:

1. **Resilient Data Transfer**
   - Robust peer-to-peer file transfer with interruption recovery
   - Queue management for pending transfers
   - Transfer resumption from point of interruption
   - Progress tracking and state preservation

2. **Adaptive Bandwidth Management**
   - Data prioritization based on user-defined importance
   - Dynamic bandwidth allocation based on network conditions
   - Throttling based on available power and connectivity
   - Scheduling of non-critical transfers during optimal conditions

3. **Local Mesh Networking**
   - Peer discovery in offline environments
   - Multi-hop data routing between research team members
   - Network topology management and optimization
   - Adaptive routing based on connection quality

4. **Scientific Instrument Connectivity**
   - Data adapters for common field instruments
   - Automated data collection and sharing
   - Metadata preservation and enrichment
   - Calibration data handling

5. **Efficient Dataset Synchronization**
   - Change detection in complex scientific datasets
   - Delta encoding and transfer
   - Version tracking and conflict resolution
   - Verification of data integrity

## Testing Requirements

- **Key Functionalities to Verify**
  - Transfers successfully resume after connectivity interruptions
  - High-priority data transfers before low-priority data in bandwidth-limited scenarios
  - Mesh network successfully routes data across multiple hops
  - Instrument data is correctly captured and shared with metadata intact
  - Differential sync correctly identifies and transfers only changed data

- **Critical User Scenarios**
  - Collecting and synchronizing environmental sensor data in areas with sporadic connectivity
  - Sharing urgent findings with base camp despite limited bandwidth
  - Maintaining data flow among a distributed research team via mesh network
  - Integrating data from multiple scientific instruments into a cohesive dataset
  - Efficiently updating central databases with field amendments to existing datasets

- **Performance Benchmarks**
  - Transfers must resume within 5 seconds of connectivity restoration
  - Bandwidth prioritization must ensure critical data transfers at least 5x faster than low-priority data
  - Mesh networking must support at least 5 hops with less than 50% throughput degradation
  - Differential sync must achieve at least 90% bandwidth savings for typical dataset updates
  - System must operate for at least 12 hours on a standard laptop battery

- **Edge Cases and Error Handling**
  - Correct behavior during prolonged connectivity loss (days or weeks)
  - Proper handling of conflicting updates from disconnected researchers
  - Recovery from corrupted transfer state
  - Graceful degradation when battery power is critically low
  - Maintaining data integrity during unexpected device shutdown

- **Test Coverage Requirements**
  - All core resilience functions must have 100% test coverage
  - Simulated field conditions must test end-to-end functionality
  - Power consumption must be measured and verified in tests
  - Error recovery paths must be thoroughly tested

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

1. It reliably shares research data despite intermittent and limited connectivity
2. Critical data successfully transfers even with severe bandwidth constraints
3. Local mesh networks enable data sharing without internet access
4. Scientific instruments can directly contribute data to the shared repository
5. Dataset updates transfer efficiently using differential synchronization
6. All operations are power-efficient and suitable for field conditions
7. The system is robust against the connectivity challenges of remote fieldwork

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Setup Instructions

1. Setup a virtual environment using `uv venv`
2. Activate the environment with `source .venv/bin/activate`
3. Install the project with `uv pip install -e .`
4. Install test dependencies with `uv pip install pytest pytest-json-report`

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```