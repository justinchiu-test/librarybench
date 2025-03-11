# LibraryBench

A framework for evaluating and improving AI model solutions to coding problems.

## Overview

LibraryBench provides a pipeline for:

1. Generating solutions to programming problems using language models
2. Executing and evaluating those solutions against test cases
3. Providing detailed feedback on solution performance
4. Iteratively improving solutions through model feedback
5. Analyzing and comparing solution improvements

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
- `CYBER_URL`: URL for the execution API endpoint

## Usage

The main workflow is in `examples/workflow.py`. For individual components:

```python
# Generate solutions
await solution_process(
    model_type="openai", model_name="o3-mini", 
    problem_types=["chess"], max_iterations=1
)

# Evaluate solutions
await evaluate_solutions_async(solution_file="path/to/solutions.json")

# Improve solutions
await solution_process(
    model_type="openai", model_name="o3-mini",
    input_solution_file="path/to/solutions.json", max_iterations=2
)

# Compare solutions
await compare_solutions(
    original_file="path/to/solutions.json",
    improved_file="path/to/solutions_improved.json"
)
```

## Main Workflow Example

The main entrypoint is `examples/workflow.py`:

```bash
uv run python examples/workflow.py \
    --model-type openai \
    --model-name o3-mini \
    --sample-size 5 \
    --problem-types chess \
    --max-iterations 2
```

## Project Structure

```
librarybench/
├── CLAUDE.md                 # Command references and coding standards
├── README.md                 # Project documentation
├── pyproject.toml            # Project configuration
├── src/
│   └── librarybench/         # Core package
│       ├── __init__.py       
│       ├── models/           # LLM clients
│       │   ├── __init__.py
│       │   ├── llm_client.py       # Base client class
│       │   ├── claude_client.py    # Anthropic client
│       │   └── openai_client.py    # OpenAI client
│       ├── analysis/         # Analysis tools
│       │   ├── __init__.py
│       │   └── model_comparison.py # Compare solutions
│       ├── feedback/         # Feedback generation
│       │   ├── __init__.py
│       │   └── feedback_generator.py
│       ├── execution.py      # Solution execution
│       ├── llm.py            # LLM interface
│       ├── processor.py      # Main pipeline
│       ├── prompting.py      # Prompt templates
│       ├── solution.py       # Solution data structures
│       ├── types.py          # Type definitions
│       └── utils.py          # Utility functions
├── examples/                 # Example workflows
│   └── workflow.py           # Main workflow script
├── scripts/                  # Utility scripts
│   └── examine_taco.py       # TACO evaluation tool
├── tests/                    # Test suite
│   ├── test_execution.py     # Execution tests
│   └── test_generation.py    # Generation tests
└── data/                     # Solution data storage
```

## Development

Run tests:
```bash
uv run pytest
```

Run a specific test:
```bash
uv run pytest path/to/test.py::test_function_name
```

Format code:
```bash
uv run ruff format
```

Run linting:
```bash
uv run ruff check .
```

Type checking:
```bash
uv run pyright
```

## License

MIT License