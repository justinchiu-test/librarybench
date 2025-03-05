# Model Feedback Framework for LibraryBench

This framework enables providing test feedback to AI models and allows them to iteratively improve their solutions based on test results.

## Setup

1. Make sure the `CYBER_URL` environment variable is set. This should point to the execution API:

```bash
export CYBER_URL="your-execution-api-url"
```

2. Install the required dependencies:

```bash
uv sync
```

## Available Scripts

### 1. `model_feedback.py`

This script provides basic test execution and feedback generation functions.

**Key Functions:**
- `extract_code(solution)`: Extracts code from a model-generated solution
- `run_unit_tests(generations, stdin_stdout_tests)`: Executes code against test cases
- `format_feedback(test_results, test_cases, passed_count, total_count)`: Formats test results as feedback
- `get_model_feedback(solution_file, problem_id, model_name)`: Gets feedback for a specific model solution

**Example Usage:**
```bash
uv run python model_feedback.py
```

This will evaluate and print feedback for both Claude and O3 mini models on search problems by default.

### 2. `iterative_repair.py`

This script implements an iterative feedback loop that allows models to improve their solutions through multiple iterations. It supports asynchronous processing with semaphores for both LLM API calls and execution.

**Key Features:**
- Runs solutions against test cases asynchronously 
- Formats failure information for the model
- Queries the model for improved solutions
- Processes multiple problems in parallel
- Implements global semaphores for LLM and execution API calls
- Tracks the best solution found per problem

**Example Usage (Single Problem):**
```bash
uv run python iterative_repair.py --solution-file claude_search_solutions.json --problem-id 0 --model-name claude-3-sonnet --max-iterations 3
```

**Example Usage (Multiple Problems):**
```bash
# Process a specific set of problems
uv run python iterative_repair.py --solution-file claude_search_solutions.json --problem-ids 0,2,5 --model-name claude-3-haiku

# Process a range of problems
uv run python iterative_repair.py --solution-file claude_search_solutions.json --range 0-9 --max-iterations 5
```

**Arguments:**
- `--solution-file`: Path to the solution JSON file (required)
- `--problem-id`: ID of a specific problem to improve
- `--problem-ids`: Comma-separated list of problem IDs to process
- `--range`: Range of problem IDs to process (e.g., '0-5')
- `--model-name`: Name of the model to use (default: claude-3-haiku)
- `--max-iterations`: Maximum number of improvement iterations per problem (default: 3)
- `--target-ratio`: Target passing ratio to stop early (default: 1.0)
- `--output-file`: File to save improved solutions (default: improved_<input-file>)
- `--concurrent-problems`: Number of problems to process concurrently (default: 3)
- `--llm-semaphore`: Maximum concurrent LLM API calls (default: 5)
- `--exec-semaphore`: Maximum concurrent execution API calls (default: 50)
- `--log-level`: Logging level (DEBUG, INFO, WARNING, ERROR) (default: INFO)

### 3. `compare_model_improvements.py`

This script compares original and improved model solutions, providing detailed statistics on the improvements.

**Key Features:**
- Compares original and improved solutions on the same test cases
- Calculates improvement statistics (number of problems improved, pass rates, etc.)
- Identifies the most improved problems and any problems that got worse
- Generates detailed reports

**Example Usage:**
```bash
uv run python compare_model_improvements.py --original-file claude_search_solutions.json --improved-file improved_claude_search_solutions.json --model-key claude_solution --output-file comparison_results.json
```

**Arguments:**
- `--original-file`: Path to the original solution file (required)
- `--improved-file`: Path to the improved solution file (required)
- `--model-key`: Key for the model solutions (default: claude_solution)
- `--problem-id`: Optional ID of a specific problem to compare
- `--output-file`: Optional file to save comparison results as JSON

## Workflow Examples

### Individual Problem Workflow

1. Get initial feedback for a model:
```bash
uv run python model_feedback.py
```

2. Improve a specific problem solution:
```bash
uv run python iterative_repair.py --solution-file claude_search_solutions.json --problem-id 0 --max-iterations 3
```

3. Compare the original and improved solutions:
```bash
uv run python compare_model_improvements.py --original-file claude_search_solutions.json --improved-file improved_claude_search_solutions.json
```

### Batch Processing Workflow

1. Improve a range of problems:
```bash
uv run python iterative_repair.py --solution-file claude_search_solutions.json --range 0-9 --max-iterations 3 --concurrent-problems 5
```

2. Compare the original and improved solutions:
```bash
uv run python compare_model_improvements.py --original-file claude_search_solutions.json --improved-file improved_claude_search_solutions.json --output-file comparison_results.json
```

3. Analyze the results:
```bash
# Use any visualization tool or Python script to analyze the JSON results
uv run python -c "import json; f = open('comparison_results.json'); data = json.load(f); print(f'Average improvement: {data[\"overall_improvement\"]*100:.2f}%')"
```

## Customizing the Model API

To use actual model APIs instead of the placeholder in `iterative_repair.py`, update the `query_model()` function with the appropriate API client code for your specific model.

For Claude, use the Anthropic Python SDK:
```python
import anthropic
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
message = client.messages.create(
    model=model_name,
    max_tokens=4000,
    temperature=temperature,
    system="You are an expert Python programmer helping to improve code based on test feedback.",
    messages=[
        {"role": "user", "content": prompt}
    ]
)
return message.content[0].text
```

For OpenAI's GPT models, use the OpenAI Python client:
```python
import openai
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
response = client.chat.completions.create(
    model=model_name,
    temperature=temperature,
    messages=[
        {"role": "system", "content": "You are an expert Python programmer helping to improve code based on test feedback."},
        {"role": "user", "content": prompt}
    ]
)
return response.choices[0].message.content
```

## Performance Considerations

- The framework uses separate semaphores for controlling concurrency:
  - `LLM_SEMAPHORE`: Limits concurrent LLM API calls (default: 5)
  - `EXECUTION_SEMAPHORE`: Limits concurrent execution API calls (default: 50)
  - Problem-level concurrency for parallel processing (default: 3)

- Adjust these limits based on your specific environment and API rate limits:
  - Increase `llm-semaphore` if you have higher API rate limits
  - Adjust `exec-semaphore` based on the execution API's capacity
  - Set `concurrent-problems` based on available CPU/memory resources

## Notes

- The execution API requires internet access to function properly.
- Make sure your model API keys are properly set up in environment variables if you're using real model APIs.
- For large batches, consider using checkpointing by specifying custom output files.