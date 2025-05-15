# Unified Configuration Manager Architecture

This document outlines the architecture for a unified configuration management system that combines the functionality of multiple persona-specific implementations (backend_developer, data_scientist, devops_engineer, qa_engineer, sysadmin) into a single cohesive library.

## Project Goals

1. Create a unified configuration management system that supports all features from existing implementations
2. Provide a consistent API while maintaining compatibility with existing tests
3. Eliminate code duplication and improve maintainability
4. Support a wide range of configuration formats and features
5. Implement proper error handling and validation

## Core Components

### 1. File System and Format Handling

- **ConfigLoader**: Abstract base class for different format loaders
  - `JSONLoader`: Handles JSON file loading
  - `INILoader`: Handles INI file loading
  - `YAMLLoader`: Handles YAML file loading (with graceful fallback)
  - `TOMLLoader`: Handles TOML file loading (with graceful fallback)

- **FormatDetector**: Utility to detect file format based on extension or content

### 2. Configuration Management

- **ConfigManager**: Central class for managing configuration
  - Static/instance methods for different usage patterns
  - Getter/setter methods with dot notation support
  - Serialization methods
  - Schema generation and validation methods

- **ConfigCache**: Manages config file caching with timestamp validation
  - Thread-safe implementation
  - Support for cache invalidation

### 3. Config Processing

- **EnvironmentExpander**: Handles environment variable expansion
  - Support for both $VAR and ${VAR} syntax
  - Recursive expansion in nested structures

- **TypeConverter**: Handles type conversion and inference
  - Convert string values to appropriate types
  - Support for basic and complex types including arrays

### 4. Validation

- **SchemaGenerator**: Generates JSON schema from configuration
  - Type inference for nested structures
  - Default value handling

- **ConfigValidator**: Validates config against schema
  - Type validation
  - Custom validators for special types (IP, port, etc.)
  - Detailed error message generation

### 5. User Interaction

- **ConfigPrompt**: Handles prompting for missing values
  - Interactive console input
  - Environment-aware behavior (skip prompts in CI)

### 6. Decorators and Utilities

- **Decorators**: Function decorators for configuration injection
  - Parameter mapping between config and function arguments
  - Type conversion based on function annotations

- **ErrorHandling**: Specialized error classes with detailed information
  - Validation errors with context
  - File/line information for errors
  - Suggested corrections

## File Structure

```
unified/
├── src/
│   ├── __init__.py                 # Package exports
│   ├── loaders/
│   │   ├── __init__.py             # Loader registry and factory
│   │   ├── base.py                 # Abstract loader interface
│   │   ├── json_loader.py          # JSON file loader
│   │   ├── ini_loader.py           # INI file loader
│   │   ├── yaml_loader.py          # YAML file loader
│   │   └── toml_loader.py          # TOML file loader
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config_manager.py       # Core ConfigManager class
│   │   ├── cache.py                # Caching implementation
│   │   └── env_expander.py         # Environment variable expansion
│   ├── validation/
│   │   ├── __init__.py
│   │   ├── schema_generator.py     # Schema generation utilities
│   │   ├── validators.py           # Validation functions
│   │   └── errors.py               # Error classes
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── type_converter.py       # Type conversion utilities
│   │   ├── path_utils.py           # Path and dot notation utilities
│   │   └── decorators.py           # Function decorators
│   ├── interactive/
│   │   ├── __init__.py
│   │   └── prompt.py               # User interaction for missing values
│   │
│   │   # Persona-specific compatibility modules
│   ├── backend_developer/
│   │   ├── __init__.py
│   │   └── configmanager.py        # Adapter for backend_developer persona
│   ├── data_scientist/
│   │   ├── __init__.py
│   │   └── config_manager.py       # Adapter for data_scientist persona
│   ├── devops_engineer/
│   │   ├── __init__.py
│   │   └── config_manager.py       # Adapter for devops_engineer persona
│   ├── qa_engineer/
│   │   ├── __init__.py
│   │   └── config_manager.py       # Adapter for qa_engineer persona
│   └── sysadmin/
│       ├── __init__.py
│       └── configtool.py           # Adapter for sysadmin persona
├── tests/
│   └── (Existing test files unchanged)
```

## Implementation Strategy

1. **Core First Approach**:
   - Implement the core functionality in a modular way
   - Focus on file loading, data structures, and core operations

2. **Incremental Testing**:
   - Implement features incrementally, testing against existing tests
   - Ensure each feature works before moving on to the next

3. **Adapter Pattern**:
   - Use adapter modules to provide compatibility with existing imports
   - Each persona-specific module adapts the core API to its specific interface

4. **Dependency Management**:
   - Optional dependencies handled gracefully (YAML, TOML)
   - Consistent fallback behavior when libraries are missing

## Key Design Decisions

1. **Single Core with Multiple Facades**:
   - Core functionality implemented once
   - Persona-specific modules are thin adapters to the core

2. **Type Handling Strategy**:
   - Type inference from values
   - Type validation during set operations
   - Special handling for collections and complex types

3. **Error Handling Philosophy**:
   - Detailed error messages with context
   - Gradual failure - continue where possible
   - Suggestions for corrections when applicable

4. **Caching Strategy**:
   - Thread-safe cache implementation
   - Timestamp validation for file changes
   - Cache invalidation on set operations

## Dependencies

- Core functionality requires only Python standard library
- Optional dependencies:
  - PyYAML for YAML support
  - toml for TOML support
  - jsonschema for advanced schema validation

## Migration Path

For users of the existing persona-specific libraries, no changes are required as the adapter modules maintain the same interfaces. For new users, the unified core API provides a more consistent and feature-rich experience.