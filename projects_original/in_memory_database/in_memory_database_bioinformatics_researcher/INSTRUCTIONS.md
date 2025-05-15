# GenomeDB: Hybrid In-Memory/Disk Database for Genomic Research

## Overview
A specialized hybrid in-memory/disk database optimized for genomic data analysis that efficiently manages large biological datasets exceeding available RAM. The system provides optimized access to genomic regions, specialized compression for biological sequences, graph relationship modeling, vectorized operations, and seamless integration with scientific Python libraries.

## Persona Description
Dr. Patel analyzes genomic data sets requiring both fast random access and complex relationship queries. She needs to efficiently process large biological datasets that exceed available RAM.

## Key Requirements

1. **Hybrid Memory/Disk Storage with Intelligent Caching**
   - Implementation of a hybrid storage system that keeps frequently accessed genomic regions in memory
   - Intelligent caching strategies based on access patterns and region importance
   - Transparent performance optimization that makes disk-backed data appear to be in-memory
   - This feature is critical for Dr. Patel as genomic datasets often exceed available RAM, but research typically focuses on specific regions at a time, making intelligent caching essential for maintaining performance while handling complete genomes

2. **Specialized Compression for Biological Sequence Data**
   - Implementation of domain-specific compression algorithms for different biological sequence types (DNA, RNA, protein)
   - Compression techniques that preserve direct queryability without full decompression
   - Support for standard biological file formats and compression standards
   - Genomic data is highly compressible with specialized algorithms, and effective compression directly impacts the volume of data that can be analyzed, allowing Dr. Patel to work with larger datasets or more samples simultaneously

3. **Graph Relationship Modeling for Biological Pathways**
   - Implementation of graph data structures for representing biological relationships and pathways
   - Support for common graph queries (paths, neighbors, centrality, etc.)
   - Integration of sequence and graph data in unified queries
   - Understanding biological relationships is central to Dr. Patel's research, requiring efficient graph structures to model pathways, protein interactions, and other biological networks alongside sequence data

4. **Vectorized Operations for Genomic Calculations**
   - Implementation of vectorized operations optimized for common genomic analyses
   - Support for sliding window calculations, sequence alignment scoring, motif finding, etc.
   - Performance optimization for compute-intensive genomic algorithms
   - Genomic research involves computationally intensive operations that benefit significantly from vectorized implementations, enabling Dr. Patel to perform complex analyses in reasonable timeframes

5. **Integration with Scientific Python Libraries**
   - Seamless integration with NumPy, Pandas, BioPython, and other scientific Python libraries
   - Support for direct data exchange without copying or conversion overhead
   - Compatibility with common bioinformatics workflows and tools
   - Dr. Patel's existing analysis pipelines rely on scientific Python libraries, making transparent integration essential for incorporating this database into her workflows without disruption

## Technical Requirements

### Testability Requirements
- Caching strategies must be benchmarkable with different access patterns
- Compression effectiveness must be measurable for various biological sequence types
- Graph queries must be testable for accuracy and performance
- Vectorized operations must be verifiable against reference implementations
- Integration with scientific libraries must be tested for data integrity and performance

### Performance Expectations
- Random access to cached genomic regions should occur in under 10ms
- Compression should achieve at least 4:1 ratio for typical genomic sequences
- Graph operations should scale efficiently to networks with 100,000+ nodes
- Vectorized operations should be at least 10x faster than naive implementations
- Data exchange with scientific libraries should have minimal overhead

### Integration Points
- APIs compatible with standard bioinformatics tools and workflows
- Support for common genomic file formats (FASTA, FASTQ, VCF, BAM, etc.)
- Interfaces for exchanging data with NumPy, Pandas, and BioPython
- Export capabilities for visualization tools
- Integration with existing analysis pipelines

### Key Constraints
- The implementation must use only Python standard library with no external dependencies
- The system must operate efficiently even when data exceeds available RAM
- Memory usage must be carefully managed to prevent out-of-memory conditions
- All operations must preserve biological data integrity and accuracy

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system must provide the following core functionality:

1. **Hybrid Storage Engine**
   - Efficient management of data across memory and disk tiers
   - Intelligent caching mechanisms for genomic regions
   - Optimized access patterns for biological data

2. **Biological Sequence Management**
   - Specialized storage and compression for DNA, RNA, and protein sequences
   - Efficient sequence manipulation and querying
   - Support for standard biological operations (reverse complement, translation, etc.)

3. **Graph Relationship System**
   - Implementation of graph data structures for biological networks
   - Query capabilities for relationship analysis
   - Integration of sequence and relationship data

4. **Vectorized Computation Framework**
   - Implementation of optimized algorithms for common genomic calculations
   - Support for sliding window analyses
   - Accelerated implementations of sequence comparison operations

5. **Scientific Library Integration**
   - Data exchange interfaces with NumPy and Pandas
   - BioPython compatibility layers
   - Support for scientific workflows and pipelines

## Testing Requirements

### Key Functionalities to Verify
- Efficient access to genomic data spanning memory and disk
- Effective compression of biological sequence data
- Accurate representation and querying of biological pathways
- Performance of vectorized genomic calculations
- Seamless integration with scientific Python libraries

### Critical User Scenarios
- Analysis of specific genomic regions across multiple samples
- Identification of patterns in compressed sequence data
- Pathway analysis using graph relationships
- Compute-intensive operations on large sequence datasets
- Integration with existing bioinformatics pipelines

### Performance Benchmarks
- Random access to frequently accessed regions should occur in under 10ms
- Compression should achieve at least 4:1 ratio for typical genomic sequences
- Graph queries should complete in under 100ms for networks with up to 100,000 nodes
- Vectorized operations should be at least 10x faster than naive implementations
- The system should handle datasets at least 5x larger than available RAM

### Edge Cases and Error Conditions
- Behavior when memory limits are reached
- Recovery from corrupted or incomplete data
- Handling of extremely large sequences or complex networks
- Performance with unusual access patterns
- Operation with limited system resources

### Required Test Coverage Metrics
- Minimum 90% code coverage for all modules
- 100% coverage of data integrity and biological calculation code
- All error recovery paths must be tested
- Performance tests must cover typical biological workflow patterns
- Integration tests must verify compatibility with scientific libraries

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

The implementation will be considered successful if:

1. It effectively manages genomic data spanning memory and disk with transparent performance optimization
2. Biological sequences are efficiently compressed while maintaining queryability
3. Graph relationships accurately model biological pathways and networks
4. Vectorized operations significantly accelerate common genomic calculations
5. Integration with scientific Python libraries is seamless and efficient

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Development Setup

To set up the development environment:

1. Clone the repository and navigate to the project directory
2. Create a virtual environment using:
   ```
   uv venv
   ```
3. Activate the virtual environment:
   ```
   source .venv/bin/activate
   ```
4. Install the project in development mode:
   ```
   uv pip install -e .
   ```
5. Run tests with:
   ```
   pip install pytest-json-report
   pytest --json-report --json-report-file=pytest_results.json
   ```

CRITICAL REMINDER: Generating and providing the pytest_results.json file is a MANDATORY requirement for project completion.