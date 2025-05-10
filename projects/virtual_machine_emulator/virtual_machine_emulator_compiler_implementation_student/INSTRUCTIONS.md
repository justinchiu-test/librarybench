# Compiler Target and Visualization Virtual Machine

## Overview
A specialized virtual machine emulator designed for compiler implementation students to understand code generation and execution. The system provides tools for visualizing the mapping between high-level language constructs and bytecode, symbol table management, static and dynamic analysis, optimization comparisons, and abstract syntax tree transformations.

## Persona Description
Aisha is learning compiler design and needs to understand target code generation. She wants to see how high-level language constructs translate to low-level operations within a controlled environment.

## Key Requirements
1. **Language Construct Mapping**: Implement visualization tools that clearly show how high-level features like loops, conditionals, and functions translate to lower-level bytecode sequences. This is essential for Aisha to build a concrete understanding of code generation strategies, helping her see the direct relationship between source language constructs and their executable representation.

2. **Symbol Table Visualization**: Create detailed representations of how variables are stored, tracked, and accessed across different scopes during compilation and execution. This feature is critical for Aisha to understand symbol management—a fundamental compiler component—allowing her to visualize how names are resolved, how memory is allocated, and how the scope hierarchy is maintained throughout the compilation process.

3. **Static vs. Dynamic Analysis Tools**: Develop systems for examining code properties both before execution (statically) and during runtime (dynamically). This capability helps Aisha understand the differences between compile-time and runtime analysis, demonstrating what can be determined from source code alone versus what requires execution context, which is crucial knowledge for implementing effective compilers.

4. **Optimization Comparison**: Implement tools for showing code before and after various compiler optimizations are applied, with performance metrics. This feature allows Aisha to directly observe how optimization techniques transform code and impact performance, helping her understand the practical effects of theoretical optimization concepts through concrete examples.

5. **Abstract Syntax Tree to Bytecode Transformation**: Design visualization tools showing how an abstract syntax tree is progressively lowered to intermediate representations and finally to bytecode. This capability is vital for Aisha to understand the complete compilation pipeline, demonstrating how structured source code representations are methodically transformed into executable instructions through a series of well-defined steps.

## Technical Requirements

### Testability Requirements
- All visualization data must be exportable as structured formats for verification
- Transformation steps must be independently testable at each stage
- Symbol table operations must be verifiable through well-defined interfaces
- Optimization effects must be measurable with consistent metrics
- Execution results must be deterministic and comparable across different optimization levels

### Performance Expectations
- The emulator should execute programs quickly enough for interactive experimentation
- Visualization data generation should not significantly impact execution performance
- Symbol table operations should complete in constant or logarithmic time
- Optimization comparisons should be generated in reasonable time (under 5 seconds)
- The system should handle programs with at least 10,000 instructions and complex symbol tables

### Integration Points
- Well-defined formats for importing abstract syntax trees or high-level code
- Exportable visualization data for use in external tools
- Interfaces for implementing custom optimizations
- APIs for extending the symbol table with advanced features
- Hooks for analyzing execution at various levels of abstraction

### Key Constraints
- The visualization must accurately represent the relationship between source and compiled code
- Performance metrics must be consistent and meaningful for optimization comparisons
- Symbol table representations must reflect actual compiler implementation strategies
- The system must support both simple and complex language constructs
- All components must be designed with educational clarity as a priority

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The virtual machine emulator must implement these core components:

1. A stack-based virtual machine with a well-defined bytecode instruction set
2. A parser and compiler for a small, educational high-level language
3. Abstract syntax tree generation and manipulation tools
4. Symbol table implementation with scope management
5. Static analysis capabilities for code examination
6. Runtime analysis for execution pattern tracking
7. Multiple optimization implementations with measurable effects
8. Visualization data generation for all compilation and execution stages
9. Comparison tools for evaluating different compilation strategies
10. Export mechanisms for sharing and analyzing results

The system should allow compiler implementation students to write code in a simple high-level language, observe how it's parsed into an abstract syntax tree, follow the transformation to intermediate representations and bytecode, examine symbol table management, understand optimization impacts, and see the execution patterns during runtime.

## Testing Requirements

### Key Functionalities to Verify
- Correct transformation from language constructs to bytecode
- Accurate symbol table management across different scopes
- Proper static analysis of code properties
- Reliable dynamic analysis during execution
- Effective application of various optimizations
- Accurate visualization data generation for all stages
- Consistent performance metrics for optimization comparison

### Critical User Scenarios
- Compiling and visualizing how basic language constructs translate to bytecode
- Tracking variable scope and access patterns through the symbol table
- Comparing code before and after applying specific optimizations
- Examining the execution path of code with different optimization levels
- Visualizing the complete compilation pipeline from source to executable
- Analyzing how specific language features are implemented at the bytecode level
- Determining which properties can be analyzed statically versus dynamically

### Performance Benchmarks
- Compilation of typical student programs in under 3 seconds
- Visualization data generation adding less than 20% overhead to compilation
- Symbol table operations completing in O(log n) time for n symbols
- Optimization application completing in under 5 seconds for moderately sized programs
- Execution of optimized code at least 30% faster than unoptimized (for optimization teaching)
- Support for programs with up to 10,000 instructions and 1,000 symbols

### Edge Cases and Error Conditions
- Handling of complex nested scopes in symbol table management
- Proper analysis of recursive functions and data structures
- Management of optimization conflicts and dependencies
- Accurate representation of non-obvious code transformations
- Handling of language corner cases and ambiguities
- Proper visualization of complex control flow graphs
- Graceful management of optimization failures

### Required Test Coverage Metrics
- Minimum 90% line coverage across all modules
- 100% coverage of language construct transformation code
- 100% coverage of symbol table operations
- All implemented optimizations must have specific test cases
- All visualization data generation must be verified
- All error handling paths must be tested

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
The implementation will be considered successful if:

1. A compiler implementation student can use it to understand how language constructs translate to executable code
2. The system clearly visualizes at least 10 common programming language constructs and their bytecode equivalents
3. Symbol table visualization accurately demonstrates scope and variable management
4. The difference between static and dynamic analysis is clearly illustrated
5. At least five distinct optimization techniques can be demonstrated with measurable performance impacts
6. The transformation from abstract syntax tree to bytecode is clearly visualized
7. All test cases pass with the specified coverage requirements
8. Documentation comprehensively explains the compilation pipeline and how to use the system for learning

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