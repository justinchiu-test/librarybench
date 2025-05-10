# Resilient Field Data Synchronization System

## Overview
A specialized peer-to-peer file sharing system designed for environmental research teams working in remote locations with intermittent connectivity, enabling reliable data collection, storage, and synchronization across distributed field sites without requiring continuous internet access.

## Persona Description
Marco conducts environmental research in remote areas with limited internet connectivity. He needs to share large datasets with colleagues at base camp and headquarters without relying on stable internet connections or central servers.

## Key Requirements
1. **Intermittent Connectivity Optimization**
   - Store-and-forward capability retaining files for transfer when peers reconnect
   - Connection opportunity detection and prioritized queue processing
   - Automatic retry and resume of interrupted transfers
   - Essential for Marco's team to exchange data despite frequent connection drops in remote field sites

2. **Bandwidth-Aware Synchronization**
   - Adaptive data transfer rates based on available connection quality
   - Configurable prioritization system for critical vs. non-critical data
   - Compression and optimization for low-bandwidth scenarios
   - Critical because field sites often rely on satellite or cellular connections with severe bandwidth limitations

3. **Mesh Networking Support**
   - Device discovery and connection across local networks without internet
   - Multi-hop routing to extend network reach in field camps
   - Dynamic topology adaptation as devices move or power down
   - Necessary for creating functional data sharing networks at field sites completely disconnected from external infrastructure

4. **Data Collection Device Integration**
   - API for direct transfer from scientific instruments and data loggers
   - Support for common field equipment protocols and data formats
   - Automated ingestion of new readings without manual intervention
   - Vital for streamlining the workflow from data collection to sharing, reducing manual steps in harsh field conditions

5. **Differential Sync for Dataset Updates**
   - Efficient updating of previously shared datasets with only new readings
   - Version tracking of evolving datasets across the research team
   - Conflict detection and resolution for concurrent updates
   - Essential for minimizing data transfer requirements when updating time-series or growing datasets from ongoing field research

## Technical Requirements
### Testability Requirements
- All components must have comprehensive unit tests with >90% coverage
- Simulated network conditions for testing intermittent connectivity scenarios
- Deterministic mesh network simulation for topology testing
- Reproducible differential sync tests with various dataset types
- Mock integration points for scientific instrument data sources

### Performance Expectations
- Efficient operation on low-power field equipment (laptops, tablets, data loggers)
- Minimal battery impact during idle periods with fast wake-on-connection
- Support for datasets up to 100GB in size
- Efficient differential updates (transfer < 110% of actual changed data)
- Mesh operation with at least 20 connected nodes spanning 3 hops

### Integration Points
- Common scientific data format support (CSV, HDF5, NetCDF)
- Standard instrument integration (Campbell Scientific, HOBO data loggers)
- GPS and location awareness for positional data tagging
- Export capabilities for GIS and analysis software
- Metadata preservation through all synchronization operations

### Key Constraints
- Must operate on standard field equipment (Windows/Linux laptops, Android tablets)
- No cloud dependencies for core functionality
- Minimal configuration requirements for field deployment
- All operations possible through programmatic API
- Maximum memory usage appropriate for field-grade hardware

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The system must be implemented as a library with the following components:

1. **Store-and-Forward Engine**
   - Persistent queue management for pending transfers
   - Metadata tracking for partially transferred files
   - Priority-based scheduling for outbound data
   - Connection state detection and optimization

2. **Bandwidth Management**
   - Connection quality detection and monitoring
   - Adaptive transfer rate control
   - Priority-based resource allocation
   - Compression selection based on data type and urgency

3. **Mesh Network Protocol**
   - Peer discovery on local networks
   - Routing table management for multi-hop transfers
   - Path optimization for efficient data movement
   - Network state monitoring and adaptation

4. **Device Integration Framework**
   - Abstract interface for data collection devices
   - Protocol implementations for common scientific equipment
   - Data format conversion and normalization
   - Automated acquisition scheduling

5. **Differential Synchronization**
   - Dataset version tracking and management
   - Change detection algorithms for various data types
   - Conflict identification and resolution strategies
   - Metadata preservation through sync operations

## Testing Requirements
### Key Functionalities to Verify
- Reliable data transfer across intermittent connections
- Efficient bandwidth utilization under constrained conditions
- Correct mesh network formation and adaptation
- Accurate integration with supported data collection devices
- Proper differential synchronization with various dataset types and change patterns

### Critical Scenarios to Test
- Data integrity through store-and-forward operations
- Transfer prioritization under bandwidth constraints
- Mesh network operation across multiple hops
- Complete data collection workflows from instruments to analysis
- Concurrent updates to shared datasets from multiple field teams

### Performance Benchmarks
- Battery impact vs. data throughput efficiency
- Reconnection and recovery times after disruption
- Bandwidth utilization efficiency (>80% of theoretical maximum)
- Time to synchronize various dataset sizes and change patterns
- Memory footprint during idle and active operations

### Edge Cases and Error Conditions
- Extremely limited bandwidth scenarios (<1 Kbps)
- Frequent connection disruptions during active transfers
- Device disappearance from mesh network during transfers
- Corrupt or incomplete data from collection devices
- Conflicting concurrent changes to the same dataset regions
- Recovery from power loss during transfer operations

### Required Test Coverage
- ≥90% line coverage for core transfer protocols
- 100% coverage of data integrity verification mechanisms
- ≥85% coverage for mesh networking components
- ≥90% coverage for device integration framework
- ≥95% coverage for differential sync algorithms

## Success Criteria
The implementation will be considered successful when:

1. Field teams can reliably exchange data despite challenging connectivity conditions
2. Critical research data receives priority treatment when bandwidth is limited
3. Researchers can form functional data sharing networks regardless of internet availability
4. Data flows directly from collection devices into the shared research ecosystem
5. Dataset updates minimize bandwidth requirements through efficient differential synchronization
6. All five key requirements are fully implemented and testable via pytest
7. Battery life impact is minimized while maintaining data sharing capabilities
8. Research workflow is accelerated by reducing manual data handling steps

To set up the development environment, use `uv venv` to create a virtual environment. From within the project directory, the environment can be activated with `source .venv/bin/activate`.