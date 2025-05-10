# Parallel Computation Virtual Machine Emulator

## Overview
A specialized virtual machine emulator designed for parallel computing researchers to visualize and analyze concurrent execution patterns. The system simulates true multi-core execution, demonstrates race conditions, implements synchronization primitives, visualizes thread scheduling, and models memory coherence protocols.

## Persona Description
Dr. Patel studies parallel algorithm design and needs to visualize concurrent execution patterns. He requires a virtual machine that can demonstrate multi-threaded behavior and synchronization mechanisms.

## Key Requirements
1. **Multi-core Simulation**: Implement a system that emulates multiple processing cores executing instructions truly in parallel. This is essential for Dr. Patel to study how parallel algorithms distribute work across cores, observe performance scaling with additional cores, and identify potential bottlenecks that only emerge in true parallel execution environments.

2. **Race Condition Demonstration**: Design tools that can reliably reproduce and visualize concurrent access patterns leading to race conditions. This capability is critical for Dr. Patel to demonstrate the subtleties of parallel programming errors, helping him illustrate how seemingly correct code can produce unexpected results when execution timing varies, and experiment with different techniques to eliminate these issues.

3. **Synchronization Primitive Implementation**: Create a comprehensive set of synchronization mechanisms including locks, semaphores, barriers, and atomic operations. This feature enables Dr. Patel to experiment with different synchronization strategies, compare their performance characteristics and overhead, and demonstrate the tradeoffs involved in controlling access to shared resources in parallel environments.

4. **Thread Scheduling Visualization**: Develop tools that clearly show context switches and core allocation decisions over time. This allows Dr. Patel to analyze how scheduling policies affect parallel performance, illustrate concepts like work stealing and load balancing, and demonstrate how different scheduling approaches impact throughput, latency, and fairness in multi-threaded applications.

5. **Memory Coherence Modeling**: Implement mechanisms that simulate cache consistency protocols and memory access patterns in multi-core systems. This capability helps Dr. Patel demonstrate how memory architecture affects parallel performance, illustrate advanced concepts like false sharing and cache line contention, and experiment with different memory access patterns to optimize parallel algorithms.

## Technical Requirements

### Testability Requirements
- All parallel behavior must be reproducible for reliable testing
- Race condition scenarios must be consistently triggerable
- Synchronization primitive correctness must be verifiable
- Thread scheduling decisions must be observable and traceable
- Memory coherence effects must be measurable and analyzable

### Performance Expectations
- The emulator should support simulation of at least 16 virtual cores
- Execution speed should be sufficient for interactive experimentation
- Thread scheduling overhead should be representative of real systems
- Synchronization primitive performance should reflect realistic costs
- Memory coherence simulation should accurately model cache behavior costs

### Integration Points
- Well-defined interfaces for creating and submitting parallel workloads
- APIs for configuring different synchronization strategies
- Hooks for monitoring thread execution and scheduling
- Export mechanisms for execution traces and performance data
- Interfaces for implementing custom memory coherence models

### Key Constraints
- The multi-core simulation must model true parallelism, not just interleaved execution
- Race conditions must be reliably reproducible when needed for demonstration
- Synchronization primitives must guarantee proper semantics
- Thread scheduling must reflect realistic operating system behavior
- Memory coherence modeling must be based on established protocols

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The virtual machine emulator must implement these core components:

1. A virtual CPU architecture that supports multi-core execution
2. A memory subsystem with configurable cache hierarchy and coherence protocols
3. A thread management system with creation, scheduling, and synchronization
4. A comprehensive set of synchronization primitives (locks, semaphores, barriers, etc.)
5. Tools for creating and reproducing race condition scenarios
6. Thread scheduling visualization and analysis capabilities
7. Memory access pattern tracking and visualization
8. Performance measurement and comparison tools
9. Export mechanisms for execution traces and analysis data
10. Configuration options for different parallel architectures and policies

The system should allow parallel computing researchers to create specific parallel workloads, execute them on a configurable multi-core environment, observe the resulting execution patterns, experiment with different synchronization strategies, and analyze performance characteristics for research and educational purposes.

## Testing Requirements

### Key Functionalities to Verify
- Correct simulation of truly parallel execution across multiple cores
- Accurate reproduction of race conditions in concurrent access scenarios
- Proper implementation of various synchronization primitives
- Realistic thread scheduling behavior with appropriate context switching
- Faithful modeling of memory coherence protocols and cache effects
- Reliable performance measurement and comparison

### Critical User Scenarios
- Running the same algorithm with varying numbers of cores to observe scaling
- Demonstrating classic race conditions and their resolution through synchronization
- Comparing different synchronization strategies for the same parallel problem
- Visualizing thread scheduling decisions and their impact on performance
- Analyzing cache coherence traffic and its effect on parallel efficiency
- Experimenting with different memory access patterns to optimize cache usage

### Performance Benchmarks
- Support for simulation of at least 16 virtual cores
- Execution of at least 1 million instructions per second in parallel mode
- Context switching overhead representative of real systems (within 2x)
- Synchronization primitive performance reflecting realistic cost ratios
- Memory coherence simulation accurate enough for educational demonstration
- Support for parallel programs with at least 100 threads and complex synchronization

### Edge Cases and Error Conditions
- Handling of deadlocks and livelocks in synchronization testing
- Detection and analysis of priority inversion scenarios
- Management of thread exhaustion and resource contention
- Proper modeling of cache coherence edge cases like false sharing
- Handling of complex interleaving patterns in race condition scenarios
- Analysis of pathological scheduling cases and their performance impact

### Required Test Coverage Metrics
- Minimum 90% line coverage across all modules
- 100% coverage of synchronization primitive implementations
- 100% coverage of thread scheduling code
- All memory coherence protocols must have specific test cases
- All race condition demonstration scenarios must be tested
- All error handling paths must be tested

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
The implementation will be considered successful if:

1. A parallel computing researcher can use it to visualize and analyze concurrent execution patterns
2. The system accurately demonstrates true multi-core execution with appropriate performance scaling
3. Race conditions can be reliably reproduced and analyzed in at least five classic scenarios
4. At least five different synchronization primitives are correctly implemented and demonstrable
5. Thread scheduling visualization clearly shows context switches and core allocation decisions
6. Memory coherence modeling accurately reflects the performance implications of different cache protocols
7. All test cases pass with the specified coverage requirements
8. Documentation comprehensively explains the parallel computing concepts demonstrated by the system

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