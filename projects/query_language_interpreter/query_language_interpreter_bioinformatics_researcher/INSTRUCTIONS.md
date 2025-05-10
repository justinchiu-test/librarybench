# Genomic Data Query Engine

A query language interpreter specialized for biological sequence analysis with integrated genomic operations.

## Overview

The Genomic Data Query Engine provides a specialized query language interpreter for genomic data analysis. This project variant focuses on enabling bioinformatics researchers to query across genome sequences, protein databases, and experimental results without forcing data into traditional database structures, featuring specialized biological operators, taxonomic awareness, and sequence analysis functions.

## Persona Description

Dr. Chen studies genomic data and needs to query across genome sequences, protein databases, and experimental results. She requires specialized operators for biological data types without forcing everything into traditional database structures.

## Key Requirements

1. **Sequence alignment operators for DNA/RNA/protein comparison queries**
   - Implement efficient alignment algorithms (local, global, semi-global)
   - Support specialized biological scoring matrices (BLOSUM, PAM)
   - Enable complex pattern searching in biological sequences (motifs, domains)
   - Provide specialized indexing for large sequence databases
   - Critical for Dr. Chen to identify similarities between sequences and find biologically significant patterns across large genomic datasets

2. **Biological metadata integration combining sequence and experimental data**
   - Develop join operations specialized for connecting sequences with their experimental contexts
   - Support integration of heterogeneous data types (sequences, expression levels, phenotypes, conditions)
   - Enable queries that combine sequence features with experimental measurements
   - Provide biological data type conversions and normalizations
   - Essential for connecting genetic data with phenotypic observations and experimental conditions to find meaningful correlations

3. **Species taxonomy awareness enabling hierarchical biological classification queries**
   - Implement taxonomy tree traversal for organism-based queries
   - Support common taxonomic classification systems (NCBI Taxonomy, etc.)
   - Enable queries grouped by taxonomic rank (domain, kingdom, phylum, class, order, family, genus, species)
   - Provide evolutionary distance calculations between organisms
   - Important for comparative genomics studies that examine how genes and features vary across evolutionary relationships

4. **Chemical property calculators for protein and small molecule analysis**
   - Create functions for computing key molecular properties (molecular weight, isoelectric point, hydrophobicity)
   - Support analysis of amino acid composition and physicochemical properties
   - Enable property-based filtering and comparison of biological molecules
   - Implement chemical similarity measures for structure comparison
   - Critical for understanding the biochemical implications of genetic variations and predicting functional properties

5. **Genome coordinate system mappings between different reference assemblies**
   - Develop coordinate translation between genome assembly versions
   - Support conversion between chromosome coordinates and gene/exon coordinates
   - Enable queries that work consistently across different reference genomes
   - Implement liftover operations for translating features between assemblies
   - Vital for integrating data generated using different genome reference versions and ensuring consistent analysis

## Technical Requirements

### Testability Requirements
- All biological algorithms must have comprehensive unit tests with pytest
- Test sequence alignment against established reference implementations
- Verify taxonomy operations with standard taxonomic trees
- Test coordinate mapping with well-documented reference genomes
- Validate property calculations against established biochemical formulas

### Performance Expectations
- Execute sequence alignment queries on 100MB sequences in under 30 seconds
- Support genomic coordinate queries across whole-genome datasets (>3GB)
- Process integrated queries joining sequence and experimental data at 10,000 records/second
- Handle taxonomic queries across databases with >1 million species
- Support interactive query response times (<5 seconds) for common operations

### Integration Points
- Import data from standard bioinformatics formats (FASTA, GenBank, GFF, VCF, PDB)
- Connect with biological databases (NCBI, UniProt, PDB, Ensembl)
- Utilize established bioinformatics libraries (Biopython, NCBI E-utilities)
- Export results in formats compatible with visualization and analysis tools
- Support standard ontologies (Gene Ontology, UMLS, MeSH)

