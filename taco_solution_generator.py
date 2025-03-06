import ast
import os
import json
import datasets
import openai
import asyncio
import abc
from tqdm.asyncio import tqdm_asyncio


class LlmClient(abc.ABC):
    """Abstract base class for LLM clients."""

    @abc.abstractmethod
    async def generate_completion(self, prompt: str, system_prompt: str) -> str:
        """Generate a completion for the given prompt."""
        pass

    @abc.abstractmethod
    def extract_code(self, solution: str) -> str:
        """Extract code from the model's solution text."""
        pass

    @property
    @abc.abstractmethod
    def model_name(self) -> str:
        """Return the name of the model being used."""
        pass


class OpenAiClient(LlmClient):
    """Client for OpenAI models."""

    def __init__(self, model: str = "o3-mini"):
        # Load API key from environment variable
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Please set the OPENAI_API_KEY environment variable")

        # Create OpenAI client
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self._model = model

    async def generate_completion(self, prompt: str, system_prompt: str) -> str:
        """Generate a completion using OpenAI API."""
        response = await self.client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        if len(response.choices) == 0:
            return "Error: len(response.choices) == 0"
        return response.choices[0].message.content

    def extract_code(self, solution: str) -> str:
        """Extract code from OpenAI solution using dash pattern."""
        import re

        # For O3 mini solutions, try to extract code between dashed lines
        dashed_code_pattern = r"[-]{5,}\n(.*?)[-]{5,}"
        match = re.search(dashed_code_pattern, solution, re.DOTALL)
        if match:
            return match.group(1)

        # Try to extract code between ```python and ``` markers
        code_pattern = r"```python\n(.*?)\n```"
        match = re.search(code_pattern, solution, re.DOTALL)
        if match:
            return match.group(1)

        # If no markers found, try to extract the first code-like block
        code_pattern = r"class .*?:|def .*?:"
        match = re.search(code_pattern, solution)
        if match:
            # Get the position of the match
            start_pos = match.start()
            # Extract from this position to the end
            return solution[start_pos:]

        return solution

    @property
    def model_name(self) -> str:
        """Return the model name for result naming."""
        return self._model.replace("-", "_")


class ClaudeClient(LlmClient):
    """Client for Anthropic Claude models."""

    def __init__(self, model: str = "claude-3-7-sonnet-20250219"):
        try:
            from anthropic import AsyncAnthropic
        except ImportError:
            raise ImportError(
                "Please install the anthropic package: pip install anthropic"
            )

        # Load API key from environment variable
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Please set the ANTHROPIC_API_KEY environment variable")

        # Create Anthropic client
        self.client = AsyncAnthropic(api_key=api_key)
        self._model = model

    async def generate_completion(self, prompt: str, system_prompt: str) -> str:
        """Generate a completion using Anthropic API."""
        response = await self.client.messages.create(
            model=self._model,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4096,
        )
        return response.content[0].text

    def extract_code(self, solution: str) -> str:
        """Extract code from Claude solution using markdown code blocks."""
        import re

        # Try to extract code between ```python and ``` markers (Claude's standard format)
        code_pattern = r"```python\n(.*?)\n```"
        match = re.search(code_pattern, solution, re.DOTALL)
        if match:
            return match.group(1)

        # If no python markers found, try with any language marker
        code_pattern = r"```(?:\w+)?\n(.*?)\n```"
        match = re.search(code_pattern, solution, re.DOTALL)
        if match:
            return match.group(1)

        # If no markers found, try to extract the first code-like block
        code_pattern = r"class .*?:|def .*?:"
        match = re.search(code_pattern, solution)
        if match:
            # Get the position of the match
            start_pos = match.start()
            # Extract from this position to the end
            return solution[start_pos:]

        return solution

    @property
    def model_name(self) -> str:
        """Return the model name for result naming."""
        return self._model.replace("-", "_").replace(".", "_")


# Default client - can be changed in config
llm_client = OpenAiClient(model="o3-mini")


def get_solutions(xs):
    """Extract examples with valid solutions."""
    examples = []
    for x in xs:
        solutions = ast.literal_eval(x["solutions"])
        if len(solutions) > 0:
            x["solutions"] = solutions
            examples.append(x)
    print(f"Found {len(examples)} valid examples with solutions")
    return examples


