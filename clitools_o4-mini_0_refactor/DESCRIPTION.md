# clitools

## Purpose and Motivation
clitools provides a thin abstraction over Python’s built-in `argparse`, `configparser`, and `logging` to accelerate CLI application development. It aims to reduce boilerplate for commands, subcommands, configuration files, and standardized logging/output. The library is great for devops scripts, automation utilities, or any command-line tool where consistency and rapid iteration matter.

## Core Functionality
- Declarative command and subcommand registration (name, help, args)
- Auto‐generation of `argparse` parser with typed arguments, choices, defaults
- Configuration file loading (INI, JSON) merged with CLI overrides
- Structured logging setup (console, file) with level control
- Built-in “help”, “version”, and common flags
- Plugin hook support for extending commands or integrating custom log handlers
