# FieldShare - A Resilient P2P File Sharing System for Remote Field Research

## Overview
FieldShare is a specialized peer-to-peer file sharing system designed for environmental researchers working in remote locations with limited or intermittent connectivity. It enables the reliable exchange of scientific data between field teams and base stations through optimized transfer protocols that adapt to challenging network conditions, ensuring that vital research data can be shared even in the most isolated field sites.

## Persona Description
Marco conducts environmental research in remote areas with limited internet connectivity. He needs to share large datasets with colleagues at base camp and headquarters without relying on stable internet connections or central servers.

## Key Requirements
1. **Intermittent Connectivity Optimization**
   - Implementation of store-and-forward techniques that queue transmissions when peers are disconnected
   - Critical for Marco because his field sites often experience unpredictable connectivity, requiring a system that can automatically resume transfers when connections return without losing progress
   - Must include intelligent reconnection strategies, partial transfer resumption, and metadata synchronization that works efficiently during brief connection windows

2. **Bandwidth-Aware Synchronization Prioritization**
   - Smart transfer scheduling that prioritizes critical data first when bandwidth is constrained
   - Essential for Marco's work as he needs to ensure that the most important research findings (e.g., anomalous readings or time-sensitive measurements) reach colleagues before less critical data when operating on limited satellite or cellular connections
   - Requires configurable priority assignment for different data types and adaptive bandwidth allocation based on connection quality

3. **Mesh Networking Support**
   - Local network infrastructure for creating sharing networks without external internet access
   - Vital for Marco's distributed research teams who often work within radio range of each other but beyond cellular coverage, enabling them to establish local data sharing networks that operate independently
   - Implementation should include automatic peer discovery on local networks, efficient routing between multiple hops, and synchronization protocols that work across the mesh

4. **Data Collection Device Integration**
   - Support for direct data transfer from scientific instruments to the P2P network
   - Important because Marco's team uses various specialized measurement devices (weather stations, water quality sensors, tracking devices) that generate data requiring seamless integration into the sharing system without manual file handling
   - Must include device protocol adapters, automated data formatting, and scheduled collection capabilities

5. **Differential Sync for Dataset Updates**
   - Efficient updating of previously shared datasets with only new or changed readings
   - Critical for Marco as his datasets grow over time with new measurements, making full retransmission impractical over constrained connections - differential sync dramatically reduces the bandwidth needed to keep distributed copies updated
   - Should include efficient change detection, binary differencing, and transaction-based update mechanism to ensure dataset consistency

## Technical Requirements
- **Testability Requirements**
  - Simulation framework for testing under various connectivity conditions
  - Mocked scientific instruments for testing device integration
  - Bandwidth throttling capabilities for validating prioritization features
  - Verification tools for confirming data integrity after interrupted transfers
  - Test harnesses for validating mesh network performance under various topologies

- **Performance Expectations**
  - Efficient operation on devices with limited resources (field laptops, tablets)
  - Battery usage optimization for extended field operation
  - Minimal CPU and memory footprint during idle periods
  - Maximum utilization of available bandwidth during brief connectivity windows
  - Support for datasets up to 100GB with efficient differential updates

- **Integration Points**
  - Standard scientific instrument data formats (CSV, HDF5, FITS)
  - Common environmental sensor protocols and APIs
  - GPS and location services for geo-tagging shared data
  - Satellite modem and radio communication systems
  - Data analysis and visualization tools used in environmental research

- **Key Constraints**
  - Must operate reliably on unstable connections with high latency (>1000ms)
  - Must handle extended offline periods (days or weeks) without data loss
  - Must preserve battery life on field equipment
  - Must ensure data integrity despite frequent connection interruptions
  - No reliance on cloud services or stable internet infrastructure

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
FieldShare must provide a complete peer-to-peer solution for scientific data sharing under challenging conditions with these core components:

1. A resilient P2P network layer designed for unstable connections with store-and-forward capabilities
2. A data synchronization system with differential updates and prioritization based on content importance
3. A local mesh networking stack that enables field teams to share data without external connectivity
4. Device integration modules that can automatically ingest data from scientific instruments
5. A robust metadata system for tracking dataset versions, updates, and priorities
6. Bandwidth management tools that optimize transfer strategies based on connection quality
7. A data integrity verification system that ensures accuracy across interrupted transfers
8. A scheduling system for automated synchronization during expected connectivity windows

The system should provide Python APIs that can be integrated into existing scientific workflows and field research tools, with clear programmatic access to all key features.

## Testing Requirements
The implementation must include comprehensive test suites verifying:

- **Key Functionalities**
  - Validation of successful data transfers under intermittent connectivity
  - Verification of correct priority-based bandwidth allocation
  - Confirmation of mesh network formation and data propagation
  - Validation of scientific instrument data ingestion accuracy
  - Verification of differential sync correctness and efficiency

- **Critical User Scenarios**
  - A field researcher collecting and sharing data during a multi-week expedition
  - A team of researchers creating a local mesh network to aggregate findings
  - A base station receiving prioritized data during brief satellite connection windows
  - Direct ingestion of data from various scientific instruments
  - Gradual synchronization of large datasets as researchers return to connectivity

- **Performance Benchmarks**
  - Successful transfer of 1GB dataset over connections with 50% packet loss
  - Differential sync reducing update bandwidth by at least 90% for typical dataset changes
  - Mesh network supporting at least 20 nodes with multi-hop data propagation
  - Battery impact not exceeding 10% above baseline for typical field device operation
  - System overhead under 15% of available CPU/memory on target field devices

- **Edge Cases and Error Conditions**
  - Recovery from completely interrupted transfers without data corruption
  - Handling of conflicting dataset updates from disconnected researchers
  - Adaptation to extremely degraded network conditions (>2000ms latency, <1KB/s throughput)
  - Proper operation when devices join/leave the mesh unpredictably
  - Graceful handling of device power loss during transfer operations

- **Required Test Coverage Metrics**
  - Minimum 90% statement coverage for all modules
  - Dedicated tests for each connectivity challenge scenario
  - Comprehensive validation of data integrity preservation mechanisms
  - Performance tests validating operation within resource constraints
  - Simulation tests for extended field deployment scenarios

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
The implementation will be considered successful when:

1. Data transfers reliably complete despite extended connectivity interruptions
2. Critical research data propagates with appropriate priority under bandwidth constraints
3. Field teams can establish functional mesh networks without external internet access
4. Scientific instruments can directly contribute data to the sharing network
5. Dataset updates transmit efficiently using minimal bandwidth
6. The system operates within the resource constraints of typical field equipment
7. Data integrity is maintained throughout the sharing process regardless of connection quality
8. The solution integrates smoothly with existing environmental research workflows

To set up your development environment, follow these steps:

1. Use `uv init --lib` to set up the project and create your `pyproject.toml`
2. Install dependencies with `uv sync`
3. Run your code with `uv run python your_script.py`
4. Run tests with `uv run pytest`
5. Format your code with `uv run ruff format`
6. Lint your code with `uv run ruff check .`
7. Type check with `uv run pyright`