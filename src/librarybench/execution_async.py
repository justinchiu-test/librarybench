"""Execution module for testing code solutions."""

import os
import json
import aiohttp
import asyncio
import logging
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, ConfigDict

# URL for execution API - load from environment variable
CYBER_URL: str = os.getenv("CYBER_URL", "")


# Classes for evaluation results
class ProblemEvaluationResult(BaseModel):
    """Results of evaluating a single problem."""

    problem_id: int
    model_tests_passed: int = 0
    model_tests_total: int = 0
    human_tests_passed: int = 0
    human_tests_total: int = 0
    detailed_model_results: List[Dict[str, Any]] = []
    detailed_human_results: List[Dict[str, Any]] = []

    # Allow arbitrary additional fields
    model_config = ConfigDict(extra="allow")


class EvaluationResults(BaseModel):
    """Results of evaluating a batch of problems."""

    results: List[ProblemEvaluationResult] = []
    model_total_passed: int = 0
    model_total_tests: int = 0
    human_total_passed: int = 0
    human_total_tests: int = 0

    # Allow arbitrary additional fields
    model_config = ConfigDict(extra="allow")


async def evaluate_solution(
    code: str,
    test_cases: List[Dict[str, str]],
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
            raise ValueError(
                "No execution API URL provided. Set CYBER_URL environment variable."
            )

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
        "results": test_results_flat,
    }


async def run_unit_tests_async(
    solutions: List[str],
    stdin_stdout_tests: List[Dict[str, str]],
    concurrency: int = 10,
) -> List[List[Dict[str, Any]]]:
    """
    Run multiple solutions against multiple test cases concurrently.

    Args:
        solutions: List of code snippets to test
        stdin_stdout_tests: List of input/output test cases
        concurrency: Maximum number of concurrent requests

    Returns:
        Nested list of test results (solution -> test case -> result)
    """
    if not stdin_stdout_tests:
        return []

    # Set up cyber URL
    url = CYBER_URL
    if not url:
        raise ValueError("CYBER_URL environment variable not set")

    # Create semaphore for limiting concurrency
    semaphore = asyncio.Semaphore(concurrency)

    async def run_test(solution: str, test_case: Dict[str, str]) -> Dict[str, Any]:
        """Run a single test for a solution."""
        async with semaphore:
            async with aiohttp.ClientSession() as session:
                try:
                    # Prepare payload
                    payload = {
                        "language": "python",
                        "code": solution,
                        "stdin": test_case.get("stdin", ""),
                        "expected_stdout": test_case.get("stdout", ""),
                    }

                    # Make API request
                    async with session.post(url, json=payload) as response:
                        if response.status != 200:
                            error_msg = await response.text()
                            return {
                                "passed": False,
                                "error": f"API Error: {response.status}: {error_msg}",
                            }

                        # Parse response
                        exec_output = await response.json()

                        # Access run output safely
                        run_output = exec_output.get("run_output", {})
                        stdout = run_output.get("stdout", "").strip()
                        stderr = run_output.get("stderr", "").strip()

                        # Normalize newlines in expected
                        expected = test_case.get("stdout", "").strip()

                        # Check if test passed
                        passed = False
                        if not stderr and stdout:
                            if stdout == expected:
                                passed = True
                            elif stdout.replace("\r\n", "\n") == expected.replace(
                                "\r\n", "\n"
                            ):
                                passed = True

                        return {"passed": passed, "exec_output": exec_output}
                except Exception as e:
                    return {"passed": False, "error": f"Exception: {str(e)}"}

    # Create tasks for all solution-test combinations
    all_results = []

    for solution in solutions:
        tasks = [run_test(solution, test) for test in stdin_stdout_tests]
        solution_results = await asyncio.gather(*tasks)
        all_results.append(solution_results)

    return all_results


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
        input_output = solution_data.get("input_output")
        if not input_output:
            print(f"  No input_output field found in solution data for problem {i + 1}")
            continue

        # Parse input_output if it's a string
        if isinstance(input_output, str):
            try:
                input_output = json.loads(input_output)
            except json.JSONDecodeError:
                print(f"  Error parsing input_output JSON for problem {i + 1}")
                continue

        # Format as stdin/stdout tests
        stdin_stdout_tests = []
        if "inputs" in input_output and "outputs" in input_output:
            for inp, out in zip(input_output["inputs"], input_output["outputs"]):
                stdin_stdout_tests.append({"stdin": inp, "stdout": out})

        if not stdin_stdout_tests:
            print(f"  No test cases found for problem {i + 1}")
            continue

        print(f"  Found {len(stdin_stdout_tests)} test cases")

        # Extract code from the solution - find model-specific solution key
        model_code = ""
        model_type = None

        # Find the first key that looks like a model solution
        for key in solution_data:
            if key.endswith("_solution") and key != "human_solution":
                # Determine model type based on key name
                if "claude" in key or "anthropic" in key:
                    model_type = "claude"
                elif "o3" in key or "gpt" in key or "openai" in key:
                    model_type = "openai"

                from librarybench.utils import extract_code

                model_code = extract_code(solution_data.get(key, ""), model_type)
                break

        # Fallback if no model solution found
        if not model_code:
            # Try the most common solution keys
            if "o3_mini_solution" in solution_data:
                from librarybench.utils import extract_code

                model_code = extract_code(
                    solution_data.get("o3_mini_solution", ""), "openai"
                )
            elif "claude_solution" in solution_data:
                from librarybench.utils import extract_code

                model_code = extract_code(
                    solution_data.get("claude_solution", ""), "claude"
                )

        human_code = solution_data.get("human_solution", "")

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
