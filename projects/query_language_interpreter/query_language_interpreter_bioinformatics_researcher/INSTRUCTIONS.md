# Genomic Data Query Language Interpreter

## Overview
This specialized Query Language Interpreter enables bioinformatics researchers to efficiently query across genomic sequences, protein databases, and experimental results without forcing the data into traditional database structures. The interpreter supports sequence alignment operations, integrates biological metadata, incorporates taxonomic awareness, calculates chemical properties, and handles coordinate system mappings, making it a powerful tool for genomic research.

## Persona Description
Dr. Chen studies genomic data and needs to query across genome sequences, protein databases, and experimental results. She requires specialized operators for biological data types without forcing everything into traditional database structures.

## Key Requirements
1. **Sequence alignment operators for DNA/RNA/protein comparison queries**: Enables researchers to perform sequence similarity searches, alignments, and pattern matching directly within queries, allowing for the identification of sequence motifs, mutations, and conserved regions across genomic data without requiring separate bioinformatics tools for each analysis step.

2. **Biological metadata integration combining sequence and experimental data**: Seamlessly links sequence data with associated experimental metadata (expression levels, phenotype associations, clinical outcomes, etc.), enabling researchers to filter sequences based on experimental conditions or identify correlations between genetic features and experimental results.

3. **Species taxonomy awareness enabling hierarchical biological classification queries**: Incorporates taxonomic relationships between species, allowing researchers to perform queries that automatically include or exclude data from specific taxonomic groups, facilitating comparative genomics studies and evolutionary analyses across different branches of the tree of life.

4. **Chemical property calculators for protein and small molecule analysis**: Provides built-in functions for calculating key chemical and physical properties of biological molecules (hydrophobicity, charge, molecular weight, isoelectric point, etc.), enabling researchers to filter and analyze sequences based on their physicochemical characteristics.

5. **Genome coordinate system mappings between different reference assemblies**: Handles the complexity of different genome assembly versions and coordinate systems, automatically translating genomic coordinates between reference assemblies, enabling researchers to integrate data from studies using different genome versions without manual coordinate conversion.

## Technical Requirements
### Testability Requirements
- All sequence alignment algorithms must be testable against known reference alignments
- Taxonomic queries must be verified against established taxonomic databases
- Chemical property calculations must be validated against published values
- Coordinate conversions must be tested with known mapping coordinates
- Integration of sequence and experimental data must be verified for accuracy

### Performance Expectations
- Must efficiently handle typical genomic datasets (human genome ~3GB)
- Sequence alignment operations should optimize for the specific alignment type
- Taxonomy operations should have O(log n) lookup complexity
- Chemical property calculations should be cached for repeated access
- Performance should scale linearly with sequence length for most operations

### Integration Points
- Support for standard bioinformatics file formats (FASTA, FASTQ, VCF, BAM, etc.)
- Integration with biological databases (RefSeq, UniProt, GO, etc.)
- Compatibility with existing bioinformatics tools and libraries
- Export capabilities to formats used in downstream analysis tools
- Potential integration with visualization tools through data export

### Key Constraints
- All operations must maintain biological accuracy and precision
- Implementation must handle the large data volumes typical in genomics
- Query execution should be optimizable for memory-constrained environments
- Core functionality must be usable without network connectivity
- Performance must be acceptable for interactive research usage

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The core functionality of this Genomic Data Query Language Interpreter includes:

1. **Query Engine with Biological Extensions**:
   - SQL-like syntax extended with bioinformatics-specific operations
   - Parser capable of handling sequence patterns and biological expressions
   - Execution planning optimized for genomic data operations
   - Support for streaming large sequence datasets

2. **Sequence Analysis Framework**:
   - Implementation of key sequence alignment algorithms
   - Pattern matching for sequence motifs and features
   - Translation between nucleotide and protein sequences
   - Statistical methods for sequence comparison

3. **Biological Data Integration**:
   - Connectors for various biological data formats
   - Linking mechanisms between sequence and experimental data
   - Metadata extraction and indexing for efficient queries
   - Schema flexibility for diverse experimental data types

4. **Taxonomic System**:
   - Hierarchical taxonomy representation
   - Efficient lookup and traversal operations
   - Query operators for taxonomic relationships
   - Integration with taxonomic reference databases

5. **Biological Property Calculators**:
   - Implementations of key physicochemical property calculations
   - Property-based filtering and comparison operations
   - Scaling methods for multi-property analysis
   - Statistical functions for property distributions

## Testing Requirements
### Key Functionalities to Verify
- Accuracy of sequence alignment algorithms against benchmark datasets
- Correct taxonomic query resolution across the tree of life
- Precision of chemical property calculations for diverse molecules
- Accurate coordinate mapping between genome assemblies
- Proper integration of sequence data with experimental metadata

### Critical User Scenarios
- Identifying conserved sequences across multiple species
- Finding correlations between genetic variants and experimental outcomes
- Analyzing protein sequences based on their chemical properties
- Integrating data from studies using different genome assembly versions
- Performing comparative genomics across specific taxonomic groups

### Performance Benchmarks
- Sequence alignment queries should complete within 5 seconds for sequences up to 10KB
- Taxonomic queries should provide results in under 1 second
- Chemical property calculations should process at least 1000 protein sequences per second
- Coordinate mapping should handle at least 10,000 conversions per second
- Overall system should accommodate datasets of at least 10GB with reasonable performance

### Edge Cases and Error Conditions
- Handling of extremely long genomic sequences
- Proper treatment of non-standard nucleotides or amino acids
- Behavior with incomplete or uncertain taxonomic information
- Graceful handling of unmappable genome coordinates
- Appropriate error messages for biologically impossible queries

### Required Test Coverage Metrics
- Minimum 90% code coverage across all modules
- 100% coverage for core biological algorithms and calculations
- All taxonomic edge cases must be explicitly tested
- Coordinate mapping must be tested with edge cases from different assemblies
- All supported file formats must have comprehensive parsing tests

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
A successful implementation will:

1. Enable biologists to perform effective sequence alignment and comparison operations, verified by tests with benchmark sequence datasets
2. Successfully integrate sequence and experimental data, demonstrated by test queries combining both data types
3. Correctly handle taxonomic relationships in queries, validated with tests spanning diverse taxonomic groups
4. Accurately calculate chemical properties for biological molecules, confirmed through comparison with reference values
5. Properly translate genomic coordinates between assemblies, verified with test cases of known coordinate mappings

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup

To set up your development environment:

```bash
# From within the project directory
uv venv
source .venv/bin/activate
uv pip install -e .
```

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY for project completion:
```bash
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```