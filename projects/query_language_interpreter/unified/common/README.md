# Common Package

This package contains functionality shared across all the persona-specific packages.
It provides a unified framework for query language interpreters with extensibility
points for domain-specific functionality.

## Structure:

- `core/`: Core data structures and algorithms
  - `query.py`: Base query models and interfaces
  - `interpreter.py`: Core interpreter functionality
  - `execution.py`: Execution pipeline and context
  - `result.py`: Result models and formatters

- `pattern/`: Pattern detection framework
  - `detector.py`: Base pattern detection
  - `matcher.py`: Pattern matching utilities
  - `confidence.py`: Confidence scoring

- `logging/`: Logging utilities
  - `base.py`: Base logging functionality
  - `audit.py`: Audit logging utilities
  - `formatter.py`: Log formatting utilities

- `policy/`: Policy enforcement framework
  - `engine.py`: Policy enforcement engine
  - `rule.py`: Rule representation and validation
  - `context.py`: Execution context for policies

- `models/`: Common data models
  - `base.py`: Base data models
  - `enums.py`: Common enumerations

- `utils/`: Utility functions
  - `concurrency.py`: Parallelization utilities
  - `validation.py`: Input validation
  - `text.py`: Text processing utilities
