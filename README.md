# LibraryBench

Tools for synthesizing repositories that must be combined.

## Overview

LibraryBench provides a pipeline for:

1. Synthesizing tasks and variations
2. Generating tests for those tasks
3. Generating solutions for those tasks

## Installation

```bash
# Install the package and dependencies using uv
uv sync

# Or install in development mode
uv pip install -e .

# Install development dependencies
uv pip install -e ".[dev]"
```

## Environment Setup

LibraryBench requires the following environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key (for OpenAI models)
- `ANTHROPIC_API_KEY`: Your Anthropic API key (for Claude models)

