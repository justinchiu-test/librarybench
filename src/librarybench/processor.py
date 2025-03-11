"""Main entry point for solution generation and improvement."""

import os
import datasets
import logging
from typing import List, Optional

from librarybench.solution import (
    get_problems,
    save_solutions,
    batch_process_solutions,
    convert_solutions_to_problems,
)
from librarybench.models import ClaudeClient, OpenAiClient
from librarybench.types import BatchResult, SolutionResult

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def solution_process(
    model_type: str = "openai",
    model_name: Optional[str] = None,
    sample_size: int = 5,
    concurrency: int = 5,
    problem_types: List[str] = ["search", "datastructure", "chess"],
    output_dir: str = "data",
    cyber_url: Optional[str] = None,
    max_iterations: int = 1,
    target_passed_ratio: float = 1.0,
    input_solution_file: Optional[str] = None,
) -> BatchResult:
    """
    Main entry point for solution generation and improvement.

    Args:
        model_type: Type of model to use ("openai" or "claude")
        model_name: Specific model name to use, or None to use default
        sample_size: Number of examples to process
        concurrency: Number of concurrent requests
        problem_types: List of problem types to generate solutions for
        output_dir: Directory to save solutions to
        cyber_url: URL for the execution API
        max_iterations: Max iterations per problem (1 for generation, >1 for improvement)
        target_passed_ratio: Target passing ratio to stop early
        input_solution_file: Optional file with existing solutions to improve

    Returns:
        BatchResult with results and statistics
    """
    # Set up the correct LLM client based on user preferences
    if model_type.lower() == "claude":
        if model_name:
            llm_client = ClaudeClient(model=model_name)
        else:
            llm_client = ClaudeClient()  # Use default Claude model
        print(f"Using Claude model: {llm_client.model_name}")
    else:
        if model_name:
            llm_client = OpenAiClient(model=model_name)
        else:
            llm_client = OpenAiClient()  # Use default OpenAI model
        print(f"Using OpenAI model: {llm_client.model_name}")

    # Define output directory prefix based on model
    output_prefix = f"{output_dir}/{llm_client.model_name}"

    # Set up cyber URL if not provided
    if cyber_url is None:
        cyber_url = os.environ.get("CYBER_URL")
        if not cyber_url:
            raise ValueError(
                "No execution API URL provided. Set CYBER_URL environment variable."
            )

    generated_files = {}

    # If improving existing solutions
    if input_solution_file:
        print(f"Improving solutions from {input_solution_file}...")
        with open(input_solution_file, "r") as f:
            import json

            solutions = [SolutionResult.model_validate(x) for x in json.load(f)]

        problems = convert_solutions_to_problems(solutions)

        # Process the solutions
        results = await batch_process_solutions(
            problems=problems,
            llm_client=llm_client,
            cyber_url=cyber_url,
            max_iterations=max_iterations,
            target_passed_ratio=target_passed_ratio,
            improvement_mode=True,
            concurrency=concurrency,
        )

        # Calculate statistics
        completed = [r for r in results if r.status == "success"]
        errors = [r for r in results if r.status == "error"]

        # Calculate average pass ratios
        avg_initial = 0.0
        avg_final = 0.0

        if completed:
            # Get initial ratio from first history item
            initial_ratios = [
                r.history[0]["pass_ratio"] if r.history else 0.0 for r in completed
            ]
            final_ratios = [r.pass_ratio for r in completed]

            avg_initial = sum(initial_ratios) / len(completed) if completed else 0.0
            avg_final = sum(final_ratios) / len(completed) if completed else 0.0

        # Determine file type from input file
        file_type = None
        for pt in problem_types:
            if pt in input_solution_file:
                file_type = pt
                break

        if file_type:
            # Save modified solutions
            output_file = f"{output_prefix}_{file_type}_solutions_improved.json"
            save_solutions(results, output_file)
            generated_files[file_type] = output_file

        # Return batch result
        return BatchResult(
            status="success",
            generated_files=generated_files,
            model_type=model_type.lower(),
            model_name=llm_client.model_name,
            total_problems=len(solutions),
            completed=len(completed),
            errors=len(errors),
            avg_initial_ratio=avg_initial,
            avg_final_ratio=avg_final,
            avg_improvement=avg_final - avg_initial,
        )

    # Otherwise, fresh generation from TACO dataset
    else:
        # Load the TACO dataset
        dataset = datasets.load_dataset("BAAI/TACO", trust_remote_code=True)
        train = dataset["test"]  # type: ignore

        # Filter for problems with specific skills
        search_problems = [x for x in train if "Complete search" in x["skill_types"]]  # type: ignore
        datastructure_problems = [
            x
            for x in train
            if "Data structures" in x["skill_types"]  # type: ignore
        ]
        chess_problems = [x for x in train if "chess" in x["question"].lower()]  # type: ignore

        mapping = dict(
            search=search_problems,
            datastrcutre=datastructure_problems,
            chess=chess_problems,
        )
        problem_sets = [mapping[x] for x in problem_types]
        for problem_type, problems in zip(problem_types, problem_sets):
            print(f"Processing {sample_size} {problem_type} problems...")
            examples = get_problems(search_problems)  # type: ignore
            results = await batch_process_solutions(
                problems=examples[:sample_size],
                llm_client=llm_client,
                cyber_url=cyber_url,
                max_iterations=max_iterations,
                target_passed_ratio=target_passed_ratio,
                improvement_mode=False,
                concurrency=concurrency,
            )
            solution_file = f"{output_prefix}_{problem_type}_solutions.json"
            save_solutions(results, solution_file)
            generated_files[problem_type] = solution_file

        print(
            f"Done! Solutions processed for all problem types using {llm_client.model_name}."
        )

        return BatchResult(
            status="success",
            generated_files=generated_files,
            model_type=model_type,
            model_name=llm_client.model_name,
            total_problems=sum([sample_size] * len(problem_types)),
            completed=len(problem_types)
            * sample_size,  # Simplistic - assumes all completed
            errors=0,
        )
