# Educational CPU Architecture Simulator

## Overview
A specialized virtual machine emulator designed for computer architecture education that provides clear visualization of CPU operation principles, including detailed pipeline stages, memory management, and instruction execution. This implementation focuses on transparency and demonstrability rather than performance, making complex concepts accessible to undergraduate students.

## Persona Description
Dr. Rodriguez teaches undergraduate computer architecture courses and needs to help students understand CPU operation principles without the complexity of modern processor designs. She wants a transparent virtual machine that clearly demonstrates fundamental concepts like fetch-decode-execute cycles and memory management.

## Key Requirements
1. **Pipeline Visualization System**: Implement a pipeline visualization component showing each instruction passing through fetch-decode-execute stages, allowing students to see how instructions flow through the CPU. This feature is critical for helping students understand the temporal nature of instruction processing and potential hazards like data dependencies.

2. **Microarchitecture Simulation**: Create a detailed simulation revealing how high-level instructions decompose into micro-operations, exposing the internal workings of complex instructions. This capability is essential for bridging the gap between assembly language and actual hardware operations, helping students understand why different instructions have varying execution costs.

3. **Cycle-Accurate Timing Model**: Develop a timing model that demonstrates performance impacts of different instruction sequences, providing accurate cycle counts for operations. This feature allows students to understand performance bottlenecks, optimization techniques, and the critical relationship between code structure and execution efficiency.

4. **Customizable Architecture**: Design a modular system allowing modification of instruction set and memory model for comparison between different architectural approaches. This flexibility enables students to experiment with architectural variations and understand trade-offs in CPU design decisions.

5. **Lecture Mode with Annotations**: Implement an annotation system for highlighting specific components and concepts during classroom demonstrations. This teaching aid allows the professor to focus student attention on particular aspects of the simulation during lectures, improving comprehension of complex topics.

## Technical Requirements
- **Testability Requirements**:
  - All components must be independently testable with well-defined inputs and expected outputs
  - Simulation states must be serializable and deserializable to verify correctness of execution
  - Pipeline stages must provide introspection interfaces for testing state transitions
  - Cycle count accuracy must be verifiable through automated test cases
  
- **Performance Expectations**:
  - The simulation must prioritize correctness and transparency over speed
  - Must support running small programs (up to 1000 instructions) with full pipeline visualization in under 5 seconds
  - State transitions should complete within predictable time bounds
  - Annotation system must not significantly impact simulation performance

- **Integration Points**:
  - Clean separation between core VM execution engine and visualization components
  - Standard interface for loading programs in both assembled and raw bytecode formats
  - API for educational tools to integrate with the simulator
  - Export mechanism for execution traces and statistics

- **Key Constraints**:
  - Implementation must use pure Python for maximum educational clarity
  - No external dependencies beyond standard library to ensure easy deployment in educational environments
  - All architecture components must be modifiable through configuration rather than code changes
  - Simulation must remain deterministic for reproducing specific behaviors

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The core functionality of this educational CPU architecture simulator includes:

1. A complete CPU simulation with explicit representation of all pipeline stages (fetch, decode, execute, memory access, write-back)

2. A memory subsystem with configurable cache levels, latency, and addressing modes

3. An instruction set implementation with micro-operation decomposition for complex instructions

4. A cycle-accurate execution engine that properly models pipeline stalls, hazards, and forwarding

5. An annotation system that can tag specific components, instructions, or cycle events with educational notes

6. A configuration system to adjust architectural parameters (pipeline depth, execution units, cache organization)

7. A statistics collection mechanism to generate metrics on program execution (CPI, stall rates, cache hit ratios)

8. A serializable execution trace capability for post-execution analysis

9. Support for different architectural variants (scalar, superscalar, VLIW) through configuration

10. The ability to introduce and demonstrate common architectural optimizations (branch prediction, out-of-order execution)

## Testing Requirements
- **Key Functionalities that Must be Verified**:
  - Correct execution of all instruction types under various pipeline conditions
  - Accurate decomposition of complex instructions into micro-operations
  - Proper handling of data and control hazards
  - Correct cycle counting across different architectural configurations
  - Functional annotation system that can highlight relevant components

- **Critical User Scenarios**:
  - Running small benchmark programs with various optimization levels
  - Demonstrating classic pipeline hazard scenarios (data dependencies, branch mispredictions)
  - Comparing performance between different architectural configurations
  - Visualizing the impact of memory hierarchy on program execution time
  - Using annotations to explain specific architectural concepts

- **Performance Benchmarks**:
  - Complete simulation of small programs (100-1000 instructions) in under 5 seconds
  - Handling of all pipeline stages with appropriate timing for at least 5 instructions per second
  - Memory subsystem simulation with realistic timing for at least 1000 memory accesses per second
  - Generation of execution statistics with negligible overhead

- **Edge Cases and Error Conditions**:
  - Handling of illegal instructions and addressing modes
  - Proper behavior with extreme pipeline conditions (all stalls, maximum forwarding)
  - Correct operation with edge case memory patterns (cache thrashing, alignment issues)
  - Graceful handling of malformed annotation requests
  - Recovery from invalid architectural configurations

- **Required Test Coverage Metrics**:
  - Minimum 90% line coverage for core simulation components
  - 100% coverage of the instruction set implementation
  - Complete coverage of all pipeline stage transitions
  - At least 85% branch coverage for hazard detection and resolution logic

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
The implementation will be considered successful if it:

1. Correctly simulates the complete fetch-decode-execute pipeline with visible state transitions

2. Accurately models instruction timing with cycle-by-cycle precision

3. Properly demonstrates architectural concepts such as pipelining, hazards, and memory hierarchies

4. Provides clear visualization of pipeline stages that makes internal CPU operations understandable

5. Supports architectural customization to demonstrate different CPU design approaches

6. Includes an effective annotation system suitable for classroom demonstrations

7. Generates accurate performance statistics that help explain the relationship between code and execution time

8. Handles a representative set of instructions sufficient to run educational examples

9. Maintains correctness across all tested instruction sequences and architectural configurations

10. Provides comprehensive test coverage validating all key requirements

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup
To set up the development environment:

1. Create a virtual environment using:
   ```
   uv venv
   ```

2. Activate the virtual environment:
   ```
   source .venv/bin/activate
   ```

3. Install the project in development mode:
   ```
   uv pip install -e .
   ```

4. CRITICAL: For test execution and reporting:
   ```
   pip install pytest-json-report
   pytest --json-report --json-report-file=pytest_results.json
   ```

REMINDER: Generating and providing the pytest_results.json file is a critical requirement for project completion. This file must be included as proof that all tests pass successfully.