# Parallel Computing Simulation Virtual Machine

## Overview
A specialized virtual machine designed to simulate and visualize parallel execution environments, with support for multiple cores, race condition demonstration, synchronization primitives, thread scheduling visualization, and memory coherence modeling.

## Persona Description
Dr. Patel studies parallel algorithm design and needs to visualize concurrent execution patterns. He requires a virtual machine that can demonstrate multi-threaded behavior and synchronization mechanisms.

## Key Requirements
1. **Multi-core simulation showing truly parallel instruction execution**: Essential for Dr. Patel to visualize and analyze how parallel algorithms perform across multiple execution units, providing insights into instruction-level parallelism, workload distribution, and the performance impacts of various core configurations and counts.

2. **Race condition demonstration with reproducible concurrent access patterns**: Critical for teaching and researching this fundamental concurrency challenge, allowing controlled and deterministic recreation of race conditions to study their causes, effects, and potential solutions without the unpredictability that makes them difficult to analyze in real systems.

3. **Synchronization primitive implementation (locks, semaphores, barriers)**: Necessary for modeling how concurrent algorithms coordinate access to shared resources, enabling experimentation with different synchronization strategies and analysis of their performance impacts, deadlock potential, and correctness guarantees.

4. **Thread scheduling visualization showing context switches and core allocation**: Important for understanding how operating systems and runtime environments manage concurrent execution, providing visibility into scheduling decisions, context switch overhead, core utilization patterns, and their effects on parallel algorithm performance.

5. **Memory coherence modeling illustrating cache consistency protocols**: Vital for researching how shared memory systems maintain a consistent view of data across cores with individual caches, visualizing the operation of protocols like MESI/MOESI, the performance impacts of cache coherence traffic, and the memory access patterns that lead to thrashing.

## Technical Requirements
- **Testability Requirements**:
  - Multi-core execution must be deterministically reproducible for testing
  - Race condition scenarios must be precisely controllable and detectable
  - Synchronization primitives must be verifiable for correctness
  - Thread scheduling algorithms must produce consistent, testable behaviors
  - Memory coherence protocols must demonstrably maintain data consistency

- **Performance Expectations**:
  - Support simulation of at least 16 virtual cores
  - Execute at least 10,000 instructions per second per simulated core
  - Context switching overhead should be realistically proportional to real systems
  - Memory coherence simulation should scale efficiently with core count
  - Visualization data generation should not significantly impact simulation performance

- **Integration Points**:
  - Parallel algorithm definition API
  - Execution trace export mechanism
  - Configurable thread scheduling policies
  - Customizable memory hierarchy specifications
  - Pluggable cache coherence protocol implementations

- **Key Constraints**:
  - Must be deterministic when required for analysis purposes
  - Should accurately represent parallel execution semantics
  - Must provide sufficient instrumentation without excessive performance impact
  - Should isolate different aspects of parallel computing for focused study

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
1. **Multi-Core Simulation Engine**: Implement a virtual machine supporting multiple execution cores with individual instruction streams, shared memory access, and coordination mechanisms.

2. **Memory Hierarchy Simulation**: Create a detailed memory system model with multiple cache levels, main memory, and configurable coherence protocols to simulate realistic memory access patterns and constraints.

3. **Synchronization Primitives**: Provide implementations of common synchronization mechanisms including mutexes, semaphores, condition variables, barriers, and atomic operations with correct semantics.

4. **Thread Scheduler**: Implement a configurable thread scheduling system with different policies, priority management, context switching, and core allocation strategies.

5. **Race Condition Simulator**: Develop tools for creating, detecting, analyzing, and visualizing race conditions with controlled execution timing to ensure reproducibility.

6. **Execution Tracing**: Create comprehensive instruction-level tracing of parallel execution, memory access patterns, synchronization events, and scheduling decisions.

7. **Performance Analysis**: Provide detailed metrics and analysis tools for measuring parallel efficiency, synchronization overhead, memory contention, and other critical parallel performance factors.

## Testing Requirements
- **Key Functionalities to Verify**:
  - Correct parallel execution of instructions across multiple cores
  - Proper implementation of synchronization primitives
  - Accurate modeling of memory coherence protocols
  - Realistic thread scheduling behavior
  - Reliable reproduction of race conditions

- **Critical User Scenarios**:
  - Executing common parallel algorithms like map-reduce or parallel sort
  - Demonstrating synchronization issues like deadlock or priority inversion
  - Analyzing the performance impact of different cache coherence protocols
  - Comparing the efficiency of different thread scheduling policies
  - Studying memory access patterns and their effect on parallel performance

- **Performance Benchmarks**:
  - Support simulation of at least 16 virtual cores simultaneously
  - Execute standard parallel benchmarks at a rate of at least 10,000 instructions per second per core
  - Complete context switches in a proportionally realistic time frame
  - Handle memory systems with at least 3 cache levels and configurable parameters
  - Generate execution traces with minimal performance impact (less than 20% overhead)

- **Edge Cases and Error Conditions**:
  - Handle deadlock detection and reporting
  - Properly identify and analyze race conditions
  - Manage priority inversion scenarios
  - Report memory consistency violations
  - Handle resource exhaustion conditions

- **Required Test Coverage Metrics**:
  - 95% code coverage for the core parallel execution engine
  - 100% coverage for synchronization primitive implementations
  - 95% coverage for memory coherence protocol implementations
  - 90% coverage for thread scheduling algorithms
  - 90% coverage for race condition detection logic

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
1. Accurately demonstrates parallel execution patterns across multiple simulated cores
2. Reliably reproduces race conditions and other concurrency issues for analysis
3. Correctly implements standard synchronization primitives with proper semantics
4. Realistically models thread scheduling and context switching behavior
5. Effectively simulates memory coherence protocols and their performance impacts
6. Provides detailed and accurate performance metrics for parallel algorithm analysis
7. Helps Dr. Patel gain new insights into parallel algorithm behavior and optimization

To set up your environment, use `uv venv` to create a virtual environment. From within the project directory, the environment can be activated with `source .venv/bin/activate`.