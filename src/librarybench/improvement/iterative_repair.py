"""Iterative repair module for improving model solutions."""

import os
import json
import asyncio
import aiohttp
import logging
from typing import Dict, Any, List, Tuple, Optional

from librarybench.utils import extract_code
from librarybench.feedback.feedback_generator import (
    create_test_cases_from_input_output,
    format_feedback,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global semaphores for controlling concurrent requests
LLM_SEMAPHORE = asyncio.Semaphore(5)  # Limit concurrent LLM API calls
EXECUTION_SEMAPHORE = asyncio.Semaphore(50)  # Limit concurrent execution API calls


async def execute_test(
    session: aiohttp.ClientSession,
    code: str,
    test: Dict[str, str],
    cyber_url: str,
) -> Dict[str, Any]:
    """Execute a single test against the execution API with semaphore control.

    Args:
        session: aiohttp ClientSession
        code: Python code to execute
        test: Test case with stdin/stdout
        cyber_url: URL for the execution API

    Returns:
        Test execution result
    """
    async with EXECUTION_SEMAPHORE:
        code_dict = {
            "code": code,
            "test": test,
        }

        params = {
            "language": "python",
            "environment": "default",
            "timeout": 30,
            "generation_formatting": "true",
            "fill_missing_imports": "true",
        }

        try:
            async with session.post(
                cyber_url, json=code_dict, params=params
            ) as response:
                result = await response.json()
                return result
        except Exception as e:
            return {
                "passed": False,
                "exec_output": {"run_output": {"stderr": str(e)}},
                "uncaught_exception": str(e),
            }


async def run_tests(
    code: str, stdin_stdout_tests: List[Dict[str, str]], cyber_url: str
) -> List[Dict[str, Any]]:
    """Execute code against unit tests using the execution API asynchronously.

    Args:
        code: Python code to execute
        stdin_stdout_tests: List of test cases with stdin/stdout pairs
        cyber_url: URL for the execution API

    Returns:
        List of test results
    """
    async with aiohttp.ClientSession() as session:
        tasks = [
            execute_test(session, code, test, cyber_url) for test in stdin_stdout_tests
        ]
        return await asyncio.gather(*tasks)


async def query_model(
    prompt: str,
    model_name: str = "claude-3-haiku",
    api_key: Optional[str] = None,
    temperature: float = 0.2,
) -> str:
    """
    Query an LLM with a prompt using the appropriate API.

    Args:
        prompt: The text prompt to send to the model
        model_name: The name of the model to use
        api_key: API key for the model provider (if None, uses environment variable)
        temperature: Temperature setting for model generation

    Returns:
        The model's text response
    """
    async with LLM_SEMAPHORE:
        logger.info(f"Querying {model_name} with prompt (length: {len(prompt)} chars)")

        # For Claude models
        if "claude" in model_name.lower():
            try:
                from anthropic import AsyncAnthropic
            except ImportError:
                raise ImportError(
                    "Please install the anthropic package: pip install anthropic"
                )

            api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("No API key provided for Anthropic API")

            client = AsyncAnthropic(api_key=api_key)
            response = await client.messages.create(
                model=model_name,
                max_tokens=4000,
                temperature=temperature,
                system="You are an expert Python programmer helping to improve code based on test feedback.",
                messages=[{"role": "user", "content": prompt}],
            )
            if not response.content or len(response.content) == 0:
                return ""
            try:
                return response.content[0].text
            except (AttributeError, IndexError):
                return ""

        # For OpenAI models
        elif "gpt" in model_name.lower() or "o3" in model_name.lower():
            try:
                from openai import AsyncOpenAI
            except ImportError:
                raise ImportError(
                    "Please install the openai package: pip install openai"
                )

            api_key = api_key or os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("No API key provided for OpenAI API")

            client = AsyncOpenAI(api_key=api_key)
            response = await client.chat.completions.create(
                model=model_name,
                temperature=temperature,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert Python programmer helping to improve code based on test feedback.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            if not response.choices or len(response.choices) == 0:
                return ""
            content = response.choices[0].message.content
            return content if content is not None else ""

        # If model type not recognized
        raise ValueError(f"Unsupported model type: {model_name}")


async def improve_solution(
    solution_data: Dict[str, Any],
    problem_id: int,
    cyber_url: str,
    model_name: str = "claude-3-haiku",
    max_iterations: int = 3,
    target_passed_ratio: float = 1.0,
) -> Tuple[str, float, Dict[str, Any]]:
    """
    Run the improvement loop for a specific problem solution.

    Args:
        solution_data: The solution data for the problem
        problem_id: The ID of the problem being improved
        cyber_url: URL for the execution API
        model_name: The name of the model to use
        max_iterations: Maximum number of iterations for improvement
        target_passed_ratio: Target passing ratio to stop early

    Returns:
        Tuple of (best_code, best_ratio, improvement_data)
    """
    # Extract problem statement
    problem_statement = solution_data.get("problem", "")

    # Get the input_output field
    input_output = solution_data.get("input_output")
    if not input_output:
        raise ValueError(f"No input_output field found for problem {problem_id}")

    # Parse input_output if it's a string
    if isinstance(input_output, str):
        try:
            input_output = json.loads(input_output)
        except json.JSONDecodeError:
            raise ValueError(
                f"Error parsing input_output JSON for problem {problem_id}"
            )

    # Format as stdin/stdout tests
    stdin_stdout_tests = create_test_cases_from_input_output(input_output)
    if not stdin_stdout_tests:
        raise ValueError(f"No test cases found for problem {problem_id}")

    # Extract the initial code (depending on model type)
    if "o3_mini" in model_name.lower() or "openai" in model_name.lower():
        initial_solution = solution_data.get("o3_mini_solution", "")
        model_type = "openai"
    else:
        initial_solution = solution_data.get("claude_solution", "")
        model_type = "claude"

    # Extract the code
    current_code = extract_code(initial_solution, model_type)

    logger.info(f"Starting improvement for problem {problem_id}")
    logger.info(f"Model: {model_name}")
    logger.info(f"Max iterations: {max_iterations}")
    logger.info(f"Target passed ratio: {target_passed_ratio}")

    iteration = 0
    best_passed_ratio = 0.0
    best_code = current_code
    improvement_history = []

    # Run initial evaluation
    initial_results = await run_tests(current_code, stdin_stdout_tests, cyber_url)
    initial_passed = sum(1 for result in initial_results if result.get("passed", False))
    initial_ratio = initial_passed / len(stdin_stdout_tests)

    # If all tests already pass, we're done
    if initial_ratio >= target_passed_ratio:
        logger.info(
            f"Initial solution already meets target pass ratio: {initial_ratio:.2%}"
        )
        return (
            current_code,
            initial_ratio,
            {
                "problem_id": problem_id,
                "initial_ratio": initial_ratio,
                "final_ratio": initial_ratio,
                "iterations": 0,
                "history": [],
                "best_code": current_code,
            },
        )

    # Initialize best code/ratio with initial values
    best_passed_ratio = initial_ratio
    best_code = current_code

    while iteration < max_iterations:
        iteration += 1
        logger.info(f"Iteration {iteration}/{max_iterations}")

        # Run the code against test cases
        test_results = await run_tests(current_code, stdin_stdout_tests, cyber_url)

        # Calculate pass rate
        passed = sum(1 for result in test_results if result.get("passed", False))
        total = len(stdin_stdout_tests)
        passed_ratio = passed / total

        logger.info(f"Current pass rate: {passed}/{total} ({passed_ratio:.2%})")
        improvement_history.append(
            {
                "iteration": iteration,
                "pass_ratio": passed_ratio,
                "passed": passed,
                "total": total,
            }
        )

        # If all tests pass or we've reached target ratio, we're done
        if passed_ratio >= target_passed_ratio:
            logger.info("Target pass ratio reached. Stopping.")
            best_passed_ratio = passed_ratio
            best_code = current_code
            break

        # Keep track of the best solution so far
        if passed_ratio > best_passed_ratio:
            best_passed_ratio = passed_ratio
            best_code = current_code

        # Format feedback for the model
        feedback = format_feedback(test_results, stdin_stdout_tests, passed, total)

        # Create prompt for the model
        prompt = f"""You are an expert Python programmer. Your task is to fix a solution to a coding problem.

Problem statement:
{problem_statement}

Here is the current solution:
```python
{current_code}
```

Here are the test results:
{feedback}

Please analyze the code carefully, identify the issues causing the failed tests, and provide a completely fixed solution.
Return just the fixed Python code, wrapped in ```python code blocks.
"""

        # Query the model for an improved solution
        response = await query_model(prompt, model_name)

        # Extract the new code from the response
        new_code = extract_code(response, model_type)

        # If we couldn't extract any code, use the original response
        if not new_code:
            new_code = response

        # Update the current code
        current_code = new_code

    # Create improvement data
    improvement_data = {
        "problem_id": problem_id,
        "initial_ratio": initial_ratio,
        "final_ratio": best_passed_ratio,
        "iterations": iteration,
        "history": improvement_history,
        "best_code": best_code,
    }

    logger.info("Final Results:")
    logger.info(f"Initial pass ratio: {initial_ratio:.2%}")
    logger.info(f"Best pass ratio: {best_passed_ratio:.2%}")
    logger.info(
        f"Improvement: {(best_passed_ratio - initial_ratio) * 100:.2f} percentage points"
    )

    return best_code, best_passed_ratio, improvement_data


async def batch_improve_solutions(
    solution_file: str,
    cyber_url: str,
    problem_ids: Optional[List[int]] = None,
    model_name: str = "claude-3-haiku",
    max_iterations: int = 3,
    target_passed_ratio: float = 1.0,
    output_file: Optional[str] = None,
    concurrent_problems: int = 3,
) -> Dict[str, Any]:
    """
    Process multiple problems for improvement in parallel.

    Args:
        solution_file: Path to the solution JSON file
        cyber_url: URL for the execution API
        problem_ids: List of problem IDs to improve (if None, process all)
        model_name: Name of the model to use
        max_iterations: Maximum number of improvement iterations per problem
        target_passed_ratio: Target passing ratio to stop early
        output_file: Optional file to save improved solutions
        concurrent_problems: Number of problems to process concurrently

    Returns:
        Dictionary with improvement results
    """
    # Load solutions
    with open(solution_file, "r") as f:
        solutions = json.load(f)

    # If no problem IDs provided, process all
    if problem_ids is None:
        problem_ids = list(range(len(solutions)))

    # Filter valid problem IDs
    valid_problem_ids = [pid for pid in problem_ids if pid < len(solutions)]
    if len(valid_problem_ids) < len(problem_ids):
        skipped = set(problem_ids) - set(valid_problem_ids)
        logger.warning(f"Skipping out-of-range problem IDs: {skipped}")

    # Create a copy of solutions to store improvements
    improved_solutions = solutions.copy()

    # Create a semaphore to limit concurrent problem processing
    problem_semaphore = asyncio.Semaphore(concurrent_problems)

    async def process_problem(problem_id: int) -> Dict[str, Any]:
        """Process a single problem with semaphore control."""
        async with problem_semaphore:
            try:
                logger.info(f"Processing problem {problem_id}")
                solution_data = solutions[problem_id]

                best_code, pass_ratio, improvement_data = await improve_solution(
                    solution_data=solution_data,
                    problem_id=problem_id,
                    cyber_url=cyber_url,
                    model_name=model_name,
                    max_iterations=max_iterations,
                    target_passed_ratio=target_passed_ratio,
                )

                # Update the solution in our copy
                if "o3_mini" in model_name.lower() or "openai" in model_name.lower():
                    model_key = "o3_mini_solution"
                else:
                    model_key = "claude_solution"

                improved_solutions[problem_id][f"improved_{model_key}"] = (
                    f"```python\n{best_code}\n```"
                )

                return {
                    "problem_id": problem_id,
                    "status": "completed",
                    **improvement_data,
                }
            except Exception as e:
                logger.error(f"Error processing problem {problem_id}: {e}")
                return {"problem_id": problem_id, "status": "error", "error": str(e)}

    # Process all problems concurrently
    tasks = [process_problem(pid) for pid in valid_problem_ids]
    results = await asyncio.gather(*tasks)

    # Generate summary
    completed = [r for r in results if r["status"] == "completed"]
    errors = [r for r in results if r["status"] == "error"]

    summary = {
        "total_problems": len(valid_problem_ids),
        "completed": len(completed),
        "errors": len(errors),
        "problem_results": results,
        "avg_initial_ratio": 0.0,
        "avg_final_ratio": 0.0,
        "avg_improvement": 0.0,
        "perfect_solutions": 0,
    }

    if completed:
        avg_initial = sum(r.get("initial_ratio", 0) for r in completed) / len(completed)
        avg_final = sum(r.get("final_ratio", 0) for r in completed) / len(completed)
        perfect = sum(1 for r in completed if r.get("final_ratio", 0) == 1.0)

        summary.update(
            {
                "avg_initial_ratio": avg_initial,
                "avg_final_ratio": avg_final,
                "avg_improvement": avg_final - avg_initial,
                "perfect_solutions": perfect,
            }
        )

    # Save improved solutions if output file is provided
    if output_file is None:
        output_file = f"improved_{os.path.basename(solution_file)}"

    with open(output_file, "w") as f:
        json.dump(improved_solutions, f, indent=2)

    logger.info(f"Improved solutions saved to {output_file}")

    # Print summary
    logger.info("\nBatch Processing Summary:")
    logger.info(f"Total problems processed: {len(valid_problem_ids)}")
    logger.info(f"Successfully completed: {len(completed)}")
    logger.info(f"Errors: {len(errors)}")

    if completed:
        avg_initial = summary["avg_initial_ratio"]
        avg_final = summary["avg_final_ratio"]
        perfect = summary["perfect_solutions"]
        logger.info(f"Average initial pass ratio: {avg_initial:.2%}")
        logger.info(f"Average final pass ratio: {avg_final:.2%}")
        logger.info(
            f"Average improvement: {(avg_final - avg_initial) * 100:.2f} percentage points"
        )
        logger.info(
            f"Problems with perfect pass ratio: {perfect}/{len(completed)} ({perfect / len(completed):.2%})"
        )

    # Save summary to a separate file
    summary_file = f"summary_{os.path.basename(output_file)}"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)

    logger.info(f"Summary saved to {summary_file}")

    return summary
