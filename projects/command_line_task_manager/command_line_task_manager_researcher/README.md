# ResearchTrack

A specialized command-line task management system designed for academic researchers conducting computational research. The system enables meticulous tracking of research tasks with detailed notes, associates analytical steps with specific research questions and datasets, and provides comprehensive documentation capabilities to ensure research reproducibility.

## Key Features

1. **Bibliographic Reference Linking**: Associate tasks with academic sources, citations, and literature.
2. **Dataset Versioning Integration**: Track which data version was used for each analysis task.
3. **Computational Environment Snapshots**: Document the complete system state for reproducibility.
4. **Academic Markdown Export**: Generate properly formatted methods sections for academic publications.
5. **Experiment Tracking**: Track experimental parameters, variations, and result logging.

## Installation

```bash
# Create and activate a virtual environment
uv venv
source .venv/bin/activate

# Install the package in development mode
uv pip install -e .
```

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-json-report

# Run tests with coverage report
pytest --json-report --json-report-file=pytest_results.json
```

## Components

The package is organized into the following modules:

- `task_management`: Core module for research task CRUD operations
- `bibliography`: Bibliographic reference management and citation formatting
- `dataset_versioning`: Dataset version tracking and provenance
- `environment`: Computational environment capture and verification
- `export`: Academic markdown export functionality
- `experiment`: Experiment tracking and result management