### Key Constraints
- Process large sequence datasets without loading everything into memory
- Maintain biological accuracy in all calculations and transformations
- Support both nucleotide and protein sequence operations
- Handle the diverse and evolving nature of biological data formats
- Preserve provenance of biological data throughout analyses

### Implementation Notes
IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The Genomic Data Query Engine must implement the following core functionality:

1. **Biological Sequence Processing**
   - Parse and represent DNA, RNA, and protein sequences
   - Implement sequence alignment algorithms
   - Support pattern matching and motif finding
   - Enable sequence transformation operations (translation, reverse complement)

2. **Query Language Interpreter**
   - Develop biological data type awareness in query parsing
   - Implement specialized operators for biological operations
   - Support complex query patterns joining sequence and experimental data
   - Optimize query execution for biological data characteristics

3. **Metadata and Annotation Management**
   - Handle diverse biological annotation formats
   - Maintain relationships between sequences and their annotations
   - Support ontology-based querying
   - Enable evidence code filtering and provenance tracking

4. **Taxonomic and Evolutionary Analysis**
   - Implement taxonomic tree representation and traversal
   - Support evolutionary distance calculations
   - Enable comparative queries across taxonomic groups
   - Provide phylogenetic analysis capabilities

5. **Coordinate Systems and Assembly Management**
   - Support various genomic coordinate systems
   - Implement mapping between reference genome versions
   - Provide feature coordinate translation
   - Handle structural variations and complex genomic regions

## Testing Requirements

### Key Functionalities to Verify
- Correct implementation of sequence alignment algorithms
- Accurate integration of sequence and experimental data
- Proper taxonomic query execution and grouping
- Correct calculation of biological properties
- Accurate coordinate system transformations

### Critical User Scenarios
- Finding conserved sequence motifs across evolutionary distant species
- Correlating genetic variations with experimental phenotypes
- Analyzing protein structural features across a taxonomic family
- Mapping features from one genome assembly to another
- Identifying patterns in gene expression across experimental conditions

### Performance Benchmarks
- Align 10,000 short sequences against a reference genome in under 5 minutes
- Process taxonomic queries across the tree of life in under 10 seconds
- Execute joins between sequence and experimental data at >10,000 records/second
- Calculate properties for 1,000 protein sequences in under 30 seconds
- Complete coordinate liftover for 100,000 genome features in under 3 minutes

### Edge Cases and Error Conditions
- Handling extremely large genomic sequences (>100MB)
- Processing highly repetitive sequences with alignment ambiguity
- Managing inconsistent taxonomic classifications
- Dealing with incomplete or draft genome assemblies
- Handling conflicts in annotation from different sources

### Required Test Coverage Metrics
- Minimum 90% code coverage for all modules
- 100% coverage of core biological algorithms
- Test with sequences of varying lengths (1 bp to 100 Mbp)
- Verify operations across at least 5 taxonomic kingdoms
- Test coordinate mapping with at least 3 different genome assemblies per species

## Success Criteria

The implementation will be considered successful if it meets the following criteria:

1. **Functional Completeness**
   - All five key requirements are fully implemented
   - Sequence operations produce biologically valid results matching reference implementations
   - Taxonomic queries correctly group and filter by evolutionary relationships
   - Property calculations match established biochemical references
   - Coordinate mappings correctly translate between assembly versions

2. **Biological Accuracy**
   - All operations maintain biological correctness
   - Sequence operations respect biological constraints (reading frames, codon boundaries)
   - Taxonomic operations reflect accepted classification systems
   - Chemical properties align with established biochemical principles
   - Results are scientifically defensible and publishable

3. **Research Productivity**
   - Reduces analysis time for common bioinformatics workflows by >50%
   - Successfully integrates heterogeneous biological data types
   - Enables queries that would be difficult or impossible with general-purpose database tools
   - Supports reproducible research through provenance tracking

4. **Performance and Scalability**
   - Handles realistic genomic dataset sizes (up to whole genomes)
   - Processes queries efficiently enough for interactive research
   - Scales appropriately with sequence length and dataset size
   - Optimizes resource usage for memory-intensive operations