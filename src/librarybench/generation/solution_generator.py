"""Solution generator module for LibraryBench."""

import ast
import json
import asyncio
from typing import Any, Dict, List, Optional
import datasets
from tqdm.asyncio import tqdm_asyncio

from librarybench.generation.models import LlmClient, OpenAiClient, ClaudeClient


def get_solutions(xs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract examples with valid solutions.

    Args:
        xs: List of examples from dataset

    Returns:
        List of examples with valid solutions
    """
    examples = []
    for x in xs:
        solutions = ast.literal_eval(x["solutions"])
        if len(solutions) > 0:
            x["solutions"] = solutions
            examples.append(x)
    print(f"Found {len(examples)} valid examples with solutions")
    return examples


def format_prompt(example: Dict[str, Any]) -> str:
    """Format the problem for the model.

    Args:
        example: Problem example with solutions

    Returns:
        Formatted prompt for the model
    """
    # Parse input_output field to extract test cases
    input_output = example.get("input_output", "{}")
    if isinstance(input_output, str):
        try:
            input_output = json.loads(input_output)
        except json.JSONDecodeError:
            input_output = {"inputs": [], "outputs": []}

    # Extract up to 3 test cases
    test_cases_md = ""
    if "inputs" in input_output and "outputs" in input_output:
        inputs = input_output["inputs"]
        outputs = input_output["outputs"]
        for i in range(min(3, len(inputs))):
            test_cases_md += f"""
### Test Case {i + 1}
**Input:**
```
{inputs[i]}
```

**Expected Output:**
```
{outputs[i]}
```
"""

    prompt = f"""
You are an expert programming problem solver. Please solve the following problem with a complete, runnable solution.

Problem:
{example["question"]}

## Example Test Cases
{test_cases_md}

## Requirements
1. Your solution MUST read all input from standard input (stdin) and write to standard output (stdout)
2. Include ALL necessary code to parse input and format output correctly
3. Your solution must pass ALL test cases and handle edge cases
4. Provide a fully executable solution - this code will be run as-is without modification
5. Do not include explanatory text or comments outside of your code block

## Solution
Please write your complete solution below:

```python
# Your solution code here
```
"""
    return prompt


async def generate_solution(
    example: Dict[str, Any],
    llm_client: LlmClient,
    semaphore: asyncio.Semaphore,
    max_retries: int = 2,
) -> Dict[str, Any]:
    """Generate a solution using the configured LLM client asynchronously.

    Args:
        example: Problem example with solutions
        llm_client: Language model client to use
        semaphore: Semaphore for limiting concurrency
        max_retries: Maximum number of retries

    Returns:
        Example with generated solution
    """
    prompt = format_prompt(example)
    system_prompt = "You are an expert programming problem solver specializing in competitive programming and algorithm challenges."

    async with semaphore:  # Properly acquire and release the semaphore
        for attempt in range(max_retries):
            try:
                # Use the abstracted LLM client
                solution_text = await llm_client.generate_completion(
                    prompt, system_prompt
                )

                # Create a copy of the original example to preserve all keys
                result = {k: v for k, v in example.items()}
                # Add the generated solution
                result["human_solution"] = (
                    example["solutions"][0] if example["solutions"] else None
                )
                # Store the solution with the model-specific key name
                model_solution_key = f"{llm_client.model_name}_solution"
                result[model_solution_key] = solution_text
                # Save the prompt used for this generation
                result["prompt"] = prompt
                # Rename question to problem for clarity in the output
                result["problem"] = (
                    result.pop("question") if "question" in result else None
                )

                return result
            except Exception as e:
                print(f"Error on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    # Create a copy of the original example to preserve all keys
                    result = {k: v for k, v in example.items()}
                    # Add the error message as the solution
                    result["human_solution"] = (
                        example["solutions"][0] if example["solutions"] else None
                    )
                    # Store the error with the model-specific key name
                    model_solution_key = f"{llm_client.model_name}_solution"
                    result[model_solution_key] = f"ERROR: {str(e)}"
                    # Save the prompt used for this generation
                    result["prompt"] = prompt
                    # Rename question to problem for clarity in the output
                    result["problem"] = (
                        result.pop("question") if "question" in result else None
                    )
                    return result
                # Add a short delay before retrying
                await asyncio.sleep(1)


async def generate_solutions_from_examples(
    examples: List[Dict[str, Any]],
    llm_client: LlmClient,
    sample_size: Optional[int] = None,
    concurrency: int = 5,
) -> List[Dict[str, Any]]:
    """
    Generate solutions for a given list of examples asynchronously.

    Args:
        examples: List of problem examples with solutions
        llm_client: Language model client to use
        sample_size: Optional number of examples to use (defaults to all)
        concurrency: Maximum number of concurrent requests (default: 5)

    Returns:
        List of results with generated solutions
    """
    if sample_size is not None:
        examples = examples[:sample_size]

    # Create semaphore to limit concurrency
    semaphore = asyncio.Semaphore(concurrency)

    # Create tasks and pass the semaphore to each
    tasks = [generate_solution(example, llm_client, semaphore) for example in examples]

    # Process examples concurrently with progress bar
    results = await tqdm_asyncio.gather(*tasks, desc="Generating solutions")

    return results


def save_solutions(results: List[Dict[str, Any]], filename: str) -> None:
    """
    Save generated solutions to a JSON file.

    Args:
        results: List of results with generated solutions
        filename: Name of the file to save results to
    """
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {filename}")


async def generate_solutions(
    model_type: str = "openai",
    model_name: Optional[str] = None,
    sample_size: int = 5,
    concurrency: int = 5,
    problem_types: List[str] = ["search", "datastructure", "chess"],
    output_dir: str = "data",
) -> None:
    """
    Main async function to generate solutions.

    Args:
        model_type: Type of model to use ("openai" or "claude")
        model_name: Specific model name to use, or None to use default
        sample_size: Number of examples to process
        concurrency: Number of concurrent requests
        problem_types: List of problem types to generate solutions for
        output_dir: Directory to save solutions to
    """
    # Set up the correct LLM client based on user preferences
    if model_type.lower() == "claude":
        if model_name:
            llm_client = ClaudeClient(model=model_name)
        else:
            llm_client = ClaudeClient()  # Use default Claude model
        print(f"Using Claude model: {llm_client._model}")
    else:
        if model_name:
            llm_client = OpenAiClient(model=model_name)
        else:
            llm_client = OpenAiClient()  # Use default OpenAI model
        print(f"Using OpenAI model: {llm_client._model}")

    # Define output directory prefix based on model
    output_prefix = f"{output_dir}/{llm_client.model_name}"

    # Load the TACO dataset
    dataset = datasets.load_dataset("BAAI/TACO", trust_remote_code=True)
    train = dataset["test"]

    # Filter for problems with specific skills
    search_problems = [x for x in train if "Complete search" in x["skill_types"]]
    datastructure_problems = [x for x in train if "Data structures" in x["skill_types"]]
    chess_problems = [x for x in train if "chess" in x["question"].lower()]

    if "search" in problem_types:
        # Generate solutions for search problems
        print(f"Generating solutions for {sample_size} search problems...")
        search_examples = get_solutions(search_problems)
        search_results = await generate_solutions_from_examples(
            search_examples, llm_client, sample_size, concurrency
        )
        save_solutions(search_results, f"{output_prefix}_search_solutions.json")

    if "datastructure" in problem_types:
        # Generate solutions for data structure problems
        print(f"Generating solutions for {sample_size} data structure problems...")
        datastructure_examples = get_solutions(datastructure_problems)
        datastructure_results = await generate_solutions_from_examples(
            datastructure_examples, llm_client, sample_size, concurrency
        )
        save_solutions(
            datastructure_results, f"{output_prefix}_datastructure_solutions.json"
        )

    if "chess" in problem_types:
        # Generate solutions for chess problems
        print(f"Generating solutions for {sample_size} chess problems...")
        chess_examples = get_solutions(chess_problems)
        chess_results = await generate_solutions_from_examples(
            chess_examples, llm_client, sample_size, concurrency
        )
        save_solutions(chess_results, f"{output_prefix}_chess_solutions.json")

    print(f"Done! Solutions generated for all problem types using {llm_client._model}.")
    return {"status": "success"}
