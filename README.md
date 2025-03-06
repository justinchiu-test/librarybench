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

### Generating Solutions

```python
import asyncio
from librarybench.generation.solution_generator import generate_solutions

async def main():
    await generate_solutions(
        model_type="claude",  # or "openai"
        model_name="claude-3-sonnet-20240229",  # or specific OpenAI model
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
from librarybench.execution.executor import evaluate_solutions

# Evaluate solutions
results = evaluate_solutions(
    solution_file="data/claude_3_sonnet_20240229_search_solutions.json",
    output_dir="data"
)
```

### Getting Model Feedback

```python
from librarybench.feedback.feedback_generator import get_model_feedback

# Get feedback for a specific model solution
feedback = get_model_feedback(
    solution_file="data/claude_3_sonnet_20240229_search_solutions.json",
    execution_results_file="data/claude_3_sonnet_20240229_search_solutions_execution_results.json",
    problem_id=0,  # Optional: specific problem ID
    model_name="claude"  # or "o3_mini"
)
print(feedback)
```

### Iteratively Improving Solutions

```python
import asyncio
from librarybench.improvement.iterative_repair import batch_improve_solutions

async def main():
    # Improve all solutions in a file
    results = await batch_improve_solutions(
        solution_file="data/claude_3_sonnet_20240229_search_solutions.json",
        execution_results_file="data/claude_3_sonnet_20240229_search_solutions_execution_results.json",
        model_name="claude-3-sonnet-20240229",
        max_iterations=3,
        target_passed_ratio=1.0,
        output_file="data/improved_claude_3_sonnet_20240229_search_solutions.json",
        concurrent_problems=3
    )

if __name__ == "__main__":
    asyncio.run(main())
```

### Comparing Improvements

```python
from librarybench.analysis.model_comparison import compare_solutions, print_comparison_results

# Compare original and improved solutions
results = compare_solutions(
    original_file="data/claude_3_sonnet_20240229_search_solutions.json",
    improved_file="data/improved_claude_3_sonnet_20240229_search_solutions.json",
    model_key="claude_3_sonnet_20240229_solution"
)

# Print human-readable comparison
print_comparison_results(results)
```

### Complete Workflow Example

The library includes a complete example workflow that demonstrates the entire pipeline:

```python
import asyncio
from librarybench.examples.example_workflow import run_workflow

async def main():
    await run_workflow(
        model_type="claude",
        model_name="claude-3-sonnet-20240229",
        sample_size=3,
        problem_types=["search"],
        max_iterations=3,
        output_dir="data"
    )

if __name__ == "__main__":
    asyncio.run(main())
```

You can also run the example directly from the command line:

```bash
uv run python examples/example_workflow.py \
    --model-type claude \
    --model-name claude-3-sonnet-20240229 \
    --sample-size 3 \
    --problem-types search \
    --max-iterations 3
```

## Project Structure

```
librarybench/
├── src/
│   └── librarybench/
│       ├── generation/        # Solution generation
│       │   ├── models/        # LLM client interfaces
│       │   │   ├── llm_client.py     # Abstract base class
│       │   │   ├── claude_client.py  # Claude-specific client
│       │   │   └── openai_client.py  # OpenAI-specific client
│       │   └── solution_generator.py # Solution generation pipeline
│       ├── execution/         # Solution testing
│       │   └── executor.py    # Execution and evaluation logic
│       ├── feedback/          # Feedback generation
│       │   └── feedback_generator.py # Model feedback generation 
│       ├── improvement/       # Iterative improvement
│       │   └── iterative_repair.py   # Solution refinement
│       ├── analysis/          # Comparison tools
│       │   └── model_comparison.py   # Solution comparison logic
│       └── utils/             # Shared utilities
│           └── helpers.py     # Helper functions
├── tests/                     # Test suite
├── examples/                  # Example scripts
└── data/                      # Solution data storage
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