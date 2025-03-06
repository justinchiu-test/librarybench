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
# Install the package in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

## Environment Setup

LibraryBench requires the following environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key (for OpenAI models)
- `ANTHROPIC_API_KEY`: Your Anthropic API key (for Claude models)
- `CYBER_URL`: URL for the execution API endpoint

## Usage

### Generating Solutions

```python
import asyncio
from librarybench.generation import generate_solutions

async def main():
    await generate_solutions(
        model_type="claude",  # or "openai"
        model_name="claude-3-haiku-20240307",  # or specific OpenAI model
        sample_size=5,  # Number of examples to process
        concurrency=5,  # Number of concurrent requests
        problem_types=["search", "datastructure", "chess"],
        output_dir="data"
    )

if __name__ == "__main__":
    asyncio.run(main())
```

### Executing and Evaluating Solutions

```python
from librarybench.execution import evaluate_solutions

# Evaluate solutions
results = evaluate_solutions(
    solution_file="data/claude_search_solutions.json",
    output_dir="data"
)
```

### Getting Model Feedback

```python
from librarybench.feedback import get_model_feedback

# Get feedback for a specific model solution
feedback, results = get_model_feedback(
    solution_file="data/claude_search_solutions.json",
    problem_id=0,  # Optional: specific problem ID
    model_name="claude"  # or "o3_mini"
)
print(feedback)
```

### Iteratively Improving Solutions

```python
import asyncio
from librarybench.improvement import batch_improve_solutions

async def main():
    # Improve all solutions in a file
    results = await batch_improve_solutions(
        solution_file="data/claude_search_solutions.json",
        cyber_url="YOUR_CYBER_URL",
        model_name="claude-3-haiku-20240307",
        max_iterations=3,
        target_passed_ratio=1.0,
        output_file="data/improved_claude_search_solutions.json",
        concurrent_problems=3
    )

if __name__ == "__main__":
    asyncio.run(main())
```

### Comparing Improvements

```python
from librarybench.analysis import compare_solutions, print_comparison_results

# Compare original and improved solutions
results = compare_solutions(
    original_file="data/claude_search_solutions.json",
    improved_file="data/improved_claude_search_solutions.json",
    model_key="claude_solution"
)

# Print human-readable comparison
print_comparison_results(results)
```

## Project Structure

```
librarybench/
├── src/
│   └── librarybench/
│       ├── generation/        # Solution generation
│       ├── execution/         # Solution testing
│       ├── feedback/          # Feedback generation
│       ├── improvement/       # Iterative improvement
│       ├── analysis/          # Comparison tools
│       └── utils/             # Shared utilities
├── tests/                     # Test suite
├── examples/                  # Example scripts
└── data/                      # Solution data storage
```

## Development

Run tests:
```bash
pytest
```

Format code:
```bash
ruff format
```

Run linting:
```bash
ruff check
```

Type checking:
```bash
pyright
```

## License

MIT License