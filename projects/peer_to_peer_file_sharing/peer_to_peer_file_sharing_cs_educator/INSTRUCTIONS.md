# P2P-Teach - Educational Peer-to-Peer Networking Framework

## Overview
P2P-Teach is an educational library that demonstrates distributed networking concepts through a functional peer-to-peer file sharing implementation. It provides visualization capabilities, configurable failure simulation, protocol inspection, distributed algorithm visualization, and performance measurement tools specifically designed for teaching distributed systems concepts in computer science courses.

## Persona Description
Dr. Rodriguez teaches distributed systems courses at a university and needs a practical demonstration tool for peer-to-peer concepts. She wants students to visualize and experiment with distributed networking principles through hands-on assignments that illustrate theoretical concepts.

## Key Requirements

1. **Network Topology Visualization**
   - Implement a data collection and representation system that tracks peer connections and data flows
   - This is essential for Dr. Rodriguez to help students visualize abstract network concepts concretely
   - The system should record connection events, data transfers, and routing decisions to generate network topology data
   - Output should be structured to enable visualization through external tools or simple rendering libraries

2. **Configurable Failure Simulation**
   - Create a comprehensive failure injection framework that can simulate various network problems
   - Critical for teaching network resilience and fault tolerance in distributed systems
   - Must support different failure types: node crashes, network partitions, packet loss, latency spikes, and Byzantine behavior
   - Should allow programmatic configuration of when, where, and how failures occur

3. **Protocol Inspection Tools**
   - Develop a message capture and analysis system that reveals underlying protocol exchanges
   - Essential for students to understand how peers communicate in a distributed system
   - Should support filtering, formatting, and analyzing different message types
   - Must preserve message ordering, timing, and relationship to help understand protocol flows

4. **Distributed Algorithm Visualization**
   - Implement instrumentation for DHT operations and routing decisions
   - Crucial for demonstrating how distributed algorithms work in practice
   - Should track key distributed operations: key lookup, node joining/leaving, and value storage
   - Must generate data that shows step-by-step algorithm execution

5. **Performance Measurement Framework**
   - Create a system to benchmark and compare different peer discovery strategies
   - Important for teaching optimization and trade-offs in distributed systems design
   - Should measure key metrics: time to discover peers, message overhead, and resilience to churn
   - Must support side-by-side comparison of different strategies

## Technical Requirements

- **Testability Requirements**
  - All components must be designed with testability as a primary concern
  - Simulated network environments must be reproducible with fixed random seeds
  - Clock and timing must be injectable for deterministic testing
  - Metrics collection must be non-intrusive to avoid affecting the system being measured

- **Performance Expectations**
  - Visualization data generation must not add more than 10% overhead to normal operations
  - Failure simulation must be precise in timing and scope
  - Protocol inspection must capture 100% of messages without loss
  - Performance measurements must be accurate within 5% margin of error

- **Integration Points**
  - Data export interfaces for visualization tools
  - Configuration interfaces for failure simulation
  - Hooks for protocol message interception
  - Logging and tracing interfaces for algorithm visualization
  - Metrics collection and export for performance measurement

- **Key Constraints**
  - All functionality must be implemented without UI components
  - Data output must be in standard formats (JSON, CSV) for compatibility with visualization tools
  - Implementation must be pure Python to maximize accessibility for students
  - Design must prioritize clarity and educational value over optimization

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The P2P-Teach implementation should provide these core functions:

1. **Educational P2P Network Core**
   - Modular peer-to-peer networking infrastructure with clear separation of concerns
   - Well-commented implementation of distributed hash table and routing
   - Clean, educational reference implementation of core P2P protocols

2. **Instrumentation and Data Collection**
   - Comprehensive hooks for collecting network events and metrics
   - Non-intrusive monitoring of internal operations
   - Structured data output for all monitored aspects

3. **Failure Injection Framework**
   - Programmatic interface for defining failure scenarios
   - Precise timing and targeting of network problems
   - Multiple failure types and patterns

4. **Protocol Analysis Tools**
   - Message capturing, formatting, and analysis
   - Protocol flow reconstruction
   - Message sequence charting capabilities

5. **Algorithm Visualization Support**
   - Step-by-step tracing of distributed operations
   - State collection at key decision points
   - Relationship tracking between events and decisions

6. **Performance Measurement System**
   - Configurable benchmark scenarios
   - Metrics collection with statistical analysis
   - Strategy comparison framework

## Testing Requirements

- **Key Functionalities to Verify**
  - Accurate collection of network topology information
  - Proper implementation of various failure scenarios
  - Complete protocol message capture and formatting
  - Correct tracing of distributed algorithm execution
  - Accurate performance measurement across different strategies

- **Critical User Scenarios**
  - Demonstrating network structure changes as peers join and leave
  - Injecting failures to show system resilience mechanisms
  - Capturing and analyzing protocol exchanges during specific operations
  - Visualizing key DHT operations like node joining and key lookup
  - Comparing performance of different peer discovery algorithms

- **Performance Benchmarks**
  - Data collection overhead must remain below 10% even with 100+ simulated peers
  - Failure injection must be accurate to within 50ms of specified timing
  - Protocol inspection must handle at least 1000 messages per second
  - Visualization data generation must complete within 5 seconds for complex operations

- **Edge Cases and Error Handling**
  - Correct behavior when multiple failures occur simultaneously
  - Proper handling of extreme network conditions
  - Robust operation when monitoring high-frequency message exchanges
  - Accurate measurement even with highly variable performance patterns

- **Test Coverage Requirements**
  - Minimum 95% code coverage for core functionality
  - All failure scenarios must be tested with different configurations
  - Protocol inspection must be tested with all message types
  - Algorithm visualization must cover all key distributed operations
  - Performance measurement must be validated against known reference points

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

1. It provides clear, educational demonstrations of peer-to-peer networking concepts
2. The network topology data accurately represents the actual network state
3. Failure simulation properly creates the specified network problems
4. Protocol inspection captures all message exchanges in appropriate detail
5. Algorithm visualization clearly shows the execution of distributed operations
6. Performance measurement accurately compares different peer discovery strategies
7. All components are implemented as well-documented, testable Python modules

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