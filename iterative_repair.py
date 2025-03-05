import os
import json
import re
import asyncio
import aiohttp
import argparse
from typing import Dict, Any, List, Tuple, Optional, Set, Union
from tqdm import tqdm
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# URL for execution API - load from environment variable
CYBER_URL: str = os.getenv("CYBER_URL", "")
if not CYBER_URL:
    raise ValueError("Please set the CYBER_URL environment variable")

# Global semaphores for controlling concurrent requests
LLM_SEMAPHORE = asyncio.Semaphore(5)  # Limit concurrent LLM API calls
EXECUTION_SEMAPHORE = asyncio.Semaphore(50)  # Limit concurrent execution API calls


# Function to extract code from model's solution
def extract_code(solution: str) -> str:
    """Extract code from a model-generated solution."""
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


async def execute_test(
    session: aiohttp.ClientSession,
    code: str,
    test: Dict[str, str],
) -> Dict[str, Any]:
    """Execute a single test against the execution API with semaphore control."""
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


async def run_tests(
    code: str, 
    stdin_stdout_tests: List[Dict[str, str]]
) -> List[Dict[str, Any]]:
    """Execute code against unit tests using the execution API asynchronously."""
    async with aiohttp.ClientSession() as session:
        tasks = [
            execute_test(session, code, test)
            for test in stdin_stdout_tests
        ]
        return await asyncio.gather(*tasks)


def create_test_cases_from_input_output(input_output: Dict) -> List[Dict[str, str]]:
    """Convert input-output pairs to test cases for execution."""
    stdin_stdout_tests = []
    if "inputs" in input_output and "outputs" in input_output:
        for inp, out in zip(input_output["inputs"], input_output["outputs"]):
            stdin_stdout_tests.append({"stdin": inp, "stdout": out})
    return stdin_stdout_tests


def format_feedback(
    test_results: List[Dict[str, Any]], 
    test_cases: List[Dict[str, str]],
    passed_count: int,
    total_count: int
) -> str:
    """Format test results as feedback for the model."""
    feedback = f"Test Results: {passed_count}/{total_count} tests passed\n\n"
    
    for i, (test, result) in enumerate(zip(test_cases, test_results), 1):
        status = "✅ PASSED" if result.get("passed", False) else "❌ FAILED"
        feedback += f"Test #{i}: {status}\n"
        feedback += f"Input:\n{test['stdin']}\n"
        feedback += f"Expected Output:\n{test['stdout']}\n"
        
        if not result.get("passed", False):
            stdout = result.get("exec_output", {}).get("run_output", {}).get("stdout", "")
            stderr = result.get("exec_output", {}).get("run_output", {}).get("stderr", "")
            feedback += f"Actual Output:\n{stdout}\n"
            if stderr:
                feedback += f"Error:\n{stderr}\n"
        
        feedback += "-" * 40 + "\n"
    
    return feedback


async def query_model(
    prompt: str, 
    model_name: str = "claude-3-haiku", 
    temperature: float = 0.2
) -> str:
    """
    Query an LLM with a prompt using the appropriate API.
    
    Args:
        prompt: The text prompt to send to the model
        model_name: The name of the model to use
        temperature: Temperature setting for model generation
        
    Returns:
        The model's text response
    """
    async with LLM_SEMAPHORE:
        logger.info(f"Querying {model_name} with prompt (length: {len(prompt)} chars)")
        
        # This is a placeholder - should be replaced with actual API implementations
        # For demo purposes, we'll just return a modified version of the current solution
        # In production, uncomment the appropriate API client code below
        
        # For Claude models
        if "claude" in model_name.lower():
            # Uncomment and adjust this code when ready to use the real API
            # import anthropic
            # client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            # message = client.messages.create(
            #     model=model_name,
            #     max_tokens=4000,
            #     temperature=temperature,
            #     system="You are an expert Python programmer helping to improve code based on test feedback.",
            #     messages=[
            #         {"role": "user", "content": prompt}
            #     ]
            # )
            # return message.content[0].text
            pass
        
        # For OpenAI models
        elif "gpt" in model_name.lower():
            # Uncomment and adjust this code when ready to use the real API
            # import openai
            # client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            # response = client.chat.completions.create(
            #     model=model_name,
            #     temperature=temperature,
            #     messages=[
            #         {"role": "system", "content": "You are an expert Python programmer helping to improve code based on test feedback."},
            #         {"role": "user", "content": prompt}
            #     ]
            # )
            # return response.choices[0].message.content
            pass
        
        # For demo purposes
        return "I've analyzed the test failures and improved the solution:\n\n```python\ndef can_split_string(s):\n    # Special case: If the string is 10 or more characters, we can always split it\n    if len(s) >= 10:\n        return \"YES\"\n    # Special case: We need at least 4 characters to form 4 non-empty parts\n    if len(s) < 4:\n        return \"NO\"\n    \n    # Try all possible ways to split the string into 4 parts\n    for i in range(1, len(s)-2):\n        for j in range(i+1, len(s)-1):\n            for k in range(j+1, len(s)):\n                # Extract the four parts\n                part1 = s[0:i]\n                part2 = s[i:j]\n                part3 = s[j:k]\n                part4 = s[k:]\n                # Check if all parts are pairwise different\n                if part1 != part2 and part1 != part3 and part1 != part4 and \\\n                   part2 != part3 and part2 != part4 and part3 != part4:\n                    return \"YES\"\n    return \"NO\"\n\n# Process test cases\nt = int(input())\nfor _ in range(t):\n    s = input().strip()\n    print(can_split_string(s))\n```"


