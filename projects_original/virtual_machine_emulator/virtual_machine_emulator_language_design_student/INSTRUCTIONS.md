# Programming Language VM Target Platform

## Overview
A specialized virtual machine implementation designed to serve as a compilation target for student-designed programming languages, providing rich introspection, visualization of code transformations, and extensibility for language-specific features. This VM is optimized for clarity and educational value rather than raw performance.

## Persona Description
Miguel is creating his own programming language as a capstone project and needs a target virtual machine to generate code for. He requires a well-documented runtime that helps him understand compiler backend design and code generation strategies.

## Key Requirements
1. **Intermediate Representation Visualization**: Implement a system that visualizes the transformation from high-level code to bytecode, showing each step in the compilation process. This feature is critical for Miguel to understand how different language constructs translate to executable code and how optimization passes transform the program representation.

2. **Optimization Framework**: Create a flexible optimization framework for implementing and testing various code improvement techniques like constant folding, dead code elimination, and register allocation. This capability allows Miguel to experiment with different optimization strategies and understand their impact on code quality and execution performance.

3. **Custom Instruction Extension Mechanism**: Develop a modular system for adding language-specific operations to the VM's instruction set without modifying the core runtime. This extensibility is essential for implementing Miguel's custom language features efficiently without being limited to a fixed instruction set.

4. **Symbol Table Management**: Implement comprehensive symbol table facilities for managing variable scoping, name resolution, and binding across compilation phases. This feature is fundamental for Miguel to understand how variables, functions, and other named entities are tracked throughout the compilation pipeline.

5. **Runtime Performance Metrics**: Create a detailed performance analysis system identifying bottlenecks in generated code, tracking execution frequency, memory usage, and instruction statistics. These metrics are vital for Miguel to evaluate the quality of his code generation strategies and optimize his compiler's output.

## Technical Requirements
- **Testability Requirements**:
  - All components must have clear interfaces with well-defined inputs and outputs
  - Compilation phases must support injection of test data at any stage
  - VM instruction execution must be deterministic and replayable
  - Symbol table operations must be fully testable independently of code execution
  - All optimization passes must be separately testable with predefined inputs
  
- **Performance Expectations**:
  - The VM must execute typical student programs at reasonable speeds (at least 100,000 instructions per second)
  - Optimization passes should complete in under 5 seconds for programs up to 10,000 bytecode instructions
  - Symbol table lookups should have O(1) average case complexity
  - Visualization generation should not impose more than 20% overhead on compilation
  - Memory consumption should remain under 512MB for typical student projects

- **Integration Points**:
  - Clean API for compiler frontends to emit bytecode or intermediate representations
  - Hooks for custom bytecode loaders and instruction implementations
  - Export formats for visualization components to be used by external tools
  - Standardized interface for performance data collection and reporting
  - Integration with custom memory management strategies

- **Key Constraints**:
  - Implementation must be in pure Python for educational clarity
  - No dependencies beyond standard library to ensure portability
  - All components must be well-documented with explanatory comments
  - VM state must be inspectable and modifiable at any point during execution
  - Generated code must not depend on any specific host OS features

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The core functionality of this programming language virtual machine target platform includes:

1. A stack-based virtual machine with a comprehensive instruction set suitable for implementing common programming language features

2. An intermediate representation (IR) system with multiple representations of increasing abstraction (high-level IR, mid-level IR, low-level IR)

3. A visualization pipeline that tracks and displays code transformations between different compilation phases

4. A symbol table implementation supporting nested scopes, visibility rules, and type information

5. A flexible bytecode format with metadata for debugging and optimization

6. A suite of standard optimization passes (constant propagation, dead code elimination, common subexpression elimination)

7. An instruction profiling system that records execution frequency and timing

8. A memory profiling system that tracks allocations and object lifetimes

9. An extension mechanism for adding custom instructions with proper integration into the optimization framework

10. A compilation framework that manages the transformation pipeline from source code to executable bytecode

## Testing Requirements
- **Key Functionalities that Must be Verified**:
  - Correct execution of all base instruction set operations
  - Accurate transformation between all IR representations
  - Proper symbol table management for various scoping rules
  - Effective implementation of all optimization passes
  - Accurate performance metrics collection
  - Proper functioning of the instruction extension mechanism

- **Critical User Scenarios**:
  - Compiling and executing programs with various language constructs (conditionals, loops, functions, recursion)
  - Applying different optimization strategies and measuring their impact
  - Extending the instruction set with language-specific operations
  - Tracking symbol definitions and references across compilation phases
  - Analyzing performance bottlenecks in generated code

- **Performance Benchmarks**:
  - Execution of at least 100,000 basic instructions per second
  - Compilation and optimization of 10,000 instruction programs in under 5 seconds
  - Symbol table operations (lookup, insert, delete) completing in microsecond range
  - Linear scaling of memory usage with program size up to at least 100K instructions
  - Visualization generation adding no more than 20% overhead to compilation time

- **Edge Cases and Error Conditions**:
  - Handling of invalid bytecode or IR representations
  - Proper error reporting for optimization failures
  - Correct behavior with extremely large or complex symbol tables
  - Graceful degradation with resource-intensive custom instructions
  - Recovery from incomplete or corrupt metadata

- **Required Test Coverage Metrics**:
  - Minimum 90% line coverage for core VM execution components
  - 100% coverage for IR transformation logic
  - At least 95% branch coverage for optimization passes
  - Complete coverage of symbol table operations
  - At least 85% coverage for custom instruction extension mechanisms

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

1. Provides a complete virtual machine environment capable of executing bytecode generated from student-created programming languages

2. Clearly visualizes the transformation steps from source code to executable bytecode

3. Supports the implementation and testing of common optimization techniques

4. Allows extension of the instruction set with custom operations

5. Provides comprehensive symbol table facilities for tracking variables and functions

6. Delivers accurate and useful performance metrics for generated code

7. Handles a variety of language constructs efficiently and correctly

8. Includes well-documented APIs for all major components

9. Offers proper error handling and diagnostic information

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