def format_prompt(example):
    """Format the problem for Claude."""
    prompt = f"""
You are an expert programming problem solver. Please solve the following problem using efficient algorithms and provide a well-commented solution.

Problem:
{example["question"]}

Please provide a clear, efficient solution in Python. Make sure to handle edge cases and optimize for the expected time and space complexity.
"""
    return prompt


async def generate_solution(example, semaphore, max_retries=2):
    """Generate a solution using the configured LLM client asynchronously."""
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
                    # Rename question to problem for clarity in the output
                    result["problem"] = (
                        result.pop("question") if "question" in result else None
                    )
                    return result
                # Add a short delay before retrying
                await asyncio.sleep(1)


async def generate_solutions_from_examples(examples, sample_size=None, concurrency=5):
    """
    Generate solutions for a given list of examples asynchronously.

    Args:
        examples: List of problem examples with solutions
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
    tasks = [generate_solution(example, semaphore) for example in examples]

    # Process examples concurrently with progress bar
    results = await tqdm_asyncio.gather(*tasks, desc="Generating solutions")

    return results


def save_solutions(results, filename):
    """
    Save generated solutions to a JSON file.

    Args:
        results: List of results with generated solutions
        filename: Name of the file to save results to
    """
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {filename}")


async def main_async(
    model_type="openai", model_name=None, sample_size=5, concurrency=5
):
    """
    Main async function to generate solutions.

    Args:
        model_type: Type of model to use ("openai" or "claude")
        model_name: Specific model name to use, or None to use default
        sample_size: Number of examples to process
        concurrency: Number of concurrent requests
    """
    global llm_client

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
    output_prefix = f"data/{llm_client.model_name}"

    # Load the TACO dataset
    dataset = datasets.load_dataset("BAAI/TACO", trust_remote_code=True)
    train = dataset["test"]

    # Filter for problems with specific skills
    search_problems = [x for x in train if "Complete search" in x["skill_types"]]
    datastructure_problems = [x for x in train if "Data structures" in x["skill_types"]]
    chess_problems = [x for x in train if "chess" in x["question"].lower()]

    # Generate solutions for search problems
    print(f"Generating solutions for {sample_size} search problems...")
    search_examples = get_solutions(search_problems)
    search_results = await generate_solutions_from_examples(
        search_examples, sample_size, concurrency
    )
    save_solutions(search_results, f"{output_prefix}_search_solutions.json")

    # Generate solutions for data structure problems
    print(f"Generating solutions for {sample_size} data structure problems...")
    datastructure_examples = get_solutions(datastructure_problems)
    datastructure_results = await generate_solutions_from_examples(
        datastructure_examples, sample_size, concurrency
    )
    save_solutions(
        datastructure_results, f"{output_prefix}_datastructure_solutions.json"
    )

    # Generate solutions for chess problems
    print(f"Generating solutions for {sample_size} chess problems...")
    chess_examples = get_solutions(chess_problems)
    chess_results = await generate_solutions_from_examples(
        chess_examples, sample_size, concurrency
    )
    save_solutions(chess_results, f"{output_prefix}_chess_solutions.json")

    print(f"Done! Solutions generated for all problem types using {llm_client._model}.")


def main():
    """Run the async main function with command line arguments."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate solutions for TACO problems")
    parser.add_argument(
        "--model-type",
        choices=["openai", "claude"],
        default="openai",
        help="Type of model to use (openai or claude)",
    )
    parser.add_argument(
        "--model-name",
        default="o3-mini",
        type=str,
        help="Specific model name to use (e.g., 'o3-mini' or 'claude-3-opus-20240229')",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=5,
        help="Number of examples to process for each problem type",
    )
    parser.add_argument(
        "--concurrency", type=int, default=5, help="Number of concurrent requests"
    )

    args = parser.parse_args()

    asyncio.run(
        main_async(
            model_type=args.model_type,
            model_name=args.model_name,
            sample_size=args.sample_size,
            concurrency=args.concurrency,
        )
    )


if __name__ == "__main__":
    main()