async def improve_solution(
    solution_data: Dict[str, Any],
    problem_id: int,
    model_name: str = "claude-3-haiku",
    max_iterations: int = 3,
    target_passed_ratio: float = 1.0
) -> Tuple[str, float, Dict[str, Any]]:
    """
    Run the improvement loop for a specific problem solution.
    
    Args:
        solution_data: The solution data for the problem
        problem_id: The ID of the problem being improved
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
            raise ValueError(f"Error parsing input_output JSON for problem {problem_id}")
    
    # Format as stdin/stdout tests
    stdin_stdout_tests = create_test_cases_from_input_output(input_output)
    if not stdin_stdout_tests:
        raise ValueError(f"No test cases found for problem {problem_id}")
    
    # Extract the initial code (depending on model type)
    if "o3_mini" in model_name.lower():
        initial_solution = solution_data.get("o3_mini_solution", "")
        model_key = "o3_mini_solution"
    else:
        initial_solution = solution_data.get("claude_solution", "")
        model_key = "claude_solution"
    
    # Extract the code
    current_code = extract_code(initial_solution)
    
    logger.info(f"Starting improvement for problem {problem_id}")
    logger.info(f"Model: {model_name}")
    logger.info(f"Max iterations: {max_iterations}")
    logger.info(f"Target passed ratio: {target_passed_ratio}")
    
    iteration = 0
    best_passed_ratio = 0.0
    best_code = current_code
    improvement_history = []
    
    # Run initial evaluation
    initial_results = await run_tests(current_code, stdin_stdout_tests)
    initial_passed = sum(1 for result in initial_results if result.get("passed", False))
    initial_ratio = initial_passed / len(stdin_stdout_tests)
    
    # If all tests already pass, we're done
    if initial_ratio >= target_passed_ratio:
        logger.info(f"Initial solution already meets target pass ratio: {initial_ratio:.2%}")
        return current_code, initial_ratio, {
            "problem_id": problem_id,
            "initial_ratio": initial_ratio,
            "final_ratio": initial_ratio,
            "iterations": 0,
            "history": [],
            "best_code": current_code
        }
    
    # Initialize best code/ratio with initial values
    best_passed_ratio = initial_ratio
    best_code = current_code
    
    while iteration < max_iterations:
        iteration += 1
        logger.info(f"Iteration {iteration}/{max_iterations}")
        
        # Run the code against test cases
        test_results = await run_tests(current_code, stdin_stdout_tests)
        
        # Calculate pass rate
        passed = sum(1 for result in test_results if result.get("passed", False))
        total = len(stdin_stdout_tests)
        passed_ratio = passed / total
        
        logger.info(f"Current pass rate: {passed}/{total} ({passed_ratio:.2%})")
        improvement_history.append({
            "iteration": iteration,
            "pass_ratio": passed_ratio,
            "passed": passed,
            "total": total
        })
        
        # If all tests pass or we've reached target ratio, we're done
        if passed_ratio >= target_passed_ratio:
            logger.info(f"Target pass ratio reached. Stopping.")
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
        new_code = extract_code(response)
        
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
        "best_code": best_code
    }
    
    logger.info(f"Final Results:")
    logger.info(f"Initial pass ratio: {initial_ratio:.2%}")
    logger.info(f"Best pass ratio: {best_passed_ratio:.2%}")
    logger.info(f"Improvement: {(best_passed_ratio - initial_ratio) * 100:.2f} percentage points")
    
    return best_code, best_passed_ratio, improvement_data


async def batch_improve_solutions(
    solution_file: str,
    problem_ids: Optional[List[int]] = None,
    model_name: str = "claude-3-haiku",
    max_iterations: int = 3,
    target_passed_ratio: float = 1.0,
    output_file: Optional[str] = None,
    concurrent_problems: int = 3
) -> Dict[str, Any]:
    """
    Process multiple problems for improvement in parallel.
    
    Args:
        solution_file: Path to the solution JSON file
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
                    model_name=model_name,
                    max_iterations=max_iterations,
                    target_passed_ratio=target_passed_ratio
                )
                
                # Update the solution in our copy
                if "o3_mini" in model_name.lower():
                    model_key = "o3_mini_solution"
                else:
                    model_key = "claude_solution"
                
                improved_solutions[problem_id][f"improved_{model_key}"] = f"```python\n{best_code}\n```"
                
                return {
                    "problem_id": problem_id,
                    "status": "completed",
                    **improvement_data
                }
            except Exception as e:
                logger.error(f"Error processing problem {problem_id}: {e}")
                return {
                    "problem_id": problem_id,
                    "status": "error",
                    "error": str(e)
                }
    
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
    }
    
    if completed:
        avg_initial = sum(r.get("initial_ratio", 0) for r in completed) / len(completed)
        avg_final = sum(r.get("final_ratio", 0) for r in completed) / len(completed)
        perfect = sum(1 for r in completed if r.get("final_ratio", 0) == 1.0)
        
        summary.update({
            "avg_initial_ratio": avg_initial,
            "avg_final_ratio": avg_final,
            "avg_improvement": avg_final - avg_initial,
            "perfect_solutions": perfect
        })
    
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
        logger.info(f"Average initial pass ratio: {avg_initial:.2%}")
        logger.info(f"Average final pass ratio: {avg_final:.2%}")
        logger.info(f"Average improvement: {(avg_final - avg_initial) * 100:.2f} percentage points")
        logger.info(f"Problems with perfect pass ratio: {perfect}/{len(completed)} ({perfect/len(completed):.2%})")
    
    # Save summary to a separate file
    summary_file = f"summary_{os.path.basename(output_file)}"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"Summary saved to {summary_file}")
    
    return summary


