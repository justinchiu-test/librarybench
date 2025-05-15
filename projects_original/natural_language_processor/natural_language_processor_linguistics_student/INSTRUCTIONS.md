# Educational NLP Algorithm Visualizer

A natural language processing toolkit designed specifically for computational linguistics students to visualize, compare, and understand core NLP algorithms by implementing them from scratch.

## Overview

This project provides an educational framework for computational linguistics students to implement, visualize, and experiment with fundamental NLP algorithms from scratch. Rather than using black-box libraries, this toolkit enables deep understanding of how language processing techniques work by allowing students to see every step of the algorithm's operation, compare different approaches, and connect implementations to linguistic theory.

## Persona Description

Maya is a graduate student studying computational linguistics who wants to understand NLP algorithms by implementing them from scratch rather than using black-box libraries. Her primary goal is to gain deep intuition about how language processing techniques work while building a portfolio project for future job applications.

## Key Requirements

1. **Algorithm Visualization Framework**: Create a system that renders step-by-step visualizations of NLP algorithm execution, showing how text data transforms through each phase of processing.
   - This feature is critical as it allows Maya to observe internal algorithm states, helping her understand complex NLP processes that are typically hidden in standard libraries.
   - The visualization should reveal parsing trees, token transitions, and algorithmic decision points.

2. **Comparative Analysis System**: Implement a framework that allows side-by-side execution of different approaches to the same NLP task (e.g., rule-based vs. statistical POS tagging).
   - This capability is essential for Maya to understand the trade-offs, strengths, and weaknesses of different NLP approaches on identical input.
   - Comparisons should include accuracy metrics, processing time, and step-by-step difference highlighting.

3. **Academic Paper Implementation Templates**: Develop a system of templates that map published NLP research algorithms to code implementations.
   - This feature bridges the gap between academic theory and practical implementation, allowing Maya to understand how theoretical concepts translate to actual code.
   - Templates should include placeholders for key algorithm components with references to corresponding paper sections.

4. **Performance Profiling Tools**: Create profiling utilities that measure algorithm efficiency, memory usage, and processing time with detailed breakdowns by component.
   - These tools help Maya identify performance bottlenecks and understand the computational complexity implications of different algorithm design choices.
   - Profiling should highlight optimization opportunities and demonstrate algorithmic complexity in practice.

5. **Linguistic Theory Annotations**: Develop a framework for annotating code implementations with formal linguistic concepts and theoretical foundations.
   - This feature connects code to the underlying linguistic principles, helping Maya build a stronger theoretical understanding alongside implementation skills.
   - Annotations should link specific code sections to recognized linguistic frameworks and relevant academic references.

## Technical Requirements

### Testability Requirements
- All algorithm visualization outputs must be capturable in a standardized format for automated testing
- Each algorithm step must expose intermediate state for validation
- All comparative metrics must be quantifiable and verifiable
- Profiling results must be consistent and reproducible across test runs
- Linguistic annotations must be programmatically verifiable against reference standards

### Performance Expectations
- Algorithm visualization generation must complete within 5 seconds for texts up to 10,000 tokens
- Comparative analysis should handle at least 5 different algorithm variations simultaneously
- Memory usage should not exceed 1GB for standard NLP tasks on texts up to 50,000 tokens
- Profiling overhead should not increase processing time by more than 20%
- All operations should be optimized to run on standard laptop hardware without GPU acceleration

### Integration Points
- The system should accept standard text corpus formats (TXT, CSV, JSON)
- Implemented algorithms should be comparable with standard metrics used in academic literature
- Visualization output should be serializable to common formats for inclusion in research papers
- Code annotations should follow a standardized format that can be extracted for documentation
- Profiling data should be exportable to formats compatible with academic analysis tools

### Key Constraints
- All implementations must be in pure Python with no dependencies on external NLP libraries
- Algorithms must be implemented from first principles, not wrappers around existing tools
- Visualization must be data-driven and serializable, not graphical
- Memory usage must be carefully managed to enable processing of large linguistic corpora
- All components must be individually testable without dependencies on other system parts

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system consists of five main components:

1. **Algorithm Visualization Engine**: A framework that captures and exposes the state of NLP algorithms at each processing step. It should:
   - Provide hooks for recording algorithm state at arbitrary execution points
   - Generate structured representations of algorithm progress (parse trees, token transformations, etc.)
   - Support custom visualization adapters for different algorithm types
   - Maintain execution history for replay and analysis
   - Allow step-by-step progression through algorithm execution

