# Educational P2P Network Visualization Framework

## Overview
A pedagogical peer-to-peer networking framework designed specifically for computer science education, allowing students to visualize, experiment with, and analyze distributed systems concepts through hands-on interaction with real P2P protocols and simulated network conditions.

## Persona Description
Dr. Rodriguez teaches distributed systems courses at a university and needs a practical demonstration tool for peer-to-peer concepts. She wants students to visualize and experiment with distributed networking principles through hands-on assignments that illustrate theoretical concepts.

## Key Requirements
1. **Network Topology Visualization**
   - Real-time interactive visualization of peer connections and data flows
   - Ability to view the network from different perspectives (global view, single peer view)
   - Visual representation of node relationships, routing paths, and data transfer
   - Critical for students to understand abstract distributed concepts through visual learning

2. **Configurable Failure Simulation**
   - Injection of various network problems (packet loss, latency, node failures, network partitions)
   - Controls for triggering specific failure scenarios during demonstrations
   - Ability to script failure sequences for reproducible experiments
   - Essential for teaching resilience and fault tolerance in distributed systems

3. **Protocol Inspection Tools**
   - Capture and display of actual message exchanges between peers
   - Filtering and search capabilities for protocol messages
   - Ability to modify messages for experimental purposes
   - Crucial for connecting theory with implementation details and understanding protocol design

4. **Distributed Algorithm Visualization**
   - Step-by-step visualization of DHT operations and routing decisions
   - Illustration of key algorithms (Kademlia routing, consistent hashing)
   - Ability to pause, step through, and replay algorithm execution
   - Vital for demystifying complex distributed algorithms and internal operations

5. **Performance Measurement Framework**
   - Collection and visualization of performance metrics
   - Comparative analysis tools for different peer discovery strategies
   - Exportable data for student analysis and reporting
   - Necessary for teaching empirical evaluation of distributed system designs

## Technical Requirements
### Testability Requirements
- All components must have comprehensive unit tests with >90% coverage
- Algorithm correctness must be verifiable through automated tests
- Visualization components must be testable without GUI dependencies
- Network simulation components must support deterministic testing scenarios
- Metrics collection must be validated for accuracy

### Performance Expectations
- Support for simulating networks of at least 100 nodes on standard hardware
- Visualization updates at minimum 5 frames per second during active simulations
- Protocol inspection with negligible impact on network operation
- Algorithm visualization with step timing controls from 10ms to 10s per step
- Ability to run accelerated simulations at least 10x real-time speed

### Integration Points
- Export data in CSV/JSON formats for external analysis
- Programmatic API for scripting experiments and scenarios
- Hooks for custom algorithm implementations
- Integration with standard network simulation tools
- Support for custom visualization extensions

### Key Constraints
- All network functionality must be implemented in pure Python
- No external databases or servers required for operation
- Visualization logic must be separable from network implementation
- Must run on standard classroom computing equipment
- No UI components in core library (visualization through data structures only)

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The system must be implemented as a library with the following components:

1. **Network Core**
   - Implementation of P2P protocols (especially Kademlia DHT)
   - Chunked file transfer with verification
   - Socket and connection management
   - Message serialization and parsing

2. **Simulation Engine**
   - Network topology management
   - Configurable network conditions
   - Time-based event simulation
   - Failure injection system

3. **Data Collection**
   - Metrics gathering from all nodes
   - Performance statistics calculation
   - Event logging and timestamping
   - Data aggregation and export

4. **Visualization Data Structures**
   - Network state representation
   - Message flow tracking
   - Algorithm state capture
   - Graph representation for topology

5. **Educational Components**
   - Annotated algorithm implementations
   - Step-by-step operation decomposition
   - Scenario definitions for common distributed systems problems
   - Comparative framework for algorithm evaluation

## Testing Requirements
### Key Functionalities to Verify
- Accurate implementation of Kademlia DHT and routing
- Correct operation of chunked file transfer protocols
- Proper implementation of network failure simulations
- Accurate collection and calculation of performance metrics
- Correct capture and representation of network state for visualization

### Critical Scenarios to Test
- Network operation under various scales (10, 50, 100 nodes)
- System behavior during node joins, graceful departures, and failures
- Routing table construction and maintenance
- Data location and retrieval with and without failures
- Performance under different network topologies

### Performance Benchmarks
- Time to stabilize network after node additions (varies by network size)
- Message efficiency of peer discovery
- Routing efficiency compared to theoretical optimum
- Resource usage scales sub-linearly with network size
- Simulation speed vs. accuracy tradeoffs

### Edge Cases and Error Conditions
- Network partitions and eventual recovery
- Byzantine node behavior (incorrect protocol implementation)
- Extremely high churn rates (nodes rapidly joining/leaving)
- Operation with minimal peers available
- Recovery from corrupted routing tables
- Resource exhaustion scenarios

### Required Test Coverage
- ≥90% line coverage for core protocol implementation
- 100% coverage of failure injection mechanisms
- ≥85% coverage for simulation components
- ≥90% coverage for metrics collection
- All algorithms must have dedicated correctness tests

## Success Criteria
The implementation will be considered successful when:

1. Students can run experiments that demonstrate key distributed systems concepts without becoming bogged down in implementation details
2. The visualization accurately represents the actual state of the network and algorithm execution
3. Failure simulations reliably produce the expected system behaviors for teaching resilience
4. Performance metrics accurately reflect system behavior under various conditions
5. All five key requirements are fully implemented and testable via pytest
6. Dr. Rodriguez can use the framework to create new teaching scenarios without modifying the core code
7. Students report improved understanding of distributed systems concepts through post-lab assessments

To set up the development environment, use `uv venv` to create a virtual environment. From within the project directory, the environment can be activated with `source .venv/bin/activate`.