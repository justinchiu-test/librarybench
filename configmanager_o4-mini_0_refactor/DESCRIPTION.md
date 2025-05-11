# ConfigManager

## Purpose and Motivation
ConfigManager offers a unified API to load, merge, and monitor configuration from multiple sources—JSON, INI, and environment variables. It applies layered precedence (defaults < file < env vars), enforces typed getters, and can hot-reload on file changes. This centralizes configuration logic, validation, and change notifications for any Python application, without external packages.

## Core Functionality
- Load and merge settings from JSON files, INI (via `configparser`), and `os.environ`  
- Typed accessors (`get_int`, `get_bool`, `get_list`, etc.) with default values and validation  
- Precedence rules and dynamic override of specific keys at runtime  
- File‐watcher that hot‐reloads on change events (using `threading` and `os.stat`)  
- Subscription callbacks so parts of your code react to config updates  
- Export merged configuration back to disk or environment  

