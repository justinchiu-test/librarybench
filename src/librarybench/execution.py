"""Execution module for testing generated solutions."""

import os
import json
import asyncio
import aiohttp
from tqdm import tqdm
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, field_validator

from librarybench.utils import extract_code
from librarybench.types import ExecutionOutput, EvaluationResult, EvaluationResults, ProblemEvaluationResult, StdinStdout

# URL for execution API - load from environment variable
CYBER_URL: str = os.getenv("CYBER_URL", "")


async def execute_test(
    session: aiohttp.ClientSession,
    code: str,
    test: StdinStdout,
    semaphore: asyncio.Semaphore,
) -> Dict[str, Any]:
    """Execute a single test against the execution API.

    Args:
        session: aiohttp ClientSession
        code: Python code to execute
        test: Test case with stdin/stdout
        semaphore: Semaphore to limit concurrency

    Returns:
        Test execution result
    """
    async with semaphore:
        code_dict = {
            "code": code,
            "test": test.model_dump(),
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
                CYBER_URL, json=code_dict, params=params
            ) as response:
                result = await response.json()
                return result
        except Exception as e:
            return {
                "passed": False,
                "exec_output": {"run_output": {"stderr": str(e)}},
                "uncaught_exception": str(e),
            }


async def run_unit_tests_async(
    generations: List[str],
    stdin_stdout_tests: List[StdinStdout],
    concurrency: int = 512,
) -> List[List[Dict[str, Any]]]:
    """Execute code against unit tests using the execution API asynchronously.

    Args:
        generations: List of code snippets to test
        stdin_stdout_tests: List of test cases with stdin/stdout pairs
        concurrency: Maximum number of concurrent requests

    Returns:
        Nested list of test results for each generation and test case
    """
    outputs = []
    semaphore = asyncio.Semaphore(concurrency)  # Limit concurrency

    async with aiohttp.ClientSession() as session:
        for generation in tqdm(generations, desc="Running tests"):
            tasks = [
                execute_test(session, generation, test, semaphore)
                for test in stdin_stdout_tests
            ]
            test_results = await asyncio.gather(*tasks)
            outputs.append(test_results)

    return outputs


def run_unit_tests(
    generations: List[str],
    stdin_stdout_tests: List[StdinStdout],
    concurrency: int = 512,
) -> List[List[Dict[str, Any]]]:
    """Execute code against unit tests using the execution API.

    Args:
        generations: List of code snippets to test
        stdin_stdout_tests: List of test cases with stdin/stdout pairs
        concurrency: Maximum number of concurrent requests

    Returns:
        Nested list of test results for each generation and test case
    """
    return asyncio.run(
        run_unit_tests_async(generations, stdin_stdout_tests, concurrency)
    )


