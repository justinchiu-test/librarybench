# Compiler Target Virtual Machine Emulator

## Overview
A specialized virtual machine emulator designed specifically for programming language design students who need a well-documented runtime environment to serve as a compilation target. This emulator provides comprehensive tools for visualization of intermediate representations, optimization frameworks, and performance metrics to support the development and understanding of compiler backends.

## Persona Description
Miguel is creating his own programming language as a capstone project and needs a target virtual machine to generate code for. He requires a well-documented runtime that helps him understand compiler backend design and code generation strategies.

## Key Requirements
1. **Intermediate Representation Visualization**: Implement a system that visually represents the transformation from high-level code to bytecode. This is essential for Miguel to understand and debug the code generation phase of his compiler, allowing him to see how source code constructs map to lower-level operations.

2. **Optimization Framework**: Create an extensible framework for implementing and testing various code improvement techniques. This feature is crucial for Miguel to experiment with different optimization strategies and measure their impact on code efficiency, helping him learn practical compiler optimization principles.

3. **Custom Instruction Extension Mechanism**: Design a system that allows for the addition of language-specific operations to the base instruction set. This enables Miguel to implement specialized instructions that better support the unique features of his programming language, making the compilation process more efficient.

4. **Symbol Table Management**: Implement comprehensive symbol management utilities for handling variable scoping and name resolution. This feature is vital for Miguel to understand how compilers track variables across different scopes and manage memory allocation, supporting proper implementation of language features like closures or nested functions.

5. **Runtime Performance Metrics**: Develop tooling that identifies bottlenecks in generated code by collecting and analyzing execution metrics. This allows Miguel to iteratively improve his compiler's output by pinpointing inefficient code generation patterns and measuring the impact of his optimizations.

## Technical Requirements

### Testability Requirements
- All components must be designed with clear interfaces that can be tested in isolation
- The emulator must support injecting custom states for testing specific scenarios
- Execution steps must be observable and verifiable through a well-defined API
- Metrics collection must be separable from execution for targeted testing
- Integration tests must validate the complete compilation to execution pipeline

### Performance Expectations
- The emulator should be capable of executing programs with at least 10,000 instructions per second on standard hardware
- Symbol table operations should have O(1) average lookup complexity
- Optimization passes should complete in reasonable time (less than 5 seconds for programs under 1,000 instructions)
- Memory consumption should be proportional to the size of the program being executed plus a reasonable constant overhead
- State serialization/deserialization should be efficient enough for frequent snapshots during execution

### Integration Points
- Clear interfaces for accepting bytecode from external compiler frontends
- Well-documented intermediate representation format for optimization passes
- APIs for extending the instruction set with custom operations
- Hooks for monitoring execution state and performance
- Export capabilities for execution traces and performance data

### Key Constraints
- The virtual machine must maintain deterministic execution for reliable testing
- Any extensions to the base instruction set must maintain backward compatibility
- The system must be usable without graphical interfaces (though visualization data should be exportable)
- Memory usage must be explicitly tracked and reported
- The implementation must be cross-platform compatible

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The virtual machine emulator must implement these core components:

1. A stack-based virtual machine with a well-defined instruction set, suitable as a compilation target for a high-level language
2. A bytecode format specification and parser/generator for loading and saving programs
3. An execution engine that can run bytecode programs with detailed state tracking
4. An intermediate representation system that captures the transformation from source code to bytecode
5. A symbol management system for tracking variables, functions, and other named entities
6. An optimization framework that allows for analyzing and transforming bytecode programs
7. A metrics collection system that gathers performance data during execution
8. A mechanism for extending the instruction set with custom operations
9. A state inspection and visualization data export system for debugging
10. Serialization capabilities for saving and loading execution states

The system should be implemented as a set of modular Python packages with clean APIs between components, allowing for flexible use in different compilation and execution scenarios.

## Testing Requirements

### Key Functionalities to Verify
- Correct execution of bytecode according to the virtual machine specification
- Accurate transformation and representation of intermediate code
- Proper symbol table management across different scopes
- Effective application of optimization techniques to improve code
- Accurate collection and reporting of performance metrics
- Successful extension of the instruction set with custom operations
- Proper state inspection and data export for visualization

### Critical User Scenarios
- Compiling a simple high-level language to bytecode and executing it
- Applying various optimizations to improve the efficiency of generated code
- Adding custom instructions to support language-specific features
- Analyzing the performance of generated code to identify bottlenecks
- Debugging execution issues by inspecting intermediate states
- Comparing different implementation strategies for the same high-level construct

### Performance Benchmarks
- Execution speed of at least 10,000 instructions per second for typical programs
- Symbol table operations completing in constant time regardless of table size
- Optimization passes completing in less than 5 seconds for moderately sized programs
- Intermediary representation transformations having minimal overhead
- State serialization/deserialization completing in under 500ms for typical execution states

### Edge Cases and Error Conditions
- Handling of invalid bytecode or instruction sequences
- Management of stack overflows and memory limitations
- Proper error reporting for undefined symbols or operations
- Graceful handling of optimization failures
- Recovery mechanisms for corrupted state information
- Proper handling of recursive or deeply nested structures

### Required Test Coverage Metrics
- Minimum 90% line coverage across all modules
- 100% coverage of the core VM execution engine
- All error handling paths must be tested
- All optimization techniques must have specific test cases
- Each custom instruction extension mechanism must be tested

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
The implementation will be considered successful if:

1. A programming language design student can use the virtual machine as a compilation target for a simple language implementation
2. The system clearly visualizes the transformation from high-level code to executable bytecode
3. Students can implement and measure the impact of at least three different optimization techniques
4. The implementation supports adding at least five custom instructions to accommodate language-specific features
5. Performance metrics accurately identify execution bottlenecks in at least 90% of test cases
6. The system correctly manages symbol tables for programs with nested scopes and complex name resolution requirements
7. All test cases pass with the specified coverage requirements
8. The documentation is comprehensive enough for students to understand the system without prior virtual machine experience

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