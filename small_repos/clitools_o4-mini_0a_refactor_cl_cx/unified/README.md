# CLI Tools Unified

This package provides a unified interface for various CLI tools targeting different personas:

## Personas

1. **Backend Developer** - CLI tools for backend development workflows
2. **Data Scientist** - CLI tools for data pipeline management 
3. **Ops Engineer** - CLI tools for operations and infrastructure
4. **Translator** - Translation and localization utilities
5. **Localization Manager** - Features for managing localizations

## Installation

```bash
pip install .
```

## Usage

Each persona has its own subpackage with specific tools:

```python
# Backend Developer example
from backend_dev.microcli.config_parser import parse_config_files

# Data Scientist example
from data_scientist.datapipeline_cli.commands import main

# Ops Engineer example
from ops_engineer.cli_toolkit.commands import CLI
```

## Development

```bash
# Run tests
pytest
```