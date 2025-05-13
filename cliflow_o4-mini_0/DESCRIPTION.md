# CLIFlow

## Purpose and Motivation
CLIFlow streamlines the creation of interactive command-line applications with subcommands, prompts, and workflow definitions. It abstracts common patterns—argument parsing, validation, nested commands, progress feedback—into a coherent framework. Perfect for data science tools, DevOps scripts, or any multi-step CLI without pulling in click or argparse extensions.

## Core Functionality
- Declare commands and subcommands with parameter specifications (types, defaults, help text).
- Automatic help text, usage generation, and error handling.
- Built-in interactive prompts (yes/no, multi-choice, free text) that can be chained into flows.
- Pipeline support for feeding one command’s output into another.
- Progress bar or spinner utilities based on console width detection.
- Hook points for custom renderers (e.g., color output vs. plain text).

