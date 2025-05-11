# Compiler Target Virtual Machine

## Overview
A specialized virtual machine implementation designed to help compiler students understand target code generation, providing visualization and analysis tools that show how high-level language constructs translate to low-level operations, supporting effective compiler backend development and optimization techniques.

## Persona Description
Aisha is learning compiler design and needs to understand target code generation. She wants to see how high-level language constructs translate to low-level operations within a controlled environment.

## Key Requirements
1. **Language Construct Mapping**: Implement a comprehensive visualization system showing how high-level constructs like loops, conditionals, and function calls translate to sequences of bytecode instructions. This feature is critical for Aisha to build the conceptual bridge between source language features and target code, helping her develop mental models for code generation strategies.

2. **Symbol Table Visualization**: Create an interactive system displaying variable storage locations, scope relationships, and access patterns throughout code execution. This capability is essential for understanding how compilers track and manage identifiers, helping Aisha grasp how variables are allocated, referenced, and managed across different scopes and lifetimes.

3. **Static vs. Dynamic Analysis**: Develop complementary tools for examining code properties both before execution (static analysis) and during runtime (dynamic analysis). This dual approach helps Aisha understand the relationship between compile-time decisions and runtime behavior, illustrating what can be determined statically versus what requires runtime information.

4. **Optimization Comparison Visualizer**: Implement a side-by-side visualization showing code before and after various compiler optimization techniques are applied. This feature allows Aisha to see the concrete effects of optimization passes, understand their impact on code structure and performance, and learn how to implement effective optimizer components.

5. **AST to Bytecode Transformation Viewer**: Create a step-by-step visualization of how abstract syntax trees are processed and transformed into executable bytecode. This detailed view helps Aisha understand the compiler backend's code generation process, revealing how logical program structures are methodically converted to linear instruction sequences.

## Technical Requirements
- **Testability Requirements**:
  - All visualization components must have programmatically verifiable outputs
  - Code transformations must be deterministic and reproducible
  - Symbol table operations must be independently testable
  - Optimization effects must be measurable and comparable
  - AST transformations must produce consistent, verifiable results
  
- **Performance Expectations**:
  - Must handle source programs of at least 1000 lines
  - Transformation process should complete in under 5 seconds for typical student programs
  - Symbol table operations should have O(1) average case complexity
  - Visualization generation should add minimal overhead to compilation
  - Complete analysis pipeline should process moderately complex programs in under 10 seconds

- **Integration Points**:
  - Standard interface for frontend integration (accepting ASTs or parse trees)
  - Export formats for all visualization types (mapping tables, symbol data, code comparisons)
  - Common intermediate format for optimization passes
  - Instrumentation hooks for custom analysis modules
  - Integration with standard compiler development tools and formats

- **Key Constraints**:
  - Implementation must be in pure Python for maximum clarity and educational value
  - No dependencies beyond standard library to ensure portability
  - All components must be well-documented with educational explanations
  - System should be usable without knowledge of specific compiler implementation details
  - Visualization outputs must be machine-readable for automated testing

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The core functionality of this compiler target virtual machine includes:

1. A stack-based virtual machine with a comprehensive bytecode instruction set

2. A mapping system that traces high-level language constructs to their bytecode implementations

3. A symbol table implementation with full support for nested scopes, variable types, and access tracking

4. Static analysis tools for examining code properties before execution

5. Dynamic analysis capability for tracking runtime behavior and performance

6. A flexible intermediate representation suitable for optimization

7. Multiple optimization pass implementations with before/after comparison

8. An AST processor that demonstrates incremental transformation to bytecode

9. Execution tracing with symbol access and state change recording

10. Performance metrics collection identifying execution hotspots and bottlenecks

11. Export mechanisms for all analysis data in machine-readable formats

12. Example implementations of common language constructs (loops, conditionals, functions, etc.)

## Testing Requirements
- **Key Functionalities that Must be Verified**:
  - Accurate mapping between language constructs and bytecode
  - Correct symbol table management across different scopes
  - Proper static analysis of code properties
  - Accurate runtime tracking of program behavior
  - Correct implementation of optimization passes
  - Proper transformation from AST to bytecode

- **Critical User Scenarios**:
  - Tracing how loop constructs translate to branch and jump instructions
  - Visualizing variable scope and lifetime management
  - Comparing optimized and unoptimized code execution
  - Analyzing function call implementations including parameter passing
  - Tracking the complete compilation pipeline from AST to executable code

- **Performance Benchmarks**:
  - Processing of 1000-line source programs in under 5 seconds
  - Symbol table operations completing in microsecond range
  - Optimization passes applying to medium-sized programs in under 2 seconds
  - Complete AST-to-bytecode transformation in under 3 seconds for typical programs
  - Full execution tracing adding no more than 50% overhead to runtime

- **Edge Cases and Error Conditions**:
  - Handling of complex nested scopes and shadowed variables
  - Proper operation with recursive and highly nested structures
  - Correct analysis of corner cases in optimization opportunities
  - Appropriate behavior with unusual or pathological AST structures
  - Graceful handling of incomplete or invalid inputs

- **Required Test Coverage Metrics**:
  - Minimum 90% line coverage for all components
  - 100% coverage for symbol table operations
  - At least 95% branch coverage for optimization passes
  - Complete coverage of AST-to-bytecode transformation logic
  - At least 85% coverage for analysis tools

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

1. Clearly demonstrates how common language constructs map to bytecode instructions

2. Provides accurate visualization of symbol table operations and variable management

3. Effectively illustrates the differences between static and dynamic code analysis

4. Shows the concrete effects of optimization techniques on code structure and performance

5. Clearly demonstrates the transformation process from AST to executable bytecode

6. Handles a representative set of language features and programming patterns

7. Provides useful insights into compiler backend implementation strategies

8. Generates clear, understandable visualizations that enhance learning

9. Offers measurable performance improvements through optimization techniques

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