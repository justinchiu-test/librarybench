# Unified Config Schema Manager - Refactoring Plan

This document outlines the plan for refactoring multiple config manager implementations into a single, unified library.

## Key Requirements

Based on the existing implementations and test cases, the unified library should support:

1. Loading configs from multiple file formats (JSON, YAML, INI)
2. Environment variable expansion
3. Type validation
4. JSON schema export
5. Config caching
6. Get/set operations with dot notation
7. Prompting for missing values
8. With_config decorator for function parameter binding
9. Thread safety

## Proposed Architecture

The unified library will be structured with a modular design, consisting of:

```
unified/
├── __init__.py         # Exports primary APIs
├── setup.py            # Package setup
├── configschema/
│   ├── __init__.py     # Main module exports
│   ├── config.py       # Core ConfigManager class
│   ├── error.py        # ValidationError and other exceptions
│   ├── decorator.py    # With_config decorator
│   ├── schema.py       # JSON schema generation
│   ├── validation.py   # Type validation functions
│   ├── loader.py       # Config file loaders for different formats
│   ├── cache.py        # Caching mechanism
│   ├── env.py          # Environment variable expansion
│   └── utils.py        # Utility functions
│
└── tests/              # Test files (already exists)
```

## Feature Implementation Plan

### Core Components

1. **ValidationError & Exceptions**
   - Unified error class with comprehensive details
   - Support for line numbers, file paths, sections, keys
   - Suggestions for fixing issues
   
2. **Config Loading**
   - Support for JSON, YAML, and INI formats
   - Extensible for additional formats
   - File-based caching with mtime checking
   - Graceful fallback if optional modules not installed (e.g., PyYAML)

3. **Environment Variable Expansion**
   - Support for both `$VAR` and `${VAR}` syntax
   - Recursive expansion in nested dictionaries and lists

4. **Type Validation**
   - Python type checking
   - JSON schema validation
   - Custom types (IP addresses, ports, etc.)
   - Support for user-defined validators

5. **JSON Schema Export**
   - Automatic schema generation from config values
   - Schema output compatible with standard tools

6. **ConfigManager Class**
   - Thread-safe implementation
   - Dot notation for paths
   - Get with default values
   - Nested dictionary creation on set
   - Config serialization/deserialization
   - Support for various config file formats

7. **With_config Decorator**
   - Function parameter auto-binding
   - Support for default values
   - Automatic type checking
   - Support for classes and instance methods

## Integration with Tests

The existing test suite will be used to verify that all functionality works as expected across the various use cases. Each test file focuses on specific functionality:

- test_backend_developer_*.py: Basic functionality
- test_data_scientist_*.py: Type validation and with_config
- test_devops_engineer_*.py: Advanced features
- test_qa_engineer_*.py: Schema integration
- test_sysadmin_*.py: System administration features

## Implementation Notes

- The implementation will prioritize backward compatibility with existing test cases
- Thread safety will be ensured for all shared resources
- Performance optimizations will be applied where possible
- The design will follow Python best practices and idioms
- Documentation will be provided for all public interfaces