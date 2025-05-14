# ConfigKit

## Purpose and Motivation
ConfigKit addresses the need for a unified, hierarchical configuration system in Python applications without relying on external dependencies. It simplifies loading, merging, and validating settings from multiple sources (JSON files, environment variables, default dicts). By offering pluggable validation schemas and override mechanisms, ConfigKit helps manage complex configurations in CLI tools, web services, or automation scripts.

## Core Functionality
- Load configuration from JSON files, environment variables, and Python dicts  
- Merge multiple configuration layers according to a defined precedence order  
- Validate configuration values against user-provided schemas or simple type checks  
- Support for variable interpolation and default fallbacks within the config tree  
- Export or serialize the final merged/validated config back to JSON or INI-style text  
- Hook system for custom loaders (e.g., YAML, database) and validators  

