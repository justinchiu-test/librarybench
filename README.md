# LibraryBench

Tools for synthesizing repositories that must be combined.

## Overview

LibraryBench provides a pipeline for:

1. Synthesizing tasks and variations
2. Generating tests for those tasks
3. Generating solutions for those tasks

## Installation
1. Install claude code and codex

## Usage
```
bash scripts/synth_ideas.sh
bash scripts/synth_personas.sh
bash scripts/synth_instructions.sh
bash scripts/synth_code_tests.sh
```

## Environment Setup

LibraryBench requires the following environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key (for OpenAI models)
- `ANTHROPIC_API_KEY`: Your Anthropic API key (for Claude models)

