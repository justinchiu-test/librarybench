# DIY Computer Architecture Simulator

## Overview
A specialized virtual machine emulator designed as a blueprint for physical computer construction, providing detailed simulation of fundamental computing components and their interactions while focusing on minimal, accessible designs that could feasibly be implemented with basic electronic components.

## Persona Description
Jamal is interested in building his own physical computer from basic electronic components. He uses the virtual machine as a blueprint to understand the minimal required components and their interactions before investing in hardware.

## Key Requirements
1. **Hardware Component Mapping**: Implement a comprehensive system that clearly shows how virtual machine elements correspond to physical electronic components and circuits. This feature is critical for Jamal to understand exactly which hardware components he would need to purchase and how they would be connected when building a physical version of the simulated computer.

2. **Signal Timing Visualization**: Create a detailed simulation of clock cycles, signal propagation, and electrical timing that illustrates the physical reality of digital circuits. This capability is essential for helping Jamal understand the temporal aspects of computer operation at the electronics level, particularly how synchronization works and why timing is crucial for reliable operation.

3. **Minimal Instruction Set Computer Design**: Develop an implementation focusing on essential operations that could be reasonably built with discrete components, prioritizing simplicity over features. This minimal approach allows Jamal to start with a viable physical construction project that teaches fundamental concepts without overwhelming complexity or requiring advanced manufacturing capabilities.

4. **Progressive Complexity Layers**: Structure the implementation to support incremental understanding and construction, from basic elements to more advanced features. This layered approach enables Jamal to build his physical computer in stages, starting with a working minimal system and gradually adding capabilities as his understanding and skills develop.

5. **Hardware Description Language Integration**: Provide export capabilities to hardware description languages that can be used for FPGA programming or circuit design tools. This feature creates a bridge between the simulation and actual implementation, allowing Jamal to transfer his designs directly to tools used for physical hardware creation.

## Technical Requirements
- **Testability Requirements**:
  - All simulated components must have clearly defined inputs and outputs
  - Signal timing must be deterministic and measurable
  - Instruction execution must be verifiable at the gate level
  - Hardware mappings must be validated against realistic component specifications
  - Exported HDL must produce identical behavior to the simulation
  
- **Performance Expectations**:
  - Simulation should run significantly faster than real hardware (minimum 100x)
  - Signal propagation simulation must maintain accuracy at nanosecond resolution
  - Complete system simulation should handle basic programs in seconds
  - All component operations should be traceable with minimal overhead
  - Export operations should complete within seconds even for complete designs

- **Integration Points**:
  - Export formats for common hardware description languages (Verilog, VHDL)
  - Component libraries mapping to commonly available electronic parts
  - Integration with electric circuit simulation tools
  - Support for loading and saving partial designs
  - Compatibility with standard logic simulation formats

- **Key Constraints**:
  - Implementation must be in pure Python for maximum accessibility
  - No dependencies beyond standard library to ensure easy deployment
  - All designs must be implementable with commercially available components
  - System complexity must remain within reasonable DIY construction capability
  - Educational clarity takes precedence over simulation performance

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The core functionality of this DIY computer architecture simulator includes:

1. A gate-level simulation of fundamental digital logic components (AND, OR, NOT, NAND, etc.)

2. A clock generation system with configurable timing parameters

3. Basic circuit elements (flip-flops, registers, counters, multiplexers)

4. A minimalist ALU implementation with essential operations

5. A simple but complete CPU design with fetch-decode-execute cycle

6. Basic memory subsystem with address decoding

7. Simple I/O interfaces that could be connected to physical devices

8. Instruction set implementation focused on buildable operations

9. Signal propagation simulation with appropriate timing

10. Component mapping to specific electronic parts

11. Export capabilities to hardware description languages

12. Progressive design stages from minimal to more complex implementations

## Testing Requirements
- **Key Functionalities that Must be Verified**:
  - Correct operation of all basic logic gates
  - Accurate signal timing and propagation
  - Proper execution of the complete instruction set
  - Correct memory addressing and data transfer
  - Accurate mapping to physical component specifications
  - Valid HDL export for implemented components

- **Critical User Scenarios**:
  - Simulating basic programs to verify complete system functionality
  - Tracing signal propagation through critical path components
  - Generating parts lists for physical construction
  - Exporting designs to HDL for FPGA implementation
  - Incrementally building more complex systems from basic components
  - Analyzing timing requirements for reliable operation

- **Performance Benchmarks**:
  - Simulation of basic computer operations at least 100x faster than physical hardware
  - Signal timing accuracy within 1 nanosecond
  - Support for designs with at least 1000 basic gates
  - Complete system simulation running simple programs in under 5 seconds
  - HDL export of complete designs in under 10 seconds

- **Edge Cases and Error Conditions**:
  - Handling of timing hazards and race conditions
  - Proper detection of electrical loading issues
  - Appropriate handling of clock domain crossing
  - Correct identification of fan-out limitations
  - Graceful handling of physically impossible configurations

- **Required Test Coverage Metrics**:
  - Minimum 90% line coverage for all components
  - 100% coverage for basic gate implementations
  - At least 95% branch coverage for timing simulation code
  - Complete coverage of instruction execution paths
  - At least 85% coverage for HDL export functionality

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

1. Accurately simulates a complete minimal computer at the gate level

2. Provides clear mapping between simulated components and physical parts

3. Demonstrates accurate signal timing and propagation

4. Supports a minimal but complete instruction set suitable for physical implementation

5. Enables incremental understanding from basic to advanced concepts

6. Produces valid hardware description language exports

7. Remains within the complexity boundaries of a feasible DIY project

8. Provides sufficient detail to serve as a blueprint for physical construction

9. Successfully executes basic programs in the simulated environment

10. Successfully passes all test cases demonstrating the required functionality

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