async def evaluate_solution(
    code: str,
    test_cases: List[StdinStdout],
    cyber_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Evaluate a code solution with the execution API.
    
    Args:
        code: Python code to evaluate
        test_cases: List of input/output test cases
        cyber_url: URL for execution API (optional)
        
    Returns:
        Dict with execution results
    """
    # Set up cyber URL
    if cyber_url is None:
        cyber_url = CYBER_URL
        if not cyber_url:
            raise ValueError("No execution API URL provided. Set CYBER_URL environment variable.")
    
    # Run code against all test cases
    test_results = await run_unit_tests_async([code], test_cases)
    test_results_flat = test_results[0] if test_results else []
    
    # Calculate pass ratio
    passed = sum(1 for result in test_results_flat if result.get("passed", False))
    total = len(test_cases)
    pass_ratio = passed / total if total > 0 else 0
    
    return {
        "pass_ratio": pass_ratio,
        "tests_passed": passed,
        "tests_total": total,
        "results": test_results_flat
    }


async def evaluate_solutions_async(
    solution_file: str, output_dir: Optional[str] = None
) -> EvaluationResults:
    """Evaluate generated solutions from the given file asynchronously.

    Args:
        solution_file: Path to JSON file with solutions
        output_dir: Directory to save results (defaults to "data")

    Returns:
        EvaluationResults object with evaluation results
    """
    if not CYBER_URL:
        raise ValueError("Please set the CYBER_URL environment variable")

    # Default output directory
    if output_dir is None:
        output_dir = "data"

    # Load solutions
    with open(solution_file, "r") as f:
        solutions = json.load(f)

    results = []

    for i, solution_data in enumerate(solutions):
        print(
            f"Evaluating problem {i + 1}: {solution_data.get('source', 'unknown')} "
            f"(Difficulty: {solution_data.get('difficulty', 'unknown')})"
        )

        # Use the input_output field directly from the solution data
        stdin_stdout_tests = solution_data.get("problem").get("tests")
        print(f"  Found {len(stdin_stdout_tests)} test cases")

        # Extract code from the solution - find model-specific solution key
        model_code = extract_code(solution_data.get("code"))
        human_code = solution_data.get("problem").get("human_solution", "")

        # Run code against test cases asynchronously
        model_results = await run_unit_tests_async([model_code], stdin_stdout_tests)
        human_results = (
            await run_unit_tests_async([human_code], stdin_stdout_tests)
            if human_code
            else []
        )

        # Summarize results - each element in model_results is a list of test results for each test
        model_passed = sum(
            1 for result in model_results[0] if result.get("passed", False)
        )
        human_passed = (
            sum(1 for result in human_results[0] if result.get("passed", False))
            if human_results
            else 0
        )

        print(
            f"  Model solution: {model_passed}/{len(stdin_stdout_tests)} tests passed"
        )
        if human_code:
            print(
                f"  Human solution: {human_passed}/{len(stdin_stdout_tests)} tests passed"
            )

        # Create problem evaluation result
        problem_result = ProblemEvaluationResult(
            problem_id=i,
            model_tests_passed=model_passed,
            model_tests_total=len(stdin_stdout_tests),
            human_tests_passed=human_passed,
            human_tests_total=len(stdin_stdout_tests),
            detailed_model_results=model_results[0] if model_results else [],
            detailed_human_results=human_results[0] if human_results else [],
        )

        # Include all original keys from solution_data
        for key, value in solution_data.items():
            if key not in problem_result.model_dump():
                setattr(problem_result, key, value)

        results.append(problem_result)

    # Create evaluation results
    model_total_passed = sum(r.model_tests_passed for r in results)
    model_total_tests = sum(r.model_tests_total for r in results)
    human_total_passed = sum(r.human_tests_passed for r in results)
    human_total_tests = sum(r.human_tests_total for r in results)

    evaluation_results = EvaluationResults(
        results=results,
        model_total_passed=model_total_passed,
        model_total_tests=model_total_tests,
        human_total_passed=human_total_passed,
        human_total_tests=human_total_tests,
    )

    # Save results to file
    output_file = os.path.join(
        output_dir,
        os.path.basename(solution_file).replace(".json", "_execution_results.json"),
    )
    with open(output_file, "w") as f:
        json.dump([r.model_dump() for r in results], f, indent=2)

    print(f"Execution results saved to {output_file}")

    # Print summary
    if model_total_tests > 0:
        print("\nSummary:")
        print(
            f"Model solutions: {model_total_passed}/{model_total_tests} tests passed ({model_total_passed / model_total_tests * 100:.2f}%)"
        )
        if human_total_tests > 0:
            print(
                f"Human solutions: {human_total_passed}/{human_total_tests} tests passed ({human_total_passed / human_total_tests * 100:.2f}%)"
            )

    return evaluation_results


def evaluate_solutions(
    solution_file: str, output_dir: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Evaluate generated solutions from the given file (synchronous wrapper).

    Args:
        solution_file: Path to JSON file with solutions
        output_dir: Directory to save results (defaults to "data")

    Returns:
        List of evaluation results
    """
    # Use run_unit_tests_async directly to avoid nested asyncio.run() calls
    results = asyncio.run(evaluate_solutions_async(solution_file, output_dir))
    return [r.model_dump() for r in results.results]
