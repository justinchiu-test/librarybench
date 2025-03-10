"""Solution processing module for code generation and improvement."""

import ast
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional

from librarybench.utils import extract_code
from librarybench.models.llm_client import LlmClient
from librarybench.llm import query_model
from librarybench.execution import evaluate_solution
from librarybench.prompting import format_generation_prompt, format_improvement_prompt
from librarybench.types import Problem, SolutionResult
from librarybench.utils import create_test_cases_from_input_output

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_problems(xs: List[Dict[str, Any]]) -> List[Problem]:
    """
    Filter and prepare problem examples for solution generation.

    Args:
        xs: List of problem examples

    Returns:
        Filtered list of problems ready for processing
    """
    results = []

    for i, x in enumerate(xs):
        assert "question" in x

        # Check if input_output exists and is valid
        input_output = x.get("input_output")
        assert input_output is not None

        # Parse input_output if it's a string
        if isinstance(input_output, str):
            input_output = json.loads(input_output)
            # if this doesnt work, can use ast.literal_eval

        # Format as stdin/stdout tests
        stdin_stdout_tests = create_test_cases_from_input_output(input_output)

        # Add source and difficulty if available
        source = x.get("source", "unknown")
        difficulty = x.get("difficulty", "unknown")

        solutions = x.get("solutions")
        if solutions is not None:
            solutions = ast.literal_eval(solutions)
        else:
            solutions = []

        # Add to results
        problem = Problem(
            problem_id=i,
            question=x["question"],
            tests=stdin_stdout_tests,
            source=source,
            difficulty=difficulty,
            human_solutions=solutions,
            original_solution=None,
        )

        results.append(problem)

    return results


def save_solutions(
    results: List[SolutionResult],
    problems: List[Problem],
    llm_client: LlmClient,
    output_file: str,
) -> None:
    """
    Save solution results to a JSON file.

    Args:
        results: List of solution results
        problems: Original list of problems
        llm_client: LLM client used for generation
        output_file: Path to save the results to
    """
    # Create a map from problem ID to result
    result_map = {r.problem_id: r for r in results}

    # Prepare output data
    output_data = []

    # For each problem, add its result data
    for i, problem in enumerate(problems):
        if i in result_map:
            result = result_map[i]

            # Create a solution entry
            solution_entry = problem.model_dump()

            # Add the model solution
            model_key = f"{llm_client.model_name}_solution"
            solution_entry[model_key] = result.code

            # Add to output
            output_data.append(solution_entry)

    # Save to file
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"Results saved to {output_file}")


