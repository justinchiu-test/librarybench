# PyPatternGuard - Research-Oriented Pattern Detection Engine

## Overview
A specialized code pattern detection system designed for computer science researchers studying software evolution. The system provides advanced pattern analysis capabilities for empirical studies on code quality trends, supporting academic research with customizable pattern definitions and statistical analysis.

## Persona Description
A computer science researcher studying software evolution who uses pattern detection for empirical studies. They need advanced pattern analysis capabilities for academic research on code quality trends.

## Key Requirements

1. **Custom pattern definition DSL for research-specific patterns**: Critical for enabling researchers to define novel patterns for their studies without modifying the core engine, supporting exploratory research and hypothesis testing.

2. **Statistical analysis of pattern distribution across repositories**: Essential for empirical research by providing quantitative data on pattern prevalence, correlation analysis, and distribution metrics across different codebases and domains.

3. **Pattern evolution tracking with git history integration**: Enables longitudinal studies by tracking how patterns emerge, evolve, and disappear over time, providing insights into software evolution and maintenance practices.

4. **Academic paper citation generation for detected patterns**: Facilitates research publication by automatically linking detected patterns to relevant academic literature, supporting proper attribution and literature review processes.

5. **Batch analysis API for large-scale empirical studies**: Provides programmatic access for analyzing thousands of repositories, enabling large-scale empirical studies and supporting reproducible research methodologies.

## Technical Requirements

### Testability Requirements
- DSL parser must handle syntax errors gracefully with clear error messages
- Statistical calculations must be verifiable against known datasets
- Git integration must work with various repository structures
- All research metrics must be reproducible and deterministic

### Performance Expectations
- Batch analysis of 10,000 repositories within 24 hours
- DSL pattern compilation under 100ms
- Statistical analysis scaling linearly with data size
- Support for parallel processing of independent repositories

### Integration Points
- AST analysis using Python's `ast` module
- Git integration using subprocess for history analysis
- Statistical computations using Python's statistics module
- JSON/CSV export for research tools (R, SPSS, etc.)

### Key Constraints
- Must work with Python 3.8+ codebases
- No external dependencies beyond Python standard library
- Must maintain research data integrity and reproducibility
- Analysis must handle incomplete or corrupted repositories

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system must provide:

1. **Pattern Definition DSL**: A domain-specific language for defining custom patterns with support for AST matching, semantic constraints, context conditions, and pattern composition, including a parser and validator for the DSL.

2. **Statistical Analyzer**: Computes distribution metrics (mean, median, mode, standard deviation) for pattern occurrences, performs correlation analysis between patterns, generates frequency histograms, and calculates statistical significance tests.

3. **Evolution Tracker**: Integrates with git to track pattern changes over commits, identifies pattern introduction and removal points, measures pattern lifetime and modification frequency, and generates evolution timelines and trend graphs.

4. **Citation Generator**: Maps detected patterns to academic paper references, generates bibliography entries in various formats (BibTeX, APA, MLA), links patterns to theoretical foundations, and maintains a pattern-to-literature database.

5. **Batch Analysis Engine**: Provides API for large-scale repository analysis, supports configurable analysis parameters, implements result aggregation and summarization, handles failures gracefully with partial results, and generates reproducible analysis reports.

## Testing Requirements

### Key Functionalities to Verify
- DSL correctly parses and validates pattern definitions
- Statistical calculations match expected values
- Git history analysis accurately tracks pattern evolution
- Citation generation produces valid bibliography formats
- Batch processing handles various failure scenarios

### Critical User Scenarios
- Defining custom patterns for a software metrics study
- Analyzing pattern distribution across 1000 GitHub repositories
- Tracking design pattern evolution in a 10-year project
- Generating citations for a systematic literature review
- Running reproducible analysis for journal publication

### Performance Benchmarks
- DSL pattern matching: < 50ms per file
- Statistical analysis: < 1 second per 1000 data points
- Git history processing: < 10 seconds per 100 commits
- Citation lookup: < 100ms per pattern
- Batch analysis: > 100 repositories per hour

### Edge Cases and Error Conditions
- Malformed DSL pattern definitions
- Repositories with complex merge histories
- Statistical analysis with insufficient data
- Missing or incorrect citation data
- Network failures during batch processing

### Required Test Coverage Metrics
- Line coverage: minimum 95%
- Branch coverage: minimum 90%
- DSL parser must have 100% error case coverage
- All statistical functions must be validated
- Integration tests for complete research workflows

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

The implementation successfully meets this persona's needs when:

1. **Research Flexibility**: The DSL supports defining patterns for at least 90% of common software engineering research scenarios.

2. **Statistical Rigor**: All statistical analyses meet academic standards for empirical software engineering research.

3. **Reproducibility**: Analysis results are 100% reproducible given the same inputs and configuration.

4. **Scalability**: The system successfully analyzes datasets comparable to those in top-tier software engineering venues.

5. **Academic Integration**: Generated citations and reports are directly usable in academic publications without manual editing.

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup

From within the project directory, set up the virtual environment:
```
uv venv
source .venv/bin/activate
uv pip install -e .
```

Run tests with pytest-json-report:
```
uv pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```