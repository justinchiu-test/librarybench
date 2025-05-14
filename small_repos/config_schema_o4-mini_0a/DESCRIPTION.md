# ConfigSchema

## Purpose and Motivation
ConfigSchema provides a thin abstraction on top of Python’s `configparser` (and native file I/O) to define, load, and validate configuration files (INI, JSON or simple key/value). Many applications require structured configuration with type-checking, default values, and error reporting. This library unifies those concerns into a small, testable package without pulling in external dependencies.

## Core Functionality
- Define a schema with sections, keys, types (int, float, bool, list, etc.) and default values  
- Load and parse INI or JSON config files into a Python dictionary  
- Validate loaded data against the schema, reporting missing keys or type mismatches  
- Merge multiple config sources (e.g., base config + environment overrides)  
- Provide programmatic API and decorator-based `@with_config` injection for functions  
- Extension hooks for custom type converters or advanced cross-field validation  