async def process_solution(
    problem: Problem,
    llm_client: LlmClient,
    cyber_url: str,
    improvement_mode: bool = False,
    max_iterations: int = 1,
    target_passed_ratio: float = 1.0,
) -> SolutionResult:
    """
    Process a single problem to generate or improve a solution.

    Args:
        problem: Problem data
        llm_client: LLM client to use
        cyber_url: URL for the execution API
        improvement_mode: Whether to improve an existing solution
        max_iterations: Maximum number of iterations
        target_passed_ratio: Target ratio of passed tests

    Returns:
        SolutionResult with the generated or improved solution
    """
    problem_id = problem.problem_id
    result = SolutionResult(
        problem_id=problem_id,
        code="",
        status="error",
    )

    # Convert input_output to test cases
    stdin_stdout_tests = problem.tests

    if not stdin_stdout_tests:
        logger.warning(f"No test cases found for problem {problem_id}")
        return SolutionResult(
            problem_id=problem_id, code="# Error: No test cases found", status="error"
        )

    # Track solution history
    history = []

    # Generate initial solution or extract existing one
    if improvement_mode:
        # Find the first solution key in the problem
        assert problem.original_solution is not None

        # Extract code from the solution
        original_code = problem.original_solution

        # Evaluate the original solution
        evaluation = await evaluate_solution(
            original_code, stdin_stdout_tests, cyber_url
        )

        # Add to history
        passed = evaluation["tests_passed"]
        total = evaluation["tests_total"]
        passed_ratio = evaluation["pass_ratio"]
        test_results = evaluation["results"]

        history.append(
            {
                "iteration": 0,
                "code": original_code,
                "pass_ratio": passed_ratio,
                "tests_passed": passed,
                "tests_total": total,
            }
        )

        # Check if initial solution already meets target
        if passed_ratio >= target_passed_ratio:
            logger.info("Initial solution already meets target pass ratio")
            return SolutionResult(
                problem_id=problem_id,
                code=original_code,
                status="success",
                pass_ratio=passed_ratio,
                tests_passed=passed,
                tests_total=total,
                iterations=1,
                history=history,
            )

        # Set initial code to start improving
        code = original_code
    else:
        # Generate a new solution
        prompt = format_generation_prompt(problem)

        # Query the model
        response = await query_model(prompt=prompt, llm_client=llm_client, iteration=1)

        # Extract code from the response
        code = extract_code(response, llm_client.model_name)

        # Evaluate the solution
        if code:
            evaluation = await evaluate_solution(code, stdin_stdout_tests, cyber_url)

            # Get results
            passed = evaluation["tests_passed"]
            total = evaluation["tests_total"]
            passed_ratio = evaluation["pass_ratio"]
            test_results = evaluation["results"]

            # Add to history
            history.append(
                {
                    "iteration": 1,
                    "code": code,
                    "pass_ratio": passed_ratio,
                    "tests_passed": passed,
                    "tests_total": total,
                }
            )

            # Check if we've reached the target
            if passed_ratio >= target_passed_ratio:
                logger.info(f"Current pass rate: {passed}/{total} ({passed_ratio:.2%})")
                logger.info("Target pass ratio reached. Stopping.")

                return SolutionResult(
                    problem_id=problem_id,
                    code=code,
                    status="success",
                    pass_ratio=passed_ratio,
                    tests_passed=passed,
                    tests_total=total,
                    iterations=1,
                    history=history,
                )
        else:
            logger.warning(f"Failed to extract code for problem {problem_id}")
            return SolutionResult(
                problem_id=problem_id,
                code="# Error: Failed to extract code",
                status="error",
            )

    # If we need to iterate for improvement or didn't reach target on first try
    if max_iterations > 1:
        # Record initial pass ratio
        if improvement_mode:
            logger.info(
                f"Initial solution pass rate: {passed}/{total} ({passed_ratio:.2%})"
            )

        # Iterate to improve the solution
        for i in range(1 if improvement_mode else 2, max_iterations + 1):
            # Only continue if we haven't reached the target
            if passed_ratio >= target_passed_ratio:
                break

            logger.info(f"Iteration {i}/{max_iterations} for problem {problem_id}")

            # Create improvement prompt with test feedback
            improve_prompt = format_improvement_prompt(
                problem=problem,
                original_code=code,
                test_results=test_results,
                passed=passed,
                total=total,
            )

            # Query the model for an improved solution
            response = await query_model(
                prompt=improve_prompt, llm_client=llm_client, iteration=i
            )

            # Extract improved code
            improved_code = extract_code(response, llm_client.model_name)

            if improved_code:
                # Evaluate the improved solution
                evaluation = await evaluate_solution(
                    improved_code, problem.tests, cyber_url
                )

                # Get results
                new_passed = evaluation["tests_passed"]
                new_total = evaluation["tests_total"]
                new_ratio = evaluation["pass_ratio"]
                test_results = evaluation["results"]

                # Log progress
                logger.info(
                    f"Current pass rate: {new_passed}/{new_total} ({new_ratio:.2%})"
                )

                # Add to history
                history.append(
                    {
                        "iteration": i,
                        "code": improved_code,
                        "pass_ratio": new_ratio,
                        "tests_passed": new_passed,
                        "tests_total": new_total,
                    }
                )

                # Only update if it's better
                if new_ratio >= passed_ratio:
                    code = improved_code
                    passed = new_passed
                    total = new_total
                    passed_ratio = new_ratio

                # Check if we've reached the target
                if passed_ratio >= target_passed_ratio:
                    logger.info("Target pass ratio reached. Stopping.")
                    break

    # Return the final solution
    return SolutionResult(
        problem_id=problem_id,
        code=code,
        status="success",
        pass_ratio=passed_ratio,
        tests_passed=passed,
        tests_total=total,
        iterations=len(history),
        history=history,
    )


async def batch_process_solutions(
    problems: List[Problem],
    llm_client: LlmClient,
    cyber_url: str,
    max_iterations: int = 1,
    target_passed_ratio: float = 1.0,
    improvement_mode: bool = False,
    concurrency: int = 5,
) -> List[SolutionResult]:
    """
    Process a batch of problems concurrently.

    Args:
        problems: List of problems to process
        llm_client: LLM client to use
        cyber_url: URL for the execution API
        max_iterations: Maximum number of iterations
        target_passed_ratio: Target ratio of passed tests
        improvement_mode: Whether to improve existing solutions
        concurrency: Number of concurrent processes

    Returns:
        List of solution results
    """
    # Process each problem concurrently with limited concurrency
    semaphore = asyncio.Semaphore(concurrency)

    async def process_with_semaphore(problem: Problem) -> SolutionResult:
        """Process a single problem with semaphore."""
        async with semaphore:
            return await process_solution(
                problem=problem,
                llm_client=llm_client,
                cyber_url=cyber_url,
                improvement_mode=improvement_mode,
                max_iterations=max_iterations,
                target_passed_ratio=target_passed_ratio,
            )

    # Create tasks
    tasks = [process_with_semaphore(problem) for problem in problems]

    # Run tasks and get results
    results = await asyncio.gather(*tasks)

    return results
