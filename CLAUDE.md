# CLAUDE.md - Guide for Refactorbench Project

## Build & Run Commands
- Run main script: `python hello.py`
- Install dependencies: `pip install -e .`
- Run tests: `pytest`
- Run single test: `pytest path/to/test.py::test_function_name`
- Format code: `black .`
- Lint code: `ruff check .`
- Type check: `mypy .`

## Code Style Guidelines
- **Formatting**: Use Black for code formatting
- **Linting**: Use Ruff for linting
- **Type Hints**: Include type hints for all function parameters and return values
- **Imports**: Group imports in order: standard library, third-party, local
- **Naming**: 
  - snake_case for functions and variables
  - CamelCase for classes
  - UPPER_CASE for constants
- **Error Handling**: Use explicit try/except blocks with specific exceptions
- **Documentation**: Use docstrings for all functions, classes, and modules
- **Line Length**: Maximum 88 characters per line