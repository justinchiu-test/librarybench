# Hardware-Oriented Virtual Machine Emulator

## Overview
A specialized virtual machine emulator that serves as a blueprint for amateur computer builders, demonstrating the relationship between virtual components and physical hardware. The system provides clear mappings to actual electronic parts, visualizes signal timing, demonstrates minimal instruction set computing, offers progressive complexity levels, and integrates with hardware description languages.

## Persona Description
Jamal is interested in building his own physical computer from basic electronic components. He uses the virtual machine as a blueprint to understand the minimal required components and their interactions before investing in hardware.

## Key Requirements
1. **Hardware Component Mapping**: Create detailed representations showing how virtual elements of the emulator correspond to physical electronic parts. This is essential for Jamal to translate his software understanding into hardware implementation decisions, helping him identify the actual components needed to build each section of a functional computer and understand their integration.

2. **Signal Timing Visualization**: Implement tools for illustrating clock cycles, control signals, and data transfers at the electrical level. This feature is critical for Jamal to understand the timing relationships between different components, helping him design appropriate clock circuits, avoid timing hazards, and appreciate the physical constraints that affect digital logic design.

3. **Minimal Instruction Set Computer Design**: Develop a simplified but functional instruction set architecture focusing on essential operations. This approach helps Jamal understand the bare minimum requirements for a working computer, allowing him to start with a manageable subset of functionality that can be implemented with reasonable effort while still demonstrating fundamental computing principles.

4. **Progressive Complexity Levels**: Structure the system to allow incremental understanding from basic gates to complex subsystems. This feature enables Jamal to build knowledge systematically, starting with fundamental digital logic elements and gradually incorporating them into more complex functional units, mirroring the physical construction process he would follow.

5. **Hardware Description Language Integration**: Provide tools for transitioning virtual machine designs to actual circuit specifications through HDL export. This capability bridges the gap between software simulation and physical implementation, giving Jamal the ability to move from conceptual understanding to practical hardware designs that can be synthesized or manually constructed.

## Technical Requirements

### Testability Requirements
- All virtual components must have clear physical hardware equivalents
- Signal timing must be precisely measurable in terms of clock cycles
- Instruction execution must be traceable at the gate level
- Progressive complexity levels must be independently testable
- HDL export must produce synthesizable descriptions

### Performance Expectations
- The emulator should accurately model clock-level timing for circuits up to 10MHz
- Signal propagation should reflect realistic gate delays and timing constraints
- The system should support simulation of designs with up to 1000 logic gates
- HDL export should complete in under 5 seconds for typical designs
- The system should execute quickly enough for interactive experimentation while maintaining accuracy

### Integration Points
- Interfaces for mapping between virtual and physical components
- Export formats for circuit diagrams and wiring specifications
- Integration with common HDL tools and formats (VHDL, Verilog)
- Libraries of standard components with physical part numbers
- Signal logging and analysis capabilities for timing verification

### Key Constraints
- The implementation must reflect physically realizable circuits
- Timing behavior must account for realistic electronic constraints
- The instruction set must be minimal yet complete enough for demonstration
- Component specifications must map to readily available electronic parts
- The system must be approachable for hobbyists without electrical engineering backgrounds

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The virtual machine emulator must implement these core components:

1. A gate-level simulation engine for basic digital logic elements
2. A clock generation and distribution system with configurable timing
3. A minimal but complete instruction set architecture
4. Memory subsystems with physically realizable addressing
5. Input/output interfaces that map to simple physical components
6. Signal visualization and analysis tools
7. Component mapping between virtual and physical parts
8. Progressive complexity levels from gates to complete systems
9. Hardware description language export capabilities
10. Documentation linking software concepts to hardware implementation

The system should allow amateur computer builders to understand the fundamental components needed for a working computer, experiment with different designs virtually before committing to hardware, visualize the inner workings at various levels of detail, and ultimately translate their understanding into physical construction plans.

## Testing Requirements

### Key Functionalities to Verify
- Accurate modeling of digital logic gates and their combinations
- Correct clock signal generation and distribution
- Proper execution of the minimal instruction set
- Accurate memory addressing and data storage
- Realistic signal timing and propagation
- Correct hardware component mapping to physical parts
- Valid HDL export for representative circuits

### Critical User Scenarios
- Designing and testing basic logic circuits (adders, multiplexers, etc.)
- Implementing and testing a complete CPU datapath
- Executing simple programs using the minimal instruction set
- Analyzing signal timing across different components
- Mapping virtual components to shopping lists of physical parts
- Exporting designs to HDL for synthesis or manual construction
- Progressing from simple to complex subsystems incrementally

### Performance Benchmarks
- Gate-level simulation accurate to within 10% of physical timings
- Support for clock frequencies up to 10MHz in simulation
- Memory subsystem supporting at least 64KB of addressable space
- Instruction execution with realistic cycle counts
- HDL export completing in under 5 seconds for designs with up to 1000 gates
- Component database covering at least 50 common electronic parts

### Edge Cases and Error Conditions
- Handling of timing hazards and race conditions
- Detection of unrealizable circuit designs
- Management of fan-out limitations for digital signals
- Identification of metastability risks in asynchronous interfaces
- Proper handling of clock domain crossings
- Warnings for physically impractical designs
- Error detection for incomplete or inconsistent specifications

### Required Test Coverage Metrics
- Minimum 95% line coverage across all modules
- 100% coverage of digital logic gate implementations
- 100% coverage of clock and timing code
- All instruction set operations must have specific test cases
- All progressive complexity levels must be tested independently
- All HDL export functionality must be verified

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
The implementation will be considered successful if:

1. An amateur computer builder can use it to understand the components needed for a working computer
2. The system provides clear mapping between at least 30 virtual components and their physical equivalents
3. Signal timing visualization accurately represents clock cycles and electrical signals
4. The minimal instruction set is sufficient to demonstrate basic computation
5. The progressive complexity approach allows learning from basic gates to complete systems
6. HDL export produces valid description files that can be used for physical implementation
7. All test cases pass with the specified coverage requirements
8. Documentation clearly connects software concepts to hardware implementation details

## Project Setup and Development

To set up the development environment:

1. Create a new project using UV:
   ```
   uv init --lib
   ```

2. Run the project:
   ```
   uv run python your_script.py
   ```

3. Install additional dependencies:
   ```
   uv sync
   ```

4. Run tests:
   ```
   uv run pytest
   ```

5. Format code:
   ```
   uv run ruff format
   ```

6. Lint code:
   ```
   uv run ruff check .
   ```

7. Type check:
   ```
   uv run pyright
   ```