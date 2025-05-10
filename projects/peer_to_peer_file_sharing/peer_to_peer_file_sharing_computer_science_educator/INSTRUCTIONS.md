# PeerShare Educational - A Peer-to-Peer File Sharing System for Computer Science Education

## Overview
PeerShare Educational is a specialized peer-to-peer file sharing system designed specifically for computer science education. It provides visual and interactive tools to demonstrate distributed systems concepts, allowing students to observe, experiment with, and analyze the inner workings of P2P networks through hands-on assignments that bridge theoretical concepts with practical implementation.

## Persona Description
Dr. Rodriguez teaches distributed systems courses at a university and needs a practical demonstration tool for peer-to-peer concepts. She wants students to visualize and experiment with distributed networking principles through hands-on assignments that illustrate theoretical concepts.

## Key Requirements
1. **Network Topology Visualization Module**
   - Real-time visualization of peer connections and data flows within the P2P network
   - This feature is critical for Dr. Rodriguez's students to see abstract network concepts materialize visually, making it easier to understand complex distributed topologies and how they evolve over time
   - Visualization must include nodes, connections, and data transfer activities with clear visual indicators for different types of peers and their roles in the network

2. **Configurable Failure Simulation System**
   - Introduction of various network problems (latency, packet loss, node disconnection, Byzantine behavior) for resilience testing
   - Essential for teaching fault tolerance in distributed systems, allowing students to observe how the network adapts to different failure scenarios, reinforcing theoretical concepts about system resilience
   - Failure scenarios should be configurable through an API with precise control over timing, duration, and failure characteristics

3. **Protocol Inspection Tools**
   - Detailed observation of message exchange between peers, including packet structure and protocol mechanics
   - Critical for students to understand the underlying communication patterns in distributed systems, providing visibility into how abstract protocol designs translate to actual messages
   - Must capture and present protocol messages in formats suitable for analysis, with filtering and search capabilities

4. **Distributed Algorithm Visualization**
   - Clear illustration of DHT operations, routing decisions, and consensus mechanisms
   - Important for demonstrating how distributed algorithms execute across multiple nodes, helping students trace the step-by-step progression of complex algorithms
   - Visualizations should highlight key algorithm states, decision points, and information propagation

5. **Performance Measurement Framework**
   - Comparative analysis tools for different peer discovery strategies and network configurations
   - Essential for empirical evaluation of different approaches to distributed system design, allowing students to collect data and evaluate tradeoffs between different implementations
   - Must include metrics collection, statistical analysis, and experimental controls for fair comparison

## Technical Requirements
- **Testability Requirements**
  - All components must be designed with observable internal states for verification
  - Simulation environment must support deterministic runs for reproducible results
  - Events and actions must be logged with timestamps for sequence verification
  - Support for automated test scenarios to verify specific distributed systems concepts

- **Performance Expectations**
  - Support for simulating networks of up to 1000 virtual peers on a standard development machine
  - Visualization components must maintain responsiveness even with large network simulations
  - Analysis functions should scale efficiently with network size and message volume
  - Low overhead monitoring to avoid significantly altering system behavior when observed

- **Integration Points**
  - Python APIs for programmatic control of all simulation aspects
  - Standardized data export for analysis in external tools (CSV, JSON)
  - Hooks for custom algorithm implementations to be tested in the simulation environment
  - Integration with Jupyter notebooks for interactive educational experiences

- **Key Constraints**
  - All visualizations must be generated as data structures, not direct UI components
  - System must support headless operation for automated testing
  - Implementation should use cross-platform Python libraries only
  - Modular design allowing individual components to be studied in isolation

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
PeerShare Educational must provide a comprehensive simulation environment for P2P networks with these core components:

1. A foundational P2P network implementation with a Kademlia-based DHT for peer discovery
2. A network simulation layer that models realistic network conditions, including latency, bandwidth constraints, and failures
3. Instrumentation to capture and expose internal network events and message exchanges
4. Data structures that represent network topology, message routing, and data transfers in formats suitable for visualization
5. Analytical tools that measure performance metrics across different network configurations
6. Interfaces to programmatically inject faults, modify configuration, and control simulations
7. A comprehensive logging system that records all significant events for analysis

The system should be designed as a Python library that can be used programmatically in educational settings, with clear separation between the core P2P functionality and the educational tools built around it.

## Testing Requirements
The implementation must include comprehensive test suites verifying:

- **Key Functionalities**
  - Verification of correct DHT operations under normal conditions
  - Confirmation that network topology is accurately represented in data structures
  - Validation that protocol messages are correctly captured and represented
  - Proof that performance metrics accurately reflect system behavior
  - Confirmation that failure simulations correctly impact the network as specified

- **Critical User Scenarios**
  - Running a distributed systems lab session with simulated network conditions
  - Comparing different DHT implementations for performance characteristics
  - Tracing the execution of specific distributed algorithms
  - Analyzing network resilience under various failure conditions
  - Collecting experimental data for student analysis

- **Performance Benchmarks**
  - System should support at least 100 simulated peers on a standard laptop
  - Visualization data structures should generate within 500ms even for large networks
  - Protocol capture should handle message rates of at least 1000 messages per second
  - Analysis calculations should complete within 5 seconds for standard metrics

- **Edge Cases and Error Conditions**
  - Graceful handling of pathological network configurations
  - Proper isolation of failures in simulation vs failures in the framework itself
  - Accurate simulation of rare but important distributed systems scenarios (network partitions, Byzantine failures)
  - Handling of extremely large data sets and high message volumes

- **Required Test Coverage Metrics**
  - Minimum 90% statement coverage for all modules
  - Explicit tests for each key distributed systems concept
  - Performance tests validating scalability requirements
  - Validation tests confirming accuracy of simulated network behavior against theoretical models

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
The implementation will be considered successful when:

1. Students can observe and interact with working demonstrations of all major distributed systems concepts covered in a typical university course
2. The system accurately simulates network behavior consistent with theoretical models
3. All key performance metrics show that the system can handle networks of sufficient size for educational purposes
4. Instructors can create custom experiments and assignments that clearly demonstrate specific P2P concepts
5. Test suites confirm the correct operation of all components under various conditions
6. The library can be integrated into existing educational workflows, including assignments and lab sessions

To set up your development environment, follow these steps:

1. Use `uv init --lib` to set up the project and create your `pyproject.toml`
2. Install dependencies with `uv sync`
3. Run your code with `uv run python your_script.py`
4. Run tests with `uv run pytest`
5. Format your code with `uv run ruff format`
6. Lint your code with `uv run ruff check .`
7. Type check with `uv run pyright`