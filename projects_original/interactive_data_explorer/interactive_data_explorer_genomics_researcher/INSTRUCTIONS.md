# Genomic Sequence Explorer

## Overview
A specialized terminal-based data exploration framework designed for genomics researchers who need to analyze complex genetic datasets, visualize sequence alignments, identify statistically significant variations, and explore relationships between genetic patterns and phenotypic traits. This tool enables comprehensive genomic analysis without requiring graphical interfaces or specialized hardware.

## Persona Description
Dr. Mbeki analyzes genomic sequencing data to identify patterns associated with specific traits or conditions. She needs to explore complex genetic datasets, visualize sequence alignments, and identify statistically significant variations.

## Key Requirements
1. **Sequence alignment visualization** - Create clear, terminal-based visualizations of DNA/RNA sequence alignments with mutation highlighting and annotation. This is critical for researchers to identify conserved regions, mutations, and structural variations across multiple sequences to understand genetic diversity and evolution.

2. **Phylogenetic tree generation** - Build and visualize evolutionary relationships between genetic sequences to reveal taxonomic groupings and evolutionary history. Researchers need to understand how different sequences relate to each other over evolutionary time and identify clades that share common genetic characteristics.

3. **Gene expression heatmaps** - Generate visual representations correlating gene activation patterns across different experimental conditions, tissues, or time points. This allows researchers to identify genes that are co-regulated and discover expression patterns associated with specific biological states or disease conditions.

4. **Variant significance scoring** - Calculate and visualize the statistical significance of genetic variants using multiple probabilistic models. This helps researchers prioritize which genetic variations are most likely to have functional importance or disease associations from among thousands of possibilities.

5. **Pathway analysis** - Map genetic variations to functional biological processes and visualize the interconnections between affected genes. This is essential for understanding how genetic changes may impact biological systems and translate to observable traits or disease mechanisms.

## Technical Requirements
- **Testability Requirements**:
  - Alignment algorithms must be verified against established bioinformatics tools (BLAST, Clustal)
  - Phylogenetic tree construction must produce consistent results with known sequence relationships
  - Statistical methods for variant significance must be validated with published benchmarks
  - Gene expression analysis must match results from standard tools (DESeq2, edgeR)
  - All visualizations must be testable for content and format accuracy

- **Performance Expectations**:
  - Must handle sequence datasets of up to 1GB in total size
  - Alignment of 100 sequences (1000bp each) should complete within 30 seconds
  - Phylogenetic tree generation for 500 sequences should complete within 2 minutes
  - Gene expression analysis for 20,000 genes across 50 samples within 1 minute
  - Memory usage must stay below 4GB during all operations

- **Integration Points**:
  - Support for standard bioinformatics file formats (FASTA, FASTQ, SAM/BAM, VCF, BED, GTF)
  - Import functionality for reference genomes and annotation databases
  - Export to common analysis formats for use in other specialized tools
  - Integration with biological pathway databases (KEGG, GO, Reactome)

- **Key Constraints**:
  - All visualizations must be terminal-compatible with no external GUI dependencies
  - Analyses must run on standard computational hardware without specialized accelerators
  - Must maintain data provenance for scientific reproducibility
  - Should minimize memory footprint to handle larger genomic datasets
  - Must handle incomplete or noisy data common in genomic research

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The Genomic Sequence Explorer must provide a comprehensive toolkit for genomic data analysis:

1. **Sequence Analysis and Alignment**:
   - Import and parse various sequence file formats (FASTA, FASTQ, etc.)
   - Implement efficient pairwise and multiple sequence alignment algorithms
   - Calculate sequence similarity metrics and distance matrices
   - Identify conserved regions, SNPs, insertions, deletions, and other variations
   - Visualize sequence alignments with highlighting for important features

2. **Evolutionary Analysis**:
   - Generate distance matrices from sequence alignments
   - Implement multiple phylogenetic tree construction algorithms (Neighbor-Joining, Maximum Likelihood)
   - Calculate evolutionary distances and branch support values
   - Visualize phylogenetic trees in terminal-friendly formats
   - Identify monophyletic groups and evolutionary clades

3. **Expression Analysis**:
   - Process gene expression data from various experiment types
   - Normalize expression values using appropriate statistical methods
   - Identify differentially expressed genes across conditions
   - Perform clustering to find co-expressed gene groups
   - Generate heatmaps and other visualizations of expression patterns

4. **Variant Analysis**:
   - Parse variant call formats (VCF) and extract relevant information
   - Calculate allele frequencies and population genetics metrics
   - Implement multiple scoring algorithms to assess variant significance
   - Annotate variants with functional predictions and existing knowledge
   - Prioritize variants based on combined evidence from multiple models

5. **Biological Pathway Integration**:
   - Map genes and variants to known biological pathways
   - Calculate enrichment statistics for gene sets
   - Visualize pathway involvement of gene lists
   - Perform Gene Ontology (GO) term enrichment analysis
   - Identify biological processes affected by gene expression changes or variants

## Testing Requirements
- **Key Functionalities to Verify**:
  - Sequence alignment correctly identifies similarities and differences between sequences
  - Phylogenetic trees accurately represent evolutionary relationships for test sequences
  - Gene expression analysis correctly identifies differentially expressed genes
  - Variant scoring accurately prioritizes known pathogenic variants
  - Pathway analysis correctly identifies enriched biological processes

- **Critical User Scenarios**:
  - Aligning a set of homologous gene sequences from different species
  - Constructing a phylogenetic tree from a set of viral strains
  - Identifying differentially expressed genes between disease and control samples
  - Prioritizing genetic variants from a whole-exome sequencing experiment
  - Mapping a set of genes to biological pathways and identifying enriched processes

- **Performance Benchmarks**:
  - Align 100 sequences (1000bp) within 30 seconds
  - Generate phylogenetic tree for 500 sequences within 2 minutes
  - Process expression data for 20,000 genes x 50 samples within 1 minute
  - Score and prioritize 100,000 variants within 5 minutes
  - Memory usage below 4GB during all operations

- **Edge Cases and Error Conditions**:
  - Handling extremely divergent sequences in alignments
  - Managing phylogenetic analysis with incomplete or ambiguous data
  - Processing expression data with batch effects or missing values
  - Dealing with variants in repetitive or complex genomic regions
  - Handling inconsistent or outdated pathway annotations

- **Required Test Coverage Metrics**:
  - 90% code coverage for all core functionality
  - 100% coverage for critical statistical calculations
  - All public APIs must have integration tests
  - All visualization functions must be tested for output format correctness
  - All file parsers must be tested with valid and invalid file formats

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
A successful implementation of the Genomic Sequence Explorer will demonstrate:

1. Accurate sequence alignment visualization with proper identification of variations
2. Phylogenetic tree generation that correctly represents evolutionary relationships
3. Gene expression analysis that identifies biologically meaningful patterns
4. Variant significance scoring that prioritizes known functional variants
5. Pathway analysis that correctly maps genes to biological processes

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

To set up the development environment, use:
```
uv venv
source .venv/bin/activate
uv pip install -e .
```

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```