# CLAUDE.md - Guide for Refactorbench Project

## Build & Run Commands
- Run main script: `python hello.py`
- Install dependencies: `uv pip install`
- Run tests: `pytest`
- Run single test: `pytest path/to/test.py::test_function_name`
- Format code: `uv run ruff format`
- Lint code: `uv run ruff check .`
- Type check: `uv run pyright`

## Code Style Guidelines
- **Formatting**: Use Ruff for code formatting
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
- **Pydantic**: Use Pydantic BaseModel when possible. Minimize complexity
