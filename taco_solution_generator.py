import os
import json
import datasets
import openai
import asyncio
from tqdm.asyncio import tqdm_asyncio

# Load API key from environment variable
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Please set the OPENAI_API_KEY environment variable")

# Create OpenAI client
async_client = openai.AsyncOpenAI(api_key=api_key)


def get_solutions(xs):
    """Extract examples with valid solutions."""
    examples = []
    for i, x in enumerate(xs):
        try:
            # Handle case where solutions may already be parsed
            if isinstance(x["solutions"], list):
                solutions = x["solutions"]
            else:
                # Try to remove any bad characters from the JSON string
                solutions_str = x["solutions"]
                # Ensure solutions_str is actually a string
                if not isinstance(solutions_str, str):
                    continue

                # Try direct parsing first
                try:
                    solutions = json.loads(solutions_str)
                except json.JSONDecodeError:
                    # If direct parsing fails, try with ast.literal_eval which is more forgiving
                    import ast

                    try:
                        solutions = ast.literal_eval(solutions_str)
                    except Exception:
                        # If all parsing fails, skip this example
                        print("Skipping example with unparseable solutions")
                        continue

            if len(solutions) > 0:
                x["solutions"] = solutions
                examples.append(x)
        except Exception as e:
            print(f"Error processing example: {str(e)[:100]}")
            continue

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
    """Generate a solution using OpenAI API asynchronously."""
    prompt = format_prompt(example)
    
    async with semaphore:  # Properly acquire and release the semaphore
        for attempt in range(max_retries):
            try:
                response = await async_client.chat.completions.create(
                    model="o3-mini",
                    messages=[
                        {"role": "system", "content": "You are an expert programming problem solver specializing in competitive programming and algorithm challenges."},
                        {"role": "user", "content": prompt}
                    ],
                )
                # Create a copy of the original example to preserve all keys
                result = {k: v for k, v in example.items()}
                # Add the generated solution
                result["human_solution"] = (
                    example["solutions"][0] if example["solutions"] else None
                )
                # Extract solution text from response content
                result["claude_solution"] = response.choices[0].message.content
                # Rename question to problem for clarity in the output
                result["problem"] = result.pop("question") if "question" in result else None
                # Rename solution field to match the model being used
                result["o3_mini_solution"] = result.pop("claude_solution")
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
                    result["o3_mini_solution"] = f"ERROR: {str(e)}"
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


async def main_async():
    # Load the TACO dataset
    dataset = datasets.load_dataset("BAAI/TACO", trust_remote_code=True)
    train = dataset["test"]

    # Filter for problems with specific skills
    search_problems = [x for x in train if "Complete search" in x["skill_types"]]
    datastructure_problems = [x for x in train if "Data structures" in x["skill_types"]]

    # Select a sample for evaluation
    sample_size = 5  # Process 5 examples of each type
    concurrency = 5  # Number of concurrent requests

    # Generate solutions for search problems
    print(f"Generating solutions for {sample_size} search problems...")
    search_examples = get_solutions(search_problems)
    search_results = await generate_solutions_from_examples(
        search_examples, sample_size, concurrency
    )
    save_solutions(search_results, "o3mini_search_solutions.json")

    # Generate solutions for data structure problems
    print(f"Generating solutions for {sample_size} data structure problems...")
    datastructure_examples = get_solutions(datastructure_problems)
    # Fix: Use the datastructure_examples directly instead of creating an unused sample
    datastructure_results = await generate_solutions_from_examples(
        datastructure_examples, sample_size, concurrency
    )
    save_solutions(datastructure_results, "o3mini_datastructure_solutions.json")

    print("Done! Solutions generated for both problem types.")


def main():
    """Run the async main function."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