async def main():
    """Parse arguments and run the appropriate function."""
    # Check if CYBER_URL is set
    if not CYBER_URL:
        logger.error("Error: CYBER_URL environment variable is not set")
        return
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Improve model solutions with test feedback")
    parser.add_argument("--solution-file", type=str, required=True, help="Path to the solution JSON file")
    
    # Problem selection arguments
    problem_group = parser.add_mutually_exclusive_group()
    problem_group.add_argument("--problem-id", type=int, help="ID of a specific problem to improve")
    problem_group.add_argument("--problem-ids", type=str, help="Comma-separated list of problem IDs to process")
    problem_group.add_argument("--range", type=str, help="Range of problem IDs to process (e.g., '0-5')")
    
    # Model and execution parameters
    parser.add_argument("--model-name", type=str, default="claude-3-haiku", help="Name of the model to use")
    parser.add_argument("--max-iterations", type=int, default=3, help="Maximum number of improvement iterations per problem")
    parser.add_argument("--target-ratio", type=float, default=1.0, help="Target passing ratio to stop early (0-1)")
    parser.add_argument("--output-file", type=str, help="File to save improved solutions (default: improved_<input-file>)")
    parser.add_argument("--concurrent-problems", type=int, default=3, help="Number of problems to process concurrently")
    parser.add_argument("--llm-semaphore", type=int, default=5, help="Maximum concurrent LLM API calls")
    parser.add_argument("--exec-semaphore", type=int, default=50, help="Maximum concurrent execution API calls")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO", help="Logging level")
    
    args = parser.parse_args()
    
    # Set log level
    logger.setLevel(getattr(logging, args.log_level))
    
    # Update global semaphores
    global LLM_SEMAPHORE, EXECUTION_SEMAPHORE
    LLM_SEMAPHORE = asyncio.Semaphore(args.llm_semaphore)
    EXECUTION_SEMAPHORE = asyncio.Semaphore(args.exec_semaphore)
    
    # Determine problem IDs to process
    problem_ids = None
    if args.problem_id is not None:
        problem_ids = [args.problem_id]
    elif args.problem_ids:
        problem_ids = [int(pid.strip()) for pid in args.problem_ids.split(",")]
    elif args.range:
        start, end = map(int, args.range.split("-"))
        problem_ids = list(range(start, end + 1))
    
    # Run batch processing
    await batch_improve_solutions(
        solution_file=args.solution_file,
        problem_ids=problem_ids,
        model_name=args.model_name,
        max_iterations=args.max_iterations,
        target_passed_ratio=args.target_ratio,
        output_file=args.output_file,
        concurrent_problems=args.concurrent_problems
    )


if __name__ == "__main__":
    asyncio.run(main())