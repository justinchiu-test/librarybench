# Hardware Blueprint Virtual Machine

## Overview
A specialized virtual machine designed as a blueprint for physical computer construction, providing clear mapping between virtual and physical components, signal timing visualization, minimal instruction set design, progressive complexity levels, and hardware description language integration.

## Persona Description
Jamal is interested in building his own physical computer from basic electronic components. He uses the virtual machine as a blueprint to understand the minimal required components and their interactions before investing in hardware.

## Key Requirements
1. **Hardware component mapping showing how virtual elements correspond to physical parts**: Essential for Jamal to translate the emulated machine into actual circuits, providing a clear connection between software abstractions and their hardware implementations, including detailed specifications for components like registers, ALUs, memory units, and buses.

2. **Signal timing visualization illustrating clock cycles and electrical signals**: Critical for understanding how digital circuits synchronize and communicate, showing clock signals, data transfers, control lines, and timing diagrams that represent the electrical behavior Jamal will need to implement in his physical computer build.

3. **Minimal instruction set computer design focusing on essential operations**: Important for creating a realistically buildable computer by limiting complexity to a core set of instructions that can be implemented with reasonable effort using discrete components, while still providing sufficient functionality for basic computing tasks.

4. **Progressive complexity allowing incremental understanding from basic to advanced concepts**: Valuable for Jamal's learning journey, providing a path from simple concepts like binary arithmetic to more complex topics like addressing modes and interrupts, with each level being buildable and testable before moving to the next level of complexity.

5. **Hardware description language integration for transition to actual circuit design**: Necessary for bridging the gap between the virtual model and physical implementation, generating HDL descriptions that Jamal can use directly with FPGAs or as references for discrete component designs, making the transition from software to hardware more straightforward.

## Technical Requirements
- **Testability Requirements**:
  - All virtual components must have clearly defined inputs, outputs, and state
  - Signal timings must be precisely measurable and comparable to hardware specifications
  - Instruction execution must be testable at the gate and signal level
  - Hardware descriptions must be validated against reference implementations
  - Each complexity level must be independently testable as a complete system

- **Performance Expectations**:
  - Simulation should operate at a speed suitable for learning (at least 100KHz equivalent)
  - Signal visualization should provide nanosecond-level precision
  - Hardware component mapping should be generated in under 1 second
  - HDL export should complete in under 5 seconds for full design
  - Should support simulation of designs with up to 1000 logic gates

- **Integration Points**:
  - Hardware description language export (VHDL/Verilog)
  - Component specification format for physical parts
  - Signal trace export for timing analysis
  - Circuit diagram generation for documentation
  - Integration with common electronic design tools

- **Key Constraints**:
  - Must be implementable using basic electronic components
  - Should prioritize buildability over performance or features
  - Must provide detailed documentation suitable for hardware construction
  - Should follow standard digital design practices

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
1. **Component-Level Simulation**: Implement a detailed digital logic simulation that operates at the level of gates, flip-flops, and other basic building blocks, with complete visibility into all internal states and signals.

2. **Instruction Set Architecture**: Define a minimal but complete instruction set suitable for physical implementation, with clear encoding, decoding, and execution specifications at the hardware level.

3. **Clock and Signal Management**: Create an accurate clock generation and distribution system with proper timing relationships, signal propagation delays, and synchronization mechanisms that reflect real electronic behavior.

4. **Hardware Mapping System**: Develop a comprehensive mapping between virtual components and physical electronic parts, including specifications, connection requirements, and implementation notes.

5. **Complexity Progression**: Implement a staged design approach that breaks the computer into progressive implementation phases, each building on the previous while remaining functional on its own.

6. **HDL Generation**: Provide automatic generation of hardware description language code from the virtual machine design, with optimizations appropriate for physical implementation.

7. **Testing and Verification**: Create thorough test systems for validating the correctness of both the virtual design and its hardware implementation, including test patterns and expected results.

## Testing Requirements
- **Key Functionalities to Verify**:
  - Correct operation of all digital logic components
  - Proper execution of the complete instruction set
  - Accurate timing of all clock and control signals
  - Valid hardware component mappings with realistic specifications
  - Correct HDL generation for all system components

- **Critical User Scenarios**:
  - Simulating a complete instruction execution with signal-level detail
  - Generating hardware specifications for physical construction
  - Progressing through complexity levels with increasing functionality
  - Exporting HDL for implementation on an FPGA
  - Analyzing timing diagrams for critical path optimization

- **Performance Benchmarks**:
  - Simulate basic CPU operations at an equivalent of at least 100KHz
  - Generate timing diagrams with nanosecond resolution
  - Support systems with at least 64 bytes of memory in basic configurations
  - Export complete HDL descriptions in under 5 seconds
  - Handle designs with up to 1000 logic gates efficiently

- **Edge Cases and Error Conditions**:
  - Detect and report timing violations and race conditions
  - Identify fan-out limitations in hardware mappings
  - Handle metastability issues in asynchronous interfaces
  - Report power consumption concerns for physical implementation
  - Identify potential signal integrity issues in the design

- **Required Test Coverage Metrics**:
  - 100% coverage of the core logic component simulations
  - 100% coverage of the instruction set implementation
  - 95% coverage of timing and signal propagation functionality
  - 90% coverage of hardware mapping algorithms
  - 95% coverage of HDL generation

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
1. Jamal can understand how each virtual component maps to physical hardware
2. Signal timing visualizations accurately represent electrical behavior in the physical implementation
3. The minimal instruction set design is complete enough for useful computation while remaining buildable
4. Each progressive complexity level functions as a complete system on its own
5. Generated HDL descriptions can be successfully implemented on actual hardware
6. The simulation accurately predicts the behavior of the physical implementation
7. Jamal can successfully build a working physical computer based on the virtual blueprint

To set up your environment, use `uv venv` to create a virtual environment. From within the project directory, the environment can be activated with `source .venv/bin/activate`.