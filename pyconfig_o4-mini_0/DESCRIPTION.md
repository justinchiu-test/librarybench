# PyConfig

## Purpose and Motivation
PyConfig provides a unified, layered configuration management system for Python applications. It solves the common pain of juggling multiple config file formats, environment variables, and defaults by offering a consistent API to load, merge, validate, and access settings. This brings clarity to config handling in scripts, web services, or CLI tools without needing third-party packages.

## Core Functionality
- Load and parse configuration from INI, JSON, or custom “YAML-lite” text files using only the standard library.
- Merge multiple configuration sources (defaults, files, env vars) with controllable precedence rules.
- Provide typed getters with built-in casting, default values, and on-access validation hooks.
- Support dynamic variable interpolation (e.g., `${HOME}/data`, environment lookups).
- Export or serialize the resulting config to various formats (INI, JSON).
- Plugin hooks or callback registration for post-load transformations or additional validation.