2. **Comparative Analysis Framework**: A system for running multiple algorithm implementations on the same input and comparing results. It should:
   - Execute multiple algorithm variants with identical inputs
   - Calculate standard NLP evaluation metrics (precision, recall, F1, etc.)
   - Generate difference reports highlighting divergent behavior
   - Measure and compare performance characteristics
   - Support custom comparison metrics for specialized algorithms

3. **Academic Implementation System**: A structured approach to implementing algorithms from research papers. It should:
   - Provide template structures mapping paper sections to code components
   - Include citation management and reference linking
   - Support validation against published results
   - Enable progressive refinement from basic to advanced implementations
   - Maintain traceability between paper descriptions and code

4. **Performance Profiling Toolkit**: A specialized profiling system for NLP algorithms. It should:
   - Measure execution time at the function and algorithm stage level
   - Track memory allocation and usage patterns
   - Count operations for computational complexity analysis
   - Identify bottlenecks and optimization opportunities
   - Generate profiling reports with actionable insights

5. **Linguistic Annotation System**: A framework for connecting code to linguistic theory. It should:
   - Link code sections to relevant linguistic concepts
   - Provide references to academic literature and theoretical frameworks
   - Support validation of linguistic correctness
   - Enable querying code by linguistic concept
   - Generate documentation connecting implementation to theory

## Testing Requirements

### Key Functionalities to Verify

1. Algorithm Visualization:
   - Test that all algorithm steps are correctly captured and serialized
   - Verify visualization data structures accurately represent algorithm state
   - Confirm deterministic behavior with identical inputs
   - Test boundary cases (empty text, very long text, special characters)
   - Validate completeness of algorithm state capture

2. Comparative Analysis:
   - Test accuracy of comparative metrics against known standards
   - Verify that differences between algorithms are correctly identified
   - Test performance measurement accuracy
   - Validate behavior with extreme algorithm performance differences
   - Confirm statistical validity of comparison methods

3. Academic Implementation:
   - Test template completeness for standard algorithm types
   - Verify reference management functionality
   - Test against published algorithm examples with known outputs
   - Validate reproducibility of published results
   - Confirm proper algorithm parameterization

4. Performance Profiling:
   - Test accuracy of timing measurements
   - Verify memory tracking precision
   - Validate computational complexity calculations
   - Test consistency across multiple runs
   - Confirm minimal overhead from profiling instrumentation

5. Linguistic Annotations:
   - Test correctness of linguistic concept mapping
   - Verify annotation completeness
   - Validate reference accuracy
   - Test query functionality by linguistic concept
   - Confirm annotation persistence across code revisions

### Critical User Scenarios

1. Implementing a new tokenization algorithm while visualizing each step
2. Comparing three different part-of-speech tagging approaches on ambiguous sentences
3. Implementing and annotating a published sentiment analysis algorithm
4. Profiling and optimizing a computationally expensive parsing algorithm
5. Annotating a coreference resolution implementation with linguistic theory

### Performance Benchmarks

- Algorithm visualization must process text at a rate of at least 1000 tokens per second
- Comparative analysis framework must support at least 5 simultaneous algorithm comparisons
- Academic implementation templates must support at least 20 different algorithm types
- Performance profiling must add no more than 20% overhead to execution time
- Linguistic annotation queries must complete in under 100ms

### Edge Cases and Error Conditions

- Test with extremely long tokens and sentences
- Verify behavior with malformed or inconsistent inputs
- Test recovery from algorithm failures or exceptions
- Validate behavior with resource constraints (memory limitations)
- Test with multilingual and non-standard text inputs
- Verify correct handling of recursive or cyclical linguistic structures
- Test with conflicting linguistic theories and annotation schemes

### Required Test Coverage Metrics

- Line coverage: Minimum 90%
- Branch coverage: Minimum 85%
- Function coverage: Minimum 95%
- All public APIs must have 100% test coverage
- All error handling paths must be tested
- All visualization and comparison logic must be thoroughly tested

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

- The system produces accurate visualizations for at least 5 core NLP algorithms (tokenization, POS tagging, parsing, NER, sentiment analysis)
- Comparative analysis correctly identifies advantages and disadvantages of different algorithm approaches
- Academic implementations successfully reproduce results from at least 3 published papers
- Performance profiling correctly identifies algorithmic complexity and bottlenecks
- Linguistic annotations correctly map code to established linguistic theories

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Development Setup

To set up your development environment:

1. Create a virtual environment using uv:
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

4. Install testing tools:
   ```
   pip install pytest pytest-json-report
   ```

5. Run tests with JSON reporting:
   ```
   pytest --json-report --json-report-file=pytest_results.json
   ```

IMPORTANT: Generating and providing the pytest_results.json file is a CRITICAL requirement for project completion. This file serves as proof that all tests pass and the implementation meets the specified requirements.