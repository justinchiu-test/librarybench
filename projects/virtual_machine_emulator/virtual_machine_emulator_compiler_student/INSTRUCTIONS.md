# Compiler Target Virtual Machine

## Overview
A specialized virtual machine implementation designed specifically for compiler students, offering detailed visualization of language construct mappings, symbol tables, static and dynamic analysis tools, optimization comparisons, and abstract syntax tree transformations.

## Persona Description
Aisha is learning compiler design and needs to understand target code generation. She wants to see how high-level language constructs translate to low-level operations within a controlled environment.

## Key Requirements
1. **Language construct mapping showing how features like loops and conditionals translate to bytecode**: Essential for Aisha to understand the fundamental connection between high-level programming patterns and their low-level implementation, providing clear visualization of how compilers transform common structures like for-loops, if-statements, and function calls into executable instructions.

2. **Symbol table visualization displaying variable storage and access patterns**: Critical for understanding how compilers track and manage variables, functions, and types, allowing Aisha to see how memory is allocated, how scope rules are implemented, and how different variable types are handled at the compilation and execution levels.

3. **Static vs. dynamic analysis tools for examining code properties before and during execution**: Important for comparing the differences between compile-time and runtime analysis, helping Aisha understand what optimizations and checks can be performed before execution versus those requiring runtime information, with tools to examine and compare both perspectives.

4. **Optimization comparison showing code before and after various compiler improvements**: Vital for learning how compilers transform code for efficiency, allowing Aisha to visualize the exact changes made by optimization passes like constant folding, dead code elimination, loop unrolling, and register allocation, with performance metrics to quantify improvements.

5. **Abstract syntax tree to bytecode transformation visualization**: Necessary for understanding the entire compilation pipeline, showing how source code is parsed into an abstract syntax tree and then progressively lowered through intermediate representations until it becomes executable bytecode, with each transformation step clearly visible.

## Technical Requirements
- **Testability Requirements**:
  - All language construct translations must be independently testable
  - Symbol table operations must be verifiable through automated tests
  - Static and dynamic analysis tools must produce consistent, testable outputs
  - Optimization transformations must be isolated and individually testable
  - AST transformation visualization must be verifiable for correctness

- **Performance Expectations**:
  - Language construct mapping visualization generation in under 500ms
  - Symbol table operations should complete in under 10ms for typical program sizes
  - Static analysis should complete within 1 second for programs up to 1000 lines
  - Optimization comparisons should be generated in under 2 seconds
  - VM execution should support at least 100,000 instructions per second in normal mode

- **Integration Points**:
  - Simple high-level language parser for demonstration examples
  - Intermediate representation data structures
  - Extensible optimization pass system
  - Bytecode generation and execution engine
  - Visualization data extraction for all compilation stages

- **Key Constraints**:
  - Must be implementable using only Python standard library
  - Should prioritize clarity and educational value over performance
  - Must support common programming language constructs
  - Should be well-documented for educational purposes

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
1. **High-Level Language Parser**: Implement a simple parser for a minimal but complete high-level language supporting common programming constructs like variables, loops, conditionals, and functions.

2. **Abstract Syntax Tree Representation**: Create a comprehensive abstract syntax tree (AST) representation with visitor pattern support for traversal and transformation.

3. **Symbol Table Management**: Implement a complete symbol table system supporting nested scopes, variable lookup, type checking, and scope lifetime management.

4. **Optimization Framework**: Develop a system for defining and applying code transformations, with the ability to compare code before and after optimization and measure performance impacts.

5. **Bytecode Generation**: Create a bytecode generator that translates AST nodes or intermediate representations into executable instructions for the virtual machine.

6. **Virtual Machine Execution Engine**: Implement a stack-based virtual machine that executes the generated bytecode with comprehensive state tracking and instrumentation.

7. **Analysis Tools**: Provide both static (compile-time) and dynamic (runtime) analysis capabilities, including data flow analysis, control flow analysis, and execution profiling.

## Testing Requirements
- **Key Functionalities to Verify**:
  - Correct translation of all language constructs to bytecode
  - Proper management of symbol tables across nested scopes
  - Accurate static and dynamic analysis results
  - Effective application of different optimization techniques
  - Correct transformation from AST to final bytecode

- **Critical User Scenarios**:
  - Compiling and executing programs with various language constructs
  - Tracking variable access patterns across different scopes
  - Comparing optimized and unoptimized code execution
  - Analyzing program behavior using both static and dynamic tools
  - Following the complete transformation from source code to execution

- **Performance Benchmarks**:
  - Parse and generate AST for 1000-line programs in under 500ms
  - Complete symbol table operations in under 10ms for typical access patterns
  - Execute optimization passes in under 1 second for programs up to 1000 lines
  - Generate language construct visualizations in under 200ms
  - Execute bytecode at a rate of at least 100,000 instructions per second

- **Edge Cases and Error Conditions**:
  - Handle malformed source code with clear error reporting
  - Manage complex nested scopes correctly
  - Identify and report optimization opportunities that cannot be safely applied
  - Handle recursion and complex control flow correctly
  - Properly detect and report type errors and other static issues

- **Required Test Coverage Metrics**:
  - 95% coverage of high-level language parsing
  - 100% coverage of language construct translation
  - 95% coverage of symbol table management
  - 90% coverage of optimization implementations
  - 95% coverage of bytecode generation and execution

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
1. Aisha can clearly observe how high-level language constructs map to low-level operations
2. Symbol table visualization correctly displays variable storage and access patterns across scopes
3. Static and dynamic analysis tools provide complementary insights into code properties
4. Optimization comparisons demonstrate measurable performance improvements
5. The complete compilation pipeline from AST to bytecode is transparent and understandable
6. The system serves as an effective learning tool for understanding compiler design concepts
7. Aisha can develop and test her own compilation strategies using the framework

To set up your environment, use `uv venv` to create a virtual environment. From within the project directory, the environment can be activated with `source .venv/bin/activate`.