# Genomic Data Query Interpreter

A specialized query language interpreter for bioinformatics research with support for sequence alignment, biological metadata integration, taxonomy-aware queries, and genome coordinate mappings.

## Overview

This project implements a query language interpreter designed specifically for genomic and biological data analysis. It allows bioinformatics researchers to query across genome sequences, protein databases, and experimental results without forcing everything into traditional database structures. The interpreter includes specialized operators for biological data types and enables complex cross-dataset queries essential for genomic research.

## Persona Description

Dr. Chen studies genomic data and needs to query across genome sequences, protein databases, and experimental results. She requires specialized operators for biological data types without forcing everything into traditional database structures.

## Key Requirements

1. **Sequence Alignment Operators**
   - Implement specialized query operators for DNA/RNA/protein sequence alignment
   - Support common alignment algorithms (e.g., local, global, Smith-Waterman, BLAST-like)
   - Enable sequence similarity searches with configurable match/mismatch parameters
   - Include gap penalty models and scoring systems for different biological contexts
   - Critical for Dr. Chen to find patterns and similarities across genetic sequences, identify gene homologs, and locate conserved regions within genomes

2. **Biological Metadata Integration**
   - Combine sequence data with experimental annotations and functional information
   - Support integration of data from standard bioinformatics formats (FASTA, GFF, VCF, etc.)
   - Enable joins between sequence features and experimental measurements
   - Create virtual relationships between different biological data repositories
   - Essential for connecting raw sequence data with functional information, experimental results, and published findings to generate biological insights

3. **Species Taxonomy Awareness**
   - Implement hierarchical biological classification queries based on taxonomic relationships
   - Support querying across evolutionary distances with species-aware operators
   - Enable phylogenetic filtering and grouping in queries
   - Include common taxonomic databases with standard identifiers
   - Important for comparing genetic features across different species, studying evolutionary relationships, and understanding conservation patterns across the tree of life

4. **Chemical Property Calculators**
   - Integrate biophysical and biochemical property calculations for protein and small molecule analysis
   - Support queries based on properties like hydrophobicity, charge, molecular weight
   - Enable filtering and aggregation based on chemical properties
   - Include standard scales and models used in bioinformatics
   - Crucial for analyzing protein domains, predicting functional regions, and understanding molecular interactions based on physical and chemical characteristics

5. **Genome Coordinate System Mappings**
   - Handle conversions between different genome assembly versions and coordinate systems
   - Support lift-over operations for genomic coordinates across reference assemblies
   - Enable querying features regardless of the underlying coordinate system
   - Maintain relationships between relative and absolute genomic positions
   - Critical for working with data from different sources that reference different genome assembly versions, ensuring consistent analysis across studies and databases

## Technical Requirements

### Testability Requirements
- Sequence alignment functions must be verifiable against established bioinformatics tools
- Taxonomic queries must produce results consistent with biological classification
- Property calculations must match published reference values
- Coordinate conversions must be validated against standard genome mappings
- Integration operations must preserve biological relationships in test datasets

### Performance Expectations
- Handle reference genomes up to 3GB in size without external database requirements
- Complete local sequence alignment queries within 30 seconds for sequences < 100KB
- Support batch processing of thousands of short sequence alignments
- Process taxonomic queries across the full tree of life in under 10 seconds
- Complete coordinate conversion operations in milliseconds per position

### Integration Points
- Import data from standard bioinformatics file formats (FASTA, FASTQ, SAM/BAM, VCF, GFF)
- Export results in formats compatible with visualization tools
- Integration with biological databases through standard APIs
- Support for high-throughput sequencing data processing pipelines
- Interoperability with common bioinformatics Python libraries

### Key Constraints
- Must operate without requiring all data to be loaded into memory simultaneously
- No external alignment algorithm dependencies outside standard libraries
- All operations must be reproducible with version tracking
- Must handle both nucleotide and protein sequences with appropriate algorithms
- Privacy preservation for sensitive genetic data

## Core Functionality

The core of this Query Language Interpreter includes:

1. **Biological Sequence Parser**
   - Handle standard bioinformatics file formats
   - Support for nucleotide and protein sequences
   - Efficient storage and indexing of genomic data
   - Quality score integration for sequencing data

2. **Sequence Analysis Engine**
   - Implement alignment algorithms for biological sequences
   - Support pattern matching with biological variations
   - Enable motif searching and feature detection
   - Provide statistical significance scoring

3. **Biological Data Integrator**
   - Join heterogeneous biological data sources
   - Handle cross-references between databases
   - Resolve biological identifiers across systems
   - Support ontology-based data integration

4. **Taxonomic Query Processor**
   - Implement hierarchical taxonomic operations
   - Support evolutionary distance calculations
   - Enable species-aware comparative queries
   - Integrate with standard taxonomic databases

5. **Coordinate System Manager**
   - Handle genome assembly version conversions
   - Support relative and absolute position references
   - Implement efficient coordinate mapping
   - Maintain feature location integrity across mappings

## Testing Requirements

### Key Functionalities to Verify
- Accuracy of sequence alignment algorithms compared to reference implementations
- Correct integration of sequence data with functional annotations
- Proper taxonomic relationship handling in hierarchical queries
- Accuracy of chemical and physical property calculations
- Correct coordinate conversion across genome assemblies

### Critical User Scenarios
- Finding conserved gene regions across multiple species
- Correlating genetic variations with experimental phenotypes
- Analyzing protein domains based on chemical properties
- Comparing genomic features across different assembly versions
- Identifying and categorizing gene families based on sequence similarity

### Performance Benchmarks
- Complete BLAST-like alignment on a 10KB sequence against a 100MB database in under 60 seconds
- Process taxonomic classification queries for 10,000 sequences in under 5 minutes
- Calculate chemical properties for 1,000 protein sequences in under 30 seconds
- Convert 100,000 genomic coordinates between assemblies in under 60 seconds
- Join sequence features with experimental data at a rate of 10,000 records per second

### Edge Cases and Error Conditions
- Handling ambiguous nucleotides and non-standard amino acids
- Managing incomplete or uncertain taxonomic classifications
- Dealing with contradictory annotations from different sources
- Processing circular genomes and alternative splicing variants
- Handling unassembled or partially assembled genome regions

### Required Test Coverage Metrics
- 95% code coverage for sequence alignment algorithms
- 100% coverage for coordinate conversion functions
- Comprehensive testing of taxonomic query operators
- Validation of chemical property calculations against reference values
- Integration tests for all supported file formats

## Success Criteria

1. Sequence alignment operations produce results consistent with standard bioinformatics tools
2. Biological metadata integrations correctly preserve relationships between features
3. Taxonomic queries properly respect evolutionary hierarchies and classifications
4. Chemical property calculations match accepted values in the field
5. Genome coordinate conversions accurately map positions across assembly versions
6. Researchers can analyze complex genomic datasets without extracting to specialized tools
7. Queries across heterogeneous biological data execute within performance benchmarks
8. The system integrates with common bioinformatics workflows

## Getting Started with Development

To start developing this project:

1. Set up the development environment using `uv`:
   ```
   uv init --lib
   ```

2. Manage dependencies with `uv`:
   ```
   uv pip install biopython numpy pandas
   ```

3. Run your code with:
   ```
   uv run python your_script.py
   ```

4. Run tests with:
   ```
   uv run pytest
   ```